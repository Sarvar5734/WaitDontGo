# Alt3r Telegram Bot

## Overview

Alt3r is a specialized Telegram dating bot designed for neurodivergent individuals. Its main purpose is to facilitate meaningful connections by providing comprehensive trait matching, AI assistance, and bilingual support (English/Russian). The bot features a complete user registration system, profile browsing, matching algorithms, AI-powered support, and now includes integrated payment functionality for project support. It aims to connect users sharing similar neurodivergent experiences, including ADHD, autism, anxiety, depression, and other neurological differences.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (August 2025)

**Russian Profile Population - COMPLETED (August 15, 2025):**
- ✅ Created authentic Russian profiles for testing and demonstration
- ✅ **FINAL: 12 female profiles with unique photos (1:1 photo-to-profile ratio)**
- ✅ 25 male profiles with Russian names (Александр, Сергей, Андрей, etc.)
- ✅ All profiles use major Russian cities (Москва, Санкт-Петербург, Новосибирск, etc.)
- ✅ Russian language bios with authentic personality types and neurodivergent traits
- ✅ Realistic interactions between profiles (likes, mutual connections)
- ✅ Database now contains culturally appropriate content for Russian users
- ✅ **COMPLETED: Perfect 1:1 ratio - exactly 12 photos for 12 female profiles**
- ✅ **UPDATED: All fake profile ages now 26 or younger (range: 18-26 years old)**

## Recent Changes (August 2025)

**Payment System Integration - COMPLETED (August 15, 2025):**
- ✅ Completely replaced existing payment infrastructure with Telegram Stars and TON cryptocurrency only
- ✅ Implemented comprehensive payment system supporting both Telegram Stars and TON payments
- ✅ Added new payment_system.py module with full Stars and TON integration
- ✅ Updated translations.py with payment-specific messaging in English and Russian
- ✅ Integrated TON Center API for transaction verification and monitoring
- ✅ Added payment configuration system with environment variable support and validation
- ✅ Configured pre-checkout query handlers and successful payment processing
- ✅ Replaced legacy payment handlers with modern Telegram Stars API integration
- ✅ Added custom amount input handling for both payment methods with proper validation
- ✅ Created payment validation and error handling for robust user experience
- ✅ Updated environment configuration to support TON wallet and API credentials
- ✅ Fixed database schema compatibility issue (lang vs language column)
- ✅ Created comprehensive PAYMENT_SETUP_GUIDE.md with setup instructions
- ✅ Bot successfully starts and processes payment callbacks without errors
- ✅ Fixed TON payment message formatting (replaced raw translation keys with proper localized text)
- ✅ Fixed TON menu description placeholder issue (now displays proper Russian/English text)
- ✅ Payment integration fully tested and operational with proper multilingual support

**Security & Access Control Fix (August 15, 2025):**
- Fixed admin panel visibility issue where regular users could see admin controls
- Cleared ADMIN_USER_IDS list to properly restrict admin access
- Admin panel now hidden from all users until proper admin IDs are configured
- Improved security by preventing unauthorized access to administrative functions
- Created comprehensive admin setup documentation for proper deployment

**Code Quality Improvements (August 15, 2025):**
- Fixed critical null pointer exceptions and type checking errors
- **COMPLETED: Eliminated all LSP diagnostic errors (reduced from 389 to 0)**
- Enhanced message handling safety with proper null checks
- Improved context.user_data validation throughout the application
- Fixed User object type handling for both ORM and dictionary formats
- **COMPLETED: Fixed all user.lang attribute access errors preventing registration crashes**
- **VERIFIED: Registration flow now working correctly with live user test (ID: 1245005805)**

**Critical Bot Startup Fix (August 14, 2025):**
- Fixed asyncio event loop conflict that prevented bot from starting
- Updated main function to properly handle async/await patterns with Telegram bot framework
- Resolved "There is no current event loop" and "Cannot close a running event loop" errors
- Bot now successfully starts and maintains stable connection to Telegram API
- Improved application initialization sequence for better reliability

**Enhanced Matching System (August 24, 2025):**
- ✅ Implemented precise gender filtering: male=boys only, female=girls only, all=everyone
- ✅ Added intelligent prioritization: similar neurodivergent traits (10pts each) + same city (50pts bonus)
- ✅ Fixed database schema conflicts between models.py and database.py User definitions
- ✅ Resolved matching system failures due to non-existent profile_complete/active columns
- ✅ Added fallback logic: shows all profiles when no gender-specific matches available
- ✅ Language-independent matching logic works consistently across English/Russian interface

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
- **Translation System (`translations.py`)**: Centralizes all bot text in a `TEXTS` dictionary, providing bilingual support for English and Russian, including comprehensive neurodivergent trait definitions in multiple languages. Enhanced with payment-specific messaging for Telegram Stars and TON payments. It includes helper functions for language detection and text retrieval.
- **Payment System (`payment_system.py`)**: Comprehensive payment integration module supporting Telegram Stars and TON cryptocurrency payments. Handles invoice creation, payment verification, transaction monitoring via TON Center API, and payment status tracking. Includes validation, error handling, and database integration for payment records.
- **Payment Configuration (`payment_config.py`)**: Centralized configuration management for payment systems, including TON wallet setup, API credentials, and environment validation with helpful setup instructions.
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