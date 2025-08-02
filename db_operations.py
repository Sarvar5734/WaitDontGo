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
    """Database operations wrapper for backward compatibility"""
    
    def get(self, query) -> Optional[Dict[str, Any]]:
        """Get user by query (TinyDB compatibility)"""
        if hasattr(query, 'user_id') and query.user_id:
            user = db_manager.get_user(query.user_id)
            if user:
                return self._model_to_dict(user)
        return None
    
    def search(self, query) -> List[Dict[str, Any]]:
        """Search users by query (TinyDB compatibility)"""
        # For now, return empty list - will implement specific searches as needed
        return []
    
    def all(self) -> List[Dict[str, Any]]:
        """Get all users"""
        # This should be used carefully - mainly for migration
        return []
    
    def update(self, data: Dict[str, Any], query) -> bool:
        """Update user data"""
        if hasattr(query, 'user_id') and query.user_id:
            try:
                user = db_manager.get_user(query.user_id)
                if user:
                    # Update the user data
                    for key, value in data.items():
                        if hasattr(user, key):
                            setattr(user, key, value)
                    
                    # Save changes
                    db_manager.create_or_update_user(self._model_to_dict(user))
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

class QueryCompatibility:
    """TinyDB Query compatibility class"""
    def __init__(self):
        self.user_id = None
    
    def __call__(self):
        return self

# Create Query compatibility
Query = QueryCompatibility