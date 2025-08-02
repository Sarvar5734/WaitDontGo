#!/usr/bin/env python3
"""
Create database tables for Alt3r Bot
"""

import os
from models import create_tables

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")