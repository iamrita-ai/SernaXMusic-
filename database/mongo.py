"""
Thin async MongoDB layer (motor). If MONGO_URI is not set, everything
falls back to a simple in-process set so the bot still runs — you just
lose persistence of broadcast lists across restarts.
"""

from config import MONGO_URI, DB_ENABLED

_users_fallback: set[int] = set()
_chats_fallback: set[int] = set()

client = None
db = None
users_col = None
chats_col = None

if DB_ENABLED:
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(MONGO_URI)
    db = client["serenaxmusic"]
    users_col = db["users"]
    chats_col = db["chats"]


async def add_served_user(user_id: int):
    if DB_ENABLED:
        await users_col.update_one(
            {"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True
        )
    else:
        _users_fallback.add(user_id)


async def add_served_chat(chat_id: int):
    if DB_ENABLED:
        await chats_col.update_one(
            {"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True
        )
    else:
        _chats_fallback.add(chat_id)


async def get_served_users() -> list[int]:
    if DB_ENABLED:
        return [doc["user_id"] async for doc in users_col.find({})]
    return list(_users_fallback)


async def get_served_chats() -> list[int]:
    if DB_ENABLED:
        return [doc["chat_id"] async for doc in chats_col.find({})]
    return list(_chats_fallback)
