"""
Database models and operations for Alt3r Bot
Handles all database interactions and user data management.
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ===== DATABASE MODELS =====

class User(Base):
    """User model for storing user profiles and preferences."""
    
    __tablename__ = 'users'
    
    # Primary identifiers
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    
    # User preferences
    language = Column(String(5), default='en')
    
    # Profile information
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))  # 'girl', 'boy'
    interest = Column(String(10))  # 'girls', 'boys', 'all'
    city = Column(String(100))
    bio = Column(Text)
    photos = Column(JSON, default=list)  # List of photo file_ids
    
    # Profile status
    profile_complete = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    # Dating interactions
    likes_sent = Column(JSON, default=list)  # List of user_ids
    likes_received = Column(JSON, default=list)  # List of user_ids
    matches = Column(JSON, default=list)  # List of user_ids
    
    # Neurodivergent traits
    nd_traits = Column(JSON, default=list)  # List of trait keys
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Feedback(Base):
    """Feedback model for storing user feedback and support requests."""
    
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    feedback_type = Column(String(50))  # 'bug', 'feature', 'general', etc.
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
Base.metadata.create_all(engine)

# ===== DATABASE OPERATIONS =====

def get_db_session() -> Session:
    """
    Get a new database session.
    
    Returns:
        SQLAlchemy session instance
    """
    return SessionLocal()

def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get user by Telegram user ID.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        User instance or None if not found
    """
    with get_db_session() as session:
        return session.query(User).filter(User.user_id == user_id).first()

def save_user_data(user_id: int, data: Dict[str, Any]) -> User:
    """
    Save or update user data in database.
    
    Args:
        user_id: Telegram user ID
        data: Dictionary of user data to save
        
    Returns:
        Updated User instance
    """
    with get_db_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if user:
            # Update existing user
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = User(user_id=user_id, **data)
            session.add(user)
        
        session.commit()
        session.refresh(user)
        return user

def get_potential_matches(user_id: int, limit: int = 50) -> List[User]:
    """
    Get potential matches for a user based on their preferences.
    
    Args:
        user_id: Telegram user ID of the current user
        limit: Maximum number of profiles to return
        
    Returns:
        List of User instances representing potential matches
    """
    with get_db_session() as session:
        current_user = session.query(User).filter(User.user_id == user_id).first()
        if not current_user:
            return []
        
        user_interest = current_user.interest if current_user.interest else 'all'
        user_gender = current_user.gender if current_user.gender else 'unknown'
        
        # Find all active, complete profiles except current user
        all_users = session.query(User).filter(
            User.user_id != user_id,
            User.profile_complete.is_(True),
            User.active.is_(True)
        ).limit(limit).all()
        
        # Filter for compatibility
        potential_matches = []
        for user in all_users:
            other_gender = user.gender if user.gender else 'unknown'
            other_interest = user.interest if user.interest else 'all'
            
            # Check compatibility logic
            compatible = False
            
            if user_interest == 'all' or other_interest == 'all':
                compatible = True
            elif user_interest == 'girls' and other_gender == 'girl':
                if other_interest == 'all' or (other_interest == 'boys' and user_gender == 'boy'):
                    compatible = True
            elif user_interest == 'boys' and other_gender == 'boy':
                if other_interest == 'all' or (other_interest == 'girls' and user_gender == 'girl'):
                    compatible = True
            
            if compatible:
                potential_matches.append(user)
        
        return potential_matches

def update_user_likes(user_id: int, target_user_id: int) -> Dict[str, Any]:
    """
    Handle like interaction between users and check for matches.
    
    Args:
        user_id: ID of user giving the like
        target_user_id: ID of user receiving the like
        
    Returns:
        Dictionary with interaction result and match status
    """
    with get_db_session() as session:
        current_user = session.query(User).filter(User.user_id == user_id).first()
        target_user = session.query(User).filter(User.user_id == target_user_id).first()
        
        if not current_user or not target_user:
            return {'success': False, 'error': 'User not found'}
        
        # Add to current user's likes_sent
        likes_sent = current_user.likes_sent if current_user.likes_sent else []
        if target_user_id not in likes_sent:
            likes_sent.append(target_user_id)
            current_user.likes_sent = likes_sent
        
        # Add to target user's likes_received
        likes_received = target_user.likes_received if target_user.likes_received else []
        if user_id not in likes_received:
            likes_received.append(user_id)
            target_user.likes_received = likes_received
        
        # Check for mutual like (match)
        target_likes_sent = target_user.likes_sent if target_user.likes_sent else []
        is_match = user_id in target_likes_sent
        
        if is_match:
            # Add to matches for both users
            current_matches = current_user.matches if current_user.matches else []
            if target_user_id not in current_matches:
                current_matches.append(target_user_id)
                current_user.matches = current_matches
            
            target_matches = target_user.matches if target_user.matches else []
            if user_id not in target_matches:
                target_matches.append(user_id)
                target_user.matches = target_matches
        
        session.commit()
        
        return {
            'success': True,
            'is_match': is_match,
            'target_name': target_user.name
        }

def save_feedback(user_id: int, feedback_type: str, content: str) -> Feedback:
    """
    Save user feedback to database.
    
    Args:
        user_id: Telegram user ID
        feedback_type: Type of feedback ('bug', 'feature', 'general', etc.)
        content: Feedback content
        
    Returns:
        Feedback instance
    """
    with get_db_session() as session:
        feedback = Feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            content=content
        )
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        return feedback

def get_user_stats() -> Dict[str, int]:
    """
    Get basic user statistics.
    
    Returns:
        Dictionary with user statistics
    """
    with get_db_session() as session:
        total_users = session.query(User).count()
        active_users = session.query(User).filter(User.active.is_(True)).count()
        complete_profiles = session.query(User).filter(User.profile_complete.is_(True)).count()
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'complete_profiles': complete_profiles
        }