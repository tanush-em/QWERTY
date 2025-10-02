"""
Database connection and management for CSE-AIML ERP MCP Server.
"""
import asyncio
import logging
import sys
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
from bson.errors import InvalidId
from config import get_mongo_uri, get_database_name, settings

# Configure logging to stderr to avoid breaking MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB database manager with connection pooling and error handling."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Establish MongoDB connection with proper configuration."""
        try:
            mongo_uri = get_mongo_uri()
            database_name = get_database_name()
            
            # Create MongoDB client with connection pooling
            self.client = MongoClient(
                mongo_uri,
                maxPoolSize=settings.max_connection_pool_size,
                serverSelectionTimeoutMS=settings.connection_timeout,
                connectTimeoutMS=settings.connection_timeout,
                socketTimeoutMS=settings.server_timeout,
                retryWrites=True,
                retryReads=True
            )
            
            # Test connection
            await self._test_connection()
            
            # Get database
            self.database = self.client[database_name]
            self._connected = True
            
            logger.info(f"Successfully connected to MongoDB database: {database_name}")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during MongoDB connection: {e}")
            raise
    
    async def _test_connection(self) -> None:
        """Test MongoDB connection."""
        if not self.client:
            raise ConnectionFailure("MongoDB client not initialized")
        
        # Run connection test in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.client.admin.command, 'ping')
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("MongoDB connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connected
    
    def get_collection(self, collection_name: str) -> Collection:
        """Get MongoDB collection."""
        if self.database is None:
            raise ConnectionFailure("Database not connected")
        return self.database[collection_name]
    
    @asynccontextmanager
    async def get_collection_async(self, collection_name: str):
        """Async context manager for collection operations."""
        if not self.is_connected:
            await self.connect()
        yield self.get_collection(collection_name)


class ObjectIdUtils:
    """Utilities for ObjectId handling."""
    
    @staticmethod
    def is_valid_object_id(object_id: str) -> bool:
        """Check if string is a valid ObjectId."""
        try:
            ObjectId(object_id)
            return True
        except (InvalidId, TypeError):
            return False
    
    @staticmethod
    def to_object_id(object_id: str) -> ObjectId:
        """Convert string to ObjectId."""
        if not ObjectIdUtils.is_valid_object_id(object_id):
            raise InvalidId(f"Invalid ObjectId: {object_id}")
        return ObjectId(object_id)
    
    @staticmethod
    def serialize_object_ids(data: Any) -> Any:
        """Recursively serialize ObjectIds in data structure."""
        if isinstance(data, dict):
            return {
                key: ObjectIdUtils.serialize_object_ids(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [ObjectIdUtils.serialize_object_ids(item) for item in data]
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data


class DatabaseOperations:
    """High-level database operations with error handling."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document with error handling."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, collection.find_one, query)
            return ObjectIdUtils.serialize_object_ids(result) if result else None
        except Exception as e:
            logger.error(f"Error finding document in {collection_name}: {e}")
            raise
    
    async def find_many(
        self, 
        collection_name: str, 
        query: Dict[str, Any] = None,
        skip: int = 0,
        limit: int = None,
        sort: List[tuple] = None
    ) -> List[Dict[str, Any]]:
        """Find multiple documents with pagination."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            
            cursor = collection.find(query or {})
            
            if sort:
                cursor = cursor.sort(sort)
            
            if skip:
                cursor = cursor.skip(skip)
            
            if limit:
                cursor = cursor.limit(limit)
            
            results = await loop.run_in_executor(None, list, cursor)
            return ObjectIdUtils.serialize_object_ids(results)
            
        except Exception as e:
            logger.error(f"Error finding documents in {collection_name}: {e}")
            raise
    
    async def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert one document."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, collection.insert_one, document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document in {collection_name}: {e}")
            raise
    
    async def update_one(
        self, 
        collection_name: str, 
        query: Dict[str, Any], 
        update: Dict[str, Any]
    ) -> bool:
        """Update one document."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, collection.update_one, query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            raise
    
    async def delete_one(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete one document."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, collection.delete_one, query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document in {collection_name}: {e}")
            raise
    
    async def delete_many(self, collection_name: str, query: Dict[str, Any] = None) -> int:
        """Delete multiple documents."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, collection.delete_many, query or {})
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents in {collection_name}: {e}")
            raise
    
    async def count_documents(self, collection_name: str, query: Dict[str, Any] = None) -> int:
        """Count documents matching query."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, collection.count_documents, query or {})
        except Exception as e:
            logger.error(f"Error counting documents in {collection_name}: {e}")
            raise
    
    async def aggregate(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline."""
        try:
            collection = self.db_manager.get_collection(collection_name)
            loop = asyncio.get_event_loop()
            cursor = collection.aggregate(pipeline)
            results = await loop.run_in_executor(None, list, cursor)
            return ObjectIdUtils.serialize_object_ids(results)
        except Exception as e:
            logger.error(f"Error executing aggregation in {collection_name}: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()
db_operations = DatabaseOperations(db_manager)


async def get_database() -> DatabaseManager:
    """Get database manager instance."""
    if not db_manager.is_connected:
        await db_manager.connect()
    return db_manager


async def get_db_operations() -> DatabaseOperations:
    """Get database operations instance."""
    if not db_manager.is_connected:
        await db_manager.connect()
    return db_operations
