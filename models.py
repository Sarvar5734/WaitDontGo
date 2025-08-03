#!/usr/bin/env python3
"""
Database models for Alt3r Bot
PostgreSQL models using SQLAlchemy
"""

import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)
    lang = Column(String(5), default='ru')
    username = Column(String(100))
    first_name = Column(String(100))
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))  # male, female, other
    interest = Column(String(10))  # male, female, both
    city = Column(String(100))
    bio = Column(Text)
    
    # Photo storage - array of Telegram file IDs
    photos = Column(JSON, default=list)
    photo_id = Column(String(200))  # Primary photo
    media_type = Column(String(20), default='photo')
    media_id = Column(String(200))
    
    # Location data
    latitude = Column(Float)
    longitude = Column(String(50))
    
    # Neurodivergent traits and symptoms
    nd_traits = Column(JSON, default=list)
    nd_symptoms = Column(JSON, default=list)
    seeking_traits = Column(JSON, default=list)
    
    # Dating interactions
    likes = Column(JSON, default=list)
    sent_likes = Column(JSON, default=list)
    received_likes = Column(JSON, default=list)
    unnotified_likes = Column(JSON, default=list)
    declined_likes = Column(JSON, default=list)
    
    # Rating system
    ratings = Column(JSON, default=list)
    total_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, name='{self.name}')>"

class Feedback(Base):
    __tablename__ = 'feedback'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Feedback(user_id={self.user_id}, resolved={self.resolved})>"

class AISession(Base):
    __tablename__ = 'ai_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_date = Column(DateTime, default=datetime.utcnow)
    message_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AISession(user_id={self.user_id}, messages={self.message_count})>"

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(
    DATABASE_URL,
    pool_size=30,              # Increased pool size for maximum concurrency
    max_overflow=70,           # Higher overflow for peak usage
    pool_recycle=1200,         # Recycle every 20 minutes for optimal performance
    pool_pre_ping=True,        # Validate connections before use (prevents SSL errors)
    pool_timeout=5,            # Even faster timeout for getting connections
    echo=False,
    connect_args={
        "connect_timeout": 3,   # Ultra-fast connection timeout
        "application_name": "alt3r_bot_ultra_optimized",
        "options": "-c statement_timeout=8s"  # Fast query timeout
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()