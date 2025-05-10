import aiosqlite
from pathlib import Path
from sys import argv


class Database:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._connection = None
        return cls._instance

    def __init__(self):
        script_dir = Path(argv[0]).parent.resolve()
        db_path = script_dir / 'utils' / 'database.db'
        self.db_path = db_path

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.cursor()

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                userID INTEGER,
                chats_topics TEXT
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY,
                creator_id INTEGER,
                topic_theme TEXT
            )
            """)

            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY,
                chat_name TEXT,
                topic_id INTEGER,
                creator_id INTEGER,
                chat_link TEXT,
                FOREIGN KEY(topic_id) REFERENCES topics(id)
            )
            """)

            await db.commit()

    async def register_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()

            await cursor.execute("SELECT id FROM users WHERE userID = ?", (user_id,))
            result = await cursor.fetchone()

            if not result:
                await cursor.execute("INSERT INTO users (userID) VALUES (?)", (user_id,))
            else:
                pass

            await db.commit()

    async def register_chat(self, topic_id, creator_id, chat_link, chat_name):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("PRAGMA foreign_keys = ON;")

            await cursor.execute(
                "INSERT INTO chats (topic_id, creator_id, chat_link, chat_name) VALUES (?, ?, ?, ?)",
                (topic_id, creator_id, chat_link, chat_name)
            )

            await db.commit()

    async def get_topics(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()

            await cursor.execute("SELECT topic_theme, id FROM topics")
            result = await cursor.fetchall()

            if result:
                return [{"text": row[0], "id": row[1], } for row in result]

    async def get_topic_chats(self, topicID):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()

            await cursor.execute("SELECT chat_name, chat_link FROM chats WHERE topic_id = ?", (topicID,))
            result = await cursor.fetchall()

            if result:
                return [{"title": row[0], "link": row[1]} for row in result]

    async def register_topic(self, topic_theme, creator_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()

            await cursor.execute(
                "INSERT INTO topics (topic_theme, creator_id) VALUES (?, ?)",
                (topic_theme, creator_id)
            )

            await db.commit()

    async def get_chat_link_by_id(self, chat_id: int) -> str:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.cursor()

            await cursor.execute("SELECT chat_link FROM chats WHERE id = ?", (chat_id,))
            result = await cursor.fetchone()

            if result:
                return result[0]
