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
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia",
    "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Mila", "Ella", "Avery",
    "Sofia", "Camila", "Aria", "Scarlett", "Victoria", "Madison", "Luna", "Grace",
    "Chloe", "Penelope", "Layla", "Riley", "Zoey", "Nora", "Lily", "Eleanor"
]

MALE_NAMES = [
    "Liam", "Noah", "Oliver", "Elijah", "William", "James", "Benjamin", "Lucas",
    "Henry", "Alexander", "Mason", "Michael", "Ethan", "Daniel", "Jacob", "Logan",
    "Jackson", "Levi", "Sebastian", "Mateo", "Jack", "Owen", "Theodore", "Aiden",
    "Samuel", "Joseph", "John", "David", "Wyatt", "Matthew", "Luke", "Asher"
]

CITIES_WITH_COORDS = [
    ("New York", "new-york", 40.7128, -74.0060),
    ("Los Angeles", "los-angeles", 34.0522, -118.2437),
    ("Chicago", "chicago", 41.8781, -87.6298),
    ("Houston", "houston", 29.7604, -95.3698),
    ("Philadelphia", "philadelphia", 39.9526, -75.1652),
    ("Phoenix", "phoenix", 33.4484, -112.0740),
    ("San Antonio", "san-antonio", 29.4241, -98.4936),
    ("San Diego", "san-diego", 32.7157, -117.1611),
    ("Dallas", "dallas", 32.7767, -96.7970),
    ("San Jose", "san-jose", 37.3382, -121.8863),
    ("Austin", "austin", 30.2672, -97.7431),
    ("Jacksonville", "jacksonville", 30.3322, -81.6557),
    ("Fort Worth", "fort-worth", 32.7555, -97.3308),
    ("Columbus", "columbus", 39.9612, -82.9988),
    ("Charlotte", "charlotte", 35.2271, -80.8431),
    ("San Francisco", "san-francisco", 37.7749, -122.4194),
    ("Indianapolis", "indianapolis", 39.7684, -86.1581),
    ("Seattle", "seattle", 47.6062, -122.3321),
    ("Denver", "denver", 39.7392, -104.9903),
    ("Boston", "boston", 42.3601, -71.0589)
]

# Neurodivergent traits available in the system
ND_TRAITS = [
    "adhd", "autism", "anxiety", "depression", "bipolar", "ocd", "ptsd", 
    "dyslexia", "dyscalculia", "dyspraxia", "tourettes", "sensory_processing",
    "executive_dysfunction", "rejection_sensitivity", "hyperfocus", 
    "stimming", "social_anxiety", "perfectionism"
]

# Bio templates for different personalities
BIO_TEMPLATES = {
    "creative": [
        "Artist at heart, finding beauty in everyday moments. Love creating and connecting with like-minded souls.",
        "Creative spirit who sees the world differently. Looking for someone who appreciates art, music, and deep conversations.",
        "Photographer and dreamer. I capture moments that others might miss. Let's explore the world together.",
        "Writer by day, stargazer by night. I believe every person has a story worth telling.",
        "Musician seeking harmony in life and love. I find peace in melodies and meaningful connections."
    ],
    "introverted": [
        "Quiet soul who loves books, cozy evenings, and genuine conversations over small talk.",
        "Introvert who recharges in nature. Looking for someone who understands that silence can be comfortable.",
        "Homebody who finds joy in simple pleasures. Movie nights and deep talks are my love language.",
        "Prefer quality over quantity in all things, especially relationships. Let's take things slow and steady.",
        "Gentle spirit who appreciates the little things. Seeking someone who values authenticity over popularity."
    ],
    "adventurous": [
        "Adventure seeker with a curious mind. Always ready to explore new places and try new experiences.",
        "Wanderlust in my veins. Looking for a travel buddy and life partner rolled into one.",
        "Outdoor enthusiast who finds peace in nature. Hiking, camping, and stargazing are my therapy.",
        "Spontaneous spirit who believes life is meant to be lived fully. Let's make memories together.",
        "Explorer of both the world and the human experience. Seeking someone equally passionate about growth."
    ],
    "intellectual": [
        "Philosophy major who loves deep conversations about life, the universe, and everything in between.",
        "Curious mind always learning something new. Looking for intellectual stimulation and emotional connection.",
        "Researcher by profession, wonderer by nature. I find patterns fascinating and people even more so.",
        "Love discussing ideas, theories, and possibilities. Seeking someone who enjoys mental adventures.",
        "Lifelong learner who believes knowledge is meant to be shared. Let's teach each other something new."
    ],
    "empathetic": [
        "Highly sensitive person who feels deeply. Looking for someone who appreciates emotional intelligence.",
        "Empath seeking genuine connection. I believe understanding each other is the foundation of love.",
        "Caregiver at heart who finds purpose in helping others. Seeking someone with a kind soul.",
        "Believe in the power of vulnerability and authentic communication. Let's be real with each other.",
        "Gentle soul who sees the good in everyone. Looking for someone who values compassion and understanding."
    ]
}

def generate_bio(personality_type, nd_traits):
    """Generate a realistic bio based on personality and traits"""
    base_bio = random.choice(BIO_TEMPLATES[personality_type])
    
    # Add trait-specific elements
    trait_additions = []
    if "adhd" in nd_traits:
        trait_additions.extend([
            "ADHD brain means I'm full of energy and ideas!",
            "My ADHD gives me a unique perspective on the world.",
            "Hyperactive mind, but I channel it into creativity."
        ])
    
    if "autism" in nd_traits:
        trait_additions.extend([
            "Autistic and proud - I see details others miss.",
            "My autism helps me appreciate life's patterns and beauty.",
            "Neurodivergent and looking for understanding connections."
        ])
    
    if "anxiety" in nd_traits:
        trait_additions.extend([
            "Anxiety is part of my journey, but it doesn't define me.",
            "Learning to manage anxiety while staying true to myself.",
            "Sensitive soul who needs patience and understanding."
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
        'lang': random.choice(['en', 'ru']),
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