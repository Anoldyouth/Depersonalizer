import random
import re
import string
from collections import defaultdict

import pymorphy2
import redis
from sqlalchemy import and_, func, not_

from config.config import REDIS_FROM_PREFIX, REDIS_TO_PREFIX, REDIS_TTL, CHUNK
from config.connection import DatabaseHelper
from config.connection import RedisHelper
from src.models.component import Component
from src.transformations.abstract_transformation import AbstractTransformation


class PersonTransformation(AbstractTransformation):
    morph = pymorphy2.MorphAnalyzer()  # Словарь для определения частей речи
    database_helper = DatabaseHelper()
    redis_helper = RedisHelper()

    chunk_size: int = CHUNK  # Размер чанка рассматриваемых компонентов со схожей популярностью
    from_prefix = REDIS_FROM_PREFIX  # Префикс для пар <Заменяемых объект> => <Произведенная замена>
    to_prefix = REDIS_TO_PREFIX  # Префикс для пар <Произведенная замена> => <Заменяемых объект>
    ttl = REDIS_TTL  # Время жизни замены

    def transform(self, person_input: str) -> str:
        words_with_positions = {}  # Словарь заменяемых слов
        replacements = {}  # Производимые замены
        # Составляем словарь заменяемых слов
        for m in re.finditer(r'\w+|[^\w\s]', person_input):
            word = m.group(0)
            start = m.start()
            end = m.end()
            words_with_positions[word] = (start, end)

        components = list(words_with_positions.keys())
        # Выбираем общий пол и падеж для заменяемых слов
        gender, case = self.__select_gender_and_case(list(words_with_positions.keys()))

        with (self.database_helper.get_session() as session, self.redis_helper.get_connection() as r):
            for component in components:
                founded: Component | None = session.query(Component).filter(and_(
                    getattr(Component, f'component_{case}') == component,
                    Component.gender == gender
                )).first()

                # Не нашли замену в БД, заменяем на случайный текст
                if founded is None:
                    length = random.randint(5, 10)
                    new_name = "".join(random.choice(string.ascii_lowercase) for _ in range(length))
                    replacements[words_with_positions[component]] = new_name.title()

                    continue

                # Проверяем кэш, были ли замены до этого
                already_replaced_id: str = r.get(f'{self.from_prefix}{founded.id}')

                # Замена нашлась
                if already_replaced_id is not None:
                    replace = session.query(Component).filter(Component.id == int(already_replaced_id)).first()
                    replacements[words_with_positions[component]] = getattr(replace, f'component_{case}')
                    self.__add_relations(r, founded, replace)  # Обновление ttl

                    continue

                related_ids = [related.id for related in founded.components]

                # Поиск аналогичных компонентов для замены
                query = session.query(Component).filter(and_(
                    Component.id != founded.id,
                    Component.gender == founded.gender,
                    Component.type == founded.type,
                    not_(Component.id.in_(related_ids))
                )).order_by(func.abs(Component.popularity - founded.popularity))

                was_found = False
                step_offset = 0
                while not was_found:
                    # Поиск чанками, чтобы был выбор дя замены
                    entities = query.offset(step_offset).limit(self.chunk_size).all()
                    random.shuffle(entities)

                    for entity in entities:
                        # В данный компонент уже есть замена
                        if r.exists(f'{self.to_prefix}{founded.id}'):
                            continue

                        # Проводим замену и сопоставляем родственные элементы
                        replacements[words_with_positions[component]] = getattr(entity, f'component_{case}')
                        self.__add_relations(r, founded, entity)
                        was_found = True

                        break

                    step_offset += self.chunk_size

        return self.__replace(person_input, replacements)

    def __select_gender_and_case(self, components: list[str], ):
        frequency_dict = defaultdict(int)

        for component in components:
            for word in self.morph.parse(component):
                if word.tag.number != 'sing':
                    continue

                if word.tag.gender == 'masc' or word.tag.gender == 'femn':
                    # Конкретный гендер
                    frequency_dict[(word.tag.gender, word.tag.case)] += 1
                else:
                    # Нельзя определить гендер, является универсальным словом
                    frequency_dict[('masc', word.tag.case)] += 1
                    frequency_dict[('femn', word.tag.case)] += 1

        # Выбираем максимальное количество совпадений
        gender, case = max(frequency_dict, key=frequency_dict.get)

        return gender, case

    """
    Проведение замены слов в тексте
    После замены все остальные позиции могут сместиться, поэтому каждый раз нужно проводить пересчет 
    """
    @staticmethod
    def __replace(text, replacements):
        sorted_replacements = sorted(replacements.items(), key=lambda x: x[0][0], reverse=True)
        for (start, end), value in sorted_replacements:
            text = text[:start] + value + text[end:]
            for i, (old_replacement, _) in enumerate(sorted_replacements):
                old_start, old_end = old_replacement
                if old_start > start:
                    sorted_replacements[i] = (
                        (old_start - (end - start) + len(value), old_end - (end - start) + len(value)),
                        sorted_replacements[i][1]
                    )

        return text

    def __add_relations(
            self,
            r: redis.Redis,
            comp_from: Component,
            comp_to: Component
    ):
        r.set(f'{self.from_prefix}{comp_from.id}', comp_to.id, ex=self.ttl)
        r.set(f'{self.to_prefix}{comp_to.id}', comp_from.id, ex=self.ttl)

        for relation_from in comp_from.components:
            relations_to = comp_to.components.filter(and_(
                Component.type == relation_from.type,
                Component.gender == relation_from.gender
            )).all()

            for relation_to in relations_to:
                # Если ключ существует, но связан с другим объектом - пропускаем
                if (r.exists(f'{self.from_prefix}{relation_from.id}')
                        and r.get(f'{self.from_prefix}{relation_from.id}') != str(relation_to.id).encode('UTF-8')):
                    continue

                # Если ключ существует, но связан с другим объектом - пропускаем
                if (r.exists(f'{self.to_prefix}{relation_to.id}')
                        and r.get(f'{self.to_prefix}{relation_to.id}') != str(relation_from.id).encode('UTF-8')):
                    continue

                r.set(f'{self.from_prefix}{relation_from.id}', relation_to.id, ex=self.ttl)
                r.set(f'{self.to_prefix}{relation_to.id}', relation_from.id, ex=self.ttl)

                break
