"""
Telegram bot handlers for Alt3r Bot
Contains all message and callback handlers for the neurodivergent dating bot.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from database import get_user_by_id, save_user_data, get_potential_matches, update_user_likes
from translations import get_text, get_available_languages

# ===== CONVERSATION STATES =====
(AGE, GENDER, INTEREST, CITY, NAME, BIO, PHOTO, CONFIRM, 
 WAITING_MESSAGE, WAITING_MEDIA, FEEDBACK_TEXT, WAITING_NAME, 
 WAITING_AGE, WAITING_CITY, WAITING_INTEREST_CHANGE, SENDING_MESSAGE, 
 SENDING_VIDEO) = range(17)

# ===== REGISTRATION HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler - entry point for new users."""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    
    # Check if user exists and has complete profile
    user = get_user_by_id(user_id)
    
    if user and user.profile_complete is True:
        # Existing user with complete profile - show main menu
        await show_main_menu(update, context)
    else:
        # New user or incomplete profile - start language selection
        languages = get_available_languages()
        keyboard = []
        for lang in languages:
            keyboard.append([InlineKeyboardButton(lang['name'], callback_data=f"lang_{lang['code']}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🌐 Choose your language / Выберите язык:",
            reply_markup=reply_markup
        )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection during onboarding."""
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
    """Handle age input during registration."""
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
    """Handle gender selection during registration."""
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
    """Handle interest selection during registration."""
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
    """Handle city input during registration."""
    if not update.effective_user or not update.message:
        return CITY
        
    user_id = update.effective_user.id
    
    if update.message.location:
        # User shared location
        location = update.message.location
        context.user_data['city'] = f"Location: {location.latitude}, {location.longitude}"
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
    """Handle name input during registration."""
    if not update.effective_user or not update.message or not update.message.text:
        return NAME
        
    user_id = update.effective_user.id
    context.user_data['name'] = update.message.text
    
    # Ask for bio
    bio_text = get_text(user_id, 'questionnaire_bio')
    await update.message.reply_text(bio_text)
    return BIO

async def bio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bio input during registration."""
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
    """Handle photo upload during registration."""
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
    """Show profile confirmation screen."""
    if not update.effective_user:
        return
        
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
    """Handle profile confirmation callback."""
    if not update.callback_query or not update.effective_user or not update.callback_query.data:
        return ConversationHandler.END
        
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "confirm_yes":
        # Save profile to database
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

# ===== MAIN MENU HANDLERS =====

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the main menu to users with complete profiles."""
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
    """Show main menu from a callback query (for inline updates)."""
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
    """Handle main menu button callbacks."""
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

# ===== PROFILE BROWSING HANDLERS =====

async def show_my_profile(query, context: ContextTypes.DEFAULT_TYPE):
    """Display the user's own profile."""
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
    """Start browsing other user profiles."""
    user_id = query.from_user.id
    
    # Get potential matches from database
    potential_matches = get_potential_matches(user_id)
    
    if not potential_matches:
        await query.edit_message_text(get_text(user_id, 'no_profiles'))
        return
    
    # Store matches in context and show first profile
    context.user_data['browsing_profiles'] = potential_matches
    context.user_data['current_profile_index'] = 0
    
    await show_profile_for_browsing(query, context, potential_matches[0])

async def show_profile_for_browsing(query, context: ContextTypes.DEFAULT_TYPE, profile_user):
    """Display a profile for browsing with like/pass options."""
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
    """Handle like/pass actions on profiles."""
    if not update.callback_query or not update.callback_query.from_user or not update.callback_query.data:
        return
        
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    action, target_user_id = query.data.split('_', 1)
    target_user_id = int(target_user_id)
    
    if action == "like":
        # Process the like using database function
        result = update_user_likes(user_id, target_user_id)
        
        if result['success']:
            if result['is_match']:
                await query.edit_message_text(get_text(user_id, 'its_match'))
                return
            else:
                await query.edit_message_text(get_text(user_id, 'like_sent'))
        else:
            await query.edit_message_text("Error processing like.")
            return
    else:
        # Pass action
        await query.edit_message_text(get_text(user_id, 'skip_profile'))
    
    # Show next profile or return to menu
    await show_next_profile_or_menu(query, context)

async def show_next_profile_or_menu(query, context: ContextTypes.DEFAULT_TYPE):
    """Show next profile in queue or return to main menu if no more profiles."""
    profiles = context.user_data.get('browsing_profiles', [])
    current_index = context.user_data.get('current_profile_index', 0)
    
    if current_index + 1 < len(profiles):
        # Show next profile
        context.user_data['current_profile_index'] = current_index + 1
        next_profile = profiles[current_index + 1]
        await show_profile_for_browsing(query, context, next_profile)
    else:
        # No more profiles, return to main menu
        await show_main_menu_from_callback(query, context)

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle back to menu button clicks."""
    if not update.callback_query:
        return
        
    query = update.callback_query
    await query.answer()
    
    await show_main_menu_from_callback(query, context)