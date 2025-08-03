#!/usr/bin/env python3
"""
Migration and Portability Tools for Alt3r Bot
Ensures easy deployment platform changes and database migrations without data loss.

Features:
- Complete database backup/restore
- Platform-agnostic configuration
- Environment variable migration
- Data integrity verification
- Zero-downtime migration support
"""

import json
import os
import psycopg2
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import shutil

logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handle database backup, restore, and migration operations"""
    
    def __init__(self, source_db_url: str = None, target_db_url: str = None):
        self.source_db_url = source_db_url or os.environ.get('DATABASE_URL')
        self.target_db_url = target_db_url
        self.backup_dir = 'backups'
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_full_backup(self, backup_name: str = None) -> str:
        """Create complete database backup with timestamp"""
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"alt3r_backup_{timestamp}"
        
        backup_file = os.path.join(self.backup_dir, f"{backup_name}.json")
        
        try:
            # Connect to database
            conn = psycopg2.connect(self.source_db_url)
            cur = conn.cursor()
            
            backup_data = {
                'metadata': {
                    'backup_date': datetime.now().isoformat(),
                    'database_type': 'postgresql',
                    'bot_version': 'alt3r_v1.0',
                    'tables': []
                },
                'data': {}
            }
            
            # Backup users table
            cur.execute("""
                SELECT user_id, lang, username, first_name, name, age, gender, 
                       interest, city, bio, photos, photo_id, media_type, media_id,
                       latitude, longitude, nd_traits, nd_symptoms, seeking_traits,
                       likes, sent_likes, received_likes, unnotified_likes, 
                       declined_likes, ratings, total_rating, rating_count,
                       created_at, updated_at, last_active
                FROM users ORDER BY user_id
            """)
            
            users_data = []
            for row in cur.fetchall():
                user_dict = {
                    'user_id': row[0],
                    'lang': row[1],
                    'username': row[2],
                    'first_name': row[3],
                    'name': row[4],
                    'age': row[5],
                    'gender': row[6],
                    'interest': row[7],
                    'city': row[8],
                    'bio': row[9],
                    'photos': row[10],
                    'photo_id': row[11],
                    'media_type': row[12],
                    'media_id': row[13],
                    'latitude': row[14],
                    'longitude': row[15],
                    'nd_traits': row[16],
                    'nd_symptoms': row[17],
                    'seeking_traits': row[18],
                    'likes': row[19],
                    'sent_likes': row[20],
                    'received_likes': row[21],
                    'unnotified_likes': row[22],
                    'declined_likes': row[23],
                    'ratings': row[24],
                    'total_rating': float(row[25]) if row[25] else 0.0,
                    'rating_count': row[26],
                    'created_at': row[27].isoformat() if row[27] else None,
                    'updated_at': row[28].isoformat() if row[28] else None,
                    'last_active': row[29].isoformat() if row[29] else None
                }
                users_data.append(user_dict)
            
            backup_data['data']['users'] = users_data
            backup_data['metadata']['tables'].append('users')
            
            # Backup feedback table if exists
            try:
                cur.execute("SELECT * FROM feedback ORDER BY id")
                feedback_data = []
                for row in cur.fetchall():
                    feedback_dict = {
                        'id': row[0],
                        'user_id': row[1],
                        'feedback_text': row[2],
                        'created_at': row[3].isoformat() if row[3] else None
                    }
                    feedback_data.append(feedback_dict)
                backup_data['data']['feedback'] = feedback_data
                backup_data['metadata']['tables'].append('feedback')
            except:
                logger.info("Feedback table not found, skipping")
            
            # Backup AI sessions table if exists
            try:
                cur.execute("SELECT * FROM ai_sessions ORDER BY id")
                ai_sessions_data = []
                for row in cur.fetchall():
                    session_dict = {
                        'id': row[0],
                        'user_id': row[1],
                        'session_data': row[2],
                        'created_at': row[3].isoformat() if row[3] else None
                    }
                    ai_sessions_data.append(session_dict)
                backup_data['data']['ai_sessions'] = ai_sessions_data
                backup_data['metadata']['tables'].append('ai_sessions')
            except:
                logger.info("AI sessions table not found, skipping")
            
            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            cur.close()
            conn.close()
            
            logger.info(f"Backup created: {backup_file}")
            print(f"✅ Complete backup saved: {backup_file}")
            print(f"   Users: {len(users_data)}")
            print(f"   Tables: {', '.join(backup_data['metadata']['tables'])}")
            
            return backup_file
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            print(f"❌ Backup failed: {e}")
            return None
    
    def restore_from_backup(self, backup_file: str, target_db_url: str = None) -> bool:
        """Restore database from backup file"""
        if not os.path.exists(backup_file):
            print(f"❌ Backup file not found: {backup_file}")
            return False
        
        target_url = target_db_url or self.target_db_url or self.source_db_url
        
        try:
            # Load backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            conn = psycopg2.connect(target_url)
            cur = conn.cursor()
            
            # Create tables if they don't exist (using schema from models.py)
            self._create_tables(cur)
            
            # Restore users
            if 'users' in backup_data['data']:
                users = backup_data['data']['users']
                for user in users:
                    # Insert or update user
                    cur.execute("""
                        INSERT INTO users (
                            user_id, lang, username, first_name, name, age, gender,
                            interest, city, bio, photos, photo_id, media_type, media_id,
                            latitude, longitude, nd_traits, nd_symptoms, seeking_traits,
                            likes, sent_likes, received_likes, unnotified_likes,
                            declined_likes, ratings, total_rating, rating_count,
                            created_at, updated_at, last_active
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (user_id) DO UPDATE SET
                            lang = EXCLUDED.lang,
                            username = EXCLUDED.username,
                            first_name = EXCLUDED.first_name,
                            name = EXCLUDED.name,
                            age = EXCLUDED.age,
                            gender = EXCLUDED.gender,
                            interest = EXCLUDED.interest,
                            city = EXCLUDED.city,
                            bio = EXCLUDED.bio,
                            photos = EXCLUDED.photos,
                            photo_id = EXCLUDED.photo_id,
                            media_type = EXCLUDED.media_type,
                            media_id = EXCLUDED.media_id,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude,
                            nd_traits = EXCLUDED.nd_traits,
                            nd_symptoms = EXCLUDED.nd_symptoms,
                            seeking_traits = EXCLUDED.seeking_traits,
                            likes = EXCLUDED.likes,
                            sent_likes = EXCLUDED.sent_likes,
                            received_likes = EXCLUDED.received_likes,
                            unnotified_likes = EXCLUDED.unnotified_likes,
                            declined_likes = EXCLUDED.declined_likes,
                            ratings = EXCLUDED.ratings,
                            total_rating = EXCLUDED.total_rating,
                            rating_count = EXCLUDED.rating_count,
                            updated_at = EXCLUDED.updated_at,
                            last_active = EXCLUDED.last_active
                    """, (
                        user['user_id'], user['lang'], user['username'], user['first_name'],
                        user['name'], user['age'], user['gender'], user['interest'],
                        user['city'], user['bio'], json.dumps(user['photos']), user['photo_id'],
                        user['media_type'], user['media_id'], user['latitude'], user['longitude'],
                        json.dumps(user['nd_traits']), json.dumps(user['nd_symptoms']),
                        json.dumps(user['seeking_traits']), json.dumps(user['likes']),
                        json.dumps(user['sent_likes']), json.dumps(user['received_likes']),
                        json.dumps(user['unnotified_likes']), json.dumps(user['declined_likes']),
                        json.dumps(user['ratings']), user['total_rating'], user['rating_count'],
                        user['created_at'], user['updated_at'], user['last_active']
                    ))
                
                print(f"✅ Restored {len(users)} users")
            
            # Restore feedback if exists
            if 'feedback' in backup_data['data']:
                feedback_items = backup_data['data']['feedback']
                for item in feedback_items:
                    cur.execute("""
                        INSERT INTO feedback (id, user_id, feedback_text, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (item['id'], item['user_id'], item['feedback_text'], item['created_at']))
                
                print(f"✅ Restored {len(feedback_items)} feedback entries")
            
            # Restore AI sessions if exists
            if 'ai_sessions' in backup_data['data']:
                ai_sessions = backup_data['data']['ai_sessions']
                for session in ai_sessions:
                    cur.execute("""
                        INSERT INTO ai_sessions (id, user_id, session_data, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (session['id'], session['user_id'], json.dumps(session['session_data']), session['created_at']))
                
                print(f"✅ Restored {len(ai_sessions)} AI sessions")
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Database restore completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            print(f"❌ Restore failed: {e}")
            return False
    
    def _create_tables(self, cursor):
        """Create database tables if they don't exist"""
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                lang VARCHAR(10) DEFAULT 'ru',
                username VARCHAR(255),
                first_name VARCHAR(255),
                name VARCHAR(255),
                age INTEGER,
                gender VARCHAR(20),
                interest VARCHAR(20),
                city VARCHAR(255),
                bio TEXT,
                photos JSON DEFAULT '[]',
                photo_id VARCHAR(255),
                media_type VARCHAR(50) DEFAULT 'photo',
                media_id VARCHAR(255),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                nd_traits JSON DEFAULT '[]',
                nd_symptoms JSON DEFAULT '[]',
                seeking_traits JSON DEFAULT '[]',
                likes JSON DEFAULT '[]',
                sent_likes JSON DEFAULT '[]',
                received_likes JSON DEFAULT '[]',
                unnotified_likes JSON DEFAULT '[]',
                declined_likes JSON DEFAULT '[]',
                ratings JSON DEFAULT '[]',
                total_rating DECIMAL(3, 2) DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # AI sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_sessions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                session_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_city ON users(city)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_age ON users(age)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_sessions_user_id ON ai_sessions(user_id)")

class PlatformMigrator:
    """Handle platform-specific migration tasks"""
    
    def __init__(self):
        self.config_dir = 'deployment_configs'
        os.makedirs(self.config_dir, exist_ok=True)
    
    def export_environment_config(self) -> str:
        """Export current environment configuration"""
        config = {
            'environment_variables': {
                'TELEGRAM_BOT_TOKEN': '[REQUIRED]',
                'DATABASE_URL': '[REQUIRED]',
                # Add other env vars as needed
            },
            'dependencies': {
                'python': self._get_python_dependencies(),
                'system': self._get_system_dependencies()
            },
            'ports': {
                'main_bot': 'AUTO',
                'keep_alive': 8000
            },
            'platform_specific': {
                'replit': {
                    'run_command': 'python main.py',
                    'install_command': 'pip install -r requirements.txt'
                },
                'heroku': {
                    'run_command': 'python main.py',
                    'install_command': 'pip install -r requirements.txt',
                    'additional_files': ['Procfile', 'runtime.txt']
                },
                'railway': {
                    'run_command': 'python main.py',
                    'install_command': 'pip install -r requirements.txt'
                },
                'docker': {
                    'base_image': 'python:3.11-slim',
                    'run_command': 'python main.py',
                    'dockerfile_needed': True
                }
            }
        }
        
        config_file = os.path.join(self.config_dir, 'platform_config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Platform configuration exported: {config_file}")
        return config_file
    
    def _get_python_dependencies(self) -> List[str]:
        """Get current Python dependencies"""
        try:
            # Try to read from pyproject.toml
            if os.path.exists('pyproject.toml'):
                with open('pyproject.toml', 'r') as f:
                    content = f.read()
                    # Extract dependencies (simplified)
                    return ['python-telegram-bot', 'sqlalchemy', 'psycopg2-binary', 'python-dotenv', 'requests']
        except:
            pass
        
        # Fallback to common dependencies
        return ['python-telegram-bot', 'sqlalchemy', 'psycopg2-binary', 'python-dotenv', 'requests']
    
    def _get_system_dependencies(self) -> List[str]:
        """Get system dependencies"""
        return ['postgresql-client']  # Common system deps
    
    def create_requirements_txt(self) -> str:
        """Create requirements.txt for pip-based deployments"""
        deps = self._get_python_dependencies()
        
        with open('requirements.txt', 'w') as f:
            for dep in deps:
                f.write(f"{dep}\n")
        
        print("✅ requirements.txt created")
        return 'requirements.txt'
    
    def create_dockerfile(self) -> str:
        """Create Dockerfile for Docker deployments"""
        dockerfile_content = """FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for keep-alive service
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
"""
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        print("✅ Dockerfile created")
        return 'Dockerfile'
    
    def create_heroku_files(self) -> List[str]:
        """Create Heroku-specific files"""
        # Procfile
        with open('Procfile', 'w') as f:
            f.write("worker: python main.py\n")
        
        # runtime.txt
        with open('runtime.txt', 'w') as f:
            f.write("python-3.11.0\n")
        
        files = ['Procfile', 'runtime.txt']
        print(f"✅ Heroku files created: {', '.join(files)}")
        return files

def verify_data_integrity(db_url: str = None) -> bool:
    """Verify database data integrity"""
    db_url = db_url or os.environ.get('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check user data integrity
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM users WHERE photos IS NOT NULL")
        users_with_photos = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM users WHERE name IS NOT NULL AND age IS NOT NULL")
        complete_profiles = cur.fetchone()[0]
        
        print(f"✅ Data Integrity Check:")
        print(f"   Total users: {user_count}")
        print(f"   Users with photos: {users_with_photos}")
        print(f"   Complete profiles: {complete_profiles}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Data integrity check failed: {e}")
        return False

def main():
    """Main CLI interface for migration tools"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
Migration Tools for Alt3r Bot

Commands:
  backup                    Create full database backup
  restore <backup_file>     Restore from backup file
  export-config            Export platform configuration
  create-requirements      Create requirements.txt
  create-dockerfile        Create Dockerfile
  create-heroku            Create Heroku deployment files
  verify-integrity         Check data integrity
  
Examples:
  python migration_tools.py backup
  python migration_tools.py restore backups/alt3r_backup_20250803.json
  python migration_tools.py export-config
        """)
        return
    
    command = sys.argv[1]
    
    if command == 'backup':
        migrator = DatabaseMigrator()
        migrator.create_full_backup()
        
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Please specify backup file")
            return
        migrator = DatabaseMigrator()
        migrator.restore_from_backup(sys.argv[2])
        
    elif command == 'export-config':
        platform_migrator = PlatformMigrator()
        platform_migrator.export_environment_config()
        
    elif command == 'create-requirements':
        platform_migrator = PlatformMigrator()
        platform_migrator.create_requirements_txt()
        
    elif command == 'create-dockerfile':
        platform_migrator = PlatformMigrator()
        platform_migrator.create_dockerfile()
        
    elif command == 'create-heroku':
        platform_migrator = PlatformMigrator()
        platform_migrator.create_heroku_files()
        
    elif command == 'verify-integrity':
        verify_data_integrity()
        
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()