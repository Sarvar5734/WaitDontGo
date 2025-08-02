#!/usr/bin/env python3
"""
Alt3r - Neurodivergent Dating Bot
A Telegram bot for connecting neurodivergent individuals
"""

import os
import json
import logging
import asyncio
import requests
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import fcntl
import atexit

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, 
    MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)
from dotenv import load_dotenv
from keep_alive import start_keep_alive
from database_manager import db_manager
from models import User as UserModel
from db_operations import db, Query

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - check both possible names
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN or BOT_TOKEN environment variable not set")

# Initialize PostgreSQL database
logger.info("Starting with PostgreSQL database")

# Legacy TinyDB compatibility
User = Query()

# AI session tracking
ai_sessions = {}
MAX_AI_MESSAGES_PER_DAY = 10

# Conversation states
(AGE, GENDER, INTEREST, CITY, NAME, BIO, PHOTO, CONFIRM, 
 WAITING_MESSAGE, WAITING_MEDIA, FEEDBACK_TEXT, WAITING_NAME, 
 WAITING_AGE, WAITING_CITY, WAITING_INTEREST_CHANGE, SENDING_MESSAGE, 
 SENDING_VIDEO) = range(17)

# Neurodivergent traits
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
        "highly_sensitive": "Высокочувствительный человек",
        "introvert": "Интроверт",
        "empath": "Эмпат",
        "creative": "Творческий/Художник",
        "none": "Предпочитаю не указывать"
    }
}

# Detailed ND symptoms/characteristics
ND_SYMPTOMS = {
    "ru": {
        # ADHD symptoms
        "hyperfocus": "Гиперфокус",
        "executive_dysfunction": "Исполнительная дисфункция",
        "time_blindness": "Слепота ко времени",
        "rejection_sensitive": "Чувствительность к отвержению",
        "procrastination": "Прокрастинация",
        "hyperactivity": "Гиперактивность",
        "impulsivity": "Импульсивность",
        "inattention": "Невнимательность",

        # Autism symptoms
        "sensory_overload": "Сенсорная перегрузка",
        "stimming": "Стимминг",
        "special_interests": "Особые интересы",
        "routine_dependent": "Зависимость от рутины",
        "social_masking": "Социальная маска",
        "meltdowns": "Срывы/мелтдауны",
        "shutdowns": "Шутдауны",
        "echolalia": "Эхолалия",
        "literal_thinking": "Буквальное мышление",

        # Anxiety symptoms
        "overthinking": "Переосмысление",
        "catastrophizing": "Катастрофизация",
        "perfectionism": "Перфекционизм",
        "avoidance": "Избегание",
        "panic_attacks": "Панические атаки",
        "social_anxiety": "Социальная тревожность",

        # Depression symptoms
        "anhedonia": "Ангедония",
        "brain_fog": "Туман в голове",
        "fatigue": "Усталость",
        "emotional_numbness": "Эмоциональное оцепенение",
        "sleep_issues": "Проблемы со сном",

        # Sensory symptoms
        "hypersensitivity": "Гиперчувствительность",
        "hyposensitivity": "Гипочувствительность",
        "sound_sensitivity": "Чувствительность к звукам",
        "light_sensitivity": "Чувствительность к свету",
        "texture_sensitivity": "Чувствительность к фактуре",
        "vestibular_issues": "Вестибулярные проблемы",

        # Cognitive symptoms
        "working_memory_issues": "Проблемы с рабочей памятью",
        "processing_speed": "Скорость обработки информации",
        "cognitive_flexibility": "Когнитивная гибкость",
        "pattern_recognition": "Распознавание паттернов",
        "detail_focused": "Фокус на деталях",

        # Social/Communication
        "nonverbal_communication": "Невербальная коммуникация",
        "social_cues": "Социальные сигналы",
        "boundaries": "Границы",
        "empathy_differences": "Особенности эмпатии",
        "communication_style": "Стиль общения"
    },
    "en": {
        # ADHD symptoms
        "hyperfocus": "Hyperfocus",
        "executive_dysfunction": "Executive Dysfunction",
        "time_blindness": "Time Blindness",
        "rejection_sensitive": "Rejection Sensitive Dysphoria",
        "procrastination": "Procrastination",
        "hyperactivity": "Hyperactivity",
        "impulsivity": "Impulsivity",
        "inattention": "Inattention",

        # Autism symptoms
        "sensory_overload": "Sensory Overload",
        "stimming": "Stimming",
        "special_interests": "Special Interests",
        "routine_dependent": "Routine Dependent",
        "social_masking": "Social Masking",
        "meltdowns": "Meltdowns",
        "shutdowns": "Shutdowns",
        "echolalia": "Echolalia",
        "literal_thinking": "Literal Thinking",

        # Anxiety symptoms
        "overthinking": "Overthinking",
        "catastrophizing": "Catastrophizing",
        "perfectionism": "Perfectionism",
        "avoidance": "Avoidance",
        "panic_attacks": "Panic Attacks",
        "social_anxiety": "Social Anxiety",

        # Depression symptoms
        "anhedonia": "Anhedonia",
        "brain_fog": "Brain Fog",
        "fatigue": "Fatigue",
        "emotional_numbness": "Emotional Numbness",
        "sleep_issues": "Sleep Issues",

        # Sensory symptoms
        "hypersensitivity": "Hypersensitivity",
        "hyposensitivity": "Hyposensitivity",
        "sound_sensitivity": "Sound Sensitivity",
        "light_sensitivity": "Light Sensitivity",
        "texture_sensitivity": "Texture Sensitivity",
        "vestibular_issues": "Vestibular Issues",

        # Cognitive symptoms
        "working_memory_issues": "Working Memory Issues",
        "processing_speed": "Processing Speed",
        "cognitive_flexibility": "Cognitive Flexibility",
        "pattern_recognition": "Pattern Recognition",
        "detail_focused": "Detail Focused",

        # Social/Communication
        "nonverbal_communication": "Nonverbal Communication",
        "social_cues": "Social Cues",
        "boundaries": "Boundaries",
        "empathy_differences": "Empathy Differences",
        "communication_style": "Communication Style"
    }
}

# Language texts for Alt3r
TEXTS = {
    "ru": {
        "welcome": "🧠 Добро пожаловать в Alt3r!\n\nЭто бот для знакомств нейроотличных людей. Здесь вы можете найти понимание, поддержку и настоящие связи с теми, кто разделяет ваш опыт.\n\n✨ Давайте создадим вашу анкету!",
        "main_menu": "🏠 Главное меню",
        "profile_menu_0": "👤 Моя анкета",
        "profile_menu_1": "👀 Смотреть анкеты",
        "profile_menu_2": "🧠 Нейропоиск",
        "profile_menu_3": "📸 Изменить фото/видео",
        "profile_menu_4": "✍️ Изменить описание",
        "profile_menu_5": "💌 Мои лайки",
        "profile_menu_6": "⚙️ Настройки профиля",
        "profile_menu_7": "📝 Обратная связь",
        "profile_menu_8": "📊 Статистика",
        "language_menu": "🌐 Язык",
        "choose_language": "🌐 Выберите язык:",
        "language_set_ru": "✅ Язык установлен: Русский",
        "language_set_en": "✅ Язык установлен: English",
        "statistics_title": "📊 Ваша статистика",
        "registration_date": "Регистрация:",
        "profile_completion": "Заполненность профиля:",
        "activity_section": "Активность:",
        "likes_sent": "Отправлено лайков:",
        "likes_received": "Получено лайков:",
        "mutual_likes": "Взаимные лайки:",
        "detailed_stats": "📈 Подробная статистика",
        "profile_views": "Просмотры профиля:",
        "days_active": "Дней в приложении:",
        "success_rate": "Процент успеха:",
        "total_users": "Всего пользователей:",
        "app_stats": "🌍 Статистика приложения:",
        "change_name": "👤 Изменить имя",
        "change_city": "📍 Изменить город",
        "change_interest": "💕 Изменить предпочтения",
        "my_characteristics": "🧠 Мои характеристики",
        "questionnaire_age": "Сколько вам лет?",
        "questionnaire_gender": "Ваш пол?",
        "questionnaire_interest": "Кто вас интересует?",
        "questionnaire_city": "📍 Поделитесь вашим местоположением или введите город:",
        "questionnaire_name": "Как к вам обращаться?",
        "questionnaire_bio": "Расскажите о себе и о том, кого хотите найти. Это поможет лучше подобрать совпадения.",
        "questionnaire_photo": "Теперь отправьте до 3 фото, видео или GIF 👍 (видео до 15 сек)",
        "profile_preview": "Вот как выглядит ваша анкета:",
        "profile_correct": "Всё правильно?",
        "btn_girls": "Девушки",
        "btn_boys": "Парни",
        "btn_all": "Всё равно",
        "btn_girl": "Девушка",
        "btn_boy": "Парень",
        "btn_yes": "✅ Да",
        "btn_change": "🔄 Изменить",
        "btn_skip": "⏭️ Пропустить",
        "years_old": "лет",
        "seeking": "ищет",
        "city": "Город:",
        "about_me": "О себе:",
        "ready_to_connect": "Готов к общению!",
        "profile_saved": "✅ Анкета сохранена! Добро пожаловать в Alt3r!",
        "no_profiles": "😕 Пока нет доступных анкет. Попробуйте позже!",
        "like_sent": "❤️ Лайк отправлен!",
        "skip_profile": "⏭️ Пропущено",
        "its_match": "🎉 Взаимный лайк!\n\nВы можете написать друг другу:",
        "new_like": "❤️ Вам поставили лайк!",
        "photo_updated": "✅ Фото обновлено!",
        "bio_updated": "✅ Описание обновлено!",
        "send_message": "💌 Отправить сообщение",
        "back_to_menu": "🏠 В главное меню",
        "message_sent": "✅ Сообщение отправлено!",
        "enter_message": "Введите ваше сообщение:",
        "cancel": "❌ Отмена",
        "feedback_prompt": "📝 Опишите вашу проблему или предложение:",
        "feedback_sent": "✅ Спасибо за обратную связь!",
        "complaint": "🚨 Жалоба",
        "suggestion": "💡 Предложение",
        "statistics": "📊 Статистика",
        "photo_count": "Фото {}/3 добавлено!",
        "photo_done": "✅ Готово",
        "photo_skip_remaining": "⏭️ Пропустить остальные",
        "photo_send_more": "Отправьте еще фото или нажмите кнопку:",
        "photo_max_reached": "⚠️ Максимум 3 фото. Нажмите 'Готово' чтобы продолжить.",
        "photo_at_least_one": "⚠️ Пожалуйста, сначала отправьте хотя бы одно фото",
        "view_my_profile": "👤 Посмотреть мою анкету",
        "profile_incomplete": "❌ Ваш профиль не завершен. Завершите создание анкеты сначала.",
        "no_photos": "📸 Фото не добавлено",
        "change_photo": "📸 Изменить фото",
        "change_bio": "✍️ Изменить описание",
        "new_bio_prompt": "Введите новое описание:",
        "new_photo_prompt": "Отправьте новое фото:",
        "browse_profiles_empty": "😕 Нет доступных анкет для просмотра",
        "profile_liked": "❤️ Лайк отправлен!",
        "profile_passed": "👎 Пропущено",
        "like_button": "❤️",
        "pass_button": "👎",
        "back_button": "🔙 Назад",
        "settings_menu": "⚙️ Настройки",
        "settings_description": "Управление настройками профиля:",
        "change_language_btn": "🌐 Изменить язык",
        "current_language": "Текущий язык: Русский",
        "nd_characteristics": "ND Характеристики",
        "nd_traits": "ND Особенности",
        "nd_search": "ND Поиск",
        "search_by_traits": "Поиск по особенностям",
        "compatibility_search": "Поиск совместимости",
        "recommendations": "Рекомендации",
        "my_characteristics": "Мои характеристики",
        "change_characteristics": "Изменить характеристики",
        "select_traits": "Выберите ваши нейроотличности:",
        "select_characteristics": "Выберите характеристики, которые вас описывают:",
        "selected": "Выбрано:",
        "save": "Сохранить",
        "traits_saved": "✅ Особенности сохранены!",
        "characteristics_saved": "✅ Характеристики сохранены!",
        "no_nd_results": "😕 Не найдено пользователей с похожими особенностями",
        "common_traits": "Общие особенности:",
        "feedback_complaint": "🚨 Опишите вашу жалобу:",
        "feedback_suggestion": "💡 Поделитесь вашим предложением:",
        "feedback_support": "🆘 Опишите техническую проблему:",
        "rate_app": "⭐ Оценить Alt3r",
        "rate_app_prompt": "⭐ Оценить Alt3r\n\nКак вам наше приложение?",
        "rating_thanks": "✅ Спасибо за оценку",
        "detailed_stats": "📈 Подробная статистика",
        "profile_views": "Просмотры профиля:",
        "days_active": "Дней в приложении:",
        "success_rate": "Процент успеха:",
        "total_users": "Всего пользователей:",
        "app_stats": "🌍 Статистика приложения:",
        "recreate_profile": "🔄 Заполнить анкету заново",
        "recreate_confirm": "⚠️ Вы уверены, что хотите заполнить анкету заново?\n\nЭто удалит всю текущую информацию и вам нужно будет заполнить всё снова.\n\nЭто действие нельзя отменить!",
        "recreate_started": "🔄 Начинаем заполнение анкеты заново!\n\n✨ Давайте создадим вашу новую анкету. Мы пройдем все шаги заново.\n\nЧтобы начать создание анкеты, отправьте /start",
        "delete_account": "🗑️ Удалить аккаунт",
        "delete_confirm": "⚠️ Вы уверены, что хотите удалить аккаунт?\n\nЭто действие нельзя отменить!",
        "account_deleted": "🗑️ Аккаунт удален.\n\nДо свидания! Используйте /start если захотите вернуться.",
        "change_city": "📍 Изменить город",
        "change_interest": "💕 Изменить предпочтения",
        "current_city": "Текущий город:",
        "current_interest": "Текущие предпочтения:",
        "city_updated": "✅ Город изменен на:",
        "interest_updated": "✅ Предпочтения обновлены!",
        "enter_city": "📍 Введите ваш новый город:",
        "share_location": "📍 Поделитесь вашим местоположением:",
        "share_gps": "📍 Поделиться GPS локацией",
        "enter_manually": "✍️ Ввести город вручную",
        "location_detected": "📍 Определено местоположение:",
        "location_help": "Это поможет найти людей поблизости!",
        "gps_error": "❌ Не удалось определить город по GPS. Пожалуйста, введите город вручную:",
        "enter_city_manual": "📝 Пожалуйста, введите ваш город:",
        "send_video_message": "🎥 Отправить видео-сообщение",
        "video_message_prompt": "🎥 Отправка видео-сообщения пользователю {}\n\nЗапишите круглое видео-сообщение (зажмите и удерживайте кнопку записи в Telegram):",
        "video_sent": "✅ Видео-сообщение отправлено!",
        "video_send_error": "❌ Не удалось отправить видео. Возможно, пользователь заблокировал бота.",
        "message_to_user": "💌 Отправка сообщения пользователю {}\n\nНапишите ваше сообщение:",
        "message_send_error": "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.",
        "gender_selection_error": "Please select gender from the given options.",
        "interest_selection_error": "Please select from the given options.",
        "nd_selection_prompt": "🧠 Select your neurodivergent traits:\n\nThis will help find people with similar experience!\nYou can select up to 3 traits.",
        "nd_selected_count": "Selected:",
        "selecting_traits": "Selecting traits...",
        "default_bio_skip": "Will tell about myself later",
        "back_to_main_menu": "🔙 Back to main menu",
        "back_button": "🔙 Back",
        "btn_save": "💾 Save",
        "btn_skip_all": "⏭️ Skip all",
        "btn_done": "✅ Done",
        "btn_skip_remaining": "⏭️ Skip remaining",
        "use_gps": "📍 Use GPS",
        "manual_entry": "✍️ Manual entry",
        "share_gps": "📍 Share GPS location",
        "max_traits_reached": "❌ Можно выбрать максимум 3 особенности",
        "max_characteristics_reached": "❌ Можно выбрать максимум 3 характеристики",
        "function_in_development": "Функция в разработке",
        "error_occurred": "Произошла ошибка. Попробуйте еще раз.",
        "restart_hint": "Используйте /start для перезапуска при необходимости.",
        "age_prompt_error": "Пожалуйста, введите ваш возраст числом.",
        "age_range_error": "Пожалуйста, введите возраст от 18 до 100 лет.",
        "gender_selection_error": "Пожалуйста, выберите пол из предложенных вариантов.",
        "interest_selection_error": "Пожалуйста, выберите из предложенных вариантов.",
        "location_sharing_error": "Пожалуйста, поделитесь местоположением или введите город вручную.",
        "photo_required": "📸 Пожалуйста, сначала отправьте хотя бы одно фото или видео",
        "media_send_prompt": "📸 Отправьте фото, видео или видео-сообщение",
        "gps_processing_error": "❌ Ошибка обработки GPS. Пожалуйста, введите город вручную:",
        "profile_missing_field_error": "❌ Ошибка: отсутствует поле '{field}'. Начните заново с /start",
        "media_upload_error": "❌ Ошибка загрузки медиафайла. Попробуйте еще раз.",
        "profile_save_error": "❌ Ошибка при сохранении профиля. Попробуйте еще раз или обратитесь в поддержку.",
        "gender_selection_error": "Пожалуйста, выберите пол из предложенных вариантов.",
        "interest_selection_error": "Пожалуйста, выберите из предложенных вариантов.",
        "nd_selection_prompt": "🧠 Выберите ваши нейроотличности:\n\nЭто поможет найти людей с похожим опытом!\nМожно выбрать до 3 особенностей.",
        "nd_selected_count": "Выбрано:",
        "selecting_traits": "Выбор особенностей...",
        "default_bio_skip": "Расскажу о себе позже",
        "back_to_main_menu": "🔙 Назад к главному меню",
        "back_button": "🔙 Назад",
        "btn_save": "💾 Сохранить", 
        "btn_skip_all": "⏭️ Пропустить всё",
        "btn_done": "✅ Готово",
        "btn_skip_remaining": "⏭️ Пропустить остальные",
        "use_gps": "📍 Использовать GPS",
        "manual_entry": "✍️ Ввести вручную",
        "reset_matches": "💔 Сбросить совпадения",
        "change_photo": "📸 Изменить фото",
        "change_bio": "✍️ Изменить описание",
        "nd_traits": "Нейроотличия", 
        "nd_characteristics_label": "Характеристики", 
        "and_more": " и ",
        "profile_not_found": "❌ Профиль не найден. Отправьте /start для создания профиля."
    },
    "en": {
        "welcome": "🧠 Welcome to Alt3r!\n\nThis is a dating bot for neurodivergent people. Here you can find understanding, support and real connections with those who share your experience.\n\n✨ Let's create your profile!",
        "main_menu": "🏠 Main Menu",
        "profile_menu_0": "👤 My Profile",
        "profile_menu_1": "👀 Browse Profiles", 
        "profile_menu_2": "🧠 ND-Search",
        "profile_menu_3": "📸 Change Photo/Video",
        "profile_menu_4": "✍️ Change Bio",
        "profile_menu_5": "💌 My Likes",
        "profile_menu_6": "⚙️ Settings",
        "profile_menu_7": "📝 Feedback",
        "profile_menu_8": "📊 Statistics",
        "language_menu": "🌐 Language",
        "choose_language": "🌐 Choose language:",
        "language_set_ru": "✅ Language set: Русский",
        "language_set_en": "✅ Language set: English",
        "statistics_title": "📊 Your Statistics",
        "registration_date": "Registration:",
        "profile_completion": "Profile completion:",
        "activity_section": "Activity:",
        "likes_sent": "Likes sent:",
        "likes_received": "Likes received:",
        "mutual_likes": "Mutual likes:",
        "detailed_stats": "📈 Detailed Statistics",
        "profile_views": "Profile views:",
        "days_active": "Days in app:",
        "success_rate": "Success rate:",
        "total_users": "Total users:",
        "app_stats": "🌍 App Statistics:",
        "change_name": "👤 Change Name",
        "change_city": "📍 Change City",
        "change_interest": "💕 Change Interest",
        "my_characteristics": "🧠 My Characteristics",
        "questionnaire_age": "How old are you?",
        "questionnaire_gender": "What's your gender?",
        "questionnaire_interest": "Who are you interested in?",
        "questionnaire_city": "📍 Share your location or enter your city:",
        "questionnaire_name": "What should I call you?",
        "questionnaire_bio": "Tell me about yourself and who you want to find. This will help better match you.",
        "questionnaire_photo": "Now send up to 3 photos, video, or GIF 👍 (video up to 15 sec)",
        "profile_preview": "This is how your profile looks:",
        "profile_correct": "Is everything correct?",
        "btn_girls": "Girls",
        "btn_boys": "Boys", 
        "btn_all": "Doesn't matter",
        "btn_girl": "I'm a girl",
        "btn_boy": "I'm a boy",
        "btn_yes": "✅ Yes",
        "btn_change": "🔄 Change",
        "btn_skip": "⏭️ Skip",
        "years_old": "years old",
        "seeking": "seeking",
        "city": "City:",
        "about_me": "About:",
        "ready_to_connect": "Ready to connect!",
        "profile_saved": "✅ Profile saved! Welcome to Alt3r!",
        "no_profiles": "😕 No profiles available right now. Try again later!",
        "like_sent": "❤️ Like sent!",
        "skip_profile": "⏭️ Skipped",
        "its_match": "🎉 It's a match!\n\nYou can message each other:",
        "new_like": "❤️ Someone liked you!",
        "photo_updated": "✅ Photo updated!",
        "bio_updated": "✅ Bio updated!",
        "send_message": "💌 Send Message",
        "back_to_menu": "🏠 Back to Menu",
        "message_sent": "✅ Message sent!",
        "enter_message": "Enter your message:",
        "cancel": "❌ Cancel",
        "feedback_prompt": "📝 Describe your issue or suggestion:",
        "feedback_sent": "✅ Thank you for your feedback!",
        "complaint": "🚨 Complaint",
        "suggestion": "💡 Suggestion", 
        "statistics": "📊 Statistics",
        "photo_count": "Photo {}/3 added!",
        "photo_done": "✅ Done",
        "photo_skip_remaining": "⏭️ Skip remaining",
        "photo_send_more": "Send another photo or click button:",
        "photo_max_reached": "⚠️ Maximum 3 photos. Click 'Done' to continue.",
        "photo_at_least_one": "⚠️ Please send at least one photo first",
        "view_my_profile": "👤 View my profile",
        "profile_incomplete": "❌ Your profile is incomplete. Please complete your profile first.",
        "no_photos": "📸 No photo added",
        "change_photo": "📸 Change photo",
        "change_bio": "✍️ Change bio",
        "new_bio_prompt": "Enter new bio:",
        "new_photo_prompt": "Send new photo:",
        "browse_profiles_empty": "😕 No profiles available to browse",
        "profile_liked": "❤️ Like sent!",
        "profile_passed": "👎 Passed",
        "like_button": "❤️",
        "pass_button": "👎",
        "back_button": "🔙 Back",
        "settings_menu": "⚙️ Settings",
        "settings_description": "Manage your profile settings:",
        "change_language_btn": "🌐 Change Language",
        "current_language": "Current language: English",
        "nd_characteristics": "ND Characteristics",
        "nd_traits": "ND Traits",
        "nd_search": "ND Search",
        "search_by_traits": "Search by Traits",
        "compatibility_search": "Compatibility Search",
        "recommendations": "Recommendations",
        "my_characteristics": "My Characteristics",
        "change_characteristics": "Change Characteristics",
        "select_traits": "Select your neurodivergent traits:",
        "select_characteristics": "Select characteristics that describe you:",
        "selected": "Selected:",
        "save": "Save",
        "traits_saved": "✅ Traits saved!",
        "characteristics_saved": "✅ Characteristics saved!",
        "no_nd_results": "😕 No users found with similar traits",
        "common_traits": "Common traits:",
        "feedback_complaint": "🚨 Describe your complaint:",
        "feedback_suggestion": "💡 Share your suggestion:",
        "feedback_support": "🆘 Describe the technical issue:",
        "rate_app": "⭐ Rate Alt3r",
        "rate_app_prompt": "⭐ Rate Alt3r\n\nHow do you like our app?",
        "rating_thanks": "✅ Thank you for rating",
        "detailed_stats": "📈 Detailed Statistics",
        "profile_views": "Profile views:",
        "days_active": "Days in app:",
        "success_rate": "Success rate:",
        "total_users": "Total users:",
        "app_stats": "🌍 App Statistics:",
        "recreate_profile": "🔄 Recreate Profile",
        "recreate_confirm": "⚠️ Are you sure you want to recreate your profile?\n\nThis will delete all your current information and you'll need to fill everything again.\n\nThis action cannot be undone!",
        "recreate_started": "🔄 Profile Recreation Started!\n\n✨ Let's create your new profile. We'll go through all the steps again.\n\nTo restart the profile creation process, please send /start",
        "delete_account": "🗑️ Delete Account",
        "delete_confirm": "⚠️ Are you sure you want to delete your account?\n\nThis action cannot be undone!",
        "account_deleted": "🗑️ Account deleted.\n\nGoodbye! Use /start if you want to return.",
        "change_city": "📍 Change City",
        "change_interest": "💕 Change Interest",
        "current_city": "Current city:",
        "current_interest": "Current interest:",
        "city_updated": "✅ City updated to:",
        "interest_updated": "✅ Interest updated!",
        "enter_city": "📍 Enter your new city:",
        "share_location": "📍 Share your location:",
        "share_gps": "📍 Share GPS location",
        "enter_manually": "✍️ Enter city manually",
        "location_detected": "📍 Location detected:",
        "location_help": "This will help find people nearby!",
        "gps_error": "❌ Couldn't determine your city from GPS. Please enter your city manually:",
        "enter_city_manual": "📝 Please enter your city:",
        "send_video_message": "🎥 Send video message",
        "video_message_prompt": "🎥 Sending video message to user {}\n\nRecord a round video message (press and hold the record button in Telegram):",
        "video_sent": "✅ Video message sent!",
        "video_send_error": "❌ Failed to send video. The user may have blocked the bot.",
        "message_to_user": "💌 Sending message to user {}\n\nWrite your message:",
        "message_send_error": "❌ Failed to send message. The user may have blocked the bot.",
        "max_traits_reached": "❌ You can select maximum 3 traits",
        "max_characteristics_reached": "❌ You can select maximum 3 characteristics",
        "function_in_development": "Function in development",
        "error_occurred": "An error occurred. Please try again.",
        "restart_hint": "Use /start to restart if needed.",
        "age_prompt_error": "Please enter your age as a number.",
        "age_range_error": "Please enter age between 18 and 100 years.",
        "gender_selection_error": "Please select gender from the suggested options.",
        "interest_selection_error": "Please select from the suggested options.",
        "location_sharing_error": "Please share your location or enter your city manually.",
        "photo_required": "📸 Please send at least one photo or video first",
        "media_send_prompt": "📸 Send photo, video or video message",
        "recreate_profile": "🔄 Recreate Profile",
        "recreate_confirm": "⚠️ Are you sure you want to recreate your profile?\n\nThis will delete all current information and you'll need to fill everything again.\n\nThis action cannot be undone!",
        "recreate_started": "🔄 Profile creation started again!\n\n✨ Let's create your new profile. We'll go through all steps again.\n\nTo start creating your profile, send /start",
        "app_stats": "🌍 App statistics:",
        "back_to_main_menu": "🔙 Back to main menu",
        "btn_save": "💾 Save",
        "btn_skip_all": "⏭️ Skip all",
        "btn_done": "✅ Done",
        "btn_skip_remaining": "⏭️ Skip remaining",
        "use_gps": "📍 Use GPS",
        "manual_entry": "✍️ Manual entry",
        "nd_selection_prompt": "🧠 Select your neurodivergent traits:\n\nThis will help find people with similar experience!\nYou can select up to 3 traits.",
        "nd_selected_count": "Selected:",
        "selecting_traits": "Selecting traits...",
        "default_bio_skip": "Will tell about myself later",
        "anhedonia": "Anhedonia",
        "avoidance": "Avoidance",
        "boundaries": "Boundaries",
        "brain_fog": "Brain Fog",
        "catastrophizing": "Catastrophizing", 
        "cognitive_flexibility": "Cognitive Flexibility",
        "communication_style": "Communication Style",
        "detail_focused": "Detail Focused",
        "echolalia": "Echolalia",
        "emotional_numbness": "Emotional Numbness",
        "empathy_differences": "Empathy Differences",
        "executive_dysfunction": "Executive Dysfunction",
        "fatigue": "Fatigue",
        "hyperactivity": "Hyperactivity",
        "hyperfocus": "Hyperfocus",
        "hypersensitivity": "Hypersensitivity",
        "hyposensitivity": "Hyposensitivity",
        "impulsivity": "Impulsivity",
        "inattention": "Inattention",
        "light_sensitivity": "Light Sensitivity",
        "literal_thinking": "Literal Thinking",
        "meltdowns": "Meltdowns",
        "nonverbal_communication": "Nonverbal Communication",
        "overthinking": "Overthinking",
        "panic_attacks": "Panic Attacks",
        "pattern_recognition": "Pattern Recognition",
        "perfectionism": "Perfectionism",
        "processing_speed": "Processing Speed",
        "procrastination": "Procrastination",
        "rejection_sensitive": "Rejection Sensitive",
        "routine_dependent": "Routine Dependent",
        "sensory_overload": "Sensory Overload",
        "shutdowns": "Shutdowns",
        "sleep_issues": "Sleep Issues",
        "social_anxiety": "Social Anxiety",
        "social_cues": "Social Cues",
        "social_masking": "Social Masking",
        "sound_sensitivity": "Sound Sensitivity",
        "special_interests": "Special Interests",
        "stimming": "Stimming",
        "texture_sensitivity": "Texture Sensitivity",
        "time_blindness": "Time Blindness",
        "vestibular_issues": "Vestibular Issues",
        "working_memory_issues": "Working Memory Issues",
        "reset_matches": "💔 Reset Matches",
        "change_photo": "📸 Change Photo",
        "change_bio": "✍️ Change Bio",
        "nd_traits": "ND Traits",
        "nd_characteristics_label": "Characteristics",
        "and_more": " and ",
        "gps_processing_error": "❌ GPS processing error. Please enter city manually:",
        "profile_missing_field_error": "❌ Error: missing field '{field}'. Start over with /start",
        "media_upload_error": "❌ Media upload error. Please try again.",
        "profile_save_error": "❌ Profile save error. Please try again or contact support.",
        "profile_not_found": "❌ Profile not found. Send /start to create a profile."
    }
}

def normalize_city(city_input):
    """Normalize city names to handle different languages/spellings with typo correction"""
    city_lower = city_input.lower().strip()

    # Comprehensive global cities database with common typos and alternative spellings
    global_cities = {
        # European Cities
        "warszawa": ["warszawa", "варшава", "wawa", "warshawa", "warsaw", "варшав", "варшаве", "варшавы", "варшавa", "waršava", "warschau"],
        "berlin": ["berlin", "берлин", "берлине", "берлина", "berlín", "berlino", "berlim", "берлін"],
        "prague": ["prague", "прага", "praha", "праге", "праги", "praga", "prága", "prag"],
        "vienna": ["vienna", "вена", "вене", "wien", "bécs", "vienne", "viena", "wiedeń"],
        "budapest": ["budapest", "будапешт", "будапеште", "budapeşt", "budapesta", "budapeste"],
        "paris": ["paris", "париж", "parijs", "parís", "parigi", "paryz"],
        "london": ["london", "лондон", "londres", "londyn", "londra", "londen"],
        "madrid": ["madrid", "мадрид", "madryt"],
        "rome": ["rome", "рим", "roma", "rzym", "rim"],
        "amsterdam": ["amsterdam", "амстердам", "amsterdã"],
        "munich": ["munich", "мюнхен", "münchen", "monaco", "munique"],
        "zurich": ["zurich", "цюрих", "zürich", "zurych"],
        "geneva": ["geneva", "женева", "genève", "genewa", "ginevra"],
        "barcelona": ["barcelona", "барселона", "barcelone"],
        "milan": ["milan", "милан", "milano", "mediolan"],
        "athens": ["athens", "афины", "athína", "athen", "atene"],
        "stockholm": ["stockholm", "стокгольм", "estocolmo"],
        "oslo": ["oslo", "осло"],
        "copenhagen": ["copenhagen", "копенгаген", "københavn", "kopenhaga"],
        "helsinki": ["helsinki", "хельсинки"],
        "dublin": ["dublin", "дублин", "dublín", "dublino"],
        "lisbon": ["lisbon", "лиссабон", "lisboa", "lizbona"],
        "brussels": ["brussels", "брюссель", "bruxelles", "brussel", "bruksela"],
        "bucharest": ["bucharest", "бухарест", "bucureşti", "bukareszt"],
        "sofia": ["sofia", "софия", "szófia"],
        "zagreb": ["zagreb", "загреб"],
        "belgrade": ["belgrade", "белград", "beograd", "belgrado"],
        "kiev": ["kiev", "киев", "kyiv", "kijów", "kyjev"],
        "minsk": ["minsk", "минск"],
        "riga": ["riga", "рига"],
        "vilnius": ["vilnius", "вильнюс", "wilno"],
        "tallinn": ["tallinn", "таллин", "таллинн"],

        # North American Cities
        "new york": ["new york", "нью-йорк", "ny", "nyc", "nueva york", "new-york"],
        "los angeles": ["los angeles", "лос-анджелес", "la", "los ángeles"],
        "chicago": ["chicago", "чикаго"],
        "houston": ["houston", "хьюстон"],
        "philadelphia": ["philadelphia", "филадельфия", "philly"],
        "phoenix": ["phoenix", "финикс"],
        "san antonio": ["san antonio", "сан-антонио"],
        "san diego": ["san diego", "сан-диего"],
        "dallas": ["dallas", "даллас"],
        "san jose": ["san jose", "сан-хосе"],
        "austin": ["austin", "остин"],
        "jacksonville": ["jacksonville", "джексонвилл"],
        "san francisco": ["san francisco", "сан-франциско", "sf"],
        "columbus": ["columbus", "колумбус"],
        "charlotte": ["charlotte", "шарлотт"],
        "fort worth": ["fort worth", "форт-уорт"],
        "detroit": ["detroit", "детройт"],
        "el paso": ["el paso", "эль-пасо"],
        "memphis": ["memphis", "мемфис"],
        "seattle": ["seattle", "сиэтл"],
        "denver": ["denver", "денвер"],
        "washington": ["washington", "вашингтон", "dc", "washington dc"],
        "boston": ["boston", "бостон"],
        "nashville": ["nashville", "нашвилл"],
        "baltimore": ["baltimore", "балтимор"],
        "oklahoma city": ["oklahoma city", "оклахома-сити"],
        "louisville": ["louisville", "луисвилл"],
        "portland": ["portland", "портланд"],
        "las vegas": ["las vegas", "лас-вегас", "vegas"],
        "milwaukee": ["milwaukee", "милуоки"],
        "albuquerque": ["albuquerque", "альбукерке"],
        "tucson": ["tucson", "туксон"],
        "fresno": ["fresno", "фресно"],
        "sacramento": ["sacramento", "сакраменто"],
        "mesa": ["mesa", "меса"],
        "kansas city": ["kansas city", "канзас-сити"],
        "atlanta": ["atlanta", "атланта"],
        "long beach": ["long beach", "лонг-бич"],
        "colorado springs": ["colorado springs", "колорадо-спрингс"],
        "raleigh": ["raleigh", "роли"],
        "miami": ["miami", "майами"],
        "virginia beach": ["virginia beach", "вирджиния-бич"],
        "omaha": ["omaha", "омаха"],
        "oakland": ["oakland", "окленд"],
        "minneapolis": ["minneapolis", "миннеаполис"],
        "tulsa": ["tulsa", "талса"],
        "arlington": ["arlington", "арлингтон"],
        "new orleans": ["new orleans", "новый орлеан"],
        "wichita": ["wichita", "уичита"],
        "cleveland": ["cleveland", "кливленд"],
        "tampa": ["tampa", "тампа"],
        "bakersfield": ["bakersfield", "бейкерсфилд"],
        "aurora": ["aurora", "аврора"],
        "anaheim": ["anaheim", "анахайм"],
        "honolulu": ["honolulu", "гонолулу"],
        "santa ana": ["santa ana", "санта-ана"],
        "corpus christi": ["corpus christi", "корпус-кристи"],
        "riverside": ["riverside", "риверсайд"],
        "lexington": ["lexington", "лексингтон"],
        "stockton": ["stockton", "стоктон"],
        "toledo": ["toledo", "толедо"],
        "st. paul": ["st. paul", "сент-пол"],
        "st. petersburg": ["st. petersburg", "санкт-петербург флорида"],
        "pittsburgh": ["pittsburgh", "питтсбург"],
        "cincinnati": ["cincinnati", "цинциннати"],
        "anchorage": ["anchorage", "анкоридж"],
        "buffalo": ["buffalo", "буффало"],
        "plano": ["plano", "плано"],
        "lincoln": ["lincoln", "линкольн"],
        "henderson": ["henderson", "хендерсон"],
        "fort wayne": ["fort wayne", "форт-уэйн"],
        "jersey city": ["jersey city", "джерси-сити"],
        "chula vista": ["chula vista", "чула-виста"],
        "orlando": ["orlando", "орландо"],
        "laredo": ["laredo", "ларедо"],
        "norfolk": ["norfolk", "норфолк"],
        "chandler": ["chandler", "чандлер"],
        "madison": ["madison", "мэдисон"],
        "lubbock": ["lubbock", "лаббок"],
        "baton rouge": ["baton rouge", "батон-руж"],
        "reno": ["reno", "рено"],
        "akron": ["akron", "акрон"],
        "hialeah": ["hialeah", "хиалеа"],
        "rochester": ["rochester", "рочестер"],
        "glendale": ["glendale", "глендейл"],
        "garland": ["garland", "гарланд"],
        "fremont": ["fremont", "фримонт"],
        "scottsdale": ["scottsdale", "скоттсдейл"],
        "irvine": ["irvine", "ирвин"],
        "chesapeake": ["chesapeake", "чесапик"],
        "irving": ["irving", "ирвинг"],
        "north las vegas": ["north las vegas", "норт-лас-вегас"],
        "boise": ["boise", "бойсе"],
        "richmond": ["richmond", "ричмонд"],
        "spokane": ["spokane", "спокан"],
        "san bernardino": ["san bernardino", "сан-бернардино"],
        "des moines": ["des moines", "де-мойн"],
        "modesto": ["modesto", "модесто"],
        "fayetteville": ["fayetteville", "файетвилл"],
        "tacoma": ["tacoma", "такома"],
        "oxnard": ["oxnard", "окснард"],
        "fontana": ["fontana", "фонтана"],
        "columbus": ["columbus", "колумбус"],
        "montgomery": ["montgomery", "монтгомери"],
        "moreno valley": ["moreno valley", "морено-валли"],
        "shreveport": ["shreveport", "шривпорт"],
        "aurora": ["aurora", "аврора"],
        "yonkers": ["yonkers", "йонкерс"],
        "huntington beach": ["huntington beach", "хантингтон-бич"],
        "little rock": ["little rock", "литл-рок"],
        "salt lake city": ["salt lake city", "солт-лейк-сити"],
        "tallahassee": ["tallahassee", "таллахасси"],
        "worcester": ["worcester", "вустер"],
        "newport news": ["newport news", "ньюпорт-ньюс"],
        "huntsville": ["huntsville", "хантсвилл"],
        "knoxville": ["knoxville", "ноксвилл"],
        "providence": ["providence", "провиденс"],
        "fort lauderdale": ["fort lauderdale", "форт-лодердейл"],
        "grand rapids": ["grand rapids", "гранд-рапидс"],
        "amarillo": ["amarillo", "амарилло"],
        "peoria": ["peoria", "пеория"],
        "mobile": ["mobile", "мобил"],
        "columbia": ["columbia", "колумбия"],
        "grand prairie": ["grand prairie", "гранд-прери"],
        "glendale": ["glendale", "глендейл"],
        "overland park": ["overland park", "оверленд-парк"],
        "santa clarita": ["santa clarita", "санта-кларита"],
        "garden grove": ["garden grove", "гарден-гроув"],
        "oceanside": ["oceanside", "оушенсайд"],
        "tempe": ["tempe", "темпе"],
        "huntington beach": ["huntington beach", "хантингтон-бич"],
        "rancho cucamonga": ["rancho cucamonga", "ранчо-кукамонга"],
        "ontario": ["ontario", "онтарио"],
        "chattanooga": ["chattanooga", "чаттануга"],
        "sioux falls": ["sioux falls", "су-фолс"],
        "vancouver": ["vancouver", "ванкувер"],
        "cape coral": ["cape coral", "кейп-корал"],
        "springfield": ["springfield", "спрингфилд"],
        "salinas": ["salinas", "салинас"],
        "pembroke pines": ["pembroke pines", "пемброк-пайнс"],
        "elk grove": ["elk grove", "элк-гроув"],
        "rockford": ["rockford", "рокфорд"],
        "palmdale": ["palmdale", "палмдейл"],
        "corona": ["corona", "корона"],
        "paterson": ["paterson", "патерсон"],
        "hayward": ["hayward", "хейвард"],
        "pomona": ["pomona", "помона"],
        "torrance": ["torrance", "торранс"],
        "bridgeport": ["bridgeport", "бриджпорт"],
        "lakewood": ["lakewood", "лейквуд"],
        "hollywood": ["hollywood", "голливуд"],
        "fort collins": ["fort collins", "форт-коллинс"],
        "escondido": ["escondido", "эскондидо"],
        "naperville": ["naperville", "нейпервилл"],
        "syracuse": ["syracuse", "сиракьюс"],
        "kansas city": ["kansas city", "канзас-сити"],
        "alexandria": ["alexandria", "александрия"],
        "orange": ["orange", "ориндж"],
        "fullerton": ["fullerton", "фуллертон"],
        "pasadena": ["pasadena", "пасадена"],
        "savannah": ["savannah", "саванна"],
        "cary": ["cary", "кэри"],
        "warren": ["warren", "уоррен"],
        "carrollton": ["carrollton", "кэрроллтон"],
        "coral springs": ["coral springs", "корал-спрингс"],
        "stamford": ["stamford", "стэмфорд"],
        "concord": ["concord", "конкорд"],
        "cedar rapids": ["cedar rapids", "сидар-рапидс"],
        "charleston": ["charleston", "чарлстон"],
        "thousand oaks": ["thousand oaks", "таузенд-окс"],
        "elizabeth": ["elizabeth", "элизабет"],
        "mckinney": ["mckinney", "маккинни"],
        "sterling heights": ["sterling heights", "стерлинг-хайтс"],
        "sioux city": ["sioux city", "су-сити"],
        "eugene": ["eugene", "юджин"],
        "round rock": ["round rock", "раунд-рок"],
        "daly city": ["daly city", "дейли-сити"],
        "topeka": ["topeka", "топика"],
        "normandy": ["normandy", "нормандия"],
        "pearland": ["pearland", "пирленд"],
        "victorville": ["victorville", "викторвилл"],
        "ann arbor": ["ann arbor", "анн-арбор"],
        "santa rosa": ["santa rosa", "санта-роза"],
        "berkeley": ["berkeley", "беркли"],
        "temecula": ["temecula", "темекула"],
        "lansing": ["lansing", "лансинг"],
        "roseville": ["roseville", "розвилл"],
        "inglewood": ["inglewood", "инглвуд"],
        "college station": ["college station", "колледж-стейшн"],
        "rochester": ["rochester", "рочестер"],
        "downey": ["downey", "дауни"],
        "wilmington": ["wilmington", "уилмингтон"],
        "evansville": ["evansville", "эвансвилл"],
        "arvada": ["arvada", "арвада"],
        "odessa": ["odessa", "одесса"],
        "miami gardens": ["miami gardens", "майами-гарденс"],
        "westminster": ["westminster", "вестминстер"],
        "elgin": ["elgin", "элгин"],
        "provo": ["provo", "прово"],
        "clearwater": ["clearwater", "клируотер"],
        "gresham": ["gresham", "грешем"],
        "murfreesboro": ["murfreesboro", "мерфрисборо"],
        "wichita falls": ["wichita falls", "уичита-фолс"],
        "billings": ["billings", "биллингс"],
        "lowell": ["lowell", "лоуэлл"],
        "pueblo": ["pueblo", "пуэбло"],
        "richardson": ["richardson", "ричардсон"],
        "davenport": ["davenport", "давенпорт"],
        "west valley city": ["west valley city", "уэст-валли-сити"],
        "south bend": ["south bend", "саут-бенд"],
        "high point": ["high point", "хай-пойнт"],
        "midland": ["midland", "мидленд"],
        "flint": ["flint", "флинт"],
        "dearborn": ["dearborn", "дирборн"],
        "tuscaloosa": ["tuscaloosa", "таскалуса"],
        "killeen": ["killeen", "киллин"],
        "greensboro": ["greensboro", "гринсборо"],
        "fargo": ["fargo", "фарго"],
        "abilene": ["abilene", "абилин"],

        # Canadian Cities
        "toronto": ["toronto", "торонто"],
        "montreal": ["montreal", "монреаль", "montréal"],
        "vancouver": ["vancouver", "ванкувер"],
        "calgary": ["calgary", "калгари"],
        "edmonton": ["edmonton", "эдмонтон"],
        "ottawa": ["ottawa", "оттава"],
        "winnipeg": ["winnipeg", "виннипег"],
        "quebec city": ["quebec city", "квебек"],
        "hamilton": ["hamilton", "гамильтон"],
        "kitchener": ["kitchener", "китченер"],

        # Asian Cities
        "tokyo": ["tokyo", "токио", "tōkyō", "东京"],
        "beijing": ["beijing", "пекин", "peking", "北京"],
        "shanghai": ["shanghai", "шанхай", "上海"],
        "delhi": ["delhi", "дели", "नई दिल्ली"],
        "mumbai": ["mumbai", "мумбаи", "bombay", "бомбей"],
        "seoul": ["seoul", "сеул", "서울"],
        "bangkok": ["bangkok", "бангкок", "กรุงเทพฯ"],
        "jakarta": ["jakarta", "джакарта"],
        "manila": ["manila", "манила"],
        "singapore": ["singapore", "сингапур"],
        "hong kong": ["hong kong", "гонконг", "香港"],
        "kuala lumpur": ["kuala lumpur", "куала-лумпур"],
        "taipei": ["taipei", "тайбэй", "臺北"],
        "ho chi minh city": ["ho chi minh city", "хошимин", "saigon", "сайгон"],
        "yangon": ["yangon", "янгон", "rangoon"],
        "phnom penh": ["phnom penh", "пномпень"],
        "vientiane": ["vientiane", "вьентьян"],
        "ulaanbaatar": ["ulaanbaatar", "улан-батор"],
        "almaty": ["almaty", "алматы", "алма-ата"],
        "nur-sultan": ["nur-sultan", "нур-султан", "astana", "астана"],
        "tashkent": ["tashkent", "ташкент"],
        "bishkek": ["bishkek", "бишкек"],
        "dushanbe": ["dushanbe", "душанбе"],
        "ashgabat": ["ashgabat", "ашгабат"],
        "baku": ["baku", "баку"],
        "yerevan": ["yerevan", "ереван"],
        "tbilisi": ["tbilisi", "тбилиси"],
        "tehran": ["tehran", "тегеран"],
        "istanbul": ["istanbul", "стамбул", "istanbul"],
        "ankara": ["ankara", "анкара"],
        "riyadh": ["riyadh", "эр-рияд"],
        "dubai": ["dubai", "дубай"],
        "abu dhabi": ["abu dhabi", "абу-даби"],
        "doha": ["doha", "доха"],
        "kuwait city": ["kuwait city", "эль-кувейт"],
        "manama": ["manama", "манама"],
        "muscat": ["muscat", "маскат"],
        "jerusalem": ["jerusalem", "иерусалим", "ירושלים"],
        "tel aviv": ["tel aviv", "тель-авив"],
        "amman": ["amman", "амман"],
        "beirut": ["beirut", "бейрут"],
        "damascus": ["damascus", "дамаск"],
        "baghdad": ["baghdad", "багдад"],
        "kabul": ["kabul", "кабул"],
        "islamabad": ["islamabad", "исламабад"],
        "karachi": ["karachi", "карачи"],
        "lahore": ["lahore", "лахор"],
        "dhaka": ["dhaka", "дакка"],
        "colombo": ["colombo", "коломбо"],
        "kathmandu": ["kathmandu", "катманду"],
        "thimphu": ["thimphu", "тхимпху"],

        # African Cities
        "cairo": ["cairo", "каир", "القاهرة"],
        "lagos": ["lagos", "лагос"],
        "kinshasa": ["kinshasa", "киншаса"],
        "johannesburg": ["johannesburg", "йоханнесбург"],
        "cape town": ["cape town", "кейптаун"],
        "casablanca": ["casablanca", "касабланка"],
        "nairobi": ["nairobi", "найроби"],
        "addis ababa": ["addis ababa", "аддис-абеба"],
        "tunis": ["tunis", "тунис"],
        "algiers": ["algiers", "алжир"],
        "rabat": ["rabat", "рабат"],
        "tripoli": ["tripoli", "триполи"],
        "accra": ["accra", "аккра"],
        "abuja": ["abuja", "абуджа"],
        "dakar": ["dakar", "дакар"],
        "bamako": ["bamako", "бамако"],
        "conakry": ["conakry", "конакри"],
        "freetown": ["freetown", "фритаун"],
        "monrovia": ["monrovia", "монровия"],
        "abidjan": ["abidjan", "абиджан"],
        "ouagadougou": ["ouagadougou", "уагадугу"],

        # South American Cities
        "são paulo": ["são paulo", "сан-паулу", "sao paulo"],
        "rio de janeiro": ["rio de janeiro", "рио-де-жанейро", "rio"],
        "buenos aires": ["buenos aires", "буэнос-айрес"],
        "lima": ["lima", "лима"],
        "bogotá": ["bogotá", "богота", "bogota"],
        "santiago": ["santiago", "сантьяго"],
        "caracas": ["caracas", "каракас"],
        "quito": ["quito", "кито"],
        "la paz": ["la paz", "ла-пас"],
        "asunción": ["asunción", "асунсьон", "asuncion"],
        "montevideo": ["montevideo", "монтевидео"],
        "georgetown": ["georgetown", "джорджтаун"],
        "paramaribo": ["paramaribo", "парамарибо"],
        "cayenne": ["cayenne", "кайенна"],

        # Australian and Oceanian Cities
        "sydney": ["sydney", "сидней"],
        "melbourne": ["melbourne", "мельбурн"],
        "brisbane": ["brisbane", "брисбен"],
        "perth": ["perth", "перт"],
        "adelaide": ["adelaide", "аделаида"],
        "darwin": ["darwin", "дарвин"],
        "hobart": ["hobart", "хобарт"],
        "canberra": ["canberra", "канберра"],
        "auckland": ["auckland", "окленд"],
        "wellington": ["wellington", "веллингтон"],
        "christchurch": ["christchurch", "крайстчерч"],
        "suva": ["suva", "сува"],
        "port vila": ["port vila", "порт-вила"],
        "nuku'alofa": ["nuku'alofa", "нукуалофа"],
        "apia": ["apia", "апиа"],
        "port moresby": ["port moresby", "порт-морсби"],

        # Russian Cities with extensive variations
        "москва": ["москва", "москве", "москвы", "мск", "moscow", "moskva", "moscow city", "москов"],
        "санкт-петербург": ["санкт-петербург", "петербург", "спб", "питер", "санкт петербург", "с-петербург", "saint petersburg", "st petersburg", "petersburg", "ленинград", "leningrad"],
        "нижний новгород": ["нижний новгород", "нижний нрвгорд", "нижний-новгород", "нижний новгорд", "нжний новгород", "нижний новгрод", "ннов", "нн", "nizhny novgorod"],
        "екатеринбург": ["екатеринбург", "екб", "екатеринбрг", "екатеринубрг", "ектеринбург", "yekaterinburg", "екатернбург"],
        "новосибирск": ["новосибирск", "новосиб", "новосибрск", "нск", "novosibirsk", "новосибрск"],
        "казань": ["казань", "казани", "казан", "kazan", "кзн"],
        "челябинск": ["челябинск", "челяб", "челябнск", "chelyabinsk", "чел"],
        "омск": ["омск", "омске", "omsk"],
        "самара": ["самара", "самаре", "самары", "samara", "смр"],
        "ростов-на-дону": ["ростов-на-дону", "ростов", "ростов на дону", "рнд", "rostov", "ростов-на-дон"],
        "уфа": ["уфа", "уфе", "уфы", "ufa"],
        "красноярск": ["красноярск", "красноярске", "красноярка", "krasnoyarsk", "крск"],
        "воронеж": ["воронеж", "воронеже", "ворнеж", "voronezh", "врн"],
        "пермь": ["пермь", "перми", "прм", "perm"],
        "волгоград": ["волгоград", "волгограде", "влгоград", "volgograd", "влг"],
        "краснодар": ["краснодар", "краснодаре", "кдр", "krasnodar", "крд"],
        "саратов": ["саратов", "саратове", "сртв", "saratov", "срт"],
        "тюмень": ["тюмень", "тюмени", "тмн", "tyumen", "тмн"],
        "тольятти": ["тольятти", "тлт", "тольятте", "tolyatti", "тольяти"],
        "ижевск": ["ижевск", "ижевске", "ижвск", "izhevsk", "ижв"],
        "барнаул": ["барнаул", "барнауле", "брнл", "barnaul"],
        "ульяновск": ["ульяновск", "ульяновске", "ульянвск", "ulyanovsk", "улн"],
        "иркутск": ["иркутск", "иркутске", "иркцтск", "irkutsk", "ирк"],
        "хабаровск": ["хабаровск", "хабаровске", "хбрвск", "khabarovsk", "хбр"],
        "ярославль": ["ярославль", "ярославле", "ярослвль", "yaroslavl", "ярс"],
        "владивосток": ["владивосток", "владивостоке", "влдвсток", "vladivostok", "влд"],
        "махачкала": ["махачкала", "махачкале", "мхчкла", "makhachkala"],
        "томск": ["томск", "томске", "тмск", "tomsk"],
        "оренбург": ["оренбург", "оренбурге", "орнбрг", "orenburg", "орн"],
        "кемерово": ["кемерово", "кемерове", "кмрв", "kemerovo", "кем"],
        "рязань": ["рязань", "рязани", "рзн", "ryazan"],
        "набережные челны": ["набережные челны", "наб челны", "набчелны", "naberezhnye chelny", "нч"],
        "пенза": ["пенза", "пензе", "пнз", "penza"],
        "липецк": ["липецк", "липецке", "лпцк", "lipetsk", "лпц"],
        "тула": ["тула", "туле", "тл", "tula"],
        "киров": ["киров", "кирове", "крв", "kirov"],
        "чебоксары": ["чебоксары", "чебоксарах", "чбксры", "cheboksary", "чбк"],
        "калининград": ["калининград", "калининграде", "клннгрд", "kaliningrad", "кгд"],
        "брянск": ["брянск", "брянске", "брнск", "bryansk", "брн"],
        "курск": ["курск", "курске", "крск", "kursk"],
        "иваново": ["иваново", "иванове", "ивнв", "ivanovo", "ивн"],
        "магнитогорск": ["магнитогорск", "магнитогорске", "мгнтгрск", "magnitogorsk", "мгн"],
        "тверь": ["тверь", "твери", "твр", "tver"],
        "ставрополь": ["ставрополь", "ставрополе", "стврпль", "stavropol", "ств"],
        "нижний тагил": ["нижний тагил", "н тагил", "нижний тгил", "nizhny tagil", "нт"],
        "белгород": ["белгород", "белгороде", "блгрд", "belgorod", "блг"],
        "архангельск": ["архангельск", "архангельске", "архнгльск", "arkhangelsk", "арх"],
        "владимир": ["владимир", "владимире", "влдмр", "vladimir", "влд"],
        "сочи": ["сочи", "сочах", "сч", "sochi"],
        "курган": ["курган", "кургане", "кргн", "kurgan", "крг"],
        "смоленск": ["смоленск", "смоленске", "смлнск", "smolensk", "смл"],
        "калуга": ["калуга", "калуге", "клг", "kaluga", "клг"],
        "чита": ["чита", "чите", "чт", "chita"],
        "орел": ["орел", "орле", "орёл", "orel", "орл"],
        "волжский": ["волжский", "влжский", "volzhsky", "влж"],
        "череповец": ["череповец", "череповце", "чрпвц", "cherepovets", "чрп"],
        "вологда": ["вологда", "вологде", "влгд", "vologda", "влг"],
        "мурманск": ["мурманск", "мурманске", "мрмнск", "murmansk", "мрм"],
        "сургут": ["сургут", "сургуте", "сргт", "surgut", "срг"],
        "тамбов": ["тамбов", "тамбове", "тмбв", "tambov", "тмб"],
        "стерлитамак": ["стерлитамак", "стерлитамаке", "стрлтмк", "sterlitamak", "стр"],
        "грозный": ["грозный", "грозном", "грзный", "grozny", "грз"],
        "якутск": ["якутск", "якутске", "якцтск", "yakutsk", "якт"],
        "кострома": ["кострома", "костроме", "кстрм", "kostroma", "кст"],
        "комсомольск-на-амуре": ["комсомольск-на-амуре", "комсомольск", "кмсмльск", "komsomolsk", "кмс"],
        "петрозаводск": ["петрозаводск", "петрозаводске", "птрзвдск", "petrozavodsk", "птр"],
        "нижневартовск": ["нижневартовск", "нижневартовске", "нжнвртвск", "nizhnevartovsk", "нвр"],
        "йошкар-ола": ["йошкар-ола", "йошкар ола", "йшкр-ола", "yoshkar-ola", "йшк"],
        "новокузнецк": ["новокузнецк", "новокузнецке", "нвкзнцк", "novokuznetsk", "нкз"],
        "химки": ["химки", "химках", "хмки", "khimki", "хим"],
        "балашиха": ["балашиха", "балашихе", "блшх", "balashikha", "блш"],
        "энгельс": ["энгельс", "энгельсе", "нгльс", "engels", "энг"],
        "подольск": ["подольск", "подольске", "пдльск", "podolsk", "пдл"]
    }

    # Advanced typo detection and correction algorithm
    def calculate_similarity(str1, str2):
        """Calculate similarity between two strings using various metrics"""
        if str1 == str2:
            return 1.0
        
        # Exact match first
        if str1.lower() == str2.lower():
            return 1.0
        
        # Length difference check
        len_diff = abs(len(str1) - len(str2))
        max_len = max(len(str1), len(str2))
        
        # If length difference is too large, return low similarity
        if len_diff > max_len * 0.5:
            return 0.0
        
        # Character-by-character comparison with tolerance for typos
        matches = 0
        total_chars = max(len(str1), len(str2))
        
        # Use dynamic programming for edit distance
        dp = [[0] * (len(str2) + 1) for _ in range(len(str1) + 1)]
        
        for i in range(len(str1) + 1):
            dp[i][0] = i
        for j in range(len(str2) + 1):
            dp[0][j] = j
        
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        edit_distance = dp[len(str1)][len(str2)]
        similarity = 1 - (edit_distance / max_len)
        
        return max(0, similarity)

    def contains_most_chars(str1, str2):
        """Check if one string contains most characters of another"""
        shorter = str1 if len(str1) <= len(str2) else str2
        longer = str2 if len(str1) <= len(str2) else str1
        
        # Count matching characters
        longer_chars = list(longer.lower())
        matches = 0
        
        for char in shorter.lower():
            if char in longer_chars:
                longer_chars.remove(char)
                matches += 1
        
        return matches / len(shorter) >= 0.7  # At least 70% of characters match

    # Try to find exact matches first
    for correct_city, variations in global_cities.items():
        for variation in variations:
            if variation == city_lower:
                return correct_city.title()

    # Try fuzzy matching with similarity scoring
    best_match = None
    best_score = 0.0
    similarity_threshold = 0.7  # Minimum similarity required

    for correct_city, variations in global_cities.items():
        for variation in variations:
            # Skip if too different in length
            if abs(len(city_lower) - len(variation)) > 3:
                continue
            
            # Calculate similarity
            similarity = calculate_similarity(city_lower, variation)
            
            # Also check character containment for cases like "нрвгорд" -> "новгород"
            if similarity < 0.6 and contains_most_chars(city_lower, variation):
                similarity = max(similarity, 0.65)
            
            # Update best match if this is better
            if similarity > best_score and similarity >= similarity_threshold:
                best_score = similarity
                best_match = correct_city.title()

    # Return best match if found, otherwise return original with proper capitalization
    return best_match if best_match else city_input.strip().title()

async def safe_edit_message(query, text, reply_markup=None):
    """Safely edit message, handling both text and media messages"""
    try:
        await query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        error_str = str(e).lower()
        if "no text in the message to edit" in error_str or "message is not modified" in error_str:
            # Message has media or content is same, send new message
            try:
                await query.message.reply_text(text, reply_markup=reply_markup)
            except Exception as e2:
                logger.error(f"Failed to send new message: {e2}")
        else:
            # Other error, try to send new message
            try:
                await query.message.reply_text(text, reply_markup=reply_markup)
            except Exception as e2:
                logger.error(f"Failed to send fallback message: {e2}")

async def get_city_from_coordinates(latitude: float, longitude: float) -> str:
    """Get city name from GPS coordinates using reverse geocoding"""
    try:
        import aiohttp
        
        # Try multiple geocoding services for better reliability
        services = [
            {
                'url': f"https://nominatim.openstreetmap.org/reverse?lat={latitude}&lon={longitude}&format=json&accept-language=en",
                'headers': {'User-Agent': 'Alt3r Dating Bot'}
            },
            {
                'url': f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en",
                'headers': {}
            }
        ]
        
        for service in services:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(service['url'], headers=service['headers']) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Handle OpenStreetMap Nominatim response
                            if 'address' in data:
                                address = data.get('address', {})
                                city = (address.get('city') or 
                                       address.get('town') or 
                                       address.get('village') or 
                                       address.get('municipality') or 
                                       address.get('county') or 
                                       address.get('state'))
                                       
                                if city and city != "Unknown Location":
                                    return normalize_city(city)
                            
                            # Handle BigDataCloud response
                            elif 'locality' in data:
                                city = (data.get('locality') or 
                                       data.get('city') or 
                                       data.get('principalSubdivision'))
                                       
                                if city and city != "Unknown Location":
                                    return normalize_city(city)
                                    
            except Exception as service_error:
                logger.error(f"Error with geocoding service {service['url']}: {service_error}")
                continue
        
        # If all services fail, return a generic message
        logger.error(f"All geocoding services failed for coordinates: {latitude}, {longitude}")
        return "Unknown Location"

    except Exception as e:
        logger.error(f"Error in reverse geocoding: {e}")
        return "Unknown Location"

def is_profile_complete(user: UserModel) -> bool:
    """Check if user profile is complete"""
    if not user:
        return False
        
    # Check basic fields
    required_fields = [user.name, user.age, user.gender, user.interest, user.city, user.bio]
    for field in required_fields:
        if not field or (isinstance(field, str) and field.strip() == ''):
            return False

    # Check media - either media_id or photos array (must have actual content)
    has_media = (user.media_id and user.media_id.strip()) or (user.photos and len(user.photos) > 0 and user.photos[0])

    return bool(has_media)

def is_profile_complete_dict(user: Dict[str, Any]) -> bool:
    """Check if user profile is complete (dictionary version)"""
    if not user:
        return False
    
    required_fields = ['name', 'age', 'gender', 'interest', 'city', 'bio']
    
    # Check if all required fields are present and not empty
    for field in required_fields:
        if field not in user or not user[field]:
            return False
    
    # Check if user has at least one photo or media
    photos = user.get('photos', [])
    media_id = user.get('media_id', '')
    has_media = (media_id and media_id.strip()) or (photos and len(photos) > 0 and photos[0])

    return bool(has_media)  # Ensure boolean return

def get_text(user_id: int, key: str) -> str:
    """Get localized text for user"""
    user = db_manager.get_user(user_id)
    lang = user.lang if user else "ru"
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)

def get_main_menu(user_id: int) -> InlineKeyboardMarkup:
    """Get main menu keyboard for user"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "profile_menu_0"), callback_data="view_profile")],
        [InlineKeyboardButton(get_text(user_id, "profile_menu_1"), callback_data="browse_profiles")],
        [InlineKeyboardButton(get_text(user_id, "profile_menu_6"), callback_data="profile_settings")],
        [InlineKeyboardButton(get_text(user_id, "profile_menu_5"), callback_data="my_likes")],
        [
            InlineKeyboardButton(get_text(user_id, "profile_menu_7"), callback_data="feedback"),
            InlineKeyboardButton(get_text(user_id, "language_menu"), callback_data="change_language")
        ],
        [InlineKeyboardButton(get_text(user_id, "profile_menu_8"), callback_data="statistics")]
    ]
    return InlineKeyboardMarkup(keyboard)

# User rating system
def initialize_user_ratings():
    """Initialize rating system for existing users"""
    users = db.all()
    for user_data in users:
        if 'ratings' not in user_data:
            db.create_or_update_user(user_data['user_id'], {'ratings': [], 'total_rating': 0.0, 'rating_count': 0})

def add_rating(rated_user_id, rating_value, rater_user_id):
    """Add a rating for a user"""
    user = db.search(User.user_id == rated_user_id)
    if user:
        user_data = user[0]
        ratings = user_data.get('ratings', [])

        # Check if this rater already rated this user
        existing_rating = next((r for r in ratings if r['rater_id'] == rater_user_id), None)

        if existing_rating:
            # Update existing rating
            existing_rating['rating'] = rating_value
        else:
            # Add new rating
            ratings.append({
                'rater_id': rater_user_id,
                'rating': rating_value
            })

        # Calculate new average
        total_rating = sum(r['rating'] for r in ratings)
        rating_count = len(ratings)
        average_rating = total_rating / rating_count if rating_count > 0 else 0.0

        # Update database
        db.update({
            'ratings': ratings,
            'total_rating': average_rating,
            'rating_count': rating_count
        }, User.user_id == rated_user_id)

        return average_rating
    return None

def get_user_rating(user_id):
    """Get user's current rating"""
    user = db.get_user(user_id)
    if user:
        return {
            'rating': user.get('total_rating', 0.0),
            'count': user.get('rating_count', 0)
        }
    return {'rating': 0.0, 'count': 0}

async def add_like(from_user_id, to_user_id):
    """Add a like from one user to another - ATOMIC operation to prevent race conditions"""
    try:
        # ATOMIC UPDATE: Use db.update with callback to prevent race conditions
        def update_target_likes(doc):
            """Atomic callback to safely update target user's likes"""
            received_likes = doc.get('received_likes', [])
            unnotified_likes = doc.get('unnotified_likes', [])
            
            # Only add if not already present (idempotent operation)
            if from_user_id not in received_likes:
                received_likes.append(from_user_id)
                unnotified_likes.append(from_user_id)
                logger.info(f"✅ Added like from {from_user_id} to {to_user_id}")
                return {
                    **doc,
                    'received_likes': received_likes,
                    'unnotified_likes': unnotified_likes
                }
            else:
                logger.info(f"⚠️ Like from {from_user_id} to {to_user_id} already exists")
                return doc

        def update_sender_likes(doc):
            """Atomic callback to safely update sender's likes"""
            sent_likes = doc.get('sent_likes', [])
            
            # Only add if not already present (idempotent operation)
            if to_user_id not in sent_likes:
                sent_likes.append(to_user_id)
                logger.info(f"✅ Updated sent likes for user {from_user_id}")
                return {**doc, 'sent_likes': sent_likes}
            else:
                logger.info(f"⚠️ Sent like from {from_user_id} to {to_user_id} already exists")
                return doc

        # PostgreSQL atomic updates
        try:
            # Update target user's received likes
            target_user = db.get_user(to_user_id)
            if target_user:
                received_likes = target_user.get('received_likes', [])
                unnotified_likes = target_user.get('unnotified_likes', [])
                
                if from_user_id not in received_likes:
                    received_likes.append(from_user_id)
                    unnotified_likes.append(from_user_id)
                    db.update_user(to_user_id, {
                        'received_likes': received_likes,
                        'unnotified_likes': unnotified_likes
                    })
                    logger.info(f"✅ Added like from {from_user_id} to {to_user_id}")
            
            # Update sender's sent likes
            sender_user = db.get_user(from_user_id)
            if sender_user:
                sent_likes = sender_user.get('sent_likes', [])
                if to_user_id not in sent_likes:
                    sent_likes.append(to_user_id)
                    db.update_user(from_user_id, {'sent_likes': sent_likes})
                    logger.info(f"✅ Updated sent likes for user {from_user_id}")
        except Exception as update_error:
            logger.error(f"❌ Error in PostgreSQL like update: {update_error}")

    except Exception as e:
        logger.error(f"❌ Error adding like: {e}")
        import traceback
        traceback.print_exc()

def get_top_rated_users(min_rating=0.0, max_rating=5.0, current_user_id=None):
    """Get users within rating range"""
    users = db.all()
    filtered_users = []

    for user_data in users:
        if user_data['user_id'] == current_user_id:
            continue

        rating = user_data.get('total_rating', 0.0)
        rating_count = user_data.get('rating_count', 0)

        # Only include users with at least 1 rating and within range
        if rating_count > 0 and min_rating <= rating <= max_rating:
            filtered_users.append(user_data)

    # Sort by rating (highest first)
    filtered_users.sort(key=lambda x: x.get('total_rating', 0.0), reverse=True)
    return filtered_users

def matches_interest_criteria(user1: dict, user2: dict) -> bool:
    """Check if users match each other's interest criteria"""
    if not user1 or not user2 or not isinstance(user1, dict) or not isinstance(user2, dict):
        return False
        
    user1_interest = user1.get("interest", "both")
    user2_interest = user2.get("interest", "both")
    user1_gender = user1.get("gender", "")
    user2_gender = user2.get("gender", "")

    # Check if user1 is interested in user2's gender
    user1_interested = (user1_interest == "both" or 
                       (user1_interest == "female" and user2_gender == "female") or
                       (user1_interest == "male" and user2_gender == "male"))

    # Check if user2 is interested in user1's gender  
    user2_interested = (user2_interest == "both" or
                       (user2_interest == "female" and user1_gender == "female") or
                       (user2_interest == "male" and user1_gender == "male"))

    return user1_interested and user2_interested

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and send welcome message"""
    user_id = update.effective_user.id

    # Initialize ratings for all users if not done
    initialize_user_ratings()

    # Clear any existing conversation data
    context.user_data.clear()
    
    # Mark that we're starting a conversation
    context.user_data['in_conversation'] = True

    # Check if user exists and has complete profile
    existing_user = db.get_user(user_id)
    logger.info(f"DEBUG: User {user_id} exists: {existing_user is not None}")
    if existing_user:
        is_complete = is_profile_complete_dict(existing_user)
        logger.info(f"DEBUG: User {user_id} profile complete: {is_complete} (type: {type(is_complete)})")
        logger.info(f"DEBUG: User data: {existing_user}")
        
        if is_complete:
            # User already exists with complete profile - show main menu
            context.user_data.pop('in_conversation', None)  # Clear conversation flag
            await update.message.reply_text(
                get_text(user_id, "main_menu"),
                reply_markup=get_main_menu(user_id)
            )
            return ConversationHandler.END

    # If user exists but profile incomplete, continue where they left off
    if existing_user and not is_profile_complete_dict(existing_user):
        lang = existing_user.get('lang', 'ru')
        
        # Fill context with existing data where available
        if existing_user.get('age'):
            context.user_data['age'] = existing_user['age']
        if existing_user.get('gender'):
            context.user_data['gender'] = existing_user['gender']
        if existing_user.get('interest'):
            context.user_data['interest'] = existing_user['interest']
        if existing_user.get('city'):
            context.user_data['city'] = existing_user['city']
        if existing_user.get('name'):
            context.user_data['name'] = existing_user['name']
        if existing_user.get('bio'):
            context.user_data['bio'] = existing_user['bio']
        
        context.user_data['selected_nd_traits'] = existing_user.get('nd_traits', [])
        context.user_data['selected_characteristics'] = existing_user.get('nd_symptoms', [])
        
        if lang == 'en':
            welcome_back = "👋 Welcome back! Let's continue completing your profile.\n"
        else:
            welcome_back = "👋 С возвращением! Продолжаем заполнение вашей анкеты.\n"
        
        await update.message.reply_text(welcome_back, reply_markup=ReplyKeyboardRemove())
        
        # Continue from where they left off
        if not existing_user.get('age'):
            keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "questionnaire_age"), reply_markup=reply_markup)
            return AGE
        elif not existing_user.get('gender'):
            keyboard = [
                [KeyboardButton(get_text(user_id, "btn_girl"))],
                [KeyboardButton(get_text(user_id, "btn_boy"))],
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "questionnaire_gender"), reply_markup=reply_markup)
            return GENDER
        elif not existing_user.get('interest'):
            keyboard = [
                [KeyboardButton(get_text(user_id, "btn_girls"))],
                [KeyboardButton(get_text(user_id, "btn_boys"))],
                [KeyboardButton(get_text(user_id, "btn_all"))],
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "questionnaire_interest"), reply_markup=reply_markup)
            return INTEREST
        elif not existing_user.get('city'):
            keyboard = [
                [KeyboardButton(get_text(user_id, "share_gps"), request_location=True)],
                [KeyboardButton(get_text(user_id, "manual_entry"))],
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "share_location"), reply_markup=reply_markup)
            return CITY
        elif not existing_user.get('name'):
            keyboard = [[KeyboardButton(get_text(user_id, "back_button"))]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "questionnaire_name"), reply_markup=reply_markup)
            return NAME
        elif not existing_user.get('bio'):
            keyboard = [
                [KeyboardButton(get_text(user_id, "btn_skip"))],
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "questionnaire_bio"), reply_markup=reply_markup)
            return BIO
        elif not (existing_user.get('photos') or existing_user.get('media_id')):
            await update.message.reply_text(get_text(user_id, "questionnaire_photo"))
            return PHOTO

    # New user - start with language selection first
    # Set default language to English for new users
    db.create_or_update_user(user_id, {'lang': 'en'})
    
    # Show language selection first
    text = "🌐 Choose your language / Выберите язык:"
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # Set a flag to continue with profile creation after language selection
    context.user_data['needs_profile_creation'] = True
    return ConversationHandler.END

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle age input"""
    user_id = update.effective_user.id

    # Check if message exists and has text
    if not update.message or not update.message.text:
        try:
            keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "age_prompt_error"), reply_markup=reply_markup)
        except:
            logger.error("Failed to send age prompt message")
        return AGE

    try:
        age_text = update.message.text.strip()
        
        # Handle back button
        if age_text in ["🔙 Назад к главному меню", "🔙 Назад", "🔙 Back to main menu", "🔙 Back"]:
            await update.message.reply_text(
                get_text(user_id, "main_menu"),
                reply_markup=ReplyKeyboardRemove()
            )
            await update.message.reply_text(
                get_text(user_id, "main_menu"),
                reply_markup=get_main_menu(user_id)
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        if not age_text.isdigit():
            keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "age_prompt_error"), reply_markup=reply_markup)
            return AGE

        age = int(age_text)
        if 18 <= age <= 100:
            context.user_data["age"] = age
            logger.info(f"User {user_id} entered age: {age}")

            # Get current user to check language
            user = db.get_user(user_id)
            
            keyboard = [
                [KeyboardButton(get_text(user_id, "btn_girl"))],
                [KeyboardButton(get_text(user_id, "btn_boy"))],
                [KeyboardButton("🔙 " + ("Назад" if user and user.get('lang') == 'ru' else "Back"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(
                get_text(user_id, "questionnaire_gender"),
                reply_markup=reply_markup
            )
            return GENDER
        else:
            keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(get_text(user_id, "age_range_error"), reply_markup=reply_markup)
            return AGE
    except (ValueError, AttributeError) as e:
        logger.error(f"Error handling age input: {e}")
        keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(get_text(user_id, "age_prompt_error"), reply_markup=reply_markup)
        return AGE
    except Exception as e:
        logger.error(f"Unexpected error in handle_age: {e}")
        keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(get_text(user_id, "error_occurred"), reply_markup=reply_markup)
        return AGE

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle gender selection"""
    gender_text = update.message.text
    user_id = update.effective_user.id

    # Handle back button
    if gender_text in ["🔙 Назад", "🔙 Back"]:
        keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            get_text(user_id, "questionnaire_age"),
            reply_markup=reply_markup
        )
        return AGE

    if gender_text == get_text(user_id, "btn_girl"):
        context.user_data["gender"] = "female"
    elif gender_text == get_text(user_id, "btn_boy"):
        context.user_data["gender"] = "male"
    else:
        await update.message.reply_text(get_text(user_id, "gender_selection_error"))
        return GENDER

    keyboard = [
        [KeyboardButton(get_text(user_id, "btn_girls"))],
        [KeyboardButton(get_text(user_id, "btn_boys"))],
        [KeyboardButton(get_text(user_id, "btn_all"))],
        [KeyboardButton(get_text(user_id, "back_button"))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        get_text(user_id, "questionnaire_interest"),
        reply_markup=reply_markup
    )
    return INTEREST

async def handle_interest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle interest selection"""
    interest_text = update.message.text
    user_id = update.effective_user.id

    # Handle back button
    if interest_text in ["🔙 Назад", "🔙 Back"]:
        keyboard = [
            [KeyboardButton(get_text(user_id, "btn_girl"))],
            [KeyboardButton(get_text(user_id, "btn_boy"))],
            [KeyboardButton(get_text(user_id, "back_button"))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            get_text(user_id, "questionnaire_gender"),
            reply_markup=reply_markup
        )
        return GENDER

    if interest_text == get_text(user_id, "btn_girls"):
        context.user_data["interest"] = "female"
    elif interest_text == get_text(user_id, "btn_boys"):
        context.user_data["interest"] = "male"
    elif interest_text == get_text(user_id, "btn_all"):
        context.user_data["interest"] = "both"
    else:
        await update.message.reply_text(get_text(user_id, "interest_selection_error"))
        return INTEREST

    # Ask for location with GPS option
    keyboard = [
        [KeyboardButton(get_text(user_id, "share_gps"), request_location=True)],
        [KeyboardButton(get_text(user_id, "manual_entry"))],
        [KeyboardButton(get_text(user_id, "back_button"))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'

    await update.message.reply_text(
        get_text(user_id, "share_location"),
        reply_markup=reply_markup
    )
    return CITY

async def handle_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle city input or GPS location"""
    user_id = update.effective_user.id

    # Handle back button
    if update.message.text and update.message.text.strip() in ["🔙 Назад", "🔙 Back"]:
        keyboard = [
            [KeyboardButton(get_text(user_id, "btn_girls"))],
            [KeyboardButton(get_text(user_id, "btn_boys"))],
            [KeyboardButton(get_text(user_id, "btn_all"))],
            [KeyboardButton(get_text(user_id, "back_button"))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            get_text(user_id, "questionnaire_interest"),
            reply_markup=reply_markup
        )
        return INTEREST

    # Handle GPS location
    if update.message.location:
        try:
            latitude = update.message.location.latitude
            longitude = update.message.location.longitude

            # Show loading message
            user = db.get_user(user_id)
            lang = user.lang if user else 'ru'
            
            if lang == 'en':
                loading_msg = "📍 Detecting your city from GPS coordinates..."
            else:
                loading_msg = "📍 Определяем ваш город по GPS координатам..."
            
            loading_message = await update.message.reply_text(loading_msg)

            # Get city name from coordinates using reverse geocoding
            city = await get_city_from_coordinates(latitude, longitude)
            
            # Delete loading message
            try:
                await loading_message.delete()
            except:
                pass
            
            if city and city != "Unknown Location":
                context.user_data["city"] = city
                context.user_data["latitude"] = latitude
                context.user_data["longitude"] = longitude

                if lang == 'en':
                    location_confirmed = f"📍 Location detected: {city}\n\nThis will help find people nearby!"
                else:
                    location_confirmed = f"📍 Определено местоположение: {city}\n\nЭто поможет найти людей поблизости!"

                await update.message.reply_text(
                    location_confirmed,
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                # GPS failed, ask for manual input
                if lang == 'en':
                    error_msg = "❌ Couldn't determine your city from GPS. Please enter your city manually:"
                else:
                    error_msg = get_text(user_id, "gps_error")

                keyboard = [
                    [KeyboardButton("📍 Попробовать еще раз" if lang == 'ru' else "📍 Try again", request_location=True)],
                    [KeyboardButton(get_text(user_id, "back_button"))]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                await update.message.reply_text(error_msg, reply_markup=reply_markup)
                return CITY

        except Exception as e:
            logger.error(f"Error processing GPS location: {e}")

            user = db.get_user(user_id)
            lang = user.lang if user else 'ru'

            error_msg = get_text(user_id, "gps_processing_error")

            keyboard = [
                [KeyboardButton("📍 Попробовать еще раз" if lang == 'ru' else "📍 Try again", request_location=True)],
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(error_msg, reply_markup=reply_markup)
            return CITY

    # Handle manual city input button
    elif update.message.text == "✍️ Ввести город вручную" or update.message.text == "✍️ Enter city manually":
        user = db.get_user(user_id)
        lang = user.get('lang', 'ru') if user else 'ru'

        if lang == 'en':
            manual_prompt = "📝 Please enter your city:"
        else:
            manual_prompt = get_text(user_id, "enter_city_manual")

        keyboard = [
            [KeyboardButton("📍 Использовать GPS" if lang == 'ru' else "📍 Use GPS", request_location=True)],
            [KeyboardButton(get_text(user_id, "back_button"))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(manual_prompt, reply_markup=reply_markup)
        return CITY

    # Handle manual city text input
    elif update.message.text and update.message.text not in ["📍 Поделиться геолокацией", "📍 Share GPS location", "📍 Попробовать еще раз", "📍 Try again", "📍 Использовать GPS", "📍 Use GPS"]:
        city = normalize_city(update.message.text)
        context.user_data["city"] = city

        await update.message.reply_text(
            get_text(user_id, "questionnaire_name"),
            reply_markup=ReplyKeyboardRemove()
        )
        return NAME

    # If neither location nor valid text, ask again
    else:
        user = db.get_user(user_id)
        lang = user.get('lang', 'ru') if user else 'ru'

        if lang == 'en':
            retry_msg = "Please share your location or enter your city manually."
        else:
            retry_msg = "Пожалуйста, поделитесь геолокацией или введите город вручную."

        await update.message.reply_text(retry_msg)
        return CITY

    # Only show name prompt if we have city data
    if context.user_data.get("city"):
        keyboard = [[KeyboardButton(get_text(user_id, "back_button"))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            get_text(user_id, "questionnaire_name"),
            reply_markup=reply_markup
        )
        return NAME
    else:
        return CITY

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle name input"""
    user_id = update.effective_user.id
    name_text = update.message.text.strip()

    # Handle back button
    if name_text in ["🔙 Назад", "🔙 Back"]:
        keyboard = [
            [KeyboardButton(get_text(user_id, "share_gps"), request_location=True)],
            [KeyboardButton(get_text(user_id, "manual_entry"))],
            [KeyboardButton(get_text(user_id, "back_button"))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        user = db.get_user(user_id)
        lang = user.lang if user else 'ru'

        if lang == 'en':
            location_text = "📍 Share your location:\n\nYou can either share your GPS location or enter your city manually."
        else:
            location_text = "📍 Поделитесь вашим местоположением:\n\nВы можете поделиться GPS-локацией или ввести город вручную."

        await update.message.reply_text(location_text, reply_markup=reply_markup)
        return CITY

    context.user_data["name"] = name_text

    # Add skip and back buttons for bio
    keyboard = [
        [KeyboardButton(get_text(user_id, "btn_skip"))],
        [KeyboardButton(get_text(user_id, "back_button"))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        get_text(update.effective_user.id, "questionnaire_bio"),
        reply_markup=reply_markup
    )
    return BIO

async def handle_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle bio input"""
    user_id = update.effective_user.id
    bio_text = update.message.text.strip()

    # Handle back button
    if bio_text in ["🔙 Назад", "🔙 Back"]:
        keyboard = [[KeyboardButton(get_text(user_id, "back_button"))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            get_text(user_id, "questionnaire_name"),
            reply_markup=reply_markup
        )
        return NAME

    # Check if user wants to skip
    if bio_text in ["⏭️ Пропустить", "пропустить", "skip", get_text(user_id, "btn_skip"), "⏭️"]:
        context.user_data["bio"] = get_text(user_id, "default_bio_skip")
    else:
        context.user_data["bio"] = bio_text

    # Initialize empty selections
    context.user_data["selected_nd_traits"] = []
    context.user_data["selected_characteristics"] = []

    # Show ND traits selection
    await show_registration_nd_traits(update, context, user_id)
    return WAITING_NAME  # We'll reuse this state for ND selection

async def show_registration_nd_traits(update, context, user_id):
    """Show ND traits selection during registration"""
    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'

    text = get_text(user_id, "nd_selection_prompt") + "\n\n"

    current_traits = context.user_data.get("selected_nd_traits", [])
    text += f"{get_text(user_id, 'nd_selected_count')} {len(current_traits)}/3\n\n"

    if current_traits:
        trait_names = [ND_TRAITS[lang].get(trait, trait) for trait in current_traits if trait in ND_TRAITS[lang] and trait != 'none']
        text += f"✅ {', '.join(trait_names)}\n\n"

    keyboard = []
    traits = ND_TRAITS[lang]

    # Add trait selection buttons
    for trait_key, trait_name in traits.items():
        if trait_key == 'none':
            continue

        # Mark selected traits with checkmark
        marker = "✅ " if trait_key in current_traits else ""
        button_text = f"{marker}{trait_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"reg_trait_{trait_key}")])

    # Always add control buttons at the end
    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_save"), callback_data="reg_traits_done")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_skip_all"), callback_data="reg_traits_skip")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="reg_traits_back")])

    # Remove any existing keyboard first
    await update.message.reply_text(
        get_text(user_id, "selecting_traits"),
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Send the trait selection interface
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo/video input during registration"""
    user_id = update.effective_user.id

    try:
        # Ensure update.message exists
        if not update.message:
            logger.warning("No message in update")
            return PHOTO

        # Handle text messages (Done/Skip/Back buttons)
        if update.message.text:
            text = update.message.text.strip()

            # Handle back button
            if text in ["🔙 Назад", "🔙 Back"]:
                # Go back to bio step
                keyboard = [
                    [KeyboardButton(get_text(user_id, "btn_skip"))],
                    [KeyboardButton(get_text(user_id, "back_button"))]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                
                await update.message.reply_text(
                    get_text(user_id, "questionnaire_bio"),
                    reply_markup=reply_markup
                )
                return BIO

            if text in ["✅ Готово", "✅ Done", get_text(user_id, "btn_done"), "⏭️ Пропустить остальные", "⏭️ Skip remaining", get_text(user_id, "btn_skip_remaining")]:
                # Check if we have at least one photo
                photos = context.user_data.get("photos", [])
                media_id = context.user_data.get("media_id")

                if photos or media_id:
                    await save_user_profile(update, context)
                    return ConversationHandler.END
                else:
                    keyboard = [
                        [KeyboardButton(get_text(user_id, "back_button"))]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                    await update.message.reply_text(
                        get_text(user_id, "photo_required"),
                        reply_markup=reply_markup
                    )
                    return PHOTO
            else:
                # Invalid text - ask for photo again
                keyboard = [
                    [KeyboardButton(get_text(user_id, "back_button"))]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                await update.message.reply_text(
                    get_text(user_id, "media_send_prompt"),
                    reply_markup=reply_markup
                )
                return PHOTO

        # Handle photo uploads
        elif update.message.photo:
            # Initialize photos list if not exists
            if "photos" not in context.user_data:
                context.user_data["photos"] = []

            # Get the largest photo
            photo = update.message.photo[-1]
            photo_id = photo.file_id

            # Add photo to the list (max 3 photos)
            photos_list = context.user_data["photos"]
            if len(photos_list) < 3:
                photos_list.append(photo_id)
                context.user_data["media_type"] = "photo"
                context.user_data["media_id"] = photo_id

                photos_count = len(photos_list)

                if photos_count < 3:
                    # Ask for more photos with localized text
                    keyboard = [
                        [KeyboardButton(get_text(user_id, "btn_done"))],
                        [KeyboardButton(get_text(user_id, "btn_skip_remaining"))],
                        [KeyboardButton(get_text(user_id, "back_button"))]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                    
                    lang = db.get_user(user_id).get('lang', 'ru') if db.get_user(user_id) else 'ru'
                    if lang == 'en':
                        photo_msg = f"✅ Photo {photos_count}/3 added!\n\nSend more photos or press a button:"
                    else:
                        photo_msg = f"✅ Фото {photos_count}/3 добавлено!\n\nОтправьте еще фото или нажмите кнопку:"
                    
                    await update.message.reply_text(photo_msg, reply_markup=reply_markup)
                    return PHOTO
                else:
                    # All 3 photos uploaded, proceed to save
                    await save_user_profile(update, context)
                    return ConversationHandler.END
            else:
                # Already have 3 photos
                keyboard = [
                    [KeyboardButton(get_text(user_id, "btn_done"))],
                    [KeyboardButton(get_text(user_id, "back_button"))]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
                
                lang = db.get_user(user_id).get('lang', 'ru') if db.get_user(user_id) else 'ru'
                max_msg = "⚠️ Maximum 3 photos. Press 'Done' to continue." if lang == 'en' else "⚠️ Максимум 3 фото. Нажмите 'Готово' чтобы продолжить."
                await update.message.reply_text(max_msg, reply_markup=reply_markup)
                return PHOTO

        # Handle video uploads
        elif update.message.video:
            video = update.message.video
            context.user_data["media_type"] = "video"
            context.user_data["media_id"] = video.file_id
            context.user_data["photos"] = []  # Clear photos array when using video
            
            lang = db.get_user(user_id).get('lang', 'ru') if db.get_user(user_id) else 'ru'
            success_msg = "✅ Video added!" if lang == 'en' else "✅ Видео добавлено!"
            await update.message.reply_text(success_msg)
            await save_user_profile(update, context)
            return ConversationHandler.END

        # Handle video note uploads
        elif update.message.video_note:
            video_note = update.message.video_note
            context.user_data["media_type"] = "video_note"
            context.user_data["media_id"] = video_note.file_id
            context.user_data["photos"] = []  # Clear photos array when using video note
            
            lang = db.get_user(user_id).get('lang', 'ru') if db.get_user(user_id) else 'ru'
            success_msg = "✅ Video message added!" if lang == 'en' else "✅ Видео-сообщение добавлено!"
            await update.message.reply_text(success_msg)
            await save_user_profile(update, context)
            return ConversationHandler.END

        # Handle GIF/animation uploads (NEW FEATURE)
        elif update.message.animation:
            animation = update.message.animation
            context.user_data["media_type"] = "animation"
            context.user_data["media_id"] = animation.file_id
            context.user_data["photos"] = []  # Clear photos array when using animation
            
            lang = db.get_user(user_id).get('lang', 'ru') if db.get_user(user_id) else 'ru'
            success_msg = "✅ GIF added!" if lang == 'en' else "✅ GIF добавлен!"
            await update.message.reply_text(success_msg)
            await save_user_profile(update, context)
            return ConversationHandler.END

        else:
            # No valid media received
            keyboard = [
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                get_text(user_id, "media_send_prompt"),
                reply_markup=reply_markup
            )
            return PHOTO

    except Exception as e:
        logger.error(f"Error in handle_photo: {e}")
        try:
            keyboard = [
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(
                get_text(user_id, "media_upload_error"),
                reply_markup=reply_markup
            )
        except Exception as e2:
            logger.error(f"Failed to send error message to user: {e2}")
        return PHOTO

async def save_user_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save user profile to database"""
    user_id = update.effective_user.id
    user_data = context.user_data

    try:
        # Ensure we have at least one photo or video
        photos = user_data.get("photos", [])
        media_id = user_data.get("media_id")

        if not photos and not media_id:
            photo_prompt = get_text(user_id, "questionnaire_photo")
            await update.message.reply_text(f"📸 {photo_prompt}")
            return PHOTO

        # Validate required fields
        required_fields = ["name", "age", "gender", "interest", "city", "bio"]
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                logger.error(f"Missing or empty required field: {field}")
                await update.message.reply_text(get_text(user_id, "profile_missing_field_error").format(field=field))
                return ConversationHandler.END

        # Save to database
        profile_data = {
            "user_id": user_id,
            "username": update.effective_user.username or "",
            "first_name": update.effective_user.first_name or "",
            "name": user_data["name"],
            "age": user_data["age"],
            "gender": user_data["gender"],
            "interest": user_data["interest"],
            "city": user_data["city"],
            "bio": user_data["bio"],
            "photos": photos,
            "photo_id": photos[0] if photos else media_id,  # Keep for backward compatibility
            "media_type": user_data.get("media_type", "photo"),
            "media_id": media_id or (photos[0] if photos else ""),
            "latitude": user_data.get("latitude"),
            "longitude": user_data.get("longitude"),
            "created_at": datetime.now().isoformat(),
            "lang": "ru",
            "nd_traits": user_data.get("selected_nd_traits", []),
            "nd_symptoms": user_data.get("selected_characteristics", []),
            "seeking_traits": [],
            "likes": [],
            "sent_likes": [],
            "received_likes": [],
            "unnotified_likes": [],
            "declined_likes": [],
            "ratings": [],
            "total_rating": 0.0,
            "rating_count": 0
        }

        db.create_or_update_user(user_id, profile_data)
        logger.info(f"Profile saved for user {user_id}")

        photos_saved_count = len(photos) if photos else 1
        photos_saved = f"✅ Сохранено {photos_saved_count} {'фото' if photos else 'видео'}!"

        # Send single message with success and main menu
        await update.message.reply_text(
            f"{photos_saved}\n\n{get_text(user_id, 'profile_saved')}",
            reply_markup=get_main_menu(user_id)
        )

        context.user_data.clear()  # This will also clear the 'in_conversation' flag

    except Exception as e:
        logger.error(f"Error saving user profile: {e}")
        await update.message.reply_text(
            get_text(user_id, "profile_save_error")
        )
        return ConversationHandler.END

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not data:
        return

    try:
        if data == "view_profile":
            await show_user_profile(query, user_id)
        elif data == "browse_profiles":
            await browse_profiles(query, context, user_id)
        elif data == "browse_all_profiles":
            # Clear previous browsing data and start browsing
            context.user_data.pop('browsing_profiles', None)
            context.user_data.pop('current_profile_index', None)
            context.user_data['browse_started'] = True
            await start_browsing_profiles(query, context, user_id)
        elif data == "change_photo":
            await start_change_photo(query, context, user_id)
        elif data == "change_bio":
            await start_change_bio(query, context, user_id)
        elif data == "change_name":
            await start_change_name(query, context, user_id)
        elif data == "change_city":
            await start_change_city(query, context, user_id)
        elif data == "change_city_setting":
            await start_change_city_setting(query, context, user_id)
        elif data == "my_likes":
            await show_my_likes_direct(query, context, user_id)
        elif data == "profile_settings":
            await show_profile_settings_menu(query, user_id)
        elif data == "feedback":
            await show_feedback_menu(query, user_id)
        elif data == "statistics":
            await show_statistics(query, user_id)
        elif data == "back_to_menu":
            await safe_edit_message(
                query,
                get_text(user_id, "main_menu"),
                get_main_menu(user_id)
            )
        elif data.startswith("like_back_"):
            parts = data.split("_", 2)
            if len(parts) < 3:
                await query.answer("❌ Ошибка обработки.")
                return
            try:
                target_id = int(parts[2])
                await handle_like_back(query, context, user_id, target_id)
            except Exception as e:
                logger.error(f"Error parsing like_back callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки.")
                return
        elif data.startswith("like_incoming_"):
            # Handle incoming like callbacks - like someone back
            try:
                profile_id = int(data.split("_")[2])
                await handle_like_back(query, context, user_id, profile_id)
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing like_incoming callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки. Попробуйте еще раз.")
                return
        elif data.startswith("like_"):
            try:
                # Format: like_410177871  
                profile_id = int(data.split("_")[1])
                await handle_like_profile(query, context, user_id, profile_id)
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing like callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки. Попробуйте еще раз.")
                return
        elif data.startswith("pass_incoming_"):
            # Handle incoming pass callbacks first - more specific match
            try:
                profile_id = int(data.split("_")[2])
                await handle_decline_like(query, user_id, profile_id)
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing pass_incoming callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки. Попробуйте еще раз.")
                return
        elif data.startswith("pass_"):
            try:
                # Format: pass_410177871
                await handle_pass_profile(query, context, user_id)
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing pass callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки. Попробуйте еще раз.")
                return
        elif data == "prev_profile":
            await show_previous_profile(query, context, user_id)
        elif data == "next_profile":
            await show_next_profile(query, context, user_id)
        elif data == "no_action":
            await query.answer()  # Just acknowledge the callback, do nothing
        elif data == "continue_browsing":
            # Continue browsing profiles from where we left off
            profiles = context.user_data.get('browsing_profiles', [])
            current_index = context.user_data.get('current_profile_index', 0)
            if profiles and current_index < len(profiles):
                await show_profile_card(query, context, user_id, profiles[current_index])
            else:
                await browse_profiles(query, context, user_id)
        elif data.startswith("send_message_"):
            try:
                target_id = int(data.split("_")[2])
                await start_message_to_user(query, context, user_id, target_id)
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing send_message callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки. Попробуйте еще раз.")
                return
        elif data.startswith("send_video_"):
            target_id = int(data.split("_")[2])
            await start_video_to_user(query, context, user_id, target_id)
        elif data.startswith("view_match_profile_"):
            target_id = int(data.split("_")[3])
            await show_detailed_match_profile(query, user_id, target_id)
        elif data.startswith("view_incoming_profile_"):
            target_id = int(data.split("_")[3])
            await show_incoming_profile(query, user_id, target_id)
        elif data.startswith("like_back_"):
            parts = data.split("_", 2)
            if len(parts) < 3:
                await query.answer("❌ Ошибка обработки.")
                return
            try:
                target_id = int(parts[2])
                await handle_like_back(query, context, user_id, target_id)
            except Exception as e:
                logger.error(f"Error parsing like_back callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки.")
                return
        elif data.startswith("decline_like_"):
            parts = data.split("_", 2)
            if len(parts) < 3:
                await query.answer("❌ Ошибка обработки.")
                return
            try:
                target_id = int(parts[2])
                await handle_decline_like(query, user_id, target_id)
            except Exception as e:
                logger.error(f"Error parsing decline_like callback data '{data}': {e}")
                await query.answer("❌ Ошибка обработки.")
                return


        elif data == "view_mutual_matches":
            await show_mutual_matches(query, context, user_id)
        elif data == "view_incoming_likes":
            await show_incoming_likes_browse(query, context, user_id)
        elif data == "prev_mutual_match":
            await navigate_mutual_matches(query, context, user_id, -1)
        elif data == "next_mutual_match":
            await navigate_mutual_matches(query, context, user_id, 1)
        elif data == "manage_symptoms":
            await show_nd_traits_menu(query, user_id)
        elif data == "manage_symptoms_detailed":
            await show_detailed_symptoms_menu(query, user_id)
        
        elif data == "add_nd_traits":
            await show_add_traits_menu(query, user_id)
        elif data.startswith("toggle_trait_"):
            trait_key = data.split("toggle_trait_")[1]
            await toggle_nd_trait(query, user_id, trait_key)
        elif data.startswith("toggle_symptom_"):
            symptom_key = data.split("toggle_symptom_")[1]
            await toggle_nd_symptom(query, user_id, symptom_key)
        elif data.startswith("reg_trait_"):
            trait_key = data.split("reg_trait_")[1]
            await toggle_registration_trait(query, context, user_id, trait_key)
        elif data.startswith("reg_symptom_"):
            symptom_key = data.split("reg_symptom_")[1]
            await toggle_registration_symptom(query, context, user_id, symptom_key)
        elif data == "reg_traits_done":
            return await show_registration_nd_symptoms(query, context, user_id)
        elif data == "reg_traits_skip":
            return await show_registration_nd_symptoms(query, context, user_id)
        elif data == "reg_symptoms_done":
            return await finish_nd_registration(query, context, user_id)
        elif data == "reg_symptoms_skip":
            return await finish_nd_registration(query, context, user_id)
        elif data == "reg_traits_back":
            # Go back to bio step
            keyboard = [
                [KeyboardButton(get_text(user_id, "btn_skip"))],
                [KeyboardButton(get_text(user_id, "back_button"))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await query.message.reply_text(
                get_text(user_id, "questionnaire_bio"),
                reply_markup=reply_markup
            )
            
            try:
                await query.delete_message()
            except:
                pass
                
            return BIO
        elif data == "reg_symptoms_back":
            # Go back to traits selection
            await show_registration_nd_traits(query, context, user_id)
        elif data == "save_traits":
            try:
                await query.edit_message_text(
                    "✅ Особенности сохранены!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К настройкам", callback_data="manage_symptoms")
                    ]])
                )
            except Exception:
                try:
                    await query.delete_message()
                except:
                    pass
                await query.message.reply_text(
                    "✅ Особенности сохранены!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К настройкам", callback_data="manage_symptoms")
                    ]])
                )
        elif data == "save_symptoms":
            try:
                await query.edit_message_text(
                    "✅ Характеристики сохранены!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К настройкам", callback_data="manage_symptoms")
                    ]])
                )
            except Exception:
                try:
                    await query.delete_message()
                except:
                    pass
                await query.message.reply_text(
                    "✅ Характеристики сохранены!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К настройкам", callback_data="manage_symptoms")
                    ]])
                )
        elif data == "search_by_traits":
            await search_by_traits(query, context, user_id)
        elif data == "next_nd_result":
            await show_next_nd_result(query, context, user_id)
        elif data == "pass_nd_profile":
            await show_next_nd_result(query, context, user_id)
        elif data == "compatibility_search":
            await compatibility_search(query, context, user_id)
        elif data == "recommendations":
            await show_recommendations(query, context, user_id)
        elif data == "next_compatibility":
            await show_next_compatibility_result(query, context, user_id)
        elif data == "prev_compatibility":
            await show_prev_compatibility_result(query, context, user_id)
        elif data == "pass_compatibility":
            await show_next_compatibility_result(query, context, user_id)
        elif data == "next_recommendation":
            await show_next_recommendation_result(query, context, user_id)
        elif data == "pass_recommendation":
            await show_next_recommendation_result(query, context, user_id)
        elif data == "next_incoming_like":
            await show_next_incoming_like(query, context, user_id)
        
        elif data.startswith("interest_"):
            interest = data.split("interest_")[1]
            db.create_or_update_user(user_id, {'interest': interest})
            await query.edit_message_text(
                "✅ Предпочтения обновлены!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К настройкам", callback_data="profile_settings")
                ]])
            )
        elif data == "recreate_profile":
            await confirm_recreate_profile(query, user_id)
        elif data == "confirm_recreate":
            # Start profile recreation
            user = db.get_user(user_id)
            current_lang = user.get('lang', 'ru') if user else 'ru'

            # Keep the language setting but clear all other profile data
            user_lang = user.get('lang', 'ru') if user else 'ru'

            db.create_or_update_user(user_id, {
                'name': '',
                'age': '',
                'gender': '',
                'interest': '',
                'city': '',
                'bio': '',
                'photos': [],
                'photo_id': '',
                'media_type': '',
                'media_id': '',
                'nd_traits': [],
                'nd_symptoms': [],
                'lang': user_lang
            })

            # Clear conversation data
            context.user_data.clear()

            if current_lang == 'en':
                welcome_text = "🔄 Profile Recreation Started!\n\n✨ Let's create your new profile. We'll go through all the steps again.\n\nTo restart the profile creation process, please send /start"
            else:
                welcome_text = "🔄 Начинаем заполнение анкеты заново!\n\n✨ Давайте создадим вашу новую анкету. Мы пройдем все шаги заново.\n\nЧтобы начать создание анкеты, отправьте /start"

            try:
                await query.edit_message_text(welcome_text)
            except:
                await query.message.reply_text(welcome_text)
        elif data == "reset_matches":
            await confirm_reset_matches(query, user_id)
        elif data == "confirm_reset_matches":
            await reset_user_matches(query, user_id)
        elif data == "confirm_delete":
            # Delete user account
            user = db.get_user(user_id)
            user_lang = user.get('lang', 'ru') if user else 'ru'
            
            if user_lang == 'en':
                delete_message = "🗑️ Account deleted.\n\nGoodbye! Use /start if you want to return."
            else:
                delete_message = "🗑️ Аккаунт удален.\n\nДо свидания! Используйте /start если захотите вернуться."
            
            db.delete_user(user_id)
            await query.edit_message_text(delete_message)
        elif data == "feedback_complaint":
            await start_feedback(query, context, user_id, "complaint")
        elif data == "feedback_suggestion":
            await start_feedback(query, context, user_id, "suggestion")
        elif data == "feedback_support":
            await start_feedback(query, context, user_id, "support")
        elif data == "rate_app":
            await show_rating_menu(query, user_id)
        elif data == "change_language":
            await change_language(query, user_id)
        elif data == "change_city_setting":
            await start_change_city_setting(query, context, user_id)
        elif data == "change_interest_setting":
            await start_change_interest_setting(query, context, user_id)
        elif data == "delete_account":
            await confirm_delete_account(query, user_id)
        elif data == "detailed_stats":
            await show_detailed_stats(query, user_id)
        elif data == "continue_profile":
            await continue_profile_creation(query, context, user_id)
        elif data == "browse_anyway":
            context.user_data['browse_started'] = True
            context.user_data['use_filters'] = False
            await start_browsing_profiles(query, context, user_id)
        elif data == "browse_all_unfiltered":
            context.user_data['browse_started'] = True
            context.user_data['use_filters'] = False
            await start_browsing_unfiltered_profiles(query, context, user_id)
        elif data.startswith("lang_"):
            lang = data.split("_")[1]
            db.update_user(user_id, {'lang': lang})
            
            # Check if this is a new user who needs to create a profile
            user = db.get_user(user_id)
            
            if lang == 'ru':
                success_text = "✅ Язык установлен: Русский"
            else:
                success_text = "✅ Language set: English"
            
            await query.edit_message_text(success_text)
            
            # If user has no profile data, start profile creation
            if not is_profile_complete_dict(user):
                await asyncio.sleep(1)  # Brief pause
                welcome_text = get_text(user_id, "welcome")
                age_text = get_text(user_id, "questionnaire_age")
                
                # Start profile creation with proper language in single message
                if lang == 'en':
                    back_btn = "🔙 Back to main menu"
                else:
                    back_btn = "🔙 Назад к главному меню"
                
                keyboard = [[KeyboardButton(back_btn)]]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                
                combined_text = f"{welcome_text}\n\n{age_text}"
                await query.message.reply_text(combined_text, reply_markup=reply_markup)
                
                # Set conversation state properly
                context.user_data.clear()
                context.user_data['in_conversation'] = True
                context.user_data['language_selected'] = True
                # Note: We can't return a state here since this is in a callback handler
            else:
                # User has complete profile, show main menu
                await asyncio.sleep(1)
                await query.message.reply_text(
                    get_text(user_id, "main_menu"),
                    reply_markup=get_main_menu(user_id)
                )
        elif data.startswith("rate_app_"):
            rating = int(data.split("_")[2])
            await save_app_rating(query, user_id, rating)
        else:
            await query.edit_message_text("Функция в разработке")

    except Exception as e:
        logger.error(f"Error in handle_callback: {e}")
        try:
            user = db.get_user(user_id)
            lang = user.get('lang', 'ru') if user else 'ru'
            error_text = "Произошла ошибка. Попробуйте еще раз." if lang == 'ru' else "An error occurred. Please try again."
            await safe_edit_message(
                query,
                error_text,
                get_main_menu(user_id)
            )
        except Exception as e2:
            logger.error(f"Failed to send error message: {e2}")
            try:
                await query.message.reply_text(
                    "Произошла ошибка. Попробуйте еще раз.",
                    reply_markup=get_main_menu(user_id)
                )
            except:
                pass

async def show_user_profile(query, user_id):
    """Show user's own profile"""
    user = db.get_user(user_id)
    if not user:
        await query.edit_message_text(
            get_text(user_id, "profile_not_found"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
            ]])
        )
        return
    
    # Check profile completion with detailed logging
    is_complete = is_profile_complete_dict(user)
    logger.info(f"Profile completion check for user {user_id}: {is_complete}")
    logger.info(f"User data: name={user.get('name')}, age={user.get('age')}, photos={len(user.get('photos', []))}, media_id={bool(user.get('media_id'))}")
    
    if not is_complete:
        # Show incomplete profile with option to continue
        profile_text = "📝 Ваш профиль:\n\n"
        
        name = user.get('name', '').strip()
        if name:
            profile_text += f"👤 Имя: {name}\n"
        else:
            profile_text += "👤 Имя: не указано\n"
            
        age = user.get('age')
        if age:
            profile_text += f"🎂 Возраст: {age} лет\n"
        else:
            profile_text += "🎂 Возраст: не указан\n"
            
        city = user.get('city', '').strip()
        if city:
            profile_text += f"📍 Город: {city}\n"
        else:
            profile_text += "📍 Город: не указан\n"
            
        bio = user.get('bio', '').strip()
        if bio:
            profile_text += f"💭 О себе: {bio}\n"
        else:
            profile_text += "💭 О себе: не указано\n"
            
        photos = user.get('photos', [])
        media_id = user.get('media_id', '').strip()
        if (photos and len(photos) > 0) or media_id:
            profile_text += "📸 Фото: добавлено\n"
        else:
            profile_text += "📸 Фото: не добавлено\n"
            
        profile_text += "\n🚧 Профиль не завершен. Вы можете продолжить заполнение или изменить существующую информацию."
        
        keyboard = [
            [InlineKeyboardButton("📝 Продолжить заполнение", callback_data="continue_profile")],
            [InlineKeyboardButton("📸 Изменить фото", callback_data="change_photo")],
            [InlineKeyboardButton("✍️ Изменить описание", callback_data="change_bio")],
            [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
        ]
        
        await query.edit_message_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Format profile text
    profile_text = f"👤 *{user['name']}*, {user['age']} {get_text(user_id, 'years_old')}\n"
    profile_text += f"📍 *{user['city']}*\n"

    # Add ND traits and symptoms display
    nd_traits = user.get('nd_traits', [])
    nd_symptoms = user.get('nd_symptoms', [])

    if nd_traits or nd_symptoms:
        lang = user.get('lang', 'ru')

        if nd_traits:
            traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 {get_text(user_id, 'nd_traits')}: *{', '.join(trait_names)}*\n"

        if nd_symptoms:
            symptoms_dict = ND_SYMPTOMS.get(lang, ND_SYMPTOMS['ru'])
            symptom_names = [symptoms_dict.get(symptom, symptom) for symptom in nd_symptoms if symptom in symptoms_dict]
            if symptom_names:
                profile_text += f"🔍 {get_text(user_id, 'nd_characteristics_label')}: *{', '.join(symptom_names[:3])}"
                if len(symptom_names) > 3:
                    profile_text += f"{get_text(user_id, 'and_more')}{len(symptom_names) - 3}"
                profile_text += "*\n"

    profile_text += f"💭 {user['bio']}\n"

    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "change_photo"), callback_data="change_photo"),
         InlineKeyboardButton(get_text(user_id, "change_bio"), callback_data="change_bio")],
        [InlineKeyboardButton(get_text(user_id, "change_name"), callback_data="change_name"),
         InlineKeyboardButton(get_text(user_id, "change_city"), callback_data="change_city")],
        [InlineKeyboardButton(get_text(user_id, "my_characteristics"), callback_data="manage_symptoms")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]

    # Send profile with photo if available
    photos = user.get('photos', [])
    if photos:
        try:
            await query.message.reply_photo(
                photo=photos[0],
                caption=profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            await query.delete_message()
        except:
            await query.edit_message_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    else:
        await query.edit_message_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def browse_profiles(query, context, user_id):
    """Browse other user profiles"""
    current_user = db.get_user(user_id)
    if not current_user:
        await safe_edit_message(
            query,
            get_text(user_id, "profile_not_found"),
            InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
            ]])
        )
        return
    
    if not is_profile_complete_dict(current_user):
        await safe_edit_message(
            query,
            "⚠️ Для просмотра анкет других пользователей рекомендуется завершить свой профиль.\n\nВы можете продолжить заполнение профиля или попробовать просматривать анкеты сейчас.",
            InlineKeyboardMarkup([
                [InlineKeyboardButton("📝 Завершить профиль", callback_data="continue_profile")],
                [InlineKeyboardButton("👀 Смотреть анкеты все равно", callback_data="browse_anyway")],
                [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
            ])
        )
        return

    # Always start browsing directly with gender filtering applied
    context.user_data['browse_started'] = True
    await start_browsing_profiles(query, context, user_id)

import math

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def calculate_location_priority(current_user, other_user):
    """Calculate location priority based on GPS coordinates and city names"""
    # First try GPS-based distance if coordinates are available
    current_lat = current_user.get('latitude')
    current_lon = current_user.get('longitude')
    other_lat = other_user.get('latitude')
    other_lon = other_user.get('longitude')
    
    if all([current_lat, current_lon, other_lat, other_lon]):
        distance_km = calculate_distance_km(current_lat, current_lon, other_lat, other_lon)
        
        # GPS-based priority levels with more granular distances
        if distance_km <= 5:   # Same neighborhood
            return 0
        elif distance_km <= 25:  # Same city/metro area
            return 1
        elif distance_km <= 100:  # Same region
            return 2
        elif distance_km <= 500:  # Same country/state
            return 3
        elif distance_km <= 2000:  # Same continent
            return 4
        else:
            return 5  # Different continents
    
    # Fallback to improved city matching if no GPS coordinates
    return calculate_city_proximity(current_user, other_user)

def calculate_city_proximity(current_user, other_user):
    """Calculate proximity based on city names with better normalization"""
    current_city = current_user.get('city', '').strip()
    other_city = other_user.get('city', '').strip()
    
    if not current_city or not other_city:
        return 5  # No location info = lowest priority
    
    # Normalize both cities
    current_normalized = normalize_city(current_city).lower()
    other_normalized = normalize_city(other_city).lower()
    
    # Exact match after normalization
    if current_normalized == other_normalized:
        return 0
    
    # Check for regional proximity using city groupings
    return get_regional_proximity(current_normalized, other_normalized)

def get_regional_proximity(city1, city2):
    """Get regional proximity score based on geographic regions"""
    # Define city regions for better matching
    regions = {
        'poland': ['warsaw', 'kraków', 'gdansk', 'wrocław', 'poznań', 'łódź', 'katowice', 'szczecin'],
        'germany': ['berlin', 'munich', 'hamburg', 'cologne', 'frankfurt', 'stuttgart', 'düsseldorf'],
        'france': ['paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg'],
        'uk': ['london', 'manchester', 'birmingham', 'liverpool', 'leeds', 'glasgow', 'edinburgh'],
        'russia': ['moscow', 'petersburg', 'novosibirsk', 'yekaterinburg', 'kazan', 'nizhny novgorod'],
        'usa_east': ['new york', 'boston', 'philadelphia', 'washington', 'atlanta', 'miami'],
        'usa_west': ['los angeles', 'san francisco', 'seattle', 'portland', 'san diego'],
        'usa_central': ['chicago', 'detroit', 'milwaukee', 'minneapolis', 'cleveland'],
        'netherlands': ['amsterdam', 'rotterdam', 'utrecht', 'eindhoven', 'tilburg'],
        'italy': ['rome', 'milan', 'turin', 'naples', 'palermo', 'genoa'],
        'spain': ['madrid', 'barcelona', 'valencia', 'seville', 'bilbao'],
    }
    
    # Find which regions each city belongs to
    city1_regions = []
    city2_regions = []
    
    for region, cities in regions.items():
        if any(city in city1 for city in cities):
            city1_regions.append(region)
        if any(city in city2 for city in cities):
            city2_regions.append(region)
    
    # Same region = high proximity
    if any(region in city2_regions for region in city1_regions):
        return 1
    
    # Same continent groupings
    european_regions = ['poland', 'germany', 'france', 'uk', 'netherlands', 'italy', 'spain']
    us_regions = ['usa_east', 'usa_west', 'usa_central']
    
    city1_in_europe = any(region in european_regions for region in city1_regions)
    city2_in_europe = any(region in european_regions for region in city2_regions)
    city1_in_us = any(region in us_regions for region in city1_regions)
    city2_in_us = any(region in us_regions for region in city2_regions)
    
    if (city1_in_europe and city2_in_europe) or (city1_in_us and city2_in_us):
        return 2  # Same continent
    
    return 5  # Different continents/regions

async def start_browsing_unfiltered_profiles(query, context, user_id):
    """Start browsing ALL profiles without gender filtering but with smart prioritization"""
    current_user = db.get_user(user_id)
    
    # Get all users except current user
    all_users = db.all()
    logger.info(f"Total users in database: {len(all_users)}")
    
    current_age = current_user.get("age", 18)
    current_city = current_user.get("city", "").lower()
    current_traits = set(current_user.get('nd_traits', []))
    
    # Get already interacted users
    sent_likes = set(current_user.get("sent_likes", []))
    declined_likes = set(current_user.get("declined_likes", []))
    excluded_ids = sent_likes.union(declined_likes)
    excluded_ids.add(user_id)  # Exclude self
    
    # Collect all profiles with comprehensive scoring
    scored_profiles = []
    
    for user in all_users:
        if user['user_id'] in excluded_ids:
            continue
            
        # More lenient profile check - only require basic info for browsing
        has_basic_info = (user.get('name') and user.get('age') and 
                         user.get('city') and (user.get('photos') or user.get('media_id')))
        
        if not has_basic_info:
            continue
            
        potential_age = user.get("age", 18)
        potential_city = user.get("city", "").lower()
        potential_traits = set(user.get('nd_traits', []))
        
        # AGE RESTRICTION: Adults shouldn't see underage profiles
        if current_age >= 18 and potential_age < 18:
            continue
        if current_age < 18 and potential_age >= 18:
            continue
        
        # Calculate comprehensive score for ALL profiles
        score = 0
        
        # 1. LOCATION PROXIMITY (Primary for unfiltered) - GPS-based scoring
        location_priority = calculate_location_priority(current_user, user)
        
        # Convert priority to score (lower priority = higher score)
        location_score_map = {
            0: 100,  # Same neighborhood/city
            1: 85,   # Same metro area
            2: 70,   # Same region  
            3: 50,   # Same country
            4: 30,   # Same continent
            5: 10    # Different continents
        }
        
        location_score = location_score_map.get(location_priority, 5)
        score += location_score
        
        # 2. ND TRAITS COMPATIBILITY
        if current_traits and potential_traits:
            common_traits = current_traits.intersection(potential_traits)
            if common_traits:
                trait_score = len(common_traits) * 20
                score += trait_score
        
        # 3. AGE COMPATIBILITY
        age_diff = abs(current_age - potential_age)
        if age_diff <= 2:
            score += 30
        elif age_diff <= 5:
            score += 20
        elif age_diff <= 10:
            score += 10
        elif age_diff <= 15:
            score += 5
        
        # 4. NEW PROFILE BONUS
        created_at = user.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at)
                days_since = (datetime.now() - created_date).days
                if days_since <= 7:
                    score += 35  # Higher bonus for new profiles
                elif days_since <= 30:
                    score += 15
                elif days_since <= 90:
                    score += 5
            except:
                pass
        
        # 5. RANDOM FACTOR for diversity (small influence)
        import random
        score += random.randint(0, 10)
        
        scored_profiles.append((user, score))

    logger.info(f"Found {len(scored_profiles)} available profiles for user {user_id} (unfiltered)")

    if not scored_profiles:
        user = db.get_user(user_id)
        lang = user.get('lang', 'ru') if user else 'ru'
        
        if lang == 'en':
            no_profiles_text = "😕 No complete profiles available in the database"
            back_btn = "🔙 Back"
        else:
            no_profiles_text = "😕 Нет завершенных анкет в базе данных"
            back_btn = "🔙 Назад"
        
        keyboard = [
            [InlineKeyboardButton(back_btn, callback_data="back_to_menu")]
        ]
        
        await safe_edit_message(
            query,
            no_profiles_text,
            InlineKeyboardMarkup(keyboard)
        )
        return

    # Sort profiles by score (highest first)
    scored_profiles.sort(key=lambda x: x[1], reverse=True)
    
    # Extract just the user objects for browsing
    sorted_profiles = [profile[0] for profile in scored_profiles]
    
    # Log the prioritization results
    same_city = len([p for p in scored_profiles if normalize_city(p[0].get('city', '')).lower() == normalize_city(current_city).lower() and current_city])
    logger.info(f"Unfiltered prioritization: {same_city} same/nearby city profiles, total {len(sorted_profiles)} profiles")

    # Show first profile
    context.user_data['browsing_profiles'] = sorted_profiles
    context.user_data['current_profile_index'] = 0
    await show_profile_card(query, context, user_id, sorted_profiles[0])

async def start_browsing_profiles(query, context, user_id):
    """Start browsing profiles with improved matching logic and graceful fallbacks"""
    current_user = db.get_user(user_id)
    
    # Get all users except current user
    all_users = db.all()
    logger.info(f"Total users in database: {len(all_users)}")
    
    current_age = current_user.get("age", 18)
    current_gender = current_user.get("gender", "")
    current_interest = current_user.get("interest", "both")
    current_city = current_user.get("city", "").lower()
    current_traits = set(current_user.get('nd_traits', []))
    current_lang = current_user.get('lang', 'ru')
    
    # Get already interacted users
    sent_likes = set(current_user.get("sent_likes", []))
    declined_likes = set(current_user.get("declined_likes", []))
    excluded_ids = sent_likes.union(declined_likes)
    excluded_ids.add(user_id)  # Exclude self
    
    # Collect all potential profiles with scoring
    potential_profiles = []
    
    for user in all_users:
        if user['user_id'] in excluded_ids:
            continue
            
        # Check if user has photos/media and basic profile info
        photos = user.get('photos', [])
        if not photos and not user.get('media_id'):
            continue
        if not user.get('name') or not user.get('age') or not user.get('city'):
            continue
            
        potential_age = user.get("age", 18)
        potential_gender = user.get("gender", "")
        potential_city = user.get("city", "").lower()
        potential_traits = set(user.get('nd_traits', []))
        
        # AGE RESTRICTION: Adults shouldn't see underage profiles
        if current_age >= 18 and potential_age < 18:
            continue
        if current_age < 18 and potential_age >= 18:
            continue
        
        # Calculate profile score based on priorities
        score = 0
        reasons = []
        
        # 1. GENDER COMPATIBILITY (Primary priority)
        gender_match = False
        if current_interest in ["both", "Всё равно", "Doesn't matter"]:
            gender_match = True
            score += 100  # High base score for "any gender"
        else:
            # Check gender preference match
            if current_lang == "ru":
                if current_interest == "male" and "парень" in potential_gender.lower():
                    gender_match = True
                    score += 100
                elif current_interest == "female" and "девуш" in potential_gender.lower():
                    gender_match = True
                    score += 100
            else:
                if current_interest == "male" and "guy" in potential_gender.lower():
                    gender_match = True
                    score += 100
                elif current_interest == "female" and "girl" in potential_gender.lower():
                    gender_match = True
                    score += 100
        
        # 2. LOCATION PROXIMITY (Secondary priority)
        location_priority = calculate_location_priority(current_user, user)
        
        # Convert priority to score and add reasons
        if location_priority == 0:
            location_score = 50
            reasons.append("📍 Same area")
        elif location_priority == 1:
            location_score = 35
            reasons.append("📍 Same city/metro")
        elif location_priority == 2:
            location_score = 25
            reasons.append("📍 Same region")
        elif location_priority == 3:
            location_score = 15
            reasons.append("📍 Same country")
        elif location_priority == 4:
            location_score = 10
            reasons.append("📍 Same continent")
        else:
            location_score = 5
        
        score += location_score
        
        # 3. ND TRAITS COMPATIBILITY (Tertiary priority)
        if current_traits and potential_traits:
            common_traits = current_traits.intersection(potential_traits)
            if common_traits:
                trait_score = len(common_traits) * 15
                score += trait_score
                reasons.append("🧠 Similar ND traits")
        
        # 4. AGE COMPATIBILITY (Quaternary priority)
        age_diff = abs(current_age - potential_age)
        if age_diff <= 2:
            score += 20
            reasons.append("🎂 Similar age")
        elif age_diff <= 5:
            score += 10
            reasons.append("🎂 Close age")
        elif age_diff <= 10:
            score += 5
        
        # 5. NEW PROFILE BONUS
        created_at = user.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at)
                days_since = (datetime.now() - created_date).days
                if days_since <= 7:
                    score += 25
                    reasons.append("✨ New profile")
                elif days_since <= 30:
                    score += 10
            except:
                pass
        
        # Add profile with score and metadata
        potential_profiles.append({
            'user': user,
            'score': score,
            'gender_match': gender_match,
            'location_score': location_score,
            'reasons': reasons
        })
    
    # Sort profiles by score (highest first)
    potential_profiles.sort(key=lambda x: x['score'], reverse=True)
    
    # First try: Show profiles that match gender preference
    preferred_gender_matches = [p for p in potential_profiles if p['gender_match']]
    
    if preferred_gender_matches:
        # Found matches in preferred gender
        matches = [p['user'] for p in preferred_gender_matches]
        logger.info(f"Found {len(matches)} profiles matching gender preference for user {user_id}")
        
        context.user_data['browsing_profiles'] = matches
        context.user_data['current_profile_index'] = 0
        await show_profile_card(query, context, user_id, matches[0])
        return
    
    # Second try: If no preferred gender matches, show closest matches regardless of gender
    if potential_profiles:
        # Show all profiles sorted by proximity and other factors
        all_matches = [p['user'] for p in potential_profiles]
        logger.info(f"No preferred gender matches, showing {len(all_matches)} closest profiles for user {user_id}")
        
        context.user_data['browsing_profiles'] = all_matches
        context.user_data['current_profile_index'] = 0
        await show_profile_card(query, context, user_id, all_matches[0])
        return
    
    # Last resort: No profiles at all - show "Show All" option
    logger.info(f"No profiles found for user {user_id}, showing fallback options")
    
    if current_lang == 'en':
        if current_interest not in ["both", "Всё равно", "Doesn't matter"]:
            gender_name = "boys" if current_interest == "male" else "girls"
            no_gender_text = f"😕 No {gender_name} found in your area\n\nWould you like to see all available profiles?"
        else:
            no_gender_text = "😕 No profiles available at the moment\n\nWould you like to see all profiles without filters?"
        view_all_btn = "👀 Show All Profiles"
        settings_btn = "⚙️ Change Settings"
        back_btn = "🔙 Back"
    else:
        if current_interest not in ["both", "Всё равно", "Doesn't matter"]:
            gender_name = "парней" if current_interest == "male" else "девушек"
            no_gender_text = f"😕 Не найдено {gender_name} в вашем регионе\n\nПоказать всех доступных пользователей?"
        else:
            no_gender_text = "😕 Нет доступных анкет в данный момент\n\nПоказать все анкеты без фильтров?"
        view_all_btn = "👀 Показать всех"
        settings_btn = "⚙️ Изменить настройки"
        back_btn = "🔙 Назад"
    
    keyboard = [
        [InlineKeyboardButton(view_all_btn, callback_data="browse_all_unfiltered")],
        [InlineKeyboardButton(settings_btn, callback_data="profile_settings")],
        [InlineKeyboardButton(back_btn, callback_data="back_to_menu")]
    ]
    
    await safe_edit_message(
        query,
        no_gender_text,
        InlineKeyboardMarkup(keyboard)
    )

async def show_filter_options(query, context, user_id):
    """Show filter options for browsing"""
    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'
    current_interest = user.get('interest', 'both')
    
    # Display interest in readable format
    interest_display = {
        'male': 'Парни' if lang == 'ru' else 'Boys',
        'female': 'Девушки' if lang == 'ru' else 'Girls', 
        'both': 'Всё равно' if lang == 'ru' else 'Anyone'
    }.get(current_interest, current_interest)
    
    if lang == 'en':
        text = "🔍 Browse Filters\n\nCurrent settings:\n"
        text += f"Looking for: {interest_display}\n\n"
        text += "Apply interest filter?"
        yes_btn = "✅ Yes, filter by interest"
        no_btn = "🌍 No, show everyone"
        back_btn = "🔙 Back"
    else:
        text = "🔍 Фильтры просмотра\n\nТекущие настройки:\n"
        text += f"Ищете: {interest_display}\n\n"
        text += "Применить фильтр по предпочтениям?"
        yes_btn = "✅ Да, фильтровать по интересам"
        no_btn = "🌍 Нет, показать всех"
        back_btn = "🔙 Назад"

    keyboard = [
        [InlineKeyboardButton(yes_btn, callback_data="apply_interest_filter")],
        [InlineKeyboardButton(no_btn, callback_data="browse_all_profiles")],
        [InlineKeyboardButton(back_btn, callback_data="browse_profiles")]
    ]

    await safe_edit_message(
        query,
        text,
        InlineKeyboardMarkup(keyboard)
    )

async def apply_interest_filter(query, context, user_id):
    """Apply interest-based filtering"""
    context.user_data['browse_started'] = True
    context.user_data['use_filters'] = True
    await start_browsing_profiles(query, context, user_id)

async def send_profile_media(query, profile_text, keyboard, profile):
    """Send profile with appropriate media type (photo, video, GIF)"""
    try:
        media_type = profile.get('media_type', 'photo')
        media_id = profile.get('media_id', '')
        photos = profile.get('photos', [])
        
        # Priority: photos array > single media > fallback to text
        if photos:
            await query.message.reply_photo(
                photo=photos[0],
                caption=profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        elif media_id:
            if media_type == 'video':
                await query.message.reply_video(
                    video=media_id,
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            elif media_type == 'animation':
                await query.message.reply_animation(
                    animation=media_id,
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            elif media_type == 'video_note':
                # Video notes don't support captions, so send separately
                await query.message.reply_video_note(video_note=media_id)
                await query.message.reply_text(
                    profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            else:
                # Default to photo for legacy compatibility
                await query.message.reply_photo(
                    photo=media_id,
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
        else:
            # No media, send text only
            await query.message.reply_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        
        # Clean up the query message
        try:
            await query.delete_message()
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error sending profile media: {e}")
        # Fallback to text only
        try:
            await query.message.reply_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            await query.delete_message()
        except:
            await query.edit_message_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )

async def show_profile_card(query, context, user_id, profile):
    """Show a profile card with navigation matching the desired interface"""
    current_user = db.get_user(user_id)
    
    profile_text = f"👤 *{profile['name']}*, {profile['age']} лет\n"
    
    # Add location with distance/proximity indicator
    city_display = profile['city']
    
    # Try to show GPS-based distance first
    current_lat = current_user.get('latitude')
    current_lon = current_user.get('longitude')
    profile_lat = profile.get('latitude')
    profile_lon = profile.get('longitude')
    
    if all([current_lat, current_lon, profile_lat, profile_lon]):
        distance_km = calculate_distance_km(current_lat, current_lon, profile_lat, profile_lon)
        
        if distance_km < 1:
            profile_text += f"📍 *{city_display}* 🏠 (<1км)\n"
        elif distance_km < 25:
            profile_text += f"📍 *{city_display}* 🏠 ({distance_km:.0f}км)\n"
        elif distance_km < 100:
            profile_text += f"📍 *{city_display}* 🌆 ({distance_km:.0f}км)\n"
        elif distance_km < 500:
            profile_text += f"📍 *{city_display}* 🌍 ({distance_km:.0f}км)\n"
        else:
            profile_text += f"📍 *{city_display}* ✈️ ({distance_km:.0f}км)\n"
    else:
        # Fallback to old priority system
        location_priority = calculate_location_priority(current_user, profile)
        
        if location_priority == 0:
            # Same city - add local indicator
            profile_text += f"📍 *{city_display}* 🏠\n"
        elif location_priority <= 2:
            # Same country/region - add regional indicator  
            profile_text += f"📍 *{city_display}* 🌍\n"
        else:
            # Different country - just show city
            profile_text += f"📍 *{city_display}*\n"

    # Add ND traits display
    nd_traits = profile.get('nd_traits', [])
    if nd_traits:
        lang = current_user.get('lang', 'ru') if current_user else 'ru'
        traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
        trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
        if trait_names:
            profile_text += f"🧠 ND: *{', '.join(trait_names)}*\n"

    profile_text += f"💭 {profile['bio']}\n"

    # Get current index for navigation
    current_index = context.user_data.get('current_profile_index', 0)
    total_profiles = len(context.user_data.get('browsing_profiles', []))

    # Message button row
    message_buttons = [
        InlineKeyboardButton("💌 Сообщение", callback_data=f"send_message_{profile['user_id']}")
    ]

    # Main navigation row: Back, Heart, Next (always show all three)
    nav_buttons = [
        InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="prev_profile" if current_index > 0 else "no_action"),
        InlineKeyboardButton("❤️", callback_data=f"like_{profile['user_id']}"),
        InlineKeyboardButton("Далее ▶️", callback_data="next_profile" if current_index < total_profiles - 1 else "no_action")
    ]

    # Home button row
    bottom_buttons = [
        InlineKeyboardButton("🏠", callback_data="back_to_menu")
    ]

    keyboard = [message_buttons, nav_buttons, bottom_buttons]

    photos = profile.get('photos', [])
    
    # Don't delete previous message - just send new one
    # This way old profiles stay visible in chat history
    
    # Send profile with appropriate media type (using new unified function)
    try:
        await send_profile_media(query, profile_text, keyboard, profile)
    except Exception as e:
        logger.error(f"Error in send_profile_media: {e}")
        # Ultimate fallback - just send text
        await query.message.reply_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def handle_like_profile(query, context, user_id, target_id):
    """Handle liking a profile"""
    try:
        current_user = db.get(Query().user_id == user_id)
        target_user = db.get(Query().user_id == target_id)

        if not current_user or not target_user:
            await safe_edit_message(
                query,
                "❌ Пользователь не найден",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="browse_profiles")
                ]])
            )
            return

        # Use the centralized add_like function
        await add_like(user_id, target_id)

        # Check for match - verify that target user has actually liked current user
        target_sent_likes = target_user.get('sent_likes', [])
        current_received_likes = current_user.get('received_likes', [])
        is_match = user_id in target_sent_likes and target_id in current_received_likes

        if is_match:
            # Send match notification as new message
            await query.message.reply_text(
                "🎉 Взаимный лайк! Посмотрите взаимные лайки в меню.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💌 Мои лайки", callback_data="my_likes")]])
            )
            
            # Send mutual match notification to the other user
            try:
                await send_mutual_match_notification(target_id, context.application, current_user)
            except Exception as notification_error:
                logger.error(f"Failed to send mutual match notification: {notification_error}")
        else:
            try:
                # Send like confirmation as new message
                await query.message.reply_text(
                    "❤️ Лайк отправлен!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("⏭️ Далее", callback_data="next_profile")
                    ]])
                )
                # Send notification to target user
                try:
                    await send_like_notification(target_id, context.application, user_id)
                except Exception as notification_error:
                    logger.error(f"Failed to send like notification: {notification_error}")
                
                # Wait a moment before showing next profile
                await asyncio.sleep(1)
                # Show next profile as new message
                await show_next_profile_as_new_message(query, context, user_id)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Error in handle_like_profile: {e}")
        try:
            await safe_edit_message(
                query,
                "✅ Лайк отправлен!",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton("⏭️ Далее", callback_data="next_profile"),
                    InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")
                ]])
            )
        except Exception as e2:
            logger.error(f"Failed to send fallback message: {e2}")
            try:
                await query.message.reply_text(
                    "✅ Лайк отправлен!",
                    reply_markup=get_main_menu(user_id)
                )
            except Exception as e3:
                logger.error(f"Failed to send reply message: {e3}")

async def handle_pass_profile(query, context, user_id):
    """Handle passing a profile"""
    # Get current profile being viewed
    profiles = context.user_data.get('browsing_profiles', [])
    current_index = context.user_data.get('current_profile_index', 0)
    
    if profiles and current_index < len(profiles):
        current_profile = profiles[current_index]
        target_id = current_profile['user_id']
        
        # Add to declined likes so it won't show again
        user = db.get_user(user_id)
        if user:
            declined_likes = user.get('declined_likes', [])
            if target_id not in declined_likes:
                declined_likes.append(target_id)
                db.create_or_update_user(user_id, {'declined_likes': declined_likes})
    
    # Send pass confirmation as new message
    await query.message.reply_text(get_text(user_id, "profile_passed"))
    # Show next profile as new message
    await show_next_profile_as_new_message(query, context, user_id)

async def show_next_profile(query, context, user_id):
    """Show next profile in browsing (legacy function for compatibility)"""
    await show_next_profile_as_new_message(query, context, user_id)

async def show_next_profile_as_new_message(query, context, user_id):
    """Show next profile as a new message (not editing existing)"""
    profiles = context.user_data.get('browsing_profiles', [])
    current_index = context.user_data.get('current_profile_index', 0)

    if current_index + 1 < len(profiles):
        context.user_data['current_profile_index'] = current_index + 1
        next_profile = profiles[current_index + 1]
        
        # Create a mock query object that won't try to edit the message
        class MockQuery:
            def __init__(self, original_query):
                self.message = original_query.message
                self.from_user = original_query.from_user
                
        mock_query = MockQuery(query)
        await show_profile_card(mock_query, context, user_id, next_profile)
    else:
        user = db.get_user(user_id)
        lang = user.get('lang', 'ru') if user else 'ru'
        
        no_more_text = "Больше нет анкет для просмотра" if lang == 'ru' else "No more profiles to browse"
        menu_text = "🏠 В меню" if lang == 'ru' else "🏠 To Menu"
        
        await query.message.reply_text(
            no_more_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(menu_text, callback_data="back_to_menu")
            ]])
        )

async def show_previous_profile(query, context, user_id):
    """Show previous profile in browsing"""
    profiles = context.user_data.get('browsing_profiles', [])
    current_index = context.user_data.get('current_profile_index', 0)

    if current_index > 0:
        context.user_data['current_profile_index'] = current_index - 1
        prev_profile = profiles[current_index - 1]
        await show_profile_card(query, context, user_id, prev_profile)
    else:
        await query.answer("Это первая анкета")

async def start_change_photo(query, context, user_id):
    """Start photo change process"""
    context.user_data['changing_photo'] = True

    await safe_edit_message(
        query,
        get_text(user_id, "new_photo_prompt"),
        InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Отмена", callback_data="profile_settings")
        ]])
    )

async def start_change_bio(query, context, user_id):
    """Start bio change process"""
    context.user_data['changing_bio'] = True

    await safe_edit_message(
        query,
        get_text(user_id, "new_bio_prompt"),
        InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Отмена", callback_data="profile_settings")
        ]])
    )

async def start_change_name(query, context, user_id):
    """Start name change process"""
    context.user_data['changing_name'] = True

    user = db.get_user(user_id)
    current_lang = user.get('lang', 'ru') if user else 'ru'

    if current_lang == 'en':
        prompt = "👤 Enter your new name:"
        cancel_text = "❌ Cancel"
    else:
        prompt = "👤 Введите ваше новое имя:"
        cancel_text = "❌ Отмена"

    # Try to edit message text, if it fails (because message has photo), send new message
    try:
        await query.edit_message_text(
            prompt,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(cancel_text, callback_data="view_profile")
            ]])
        )
    except Exception:
        # Message has photo/media, delete it and send new text message
        try:
            await query.delete_message()
        except:
            pass
        await query.message.reply_text(
            prompt,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(cancel_text, callback_data="view_profile")
            ]])
        )

async def start_change_city(query, context, user_id):
    """Start city change process"""
    context.user_data['changing_city'] = True

    user = db.get_user(user_id)
    current_lang = user.get('lang', 'ru') if user else 'ru'

    if current_lang == 'en':
        prompt = "📍 Change your city:\n\nYou can share your GPS location or enter city manually:"
        gps_btn = "📍 Share GPS Location"
        manual_btn = "✍️ Enter Manually"
        cancel_text = "❌ Cancel"
    else:
        prompt = "📍 Изменить город:\n\nВы можете поделиться GPS-локацией или ввести город вручную:"
        gps_btn = "📍 Поделиться GPS"
        manual_btn = "✍️ Ввести вручную"
        cancel_text = "❌ Отмена"

    # Try to edit message text, if it fails (because message has photo), send new message
    try:
        await query.delete_message()
    except:
        pass
    
    # Send message with location request keyboard
    keyboard = [
        [KeyboardButton(gps_btn, request_location=True)],
        [KeyboardButton(manual_btn)],
        [KeyboardButton(cancel_text)]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await query.message.reply_text(prompt, reply_markup=reply_markup)

# Placeholder functions for unimplemented features
async def show_my_likes_direct(query, context, user_id):
    """Show likes management - incoming likes and mutual matches"""
    user = db.get_user(user_id)
    if not user:
        return

    received_likes = user.get('received_likes', [])
    sent_likes = user.get('sent_likes', [])
    declined_likes = user.get('declined_likes', [])

    logger.info(f"Debug my_likes for user {user_id}: received={len(received_likes)}, sent={len(sent_likes)}, declined={len(declined_likes)}")

    # Find mutual matches (people who liked each other)
    mutual_matches = []
    for like_id in received_likes:
        if like_id in sent_likes and like_id not in declined_likes:
            matched_user = db.get_user(like_id)
            if matched_user and is_profile_complete_dict(matched_user):
                mutual_matches.append(matched_user)
                logger.info(f"Found mutual match with user {like_id}: {matched_user.get('name', 'Unknown')}")

    # Find incoming likes (not yet responded to) - exclude declined and already matched
    incoming_likes = []
    for like_id in received_likes:
        if like_id not in sent_likes and like_id not in declined_likes:
            liked_user = db.get_user(like_id)
            if liked_user and is_profile_complete_dict(liked_user):
                incoming_likes.append(liked_user)
                logger.info(f"Found incoming like from user {like_id}: {liked_user.get('name', 'Unknown')}")

    logger.info(f"Total mutual matches found: {len(mutual_matches)}")
    logger.info(f"Total incoming likes found: {len(incoming_likes)}")

    # Show options menu
    if mutual_matches or incoming_likes:
        buttons = []
        if mutual_matches:
            buttons.append([InlineKeyboardButton(f"💝 Взаимные лайки ({len(mutual_matches)})", callback_data="view_mutual_matches")])
        if incoming_likes:
            buttons.append([InlineKeyboardButton(f"💌 Входящие лайки ({len(incoming_likes)})", callback_data="view_incoming_likes")])
        buttons.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")])

        await safe_edit_message(
            query,
            "💕 Ваши лайки:\n\nВыберите что хотите посмотреть:",
            InlineKeyboardMarkup(buttons)
        )
        
        # Store data for viewing
        context.user_data['mutual_matches'] = mutual_matches
        context.user_data['browsing_incoming_likes'] = incoming_likes
    else:
        await safe_edit_message(
            query,
            "Пока нет новых лайков.",
            InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
            ]])
        )

async def show_mutual_matches(query, context, user_id):
    """Show mutual matches as browsable profiles"""
    mutual_matches = context.user_data.get('mutual_matches', [])
    if not mutual_matches:
        await safe_edit_message(
            query,
            "Нет взаимных лайков.",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")
            ]])
        )
        return
    
    # Set up browsing for mutual matches
    context.user_data['browsing_mutual_matches'] = mutual_matches
    context.user_data['current_mutual_index'] = 0
    
    # Show first mutual match
    await show_mutual_match_card(query, context, user_id, mutual_matches[0])

async def show_mutual_match_card(query, context, user_id, profile):
    """Show mutual match profile with contact info"""
    try:
        profile_name = profile.get('name', 'Пользователь')
        profile_username = profile.get('username', '')
        
        # Create hyperlinked name if username exists
        if profile_username:
            profile_text = f"💝 Взаимный лайк!\n\n👤 [{profile_name}](https://t.me/{profile_username}), {profile.get('age', '?')} лет\n"
        else:
            profile_text = f"💝 Взаимный лайк!\n\n👤 *{profile_name}*, {profile.get('age', '?')} лет\n"
        
        profile_text += f"📍 *{profile.get('city', 'Неизвестно')}*\n"
        
        # Add ND traits
        nd_traits = profile.get('nd_traits', [])
        if nd_traits:
            traits_dict = ND_TRAITS.get('ru', ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 {get_text(user_id, 'nd_traits')}: *{', '.join(trait_names)}*\n"
        
        profile_text += f"\n💭 {profile.get('bio', '')}\n"
        profile_text += f"\n✨ Свяжитесь друг с другом напрямую в Telegram!"

        # Navigation buttons
        current_index = context.user_data.get('current_mutual_index', 0)
        total_matches = len(context.user_data.get('browsing_mutual_matches', []))
        
        keyboard = []
        nav_row = []
        if current_index > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Пред", callback_data="prev_mutual_match"))
        if current_index < total_matches - 1:
            nav_row.append(InlineKeyboardButton("След ➡️", callback_data="next_mutual_match"))
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")])

        # Send with photo if available
        photos = profile.get('photos', [])
        if photos:
            try:
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                await query.delete_message()
            except Exception:
                await safe_edit_message(query, profile_text, InlineKeyboardMarkup(keyboard))
        else:
            await safe_edit_message(query, profile_text, InlineKeyboardMarkup(keyboard))
            
    except Exception as e:
        logger.error(f"Error showing mutual match card: {e}")

async def navigate_mutual_matches(query, context, user_id, direction):
    """Navigate through mutual matches"""
    try:
        mutual_matches = context.user_data.get('browsing_mutual_matches', [])
        current_index = context.user_data.get('current_mutual_index', 0)
        
        new_index = current_index + direction
        if 0 <= new_index < len(mutual_matches):
            context.user_data['current_mutual_index'] = new_index
            await show_mutual_match_card(query, context, user_id, mutual_matches[new_index])
    except Exception as e:
        logger.error(f"Error navigating mutual matches: {e}")

async def show_incoming_likes_browse(query, context, user_id):
    """Show incoming likes as browsable profiles"""
    incoming_likes = context.user_data.get('browsing_incoming_likes', [])
    if not incoming_likes:
        await safe_edit_message(
            query,
            "Нет входящих лайков.",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")
            ]])
        )
        return
    
    # Set up browsing context for incoming likes
    context.user_data['current_incoming_index'] = 0
    
    # Show first incoming like profile
    await show_incoming_like_card(query, context, user_id, incoming_likes[0])

async def show_incoming_like_card(query, context, user_id, profile):
    """Show incoming like profile card with like/pass buttons"""
    try:
        current_user = db.get_user(user_id)
        
        profile_text = f"💕 Вам нравится!\n\n"
        profile_text += f"👤 *{profile['name']}*, {profile['age']} лет\n"
        
        # Add location with distance/proximity indicator if available
        city_display = profile['city']
        
        # Try to show GPS-based distance first
        current_lat = current_user.get('latitude')
        current_lon = current_user.get('longitude')
        profile_lat = profile.get('latitude')
        profile_lon = profile.get('longitude')
        
        if all([current_lat, current_lon, profile_lat, profile_lon]):
            distance_km = calculate_distance_km(current_lat, current_lon, profile_lat, profile_lon)
            
            if distance_km < 1:
                profile_text += f"📍 *{city_display}* 🏠 (<1км)\n"
            elif distance_km < 25:
                profile_text += f"📍 *{city_display}* 🏠 ({distance_km:.0f}км)\n"
            elif distance_km < 100:
                profile_text += f"📍 *{city_display}* 🌆 ({distance_km:.0f}км)\n"
            elif distance_km < 500:
                profile_text += f"📍 *{city_display}* 🌍 ({distance_km:.0f}км)\n"
            else:
                profile_text += f"📍 *{city_display}* ✈️ ({distance_km:.0f}км)\n"
        else:
            # Fallback to old priority system
            location_priority = calculate_location_priority(current_user, profile)
            
            if location_priority == 0:
                profile_text += f"📍 *{city_display}* 🏠\n"
            elif location_priority <= 2:
                profile_text += f"📍 *{city_display}* 🌍\n"
            else:
                profile_text += f"📍 *{city_display}*\n"

        # Add ND traits display
        nd_traits = profile.get('nd_traits', [])
        if nd_traits:
            lang = current_user.get('lang', 'ru') if current_user else 'ru'
            traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 ND: *{', '.join(trait_names)}*\n"

        profile_text += f"\n💭 {profile['bio']}"

        # Get current index for navigation
        current_index = context.user_data.get('current_incoming_index', 0)
        total_profiles = len(context.user_data.get('browsing_incoming_likes', []))

        # Create buttons - same as normal browsing but for incoming likes
        keyboard = [
            [
                InlineKeyboardButton("❤️", callback_data=f"like_incoming_{profile['user_id']}"),
                InlineKeyboardButton("👎", callback_data=f"pass_incoming_{profile['user_id']}")
            ],
            [InlineKeyboardButton("🏠", callback_data="back_to_menu")]
        ]

        logger.info(f"Showing incoming like card for profile {profile['user_id']} to user {user_id}")

        # Always delete previous message first to prevent duplicates
        try:
            await query.delete_message()
        except:
            pass
        
        photos = profile.get('photos', [])
        if photos:
            try:
                # Send new photo message
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                logger.info(f"Successfully sent incoming like photo for user {profile['user_id']}")
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                # Fallback to text only
                await query.message.reply_text(
                    profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
        else:
            # No photos - send as text message
            await query.message.reply_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            logger.info(f"Successfully sent incoming like text for user {profile['user_id']}")
            
    except Exception as e:
        logger.error(f"Error in show_incoming_like_card: {e}")
        try:
            await query.message.reply_text(
                "❌ Ошибка при загрузке профиля",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
                ]])
            )
        except:
            pass

async def show_profile_settings_menu(query, user_id):
    """Show profile settings menu"""
    user = db.get_user(user_id)
    current_lang = user.get('lang', 'ru') if user else 'ru'
    current_city = user.get('city', 'Не указан') if user else 'Не указан'

    if current_lang == 'en':
        text = "⚙️ Profile Settings\n\n"
        text += "Here you can change your profile information:"
        lang_display = "Current language: English"
        city_display = f"Current city: {current_city}"
    else:
        text = "⚙️ Настройки профиля\n\n"
        text += "Здесь вы можете изменить информацию о себе:"
        lang_display = "Текущий язык: Русский"
        city_display = f"Текущий город: {current_city}"

    text += f"\n\n🌐 {lang_display}"
    text += f"\n📍 {city_display}"

    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "change_photo"), callback_data="change_photo")],
        [InlineKeyboardButton(get_text(user_id, "change_bio"), callback_data="change_bio")],
        [InlineKeyboardButton(get_text(user_id, "change_city"), callback_data="change_city")],
        [InlineKeyboardButton(get_text(user_id, "my_characteristics"), callback_data="manage_symptoms")],
        [InlineKeyboardButton(get_text(user_id, "reset_matches"), callback_data="reset_matches")],
        [InlineKeyboardButton(get_text(user_id, "recreate_profile"), callback_data="recreate_profile")],
        [InlineKeyboardButton(get_text(user_id, "delete_account"), callback_data="delete_account")],
        [InlineKeyboardButton(get_text(user_id, "change_language_btn"), callback_data="change_language")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]

    await safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))

async def show_settings_menu(query, user_id):
    """Show settings menu"""
    user = db.get_user(user_id)
    if not user:
        return

    current_lang = user.get('lang', 'ru')
    current_city = user.get('city', 'Не указан')
    current_interest = user.get('interest', 'both')

    interest_text = {
        'male': 'Парни',
        'female': 'Девушки', 
        'both': 'Всё равно'
    }.get(current_interest, 'Всё равно')

    text = f"⚙️ Настройки\n\n"
    text += f"🌐 Язык: {'Русский' if current_lang == 'ru' else 'English'}\n"
    text += f"📍 Город: {current_city}\n"
    text += f"💕 Интересуют: {interest_text}\n"

    keyboard = [
        [InlineKeyboardButton("🌐 Сменить язык", callback_data="change_language")],
        [InlineKeyboardButton("📍 Сменить город", callback_data="change_city_setting")],
        [InlineKeyboardButton("💕 Изменить предпочтения", callback_data="change_interest_setting")],
        [InlineKeyboardButton("🗑️ Удалить аккаунт", callback_data="delete_account")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_feedback_menu(query, user_id):
    """Show feedback menu"""
    text = "📝 Обратная связь\n\n"
    text += "Помогите нам улучшить Alt3r! Выберите тип обратной связи:"

    keyboard = [
        [InlineKeyboardButton("🚨 Жалоба", callback_data="feedback_complaint")],
        [InlineKeyboardButton("💡 Предложение", callback_data="feedback_suggestion")],
        [InlineKeyboardButton("🆘 Техническая поддержка", callback_data="feedback_support")],
        [InlineKeyboardButton("⭐ Оценить приложение", callback_data="rate_app")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_statistics(query, user_id):
    """Show user statistics"""
    user = db.get_user(user_id)
    if not user:
        return

    lang = user.get('lang', 'ru')

    # Get user stats
    sent_likes = len(user.get('sent_likes', []))
    received_likes = len(user.get('received_likes', []))

    # Calculate matches
    user_sent = set(user.get('sent_likes', []))
    user_received = set(user.get('received_likes', []))
    matches = len(user_sent.intersection(user_received))

    # Get user rating
    rating_info = get_user_rating(user_id)
    user_rating = rating_info['rating']
    rating_count = rating_info['count']

    # Get registration date
    created_at = user.get('created_at', '')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at).strftime("%d.%m.%Y")
        except:
            created_date = "Unknown" if lang == 'en' else "Неизвестно"
    else:
        created_date = "Unknown" if lang == 'en' else "Неизвестно"

    # Calculate profile completion
    completion_items = []
    if user.get('name'): completion_items.append('Name' if lang == 'en' else 'Имя')
    if user.get('bio'): completion_items.append('Bio' if lang == 'en' else 'Описание')
    if user.get('photos') or user.get('media_id'): completion_items.append('Photo' if lang == 'en' else 'Фото')
    if user.get('city'): completion_items.append('City' if lang == 'en' else 'Город')
    if user.get('nd_traits'): completion_items.append('ND traits' if lang == 'en' else 'Нейроотличия')

    completion_percent = int((len(completion_items) / 5) * 100)

    text = f"📊 {get_text(user_id, 'statistics_title')}\n\n"
    text += f"📅 {get_text(user_id, 'registration_date')} {created_date}\n"
    text += f"✅ {get_text(user_id, 'profile_completion')} {completion_percent}%\n\n"

    text += f"💕 {get_text(user_id, 'activity_section')}\n"
    text += f"• {get_text(user_id, 'likes_sent')} {sent_likes}\n"
    text += f"• {get_text(user_id, 'likes_received')} {received_likes}\n"
    text += f"• {get_text(user_id, 'mutual_likes')} {matches}\n\n"

    

    detailed_btn_text = get_text(user_id, 'detailed_stats')
    back_btn_text = get_text(user_id, 'back_button')

    keyboard = [
        [InlineKeyboardButton(detailed_btn_text, callback_data="detailed_stats")],
        [InlineKeyboardButton(back_btn_text, callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def force_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force access to main menu regardless of profile completion"""
    user_id = update.effective_user.id
    
    # Clear any conversation state
    context.user_data.clear()
    
    # Show main menu directly without intermediate message
    await update.message.reply_text(
        get_text(user_id, "main_menu"),
        reply_markup=get_main_menu(user_id)
    )
    
    return ConversationHandler.END

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages"""
    if not update.effective_user:
        logger.warning("No effective user in update")
        return

    user_id = update.effective_user.id

    # Check if we're in an active conversation state - if so, don't interfere
    if context.user_data.get('in_conversation'):
        return
    
    # If we have conversation data (age, gender, etc.), we're likely in profile creation
    if any(key in context.user_data for key in ['age', 'gender', 'interest', 'city', 'name', 'bio']):
        return

    # Handle menu choice for existing users with incomplete profiles
    if update.message.text in ["🏠 Главное меню", "🏠 Main Menu"]:
        return await force_main_menu(update, context)
    
    if update.message.text in ["📝 Завершить анкету", "📝 Complete Profile"]:
        # Restart profile creation
        welcome_text = get_text(user_id, "welcome")
        age_text = get_text(user_id, "questionnaire_age")

        await update.message.reply_text(welcome_text)
        
        keyboard = [[KeyboardButton(get_text(user_id, "back_to_main_menu"))]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(age_text, reply_markup=reply_markup)
        return AGE

    # Handle photo changes
    if context.user_data.get('changing_photo') and update.message.photo:
        photo = update.message.photo[-1]
        photo_id = photo.file_id

        # Update user's photo
        db.update({
            'photos': [photo_id],
            'photo_id': photo_id,
            'media_id': photo_id,
            'media_type': 'photo'
        }, Query().user_id == user_id)

        context.user_data.pop('changing_photo', None)
        await update.message.reply_text(
            get_text(user_id, "photo_updated"),
            reply_markup=get_main_menu(user_id)
        )
        return

    # Handle name changes
    if context.user_data.get('changing_name') and update.message.text:
        new_name = update.message.text.strip()
        db.update({'name': new_name}, Query().user_id == user_id)

        context.user_data.pop('changing_name', None)

        user = db.get(Query().user_id == user_id)
        current_lang = user.get('lang', 'ru') if user else 'ru'

        if current_lang == 'en':
            success_message = f"✅ Name updated to: {new_name}"
        else:
            success_message = f"✅ Имя изменено на: {new_name}"

        await update.message.reply_text(
            success_message,
            reply_markup=get_main_menu(user_id)
        )
        return

    # Handle bio changes
    if context.user_data.get('changing_bio') and update.message.text:
        new_bio = update.message.text.strip()
        db.update({'bio': new_bio}, Query().user_id == user_id)

        context.user_data.pop('changing_bio', None)
        await update.message.reply_text(
            get_text(user_id, "bio_updated"),
            reply_markup=get_main_menu(user_id)
        )
        return

    # Handle city changes
    if context.user_data.get('changing_city'):
        user = db.get(Query().user_id == user_id)
        current_lang = user.get('lang', 'ru') if user else 'ru'
        
        # Handle GPS location for city change
        if update.message.location:
            try:
                latitude = update.message.location.latitude
                longitude = update.message.location.longitude

                # Show loading message
                if current_lang == 'en':
                    loading_msg = "📍 Detecting your city from GPS coordinates..."
                else:
                    loading_msg = "📍 Определяем ваш город по GPS координатам..."
                
                loading_message = await update.message.reply_text(loading_msg, reply_markup=ReplyKeyboardRemove())

                # Get city name from coordinates
                new_city = await get_city_from_coordinates(latitude, longitude)
                
                # Delete loading message
                try:
                    await loading_message.delete()
                except:
                    pass
                
                if new_city and new_city != "Unknown Location":
                    # Update city in database
                    db.update({'city': new_city, 'latitude': latitude, 'longitude': longitude}, Query().user_id == user_id)
                    context.user_data.pop('changing_city', None)

                    if current_lang == 'en':
                        success_message = f"✅ City updated to: {new_city}"
                    else:
                        success_message = f"✅ Город изменен на: {new_city}"

                    await update.message.reply_text(
                        success_message,
                        reply_markup=get_main_menu(user_id)
                    )
                    return
                else:
                    # GPS failed
                    if current_lang == 'en':
                        error_msg = "❌ Couldn't determine your city from GPS. Please enter your city manually:"
                    else:
                        error_msg = get_text(user_id, "gps_error")
                    
                    keyboard = [
                        [KeyboardButton("📍 Попробовать еще раз" if current_lang == 'ru' else "📍 Try GPS again", request_location=True)],
                        [KeyboardButton("❌ Отмена" if current_lang == 'ru' else "❌ Cancel")]
                    ]
                    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                    await update.message.reply_text(error_msg, reply_markup=reply_markup)
                    return

            except Exception as e:
                logger.error(f"Error processing GPS for city change: {e}")
                if current_lang == 'en':
                    error_msg = "❌ Error processing GPS location. Please enter your city manually:"
                else:
                    error_msg = "❌ Ошибка обработки GPS. Пожалуйста, введите город вручную:"
                
                keyboard = [
                    [KeyboardButton("📍 Попробовать еще раз" if current_lang == 'ru' else "📍 Try GPS again", request_location=True)],
                    [KeyboardButton("❌ Отмена" if current_lang == 'ru' else "❌ Cancel")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                await update.message.reply_text(error_msg, reply_markup=reply_markup)
                return
        
        # Handle manual city input or button presses
        elif update.message.text:
            text = update.message.text.strip()
            
            # Handle cancel button
            if text in ["❌ Отмена", "❌ Cancel"]:
                context.user_data.pop('changing_city', None)
                await update.message.reply_text(
                    get_text(user_id, "main_menu"),
                    reply_markup=get_main_menu(user_id)
                )
                return
            
            # Handle manual input button
            elif text in ["✍️ Ввести вручную", "✍️ Enter Manually"]:
                if current_lang == 'en':
                    prompt = "📝 Please enter your new city:"
                else:
                    prompt = "📝 Пожалуйста, введите ваш новый город:"
                
                keyboard = [
                    [KeyboardButton("📍 Использовать GPS" if current_lang == 'ru' else "📍 Use GPS", request_location=True)],
                    [KeyboardButton("❌ Отмена" if current_lang == 'ru' else "❌ Cancel")]
                ]
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                await update.message.reply_text(prompt, reply_markup=reply_markup)
                return
            
            # Handle actual city name input
            elif text not in ["📍 Поделиться GPS", "📍 Share GPS Location", "📍 Попробовать еще раз", "📍 Try GPS again", "📍 Использовать GPS", "📍 Use GPS"]:
                new_city = normalize_city(text)
                db.update({'city': new_city}, Query().user_id == user_id)
                context.user_data.pop('changing_city', None)

                if current_lang == 'en':
                    success_message = f"✅ City updated to: {new_city}"
                else:
                    success_message = f"✅ Город изменен на: {new_city}"

                await update.message.reply_text(
                    success_message,
                    reply_markup=get_main_menu(user_id)
                )
                return

    # Handle direct message sending (text)
    if context.user_data.get('sending_message') and update.message.text:
        target_id = context.user_data.get('message_target_id')
        message_text = update.message.text.strip()

        if target_id:
            try:
                sender = db.get_user(user_id)
                target_user = db.get_user(target_id)
                
                if not sender or not target_user:
                    await update.message.reply_text("❌ Ошибка: пользователь не найден")
                    context.user_data.pop('sending_message', None)
                    context.user_data.pop('message_target_id', None)
                    return

                sender_name = sender.get('name', 'Неизвестный')

                # Automatically like the target user's profile
                await add_like(user_id, target_id)
                
                # Check if it's a mutual like
                target_sent_likes = target_user.get('sent_likes', [])
                is_match = user_id in target_sent_likes

                # Send message with sender's profile to target user
                await send_message_with_profile(context.bot, target_id, sender, message_text, is_match)

                # Send confirmation to sender
                if is_match:
                    await update.message.reply_text(
                        f"✅ Сообщение отправлено!\n🎉 Взаимный лайк с {target_user.get('name', 'пользователем')}!",
                        reply_markup=get_main_menu(user_id)
                    )
                    
                    # Send mutual match notification to target
                    try:
                        await send_mutual_match_notification(target_id, context.application, sender)
                    except Exception as notification_error:
                        logger.error(f"Failed to send mutual match notification: {notification_error}")
                else:
                    await update.message.reply_text(
                        "✅ Лайк и сообщение отправлены!",
                        reply_markup=get_main_menu(user_id)
                    )

            except Exception as e:
                logger.error(f"Error sending message with like: {e}")
                await update.message.reply_text(
                    "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 К анкетам", callback_data="browse_profiles")
                    ]])
                )

        context.user_data.pop('sending_message', None)
        context.user_data.pop('message_target_id', None)
        return

    # Handle direct message sending (video note)
    if context.user_data.get('sending_message') and update.message.video_note:
        target_id = context.user_data.get('message_target_id')
        video_note = update.message.video_note

        if target_id:
            try:
                sender = db.get_user(user_id)
                target_user = db.get_user(target_id)
                
                if not sender or not target_user:
                    await update.message.reply_text("❌ Ошибка: пользователь не найден")
                    context.user_data.pop('sending_message', None)
                    context.user_data.pop('message_target_id', None)
                    return

                sender_name = sender.get('name', 'Неизвестный')

                # Automatically like the target user's profile
                await add_like(user_id, target_id)
                
                # Check if it's a mutual like
                target_sent_likes = target_user.get('sent_likes', [])
                is_match = user_id in target_sent_likes

                # Send video message with sender info
                await context.bot.send_message(
                    chat_id=target_id,
                    text=f"🎥 Видео-сообщение от {sender_name}:"
                )

                await context.bot.send_video_note(
                    chat_id=target_id,
                    video_note=video_note.file_id
                )

                # Send like-back interface if not mutual
                if not is_match:
                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("❤️ Лайк назад", callback_data=f"like_back_{user_id}")],
                        [InlineKeyboardButton("👎 Пропустить", callback_data=f"decline_like_{user_id}")]
                    ])
                    
                    profile_text = f"👤 {sender_name}, {sender.get('age', '?')} лет\n"
                    profile_text += f"📍 {sender.get('city', 'Неизвестно')}"
                    
                    await context.bot.send_message(
                        chat_id=target_id,
                        text=profile_text,
                        reply_markup=keyboard
                    )

                # Send confirmation
                if is_match:
                    await update.message.reply_text(
                        f"✅ Видео отправлено!\n🎉 Взаимный лайк с {target_user.get('name', 'пользователем')}!",
                        reply_markup=get_main_menu(user_id)
                    )
                    
                    # Send mutual match notification
                    try:
                        await send_mutual_match_notification(target_id, context.application, sender)
                    except Exception as notification_error:
                        logger.error(f"Failed to send mutual match notification: {notification_error}")
                else:
                    await update.message.reply_text(
                        "✅ Лайк и видео-сообщение отправлены!",
                        reply_markup=get_main_menu(user_id)
                    )

            except Exception as e:
                logger.error(f"Error sending video with like: {e}")
                await update.message.reply_text(
                    "❌ Не удалось отправить видео. Возможно, пользователь заблокировал бота.",
                    reply_markup=get_main_menu(user_id)
                )

        context.user_data.pop('sending_message', None)
        context.user_data.pop('message_target_id', None)
        return

    # Handle video message sending
    if context.user_data.get('sending_video'):
        if update.message.video_note:
            target_id = context.user_data.get('video_target_id')
            video_note = update.message.video_note

            if target_id:
                try:
                    # Send video note to target user
                    sender = db.get_user(user_id)
                    sender_name = sender.get('name', 'Неизвестный') if sender else 'Неизвестный'

                    await context.bot.send_message(
                        chat_id=target_id,
                        text=f"🎥 Видео-сообщение от {sender_name}:"
                    )

                    await context.bot.send_video_note(
                        chat_id=target_id,
                        video_note=video_note.file_id
                    )

                    await update.message.reply_text(
                        "✅ Видео-сообщение отправлено!",
                        reply_markup=get_main_menu(user_id)
                    )
                except Exception as e:
                    await update.message.reply_text(
                        "❌ Не удалось отправить видео. Возможно, пользователь заблокировал бота.",
                        reply_markup=get_main_menu(user_id)
                    )

            context.user_data.pop('sending_video', None)
            context.user_data.pop('video_target_id', None)
            return
        elif update.message.text:
            # If they send text while in video mode, treat it as a regular message
            target_id = context.user_data.get('video_target_id')
            message_text = update.message.text.strip()

            if target_id and message_text not in ["❌ Отмена", "❌ Cancel"]:
                try:
                    sender = db.get_user(user_id)
                    sender_name = sender.get('name', 'Неизвестный') if sender else 'Неизвестный'

                    await context.bot.send_message(
                        chat_id=target_id,
                        text=f"💌 Сообщение от {sender_name}:\n\n{message_text}"
                    )

                    await update.message.reply_text(
                        "✅ Сообщение отправлено!",
                        reply_markup=get_main_menu(user_id)
                    )
                except Exception as e:
                    await update.message.reply_text(
                        "❌ Не удалось отправить сообщение. Возможно, пользователь заблокировал бота.",
                        reply_markup=get_main_menu(user_id)
                    )

                context.user_data.pop('sending_video', None)
                context.user_data.pop('video_target_id', None)
                return

    # Handle feedback submission
    if context.user_data.get('waiting_feedback') and update.message.text:
        feedback_type = context.user_data.get('feedback_type', 'general')
        feedback_text = update.message.text.strip()

        # Save feedback to database
        feedback_data = {
            'user_id': user_id,
            'username': update.effective_user.username or '',
            'first_name': update.effective_user.first_name or '',
            'type': feedback_type,
            'text': feedback_text,
            'timestamp': datetime.now().isoformat()
        }

        feedback_db.insert(feedback_data)

        context.user_data.pop('waiting_feedback', None)
        context.user_data.pop('feedback_type', None)

        await update.message.reply_text(
            "✅ Спасибо за обратную связь! Мы обязательно рассмотрим ваше сообщение.",
            reply_markup=get_main_menu(user_id)
        )
        return

    # Handle city change from settings
    if context.user_data.get('changing_city_setting') and update.message.text:
        new_city = normalize_city(update.message.text.strip())
        db.create_or_update_user(user_id, {'city': new_city})

        context.user_data.pop('changing_city_setting', None)
        await update.message.reply_text(
            f"✅ Город изменен на: {new_city}",
            reply_markup=get_main_menu(user_id)
        )
        return

    # Check if user has profile
    user = db.get_user(user_id)
    if not user:
        await update.message.reply_text(
            "👋 Привет! Отправьте /start чтобы начать знакомство!"
        )
        return

    # Always show main menu for existing users, regardless of profile completion
    # Remove any reply keyboard and show main menu
    await update.message.reply_text(
        get_text(user_id, "main_menu"),
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text(
        get_text(user_id, "main_menu"),
        reply_markup=get_main_menu(user_id)
    )

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Restart conversation - useful when bot gets stuck"""
    context.user_data.clear()
    return await start(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    await update.message.reply_text("Операция отменена. Используйте /start для перезапуска.")
    context.user_data.clear()  # This will also clear the 'in_conversation' flag
    return ConversationHandler.END

async def show_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language command"""
    user_id = update.effective_user.id
    
    text = "🌐 Выберите язык / Choose language:"
    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'
    
    if lang == 'en':
        help_text = """ℹ️ Alt3r Help

🚀 /start - Start or restart the bot
🌐 /language - Change language
ℹ️ /help - Show this help
🏠 /menu - Go to main menu

Alt3r is a dating bot for neurodivergent people. Here you can find understanding, support and real connections with those who share your experience.

Features:
• Create detailed profile with ND traits
• Browse compatible profiles
• Advanced ND-based matching
• Send messages and likes
• Privacy-focused design

For support, use the feedback option in the main menu."""
    else:
        help_text = """ℹ️ Помощь Alt3r

🚀 /start - Запустить или перезапустить бота
🌐 /language - Изменить язык
ℹ️ /help - Показать эту помощь
🏠 /menu - Перейти в главное меню

Alt3r - это бот для знакомств нейроотличных людей. Здесь вы можете найти понимание, поддержку и настоящие связи с теми, кто разделяет ваш опыт.

Возможности:
• Создание подробного профиля с Нейр
• Просмотр совместимых анкет
• Продвинутый поиск по ND-характеристикам
• Отправка сообщений и лайков
• Конфиденциальность

Для поддержки используйте опцию обратной связи в главном меню."""
    
    keyboard = [[InlineKeyboardButton("🏠 Главное меню" if lang == 'ru' else "🏠 Main Menu", callback_data="back_to_menu")]]
    
    await update.message.reply_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def debug_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to check profiles in database"""
    user_id = update.effective_user.id
    all_users = db.all()
    
    debug_text = f"🔍 Debug Info:\n\n"
    debug_text += f"Total users in database: {len(all_users)}\n\n"
    
    current_user = db.get_user(user_id)
    if current_user:
        debug_text += f"Your profile:\n"
        debug_text += f"- Complete: {is_profile_complete_dict(current_user)}\n"
        debug_text += f"- Gender: {current_user.get('gender', 'None')}\n"
        debug_text += f"- Interest: {current_user.get('interest', 'None')}\n"
        debug_text += f"- Sent likes: {len(current_user.get('sent_likes', []))}\n\n"
    
    complete_profiles = 0
    for user in all_users:
        if user['user_id'] != user_id and is_profile_complete_dict(user):
            complete_profiles += 1
    
    debug_text += f"Other complete profiles: {complete_profiles}\n"
    debug_text += f"Profiles with names: {len([u for u in all_users if u.get('name')])}\n"
    debug_text += f"Profiles with photos: {len([u for u in all_users if u.get('photos') or u.get('media_id')])}"
    
    await update.message.reply_text(debug_text)

async def show_nd_traits_menu(query, user_id):
    """Show neurodivergent traits management menu"""
    user = db.get_user(user_id)
    if not user:
        return

    current_traits = user.get('nd_traits', [])
    current_symptoms = user.get('nd_symptoms', [])

    text = "🧠 Мои Нейроотличия\n\n"

    if current_traits:
        lang = user.get('lang', 'ru')
        trait_names = [ND_TRAITS[lang].get(trait, trait) for trait in current_traits if trait != 'none']
        if trait_names:
            text += f"Выбранные особенности:\n• " + "\n• ".join(trait_names) + "\n\n"

    if current_symptoms:
        lang = user.get('lang', 'ru')
        symptom_names = [ND_SYMPTOMS[lang].get(symptom, symptom) for symptom in current_symptoms]
        if symptom_names:
            text += f"Характеристики:\n• " + "\n• ".join(symptom_names[:5])
            if len(symptom_names) > 5:
                text += f"\n• ...{get_text(user_id, 'and_more')}{len(symptom_names) - 5}"
            text += "\n\n"

    text += "Что вы хотите изменить?"

    keyboard = [
        [InlineKeyboardButton("🧠 Изменить особенности", callback_data="add_nd_traits")],
        [InlineKeyboardButton("📋 Изменить характеристики", callback_data="manage_symptoms_detailed")],
        [InlineKeyboardButton("🔙 К настройкам", callback_data="profile_settings")]
    ]

    await safe_edit_message(query, text, InlineKeyboardMarkup(keyboard))

async def toggle_registration_trait(query, context, user_id, trait_key):
    """Toggle trait selection during registration"""
    current_traits = context.user_data.get("selected_nd_traits", [])

    if trait_key in current_traits:
        current_traits.remove(trait_key)
    else:
        if len(current_traits) < 3:
            current_traits.append(trait_key)
        else:
            await query.answer("❌ Можно выбрать максимум 3 особенности")
            return

    context.user_data["selected_nd_traits"] = current_traits
    
    # Update the interface immediately with new selection state
    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'

    text = "🧠 Выберите ваши нейроотличности:\n\n"
    text += "Это поможет найти людей с похожим опытом!\n"
    text += "Можно выбрать до 3 особенностей.\n\n"
    text += f"Выбрано: {len(current_traits)}/3\n\n"

    if current_traits:
        trait_names = [ND_TRAITS[lang].get(trait, trait) for trait in current_traits if trait in ND_TRAITS[lang] and trait != 'none']
        text += f"✅ {', '.join(trait_names)}\n\n"

    keyboard = []
    traits = ND_TRAITS[lang]

    for trait_key_btn, trait_name in traits.items():
        if trait_key_btn == 'none':
            continue

        # Mark selected traits with checkmark
        marker = "✅ " if trait_key_btn in current_traits else ""
        button_text = f"{marker}{trait_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"reg_trait_{trait_key_btn}")])

    # Always add control buttons
    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_save"), callback_data="reg_traits_done")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_skip_all"), callback_data="reg_traits_skip")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="reg_traits_back")])

    try:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Error updating trait selection: {e}")
        # Fallback: delete and send new message
        try:
            await query.delete_message()
            await query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e2:
            logger.error(f"Fallback failed: {e2}")
            await query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

async def toggle_registration_symptom(query, context, user_id, symptom_key):
    """Toggle symptom selection during registration"""
    current_symptoms = context.user_data.get("selected_characteristics", [])

    if symptom_key in current_symptoms:
        current_symptoms.remove(symptom_key)
    else:
        if len(current_symptoms) < 3:
            current_symptoms.append(symptom_key)
        else:
            await query.answer("❌ Можно выбрать максимум 3 характеристики")
            return

    context.user_data["selected_characteristics"] = current_symptoms
    await show_registration_nd_symptoms(query, context, user_id)

async def show_registration_nd_symptoms(query, context, user_id):
    """Show ND symptoms selection during registration"""
    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'

    text = "🔍 Выберите характеристики, которые вас описывают:\n\n"
    text += "Это поможет найти людей с похожим опытом!\n"
    text += "Можно выбрать до 3 характеристик.\n\n"

    current_symptoms = context.user_data.get("selected_characteristics", [])
    text += f"Выбрано: {len(current_symptoms)}/3\n\n"

    if current_symptoms:
        symptom_names = [ND_SYMPTOMS[lang].get(symptom, symptom) for symptom in current_symptoms]
        text += f"✅ {', '.join(symptom_names)}\n\n"

    keyboard = []
    symptoms = ND_SYMPTOMS[lang]

    # Show first 10 symptoms
    for i, (symptom_key, symptom_name) in enumerate(list(symptoms.items())[:10]):
        marker = "✅ " if symptom_key in current_symptoms else ""
        button_text = f"{marker}{symptom_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"reg_symptom_{symptom_key}")])

    # Add control buttons
    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_save"), callback_data="reg_symptoms_done")])
    keyboard.append([InlineKeyboardButton("⏭️ Пропустить", callback_data="reg_symptoms_skip")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="reg_symptoms_back")])

    try:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    return WAITING_NAME

async def finish_nd_registration(query, context, user_id):
    """Finish ND registration and move to photo upload"""
    # Save the selections (they're already in context.user_data)

    # First remove any existing keyboards
    await query.message.reply_text(
        get_text(user_id, "questionnaire_photo"),
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Delete the inline keyboard message
    try:
        await query.delete_message()
    except:
        pass

    # Return PHOTO state to continue photo upload
    return PHOTO

async def toggle_nd_trait(query, user_id, trait_key):
    """Toggle ND trait selection for existing user"""
    user = db.get_user(user_id)
    if not user:
        return

    current_traits = user.get('nd_traits', [])

    if trait_key in current_traits:
        current_traits.remove(trait_key)
    else:
        if len(current_traits) < 3:
            current_traits.append(trait_key)
        else:
            await query.answer("❌ Можно выбрать максимум 3 особенности")
            return

    db.create_or_update_user(user_id, {'nd_traits': current_traits})
    await show_add_traits_menu(query, user_id)

async def toggle_nd_symptom(query, user_id, symptom_key):
    """Toggle ND symptom selection for existing user"""
    user = db.get_user(user_id)
    if not user:
        return

    current_symptoms = user.get('nd_symptoms', [])

    if symptom_key in current_symptoms:
        current_symptoms.remove(symptom_key)
    else:
        if len(current_symptoms) < 3:
            current_symptoms.append(symptom_key)
        else:
            await query.answer("❌ Можно выбрать максимум 3 характеристики")
            return

    db.create_or_update_user(user_id, {'nd_symptoms': current_symptoms})
    await show_detailed_symptoms_menu(query, user_id)

async def show_add_traits_menu(query, user_id):
    """Show trait selection menu for existing user"""
    user = db.get_user(user_id)
    if not user:
        return

    lang = user.get('lang', 'ru')
    current_traits = user.get('nd_traits', [])

    text = "🧠 Выберите ваши нейроотличности:\n\n"
    text += f"Выбрано: {len(current_traits)}/3\n\n"

    if current_traits:
        trait_names = [ND_TRAITS[lang].get(trait, trait) for trait in current_traits]
        text += f"✅ {', '.join(trait_names)}\n\n"

    keyboard = []
    traits = ND_TRAITS[lang]

    for trait_key, trait_name in traits.items():
        if trait_key == 'none':
            continue

        marker = "✅ " if trait_key in current_traits else ""
        button_text = f"{marker}{trait_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"toggle_trait_{trait_key}")])

    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_save"), callback_data="save_traits")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="manage_symptoms")])

    try:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_detailed_symptoms_menu(query, user_id):
    """Show detailed symptoms menu for existing user"""
    user = db.get_user(user_id)
    if not user:
        return

    lang = user.get('lang', 'ru')
    current_symptoms = user.get('nd_symptoms', [])

    text = "🔍 Выберите характеристики:\n\n"
    text += f"Выбрано: {len(current_symptoms)}/3\n\n"

    if current_symptoms:
        symptom_names = [ND_SYMPTOMS[lang].get(symptom, symptom) for symptom in current_symptoms]
        text += f"✅ {', '.join(symptom_names)}\n\n"

    keyboard = []
    symptoms = list(ND_SYMPTOMS[lang].items())[:15]  # Show first 15

    for symptom_key, symptom_name in symptoms:
        marker = "✅ " if symptom_key in current_symptoms else ""
        button_text = f"{marker}{symptom_name}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"toggle_symptom_{symptom_key}")])

    keyboard.append([InlineKeyboardButton(get_text(user_id, "btn_save"), callback_data="save_symptoms")])
    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="manage_symptoms")])

    try:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except:
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_nd_search_menu(query, user_id):
    """Show ND search menu"""
    text = "🧠 ND-поиск\n\n"
    text += "Поиск людей с похожими нейроотличностями:"

    keyboard = [
        [InlineKeyboardButton("🔍 Поиск по особенностям", callback_data="search_by_traits")],
        [InlineKeyboardButton("🎯 Совместимость", callback_data="compatibility_search")],
        [InlineKeyboardButton("💡 Рекомендации", callback_data="recommendations")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def search_by_traits(query, context, user_id):
    """Search users by similar traits"""
    user = db.get_user(user_id)
    if not user:
        return

    user_traits = set(user.get('nd_traits', []))
    if not user_traits or 'none' in user_traits:
        await query.edit_message_text(
            "❌ Сначала добавьте свои Нейроотличия в настройках профиля",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🧠 Добавить особенности", callback_data="manage_symptoms"),
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="nd_search")
            ]])
        )
        return

    # Find users with similar traits
    all_users = db.all()
    similar_users = []

    for other_user in all_users:
        if (other_user['user_id'] != user_id and 
            is_profile_complete_dict(other_user) and
            matches_interest_criteria(user, other_user) and
            other_user['user_id'] not in user.get('sent_likes', [])):

            other_traits = set(other_user.get('nd_traits', []))
            if other_traits and 'none' not in other_traits:
                common_traits = user_traits.intersection(other_traits)

                if common_traits:
                    # Calculate similarity score based on common traits
                    similarity_score = len(common_traits) / len(user_traits.union(other_traits))
                    similar_users.append((other_user, similarity_score, common_traits))

    if not similar_users:
        await query.edit_message_text(
            "😕 Не найдено пользователей с похожими ND-особенностями\n\nПопробуйте:\n• Расширить свои особенности\n• Поискать по характеристикам",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Совместимость", callback_data="compatibility_search")],
                [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="nd_search")]
            ])
        )
        return

    # Sort by similarity (highest first)
    similar_users.sort(key=lambda x: x[1], reverse=True)
    context.user_data['nd_search_results'] = similar_users
    context.user_data['nd_search_index'] = 0

    await show_nd_result(query, context, user_id, similar_users[0])

async def show_nd_result(query, context, user_id, result_tuple):
    """Show ND search result"""
    other_user, similarity_score, common_traits = result_tuple

    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'

    profile_text = f"👤 *{other_user['name']}*, {other_user['age']} лет\n"
    profile_text += f"📍 *{other_user['city']}*\n"

    # Show common traits
    trait_names = [ND_TRAITS[lang].get(trait, trait) for trait in common_traits]
    profile_text += f"🧠 Общие особенности: *{', '.join(trait_names)}*\n"
    profile_text += f"📊 Совместимость: {int(similarity_score * 100)}%\n\n"
    profile_text += f"💭 {other_user['bio']}"

    current_index = context.user_data.get('nd_search_index', 0)
    total_results = len(context.user_data.get('nd_search_results', []))

    keyboard = [
        [InlineKeyboardButton("❤️", callback_data=f"like_{other_user['user_id']}")],
        [InlineKeyboardButton("💌 Сообщение", callback_data=f"send_message_{other_user['user_id']}")],
        [InlineKeyboardButton("⏭️ Следующий", callback_data="next_nd_result") if current_index < total_results - 1 else InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")]
    ]

    photos = other_user.get('photos', [])
    if photos:
        try:
            await query.message.reply_photo(
                photo=photos[0],
                caption=profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await query.delete_message()
        except:
            await query.edit_message_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await query.edit_message_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_next_nd_result(query, context, user_id):
    """Show next ND search result"""
    results = context.user_data.get('nd_search_results', [])
    current_index = context.user_data.get('nd_search_index', 0)

    if current_index + 1 < len(results):
        context.user_data['nd_search_index'] = current_index + 1
        await show_nd_result(query, context, user_id, results[current_index + 1])
    else:
        await query.edit_message_text(
            "Больше нет результатов поиска",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К поиску", callback_data="nd_search")
            ]])
        )

async def compatibility_search(query, context, user_id):
    """Advanced compatibility search based on traits and symptoms"""
    user = db.get_user(user_id)
    if not user:
        return

    user_traits = set(user.get('nd_traits', []))
    user_symptoms = set(user.get('nd_symptoms', []))
    
    if not user_traits and not user_symptoms:
        await query.edit_message_text(
            "❌ Добавьте Нейроотличия и характеристики для поиска совместимости",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🧠 Настроить профиль", callback_data="manage_symptoms"),
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="nd_search")
            ]])
        )
        return

    # Find compatible users
    all_users = db.all()
    compatible_users = []

    for other_user in all_users:
        if (other_user['user_id'] != user_id and 
            is_profile_complete_dict(other_user) and
            matches_interest_criteria(user, other_user) and
            other_user['user_id'] not in user.get('sent_likes', [])):

            other_traits = set(other_user.get('nd_traits', []))
            other_symptoms = set(other_user.get('nd_symptoms', []))
            
            # Calculate compatibility score
            trait_match = 0
            symptom_match = 0
            total_score = 0
            
            if user_traits and other_traits:
                common_traits = user_traits.intersection(other_traits)
                trait_match = len(common_traits) / len(user_traits.union(other_traits)) if user_traits.union(other_traits) else 0
                total_score += trait_match * 0.6  # Traits weight 60%
            
            if user_symptoms and other_symptoms:
                common_symptoms = user_symptoms.intersection(other_symptoms)
                symptom_match = len(common_symptoms) / len(user_symptoms.union(other_symptoms)) if user_symptoms.union(other_symptoms) else 0
                total_score += symptom_match * 0.4  # Symptoms weight 40%
            
            # Only include if there's some compatibility
            if total_score > 0.1:  # At least 10% compatibility
                compatible_users.append((other_user, total_score, user_traits.intersection(other_traits), user_symptoms.intersection(other_symptoms)))

    if not compatible_users:
        await query.edit_message_text(
            "😕 Не найдено совместимых пользователей\n\nПопробуйте добавить больше характеристик в профиль",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Поиск по особенностям", callback_data="search_by_traits")],
                [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="nd_search")]
            ])
        )
        return

    # Sort by compatibility score
    compatible_users.sort(key=lambda x: x[1], reverse=True)
    context.user_data['compatibility_results'] = compatible_users
    context.user_data['compatibility_index'] = 0

    await show_compatibility_result(query, context, user_id, compatible_users[0])

async def show_recommendations(query, context, user_id):
    """Show personalized recommendations based on user's profile and activity"""
    user = db.get_user(user_id)
    if not user:
        return

    user_traits = set(user.get('nd_traits', []))
    user_symptoms = set(user.get('nd_symptoms', []))
    user_city = user.get('city', '')
    user_sent_likes = set(user.get('sent_likes', []))
    
    # Find recommended users
    all_users = db.all()
    recommendations = []

    for other_user in all_users:
        if (other_user['user_id'] != user_id and 
            is_profile_complete_dict(other_user) and
            matches_interest_criteria(user, other_user) and
            other_user['user_id'] not in user_sent_likes):

            score = 0
            reasons = []
            
            # Same city bonus
            if other_user.get('city') == user_city and user_city:
                score += 0.3
                reasons.append("📍 Ваш город")
            
            # ND traits compatibility
            other_traits = set(other_user.get('nd_traits', []))
            if user_traits and other_traits:
                common_traits = user_traits.intersection(other_traits)
                if common_traits:
                    trait_score = len(common_traits) / len(user_traits.union(other_traits))
                    score += trait_score * 0.4
                    reasons.append("🧠 Похожие особенности")
            
            # ND symptoms compatibility
            other_symptoms = set(other_user.get('nd_symptoms', []))
            if user_symptoms and other_symptoms:
                common_symptoms = user_symptoms.intersection(other_symptoms)
                if common_symptoms:
                    symptom_score = len(common_symptoms) / len(user_symptoms.union(other_symptoms))
                    score += symptom_score * 0.2
                    reasons.append("🔍 Общие характеристики")
            
            # Age compatibility (closer ages get higher score)
            user_age = user.get('age', 25)
            other_age = other_user.get('age', 25)
            age_diff = abs(user_age - other_age)
            if age_diff <= 3:
                score += 0.1
                reasons.append("🎂 Близкий возраст")
            
            # New user bonus (registered recently)
            if other_user.get('created_at'):
                try:
                    created_date = datetime.fromisoformat(other_user['created_at'])
                    days_since = (datetime.now() - created_date).days
                    if days_since <= 7:
                        score += 0.1
                        reasons.append("✨ Новый пользователь")
                except:
                    pass
            
            # Only recommend if there's some compatibility
            if score > 0.2 and reasons:
                recommendations.append((other_user, score, reasons))

    if not recommendations:
        await query.edit_message_text(
            "😊 Пока нет новых рекомендаций\n\nПопробуйте:\n• Обновить свой профиль\n• Добавить больше ND-характеристик\n• Использовать обычный поиск",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👀 Смотреть анкеты", callback_data="browse_profiles")],
                [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="nd_search")]
            ])
        )
        return

    # Sort by recommendation score
    recommendations.sort(key=lambda x: x[1], reverse=True)
    context.user_data['recommendation_results'] = recommendations
    context.user_data['recommendation_index'] = 0

    await show_recommendation_result(query, context, user_id, recommendations[0])

async def show_recommendation_result(query, context, user_id, result_tuple):
    """Show recommendation result"""
    other_user, score, reasons = result_tuple

    profile_text = f"💡 Рекомендация для вас\n\n"
    profile_text += f"👤 **{other_user['name']}**, {other_user['age']} лет\n"
    profile_text += f"📍 **{other_user['city']}**\n"
    profile_text += f"⭐ Совпадение: {int(score * 100)}%\n\n"
    
    if reasons:
        profile_text += f"Почему мы рекомендуем:\n• " + "\n• ".join(reasons) + "\n\n"
    
    profile_text += f"💭 {other_user['bio']}"

    current_index = context.user_data.get('recommendation_index', 0)
    total_results = len(context.user_data.get('recommendation_results', []))

    keyboard = [
        [InlineKeyboardButton("❤️", callback_data=f"like_{other_user['user_id']}")],
        [InlineKeyboardButton("💌 Сообщение", callback_data=f"send_message_{other_user['user_id']}")],
        []
    ]

    # Navigation
    if current_index < total_results - 1:
        keyboard[2].append(InlineKeyboardButton("⏭️ Следующая", callback_data="next_recommendation"))
    
    if not keyboard[2]:
        keyboard[2].append(InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu"))

    keyboard.append([InlineKeyboardButton("🔙 К поиску", callback_data="nd_search")])

    photos = other_user.get('photos', [])
    if photos:
        try:
            await query.message.reply_photo(
                photo=photos[0],
                caption=profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await query.delete_message()
        except:
            await query.edit_message_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await query.edit_message_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_compatibility_result(query, context, user_id, result_tuple):
    """Show compatibility search result"""
    other_user, compatibility_score, common_traits, common_symptoms = result_tuple

    user = db.get_user(user_id)
    lang = user.get('lang', 'ru') if user else 'ru'

    profile_text = f"👤 *{other_user['name']}*, {other_user['age']} лет\n"
    profile_text += f"📍 *{other_user['city']}*\n"
    profile_text += f"🎯 Совместимость: {int(compatibility_score * 100)}%\n\n"

    # Show common traits if any
    if common_traits:
        trait_names = [ND_TRAITS[lang].get(trait, trait) for trait in common_traits if trait != 'none']
        if trait_names:
            profile_text += f"🧠 Общие особенности: *{', '.join(trait_names)}*\n"

    # Show common symptoms if any
    if common_symptoms:
        symptom_names = [ND_SYMPTOMS[lang].get(symptom, symptom) for symptom in common_symptoms]
        if symptom_names:
            profile_text += f"🔍 Общие характеристики: *{', '.join(symptom_names[:3])}"
            if len(symptom_names) > 3:
                profile_text += f" (+{len(symptom_names) - 3})"
            profile_text += "*\n"

    profile_text += f"\n💭 {other_user['bio']}"

    current_index = context.user_data.get('compatibility_index', 0)
    total_results = len(context.user_data.get('compatibility_results', []))

    keyboard = [
        [InlineKeyboardButton("❤️", callback_data=f"like_{other_user['user_id']}")],
        [InlineKeyboardButton("💌 Сообщение", callback_data=f"send_message_{other_user['user_id']}")],
        []
    ]

    # Navigation buttons
    if current_index < total_results - 1:
        keyboard[2].append(InlineKeyboardButton("⏭️ Следующий", callback_data="next_compatibility"))
    
    if current_index > 0:
        keyboard[2].append(InlineKeyboardButton("⏪ Предыдущий", callback_data="prev_compatibility"))
    
    if not keyboard[2]:  # If no navigation buttons
        keyboard[2].append(InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu"))

    keyboard.append([InlineKeyboardButton("🔙 К поиску", callback_data="nd_search")])

    photos = other_user.get('photos', [])
    if photos:
        try:
            await query.message.reply_photo(
                photo=photos[0],
                caption=profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await query.delete_message()
        except:
            await query.edit_message_text(
                profile_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await query.edit_message_text(
            profile_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_next_compatibility_result(query, context, user_id):
    """Show next compatibility result"""
    results = context.user_data.get('compatibility_results', [])
    current_index = context.user_data.get('compatibility_index', 0)

    if current_index + 1 < len(results):
        context.user_data['compatibility_index'] = current_index + 1
        await show_compatibility_result(query, context, user_id, results[current_index + 1])
    else:
        await query.edit_message_text(
            "Больше совместимых пользователей не найдено",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Новый поиск", callback_data="compatibility_search"),
                InlineKeyboardButton("🔙 К поиску", callback_data="nd_search")
            ]])
        )

async def start_message_to_user(query, context, user_id, target_id):
    """Start sending message to user - this will like their profile and send message"""
    context.user_data['sending_message'] = True
    context.user_data['message_target_id'] = target_id

    target_user = db.get_user(target_id)
    target_name = target_user.get('name', 'Пользователь') if target_user else 'Пользователь'

    try:
        await query.edit_message_text(
            f"💌 Отправка сообщения пользователю {target_name}\n\n❤️ Это автоматически поставит лайк и отправит сообщение.\n\nНапишите ваше сообщение:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="browse_profiles")
            ]])
        )
    except:
        await query.message.reply_text(
            f"💌 Отправка сообщения пользователю {target_name}\n\n❤️ Это автоматически поставит лайк и отправит сообщение.\n\nНапишите ваше сообщение:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="browse_profiles")
            ]])
        )

async def start_video_to_user(query, context, user_id, target_id):
    """Start sending video to user"""
    context.user_data['sending_video'] = True
    context.user_data['video_target_id'] = target_id

    target_user = db.get_user(target_id)
    target_name = target_user.get('name', 'Пользователь') if target_user else 'Пользователь'

    try:
        await query.edit_message_text(
            f"🎥 Отправка видео-сообщения пользователю {target_name}\n\nЗапишите круглое видео-сообщение:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="browse_profiles")
            ]])
        )
    except:
        await query.message.reply_text(
            f"🎥 Отправка видео-сообщения пользователю {target_name}\n\nЗапишите круглое видео-сообщение:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="browse_profiles")
            ]])
        )

async def start_feedback(query, context, user_id, feedback_type):
    """Start feedback collection"""
    context.user_data['waiting_feedback'] = True
    context.user_data['feedback_type'] = feedback_type

    prompts = {
        'complaint': "🚨 Опишите вашу жалобу:",
        'suggestion': "💡 Поделитесь вашим предложением:",
        'support': "🆘 Опишите техническую проблему:"
    }

    prompt = prompts.get(feedback_type, "📝 Опишите ваше сообщение:")

    try:
        await query.edit_message_text(
            prompt,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="feedback")
            ]])
        )
    except:
        await query.message.reply_text(
            prompt,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="feedback")
            ]])
        )

async def show_rating_menu(query, user_id):
    """Show app rating menu"""
    text = "⭐ Оцените Alt3r\n\nКак вам наше приложение?"

    keyboard = []
    for i in range(1, 6):
        stars = "⭐" * i
        keyboard.append([InlineKeyboardButton(f"{stars} {i}", callback_data=f"rate_app_{i}")])

    keyboard.append([InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="feedback")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def save_app_rating(query, user_id, rating):
    """Save app rating"""
    # Save rating to feedback database
    feedback_data = {
        'user_id': user_id,
        'username': query.from_user.username or '',
        'first_name': query.from_user.first_name or '',
        'type': 'rating',
        'text': f"Оценка: {rating}/5",
        'rating': rating,
        'timestamp': datetime.now().isoformat()
    }

    feedback_db.insert(feedback_data)

    await query.edit_message_text(
        f"✅ Спасибо за оценку! Вы поставили {rating}/5 звезд",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 К обратной связи", callback_data="feedback")
        ]])
    )

async def change_language(query, user_id):
    """Show language selection"""
    text = "🌐 Выберите язык / Choose language:"

    keyboard = [
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def set_language(query, user_id, lang):
    """Set user language"""
    db.create_or_update_user(user_id, {'lang': lang})

    # Show language confirmation message in the selected language
    if lang == 'ru':
        success_text = "✅ Язык установлен: Русский"
        menu_text = "🏠 Главное меню"
        back_text = "🔙 Назад"
    else:
        success_text = "✅ Language set: English"
        menu_text = "🏠 Main Menu"
        back_text = "🔙 Back"
    
    # Show confirmation with immediate menu
    try:
        await query.edit_message_text(
            success_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(back_text, callback_data="back_to_menu")
            ]])
        )
        
        # Auto-redirect to main menu after 2 seconds to show updated language
        import asyncio
        await asyncio.sleep(2)
        await query.edit_message_text(
            menu_text,
            reply_markup=get_main_menu(user_id)
        )
    except:
        await query.message.reply_text(
            success_text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(back_text, callback_data="back_to_menu")
            ]])
        )

async def start_change_city_setting(query, context, user_id):
    """Start city change from settings"""
    context.user_data['changing_city_setting'] = True

    try:
        await query.edit_message_text(
            "📍 Введите ваш новый город:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="profile_settings")
            ]])
        )
    except:
        await query.message.reply_text(
            "📍 Введите ваш новый город:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="profile_settings")
            ]])
        )

async def start_change_interest_setting(query, context, user_id):
    """Start interest change from settings"""
    text = "💕 Кто вас интересует?"

    keyboard = [
        [InlineKeyboardButton("Парни", callback_data="interest_male")],
        [InlineKeyboardButton("Девушки", callback_data="interest_female")],
        [InlineKeyboardButton("Всё равно", callback_data="interest_both")],
        [InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="profile_settings")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm_recreate_profile(query, user_id):
    """Confirm profile recreation"""
    text = "⚠️ Вы уверены, что хотите заполнить анкету заново?\n\n"
    text += "Это удалит всю текущую информацию и вам нужно будет заполнить всё снова.\n\n"
    text += "Это действие нельзя отменить!"

    keyboard = [
        [InlineKeyboardButton("✅ Да, заполнить заново", callback_data="confirm_recreate")],
        [InlineKeyboardButton("❌ Отмена", callback_data="profile_settings")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def confirm_reset_matches(query, user_id):
    """Confirm match reset"""
    user = db.get_user(user_id)
    current_lang = user.get('lang', 'ru') if user else 'ru'
    
    if current_lang == 'en':
        text = "⚠️ Are you sure you want to reset your matches?\n\n"
        text += "This will clear:\n"
        text += "• All sent likes\n"
        text += "• All received likes\n" 
        text += "• All declined profiles\n\n"
        text += "You'll be able to see and like all profiles again.\n\n"
        text += "This action cannot be undone!"
        confirm_btn = "💔 Yes, reset matches"
        cancel_btn = "❌ Cancel"
    else:
        text = "⚠️ Вы уверены, что хотите сбросить совпадения?\n\n"
        text += "Это очистит:\n"
        text += "• Все отправленные лайки\n"
        text += "• Все полученные лайки\n"
        text += "• Все пропущенные анкеты\n\n"
        text += "Вы снова сможете видеть и лайкать все анкеты.\n\n"
        text += "Это действие нельзя отменить!"
        confirm_btn = "💔 Да, сбросить совпадения"
        cancel_btn = "❌ Отмена"

    keyboard = [
        [InlineKeyboardButton(confirm_btn, callback_data="confirm_reset_matches")],
        [InlineKeyboardButton(cancel_btn, callback_data="profile_settings")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def reset_user_matches(query, user_id):
    """Reset user's match history"""
    user = db.get_user(user_id)
    current_lang = user.get('lang', 'ru') if user else 'ru'
    
    # Clear all match-related data
    db.update({
        'sent_likes': [],
        'received_likes': [],
        'unnotified_likes': [],
        'declined_likes': []
    }, User.user_id == user_id)
    
    if current_lang == 'en':
        success_text = "✅ Matches reset successfully!\n\nYou can now browse all profiles again and start fresh."
        back_btn = "🔙 Back to Settings"
    else:
        success_text = "✅ Совпадения успешно сброшены!\n\nТеперь вы можете снова просматривать все анкеты и начать заново."
        back_btn = "🔙 К настройкам"
    
    await query.edit_message_text(
        success_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(back_btn, callback_data="profile_settings")
        ]])
    )

async def confirm_delete_account(query, user_id):
    """Confirm account deletion"""
    text = "⚠️ Вы уверены, что хотите удалить аккаунт?\n\n"
    text += "Это действие нельзя отменить!"

    keyboard = [
        [InlineKeyboardButton("🗑️ Да, удалить", callback_data="confirm_delete")],
        [InlineKeyboardButton("❌ Отмена", callback_data="profile_settings")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_prev_compatibility_result(query, context, user_id):
    """Show previous compatibility result"""
    results = context.user_data.get('compatibility_results', [])
    current_index = context.user_data.get('compatibility_index', 0)

    if current_index > 0:
        context.user_data['compatibility_index'] = current_index - 1
        await show_compatibility_result(query, context, user_id, results[current_index - 1])
    else:
        await query.answer("Это первая рекомендация")

async def show_next_recommendation_result(query, context, user_id):
    """Show next recommendation result"""
    results = context.user_data.get('recommendation_results', [])
    current_index = context.user_data.get('recommendation_index', 0)

    if current_index + 1 < len(results):
        context.user_data['recommendation_index'] = current_index + 1
        await show_recommendation_result(query, context, user_id, results[current_index + 1])
    else:
        await query.edit_message_text(
            "Больше рекомендаций нет",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Обновить рекомендации", callback_data="recommendations"),
                InlineKeyboardButton("🔙 К поиску", callback_data="nd_search")
            ]])
        )

async def continue_profile_creation(query, context, user_id):
    """Continue profile creation by guiding user to use /start"""
    user = db.get_user(user_id)
    if not user:
        await query.edit_message_text(
            get_text(user_id, "profile_not_found"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
            ]])
        )
        return
    
    # Clear any existing conversation data
    context.user_data.clear()
    
    lang = user.get('lang', 'ru')
    
    if lang == 'en':
        text = "🔄 To complete your profile, please send /start\n\nThis will restart the profile creation process and guide you through the remaining steps."
    else:
        text = "🔄 Чтобы завершить заполнение профиля, отправьте /start\n\nЭто запустит процесс создания профиля и поможет вам заполнить оставшиеся поля."
    
    try:
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button") if lang == 'ru' else "🔙 Back", callback_data="back_to_menu")
            ]])
        )
    except:
        await query.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button") if lang == 'ru' else "🔙 Back", callback_data="back_to_menu")
            ]])
        )

async def show_detailed_stats(query, user_id):
    """Show detailed statistics"""
    user = db.get_user(user_id)
    if not user:
        return

    lang = user.get('lang', 'ru')

    # Get detailed stats
    sent_likes = len(user.get('sent_likes', []))
    received_likes = len(user.get('received_likes', []))

    user_sent = set(user.get('sent_likes', []))
    user_received = set(user.get('received_likes', []))
    matches = len(user_sent.intersection(user_received))

    # Calculate days since registration
    created_at = user.get('created_at', '')
    if created_at:
        try:
            created_date = datetime.fromisoformat(created_at)
            days_active = (datetime.now() - created_date).days
        except:
            days_active = 0
    else:
        days_active = 0

    if lang == 'en':
        text = f"📈 Detailed Statistics\n\n"
        text += f"👤 Profile:\n"
        text += f"• Days in app: {days_active}\n"
        text += f"• City: {user.get('city', 'Not specified')}\n\n"

        text += f"💕 Activity:\n"
        text += f"• Likes sent: {sent_likes}\n"
        text += f"• Likes received: {received_likes}\n"
        text += f"• Mutual likes: {matches}\n\n"

        if sent_likes > 0:
            success_rate = int((matches / sent_likes) * 100)
            text += f"🎯 Success rate: {success_rate}%\n"

        # ND traits stats
        nd_traits = user.get('nd_traits', [])
        nd_symptoms = user.get('nd_symptoms', [])

        if nd_traits or nd_symptoms:
            text += f"\n🧠 ND Profile:\n"
            text += f"• Traits: {len(nd_traits)}/3\n"
            text += f"• Characteristics: {len(nd_symptoms)}/3\n"

        back_text = "🔙 Back"
    else:
        text = f"📈 Подробная статистика\n\n"
        text += f"👤 Профиль:\n"
        text += f"• Дней в приложении: {days_active}\n"
        text += f"• Город: {user.get('city', 'Не указан')}\n\n"

        text += f"💕 Активность:\n"
        text += f"• Отправлено лайков: {sent_likes}\n"
        text += f"• Получено лайков: {received_likes}\n"
        text += f"• Взаимные лайки: {matches}\n\n"

        if sent_likes > 0:
            success_rate = int((matches / sent_likes) * 100)
            text += f"🎯 Успешность: {success_rate}%\n"

        # ND traits stats
        nd_traits = user.get('nd_traits', [])
        nd_symptoms = user.get('nd_symptoms', [])

        if nd_traits or nd_symptoms:
            text += f"\n🧠 ND-профиль:\n"
            text += f"• Особенности: {len(nd_traits)}/3\n"
            text += f"• Характеристики: {len(nd_symptoms)}/3\n"

        back_text = "🔙 Назад"

    keyboard = [
        [InlineKeyboardButton(back_text, callback_data="statistics")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_mutual_match_profile(query, current_user, matched_user):
    """Show mutual match profile with persistent connection information"""
    try:
        current_lang = current_user.get('lang', 'ru')
        matched_name = matched_user['name']
        
        # Format profile text with clickable username if available
        matched_username = matched_user.get('username', '')
        profile_text = f"🎉 Взаимный лайк! Соединение установлено!\n\n"
        if matched_username:
            profile_text += f"👤 *{matched_name}* (@{matched_username}), {matched_user['age']} лет\n"
        else:
            profile_text += f"👤 *{matched_name}*, {matched_user['age']} лет\n"
        profile_text += f"📍 *{matched_user['city']}*\n"
        
        # Add ND traits if available
        nd_traits = matched_user.get('nd_traits', [])
        if nd_traits:
            traits_dict = ND_TRAITS.get(current_lang, ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 ND: *{', '.join(trait_names)}*\n"
        
        profile_text += f"\n💭 {matched_user['bio']}\n\n"
        profile_text += "✨ Теперь вы можете общаться! Контакт сохранен в ваших лайках."

        # Keep connection-friendly buttons - users can contact directly via Telegram usernames
        keyboard = [
            [InlineKeyboardButton("⏭️ Продолжить просмотр", callback_data="next_profile"),
             InlineKeyboardButton("💌 Мои лайки", callback_data="my_likes")]
        ]

        # Send with photo if available - always as new message
        photos = matched_user.get('photos', [])
        if photos:
            try:
                # Delete previous message
                try:
                    await query.delete_message()
                except:
                    pass
                    
                # Send new photo message
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending match photo: {e}")
                try:
                    await query.message.reply_text(
                        profile_text,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='Markdown'
                    )
                except:
                    await safe_edit_message(
                        query,
                        profile_text,
                        InlineKeyboardMarkup(keyboard)
                    )
        else:
            try:
                await query.message.reply_text(
                    profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
            except:
                await safe_edit_message(
                    query,
                    profile_text,
                    InlineKeyboardMarkup(keyboard)
                )
            
    except Exception as e:
        logger.error(f"Error showing mutual match profile: {e}")
        # Clean fallback with messaging options
        try:
            await query.message.reply_text(
                "🎉 Взаимный лайк! Соединение установлено!\n\nТеперь вы можете общаться напрямую в Telegram!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭️ Далее", callback_data="next_profile"),
                     InlineKeyboardButton("💌 Мои лайки", callback_data="my_likes")]
                ])
            )
        except:
            await safe_edit_message(
                query,
                "🎉 Взаимный лайк! Соединение установлено!\n\nТеперь вы можете общаться напрямую в Telegram!",
                InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏭️ Далее", callback_data="next_profile"),
                     InlineKeyboardButton("💌 Мои лайки", callback_data="my_likes")]
                ])
            )



async def send_mutual_match_notification(user_id, application, matched_user):
    """Send mutual match notification with matched user's profile and revealed usernames"""
    try:
        user = db.get(Query().user_id == user_id)
        if not user:
            logger.warning(f"User {user_id} not found for mutual match notification")
            return

        lang = user.get('lang', 'ru')
        matched_name = matched_user.get('name', 'Пользователь')
        matched_username = matched_user.get('username', '')
        user_username = user.get('username', '')
        
        if lang == 'en':
            text = f"🎉 Mutual Like!\n\nYou can now chat directly on Telegram!\n\n"
            if matched_username:
                text += f"📱 {matched_name}: @{matched_username}\n"
            else:
                text += f"📱 {matched_name}: (no username set)\n"
            
            if user_username:
                text += f"📱 You: @{user_username}\n"
            else:
                text += f"📱 You: (no username set)\n"
                
            text += "\n✨ Contact each other directly in Telegram!"
            view_btn = f"👤 View {matched_name}'s Profile"
            message_btn = f"💌 Message {matched_name}"
        else:
            text = f"🎉 Взаимный лайк!\n\nТеперь вы можете общаться напрямую в Telegram!\n\n"
            if matched_username:
                text += f"📱 {matched_name}: @{matched_username}\n"
            else:
                text += f"📱 {matched_name}: (username не указан)\n"
            
            if user_username:
                text += f"📱 Вы: @{user_username}\n"
            else:
                text += f"📱 Вы: (username не указан)\n"
                
            text += "\n✨ Свяжитесь друг с другом напрямую в Telegram!"
            view_btn = f"👤 Посмотреть профиль {matched_name}"
            message_btn = f"💌 Написать {matched_name}"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 Мои лайки" if lang == 'ru' else "💌 My Likes", callback_data="my_likes")]
        ])

        # Send with matched user's photo if available
        photos = matched_user.get('photos', [])
        if photos:
            try:
                await application.bot.send_photo(
                    chat_id=user_id,
                    photo=photos[0],
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending photo notification: {e}")
                await application.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
        else:
            await application.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        logger.info(f"Mutual match notification sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending mutual match notification to {user_id}: {e}")

async def send_message_with_profile(bot, target_id, sender, message_text, is_match=False):
    """Send message with sender's profile for easy like-back"""
    try:
        target_user = db.get_user(target_id)
        if not target_user:
            return

        lang = target_user.get('lang', 'ru')
        sender_name = sender.get('name', 'Пользователь')
        sender_username = sender.get('username', '')
        
        # Format message at the top, then profile preview
        if is_match:
            if lang == 'en':
                # Show message at top with revealed username for mutual likes
                message_header = f"💌 Message from {sender_name}"
                if sender_username:
                    message_header += f" (@{sender_username})"
                message_header += f":\n\n\"{message_text}\"\n\n"
                
                text = f"{message_header}🎉 Mutual Like! You can now chat freely!\n\n"
                text += f"👤 *{sender_name}*, {sender.get('age', '?')} years old\n"
                text += f"📍 *{sender.get('city', 'Unknown')}*\n"
            else:
                # Show message at top with revealed username for mutual likes
                message_header = f"💌 Сообщение от {sender_name}"
                if sender_username:
                    message_header += f" (@{sender_username})"
                message_header += f":\n\n\"{message_text}\"\n\n"
                
                text = f"{message_header}🎉 Взаимный лайк! Теперь вы можете свободно общаться!\n\n"
                text += f"👤 *{sender_name}*, {sender.get('age', '?')} лет\n"
                text += f"📍 *{sender.get('city', 'Неизвестно')}*\n"
            
            # Add ND traits if available
            nd_traits = sender.get('nd_traits', [])
            if nd_traits:
                traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
                trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
                if trait_names:
                    text += f"🧠 ND: *{', '.join(trait_names)}*\n"
            
            text += f"\n💭 {sender.get('bio', '')}"
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("💌 Мои лайки" if lang == 'ru' else "💌 My Likes", callback_data="my_likes"),
                 InlineKeyboardButton("🔍 Смотреть профили" if lang == 'ru' else "🔍 Browse Profiles", callback_data="browse_profiles")]
            ])
        else:
            # Show message at top, profile below, NO username revealed for non-mutual likes
            if lang == 'en':
                message_header = f"💌 Message from {sender_name}:\n\n\"{message_text}\"\n\n"
                text = f"{message_header}👤 *{sender_name}*, {sender.get('age', '?')} years old\n"
                text += f"📍 *{sender.get('city', 'Unknown')}*\n"
            else:
                message_header = f"💌 Сообщение от {sender_name}:\n\n\"{message_text}\"\n\n"
                text = f"{message_header}👤 *{sender_name}*, {sender.get('age', '?')} лет\n"
                text += f"📍 *{sender.get('city', 'Неизвестно')}*\n"
            
            # Add ND traits if available
            nd_traits = sender.get('nd_traits', [])
            if nd_traits:
                traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
                trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
                if trait_names:
                    text += f"🧠 ND: *{', '.join(trait_names)}*\n"
            
            bio = sender.get('bio', '')
            if bio and len(bio) > 100:
                bio = bio[:100] + "..."
            text += f"\n💭 {bio}"

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❤️ Лайк назад" if lang == 'ru' else "❤️ Like Back", callback_data=f"like_back_{sender['user_id']}")],
                [InlineKeyboardButton("👎 Пропустить" if lang == 'ru' else "👎 Skip", callback_data=f"decline_like_{sender['user_id']}")]
            ])

        # Send with sender's photo if available
        photos = sender.get('photos', [])
        if photos:
            try:
                await bot.send_photo(
                    chat_id=target_id,
                    photo=photos[0],
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
            except Exception:
                await bot.send_message(
                    chat_id=target_id,
                    text=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
        else:
            await bot.send_message(
                chat_id=target_id,
                text=text,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
        logger.info(f"Message with profile sent from {sender['user_id']} to {target_id}")
        
    except Exception as e:
        logger.error(f"Error sending message with profile: {e}")

async def send_like_notification(user_id, application, sender_id=None):
    """Send notification about new like"""
    try:
        user = db.get(Query().user_id == user_id)
        if not user:
            logger.warning(f"User {user_id} not found for like notification")
            return

        lang = user.get('lang', 'ru')
        
        # Get sender info if provided
        sender_name = "Кто-то"
        if sender_id:
            sender = db.get(Query().user_id == sender_id)
            if sender:
                sender_name = sender.get('name', 'Кто-то')

        if lang == 'en':
            text = f"❤️ {sender_name} liked your profile!"
            button_text = "View Likes"
        else:
            text = f"❤️ {sender_name} лайкнул вашу анкету!"
            button_text = "Посмотреть лайки"

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(button_text, callback_data="my_likes")
        ]])

        await application.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=None  # Avoid parse mode issues
        )
        logger.info(f"Like notification sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending like notification to {user_id}: {e}")
        # Don't re-raise the exception as this shouldn't block the like process

async def show_incoming_profile(query, user_id, target_id):
    """Show profile of someone who liked you"""
    try:
        current_user = db.get(Query().user_id == user_id)
        target_user = db.get(Query().user_id == target_id)
        
        if not current_user or not target_user:
            await safe_edit_message(
                query,
                "❌ Пользователь не найден",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")
                ]])
            )
            return
            
        lang = current_user.get('lang', 'ru')
        
        # Get user's name and username
        target_name = target_user['name']
        target_username = target_user.get('username', '')
        
        # Format profile
        profile_text = f"💕 {target_name} лайкнул вас!\n\n"
        if target_username:
            profile_text += f"👤 *{target_name}* (@{target_username}), {target_user['age']} лет\n"
        else:
            profile_text += f"👤 *{target_name}*, {target_user['age']} лет\n"
            
        profile_text += f"📍 *{target_user['city']}*\n"
        
        # Add ND traits if available
        nd_traits = target_user.get('nd_traits', [])
        if nd_traits:
            traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 ND: *{', '.join(trait_names)}*\n"
        
        profile_text += f"\n💭 {target_user['bio']}"

        # Simple response buttons - like back or skip
        keyboard = [
            [
                InlineKeyboardButton("❤️ Лайк назад", callback_data=f"like_back_{target_id}"),
                InlineKeyboardButton("👎 Пропустить", callback_data=f"decline_like_{target_id}")
            ],
            [InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")]
        ]

        # Send with photo if available
        photos = target_user.get('photos', [])
        if photos:
            try:
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                await query.delete_message()
            except Exception:
                await safe_edit_message(
                    query,
                    profile_text,
                    InlineKeyboardMarkup(keyboard)
                )
        else:
            await safe_edit_message(
                query,
                profile_text,
                InlineKeyboardMarkup(keyboard)
            )
            
    except Exception as e:
        logger.error(f"Error showing incoming profile: {e}")
        await safe_edit_message(
            query,
            "❌ Ошибка при загрузке профиля",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")
            ]])
        )

async def handle_decline_like(query, user_id, target_id):
    """Handle declining someone's like"""
    try:
        current_user = db.get(Query().user_id == user_id)
        if not current_user:
            return

        # Add to declined likes so they don't show up again - ATOMIC
        def atomic_decline_browse_add(doc):
            declined_likes = doc.get('declined_likes', [])
            if target_id not in declined_likes:
                declined_likes.append(target_id)
            return {**doc, 'declined_likes': declined_likes}
        
        db.update(atomic_decline_browse_add, Query().user_id == user_id)

        lang = current_user.get('lang', 'ru')
        
        if lang == 'en':
            skip_text = "👎 Skipped"
            continue_text = "Continue browsing"
            menu_text = "🏠 Main Menu"
        else:
            skip_text = "👎 Пропущено"
            continue_text = "Продолжить просмотр"
            menu_text = "🏠 Главное меню"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(continue_text, callback_data="browse_profiles")],
            [InlineKeyboardButton(menu_text, callback_data="back_to_menu")]
        ])

        # Try to edit message text first, if it fails try caption, if both fail send new message
        try:
            await query.edit_message_text(skip_text, reply_markup=keyboard)
        except Exception:
            try:
                await query.edit_message_caption(caption=skip_text, reply_markup=keyboard)
            except Exception:
                await query.message.reply_text(skip_text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error declining like: {e}")
        # Fallback with same approach
        fallback_text = "✅ Пропущено"
        fallback_keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_menu")
        ]])
        
        try:
            await query.edit_message_text(fallback_text, reply_markup=fallback_keyboard)
        except Exception:
            try:
                await query.edit_message_caption(caption=fallback_text, reply_markup=fallback_keyboard)
            except Exception:
                await query.message.reply_text(fallback_text, reply_markup=fallback_keyboard)

async def handle_like_back(query, context, user_id, target_id):
    """Handle liking back someone who liked you"""
    try:
        current_user = db.get(Query().user_id == user_id)
        target_user = db.get(Query().user_id == target_id)

        if not current_user or not target_user:
            # Try to edit message text first, if it fails try caption, if both fail send new message
            error_text = "❌ Пользователь не найден"
            error_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")
            ]])
            
            try:
                await query.edit_message_text(error_text, reply_markup=error_keyboard)
            except Exception:
                try:
                    await query.edit_message_caption(caption=error_text, reply_markup=error_keyboard)
                except Exception:
                    await query.message.reply_text(error_text, reply_markup=error_keyboard)
            return

        # Check if they actually liked us first
        received_likes = current_user.get('received_likes', [])
        if target_id not in received_likes:
            error_text = "❌ Этот пользователь не лайкал вас"
            error_keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К лайкам", callback_data="my_likes")
            ]])
            
            try:
                await query.edit_message_text(error_text, reply_markup=error_keyboard)
            except Exception:
                try:
                    await query.edit_message_caption(caption=error_text, reply_markup=error_keyboard)
                except Exception:
                    await query.message.reply_text(error_text, reply_markup=error_keyboard)
            return

        # Add our like back
        await add_like(user_id, target_id)

        # Show full target profile with hyperlinked name for mutual match
        lang = current_user.get('lang', 'ru')
        target_name = target_user.get('name', 'Пользователь')
        target_username = target_user.get('username', '')
        
        # Create hyperlinked name if username exists
        if target_username:
            profile_text = f"🎉 Взаимный лайк!\n\n👤 [{target_name}](https://t.me/{target_username}), {target_user.get('age', '?')} лет\n"
        else:
            profile_text = f"🎉 Взаимный лайк!\n\n👤 *{target_name}*, {target_user.get('age', '?')} лет\n"
        
        profile_text += f"📍 *{target_user.get('city', 'Неизвестно')}*\n"
        
        # Add ND traits and symptoms
        nd_traits = target_user.get('nd_traits', [])
        nd_symptoms = target_user.get('nd_symptoms', [])

        if nd_traits:
            traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 {get_text(user_id, 'nd_traits')}: *{', '.join(trait_names)}*\n"

        if nd_symptoms:
            symptoms_dict = ND_SYMPTOMS.get(lang, ND_SYMPTOMS['ru'])
            symptom_names = [symptoms_dict.get(symptom, symptom) for symptom in nd_symptoms if symptom in symptoms_dict]
            if symptom_names:
                profile_text += f"🔍 {get_text(user_id, 'nd_characteristics_label')}: *{', '.join(symptom_names[:3])}"
                if len(symptom_names) > 3:
                    profile_text += f"{get_text(user_id, 'and_more')}{len(symptom_names) - 3}"
                profile_text += "*\n"
        
        profile_text += f"\n💭 {target_user.get('bio', '')}\n"
        profile_text += f"\n✨ Теперь вы можете общаться напрямую в Telegram!"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💌 Мои лайки" if lang == 'ru' else "💌 My Likes", callback_data="my_likes")],
            [InlineKeyboardButton("🔍 Смотреть профили" if lang == 'ru' else "🔍 Browse Profiles", callback_data="browse_profiles")]
        ])
        
        text = profile_text

        # Send full profile with photo if available - as new message for better display
        photos = target_user.get('photos', [])
        if photos:
            try:
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                await query.delete_message()
            except Exception:
                # Fallback to text message
                await query.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
                await query.delete_message()
        else:
            # No photo, send text message
            try:
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            except Exception:
                await query.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
        # Send mutual match notification to the other user
        try:
            await send_mutual_match_notification(target_id, context.application, current_user)
        except Exception as notification_error:
            logger.error(f"Failed to send mutual match notification: {notification_error}")

    except Exception as e:
        logger.error(f"Error in handle_like_back: {e}")
        await safe_edit_message(
            query,
            "✅ Лайк отправлен! Теперь у вас взаимный лайк!",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("💌 Мои лайки", callback_data="my_likes"),
                InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")
            ]])
        )



async def handle_decline_like(query, user_id, target_id):
    """Handle declining a like from someone - ATOMIC operation to prevent race conditions"""
    try:
        def atomic_decline_update(doc):
            """Atomic callback to safely decline a like"""
            declined_likes = doc.get('declined_likes', [])
            received_likes = doc.get('received_likes', [])
            
            # Add to declined if not already there
            if target_id not in declined_likes:
                declined_likes.append(target_id)
                
            # Remove from received if present  
            if target_id in received_likes:
                received_likes.remove(target_id)
                
            return {
                **doc,
                'declined_likes': declined_likes,
                'received_likes': received_likes
            }

        # Perform atomic update
        updated = db.update(atomic_decline_update, Query().user_id == user_id)
        if not updated:
            await query.answer("❌ Ошибка")
            return

        await query.edit_message_text(
            "👎 Пропущено",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")]
            ])
        )

    except Exception as e:
        logger.error(f"Error in handle_decline_like: {e}")
        await query.answer("❌ Ошибка")

async def handle_like_incoming_profile(query, context, user_id, target_id):
    """Handle liking back someone from incoming likes"""
    try:
        current_user = db.get(Query().user_id == user_id)
        target_user = db.get(Query().user_id == target_id)

        if not current_user or not target_user:
            await safe_edit_message(
                query,
                "❌ Пользователь не найден",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
                ]])
            )
            return

        # Check if they actually liked us first
        received_likes = current_user.get('received_likes', [])
        if target_id not in received_likes:
            await safe_edit_message(
                query,
                "❌ Этот пользователь не лайкал вас",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="back_to_menu")
                ]])
            )
            return

        # Add our like back
        await add_like(user_id, target_id)

        # Show mutual match confirmation
        await safe_edit_message(
            query,
            "🎉 Взаимный лайк! Соединение установлено!",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭️ Далее", callback_data="next_incoming_like")
            ]])
        )
        
        # Send mutual match notification to the other user
        try:
            await send_mutual_match_notification(target_id, context.application, current_user)
        except Exception as notification_error:
            logger.error(f"Failed to send mutual match notification: {notification_error}")

        # Wait a moment before showing next profile
        await asyncio.sleep(2)
        await show_next_incoming_like(query, context, user_id)

    except Exception as e:
        logger.error(f"Error in handle_like_incoming_profile: {e}")
        await safe_edit_message(
            query,
            "✅ Лайк отправлен! Теперь у вас взаимный лайк!",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭️ Далее", callback_data="next_incoming_like"),
                InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")
            ]])
        )

async def handle_pass_incoming_profile(query, context, user_id, target_id):
    """Handle passing someone from incoming likes - ATOMIC operation"""
    try:
        def atomic_pass_update(doc):
            declined_likes = doc.get('declined_likes', [])
            if target_id not in declined_likes:
                declined_likes.append(target_id)
            return {**doc, 'declined_likes': declined_likes}
        
        # Perform atomic update
        updated = db.update(atomic_pass_update, Query().user_id == user_id)
        if not updated:
            return

        await safe_edit_message(
            query,
            "👎 Пропущено",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("⏭️ Далее", callback_data="next_incoming_like")
            ]])
        )

        # Wait a moment before showing next profile
        await asyncio.sleep(1)
        await show_next_incoming_like(query, context, user_id)

    except Exception as e:
        logger.error(f"Error passing incoming profile: {e}")
        await show_next_incoming_like(query, context, user_id)

async def show_next_incoming_like(query, context, user_id):
    """Show next incoming like profile"""
    incoming_likes = context.user_data.get('browsing_incoming_likes', [])
    current_index = context.user_data.get('current_incoming_index', 0)

    if current_index + 1 < len(incoming_likes):
        context.user_data['current_incoming_index'] = current_index + 1
        next_profile = incoming_likes[current_index + 1]
        await show_incoming_like_card(query, context, user_id, next_profile)
    else:
        # No more incoming likes
        await safe_edit_message(
            query,
            "Больше нет новых лайков.",
            InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")
            ]])
        )
        # Clear the browsing context
        context.user_data.pop('browsing_incoming_likes', None)
        context.user_data.pop('current_incoming_index', None)

async def show_detailed_match_profile(query, user_id, target_id):
    """Show detailed profile of matched user with clickable Telegram username"""
    try:
        current_user = db.get(Query().user_id == user_id)
        target_user = db.get(Query().user_id == target_id)
        
        if not current_user or not target_user:
            await safe_edit_message(
                query,
                "❌ Пользователь не найден",
                InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="my_likes")
                ]])
            )
            return
            
        lang = current_user.get('lang', 'ru')
        
        # Get user's name and username
        target_name = target_user['name']
        target_username = target_user.get('username', '')
        
        # Format detailed profile with clickable username if available
        profile_text = f"💕 Профиль совпадения\n\n"
        if target_username:
            profile_text += f"👤 *{target_name}* (@{target_username}), {target_user['age']} лет\n"
        else:
            profile_text += f"👤 *{target_name}*, {target_user['age']} лет\n"
            
        profile_text += f"📍 *{target_user['city']}*\n"
        
        # Add ND traits and symptoms
        nd_traits = target_user.get('nd_traits', [])
        nd_symptoms = target_user.get('nd_symptoms', [])

        if nd_traits:
            traits_dict = ND_TRAITS.get(lang, ND_TRAITS['ru'])
            trait_names = [traits_dict.get(trait, trait) for trait in nd_traits if trait in traits_dict and trait != 'none']
            if trait_names:
                profile_text += f"🧠 {get_text(user_id, 'nd_traits')}: *{', '.join(trait_names)}*\n"

        if nd_symptoms:
            symptoms_dict = ND_SYMPTOMS.get(lang, ND_SYMPTOMS['ru'])
            symptom_names = [symptoms_dict.get(symptom, symptom) for symptom in nd_symptoms if symptom in symptoms_dict]
            if symptom_names:
                profile_text += f"🔍 {get_text(user_id, 'nd_characteristics_label')}: *{', '.join(symptom_names[:3])}"
                if len(symptom_names) > 3:
                    profile_text += f"{get_text(user_id, 'and_more')}{len(symptom_names) - 3}"
                profile_text += "*\n"
        
        profile_text += f"\n💭 {target_user['bio']}\n"
        profile_text += f"\n✨ Вы понравились друг другу!"

        # Simplified buttons without crossed ones - users can contact directly via usernames
        keyboard = [
            [InlineKeyboardButton("💌 Мои лайки", callback_data="my_likes"),
             InlineKeyboardButton("🏠 В меню", callback_data="back_to_menu")]
        ]

        # Send with all photos if available
        photos = target_user.get('photos', [])
        if photos and len(photos) > 1:
            try:
                # Send as media group for multiple photos
                media_group = []
                for i, photo_id in enumerate(photos[:3]):  # Max 3 photos
                    if i == 0:
                        media_group.append(InputMediaPhoto(media=photo_id, caption=profile_text, parse_mode='Markdown'))
                    else:
                        media_group.append(InputMediaPhoto(media=photo_id))
                
                await query.message.reply_media_group(media=media_group)
                await query.message.reply_text("👆 Профиль совпадения", reply_markup=InlineKeyboardMarkup(keyboard))
                await query.delete_message()
            except Exception as e:
                logger.error(f"Error sending media group: {e}")
                # Fallback to single photo
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                await query.delete_message()
        elif photos:
            try:
                await query.message.reply_photo(
                    photo=photos[0],
                    caption=profile_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode='Markdown'
                )
                await query.delete_message()
            except Exception:
                await safe_edit_message(
                    query,
                    profile_text,
                    InlineKeyboardMarkup(keyboard)
                )
        else:
            await safe_edit_message(
                query,
                profile_text,
                InlineKeyboardMarkup(keyboard)
            )
            
    except Exception as e:
        logger.error(f"Error showing detailed match profile: {e}")
        await safe_edit_message(
            query,
            "❌ Ошибка при загрузке профиля",
            InlineKeyboardMarkup([[
                InlineKeyboardButton(get_text(user_id, "back_button"), callback_data="my_likes")
            ]])
        )

async def send_browsing_interruption(user_id, application):
    """Send special notification if user is currently browsing profiles"""
    try:
        user = db.get_user(user_id)
        if not user:
            return

        lang = user.get('lang', 'ru')
        
        if lang == 'en':
            text = "💕 Someone liked you while you were browsing! Check your likes."
        else:
            text = "💕 Кто-то лайкнул вас пока вы смотрели анкеты! Проверьте лайки."

        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("💌 Мои лайки" if lang == 'ru' else "💌 My Likes", callback_data="my_likes")
        ]])

        await application.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error sending browsing interruption: {e}")

def main():
    """Main function to run the bot"""
    from telegram.request import HTTPXRequest
    from telegram import BotCommand
    from telegram.error import Conflict
    import signal
    import sys
    
    # Signal handler for graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal, stopping bot...")
        if lock_file:
            try:
                lock_file.close()
                if os.path.exists(lock_file_path):
                    os.remove(lock_file_path)
                logger.info("Lock file cleaned up")
            except:
                pass
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create process lock to prevent multiple instances
    lock_file = None
    lock_file_path = '/tmp/alt3r_bot.lock'
    
    try:
        # Force cleanup of any existing lock file first
        if os.path.exists(lock_file_path):
            logger.info("Found existing lock file, removing it...")
            try:
                os.remove(lock_file_path)
            except OSError as e:
                logger.warning(f"Could not remove existing lock file: {e}")
        
        # Create new lock file
        lock_file = open(lock_file_path, 'w')
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            logger.error("Could not acquire file lock - another instance might be running")
            lock_file.close()
            sys.exit(1)
            
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        
        def cleanup_lock():
            if lock_file:
                try:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)  # Explicitly unlock
                    lock_file.close()
                    if os.path.exists(lock_file_path):
                        os.remove(lock_file_path)
                    logger.info("Lock file cleaned up successfully")
                except Exception as e:
                    logger.warning(f"Error cleaning up lock file: {e}")
        
        atexit.register(cleanup_lock)
        logger.info("Process lock acquired successfully")
        
    except (IOError, OSError) as e:
        logger.error(f"Cannot acquire lock: {e}")
        sys.exit(1)
    
    # Configure request with better timeout and retry settings
    request = HTTPXRequest(
        connection_pool_size=1,
        pool_timeout=10.0,
        read_timeout=10.0,
        write_timeout=10.0,
        connect_timeout=10.0
    )
    
    application = ApplicationBuilder().token(TOKEN).request(request).build()
    
    # Set bot commands
    async def post_init(application):
        commands = [
            BotCommand("start", "🔄 Перезапустить бота / Restart the bot"),
            BotCommand("language", "🌐 Изменить язык / Change Language"),
            BotCommand("help", "❓ Помощь / Help")
        ]
        await application.bot.set_my_commands(commands)
    
    application.post_init = post_init

    # Conversation handler for profile creation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender)],
            INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interest)],
            CITY: [
                MessageHandler(filters.LOCATION, handle_city),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city)
            ],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bio)],
            PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.VIDEO, handle_photo),
                MessageHandler(filters.VIDEO_NOTE, handle_photo),
                MessageHandler(filters.ANIMATION, handle_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_photo)
            ],
            WAITING_NAME: [
                CallbackQueryHandler(handle_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("restart", restart))
    
    application.add_handler(CommandHandler("language", show_language_command))
    application.add_handler(CommandHandler("help", show_help_command))
    application.add_handler(CommandHandler("debug", debug_profiles))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    # Start keep-alive server
    start_keep_alive()

    # Run the bot
    logger.info("Starting Alt3r bot...")
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.info(f"Attempt {retry_count + 1}/{max_retries} to start bot...")
            # Add polling timeout to reduce API call frequency
            application.run_polling(
                drop_pending_updates=True,
                timeout=15,  # Wait up to 15 seconds for new updates
                poll_interval=2.0  # Wait 2 seconds between polling attempts
            )
            break
        except Conflict as e:
            retry_count += 1
            logger.warning(f"Bot conflict detected (attempt {retry_count}): {e}")
            if retry_count < max_retries:
                logger.info("Waiting 5 seconds before retry...")
                import time
                time.sleep(5)
            else:
                logger.error("Max retries reached. Another bot instance may be running.")
                # Clean up lock file before exiting
                if lock_file:
                    try:
                        lock_file.close()
                        if os.path.exists(lock_file_path):
                            os.remove(lock_file_path)
                    except:
                        pass
                sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Bot crashed with unexpected error: {e}")
            import traceback
            traceback.print_exc()
            # Clean up lock file before exiting
            if lock_file:
                try:
                    lock_file.close()
                    if os.path.exists(lock_file_path):
                        os.remove(lock_file_path)
                except:
                    pass
            sys.exit(1)
    
    # Final cleanup
    if lock_file:
        try:
            lock_file.close()
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)
            logger.info("Bot shutdown complete")
        except:
            pass

if __name__ == "__main__":
    main()