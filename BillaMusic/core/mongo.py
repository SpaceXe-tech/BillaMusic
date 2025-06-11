import logging

from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_DB_URI

meow = AsyncIOMotorClient(MONGO_DB_URI)
mongodb = meow.billamusic
logging.info("Space-X Database From MongoDB Connected Successfully.")
