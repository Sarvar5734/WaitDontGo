"""
Payment Configuration for Alt3r Bot
Set up your TON wallet and API credentials here
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# TON Payment Configuration
TON_WALLET_ADDRESS = os.getenv('TON_WALLET', 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c')  # Replace with your TON wallet address
TON_API_KEY = os.getenv('TON_API_KEY', '')  # Get from @tonapibot on Telegram
TON_TESTNET = os.getenv('TON_TESTNET', 'true').lower() == 'true'  # Set to 'false' for mainnet

# Telegram Stars Configuration 
# No additional configuration needed - handled by Telegram API directly

# Payment validation settings
MIN_STARS_AMOUNT = 10
MIN_TON_AMOUNT = 0.1

# Payment timeout (in hours)
PAYMENT_TIMEOUT_HOURS = 1

def get_ton_api_base():
    """Get the appropriate TON API base URL"""
    if TON_TESTNET:
        return "https://testnet.toncenter.com/api/v2"
    else:
        return "https://toncenter.com/api/v2"

def validate_payment_config():
    """Validate payment configuration"""
    issues = []
    
    if not TON_API_KEY:
        issues.append("TON_API_KEY not set - TON payments will not work")
    
    if TON_WALLET_ADDRESS == 'EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c':
        issues.append("TON_WALLET address is still placeholder - replace with your actual wallet")
    
    return issues

# Print configuration status on import
config_issues = validate_payment_config()
if config_issues:
    print("⚠️  Payment Configuration Issues:")
    for issue in config_issues:
        print(f"   - {issue}")
    print("\n💡 To fix:")
    print("   1. Get TON API key from @tonapibot")
    print("   2. Set your TON wallet address")
    print("   3. Update environment variables")
else:
    print("✅ Payment configuration looks good!")