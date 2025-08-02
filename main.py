#!/usr/bin/env python3
"""
Alt3r - Neurodivergent Dating Bot
Main entry point for the bot application.

This is a specialized Telegram dating bot designed for neurodivergent individuals,
providing comprehensive trait matching, AI assistance, and bilingual support.
"""

import os
import logging
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv

# Import modular components
from keep_alive import start_keep_alive
from database import User, Feedback
from handlers import (
    start, language_callback, age_handler, gender_handler, interest_handler,
    city_handler, name_handler, bio_handler, photo_handler, confirm_callback,
    menu_callback, like_pass_callback, back_to_menu_callback,
    AGE, GENDER, INTEREST, CITY, NAME, BIO, PHOTO, CONFIRM
)

# Load environment variables
load_dotenv()

# ===== LOGGING SETUP =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== CONFIGURATION =====
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable not set")
    print("Please provide TELEGRAM_BOT_TOKEN environment variable")
    exit(1)

# ===== MAIN APPLICATION =====

def main():
    """Main function to run the Alt3r bot."""
    logger.info("Starting Alt3r bot initialization...")
    
    # Start keep-alive service for hosting platforms
    start_keep_alive()
    
    # Create Telegram application
    application = Application.builder().token(TOKEN).build()
    
    # ===== CONVERSATION HANDLER =====
    # Registration flow for new users
    registration_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age_handler)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_handler)],
            INTEREST: [MessageHandler(filters.TEXT & ~filters.COMMAND, interest_handler)],
            CITY: [MessageHandler((filters.TEXT | filters.LOCATION) & ~filters.COMMAND, city_handler)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_handler)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio_handler)],
            PHOTO: [MessageHandler((filters.PHOTO | filters.VIDEO | filters.TEXT) & ~filters.COMMAND, photo_handler)],
            CONFIRM: [CallbackQueryHandler(confirm_callback, pattern="^confirm_")]
        },
        fallbacks=[CommandHandler('start', start)],
        per_message=False,
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )
    
    # ===== CALLBACK HANDLERS =====
    # Language selection during onboarding
    language_handler = CallbackQueryHandler(language_callback, pattern="^lang_")
    
    # Main menu navigation
    menu_handler = CallbackQueryHandler(menu_callback, pattern="^menu_")
    
    # Profile interactions (like/pass)
    interaction_handler = CallbackQueryHandler(like_pass_callback, pattern="^(like|pass)_")
    
    # Navigation callbacks
    navigation_handler = CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$")
    
    # ===== REGISTER HANDLERS =====
    # Order matters: more specific patterns should come first
    application.add_handler(registration_handler)
    application.add_handler(language_handler)
    application.add_handler(menu_handler)
    application.add_handler(interaction_handler)
    application.add_handler(navigation_handler)
    
    # ===== START BOT =====
    logger.info("Alt3r bot started successfully! Listening for updates...")
    
    # Run the bot with polling
    application.run_polling(
        allowed_updates=['message', 'callback_query'],
        drop_pending_updates=True
    )

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed with error: {e}")
        raise