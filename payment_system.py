"""
Payment System Integration Module for Alt3r Bot
Handles Telegram Stars and TON cryptocurrency payments
"""

import os
import logging
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import aiohttp
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import ContextTypes
from database_manager import DatabaseManager
from translations import get_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseManager()

class TelegramStarsPayment:
    """Handle Telegram Stars payment processing"""
    
    @staticmethod
    async def create_stars_invoice(user_id: int, amount: int, title: str, description: str) -> Dict[str, Any]:
        """Create a Telegram Stars invoice"""
        try:
            # Create price list - amount is already in Stars
            prices = [LabeledPrice(label=title, amount=amount)]
            
            # Generate unique payload for tracking
            payload = f"stars_{amount}_{user_id}_{int(datetime.now().timestamp())}"
            
            return {
                "title": title,
                "description": description,
                "payload": payload,
                "provider_token": "",  # Empty for Stars payments
                "currency": "XTR",     # Required for Stars
                "prices": prices,
                "max_tip_amount": 0,
                "suggested_tip_amounts": []
            }
        except Exception as e:
            logger.error(f"Error creating Stars invoice: {e}")
            return None

    @staticmethod
    async def send_stars_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               invoice_data: Dict[str, Any]) -> bool:
        """Send Telegram Stars invoice to user"""
        try:
            await context.bot.send_invoice(
                chat_id=update.effective_chat.id,
                **invoice_data
            )
            return True
        except Exception as e:
            logger.error(f"Error sending Stars invoice: {e}")
            return False

    @staticmethod
    async def handle_pre_checkout_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle pre-checkout query for Stars payments"""
        query = update.pre_checkout_query
        try:
            # Validate payment data
            if query.currency == "XTR" and query.invoice_payload.startswith("stars_"):
                await query.answer(ok=True)
            else:
                await query.answer(ok=False, error_message="Invalid payment data")
        except Exception as e:
            logger.error(f"Error in pre-checkout query: {e}")
            await query.answer(ok=False, error_message="Payment validation failed")

    @staticmethod
    async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle successful Stars payment"""
        payment = update.message.successful_payment
        user_id = update.message.from_user.id
        
        try:
            # Extract payment details
            amount = payment.total_amount  # Already in Stars
            payload = payment.invoice_payload
            charge_id = payment.telegram_payment_charge_id
            
            # Log successful payment
            logger.info(f"Stars payment successful: user {user_id}, amount {amount} Stars, charge_id {charge_id}")
            
            # Store payment record in database
            payment_record = {
                "user_id": user_id,
                "payment_type": "telegram_stars",
                "amount": amount,
                "currency": "XTR",
                "charge_id": charge_id,
                "payload": payload,
                "status": "completed",
                "created_at": datetime.now().isoformat()
            }
            
            # Add to database (you may want to create a payments table)
            # For now, we'll store in user data
            user = db.get_user(user_id)
            if user:
                payments = user.get('payments', [])
                payments.append(payment_record)
                db.create_or_update_user(user_id, {'payments': payments})
            
            # Send thank you message
            lang = user.get('lang', 'ru') if user else 'ru'
            thank_you_text = get_text(user_id, "payment_success")
            
            await update.message.reply_text(
                thank_you_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="back_to_menu")
                ]])
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling successful Stars payment: {e}")
            return False

class TONPayment:
    """Handle TON cryptocurrency payment processing"""
    
    def __init__(self):
        # Import configuration
        from payment_config import TON_WALLET_ADDRESS, TON_API_KEY, get_ton_api_base
        
        # TON wallet configuration
        self.ton_wallet = TON_WALLET_ADDRESS
        self.ton_api_key = TON_API_KEY
        self.api_base = get_ton_api_base()

    async def generate_payment_comment(self, user_id: int, amount: float) -> str:
        """Generate unique payment comment for tracking"""
        timestamp = int(datetime.now().timestamp())
        comment = f"ALT3R_{user_id}_{timestamp}_{amount}"
        return comment

    async def create_ton_invoice(self, user_id: int, amount: float) -> Dict[str, Any]:
        """Create TON payment invoice data"""
        try:
            comment = await self.generate_payment_comment(user_id, amount)
            
            # Store pending payment
            payment_record = {
                "user_id": user_id,
                "payment_type": "ton",
                "amount": amount,
                "currency": "TON",
                "comment": comment,
                "wallet_address": self.ton_wallet,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
            # Store in database
            user = db.get_user(user_id)
            if user:
                pending_payments = user.get('pending_ton_payments', [])
                pending_payments.append(payment_record)
                db.create_or_update_user(user_id, {'pending_ton_payments': pending_payments})
            
            return {
                "wallet_address": self.ton_wallet,
                "amount": amount,
                "comment": comment,
                "payment_id": comment
            }
            
        except Exception as e:
            logger.error(f"Error creating TON invoice: {e}")
            return None

    async def check_ton_payment(self, payment_id: str, expected_amount: float) -> bool:
        """Check if TON payment has been received"""
        try:
            if not self.ton_api_key:
                logger.warning("TON API key not configured")
                return False
                
            # Get recent transactions
            url = f"{self.api_base}/getTransactions"
            params = {
                "address": self.ton_wallet,
                "limit": 50,
                "api_key": self.ton_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"TON API error: {response.status}")
                        return False
                    
                    data = await response.json()
                    
                    if not data.get("ok"):
                        logger.error(f"TON API response not ok: {data}")
                        return False
                    
                    transactions = data.get("result", [])
                    
                    # Check for matching transaction
                    for tx in transactions:
                        in_msg = tx.get("in_msg", {})
                        if not in_msg:
                            continue
                            
                        # Check amount (convert from nanotons)
                        value_nanotons = int(in_msg.get("value", 0))
                        value_tons = value_nanotons / 1000000000  # Convert to TON
                        
                        # Check comment
                        message = in_msg.get("message", "")
                        
                        if (abs(value_tons - expected_amount) < 0.001 and  # Allow small tolerance
                            payment_id in message):
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking TON payment: {e}")
            return False

    async def verify_and_complete_payment(self, user_id: int, payment_id: str) -> bool:
        """Verify TON payment and mark as completed"""
        try:
            user = db.get_user(user_id)
            if not user:
                return False
                
            pending_payments = user.get('pending_ton_payments', [])
            payment_record = None
            
            # Find the payment record
            for payment in pending_payments:
                if payment.get('comment') == payment_id:
                    payment_record = payment
                    break
            
            if not payment_record:
                logger.error(f"Payment record not found for ID: {payment_id}")
                return False
            
            # Check if payment is received
            expected_amount = float(payment_record['amount'])
            payment_received = await self.check_ton_payment(payment_id, expected_amount)
            
            if payment_received:
                # Mark as completed
                payment_record['status'] = 'completed'
                payment_record['completed_at'] = datetime.now().isoformat()
                
                # Move to completed payments
                completed_payments = user.get('payments', [])
                completed_payments.append(payment_record)
                
                # Remove from pending
                pending_payments = [p for p in pending_payments if p.get('comment') != payment_id]
                
                # Update database
                db.create_or_update_user(user_id, {
                    'payments': completed_payments,
                    'pending_ton_payments': pending_payments
                })
                
                logger.info(f"TON payment completed: user {user_id}, amount {expected_amount} TON")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying TON payment: {e}")
            return False

# Payment system instances
stars_payment = TelegramStarsPayment()
ton_payment = TONPayment()

# Utility functions for main bot integration

async def get_payment_options(user_id: int) -> InlineKeyboardMarkup:
    """Get payment options keyboard"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "support_stars_title"), callback_data="payment_method_stars")],
        [InlineKeyboardButton(get_text(user_id, "support_ton_title"), callback_data="payment_method_ton")],
        [InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_stars_amounts_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get Stars amounts selection keyboard"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "support_stars_50"), callback_data="stars_50")],
        [InlineKeyboardButton(get_text(user_id, "support_stars_100"), callback_data="stars_100")],
        [InlineKeyboardButton(get_text(user_id, "support_stars_250"), callback_data="stars_250")],
        [InlineKeyboardButton(get_text(user_id, "support_stars_500"), callback_data="stars_500")],
        [InlineKeyboardButton(get_text(user_id, "support_custom_stars"), callback_data="stars_custom")],
        [InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="support_project")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_ton_amounts_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get TON amounts selection keyboard"""
    keyboard = [
        [InlineKeyboardButton(get_text(user_id, "support_ton_1"), callback_data="ton_1.0")],
        [InlineKeyboardButton(get_text(user_id, "support_ton_5"), callback_data="ton_5.0")],
        [InlineKeyboardButton(get_text(user_id, "support_ton_10"), callback_data="ton_10.0")],
        [InlineKeyboardButton(get_text(user_id, "support_custom_ton"), callback_data="ton_custom")],
        [InlineKeyboardButton(get_text(user_id, "back_to_menu"), callback_data="support_project")]
    ]
    return InlineKeyboardMarkup(keyboard)

def validate_stars_amount(amount_str: str) -> Optional[int]:
    """Validate Stars amount input"""
    try:
        amount = int(float(amount_str))
        return amount if amount >= 10 else None
    except (ValueError, TypeError):
        return None

def validate_ton_amount(amount_str: str) -> Optional[float]:
    """Validate TON amount input"""
    try:
        amount = float(amount_str)
        return amount if amount >= 0.1 else None
    except (ValueError, TypeError):
        return None