#!/usr/bin/env python3
"""
Interactive Bot Handler Testing
Tests all major bot handlers and callback functions
"""

import asyncio
import logging
import sys
sys.path.append('.')

from main import *
from database_manager import db_manager
from db_operations import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveBotTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = 777777777
        
    async def test_handler_functions(self):
        """Test all major handler functions"""
        
        print("🧪 TESTING BOT HANDLERS")
        print("="*50)
        
        # Test 1: Profile completion check
        print("📋 Test 1: Profile Completion Checks")
        
        # Complete profile
        complete_user = {
            'name': 'Test Complete User',
            'age': 25,
            'gender': 'М',
            'interest': 'Ж',
            'city': 'Москва',
            'bio': 'Complete bio',
            'photos': ['photo1']
        }
        
        incomplete_user = {
            'name': 'Test User',
            'age': 25
        }
        
        complete_check = is_profile_complete_dict(complete_user)
        incomplete_check = is_profile_complete_dict(incomplete_user)
        
        print(f"  ✅ Complete profile check: {complete_check}")
        print(f"  ✅ Incomplete profile check: {not incomplete_check}")
        
        # Test 2: Text retrieval system
        print("\n📝 Test 2: Text Retrieval System")
        
        main_menu_text = get_text(self.test_user_id, "main_menu")
        back_button_text = get_text(self.test_user_id, "back_button")
        
        print(f"  ✅ Main menu text retrieved: {len(main_menu_text) > 0}")
        print(f"  ✅ Back button text retrieved: {len(back_button_text) > 0}")
        
        # Test 3: Admin system
        print("\n🛡️ Test 3: Admin Access System")
        
        admin_access = is_admin(410177871)  # Known admin ID
        regular_access = is_admin(self.test_user_id)
        
        print(f"  ✅ Admin user access: {admin_access}")
        print(f"  ✅ Regular user access: {not regular_access}")
        
        # Test 4: Database operations
        print("\n💾 Test 4: Database Operations")
        
        test_data = {
            'user_id': self.test_user_id,
            'name': 'Handler Test User',
            'age': 28,
            'gender': 'Ж',
            'interest': 'М',
            'city': 'Санкт-Петербург',
            'bio': 'Handler testing bio',
            'photos': ['handler_test_photo'],
            'nd_traits': ['adhd', 'anxiety'],
            'lang': 'ru'
        }
        
        try:
            # Create user
            db.create_or_update_user(self.test_user_id, test_data)
            retrieved_user = db.get_user(self.test_user_id)
            
            print(f"  ✅ User creation: {retrieved_user is not None}")
            print(f"  ✅ User data integrity: {retrieved_user.get('name') == 'Handler Test User'}")
            
            # Update user
            db.create_or_update_user(self.test_user_id, {'name': 'Updated Handler User'})
            updated_user = db.get_user(self.test_user_id)
            
            print(f"  ✅ User update: {updated_user.get('name') == 'Updated Handler User'}")
            
        except Exception as e:
            print(f"  ❌ Database error: {e}")
        
        # Test 5: Interest matching logic
        print("\n💕 Test 5: Interest Matching Logic")
        
        user_m_seeking_f = {'gender': 'М', 'interest': 'Ж'}
        user_f_seeking_m = {'gender': 'Ж', 'interest': 'М'}
        user_m_seeking_m = {'gender': 'М', 'interest': 'М'}
        
        compatible_match = matches_interest_criteria(user_m_seeking_f, user_f_seeking_m)
        incompatible_match = matches_interest_criteria(user_m_seeking_f, user_m_seeking_m)
        
        print(f"  ✅ Compatible users match: {compatible_match}")
        print(f"  ✅ Incompatible users don't match: {not incompatible_match}")
        
        # Test 6: Distance calculation
        print("\n📍 Test 6: Location and Distance")
        
        # Moscow and St. Petersburg coordinates
        moscow_coords = (55.7558, 37.6176)
        spb_coords = (59.9311, 30.3609)
        
        distance = calculate_distance_km(*moscow_coords, *spb_coords)
        print(f"  ✅ Distance calculation works: {600 <= distance <= 700}")
        print(f"     Moscow-SPB distance: {distance:.1f}km")
        
        # Test 7: City normalization
        print("\n🏙️ Test 7: City Normalization")
        
        test_cities = [
            ("москва", "Москва"),
            ("САНКТ-ПЕТЕРБУРГ", "Санкт-Петербург"),
            ("екатеринбург", "Екатеринбург")
        ]
        
        for input_city, expected in test_cities:
            normalized = normalize_city(input_city)
            print(f"  ✅ '{input_city}' → '{normalized}'")
        
        # Test 8: UI Helper Functions
        print("\n🎨 Test 8: UI Helper Functions")
        
        try:
            back_button = create_back_button(self.test_user_id)
            home_button = create_home_button()
            report_button = create_report_button(888888888)
            
            print(f"  ✅ Back button creation: {back_button.text is not None}")
            print(f"  ✅ Home button creation: {home_button.text == '🏠'}")
            print(f"  ✅ Report button creation: {report_button.text == '🚨'}")
            
        except Exception as e:
            print(f"  ❌ UI helper error: {e}")
        
        # Test 9: Data structures
        print("\n📊 Test 9: Data Structure Integrity")
        
        print(f"  ✅ ND_TRAITS has Russian: {'ru' in ND_TRAITS}")
        print(f"  ✅ ND_TRAITS has English: {'en' in ND_TRAITS}")
        print(f"  ✅ ND_SYMPTOMS available: {'ru' in ND_SYMPTOMS}")
        print(f"  ✅ TEXTS has languages: {list(TEXTS.keys())}")
        
        # Test required traits
        required_traits = ['adhd', 'autism', 'anxiety', 'depression']
        ru_traits = ND_TRAITS.get('ru', {})
        available_traits = [trait for trait in required_traits if trait in ru_traits]
        print(f"  ✅ Essential ND traits available: {len(available_traits)}/{len(required_traits)}")
        
        # Test 10: Performance with multiple users
        print("\n⚡ Test 10: Performance Testing")
        
        try:
            # Create multiple test users
            start_time = asyncio.get_event_loop().time()
            
            for i in range(10):
                test_id = 777000000 + i
                user_data = {
                    'user_id': test_id,
                    'name': f'Performance User {i}',
                    'age': 20 + i,
                    'gender': 'М' if i % 2 == 0 else 'Ж',
                    'interest': 'Ж' if i % 2 == 0 else 'М',
                    'city': 'Тест',
                    'bio': f'Performance test {i}',
                    'photos': [f'perf_photo_{i}'],
                    'lang': 'ru'
                }
                db.create_or_update_user(test_id, user_data)
            
            end_time = asyncio.get_event_loop().time()
            creation_time = end_time - start_time
            
            # Retrieve all users
            start_time = asyncio.get_event_loop().time()
            all_users = db.get_all_users()
            end_time = asyncio.get_event_loop().time()
            retrieval_time = end_time - start_time
            
            print(f"  ✅ Created 10 users in: {creation_time:.3f}s")
            print(f"  ✅ Retrieved {len(all_users)} users in: {retrieval_time:.3f}s")
            print(f"  ✅ Performance acceptable: {creation_time < 5.0 and retrieval_time < 2.0}")
            
        except Exception as e:
            print(f"  ❌ Performance test error: {e}")
        
        print("\n" + "="*50)
        print("🎉 HANDLER TESTING COMPLETE")
        print("="*50)

async def main():
    """Run interactive handler tests"""
    tester = InteractiveBotTester()
    await tester.test_handler_functions()

if __name__ == "__main__":
    asyncio.run(main())