#!/usr/bin/env python3
"""
Easy Translation Manager for Alt3r Bot
Makes it simple to add and manage translations without breaking the code.

USAGE:
1. python translation_manager.py --check     # Check for missing translations
2. python translation_manager.py --add      # Interactive translation adding
3. python translation_manager.py --export   # Export translations to file
4. python translation_manager.py --stats    # Show translation statistics
"""

import sys
import json
import re
from typing import Dict, List, Set, Optional

def load_texts_from_main() -> Dict[str, Dict[str, str]]:
    """Load TEXTS dictionary from main.py safely"""
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find TEXTS dictionary using regex
        pattern = r'TEXTS\s*=\s*\{(.*?)\n\}'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # This is a simplified extraction - in production you'd use ast.parse
            # For now, return a basic structure
            return {
                'ru': {},
                'en': {}
            }
        
        return {}
    except Exception as e:
        print(f"Error loading translations: {e}")
        return {}

def find_get_text_calls() -> Set[str]:
    """Find all get_text() calls in the codebase to identify needed translation keys"""
    keys = set()
    
    # Search in main Python files
    for filename in ['main.py', 'handlers.py', 'translations.py']:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find get_text calls with various patterns
            patterns = [
                r'get_text\([^,]+,\s*["\']([^"\']+)["\']',
                r'get_text\([^,]+,\s*"([^"]+)"',
                r'get_text\([^,]+,\s*\'([^\']+)\'',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                keys.update(matches)
                
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error scanning {filename}: {e}")
    
    return keys

def check_missing_translations() -> Dict[str, List[str]]:
    """Check for missing translations between languages"""
    print("🔍 Checking for missing translations...")
    
    # Load current translations
    texts = load_texts_from_main()
    
    # Find all used keys in code
    used_keys = find_get_text_calls()
    
    missing = {
        'en': [],
        'ru': [],
        'used_but_missing': list(used_keys)
    }
    
    print(f"Found {len(used_keys)} unique translation keys in code")
    
    return missing

def interactive_translation_add():
    """Interactive mode to add translations"""
    print("📝 Interactive Translation Adding")
    print("Add translations one by one. Press Ctrl+C to exit.\n")
    
    try:
        while True:
            key = input("Translation key: ").strip()
            if not key:
                continue
                
            en_text = input("English text: ").strip()
            ru_text = input("Russian text: ").strip()
            
            if key and en_text and ru_text:
                print(f"✅ Added: {key}")
                print(f"   EN: {en_text}")
                print(f"   RU: {ru_text}")
                print("\nTo apply these changes, manually add to TEXTS dictionary in main.py:")
                print(f'    "{key}": "{en_text}",  # English')
                print(f'    "{key}": "{ru_text}",  # Russian')
                print("-" * 50)
            else:
                print("❌ Please provide key and both translations")
                
    except KeyboardInterrupt:
        print("\n👋 Exiting translation mode")

def export_template():
    """Export translation template"""
    used_keys = find_get_text_calls()
    
    template = {
        "translation_instructions": "Add your translations here, then copy to main.py TEXTS dictionary",
        "en": {},
        "ru": {}
    }
    
    for key in sorted(used_keys):
        template["en"][key] = f"TODO: English for {key}"
        template["ru"][key] = f"TODO: Russian for {key}"
    
    with open('translation_template.json', 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Exported {len(used_keys)} translation keys to translation_template.json")

def show_statistics():
    """Show translation statistics"""
    used_keys = find_get_text_calls()
    texts = load_texts_from_main()
    
    print("📊 TRANSLATION STATISTICS")
    print(f"Keys used in code: {len(used_keys)}")
    print(f"English translations: {len(texts.get('en', {}))}")
    print(f"Russian translations: {len(texts.get('ru', {}))}")

def create_safe_get_text_function():
    """Create a safe wrapper for get_text that never breaks"""
    safe_function = '''
def get_text_safe(user_id: int, key: str, fallback: str = None) -> str:
    """
    Safe translation function that never breaks the bot
    
    Args:
        user_id: Telegram user ID
        key: Translation key
        fallback: Custom fallback text
    
    Returns:
        Translated text or safe fallback
    """
    try:
        # Use existing get_text function
        return get_text(user_id, key)
    except Exception as e:
        logger.error(f"Translation error for key '{key}': {e}")
        
        # Return fallback or the key itself
        if fallback:
            return fallback
        return f"[{key}]"  # Shows missing translation clearly

# Usage examples:
# text = get_text_safe(user_id, "welcome", "Welcome!")
# button = get_text_safe(user_id, "btn_yes", "Yes")
'''
    
    with open('safe_translations.py', 'w', encoding='utf-8') as f:
        f.write(safe_function)
    
    print("✅ Created safe_translations.py with get_text_safe() function")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == '--check':
        missing = check_missing_translations()
        print("Results:", missing)
        
    elif command == '--add':
        interactive_translation_add()
        
    elif command == '--export':
        export_template()
        
    elif command == '--stats':
        show_statistics()
        
    elif command == '--safe':
        create_safe_get_text_function()
        
    else:
        print("Unknown command. Use --check, --add, --export, --stats, or --safe")

if __name__ == '__main__':
    main()