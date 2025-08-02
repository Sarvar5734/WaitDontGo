#!/usr/bin/env python3
"""
Database operations manager for Alt3r Bot
Handles PostgreSQL operations and data migration from TinyDB
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import User, Feedback, AISession, engine, SessionLocal, create_tables
try:
    from tinydb import TinyDB, Query
except ImportError:
    # TinyDB not available, migration will be skipped
    TinyDB = None
    Query = None

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # Create tables if they don't exist
        create_tables()
        
    def get_session(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def migrate_from_tinydb(self, tinydb_path: str = "db.json", feedback_path: str = "feedback.json") -> bool:
        """Migrate data from TinyDB to PostgreSQL"""
        if TinyDB is None:
            logger.warning("TinyDB not available, skipping migration")
            return True
            
        try:
            # Check if files exist
            import os
            if not os.path.exists(tinydb_path):
                logger.info("TinyDB file not found, skipping migration")
                return True
                
            # Load TinyDB data
            tiny_db = TinyDB(tinydb_path)
            feedback_db = TinyDB(feedback_path) if os.path.exists(feedback_path) else None
            
            session = self.get_session()
            
            # Migrate users
            users_data = tiny_db.all()
            migrated_users = 0
            
            for user_data in users_data:
                # Check if user already exists
                existing_user = session.query(User).filter(User.user_id == user_data.get('user_id')).first()
                if existing_user:
                    logger.info(f"User {user_data.get('user_id')} already exists, skipping")
                    continue
                
                # Create new user
                user = User(
                    user_id=user_data.get('user_id'),
                    lang=user_data.get('lang', 'ru'),
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    name=user_data.get('name'),
                    age=user_data.get('age'),
                    gender=user_data.get('gender'),
                    interest=user_data.get('interest'),
                    city=user_data.get('city'),
                    bio=user_data.get('bio'),
                    photos=user_data.get('photos', []),
                    photo_id=user_data.get('photo_id'),
                    media_type=user_data.get('media_type', 'photo'),
                    media_id=user_data.get('media_id'),
                    latitude=user_data.get('latitude'),
                    longitude=user_data.get('longitude'),
                    nd_traits=user_data.get('nd_traits', []),
                    nd_symptoms=user_data.get('nd_symptoms', []),
                    seeking_traits=user_data.get('seeking_traits', []),
                    likes=user_data.get('likes', []),
                    sent_likes=user_data.get('sent_likes', []),
                    received_likes=user_data.get('received_likes', []),
                    unnotified_likes=user_data.get('unnotified_likes', []),
                    declined_likes=user_data.get('declined_likes', []),
                    ratings=user_data.get('ratings', []),
                    total_rating=user_data.get('total_rating', 0.0),
                    rating_count=user_data.get('rating_count', 0),
                    created_at=datetime.fromisoformat(user_data.get('created_at', datetime.utcnow().isoformat())),
                    last_active=datetime.utcnow()
                )
                
                session.add(user)
                migrated_users += 1
                logger.info(f"Migrated user: {user_data.get('name')} ({user_data.get('user_id')})")
            
            # Migrate feedback
            migrated_feedback = 0
            if feedback_db:
                feedback_data = feedback_db.all()
                
                for feedback_item in feedback_data:
                    existing_feedback = session.query(Feedback).filter(
                    and_(
                        Feedback.user_id == feedback_item.get('user_id'),
                        Feedback.message == feedback_item.get('message')
                    )
                    ).first()
                    
                    if existing_feedback:
                        continue
                        
                    feedback = Feedback(
                    user_id=feedback_item.get('user_id'),
                    message=feedback_item.get('message'),
                    created_at=datetime.fromisoformat(feedback_item.get('created_at', datetime.utcnow().isoformat())),
                        resolved=feedback_item.get('resolved', False)
                    )
                
                    session.add(feedback)
                    migrated_feedback += 1
            
            session.commit()
            session.close()
            
            logger.info(f"Migration completed: {migrated_users} users, {migrated_feedback} feedback items")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by Telegram user ID"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user
        finally:
            session.close()
    
    def create_or_update_user(self, user_data: Dict[str, Any]) -> User:
        """Create new user or update existing"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.user_id == user_data['user_id']).first()
            
            if user:
                # Update existing user
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                # updated_at will be handled by SQLAlchemy onupdate
            else:
                # Create new user
                user = User(**user_data)
                session.add(user)
            
            session.commit()
            session.refresh(user)
            return user
        finally:
            session.close()
    
    def get_browsable_profiles(self, current_user_id: int, limit: int = 10) -> List[User]:
        """Get profiles for browsing (excluding current user and already interacted)"""
        session = self.get_session()
        try:
            current_user = session.query(User).filter(User.user_id == current_user_id).first()
            if not current_user:
                return []
            
            # Get users to exclude (already liked or declined)
            excluded_ids = (current_user.sent_likes or []) + (current_user.declined_likes or []) + [current_user_id]
            
            # Build query filters
            query_filters = [
                ~User.user_id.in_(excluded_ids),
                User.name.isnot(None),
                User.age.isnot(None),
                User.bio.isnot(None)
            ]
            
            # Add gender filter based on interest
            if current_user.interest == 'male':
                query_filters.append(User.gender == 'male')
            elif current_user.interest == 'female':
                query_filters.append(User.gender == 'female')
            else:  # both
                query_filters.append(User.gender.in_(['male', 'female']))
            
            profiles = session.query(User).filter(and_(*query_filters)).limit(limit).all()
            
            return profiles
        finally:
            session.close()
    
    def add_like(self, liker_id: int, liked_id: int) -> bool:
        """Add a like interaction"""
        session = self.get_session()
        try:
            # Update liker's sent_likes
            liker = session.query(User).filter(User.user_id == liker_id).first()
            if liker:
                sent_likes = liker.sent_likes if liker.sent_likes else []
                if liked_id not in sent_likes:
                    sent_likes.append(liked_id)
                    liker.sent_likes = sent_likes
                    session.merge(liker)
            
            # Update liked user's received_likes and unnotified_likes
            liked_user = session.query(User).filter(User.user_id == liked_id).first()
            if liked_user:
                received_likes = liked_user.received_likes if liked_user.received_likes else []
                unnotified_likes = liked_user.unnotified_likes if liked_user.unnotified_likes else []
                
                if liker_id not in received_likes:
                    received_likes.append(liker_id)
                    liked_user.received_likes = received_likes
                
                if liker_id not in unnotified_likes:
                    unnotified_likes.append(liker_id)
                    liked_user.unnotified_likes = unnotified_likes
                
                session.merge(liked_user)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding like: {e}")
            return False
        finally:
            session.close()
    
    def is_mutual_match(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users have mutual likes"""
        session = self.get_session()
        try:
            user1 = session.query(User).filter(User.user_id == user1_id).first()
            user2 = session.query(User).filter(User.user_id == user2_id).first()
            
            if not user1 or not user2:
                return False
            
            user1_sent = user1.sent_likes if user1.sent_likes else []
            user2_sent = user2.sent_likes if user2.sent_likes else []
            
            return user2_id in user1_sent and user1_id in user2_sent
        finally:
            session.close()
    
    def add_feedback(self, user_id: int, message: str) -> bool:
        """Add user feedback"""
        session = self.get_session()
        try:
            feedback = Feedback(user_id=user_id, message=message)
            session.add(feedback)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding feedback: {e}")
            return False
        finally:
            session.close()
    
    def get_user_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        session = self.get_session()
        try:
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.last_active >= datetime.utcnow().replace(hour=0, minute=0, second=0)).count()
            total_feedback = session.query(Feedback).count()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_feedback': total_feedback
            }
        finally:
            session.close()

# Global database manager instance
db_manager = DatabaseManager()