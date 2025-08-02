#!/usr/bin/env python3
"""
Alt3r - Neurodivergent Dating Bot
A Telegram bot for connecting neurodivergent individuals

Main entry point for the bot application.
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, ContextTypes, CommandHandler, 
    MessageHandler, CallbackQueryHandler, ConversationHandler, filters
)
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

# Import modules
from keep_alive import start_keep_alive

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token validation
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
    print("Please provide TELEGRAM_BOT_TOKEN environment variable")
    exit(1)

# Import modular components
from database import User, Feedback, get_db_session, get_user_by_id, save_user_data
from translations import get_text, TEXTS, ND_TRAITS
from handlers import (
    start, language_callback, age_handler, gender_handler, interest_handler,
    city_handler, name_handler, bio_handler, photo_handler, confirm_callback,
    menu_callback, like_pass_callback, back_to_menu_callback,
    AGE, GENDER, INTEREST, CITY, NAME, BIO, PHOTO, CONFIRM
)

# Database connection
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
        "questionnaire_age": "Сколько вам лет?",
        "questionnaire_gender": "Ваш пол?",
        "questionnaire_interest": "Кто вас интересует?",
        "questionnaire_city": "📍 Поделитесь вашим местоположением или введите город:",
        "questionnaire_name": "Как к вам обращаться?",
        "questionnaire_bio": "Расскажите о себе и о том, кого хотите найти. Это поможет лучше подобрать совпадения.",
        "questionnaire_photo": "Теперь отправьте до 3 фото или запишите видео 👍 (до 15 сек)",
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
        "invalid_age": "❌ Пожалуйста, введите корректный возраст (18-100)"
    },
    "en": {
        "welcome": "🧠 Welcome to Alt3r!\n\nThis is a dating bot for neurodivergent people. Here you can find understanding, support and real connections with those who share your experience.\n\n✨ Let's create your profile!",
        "main_menu": "🏠 Main Menu",
        "profile_menu_0": "👤 My Profile",
        "profile_menu_1": "👀 Browse Profiles",
        "profile_menu_2": "🧠 Neurosearch",
        "profile_menu_3": "📸 Change Photo/Video",
        "profile_menu_4": "✍️ Change Description",
        "profile_menu_5": "💌 My Likes",
        "profile_menu_6": "⚙️ Profile Settings",
        "profile_menu_7": "📝 Feedback",
        "profile_menu_8": "📊 Statistics",
        "language_menu": "🌐 Language",
        "choose_language": "🌐 Choose language:",
        "language_set_ru": "✅ Language set: Русский",
        "language_set_en": "✅ Language set: English",
        "questionnaire_age": "How old are you?",
        "questionnaire_gender": "What's your gender?",
        "questionnaire_interest": "Who are you interested in?",
        "questionnaire_city": "📍 Share your location or enter your city:",
        "questionnaire_name": "What should we call you?",
        "questionnaire_bio": "Tell about yourself and who you're looking for. This helps with better matching.",
        "questionnaire_photo": "Now send up to 3 photos or record a video 👍 (up to 15 sec)",
        "profile_preview": "Here's how your profile looks:",
        "profile_correct": "Is everything correct?",
        "btn_girls": "Girls",
        "btn_boys": "Boys",
        "btn_all": "Anyone",
        "btn_girl": "Girl",
        "btn_boy": "Boy",
        "btn_yes": "✅ Yes",
        "btn_change": "🔄 Change",
        "btn_skip": "⏭️ Skip",
        "years_old": "years old",
        "seeking": "seeking",
        "city": "City:",
        "about_me": "About me:",
        "ready_to_connect": "Ready to connect!",
        "profile_saved": "✅ Profile saved! Welcome to Alt3r!",
        "no_profiles": "😕 No profiles available right now. Try again later!",
        "like_sent": "❤️ Like sent!",
        "skip_profile": "⏭️ Skipped",
        "its_match": "🎉 It's a match!\n\nYou can message each other:",
        "new_like": "❤️ Someone liked you!",
        "photo_updated": "✅ Photo updated!",
        "bio_updated": "✅ Description updated!",
        "send_message": "💌 Send Message",
        "back_to_menu": "🏠 Back to Menu",
        "message_sent": "✅ Message sent!",
        "invalid_age": "❌ Please enter a valid age (18-100)"
    }
}

def get_db_session():
    """Get database session"""
    return SessionLocal()

def get_user_language(user_id):
    """Get user's language preference"""
    with get_db_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user and user.language:
            return user.language
        return 'en'

def get_text(user_id, key):
    """Get localized text for user"""
    lang = get_user_language(user_id)
    return TEXTS[lang].get(key, TEXTS['en'].get(key, key))

def get_user_by_id(user_id):
    """Get user by user_id"""
    with get_db_session() as session:
        return session.query(User).filter(User.user_id == user_id).first()

def save_user_data(user_id, data):
    """Save or update user data"""
    with get_db_session() as session:
        user = session.query(User).filter(User.user_id == user_id).first()
        
        if user:
            # Update existing user
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = User(user_id=user_id, **data)
            session.add(user)
        
        session.commit()
        session.refresh(user)
        return user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    
    # Check if user exists
    user = get_user_by_id(user_id)
    
    if user and user.profile_complete is True:
        # User exists and profile is complete - show main menu
        await show_main_menu(update, context)
    else:
        # New user or incomplete profile - start registration
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🌐 Choose your language / Выберите язык:",
            reply_markup=reply_markup
        )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection"""
    if not update.callback_query or not update.effective_user:
        return
        
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not query.data:
        return
        
    language = query.data.split('_')[1]
    
    # Save language preference
    save_user_data(user_id, {'language': language})
    
    # Send welcome message in selected language
    welcome_text = get_text(user_id, 'welcome')
    await query.edit_message_text(welcome_text)
    
    # Start registration process
    context.user_data['step'] = 'age'
    age_text = get_text(user_id, 'questionnaire_age')
    await context.bot.send_message(chat_id=user_id, text=age_text)
    
    return AGE

async def age_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle age input"""
    if not update.effective_user or not update.message or not update.message.text:
        return AGE
        
    user_id = update.effective_user.id
    
    try:
        age = int(update.message.text)
        if 18 <= age <= 100:
            context.user_data['age'] = age
            
            # Ask for gender
            gender_text = get_text(user_id, 'questionnaire_gender')
            keyboard = [
                [KeyboardButton(get_text(user_id, 'btn_girl'))],
                [KeyboardButton(get_text(user_id, 'btn_boy'))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(gender_text, reply_markup=reply_markup)
            return GENDER
        else:
            await update.message.reply_text(get_text(user_id, 'invalid_age'))
            return AGE
    except ValueError:
        await update.message.reply_text(get_text(user_id, 'invalid_age'))
        return AGE

async def gender_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle gender selection"""
    if not update.effective_user or not update.message or not update.message.text:
        return GENDER
        
    user_id = update.effective_user.id
    gender_text = update.message.text
    
    # Map gender text to internal representation
    if gender_text == get_text(user_id, 'btn_girl'):
        context.user_data['gender'] = 'girl'
    elif gender_text == get_text(user_id, 'btn_boy'):
        context.user_data['gender'] = 'boy'
    else:
        # Invalid selection, ask again
        await update.message.reply_text(get_text(user_id, 'questionnaire_gender'))
        return GENDER
    
    # Ask for interest
    interest_text = get_text(user_id, 'questionnaire_interest')
    keyboard = [
        [KeyboardButton(get_text(user_id, 'btn_girls'))],
        [KeyboardButton(get_text(user_id, 'btn_boys'))],
        [KeyboardButton(get_text(user_id, 'btn_all'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(interest_text, reply_markup=reply_markup)
    return INTEREST

async def interest_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interest selection"""
    if not update.effective_user or not update.message or not update.message.text:
        return INTEREST
        
    user_id = update.effective_user.id
    interest_text = update.message.text
    
    # Map interest text to internal representation
    if interest_text == get_text(user_id, 'btn_girls'):
        context.user_data['interest'] = 'girls'
    elif interest_text == get_text(user_id, 'btn_boys'):
        context.user_data['interest'] = 'boys'
    elif interest_text == get_text(user_id, 'btn_all'):
        context.user_data['interest'] = 'all'
    else:
        # Invalid selection, ask again
        await update.message.reply_text(get_text(user_id, 'questionnaire_interest'))
        return INTEREST
    
    # Ask for city
    city_text = get_text(user_id, 'questionnaire_city')
    await update.message.reply_text(city_text, reply_markup=ReplyKeyboardRemove())
    return CITY

async def city_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle city input"""
    if not update.effective_user or not update.message:
        return CITY
        
    user_id = update.effective_user.id
    
    if update.message.location:
        # User shared location
        context.user_data['city'] = f"Location: {update.message.location.latitude}, {update.message.location.longitude}"
    elif update.message.text:
        # User typed city name
        context.user_data['city'] = update.message.text
    else:
        return CITY
    
    # Ask for name
    name_text = get_text(user_id, 'questionnaire_name')
    await update.message.reply_text(name_text)
    return NAME

async def name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name input"""
    if not update.effective_user or not update.message or not update.message.text:
        return NAME
        
    user_id = update.effective_user.id
    context.user_data['name'] = update.message.text
    
    # Ask for bio
    bio_text = get_text(user_id, 'questionnaire_bio')
    await update.message.reply_text(bio_text)
    return BIO

async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bio input"""
    if not update.effective_user or not update.message or not update.message.text:
        return BIO
        
    user_id = update.effective_user.id
    context.user_data['bio'] = update.message.text
    
    # Ask for photo
    photo_text = get_text(user_id, 'questionnaire_photo')
    keyboard = [[KeyboardButton(get_text(user_id, 'btn_skip'))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(photo_text, reply_markup=reply_markup)
    context.user_data['photos'] = []
    return PHOTO

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo upload"""
    if not update.effective_user or not update.message:
        return PHOTO
        
    user_id = update.effective_user.id
    
    if update.message.text and update.message.text == get_text(user_id, 'btn_skip'):
        # User skipped photos
        await confirm_profile(update, context)
        return CONFIRM
    
    if update.message.photo:
        # Get the largest photo
        photo = update.message.photo[-1]
        if 'photos' not in context.user_data:
            context.user_data['photos'] = []
        
        context.user_data['photos'].append(photo.file_id)
        
        if len(context.user_data['photos']) >= 3:
            # Max photos reached
            await confirm_profile(update, context)
            return CONFIRM
        else:
            # Ask for more photos or continue
            keyboard = [
                [KeyboardButton("✅ Done")],
                [KeyboardButton(get_text(user_id, 'btn_skip'))]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(
                f"Photo {len(context.user_data['photos'])}/3 added! Send another or continue:",
                reply_markup=reply_markup
            )
            return PHOTO
    else:
        # Invalid input
        await update.message.reply_text("Please send a photo or skip this step.")
        return PHOTO

async def confirm_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show profile confirmation"""
    user_id = update.effective_user.id
    
    # Build profile preview
    user_data = context.user_data
    name = user_data.get('name', 'Unknown')
    age = user_data.get('age', 0)
    gender = user_data.get('gender', 'unknown')
    interest = user_data.get('interest', 'all')
    city = user_data.get('city', 'Unknown')
    bio = user_data.get('bio', 'No bio')
    
    # Gender display
    gender_display = get_text(user_id, 'btn_girl') if gender == 'girl' else get_text(user_id, 'btn_boy')
    
    # Interest display
    if interest == 'girls':
        interest_display = get_text(user_id, 'btn_girls')
    elif interest == 'boys':
        interest_display = get_text(user_id, 'btn_boys')
    else:
        interest_display = get_text(user_id, 'btn_all')
    
    profile_text = f"""
{get_text(user_id, 'profile_preview')}

👤 {name}, {age} {get_text(user_id, 'years_old')}
{gender_display} {get_text(user_id, 'seeking')} {interest_display}

📍 {get_text(user_id, 'city')} {city}

💭 {get_text(user_id, 'about_me')} {bio}

{get_text(user_id, 'profile_correct')}
"""
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'btn_yes'), callback_data="confirm_yes")],
        [InlineKeyboardButton(get_text(user_id, 'btn_change'), callback_data="confirm_change")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(profile_text, reply_markup=reply_markup)

async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile confirmation"""
    if not update.callback_query or not update.effective_user or not update.callback_query.data:
        return ConversationHandler.END
        
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "confirm_yes":
        # Save profile
        user_data = context.user_data
        profile_data = {
            'name': user_data.get('name'),
            'age': user_data.get('age'),
            'gender': user_data.get('gender'),
            'interest': user_data.get('interest'),
            'city': user_data.get('city'),
            'bio': user_data.get('bio'),
            'photos': user_data.get('photos', []),
            'profile_complete': True,
            'active': True,
            'likes_sent': [],
            'likes_received': [],
            'matches': []
        }
        
        save_user_data(user_id, profile_data)
        
        await query.edit_message_text(get_text(user_id, 'profile_saved'))
        
        # Show main menu
        await show_main_menu_from_callback(query, context)
        
        return ConversationHandler.END
    else:
        # User wants to change something - restart registration
        await query.edit_message_text("Let's start over. Send /start to begin again.")
        return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_0'), callback_data="menu_profile")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_1'), callback_data="menu_browse")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_2'), callback_data="menu_neurosearch")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_3'), callback_data="menu_change_photo")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_4'), callback_data="menu_change_bio")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_5'), callback_data="menu_likes")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_6'), callback_data="menu_settings")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_7'), callback_data="menu_feedback")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_text(user_id, 'main_menu'),
        reply_markup=reply_markup
    )

async def show_main_menu_from_callback(query, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu from callback query"""
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_0'), callback_data="menu_profile")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_1'), callback_data="menu_browse")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_2'), callback_data="menu_neurosearch")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_3'), callback_data="menu_change_photo")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_4'), callback_data="menu_change_bio")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_5'), callback_data="menu_likes")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_6'), callback_data="menu_settings")],
        [InlineKeyboardButton(get_text(user_id, 'profile_menu_7'), callback_data="menu_feedback")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            get_text(user_id, 'main_menu'),
            reply_markup=reply_markup
        )
    except:
        await context.bot.send_message(
            chat_id=user_id,
            text=get_text(user_id, 'main_menu'),
            reply_markup=reply_markup
        )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu callbacks"""
    if not update.callback_query or not update.callback_query.from_user or not update.callback_query.data:
        return
        
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    action = query.data.split('_')[1]
    
    if action == "profile":
        await show_my_profile(query, context)
    elif action == "browse":
        await browse_profiles(query, context)
    elif action == "neurosearch":
        await query.edit_message_text("🧠 Neurosearch feature coming soon!")
    elif action == "change":
        await query.edit_message_text("📸 Photo change feature coming soon!")
    elif action == "bio":
        await query.edit_message_text("✍️ Bio change feature coming soon!")
    elif action == "likes":
        await query.edit_message_text("💌 Likes feature coming soon!")
    elif action == "settings":
        await query.edit_message_text("⚙️ Settings feature coming soon!")
    elif action == "feedback":
        await query.edit_message_text("📝 Feedback feature coming soon!")

async def show_my_profile(query, context: ContextTypes.DEFAULT_TYPE):
    """Show user's own profile"""
    user_id = query.from_user.id
    user = get_user_by_id(user_id)
    
    if not user:
        await query.edit_message_text("Profile not found. Please use /start to create one.")
        return
    
    name = user.name if user.name else 'Unknown'
    age = user.age if user.age else 0
    gender = user.gender if user.gender else 'unknown'
    interest = user.interest if user.interest else 'all'
    city = user.city if user.city else 'Unknown'
    bio = user.bio if user.bio else 'No bio'
    
    # Gender display
    gender_display = get_text(user_id, 'btn_girl') if gender == 'girl' else get_text(user_id, 'btn_boy')
    
    # Interest display
    if interest == 'girls':
        interest_display = get_text(user_id, 'btn_girls')
    elif interest == 'boys':
        interest_display = get_text(user_id, 'btn_boys')
    else:
        interest_display = get_text(user_id, 'btn_all')
    
    profile_text = f"""
👤 {name}, {age} {get_text(user_id, 'years_old')}
{gender_display} {get_text(user_id, 'seeking')} {interest_display}

📍 {get_text(user_id, 'city')} {city}

💭 {get_text(user_id, 'about_me')} {bio}

{get_text(user_id, 'ready_to_connect')}
"""
    
    keyboard = [[InlineKeyboardButton(get_text(user_id, 'back_to_menu'), callback_data="back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(profile_text, reply_markup=reply_markup)

async def browse_profiles(query, context: ContextTypes.DEFAULT_TYPE):
    """Browse other profiles"""
    user_id = query.from_user.id
    current_user = get_user_by_id(user_id)
    
    if not current_user:
        await query.edit_message_text("Profile not found.")
        return
    
    user_interest = current_user.interest if current_user.interest else 'all'
    user_gender = current_user.gender if current_user.gender else 'unknown'
    
    # Find matching profiles
    with get_db_session() as session:
        all_users = session.query(User).filter(
            User.user_id != user_id,
            User.profile_complete.is_(True),
            User.active.is_(True)
        ).all()
    
    potential_matches = []
    
    for user in all_users:
        other_gender = user.gender if user.gender else 'unknown'
        other_interest = user.interest if user.interest else 'all'
        
        # Check compatibility
        compatible = False
        
        if user_interest == 'all' or other_interest == 'all':
            compatible = True
        elif user_interest == 'girls' and other_gender == 'girl':
            if other_interest == 'all' or (other_interest == 'boys' and user_gender == 'boy'):
                compatible = True
        elif user_interest == 'boys' and other_gender == 'boy':
            if other_interest == 'all' or (other_interest == 'girls' and user_gender == 'girl'):
                compatible = True
        
        if compatible:
            potential_matches.append(user)
    
    if not potential_matches:
        await query.edit_message_text(get_text(user_id, 'no_profiles'))
        return
    
    # Show first profile
    context.user_data['browsing_profiles'] = potential_matches
    context.user_data['current_profile_index'] = 0
    
    await show_profile_for_browsing(query, context, potential_matches[0])

async def show_profile_for_browsing(query, context: ContextTypes.DEFAULT_TYPE, profile_user):
    """Show a profile for browsing"""
    user_id = query.from_user.id
    
    name = profile_user.name if profile_user.name else 'Unknown'
    age = profile_user.age if profile_user.age else 0
    gender = profile_user.gender if profile_user.gender else 'unknown'
    city = profile_user.city if profile_user.city else 'Unknown'
    bio = profile_user.bio if profile_user.bio else 'No bio'
    
    # Gender display
    gender_display = get_text(user_id, 'btn_girl') if gender == 'girl' else get_text(user_id, 'btn_boy')
    
    profile_text = f"""
👤 {name}, {age} {get_text(user_id, 'years_old')}
{gender_display}

📍 {get_text(user_id, 'city')} {city}

💭 {get_text(user_id, 'about_me')} {bio}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("❤️", callback_data=f"like_{profile_user.user_id}"),
            InlineKeyboardButton("👎", callback_data=f"pass_{profile_user.user_id}")
        ],
        [InlineKeyboardButton(get_text(user_id, 'back_to_menu'), callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(profile_text, reply_markup=reply_markup)

async def like_pass_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle like/pass actions"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    action, target_user_id = query.data.split('_', 1)
    target_user_id = int(target_user_id)
    
    current_user = get_user_by_id(user_id)
    if not current_user:
        return
    
    if action == "like":
        with get_db_session() as session:
            # Get users
            current_user_db = session.query(User).filter(User.user_id == user_id).first()
            target_user_db = session.query(User).filter(User.user_id == target_user_id).first()
            
            if not current_user_db or not target_user_db:
                return
            
            # Add to likes_sent for current user
            likes_sent = current_user_db.likes_sent or []
            if target_user_id not in likes_sent:
                likes_sent.append(target_user_id)
                current_user_db.likes_sent = likes_sent
            
            # Add to likes_received for target user
            likes_received = target_user_db.likes_received or []
            if user_id not in likes_received:
                likes_received.append(user_id)
                target_user_db.likes_received = likes_received
            
            # Check if it's a match
            target_likes_sent = target_user_db.likes_sent or []
            if user_id in target_likes_sent:
                # It's a match!
                current_matches = current_user_db.matches or []
                if target_user_id not in current_matches:
                    current_matches.append(target_user_id)
                    current_user_db.matches = current_matches
                
                target_matches = target_user_db.matches or []
                if user_id not in target_matches:
                    target_matches.append(user_id)
                    target_user_db.matches = target_matches
                
                session.commit()
                await query.edit_message_text(get_text(user_id, 'its_match'))
                return
            
            session.commit()
        
        await query.edit_message_text(get_text(user_id, 'like_sent'))
    else:
        await query.edit_message_text(get_text(user_id, 'skip_profile'))
    
    # Show next profile or go back to menu
    await show_next_profile_or_menu(query, context)

async def show_next_profile_or_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show next profile or return to menu if no more profiles"""
    profiles = context.user_data.get('browsing_profiles', [])
    current_index = context.user_data.get('current_profile_index', 0)
    
    if current_index + 1 < len(profiles):
        # Show next profile
        context.user_data['current_profile_index'] = current_index + 1
        next_profile = profiles[current_index + 1]
        await show_profile_for_browsing(query, context, next_profile)
    else:
        # No more profiles, go back to menu
        await show_main_menu_from_callback(query, context)

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to menu button"""
    if not update.callback_query:
        return
        
    query = update.callback_query
    await query.answer()
    
    await show_main_menu_from_callback(query, context)

def main():
    """Main function to run the bot"""
    # Start keep-alive service
    start_keep_alive()
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Registration conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_handler)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_handler)],
            INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, interest_handler)],
            CITY: [MessageHandler((filters.TEXT | filters.LOCATION) & ~filters.COMMAND, city_handler)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio_handler)],
            PHOTO: [MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, photo_handler)],
            CONFIRM: [CallbackQueryHandler(confirm_callback, pattern="^confirm_")]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    application.add_handler(CallbackQueryHandler(like_pass_callback, pattern="^(like|pass)_"))
    application.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    
    # Run the bot
    logger.info("Starting Alt3r bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()