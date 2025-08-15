#!/usr/bin/env python3
"""
Script to populate the database with realistic fake profiles for testing.
This script will:
1. Delete all existing profiles
2. Create realistic fake profiles for both men and women
3. Use provided photos for women's profiles
4. Generate diverse neurodivergent traits and bios
"""

import os
import json
import random
from datetime import datetime, timedelta
from database_manager import DatabaseManager
from models import User

# Initialize database manager
db_manager = DatabaseManager()

# Photo file paths for women's profiles (from attached assets)
WOMEN_PHOTOS = [
    "assets/photos/woman1.jpg",  # Woman by river in pink top
    "assets/photos/woman2.jpg",  # Mirror selfie in white top
    "assets/photos/woman3.jpg",  # Autumn outdoor photo
    "assets/photos/woman4.jpg",  # Blonde with glasses
    "assets/photos/woman5.jpg",  # Dark hair with headphones
    "assets/photos/woman6.jpg",  # Night photo in black coat
]

# Realistic names and data
FEMALE_NAMES = [
    "Анна", "Мария", "Елена", "Ольга", "Татьяна", "Наталья", "Светлана", "Ирина",
    "Екатерина", "Юлия", "Людмила", "Галина", "Валентина", "Нина", "Любовь", "Вера",
    "Надежда", "Алина", "Виктория", "Дарья", "Алёна", "Кристина", "Полина", "Анастасия",
    "Софья", "Варвара", "Милана", "Ксения", "Александра", "Арина", "Валерия", "Вероника"
]

MALE_NAMES = [
    "Александр", "Сергей", "Андрей", "Алексей", "Дмитрий", "Максим", "Иван", "Михаил",
    "Владимир", "Николай", "Денис", "Евгений", "Артём", "Игорь", "Роман", "Антон",
    "Кирилл", "Павел", "Олег", "Виталий", "Константин", "Даниил", "Егор", "Вадим",
    "Станислав", "Владислав", "Тимур", "Георгий", "Руслан", "Глеб", "Матвей", "Никита"
]

CITIES_WITH_COORDS = [
    ("Москва", "moscow", 55.7558, 37.6176),
    ("Санкт-Петербург", "st-petersburg", 59.9311, 30.3609),
    ("Новосибирск", "novosibirsk", 55.0084, 82.9357),
    ("Екатеринбург", "yekaterinburg", 56.8431, 60.6454),
    ("Нижний Новгород", "nizhny-novgorod", 56.2965, 43.9361),
    ("Казань", "kazan", 55.8304, 49.0661),
    ("Челябинск", "chelyabinsk", 55.1644, 61.4368),
    ("Омск", "omsk", 54.9885, 73.3242),
    ("Самара", "samara", 53.2001, 50.15),
    ("Ростов-на-Дону", "rostov-on-don", 47.2357, 39.7015),
    ("Уфа", "ufa", 54.7388, 55.9721),
    ("Красноярск", "krasnoyarsk", 56.0184, 92.8672),
    ("Воронеж", "voronezh", 51.6720, 39.1843),
    ("Пермь", "perm", 58.0105, 56.2502),
    ("Волгоград", "volgograd", 48.7080, 44.5133),
    ("Краснодар", "krasnodar", 45.0328, 38.9769),
    ("Саратов", "saratov", 51.5924, 46.0037),
    ("Тюмень", "tyumen", 57.1522, 65.5272),
    ("Тольятти", "tolyatti", 53.5303, 49.3461),
    ("Ижевск", "izhevsk", 56.8527, 53.2041)
]

# Neurodivergent traits available in the system
ND_TRAITS = [
    "adhd", "autism", "anxiety", "depression", "bipolar", "ocd", "ptsd", 
    "dyslexia", "dyscalculia", "dyspraxia", "tourettes", "sensory_processing",
    "executive_dysfunction", "rejection_sensitivity", "hyperfocus", 
    "stimming", "social_anxiety", "perfectionism"
]

# Bio templates for different personalities (in Russian)
BIO_TEMPLATES = {
    "creative": [
        "Творческая душа, которая находит красоту в обычных моментах. Люблю создавать и общаться с единомышленниками.",
        "Креативный человек, который видит мир по-особенному. Ищу того, кто ценит искусство, музыку и глубокие разговоры.",
        "Фотограф и мечтатель. Ловлю моменты, которые другие могут пропустить. Давайте исследовать мир вместе.",
        "Пишу днём, любуюсь звёздами ночью. Верю, что у каждого человека есть история, которую стоит рассказать.",
        "Музыкант в поисках гармонии в жизни и любви. Нахожу покой в мелодиях и значимых связях."
    ],
    "introverted": [
        "Тихая душа, которая любит книги, уютные вечера и искренние разговоры больше светской болтовни.",
        "Интроверт, который восстанавливается на природе. Ищу того, кто понимает, что молчание может быть комфортным.",
        "Домосед, который находит радость в простых удовольствиях. Вечера кино и глубокие беседы - мой язык любви.",
        "Предпочитаю качество количеству во всём, особенно в отношениях. Давайте не будем торопиться.",
        "Нежная душа, которая ценит мелочи. Ищу того, кто ценит искренность больше популярности."
    ],
    "adventurous": [
        "Искатель приключений с любопытным умом. Всегда готова исследовать новые места и пробовать новое.",
        "Страсть к путешествиям в моих венах. Ищу попутчика и спутника жизни в одном лице.",
        "Любитель активного отдыха, который находит покой на природе. Походы, кемпинг и созерцание звёзд - моя терапия.",
        "Спонтанная душа, которая верит, что жизнь нужно проживать полно. Давайте создавать воспоминания вместе.",
        "Исследователь мира и человеческого опыта. Ищу того, кто так же страстно стремится к росту."
    ],
    "intellectual": [
        "Выпускница философского факультета, которая любит глубокие разговоры о жизни, вселенной и всём остальном.",
        "Любопытный ум, всегда изучающий что-то новое. Ищу интеллектуальную стимуляцию и эмоциональную связь.",
        "Исследователь по профессии, мечтатель по натуре. Нахожу закономерности увлекательными, а людей ещё более интересными.",
        "Люблю обсуждать идеи, теории и возможности. Ищу того, кто наслаждается умственными приключениями.",
        "Студент на всю жизнь, который верит, что знания нужно делить. Давайте научим друг друга чему-то новому."
    ],
    "empathetic": [
        "Высокочувствительная личность, которая глубоко чувствует. Ищу того, кто ценит эмоциональный интеллект.",
        "Эмпат в поисках искренней связи. Верю, что понимание друг друга - основа любви.",
        "Заботливая душа, которая находит смысл в помощи другим. Ищу человека с доброй душой.",
        "Верю в силу уязвимости и искреннего общения. Давайте будем настоящими друг с другом.",
        "Нежная душа, которая видит хорошее в каждом. Ищу того, кто ценит сострадание и понимание."
    ]
}

def generate_bio(personality_type, nd_traits):
    """Generate a realistic bio based on personality and traits"""
    base_bio = random.choice(BIO_TEMPLATES[personality_type])
    
    # Add trait-specific elements (in Russian)
    trait_additions = []
    if "adhd" in nd_traits:
        trait_additions.extend([
            "СДВГ-мозг означает, что я полна энергии и идей!",
            "Мой СДВГ даёт мне уникальный взгляд на мир.",
            "Гиперактивный ум, но я направляю его на творчество."
        ])
    
    if "autism" in nd_traits:
        trait_additions.extend([
            "Аутист и горжусь этим - я вижу детали, которые упускают другие.",
            "Мой аутизм помогает мне ценить закономерности и красоту жизни.",
            "Нейроотличная и ищу понимающие связи."
        ])
    
    if "anxiety" in nd_traits:
        trait_additions.extend([
            "Тревожность - часть моего пути, но она меня не определяет.",
            "Учусь справляться с тревогой, оставаясь собой.",
            "Чувствительная душа, которой нужны терпение и понимание."
        ])
    
    # Combine base bio with trait-specific addition
    if trait_additions and random.choice([True, False]):
        addition = random.choice(trait_additions)
        return f"{base_bio} {addition}"
    
    return base_bio

def clear_all_profiles():
    """Delete all existing user profiles"""
    session = db_manager.get_session()
    try:
        # Delete all users
        deleted_count = session.query(User).delete()
        session.commit()
        print(f"Deleted {deleted_count} existing profiles")
    finally:
        session.close()

def create_fake_profile(user_id, name, gender, photos=None):
    """Create a single fake profile"""
    # Random age between 18-35
    age = random.randint(18, 35)
    
    # Random city
    city_data = random.choice(CITIES_WITH_COORDS)
    city, city_slug, latitude, longitude = city_data
    
    # Random interest (who they're looking for)
    if gender == "female":
        interest = random.choice(["male", "both"])
    else:
        interest = random.choice(["female", "both"])
    
    # Random neurodivergent traits (1-3 traits)
    num_traits = random.randint(1, 3)
    nd_traits = random.sample(ND_TRAITS, num_traits)
    
    # Generate seeking traits (what they're looking for in others)
    seeking_traits = random.sample(ND_TRAITS, random.randint(1, 2))
    
    # Random personality type for bio generation
    personality = random.choice(list(BIO_TEMPLATES.keys()))
    bio = generate_bio(personality, nd_traits)
    
    # Random creation time (within last 30 days)
    created_ago = random.randint(0, 30)
    created_at = datetime.utcnow() - timedelta(days=created_ago)
    
    # Random last active (within last 7 days)
    last_active_ago = random.randint(0, 7)
    last_active = datetime.utcnow() - timedelta(days=last_active_ago)
    
    user_data = {
        'user_id': user_id,
        'name': name,
        'age': age,
        'gender': gender,
        'interest': interest,
        'city': city,
        'city_slug': city_slug,
        'latitude': latitude,
        'longitude': longitude,
        'bio': bio,
        'photos': photos or [],
        'nd_traits': nd_traits,
        'seeking_traits': seeking_traits,
        'lang': 'ru',
        'created_at': created_at,
        'last_active': last_active,
        'likes': [],
        'sent_likes': [],
        'received_likes': [],
        'unnotified_likes': [],
        'declined_likes': [],
        'total_rating': round(random.uniform(3.5, 5.0), 1),
        'rating_count': random.randint(0, 20)
    }
    
    return db_manager.create_or_update_user(user_data)

def populate_fake_profiles():
    """Populate database with fake profiles"""
    print("Creating fake profiles...")
    
    # Create 30 female profiles with provided photos
    female_count = 30
    for i in range(female_count):
        user_id = 1000000 + i  # Start from high number to avoid conflicts
        name = random.choice(FEMALE_NAMES)
        
        # Assign photos cyclically
        if i < len(WOMEN_PHOTOS):
            photos = [WOMEN_PHOTOS[i]]
        else:
            # For additional profiles, randomly assign photos
            photos = [random.choice(WOMEN_PHOTOS)]
        
        user = create_fake_profile(user_id, name, "female", photos)
        print(f"Created female profile: {user.name} (ID: {user.user_id})")
    
    # Create 25 male profiles (no photos)
    male_count = 25
    for i in range(male_count):
        user_id = 2000000 + i  # Different range for males
        name = random.choice(MALE_NAMES)
        
        user = create_fake_profile(user_id, name, "male")
        print(f"Created male profile: {user.name} (ID: {user.user_id})")
    
    print(f"\nSuccessfully created {female_count + male_count} fake profiles!")
    print(f"- {female_count} female profiles with photos")
    print(f"- {male_count} male profiles")

def add_interactions():
    """Add some realistic interactions between profiles"""
    print("\nAdding realistic interactions...")
    
    session = db_manager.get_session()
    try:
        users = session.query(User).all()
        
        # Add some likes and matches
        for user in users:
            # Each user likes 3-8 other users
            potential_matches = [u for u in users if u.user_id != user.user_id]
            num_likes = random.randint(3, 8)
            liked_users = random.sample(potential_matches, min(num_likes, len(potential_matches)))
            
            user.sent_likes = [u.user_id for u in liked_users]
            
            # Add received likes
            for liked_user in liked_users:
                if liked_user.received_likes is None:
                    liked_user.received_likes = []
                if user.user_id not in liked_user.received_likes:
                    liked_user.received_likes.append(user.user_id)
                
                # 30% chance of mutual like (mutual interaction)
                if random.random() < 0.3:
                    if liked_user.sent_likes is None:
                        liked_user.sent_likes = []
                    if user.user_id not in liked_user.sent_likes:
                        liked_user.sent_likes.append(user.user_id)
        
        session.commit()
        print("Added realistic interactions between profiles")
        
    finally:
        session.close()

def main():
    """Main function to reset and populate profiles"""
    print("🗑️  Clearing all existing profiles...")
    clear_all_profiles()
    
    print("\n👥 Populating with fake profiles...")
    populate_fake_profiles()
    
    print("\n💕 Adding interactions...")
    add_interactions()
    
    # Show final statistics
    session = db_manager.get_session()
    try:
        total_users = session.query(User).count()
        female_users = session.query(User).filter(User.gender == 'female').count()
        male_users = session.query(User).filter(User.gender == 'male').count()
        
        print(f"\n📊 Final Statistics:")
        print(f"Total profiles: {total_users}")
        print(f"Female profiles: {female_users}")
        print(f"Male profiles: {male_users}")
        print(f"Photos assigned: {len(WOMEN_PHOTOS)} unique photos for female profiles")
        
    finally:
        session.close()
    
    print("\n✅ Database populated successfully!")
    print("The bot now has realistic fake profiles for testing.")

if __name__ == "__main__":
    main()