# Alt3r - Neurodivergent Dating Bot

A specialized Telegram dating bot designed for neurodivergent individuals, providing comprehensive trait matching and bilingual support (English/Russian).

## 🏗️ Project Structure

The codebase is organized into focused, modular components for easy maintenance and translation management:

```
Alt3r Bot/
├── main.py              # Main entry point - bot configuration and startup
├── database.py          # Database models and operations
├── handlers.py          # Telegram message and callback handlers
├── translations.py      # Centralized translation system
├── keep_alive.py        # Keep-alive service for hosting platforms
├── main_old.py          # Previous monolithic version (backup)
└── replit.md           # Project documentation and architecture
```

## 🌍 Adding New Translations

The translation system is designed to make adding new languages as simple as possible:

### 1. Add Language to TEXTS Dictionary

Edit `translations.py` and add your language to the main `TEXTS` dictionary:

```python
TEXTS = {
    "en": { ... },
    "ru": { ... },
    "es": {  # New Spanish translation
        "welcome": "¡Bienvenido a Alt3r!",
        "main_menu": "Menú Principal",
        # ... add all required keys
    }
}
```

### 2. Add Neurodivergent Traits Translation

Add trait translations in the `ND_TRAITS` dictionary:

```python
ND_TRAITS = {
    "en": { ... },
    "ru": { ... },
    "es": {  # Spanish traits
        "adhd": "TDAH",
        "autism": "Autismo/Asperger",
        # ... add all trait keys
    }
}
```

### 3. Update Available Languages

Add your language to the `get_available_languages()` function:

```python
def get_available_languages() -> List[Dict[str, str]]:
    return [
        {'code': 'en', 'name': '🇬🇧 English'},
        {'code': 'ru', 'name': '🇷🇺 Русский'},
        {'code': 'es', 'name': '🇪🇸 Español'}  # New language
    ]
```

### 4. Translation Keys Reference

All required translation keys are available in the English (`"en"`) section of `TEXTS`. Key categories include:

- **Welcome & Onboarding**: `welcome`, `language_prompt`
- **Questionnaire**: `questionnaire_age`, `questionnaire_gender`, etc.
- **Profile**: `profile_preview`, `profile_saved`, `ready_to_connect`
- **Main Menu**: `main_menu`, `profile_menu_0` through `profile_menu_7`
- **Buttons**: `btn_girl`, `btn_boy`, `btn_yes`, `btn_change`, etc.
- **Dating**: `like_sent`, `its_match`, `no_profiles`
- **Status Messages**: `photo_updated`, `message_sent`, `invalid_age`

## 🛠️ Development

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Telegram Bot Token

### Environment Variables
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://username:password@host:port/database
```

### Running the Bot
```bash
python main.py
```

### Key Features
- **Modular Architecture**: Separated concerns across multiple files
- **Bilingual Support**: English and Russian with easy expansion
- **Profile Management**: Complete user registration and profile system
- **Matching Algorithm**: Compatibility-based profile filtering
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Keep-Alive Service**: Prevents hosting platform timeouts

## 📋 Code Organization Benefits

### For Developers
- **Clean Separation**: Each file has a single responsibility
- **Easy Testing**: Modular functions can be tested independently
- **Maintainable**: Changes are isolated to specific modules
- **Readable**: Clear naming and organized structure

### For Translators
- **Centralized Translations**: All text in one file (`translations.py`)
- **Simple Structure**: Key-value pairs for easy translation
- **Coverage Tracking**: Built-in functions to check translation completeness
- **Helper Functions**: Tools for managing and adding translations

### For Deployment
- **Simple Entry Point**: `main.py` contains only essential startup code
- **Environment Ready**: Works with Replit, Heroku, or any Python hosting
- **Database Migrations**: Automatic table creation on startup
- **Error Handling**: Comprehensive logging and error management

## 🔧 Technical Details

- **Framework**: python-telegram-bot (v20.8)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Architecture**: Async/await pattern with conversation handlers
- **Hosting**: Compatible with Replit, Heroku, and other platforms
- **Features**: Multi-step registration, inline keyboards, photo handling