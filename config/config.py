import os

MODEL_PATH = os.getenv("MODEL_PATH", "ru_core_news_sm")
YEAR_DELTA = os.getenv("YEAR_DELTA", 2)
CHUNK = int(os.getenv('CHUNK', 200))

REDIS_FROM_PREFIX = os.getenv('REDIS_FROM_PREFIX', 'from_')
REDIS_TO_PREFIX = os.getenv('REDIS_TO_PREFIX', 'to_')
REDIS_TTL = int(os.getenv('REDIS_TTL', 3600))

SAR_HOST = os.getenv('SAR_HOST', 'localhost')
SAR_MASTER_KEY = os.getenv('SAR_MASTER_KEY')
MAX_LEVEL = int(os.getenv('MAX_LEVEL', 6))

