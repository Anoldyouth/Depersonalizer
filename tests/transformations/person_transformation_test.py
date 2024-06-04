from unittest.mock import patch

import pytest
from alembic.command import upgrade
from pytest_mock_resources import create_redis_fixture
from redis import Redis

from config.connection import DatabaseHelper
from models.component import Component, Relation
from transformations.person_transformation import PersonTransformation
from utils import alembic_config_from_url

redis_engine = create_redis_fixture()


@pytest.fixture
def make_migrations():
    alembic_config = alembic_config_from_url(DatabaseHelper().get_url())
    upgrade(alembic_config, 'head')


@pytest.fixture
def prepared_transformation():
    transformation = PersonTransformation()
    transformation.chunk_size = 1
    transformation.from_prefix = 'from_'
    transformation.to_prefix = 'to_'
    transformation.ttl = 3600

    yield transformation


@pytest.fixture
def test_redis(redis_engine):
    redis = Redis(**redis_engine.pmr_credentials.as_redis_kwargs())

    yield redis


@pytest.mark.parametrize('comp_type', [
    'name',
    'surname',
    'last_name'
])
def test_transform_component_type_masc(
        make_migrations,
        test_redis,
        prepared_transformation,
        comp_type
):
    session = DatabaseHelper().get_session()
    component_from = Component(
        id=1,
        type=comp_type,
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    component_to = Component(
        id=2,
        type=comp_type,
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=100
    )

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(component_from)
        session.add(component_to)
        result = prepared_transformation.transform(component_from.component_nomn)

        assert result == component_to.component_nomn
        assert test_redis.exists('from_1', 'to_2') == 2

    session.close()


@pytest.mark.parametrize('comp_type', [
    'name',
    'surname',
    'last_name'
])
def test_transform_component_type_femn(
        make_migrations,
        test_redis,
        prepared_transformation,
        comp_type
):
    session = DatabaseHelper().get_session()
    session.begin()
    component_from = Component(
        id=1,
        type=comp_type,
        component_nomn='Татьяна',
        component_gent='Татьяны',
        component_datv='Татьяне',
        component_accs='Татьяну',
        component_ablt='Татьяной',
        component_loct='Татьяне',
        gender='femn',
        popularity=100
    )
    component_to = Component(
        id=2,
        type=comp_type,
        component_nomn='Ольга',
        component_gent='Ольги',
        component_datv='Ольге',
        component_accs='Ольгу',
        component_ablt='Ольгой',
        component_loct='Ольгой',
        gender='femn',
        popularity=100
    )

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(component_from)
        session.add(component_to)
        result = prepared_transformation.transform(component_from.component_nomn)

        assert result == component_to.component_nomn
        assert test_redis.exists('from_1', 'to_2') == 2

    session.close()


@pytest.mark.parametrize('case', [
    'nomn',
    'gent',
    'datv',
    'accs',
    'ablt',
    'loct'
])
def test_transform_component_case(
        make_migrations,
        test_redis,
        prepared_transformation,
        case
):
    session = DatabaseHelper().get_session()
    session.begin()
    component_from = Component(
        id=1,
        type='name',
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    component_to = Component(
        id=2,
        type='name',
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=100
    )

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(component_from)
        session.add(component_to)
        result = prepared_transformation.transform(getattr(component_from, f'component_{case}'))

        assert result == getattr(component_to, f'component_{case}')
        assert test_redis.exists('from_1', 'to_2') == 2

    session.close()


def test_transform_component_relation(
        make_migrations,
        test_redis,
        prepared_transformation
):
    session = DatabaseHelper().get_session()
    session.begin()
    component_from = Component(
        id=1,
        type='name',
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    related_from = Component(
        id=3,
        type='name',
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    component_to = Component(
        id=2,
        type='name',
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=100
    )
    related_to = Component(
        id=4,
        type='name',
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=100
    )
    relation_from = Relation(component_id_1=component_from.id, component_id_2=related_from.id)
    relation_to = Relation(component_id_1=component_to.id, component_id_2=related_to.id)

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(component_from)
        session.add(related_from)
        session.add(component_to)
        session.add(related_to)
        session.add(relation_from)
        session.add(relation_to)

        result = prepared_transformation.transform(component_from.component_nomn)

        assert result == component_to.component_nomn
        assert test_redis.exists('from_1', 'to_2', 'from_3', 'to_4') == 4

    session.close()


def test_transform_select_with_closest_popularity(
        make_migrations,
        test_redis,
        prepared_transformation
):
    test_redis.flushall()
    session = DatabaseHelper().get_session()
    session.begin()
    component_from = Component(
        id=1,
        type='name',
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    component = Component(
        id=2,
        type='name',
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=120
    )
    component_to = Component(
        id=3,
        type='name',
        component_nomn='Виктор',
        component_gent='Виктора',
        component_datv='Виктору',
        component_accs='Виктора',
        component_ablt='Виктором',
        component_loct='Викторе',
        gender='masc',
        popularity=102
    )

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(component_from)
        session.add(component_to)
        session.add(component)

        result = prepared_transformation.transform(component_from.component_nomn)

        assert result == component_to.component_nomn
        assert test_redis.exists('from_1', 'to_3') == 2

    session.close()


def test_transform_get_from_cache(
        make_migrations,
        test_redis,
        prepared_transformation
):
    test_redis.flushall()
    session = DatabaseHelper().get_session()
    session.begin()
    component_from = Component(
        id=1,
        type='name',
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    component = Component(
        id=2,
        type='name',
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=120
    )
    component_to = Component(
        id=3,
        type='name',
        component_nomn='Виктор',
        component_gent='Виктора',
        component_datv='Виктору',
        component_accs='Виктора',
        component_ablt='Виктором',
        component_loct='Викторе',
        gender='masc',
        popularity=102
    )

    test_redis.set('from_1', '2')
    test_redis.set('to_2', '1')
    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(component_from)
        session.add(component_to)
        session.add(component)

        result = prepared_transformation.transform(component_from.component_nomn)

        assert result == component.component_nomn
        assert test_redis.exists('from_1', 'to_2') == 2

    session.close()


def test_not_found(
        make_migrations,
        test_redis,
        prepared_transformation
):
    test_redis.flushall()
    session = DatabaseHelper().get_session()
    session.begin()

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        result = prepared_transformation.transform("Сергей")

        assert result != "Сергей"

    session.close()


def test_several_components(
        make_migrations,
        test_redis,
        prepared_transformation
):
    test_redis.flushall()
    session = DatabaseHelper().get_session()
    session.begin()
    name_component_from = Component(
        id=1,
        type='name',
        component_nomn='Сергей',
        component_gent='Сергея',
        component_datv='Сергею',
        component_accs='Сергея',
        component_ablt='Сергеем',
        component_loct='Сергее',
        gender='masc',
        popularity=100
    )
    name_component_to = Component(
        id=2,
        type='name',
        component_nomn='Иван',
        component_gent='Ивана',
        component_datv='Ивану',
        component_accs='Ивана',
        component_ablt='Иваном',
        component_loct='Иване',
        gender='masc',
        popularity=120
    )
    surname_component_from = Component(
        id=3,
        type='surname',
        component_nomn='Егоров',
        component_gent='Егорова',
        component_datv='Егорову',
        component_accs='Егорова',
        component_ablt='Егоровым',
        component_loct='Егорове',
        gender='masc',
        popularity=102
    )
    surname_component_to = Component(
        id=4,
        type='surname',
        component_nomn='Иванов',
        component_gent='Иванова',
        component_datv='Иванову',
        component_accs='Иванова',
        component_ablt='Ивановым',
        component_loct='Иванове',
        gender='masc',
        popularity=102
    )

    with (patch('config.connection.RedisHelper') as mock_redis_helper,
          patch('config.connection.DatabaseHelper') as mock_db_helper):
        mock_redis_helper.get_connection.return_value = test_redis
        mock_db_helper.get_session.return_value = session

        prepared_transformation.redis_helper = mock_redis_helper
        prepared_transformation.database_helper = mock_db_helper

        session.add(name_component_from)
        session.add(name_component_to)
        session.add(surname_component_from)
        session.add(surname_component_to)

        result = prepared_transformation.transform(
            f'{name_component_from.component_nomn} {surname_component_from.component_nomn}'
        )

        assert result == f'{name_component_to.component_nomn} {surname_component_to.component_nomn}'
        assert test_redis.exists('from_1', 'to_2', 'from_3', 'to_4') == 4

    session.close()
