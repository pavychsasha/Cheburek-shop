from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

mongo_client = AsyncIOMotorClient(settings.mongo_db.url)
db = mongo_client[settings.mongo_db.database_name]
carts_collection = db[settings.mongo_db.collections.carts]
