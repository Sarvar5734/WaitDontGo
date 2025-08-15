# Admin Setup Guide for Alt3r Bot

## 🛠️ Setting Up Admin Access

### Step 1: Find Your Telegram User ID

1. Open Telegram and message [@userinfobot](https://t.me/userinfobot)
2. The bot will reply with your user ID (a number like `123456789`)
3. Save this number - you'll need it for configuration

### Step 2: Configure Admin Access

**Option A: Environment Variable (Recommended)**
```bash
# Add to your .env file
ADMIN_USER_IDS=123456789,987654321
```

**Option B: Direct Code Edit**
In `main.py`, find line ~5637 and update:
```python
ADMIN_USER_IDS = [123456789, 987654321]  # Your actual user IDs here
```

### Step 3: Restart the Bot

After adding your admin user ID, restart the bot to apply changes.

## 🔧 Admin Features Available

### User Management
- **View user reports**: See spam, harassment, and fake profile reports
- **User statistics**: Monitor total users, daily signups, etc.
- **Profile moderation**: Review reported profiles

### System Monitoring
- **Bot health**: Check system status and performance
- **Database stats**: Monitor user growth and engagement
- **Error logs**: Review system errors and issues

### Content Moderation
- **Report handling**: Process user reports systematically
- **Profile review**: Moderate questionable content
- **User blocking**: Remove problematic users when needed

## 🚨 Admin Security

### Best Practices
1. **Keep admin IDs private** - Never share your admin user ID
2. **Use multiple admins** - Add 2-3 trusted user IDs for backup access
3. **Regular monitoring** - Check reports and system health daily
4. **Document decisions** - Keep records of moderation actions

### Admin Commands
- All admin features are accessible through the bot interface
- No special commands needed - admin panels appear automatically for authorized users
- Admin status is verified by checking if your user ID is in the `ADMIN_USER_IDS` list

## 🔍 Testing Admin Access

1. Configure your user ID as shown above
2. Restart the bot
3. Send `/start` to the bot
4. You should see additional admin options in the menu
5. Test the user reports and statistics features

## ⚠️ Important Notes

- **Admin access is required** for proper platform moderation
- **Empty admin list** means no admin oversight (unsafe for public launch)
- **Admin panels won't show** until user IDs are properly configured
- **Case sensitive**: Make sure user IDs are exact numbers (no quotes, spaces, etc.)

---

*For security questions or admin issues, check the bot's error logs or test with @userinfobot*