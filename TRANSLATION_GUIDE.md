# Easy Translation Guide for Alt3r Bot

## Quick Start

### 1. Check Missing Translations
```bash
python translation_manager.py --check
```

### 2. Add New Translations
```bash
python translation_manager.py --add
```

### 3. Get Translation Template
```bash
python translation_manager.py --export
```

## Safe Translation Usage

Use `get_text_safe()` instead of `get_text()` to prevent bot crashes:

```python
# OLD (can break):
text = get_text(user_id, "some_key")

# NEW (never breaks):
text = get_text_safe(user_id, "some_key", "Default text")
```

## Manual Translation Adding

### Step 1: Find the TEXTS dictionary in main.py (around line 224)

### Step 2: Add to both languages

```python
TEXTS = {
    "ru": {
        # ... existing translations ...
        "new_key": "Новый текст на русском",
    },
    "en": {
        # ... existing translations ...
        "new_key": "New text in English",
    }
}
```

## Translation Key Naming Convention

- Use descriptive names: `welcome_message` not `msg1`
- Use snake_case: `profile_updated` not `profileUpdated`
- Group related keys: `btn_yes`, `btn_no`, `btn_cancel`
- Include context: `error_invalid_age` not just `error`

## Common Translation Categories

### Buttons
```python
"btn_yes": "Yes" / "Да"
"btn_no": "No" / "Нет"
"btn_back": "Back" / "Назад"
```

### Messages
```python
"welcome": "Welcome!" / "Добро пожаловать!"
"profile_saved": "Profile saved!" / "Профиль сохранен!"
```

### Errors
```python
"error_invalid_input": "Invalid input" / "Неверный ввод"
"error_network": "Network error" / "Ошибка сети"
```

## Testing Translations

1. Change bot language: `/language`
2. Test all features in both languages
3. Check for mixed language interfaces
4. Verify buttons work in both languages

## Troubleshooting

### Missing Translation Shows [key_name]
- Key exists in code but not in TEXTS dictionary
- Add translation to both languages

### Bot Shows English in Russian Mode
- Translation exists but key might be misspelled
- Check exact key name used in get_text() call

### Bot Crashes on Translation
- Use get_text_safe() instead of get_text()
- Always provide fallback text

## Best Practices

1. **Always add to both languages** - Never add to just one
2. **Test immediately** - Check translations work after adding
3. **Use meaningful keys** - Make keys self-documenting
4. **Provide fallbacks** - Use get_text_safe() with default text
5. **Keep consistent tone** - Match existing translation style

## Quick Commands Summary

```bash
# Check what's missing
python translation_manager.py --check

# Add translations interactively  
python translation_manager.py --add

# Export template file
python translation_manager.py --export

# Show statistics
python translation_manager.py --stats

# Create safe translation function
python translation_manager.py --safe
```

## Emergency Fix for Broken Translations

If translations break the bot:

1. Find the problematic key in error logs
2. Add it to both languages in TEXTS dictionary
3. Restart bot
4. Use get_text_safe() to prevent future issues

## Example: Adding a New Feature Translation

```python
# 1. Add to TEXTS in main.py
"feature_new_search": {
    "en": "🔍 Advanced Search",
    "ru": "🔍 Расширенный поиск"
}

# 2. Use in code
button_text = get_text_safe(user_id, "feature_new_search", "Search")

# 3. Test in both languages
# 4. Commit changes
```

This system ensures your bot never breaks due to missing translations while making it easy to add new ones.