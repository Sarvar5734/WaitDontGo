"""
Translation system for Alt3r Bot
Manages multilingual text content for the neurodivergent dating bot.

EASY TRANSLATION GUIDE:
1. Add new translations to the TEXTS dictionary below
2. Use format: "translation_key": "Your text here"
3. Always add to BOTH 'en' and 'ru' sections
4. Use the check_missing_translations() function to find gaps
5. Test with get_text_safe() which never breaks the bot
"""

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# ===== TRANSLATION TEXTS =====
# Main dictionary containing all bot texts in multiple languages
TEXTS = {
    "en": {
        # === WELCOME & ONBOARDING ===
        "welcome": "🌟 Welcome to Alt3r!\n\nA dating platform designed specifically for neurodivergent individuals. Let's create your profile!",
        "language_prompt": "🌐 Choose your language / Выберите язык:",
        
        # === QUESTIONNAIRE ===
        "questionnaire_age": "👶 How old are you? (18-100)",
        "questionnaire_gender": "🚻 What's your gender?",
        "questionnaire_interest": "💖 Who are you interested in meeting?",
        "questionnaire_city": "📍 What city are you in? (or share your location)",
        "questionnaire_name": "👤 What's your name?",
        "questionnaire_bio": "✍️ Tell us a bit about yourself! Share your interests, hobbies, or what makes you unique.",
        "questionnaire_photo": "📸 Upload a photo of yourself (optional - you can skip this step)",
        
        # === PROFILE ===
        "profile_preview": "📋 Here's your profile:",
        "profile_correct": "Is everything correct?",
        "profile_saved": "✅ Profile saved! Welcome to Alt3r!",
        "ready_to_connect": "Ready to connect!",
        
        # === MAIN MENU ===
        "main_menu": "🏠 Main Menu - What would you like to do?",
        "profile_menu_0": "👤 My Profile",
        "profile_menu_1": "🔍 Browse Profiles", 
        "profile_menu_2": "🧠 NeuroSearch",
        "profile_menu_3": "📸 Change Photo",
        "profile_menu_4": "✍️ Change Bio",
        "profile_menu_5": "💌 My Likes",
        "profile_menu_6": "⚙️ Settings",
        "profile_menu_7": "📝 Feedback",
        "profile_menu_8": "💖 Support the Project",
        
        # === BUTTONS ===
        "btn_girl": "Girl",
        "btn_boy": "Boy", 
        "btn_girls": "Girls",
        "btn_boys": "Boys",
        "btn_all": "Everyone",
        "btn_yes": "✅ Yes",
        "btn_change": "🔄 Change",
        "btn_skip": "⏭️ Skip",
        "back_to_menu": "🏠 Back to Menu",
        
        # === DATING ===
        "no_profiles": "😕 No profiles available right now. Try again later!",
        "like_sent": "❤️ Like sent!",
        "skip_profile": "⏭️ Skipped",
        "its_match": "🎉 It's a match!\n\nYou can message each other!",
        "new_like": "❤️ Someone liked you!",
        
        # === STATUS MESSAGES ===
        "photo_updated": "✅ Photo updated!",
        "bio_updated": "✅ Description updated!",
        "message_sent": "✅ Message sent!",
        "invalid_age": "❌ Please enter a valid age (18-100)",
        
        # === PAYMENT & SUPPORT ===
        "support_title": "💖 Support Alt3r Project",
        "support_description": "Help us improve Alt3r and create better connections for the neurodivergent community!\n\n💫 We now accept Telegram Stars and TON payments!",
        "support_amounts": "Choose your support method:",
        "support_stars_title": "⭐ Telegram Stars",
        "support_ton_title": "💎 TON Cryptocurrency",
        "support_stars_50": "⭐ 50 Stars - Coffee support",
        "support_stars_100": "⭐ 100 Stars - Pizza fund", 
        "support_stars_250": "⭐ 250 Stars - Generous support",
        "support_stars_500": "⭐ 500 Stars - Super supporter",
        "support_ton_1": "💎 1 TON - Basic support",
        "support_ton_5": "💎 5 TON - Strong support",
        "support_ton_10": "💎 10 TON - Major support",
        "support_custom_stars": "⭐ Custom Stars amount",
        "support_custom_ton": "💎 Custom TON amount",
        "payment_success": "🎉 Thank you for your support! Your contribution helps us build a better platform for neurodivergent connections.",
        "payment_cancelled": "❌ Payment was cancelled. No worries - you can support us anytime!",
        "payment_failed": "❌ Payment failed. Please try again or contact support.",
        "custom_stars_prompt": "⭐ Enter Stars amount (minimum 10 Stars):",
        "custom_ton_prompt": "💎 Enter TON amount (minimum 0.1 TON):",
        "invalid_stars_amount": "❌ Please enter a valid Stars amount (minimum 10)",
        "invalid_ton_amount": "❌ Please enter a valid TON amount (minimum 0.1)",
        "stars_payment_description": "Support Alt3r with Telegram Stars",
        "ton_payment_description": "Support Alt3r with TON cryptocurrency",
        "generate_ton_invoice": "💎 Generate TON Payment",
        "ton_payment_address": "Send TON to this address:",
        "ton_payment_comment": "Include this comment:",
        "ton_payment_wait": "⏳ Waiting for payment confirmation...",
        "ton_payment_verified": "✅ TON payment verified!",
        
        # === DESCRIPTIVE TEXTS ===
        "years_old": "years old",
        "seeking": "seeking",
        "city": "City:",
        "about_me": "About me:",
        "send_message": "💌 Send Message",
        
        # === MISSING TRANSLATION FALLBACKS ===
        "missing_translation": "❌ Missing translation",
        "fallback_text": "Text not available",
    },
    
    "ru": {
        # === WELCOME & ONBOARDING ===
        "welcome": "🌟 Добро пожаловать в Alt3r!\n\nПлатформа знакомств, специально созданная для нейроотличных людей. Давайте создадим ваш профиль!",
        "language_prompt": "🌐 Choose your language / Выберите язык:",
        
        # === QUESTIONNAIRE ===
        "questionnaire_age": "👶 Сколько вам лет? (18-100)",
        "questionnaire_gender": "🚻 Ваш пол?",
        "questionnaire_interest": "💖 Кто вас интересует для знакомства?",
        "questionnaire_city": "📍 В каком городе вы находитесь? (или поделитесь геолокацией)",
        "questionnaire_name": "👤 Как вас зовут?",
        "questionnaire_bio": "✍️ Расскажите немного о себе! Поделитесь интересами, хобби или тем, что делает вас уникальным.",
        "questionnaire_photo": "📸 Загрузите свое фото (необязательно - можно пропустить)",
        
        # === PROFILE ===
        "profile_preview": "📋 Вот ваш профиль:",
        "profile_correct": "Всё правильно?",
        "profile_saved": "✅ Профиль сохранен! Добро пожаловать в Alt3r!",
        "ready_to_connect": "Готов к знакомствам!",
        
        # === MAIN MENU ===
        "main_menu": "🏠 Главное меню - Что хотите делать?",
        "profile_menu_0": "👤 Мой профиль",
        "profile_menu_1": "🔍 Смотреть профили",
        "profile_menu_2": "🧠 НейроПоиск", 
        "profile_menu_3": "📸 Сменить фото",
        "profile_menu_4": "✍️ Изменить описание",
        "profile_menu_5": "💌 Мои лайки",
        "profile_menu_6": "⚙️ Настройки", 
        "profile_menu_7": "📝 Обратная связь",
        "profile_menu_8": "💖 Поддержать проект",
        
        # === BUTTONS ===
        "btn_girl": "Девушка",
        "btn_boy": "Парень",
        "btn_girls": "Девушки", 
        "btn_boys": "Парни",
        "btn_all": "Все",
        "btn_yes": "✅ Да",
        "btn_change": "🔄 Изменить",
        "btn_skip": "⏭️ Пропустить",
        "back_to_menu": "🏠 В главное меню",
        
        # === DATING ===
        "no_profiles": "😕 Сейчас нет доступных профилей. Попробуйте позже!",
        "like_sent": "❤️ Лайк отправлен!",
        "skip_profile": "⏭️ Пропущено",
        "its_match": "🎉 Взаимная симпатия!\n\nТеперь вы можете писать друг другу!",
        "new_like": "❤️ Кто-то поставил вам лайк!",
        
        # === STATUS MESSAGES ===
        "photo_updated": "✅ Фото обновлено!",
        "bio_updated": "✅ Описание обновлено!",
        "message_sent": "✅ Сообщение отправлено!",
        "invalid_age": "❌ Пожалуйста, введите корректный возраст (18-100)",
        
        # === PAYMENT & SUPPORT ===
        "support_title": "💖 Поддержка проекта Alt3r",
        "support_description": "Помогите нам улучшить Alt3r и создать лучшие связи для нейроразнообразного сообщества!\n\n💫 Теперь мы принимаем Telegram Stars и TON!",
        "support_amounts": "Выберите способ поддержки:",
        "support_stars_title": "⭐ Telegram Stars",
        "support_ton_title": "💎 TON Криптовалюта",
        "support_stars_50": "⭐ 50 Stars - Поддержка кофе",
        "support_stars_100": "⭐ 100 Stars - Фонд пиццы", 
        "support_stars_250": "⭐ 250 Stars - Щедрая поддержка",
        "support_stars_500": "⭐ 500 Stars - Супер поддержка",
        "support_ton_1": "💎 1 TON - Базовая поддержка",
        "support_ton_5": "💎 5 TON - Сильная поддержка",
        "support_ton_10": "💎 10 TON - Крупная поддержка",
        "support_custom_stars": "⭐ Произвольная сумма Stars",
        "support_custom_ton": "💎 Произвольная сумма TON",
        "payment_success": "🎉 Спасибо за вашу поддержку! Ваш вклад помогает нам строить лучшую платформу для нейроразнообразных связей.",
        "payment_cancelled": "❌ Платеж отменен. Не беспокойтесь - вы можете поддержать нас в любое время!",
        "payment_failed": "❌ Платеж не прошел. Пожалуйста, попробуйте снова или свяжитесь с поддержкой.",
        "custom_stars_prompt": "⭐ Введите количество Stars (минимум 10 Stars):",
        "custom_ton_prompt": "💎 Введите сумму TON (минимум 0.1 TON):",
        "invalid_stars_amount": "❌ Пожалуйста, введите корректное количество Stars (минимум 10)",
        "invalid_ton_amount": "❌ Пожалуйста, введите корректную сумму TON (минимум 0.1)",
        "stars_payment_description": "Поддержка Alt3r через Telegram Stars",
        "ton_payment_description": "Поддержка Alt3r через TON криптовалюту",
        "generate_ton_invoice": "💎 Сгенерировать TON платеж",
        "ton_payment_address": "Отправьте TON на этот адрес:",
        "ton_payment_comment": "Включите этот комментарий:",
        "ton_payment_wait": "⏳ Ожидание подтверждения платежа...",
        "ton_payment_verified": "✅ TON платеж подтвержден!",
        
        # === DESCRIPTIVE TEXTS ===
        "years_old": "лет",
        "seeking": "ищет",
        "city": "Город:",
        "about_me": "Обо мне:",
        "send_message": "💌 Написать сообщение",
    }
}

# ===== NEURODIVERGENT TRAITS =====
# Comprehensive list of neurodivergent traits in multiple languages
ND_TRAITS = {
    "en": {
        "adhd": "ADHD",
        "autism": "Autism/Aspergers", 
        "anxiety": "Anxiety",
        "depression": "Depression",
        "bipolar": "Bipolar",
        "ocd": "OCD",
        "ptsd": "PTSD",
        "sensory": "Sensory Processing",
        "dyslexia": "Dyslexia/Learning Differences",
        "highly_sensitive": "Highly Sensitive Person (HSP)",
        "introvert": "Introvert",
        "empath": "Empath",
        "creative": "Creative/Artist",
        "none": "Prefer not to specify"
    },
    "ru": {
        "adhd": "СДВГ",
        "autism": "Аутизм/Аспергер",
        "anxiety": "Тревожность", 
        "depression": "Депрессия",
        "bipolar": "Биполярное расстройство",
        "ocd": "ОКР",
        "ptsd": "ПТСР",
        "sensory": "Сенсорные особенности",
        "dyslexia": "Дислексия/Особенности обучения",
        "highly_sensitive": "Высокочувствительный человек (ВЧЛ)",
        "introvert": "Интроверт",
        "empath": "Эмпат",
        "creative": "Творческий человек/Художник", 
        "none": "Предпочитаю не указывать"
    }
}

# ===== TRANSLATION FUNCTIONS =====

def get_user_language(user_id: int, session) -> str:
    """
    Get user's language preference from database.
    
    Args:
        user_id: Telegram user ID
        session: Database session
        
    Returns:
        Language code ('en' or 'ru'), defaults to 'en'
    """
    from database import User  # Import here to avoid circular imports
    
    user = session.query(User).filter(User.user_id == user_id).first()
    if user and user.lang:
        return user.lang
    return 'en'

def get_text(user_id: int, key: str, session=None) -> str:
    """
    Get localized text for a user.
    
    Args:
        user_id: Telegram user ID
        key: Text key to look up
        session: Optional database session (will create new if not provided)
        
    Returns:
        Localized text string
    """
    if session:
        lang = get_user_language(user_id, session)
    else:
        from database import get_db_session  # Import here to avoid circular imports
        with get_db_session() as db_session:
            lang = get_user_language(user_id, db_session)
    
    return TEXTS[lang].get(key, TEXTS['en'].get(key, key))

def get_nd_trait(trait_key: str, language: str = 'en') -> str:
    """
    Get neurodivergent trait name in specified language.
    
    Args:
        trait_key: Trait identifier key
        language: Language code ('en' or 'ru')
        
    Returns:
        Localized trait name
    """
    return ND_TRAITS[language].get(trait_key, ND_TRAITS['en'].get(trait_key, trait_key))

def get_available_languages() -> List[Dict[str, str]]:
    """
    Get list of available languages with display names.
    
    Returns:
        List of dictionaries with 'code' and 'name' keys
    """
    return [
        {'code': 'en', 'name': '🇬🇧 English'},
        {'code': 'ru', 'name': '🇷🇺 Русский'}
    ]

def add_translation(language: str, key: str, text: str) -> bool:
    """
    Add or update a translation entry.
    
    Args:
        language: Language code
        key: Text key
        text: Translated text
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if language not in TEXTS:
            TEXTS[language] = {}
        
        TEXTS[language][key] = text
        return True
    except Exception:
        return False

def get_translation_coverage(language: str) -> dict:
    """
    Get translation coverage statistics for a language.
    
    Args:
        language: Language code to check
        
    Returns:
        Dictionary with coverage statistics
    """
    if language not in TEXTS:
        return {'total': 0, 'translated': 0, 'coverage': 0.0}
    
    en_keys = set(TEXTS['en'].keys())
    lang_keys = set(TEXTS[language].keys())
    
    total = len(en_keys)
    translated = len(lang_keys.intersection(en_keys))
    coverage = (translated / total * 100) if total > 0 else 0.0
    
    return {
        'total': total,
        'translated': translated,
        'coverage': coverage,
        'missing': list(en_keys - lang_keys)
    }