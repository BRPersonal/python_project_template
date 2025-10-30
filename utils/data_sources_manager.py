from .mongo_db_manager import mongodb_manager
from .postgre_db_manager import postgre_manager
from .logger import logger
from typing import Dict, Any

class DataSourcesManager:
    """
    Unified database manager for both MongoDB and PostgreSQL
    """
    def __init__(self):
        self.mongodb = mongodb_manager
        self.postgresql = postgre_manager
        self.is_connected = False

    async def connect_all(self):
        """
        Connect to both MongoDB and PostgreSQL databases
        """
        try:
            logger.info("Initializing database connections...")

            # Connect to MongoDB
            await self.mongodb.connect()

            # Connect to PostgreSQL
            await self.postgresql.connect()

            self.is_connected = True
            logger.info("All database connections established successfully")

        except Exception as e:
            logger.error(f"Failed to establish database connections: {str(e)}")
            await self.disconnect_all()
            raise

    async def disconnect_all(self):
        """
        Disconnect from both databases
        """
        try:
            if self.mongodb:
                await self.mongodb.disconnect()
                self.mongodb = None

            if self.postgresql:
                await self.postgresql.disconnect()
                self.postgresql = None

            self.is_connected = False
            logger.info("All database connections closed")

        except Exception as e:
            logger.error(f"Error during database disconnection: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on both databases
        """
        mongodb_status = await self.mongodb.health_check()
        postgresql_status = await self.postgresql.health_check()

        return {
            "mongodb": {
                "status": "healthy" if mongodb_status else "unhealthy",
                "connected": mongodb_status
            },
            "postgresql": {
                "status": "healthy" if postgresql_status else "unhealthy",
                "connected": postgresql_status
            },
            "overall_status": "healthy" if (mongodb_status and postgresql_status) else "degraded"
        }

#global instance
data_sources_manager = DataSourcesManager()