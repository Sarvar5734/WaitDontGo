# Alt3r Telegram Bot

## Overview

Alt3r is a specialized Telegram dating bot designed for neurodivergent individuals, providing comprehensive trait matching, AI assistance, and bilingual support (English/Russian). The bot facilitates meaningful connections between users who share similar neurodivergent experiences, including ADHD, autism, anxiety, depression, and other neurological differences. It features a complete user registration system, profile browsing, matching algorithms, and keeps users engaged with AI-powered support features.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Code Structure (Modular Design)

**Main Entry Point** (`main.py`)
- Clean, focused entry point with minimal code
- Imports all handlers and database models from separate modules
- Configures and starts the Telegram bot application
- Handler registration and error handling

**Database Layer** (`database.py`)
- **Database**: TinyDB JSON-based database with atomic operations
- **Models**: User and Feedback models with comprehensive fields
- **Operations**: Atomic database operations preventing race conditions
- **Features**: Matching algorithms, like/pass interactions, user statistics
- **Schema**: JSON fields for arrays (photos, likes, matches, traits)
- **Concurrency Safety**: All critical operations use atomic callback functions

**Translation System** (`translations.py`)
- **Centralized Translations**: All bot text in TEXTS dictionary
- **Bilingual Support**: English and Russian translations
- **Easy Translation Management**: Simple key-value structure for adding new languages
- **Neurodivergent Traits**: Comprehensive ND trait definitions in multiple languages
- **Helper Functions**: Language detection, text retrieval, coverage statistics

**Handler Modules** (`handlers.py`)
- **Registration Flow**: Complete user onboarding conversation handlers
- **Menu System**: Main menu navigation and callback handling
- **Profile Management**: Profile viewing, editing, and browsing
- **Dating Features**: Like/pass system, match detection, profile browsing
- **Navigation**: Back buttons and menu transitions

**Keep-Alive Service** (`keep_alive.py`)
- **Purpose**: Prevents the bot from going idle on hosting platforms
- **Implementation**: Custom HTTP server for health checks
- **Features**: Threaded server, logging integration

### Translation Management
- **Centralized System**: All translations in TEXTS dictionary within main.py
- **Easy Addition**: Simple key-value structure for adding new languages
- **Complete Coverage**: 200+ translation keys covering all bot functionality
- **Multilingual Cities**: Advanced city normalization with international spellings
- **Neurodivergent Traits**: Comprehensive ND trait translations in multiple languages

### Recent Changes (August 2025)
- **Restored Working Version**: Implemented user's working main.py with comprehensive features
- **Translation-Focused Structure**: Maintained centralized, easy-to-manage translation system
- **Complete Feature Set**: Full dating bot functionality with ND matching, statistics, messaging
- **Advanced City Support**: Global city database with typo correction and multiple languages
- **User-Friendly Design**: Well-organized code structure optimized for translation management
- **Enhanced Messaging System**: Added comprehensive video messaging functionality across all profile types
- **Fixed Code Redundancy**: Removed duplicate send_message_with_profile functions
- **Complete Button Coverage**: All profile cards now offer both text (💌) and video (🎥) messaging options
- **CRITICAL BUG FIX**: Fixed dangerous race condition vulnerabilities in database operations (August 2, 2025)
- **UI IMPROVEMENT**: Removed unnecessary "💌 Написать" (Write) buttons after mutual connections since users can contact each other directly via Telegram usernames (August 2, 2025)
- **COMPLETE TRANSLATION OVERHAUL**: Achieved comprehensive English translation coverage by fixing ALL hardcoded Russian text throughout the entire codebase (August 2, 2025)
  - Fixed missing English translations for ALL UI buttons: back_to_main_menu, back_button, btn_save, btn_skip_all, btn_done, btn_skip_remaining, use_gps, manual_entry, share_gps
  - Replaced hardcoded Russian button texts with proper get_text() calls in every menu and dialog
  - Fixed hardcoded prompts and error messages with translation system
  - Resolved circular reference errors in TEXTS dictionary
  - Bot now provides 100% bilingual interface with zero mixed-language content

### Design Patterns

**Service Architecture**
- Modular design separating keep-alive functionality from core bot operations
- HTTP server provides external health monitoring capabilities
- Logging framework integration for operational visibility

**Error Handling**
- Structured logging implementation for debugging and monitoring
- HTTP status code management for proper client communication

## External Dependencies

### Python Standard Library
- `threading` - Multi-threaded operation support
- `time` - Timing and scheduling operations
- `http.server` - HTTP server implementation
- `socketserver` - Network server framework
- `logging` - Application logging and monitoring

### Database Schema
- **Users Table**: Complete user profiles with neurodivergent traits, preferences, and interaction history
- **Feedback Table**: User feedback and support requests
- **JSON Fields**: Flexible storage for arrays (photos, likes, matches, traits)

### Hosting Platform Integration
- Keep-alive service designed for platforms like Replit, Heroku, or similar
- HTTP endpoint structure compatible with uptime monitoring services