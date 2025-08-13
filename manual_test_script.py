#!/usr/bin/env python3
"""
Manual Bot Testing Script
Tests core functionality of the Alt3r bot
"""

import asyncio
import logging
from database_manager import db_manager
from db_operations import db
from main import (
    get_text, is_profile_complete_dict, is_admin, 
    normalize_city, calculate_distance_km, matches_interest_criteria,
    ND_TRAITS, ND_SYMPTOMS, TEXTS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManualBotTester:
    def __init__(self):
        self.test_results = []
        self.tests_passed = 0
        self.tests_failed = 0
        
    def test_assert(self, test_name, condition, description=""):
        """Assert a test condition and record result"""
        try:
            if condition:
                self.tests_passed += 1
                self.test_results.append(f"✅ {test_name}: PASSED {description}")
                logger.info(f"✅ {test_name}: PASSED")
                return True
            else:
                self.tests_failed += 1
                self.test_results.append(f"❌ {test_name}: FAILED {description}")
                logger.error(f"❌ {test_name}: FAILED")
                return False
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append(f"❌ {test_name}: ERROR - {str(e)}")
            logger.error(f"❌ {test_name}: ERROR - {str(e)}")
            return False

    def test_database_functions(self):
        """Test database functionality"""
        logger.info("=== Testing Database Functions ===")
        
        # Test user creation
        test_user_id = 999999999
        test_data = {
            'user_id': test_user_id,
            'name': 'Test User',
            'age': 25,
            'gender': 'М',
            'interest': 'Ж',
            'city': 'Москва',
            'bio': 'Test bio for comprehensive testing',
            'photos': ['test_photo_id_123'],
            'nd_traits': ['adhd', 'anxiety'],
            'lang': 'ru'
        }
        
        try:
            db.create_or_update_user(test_user_id, test_data)
            user = db.get_user(test_user_id)
            
            self.test_assert("Database User Creation", user is not None)
            self.test_assert("Database User Data Integrity", 
                           user.get('name') == 'Test User' and user.get('age') == 25)
            
            # Test user update
            db.create_or_update_user(test_user_id, {'name': 'Updated Test User'})
            updated_user = db.get_user(test_user_id)
            self.test_assert("Database User Update", 
                           updated_user.get('name') == 'Updated Test User')
            
            # Test get all users
            all_users = db.get_all_users()
            self.test_assert("Database Get All Users", 
                           isinstance(all_users, list) and len(all_users) > 0)
            
        except Exception as e:
            self.test_assert("Database Operations", False, f"Exception: {str(e)}")

    def test_utility_functions(self):
        """Test utility and helper functions"""
        logger.info("=== Testing Utility Functions ===")
        
        # Test text retrieval
        test_text = get_text(123456, "main_menu")
        self.test_assert("Text Retrieval Function", 
                        isinstance(test_text, str) and len(test_text) > 0)
        
        # Test different languages
        ru_text = get_text(123456, "main_menu")  # Default Russian
        self.test_assert("Russian Text Retrieval", "меню" in ru_text.lower())
        
        # Test profile completion check
        complete_profile = {
            'name': 'Test User',
            'age': 25,
            'gender': 'М',
            'interest': 'Ж',
            'city': 'Москва',
            'bio': 'Test bio',
            'photos': ['photo1']
        }
        
        incomplete_profile = {
            'name': 'Test User',
            'age': 25
            # Missing required fields
        }
        
        self.test_assert("Complete Profile Check", 
                        is_profile_complete_dict(complete_profile) == True)
        self.test_assert("Incomplete Profile Check", 
                        is_profile_complete_dict(incomplete_profile) == False)
        
        # Test admin check
        admin_id = 410177871  # From ADMIN_USER_IDS
        regular_id = 123456789
        
        self.test_assert("Admin Access Check", is_admin(admin_id) == True)
        self.test_assert("Non-Admin Access Check", is_admin(regular_id) == False)
        
        # Test city normalization
        normalized = normalize_city("  москва  ")
        self.test_assert("City Normalization", normalized == "Москва")
        
        # Test distance calculation
        # Moscow to St. Petersburg coordinates (approximate)
        moscow_lat, moscow_lon = 55.7558, 37.6176
        spb_lat, spb_lon = 59.9311, 30.3609
        
        distance = calculate_distance_km(moscow_lat, moscow_lon, spb_lat, spb_lon)
        self.test_assert("Distance Calculation", 
                        600 <= distance <= 700,  # ~635km actual distance
                        f"Distance: {distance:.1f}km")
        
        # Test interest matching
        user1 = {'gender': 'М', 'interest': 'Ж'}
        user2 = {'gender': 'Ж', 'interest': 'М'}
        user3 = {'gender': 'М', 'interest': 'М'}
        
        self.test_assert("Interest Matching - Compatible", 
                        matches_interest_criteria(user1, user2) == True)
        self.test_assert("Interest Matching - Incompatible", 
                        matches_interest_criteria(user1, user3) == False)

    def test_data_structures(self):
        """Test data structure integrity"""
        logger.info("=== Testing Data Structures ===")
        
        # Test ND_TRAITS structure
        self.test_assert("ND_TRAITS Structure - Russian", 
                        'ru' in ND_TRAITS and isinstance(ND_TRAITS['ru'], dict))
        self.test_assert("ND_TRAITS Structure - English", 
                        'en' in ND_TRAITS and isinstance(ND_TRAITS['en'], dict))
        
        # Test required traits exist
        required_traits = ['adhd', 'autism', 'anxiety', 'depression']
        ru_traits = ND_TRAITS.get('ru', {})
        
        for trait in required_traits:
            self.test_assert(f"Required ND Trait - {trait}", 
                           trait in ru_traits)
        
        # Test ND_SYMPTOMS structure
        self.test_assert("ND_SYMPTOMS Structure", 
                        'ru' in ND_SYMPTOMS and isinstance(ND_SYMPTOMS['ru'], dict))
        
        # Test TEXTS structure
        self.test_assert("TEXTS Structure - Russian", 
                        'ru' in TEXTS and isinstance(TEXTS['ru'], dict))
        self.test_assert("TEXTS Structure - English", 
                        'en' in TEXTS and isinstance(TEXTS['en'], dict))
        
        # Test essential text keys exist
        essential_keys = ['main_menu', 'back_button', 'questionnaire_age']
        ru_texts = TEXTS.get('ru', {})
        
        for key in essential_keys:
            self.test_assert(f"Essential Text Key - {key}", 
                           key in ru_texts)

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        logger.info("=== Testing Edge Cases ===")
        
        # Test with None values
        self.test_assert("Profile Check with None", 
                        is_profile_complete_dict(None) == False)
        
        # Test with empty profile
        self.test_assert("Profile Check with Empty Dict", 
                        is_profile_complete_dict({}) == False)
        
        # Test distance with invalid coordinates
        invalid_distance = calculate_distance_km(None, None, 55.7558, 37.6176)
        self.test_assert("Distance with Invalid Coordinates", 
                        invalid_distance == float('inf'))
        
        # Test get_text with invalid user_id
        fallback_text = get_text(None, "main_menu")
        self.test_assert("Text Retrieval with Invalid User", 
                        isinstance(fallback_text, str))
        
        # Test normalize_city with various inputs (avoid division by zero)
        test_cases = [
            ("москва", "Москва"),
            ("САНКТ-ПЕТЕРБУРГ", "Санкт-петербург"),
            ("new york", "New York")
        ]
        
        for input_city, expected in test_cases:
            if input_city:  # Skip empty strings to avoid division by zero
                result = normalize_city(input_city)
                self.test_assert(f"City Normalization - '{input_city}'", 
                               result == expected, f"Got: '{result}', Expected: '{expected}'")

    def test_performance_functions(self):
        """Test performance-related functions"""
        logger.info("=== Testing Performance Functions ===")
        
        # Test with large user dataset simulation
        try:
            # Create multiple test users
            test_user_ids = list(range(990000000, 990000010))
            
            for i, user_id in enumerate(test_user_ids):
                test_data = {
                    'user_id': user_id,
                    'name': f'Performance Test User {i}',
                    'age': 20 + (i % 10),
                    'gender': 'М' if i % 2 == 0 else 'Ж',
                    'interest': 'Ж' if i % 2 == 0 else 'М',
                    'city': 'Тест Город',
                    'bio': f'Performance test bio {i}',
                    'photos': [f'photo_{i}'],
                    'lang': 'ru'
                }
                db.create_or_update_user(user_id, test_data)
            
            # Test bulk retrieval
            all_users = db.get_all_users()
            test_users_found = [u for u in all_users if u.get('user_id', 0) >= 990000000]
            
            self.test_assert("Bulk User Creation and Retrieval", 
                           len(test_users_found) >= len(test_user_ids))
            
        except Exception as e:
            self.test_assert("Performance Test", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all test categories"""
        logger.info("🧪 Starting manual bot testing...")
        
        try:
            self.test_database_functions()
            self.test_utility_functions()
            self.test_data_structures()
            self.test_edge_cases()
            self.test_performance_functions()
        except Exception as e:
            logger.error(f"Critical error during testing: {e}")
        
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*70)
        print("🧪 MANUAL BOT TEST REPORT")
        print("="*70)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("\n" + "="*70)
        print("📋 DETAILED RESULTS:")
        print("="*70)
        
        for result in self.test_results:
            print(result)
        
        print("\n" + "="*70)
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED! Bot core functions are working correctly.")
        else:
            print(f"⚠️  {self.tests_failed} tests failed. Review the issues above.")
        print("="*70)

def main():
    """Run the manual test suite"""
    tester = ManualBotTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()