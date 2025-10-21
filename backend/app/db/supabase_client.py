"""Supabase database client"""

from supabase import create_client, Client
from typing import Optional, Dict, List
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Supabase database client"""
    
    _instance: Optional['SupabaseClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            logger.info("Initializing Supabase client")
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {e}", exc_info=True)
            raise
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    async def insert(self, table: str, data: Dict) -> Dict:
        """Insert data into table"""
        try:
            result = self.client.table(table).insert(data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}", exc_info=True)
            raise
    
    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Select data from table"""
        try:
            query = self.client.table(table).select(columns)
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}", exc_info=True)
            raise
    
    async def update(
        self,
        table: str,
        data: Dict,
        filters: Dict
    ) -> Dict:
        """Update data in table"""
        try:
            query = self.client.table(table).update(data)
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            result = query.execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error updating {table}: {e}", exc_info=True)
            raise
    
    async def delete(self, table: str, filters: Dict) -> bool:
        """Delete data from table"""
        try:
            query = self.client.table(table).delete()
            
            for key, value in filters.items():
                query = query.eq(key, value)
            
            query.execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting from {table}: {e}", exc_info=True)
            raise


# Create singleton instance
supabase_client = SupabaseClient()

