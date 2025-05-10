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
                username TEXT
            )
            """)
            await db.commit()

    async def test(self):
        async with aiosqlite.connect(self.db_path) as db:

            cursor = await db.cursor()
            query = 'INSERT INTO users (id, username) VALUES (?, ?)'

            await cursor.execute(query, (1, 'хуй'))

            await db.commit()
