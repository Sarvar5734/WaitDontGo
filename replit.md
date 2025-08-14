# Alt3r Telegram Bot

## Overview

Alt3r is a specialized Telegram dating bot designed for neurodivergent individuals. Its main purpose is to facilitate meaningful connections by providing comprehensive trait matching, AI assistance, and bilingual support (English/Russian). The bot features a complete user registration system, profile browsing, matching algorithms, AI-powered support, and now includes integrated payment functionality for project support. It aims to connect users sharing similar neurodivergent experiences, including ADHD, autism, anxiety, depression, and other neurological differences.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 2025)

**Critical Bug Fixes & Launch Preparation:**
- Fixed feedback_db crashes by migrating to PostgreSQL (db_manager.add_feedback)
- Eliminated double menu sends in main message handler
- Cleaned up unused imports (fcntl, atexit) - now using process_manager
- Streamlined atomic update logic in add_like function
- Fixed report button UI split (🏠 Home + 🚨 Report buttons)

**Comprehensive City Handling System (NEW - August 14, 2025):**
- Added city_slug database column for consistent city matching across languages
- Implemented forward geocoding using OpenStreetMap API for coordinate lookup
- Created comprehensive city normalization and diacritics removal functions
- Built multilingual city alias system (Moscow/Москва, Warsaw/Warszawa, etc.)
- Enhanced distance calculation using Haversine formula for accurate proximity
- Added regional proximity detection with slug-based matching system
- Implemented automatic migration for existing users to populate city_slug values
- Updated user registration flow to generate coordinates from manual city input
- Integrated new location system with existing matching algorithms for improved accuracy

**Navigation System Improvements:**
- Added comprehensive debugging for profile navigation buttons
- Fixed compatibility issues in profile browsing with proper gender/interest matching
- Enhanced navigation with detailed logging for back/forth button functionality
- Verified navigation works correctly with multiple profiles (3+ users)

**Admin Tools Implementation:**
- Added admin panel functionality with user reporting system
- Implemented user report system with multiple categories (spam, harassment, fake profiles)
- Admin access restricted to authorized user IDs with full management interface
- Report logging integrated with PostgreSQL backend

**Video Support Enhancement:**
- Implemented video display support for incoming like profiles
- Added media fallback logic: photos → videos → text-only display
- Enhanced media debugging to track photo vs video content properly

**Process Management:**
- Integrated robust process manager with automatic cleanup and conflict prevention
- Replaced complex lock system with simple, effective solution for bot stability

## System Architecture

### Code Structure

The bot follows a modular design, separating concerns into distinct modules:
- **Main Entry Point (`main.py`)**: Configures and starts the bot, handles registration of handlers, and manages error handling.
- **Database Layer (`models.py`, `database_manager.py`, `db_operations.py`)**: Manages interactions with a pure PostgreSQL database using SQLAlchemy ORM for User, Feedback, and AISession models. It supports full CRUD operations, advanced querying, indexing, and is designed for scalability to support 10,000+ concurrent users. JSON fields are used for arrays like photos, likes, and traits. Enhanced with city_slug column for consistent location matching and coordinate storage for distance calculations.
- **Translation System (`translations.py`)**: Centralizes all bot text in a `TEXTS` dictionary, providing bilingual support for English and Russian, including comprehensive neurodivergent trait definitions in multiple languages. It includes helper functions for language detection and text retrieval.
- **Handler Modules (`handlers.py`)**: Contains conversation handlers for user registration, the main menu system, profile management (viewing, editing), and dating features (like/pass, match detection, profile browsing), along with navigation elements like back buttons.
- **Keep-Alive Service (`keep_alive.py`)**: A custom HTTP server that prevents the bot from going idle on hosting platforms and integrates with logging.
- **Process Management (`process_manager.py`)**: Robust system to prevent multiple bot instances from running simultaneously. Uses PID files, process monitoring, and automatic cleanup to ensure only one bot runs at a time. Includes signal handlers for graceful shutdown and automatic killing of conflicting processes.

### Translation Management

All translations are centralized in a `TEXTS` dictionary, allowing for easy management and addition of new languages. It ensures complete coverage of bot functionality and includes comprehensive multilingual support for neurodivergent traits and city normalization.

### Design Patterns

- **Service Architecture**: Modular design separates core bot operations from support services like the keep-alive function.
- **Error Handling**: Implements structured logging for debugging and monitoring.
- **Process Isolation**: Prevents multiple bot instances through robust locking mechanisms with automatic cleanup and conflict resolution.
- **Graceful Shutdown**: Signal handlers ensure proper cleanup of resources and lock files on termination.

## External Dependencies

### Python Standard Library

- `threading`
- `time`
- `http.server`
- `socketserver`
- `logging`

### Database Schema

- **PostgreSQL**: The core database.
  - **Users Table**: Stores complete user profiles, including indexed fields, neurodivergent traits, preferences, and interaction history. Utilizes PostgreSQL JSON support for arrays (photos, likes, matches, traits). Enhanced with city_slug field for consistent location matching and latitude/longitude coordinates for precise distance calculations.
  - **Feedback Table**: Records user feedback and support requests.
  - **AI Sessions Table**: Tracks AI usage and rate limiting.
  - Strategic indexing is applied to frequently queried fields for performance, including new indexes on city_slug and coordinate fields.

### Hosting Platform Integration

- The `keep-alive` service is designed for compatibility with platforms like Replit, Heroku, or similar, using HTTP endpoints for uptime monitoring.
- **Process Management**: Includes `start_bot.py` for safe bot startup with automatic cleanup of existing instances, ensuring no overlapping processes occur during restarts or deployments.