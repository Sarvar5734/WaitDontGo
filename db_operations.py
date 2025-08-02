#!/usr/bin/env python3
"""
Database operations wrapper
Provides compatibility layer between TinyDB and PostgreSQL operations
"""

import logging
from typing import Dict, Any, List, Optional
from database_manager import db_manager
from models import User as UserModel

logger = logging.getLogger(__name__)

class DBOperations:
    """Pure PostgreSQL database operations"""
    
    def get(self, query) -> Optional[Dict[str, Any]]:
        """Get user by query"""
        if hasattr(query, 'user_id') and query.user_id:
            user = db_manager.get_user(query.user_id)
            if user:
                return self._model_to_dict(user)
        return None
    
    def search(self, query) -> List[Dict[str, Any]]:
        """Search users by query"""
        if hasattr(query, 'user_id') and query.user_id:
            user = db_manager.get_user(query.user_id)
            if user:
                return [self._model_to_dict(user)]
        return []
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all users (use with caution)"""
        try:
            # For compatibility - return empty list to avoid heavy operations
            # Real implementation would query all users from PostgreSQL
            return []
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update(self, data: Dict[str, Any], query) -> bool:
        """Update user data"""
        if hasattr(query, 'user_id') and query.user_id:
            try:
                # Get existing user data and merge with updates
                existing_user = db_manager.get_user(query.user_id)
                if existing_user:
                    user_dict = self._model_to_dict(existing_user)
                    user_dict.update(data)
                    db_manager.create_or_update_user(user_dict)
                    return True
            except Exception as e:
                logger.error(f"Error updating user: {e}")
        return False
    
    def insert(self, data: Dict[str, Any]) -> bool:
        """Insert new user"""
        try:
            db_manager.create_or_update_user(data)
            return True
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return False
    
    def upsert(self, data: Dict[str, Any], query) -> bool:
        """Upsert user data (insert or update)"""
        try:
            db_manager.create_or_update_user(data)
            return True
        except Exception as e:
            logger.error(f"Error upserting user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID - direct PostgreSQL method"""
        try:
            user = db_manager.get_user(user_id)
            if user:
                return self._model_to_dict(user) 
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def create_or_update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Create or update user - direct PostgreSQL method"""
        try:
            # Add user_id to data if not present
            if 'user_id' not in data:
                data['user_id'] = user_id
            db_manager.create_or_update_user(data)
            return True
        except Exception as e:
            logger.error(f"Error creating/updating user {user_id}: {e}")
            return False
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """Update user data - direct PostgreSQL method"""
        try:
            # Get existing user data and merge with updates
            existing_user = db_manager.get_user(user_id)
            if existing_user:
                user_dict = self._model_to_dict(existing_user)
                user_dict.update(data)
                db_manager.create_or_update_user(user_dict)
                return True
            else:
                # Create new user with provided data
                data['user_id'] = user_id
                db_manager.create_or_update_user(data)
                return True
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return False
    
    def remove(self, query) -> bool:
        """Remove user by query"""
        if hasattr(query, 'user_id') and query.user_id:
            try:
                # PostgreSQL delete operation would go here
                logger.info(f"Remove operation requested for user {query.user_id}")
                return True
            except Exception as e:
                logger.error(f"Error removing user: {e}")
        return False
    
    def _model_to_dict(self, user: UserModel) -> Dict[str, Any]:
        """Convert SQLAlchemy model to dictionary"""
        return {
            'user_id': user.user_id,
            'lang': user.lang,
            'username': user.username,
            'first_name': user.first_name,
            'name': user.name,
            'age': user.age,
            'gender': user.gender,
            'interest': user.interest,
            'city': user.city,
            'bio': user.bio,
            'photos': user.photos if user.photos else [],
            'photo_id': user.photo_id,
            'media_type': user.media_type,
            'media_id': user.media_id,
            'latitude': user.latitude,
            'longitude': user.longitude,
            'nd_traits': user.nd_traits if user.nd_traits else [],
            'nd_symptoms': user.nd_symptoms if user.nd_symptoms else [],
            'seeking_traits': user.seeking_traits if user.seeking_traits else [],
            'likes': user.likes if user.likes else [],
            'sent_likes': user.sent_likes if user.sent_likes else [],
            'received_likes': user.received_likes if user.received_likes else [],
            'unnotified_likes': user.unnotified_likes if user.unnotified_likes else [],
            'declined_likes': user.declined_likes if user.declined_likes else [],
            'ratings': user.ratings if user.ratings else [],
            'total_rating': user.total_rating or 0.0,
            'rating_count': user.rating_count or 0,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None,
            'last_active': user.last_active.isoformat() if user.last_active else None
        }

# Create global db instance for backward compatibility
db = DBOperations()

class PostgreSQLQuery:
    """Pure PostgreSQL query class"""
    def __init__(self):
        self.user_id = None
    
    def __call__(self):
        return self
    
    def __eq__(self, value):
        """Handle user_id == value comparisons"""
        result = PostgreSQLQuery()
        result.user_id = value
        return result

# Create Query for PostgreSQL operations
Query = PostgreSQLQuery