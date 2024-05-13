import datetime
import locale

import spacy
from spacy import Language

from config.config import MODEL_PATH
from src.entity_type import EntityType
from src.transformations.abstract_transformation import AbstractTransformation
from src.transformations.address_transformation import AddressTransformation
from src.transformations.date_transformation import DateTransformation
from src.transformations.email_transformation import EmailTransformation
from src.transformations.passport_transformation import PassportTransformation
from src.transformations.person_transformation import PersonTransformation
from src.transformations.phone_transformation import PhoneTransformation


class Depersonalizer:
    def __init__(self):
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")  # Установка русской локали
        self._nlp: Language = spacy.load(MODEL_PATH)
        self._transformed_date: datetime = None

    def handle(self, input_string: str) -> str:
        doc = self._nlp(input_string)
        sorted_ents = sorted(doc.ents, key=lambda ent: (ent.label_ != 'DATE', ent.text))
        replacements = {}

        for personal_info in sorted_ents:
            replacements[(personal_info.start_char, personal_info.end_char)] = self.transform(
                personal_info.text,
                personal_info.label_
            )

        return self.__replace(input_string, replacements)

    def transform(self, input_string: str, label: str) -> str | None:
        try:
            entity_type = EntityType(label)
        except ValueError:
            return None

        transformations: dict[EntityType, AbstractTransformation] = {
            EntityType.PERSON: PersonTransformation(),
            EntityType.DATE: DateTransformation(),
            EntityType.EMAIL: EmailTransformation(),
            EntityType.PHONE: PhoneTransformation(),
            EntityType.PASSPORT: PassportTransformation(self._transformed_date),
            EntityType.LOCATION: AddressTransformation(),
        }

        transformation = transformations[entity_type]
        entity = transformation.transform(input_string)
        if entity_type == EntityType.DATE:
            self._transformed_date = transformation.get_transformed_date()

        return entity

    """
    Проведение замены слов в тексте
    После замены все остальные позиции могут сместиться, поэтому каждый раз нужно проводить пересчет 
    """

    @staticmethod
    def __replace(text, replacements: dict) -> str:
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
