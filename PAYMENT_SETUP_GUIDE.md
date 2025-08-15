# Payment System Setup Guide for Alt3r Bot

The Alt3r bot now supports **Telegram Stars** and **TON cryptocurrency** payments for project donations. This guide will help you configure and use the payment system.

## ✨ Payment Methods Supported

### 1. Telegram Stars ⭐
- **Native Telegram payments** - works out of the box
- **No additional setup required** for basic functionality
- Payments processed directly through Telegram
- Instant payment confirmation
- Supported amounts: 10+ Stars (customizable)

### 2. TON Cryptocurrency 💎
- **The Open Network (TON)** - Telegram's official blockchain
- Requires wallet and API configuration
- Real cryptocurrency transactions
- Automatic payment verification
- Supported amounts: 0.1+ TON (customizable)

## 🚀 Quick Setup

### For Telegram Stars (Immediate Use)
1. **No configuration needed** - works immediately
2. Users can pay with Telegram Stars they purchase in the app
3. Payments are processed through official Telegram Bot API

### For TON Payments (Requires Setup)
1. **Get a TON wallet address** (use any TON wallet like Tonkeeper)
2. **Get TON API key** from @tonapibot on Telegram
3. **Configure environment variables**

## 🔧 TON Payment Configuration

### Step 1: Get TON Wallet
1. Install a TON wallet (Tonkeeper, TonHub, etc.)
2. Create or import a wallet
3. Copy your wallet address (starts with "EQ" or "UQ")

### Step 2: Get API Key
1. Message @tonapibot on Telegram
2. Get your free API key for TON Center
3. Choose between testnet (for testing) or mainnet (for production)

### Step 3: Environment Variables
Add these to your environment variables or `.env` file:

```env
# TON Payment Configuration
TON_WALLET=your_ton_wallet_address_here
TON_API_KEY=your_ton_api_key_from_tonapibot
TON_TESTNET=true  # Set to 'false' for mainnet
```

### Step 4: Test the Configuration
The bot will automatically validate your configuration on startup:
- ✅ Green checkmark = Configuration OK
- ⚠️ Warning = Issues found with helpful instructions

## 💫 How It Works

### User Experience
1. User clicks "💖 Support Alt3r Project" in the main menu
2. Bot shows payment method selection:
   - ⭐ Telegram Stars
   - 💎 TON Cryptocurrency
3. User selects preferred method and amount
4. Payment is processed and confirmed automatically

### For Telegram Stars
1. User selects Stars amount (50, 100, 250, 500, or custom)
2. Telegram shows native payment interface
3. User completes payment with their Stars balance
4. Bot receives instant confirmation
5. Thank you message sent to user

### For TON Payments
1. User selects TON amount (1, 5, 10, or custom)
2. Bot generates unique payment invoice with:
   - Your TON wallet address
   - Exact amount to send
   - Unique comment for tracking
3. User sends TON from their wallet
4. Bot automatically detects and verifies payment
5. Confirmation sent once payment is received

## 🛠️ Technical Details

### Files Added/Modified
- **`payment_system.py`** - Core payment processing logic
- **`payment_config.py`** - Configuration management
- **`translations.py`** - Updated with payment messaging
- **`main.py`** - Integrated payment handlers
- **`.env.example`** - Added payment configuration template

### Payment Validation
- **Stars**: Minimum 10 Stars (customizable)
- **TON**: Minimum 0.1 TON (customizable)
- **Timeout**: 1 hour for TON payments
- **Error handling**: Comprehensive validation and user feedback

### Database Integration
- Payment records stored in user profiles
- Transaction tracking for both payment methods
- Payment history and status monitoring

## 🔒 Security Features

- **No private keys stored** - only wallet addresses
- **Read-only API access** - cannot send transactions
- **Transaction verification** - payments confirmed on blockchain
- **Timeout protection** - payments expire after 1 hour
- **Unique tracking** - each payment has unique identifier

## 🎯 Testing

### Test Mode (Recommended)
1. Set `TON_TESTNET=true` in your environment
2. Use TON testnet wallet and API
3. Test all payment flows before going live

### Production Mode
1. Set `TON_TESTNET=false`
2. Use mainnet wallet and API
3. Monitor payments in production environment

## 📞 Support

If you encounter issues:
1. Check environment variables are correctly set
2. Verify TON wallet address format
3. Ensure TON API key is active
4. Check bot logs for detailed error messages

## 🚀 Benefits of This System

- **Future-proof**: Uses Telegram's official payment methods
- **Low fees**: Minimal transaction costs
- **Fast processing**: Near-instant confirmations
- **User-friendly**: Familiar Telegram interface
- **Secure**: No handling of sensitive payment data
- **Global**: Works worldwide with Telegram users

## 💡 Tips

- Start with testnet to familiarize yourself with the system
- Monitor payment logs to understand user behavior
- Consider adjusting minimum amounts based on usage
- Keep API keys secure and never share them publicly

This payment system provides a modern, secure, and user-friendly way to accept donations for your Alt3r bot project!