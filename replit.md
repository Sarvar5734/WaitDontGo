# Alt3r Telegram Bot

## Overview

Alt3r is a specialized Telegram dating bot designed for neurodivergent individuals. Its main purpose is to facilitate meaningful connections by providing comprehensive trait matching, AI assistance, and bilingual support (English/Russian). The bot features a complete user registration system, profile browsing, matching algorithms, AI-powered support, and now includes integrated payment functionality for project support. It aims to connect users sharing similar neurodivergent experiences, including ADHD, autism, anxiety, depression, and other neurological differences.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Code Structure

The bot follows a modular design, separating concerns into distinct modules:
- **Main Entry Point (`main.py`)**: Configures and starts the bot, handles registration of handlers, and manages error handling.
- **Database Layer (`models.py`, `database_manager.py`, `db_operations.py`)**: Manages interactions with a pure PostgreSQL database using SQLAlchemy ORM for User, Feedback, and AISession models. It supports full CRUD operations, advanced querying, indexing, and is designed for scalability to support 10,000+ concurrent users. JSON fields are used for arrays like photos, likes, and traits.
- **Translation System (`translations.py`)**: Centralizes all bot text in a `TEXTS` dictionary, providing bilingual support for English and Russian, including comprehensive neurodivergent trait definitions in multiple languages. It includes helper functions for language detection and text retrieval.
- **Handler Modules (`handlers.py`)**: Contains conversation handlers for user registration, the main menu system, profile management (viewing, editing), and dating features (like/pass, match detection, profile browsing), along with navigation elements like back buttons.
- **Keep-Alive Service (`keep_alive.py`)**: A custom HTTP server that prevents the bot from going idle on hosting platforms and integrates with logging.

### Translation Management

All translations are centralized in a `TEXTS` dictionary, allowing for easy management and addition of new languages. It ensures complete coverage of bot functionality and includes comprehensive multilingual support for neurodivergent traits and city normalization.

### Design Patterns

- **Service Architecture**: Modular design separates core bot operations from support services like the keep-alive function.
- **Error Handling**: Implements structured logging for debugging and monitoring.

## External Dependencies

### Python Standard Library

- `threading`
- `time`
- `http.server`
- `socketserver`
- `logging`

### Database Schema

- **PostgreSQL**: The core database.
  - **Users Table**: Stores complete user profiles, including indexed fields, neurodivergent traits, preferences, and interaction history. Utilizes PostgreSQL JSON support for arrays (photos, likes, matches, traits).
  - **Feedback Table**: Records user feedback and support requests.
  - **AI Sessions Table**: Tracks AI usage and rate limiting.
  - Strategic indexing is applied to frequently queried fields for performance.

### Hosting Platform Integration

- The `keep-alive` service is designed for compatibility with platforms like Replit, Heroku, or similar, using HTTP endpoints for uptime monitoring.