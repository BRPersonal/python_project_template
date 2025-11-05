from databases import Database
from .config import settings
from .logger import logger
from typing import Dict,Optional,Any

class PostgreDbManager:
    def __init__(self):
        self.database = None

    async def connect(self):
        try:
            logger.info(f"Connecting to Postgre database:{settings.POSTGRE_DATABASE}")
            if not self.database:
                self.database = Database(settings.postgre_db_url)
            await self.database.connect()
        except Exception as e:
            logger.error(f"Failed to connect to Postgre: {str(e)}")
            raise

    async def disconnect(self):
        if self.database:
            await self.database.disconnect()
            self.database = None
            logger.info("PostGre connection closed")

    async def health_check(self) -> bool:
        try:
            if self.database:
                await self.database.fetch_val("SELECT 1")
                return True
            return False
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {str(e)}")
            return False

    async def execute(self,query:str, values: Optional[Dict[str,Any]] = None):
        await self.database.execute(query=query, values=values)

    async def fetch_one(self,query:str, values: Optional[Dict[str,Any]] = None):
        return await self.database.fetch_one(query=query, values=values)

    async def fetch_all(self,query:str,values: Optional[Dict[str,Any]] = None):
        return await self.database.fetch_all(query=query, values=values)

#global instance
postgre_manager = PostgreDbManager()

