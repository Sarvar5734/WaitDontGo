# Alt3r Telegram Bot

## Overview

Alt3r is a specialized Telegram dating bot designed for neurodivergent individuals, providing comprehensive trait matching, AI assistance, and bilingual support (English/Russian). The bot facilitates meaningful connections between users who share similar neurodivergent experiences, including ADHD, autism, anxiety, depression, and other neurological differences. It features a complete user registration system, profile browsing, matching algorithms, and keeps users engaged with AI-powered support features.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components

**Telegram Bot Framework**
- **Framework**: Python-telegram-bot library (v20.8)
- **Architecture**: Async/await pattern with conversation handlers
- **Features**: 
  - Multi-step user registration flow
  - Inline keyboard interactions
  - Profile creation and management
  - Photo and media handling
  - Bilingual support (English/Russian)

**Database Layer**
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Storage**: Cloud-hosted PostgreSQL database
- **Schema**: Relational database with User and Feedback tables
- **Features**: ACID compliance, JSON field support for complex data, automatic timestamps

**Neurodivergent Matching System**
- **Traits Database**: Comprehensive ND trait definitions in multiple languages
- **Matching Algorithm**: Compatibility-based profile filtering
- **Features**: Trait-based search, symptom matching, preference alignment

**Keep-Alive Service**
- **Purpose**: Prevents the bot from going idle on hosting platforms
- **Implementation**: Custom HTTP server using Python's built-in `http.server` module
- **Features**: 
  - Threaded server using `ThreadingMixIn` for concurrent request handling
  - Health check endpoint with styled HTML response
  - Logging integration for monitoring and debugging

**Removed Components**
- **AI Integration**: OpenAI integration removed per user request
- **Simplified Architecture**: Focus on core dating functionality without AI assistance

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