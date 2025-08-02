# Alt3r Bot - Translation Guide

This guide shows you how to easily add new translations to the Alt3r neurodivergent dating bot.

## 🌍 Current Languages
- **Russian** (`ru`) - Complete
- **English** (`en`) - Complete

## 📝 How to Add a New Language

### Step 1: Add Language to TEXTS Dictionary

In `main.py`, find the `TEXTS = {` section (around line 224) and add your new language:

```python
TEXTS = {
    "ru": { ... },
    "en": { ... },
    "es": {  # Add your new language here (Spanish example)
        "welcome": "🧠 ¡Bienvenido a Alt3r!\n\nEste es un bot de citas para personas neurodivergentes...",
        "main_menu": "🏠 Menú Principal",
        "profile_menu_0": "👤 Mi Perfil",
        # ... copy all keys from English and translate
    }
}
```

### Step 2: Add Neurodivergent Traits Translation

Find the `ND_TRAITS = {` section (around line 66) and add your language:

```python
ND_TRAITS = {
    "en": { ... },
    "ru": { ... },
    "es": {  # Spanish example
        "adhd": "TDAH",
        "autism": "Autismo/Asperger",
        "anxiety": "Ansiedad",
        # ... translate all traits
    }
}
```

### Step 3: Add Neurodivergent Symptoms Translation

Find the `ND_SYMPTOMS = {` section (around line 102) and add your language:

```python
ND_SYMPTOMS = {
    "ru": { ... },
    "en": { ... },
    "es": {  # Spanish example
        "hyperfocus": "Hiperfoco",
        "executive_dysfunction": "Disfunción Ejecutiva",
        # ... translate all symptoms
    }
}
```

### Step 4: Add Cities to Normalization Database

In the `normalize_city()` function (around line 557), add your country's cities to the `global_cities` dictionary:

```python
global_cities = {
    # Existing cities...
    
    # Spanish Cities (add your country's cities)
    "madrid": ["madrid", "мадрид", "madryt"],
    "barcelona": ["barcelona", "барселона", "barcelone"],
    "valencia": ["valencia", "валенсия"],
    "sevilla": ["sevilla", "севилья", "seville"],
    # ... add more cities
}
```

## 🔧 Translation Keys Reference

### Core Categories:

**Welcome & Onboarding**
- `welcome`, `choose_language`, `language_set_*`

**Profile Creation**
- `questionnaire_*` (age, gender, interest, city, name, bio, photo)
- `btn_*` (buttons like yes, no, skip, etc.)

**Main Menu**
- `main_menu`, `profile_menu_0` through `profile_menu_8`

**Dating Features**
- `like_sent`, `its_match`, `no_profiles`, `send_message`

**Settings & Profile**
- `change_*`, `current_*`, `*_updated`

**Error Messages**
- `*_error`, `error_occurred`, `*_required`

**Statistics**
- `statistics_*`, `likes_*`, `profile_views`, etc.

## 📋 Complete Key List

There are approximately 200+ translation keys. The easiest way to add a new language is to:

1. Copy the entire English (`"en"`) section
2. Rename it to your language code (e.g., `"fr"` for French)
3. Translate each value while keeping the keys unchanged

## 🔍 Language Detection

The bot automatically detects user language preferences and stores them in the database. Users can change their language anytime through:
- `/language` command
- Settings menu → Language

## 🧪 Testing Your Translation

1. Add your language code to the language selection menu
2. Restart the bot
3. Test all user flows in your language
4. Check that all buttons, messages, and menus display correctly

## 💡 Tips for Translators

- Keep emojis consistent across languages
- Maintain the same tone (friendly, supportive)
- Consider cultural differences in dating terminology
- Test with native speakers if possible
- Use gender-neutral language where appropriate

## 🛠️ Technical Notes

- Language codes should be 2-letter ISO codes (en, ru, es, fr, etc.)
- All translations are stored in memory (no database needed)
- The bot automatically falls back to English if a key is missing
- City names support multiple spellings and languages for better matching

## 🚀 Deployment

After adding translations:
1. Test thoroughly with the new language
2. Commit your changes
3. The bot will automatically restart and include the new language

---

Need help? The translation system is designed to be simple - just copy, translate, and test!