#!/usr/bin/env python3
"""
Comprehensive Bot Testing Script
Tests all handlers and functionality of the Alt3r bot
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, CallbackQuery, Chat
from telegram.ext import ContextTypes
from datetime import datetime

# Import main bot functions
import sys
sys.path.append('.')
from main import *

# Setup test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotTester:
    def __init__(self):
        self.test_user_id = 999999999
        self.test_target_id = 888888888
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
    def create_mock_update(self, message_text=None, callback_data=None, user_id=None):
        """Create a mock update object for testing"""
        if user_id is None:
            user_id = self.test_user_id
            
        mock_user = User(id=user_id, first_name="TestUser", is_bot=False)
        mock_chat = Chat(id=user_id, type="private")
        
        if callback_data:
            # Create callback query update
            mock_message = Message(
                message_id=1,
                date=datetime.now(),
                chat=mock_chat,
                from_user=mock_user
            )
            mock_message.reply_text = AsyncMock()
            mock_message.reply_photo = AsyncMock()
            mock_message.reply_video = AsyncMock()
            
            mock_query = CallbackQuery(
                id="test_query",
                from_user=mock_user,
                chat_instance="test_instance",
                data=callback_data,
                message=mock_message
            )
            mock_query.answer = AsyncMock()
            mock_query.edit_message_text = AsyncMock()
            mock_query.delete_message = AsyncMock()
            
            mock_update = Update(update_id=1, callback_query=mock_query)
        else:
            # Create message update
            mock_message = Message(
                message_id=1,
                date=datetime.now(),
                chat=mock_chat,
                from_user=mock_user,
                text=message_text
            )
            mock_message.reply_text = AsyncMock()
            mock_message.reply_photo = AsyncMock()
            mock_message.reply_video = AsyncMock()
            
            mock_update = Update(update_id=1, message=mock_message)
            
        mock_update.effective_user = mock_user
        mock_update.effective_chat = mock_chat
        
        return mock_update

    def create_mock_context(self, user_data=None):
        """Create a mock context object for testing"""
        mock_context = MagicMock()
        mock_context.user_data = user_data or {}
        mock_context.bot = MagicMock()
        return mock_context

    async def test_function(self, test_name, test_func, *args, **kwargs):
        """Test a specific function and record results"""
        try:
            logger.info(f"🧪 Testing: {test_name}")
            result = await test_func(*args, **kwargs)
            self.tests_passed += 1
            self.test_results.append(f"✅ {test_name}: PASSED")
            logger.info(f"✅ {test_name}: PASSED")
            return result
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append(f"❌ {test_name}: FAILED - {str(e)}")
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")
            return None

    async def test_basic_handlers(self):
        """Test basic message handlers"""
        logger.info("=== Testing Basic Handlers ===")
        
        # Test start command
        update = self.create_mock_update("/start")
        context = self.create_mock_context()
        await self.test_function("Start Command", start, update, context)
        
        # Test help command
        update = self.create_mock_update("/help")
        context = self.create_mock_context()
        await self.test_function("Help Command", show_help_command, update, context)
        
        # Test language command
        update = self.create_mock_update("/language")
        context = self.create_mock_context()
        await self.test_function("Language Command", show_language_command, update, context)

    async def test_registration_flow(self):
        """Test user registration workflow"""
        logger.info("=== Testing Registration Flow ===")
        
        # Test age handler
        update = self.create_mock_update("25")
        context = self.create_mock_context()
        await self.test_function("Age Handler", handle_age, update, context)
        
        # Test gender handler
        update = self.create_mock_update("М")
        context = self.create_mock_context({'age': 25})
        await self.test_function("Gender Handler", handle_gender, update, context)
        
        # Test interest handler
        update = self.create_mock_update("Ж")
        context = self.create_mock_context({'age': 25, 'gender': 'М'})
        await self.test_function("Interest Handler", handle_interest, update, context)
        
        # Test city handler
        update = self.create_mock_update("Москва")
        context = self.create_mock_context({'age': 25, 'gender': 'М', 'interest': 'Ж'})
        await self.test_function("City Handler", handle_city, update, context)
        
        # Test name handler
        update = self.create_mock_update("Тестовое Имя")
        context = self.create_mock_context({'age': 25, 'gender': 'М', 'interest': 'Ж', 'city': 'Москва'})
        await self.test_function("Name Handler", handle_name, update, context)
        
        # Test bio handler
        update = self.create_mock_update("Тестовое описание профиля")
        context = self.create_mock_context({'age': 25, 'gender': 'М', 'interest': 'Ж', 'city': 'Москва', 'name': 'Тестовое Имя'})
        await self.test_function("Bio Handler", handle_bio, update, context)

    async def test_callback_handlers(self):
        """Test callback query handlers"""
        logger.info("=== Testing Callback Handlers ===")
        
        # Create test user in database
        test_user_data = {
            'user_id': self.test_user_id,
            'name': 'Test User',
            'age': 25,
            'gender': 'М',
            'interest': 'Ж',
            'city': 'Москва',
            'bio': 'Test bio',
            'photos': ['test_photo_id'],
            'nd_traits': ['adhd'],
            'lang': 'ru'
        }
        db.create_or_update_user(self.test_user_id, test_user_data)
        
        # Test main menu callbacks
        callbacks_to_test = [
            "view_profile",
            "browse_profiles", 
            "my_likes",
            "profile_settings",
            "feedback",
            "statistics",
            "support_project",
            "back_to_menu"
        ]
        
        for callback_data in callbacks_to_test:
            update = self.create_mock_update(callback_data=callback_data)
            context = self.create_mock_context()
            await self.test_function(f"Callback: {callback_data}", handle_callback, update, context)

    async def test_admin_functions(self):
        """Test admin functionality"""
        logger.info("=== Testing Admin Functions ===")
        
        # Test with admin user
        admin_user_id = 410177871  # From ADMIN_USER_IDS
        
        # Test admin panel
        update = self.create_mock_update(callback_data="admin_panel", user_id=admin_user_id)
        context = self.create_mock_context()
        await self.test_function("Admin Panel Access", handle_callback, update, context)
        
        # Test admin reports
        update = self.create_mock_update(callback_data="admin_reports", user_id=admin_user_id)
        context = self.create_mock_context()
        await self.test_function("Admin Reports", handle_callback, update, context)
        
        # Test admin users
        update = self.create_mock_update(callback_data="admin_users", user_id=admin_user_id)
        context = self.create_mock_context()
        await self.test_function("Admin Users", handle_callback, update, context)

    async def test_profile_management(self):
        """Test profile editing functions"""
        logger.info("=== Testing Profile Management ===")
        
        # Test profile settings menu
        update = self.create_mock_update(callback_data="profile_settings")
        context = self.create_mock_context()
        await self.test_function("Profile Settings Menu", show_profile_settings_menu, update.callback_query, self.test_user_id)
        
        # Test change photo
        update = self.create_mock_update(callback_data="change_photo")
        context = self.create_mock_context()
        await self.test_function("Change Photo", start_change_photo, update.callback_query, context, self.test_user_id)
        
        # Test change bio
        update = self.create_mock_update(callback_data="change_bio")
        context = self.create_mock_context()
        await self.test_function("Change Bio", start_change_bio, update.callback_query, context, self.test_user_id)

    async def test_browsing_functionality(self):
        """Test profile browsing functionality"""
        logger.info("=== Testing Browsing Functionality ===")
        
        # Create additional test users for browsing
        for i in range(3):
            target_id = self.test_target_id + i
            target_data = {
                'user_id': target_id,
                'name': f'Target User {i+1}',
                'age': 22 + i,
                'gender': 'Ж',
                'interest': 'М',
                'city': 'Санкт-Петербург',
                'bio': f'Test target bio {i+1}',
                'photos': [f'target_photo_{i}'],
                'nd_traits': ['anxiety'],
                'lang': 'ru'
            }
            db.create_or_update_user(target_id, target_data)
        
        # Test browse profiles
        update = self.create_mock_update(callback_data="browse_profiles")
        context = self.create_mock_context()
        await self.test_function("Browse Profiles", browse_profiles, update.callback_query, context, self.test_user_id)
        
        # Test next/previous navigation
        context.user_data = {
            'browsing_profiles': [
                {'user_id': self.test_target_id, 'name': 'Target 1'},
                {'user_id': self.test_target_id + 1, 'name': 'Target 2'}
            ],
            'current_profile_index': 0
        }
        
        update = self.create_mock_update(callback_data="next_profile")
        await self.test_function("Next Profile Navigation", handle_callback, update, context)
        
        update = self.create_mock_update(callback_data="prev_profile")
        await self.test_function("Previous Profile Navigation", handle_callback, update, context)

    async def test_like_system(self):
        """Test like/pass system"""
        logger.info("=== Testing Like System ===")
        
        # Test like profile
        update = self.create_mock_update(callback_data=f"like_{self.test_target_id}")
        context = self.create_mock_context()
        await self.test_function("Like Profile", handle_like_profile, update.callback_query, context, self.test_user_id, self.test_target_id)
        
        # Test pass profile
        update = self.create_mock_update(callback_data=f"pass_{self.test_target_id}")
        context = self.create_mock_context({
            'browsing_profiles': [{'user_id': self.test_target_id, 'name': 'Target'}],
            'current_profile_index': 0
        })
        await self.test_function("Pass Profile", handle_pass_profile, update.callback_query, context, self.test_user_id)

    async def test_utility_functions(self):
        """Test utility and helper functions"""
        logger.info("=== Testing Utility Functions ===")
        
        # Test text functions
        test_text = get_text(self.test_user_id, "main_menu")
        if test_text:
            self.tests_passed += 1
            self.test_results.append("✅ get_text function: PASSED")
        else:
            self.tests_failed += 1
            self.test_results.append("❌ get_text function: FAILED")
            
        # Test profile completion check
        user = db.get_user(self.test_user_id)
        is_complete = is_profile_complete_dict(user) if user else False
        if isinstance(is_complete, bool):
            self.tests_passed += 1
            self.test_results.append("✅ Profile completion check: PASSED")
        else:
            self.tests_failed += 1
            self.test_results.append("❌ Profile completion check: FAILED")
            
        # Test admin access
        admin_access = is_admin(410177871)
        non_admin_access = is_admin(self.test_user_id)
        if admin_access and not non_admin_access:
            self.tests_passed += 1
            self.test_results.append("✅ Admin access check: PASSED")
        else:
            self.tests_failed += 1
            self.test_results.append("❌ Admin access check: FAILED")

    async def test_database_operations(self):
        """Test database operations"""
        logger.info("=== Testing Database Operations ===")
        
        # Test user creation/update
        test_data = {'name': 'Updated Test User', 'age': 26}
        try:
            db.create_or_update_user(self.test_user_id, test_data)
            updated_user = db.get_user(self.test_user_id)
            if updated_user and updated_user.get('name') == 'Updated Test User':
                self.tests_passed += 1
                self.test_results.append("✅ Database user update: PASSED")
            else:
                self.tests_failed += 1
                self.test_results.append("❌ Database user update: FAILED")
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append(f"❌ Database user update: FAILED - {str(e)}")
        
        # Test getting all users
        try:
            all_users = db.get_all_users()
            if isinstance(all_users, list) and len(all_users) > 0:
                self.tests_passed += 1
                self.test_results.append("✅ Database get all users: PASSED")
            else:
                self.tests_failed += 1
                self.test_results.append("❌ Database get all users: FAILED")
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append(f"❌ Database get all users: FAILED - {str(e)}")

    async def run_all_tests(self):
        """Run all tests and generate report"""
        logger.info("🚀 Starting comprehensive bot testing...")
        
        try:
            await self.test_basic_handlers()
            await self.test_registration_flow()
            await self.test_callback_handlers()
            await self.test_admin_functions()
            await self.test_profile_management()
            await self.test_browsing_functionality()
            await self.test_like_system()
            await self.test_utility_functions()
            await self.test_database_operations()
        except Exception as e:
            logger.error(f"Critical error during testing: {e}")
            
        self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*60)
        print("🧪 COMPREHENSIVE BOT TEST REPORT")
        print("="*60)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("\n" + "="*60)
        print("📋 DETAILED RESULTS:")
        print("="*60)
        
        for result in self.test_results:
            print(result)
            
        print("\n" + "="*60)
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED! Bot is functioning correctly.")
        else:
            print(f"⚠️  {self.tests_failed} tests failed. Review the issues above.")
        print("="*60)

async def main():
    """Run the comprehensive test suite"""
    tester = BotTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())