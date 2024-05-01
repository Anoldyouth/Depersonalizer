import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import redis


class DatabaseHelper:
    def __init__(self):
        self.db_config = {
            "driver": os.getenv("DB_DRIVER", "postgresql"),
            "username": os.getenv("DB_USERNAME", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
            "host": os.getenv("DB_HOST", "127.0.0.1"),
            "port": os.getenv("DB_PORT", "5432"),
            "database": os.getenv("DB_NAME", "postgres"),
        }

    def get_url(self):
        return (f"{self.db_config['driver']}://{self.db_config['username']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")

    def get_session(self):
        engine = create_engine(self.get_url())
        session = sessionmaker(bind=engine)

        return session()


class RedisHelper:
    def __init__(self):
        self.redis_config = {
            "host": os.getenv("REDIS_HOST", "127.0.0.1"),
            "port": os.getenv("REDIS_PORT", "6379"),
            "db": os.getenv("REDIS_DB", "0"),
            "password": os.getenv("REDIS_PASSWORD", "pass"),
        }

    def get_connection(self) -> redis.Redis:
        return redis.StrictRedis(
            host=self.redis_config["host"],
            port=self.redis_config["port"],
            db=self.redis_config["db"],
            password=self.redis_config["password"],
        )
