# Alt3r Bot Deployment & Migration Guide

## Quick Migration Overview

Your Alt3r bot is designed for easy platform migration without data loss. Here's what you need:

1. **Data Backup** - Complete PostgreSQL backup with one command
2. **Platform Files** - Auto-generated config files for any platform
3. **Environment Setup** - Portable environment variable configuration
4. **Zero Downtime** - Restore data to new platform seamlessly

## Emergency Backup (Do This First!)

```bash
# Create immediate backup of all data
python migration_tools.py backup

# Verify backup was created
ls -la backups/
```

This creates a complete JSON backup with all users, profiles, photos, and settings.

## Platform Migration Steps

### 1. Backup Current Data
```bash
python migration_tools.py backup
python migration_tools.py verify-integrity
```

### 2. Choose Target Platform

#### For Heroku:
```bash
python migration_tools.py create-heroku
python migration_tools.py create-requirements
# Files created: Procfile, runtime.txt, requirements.txt
```

#### For Railway/Render:
```bash
python migration_tools.py create-requirements
python migration_tools.py export-config
# Use platform_config.json for setup
```

#### For Docker (any platform):
```bash
python migration_tools.py create-dockerfile
python migration_tools.py create-requirements
# Files created: Dockerfile, requirements.txt
```

#### For VPS/Custom Server:
```bash
python migration_tools.py export-config
python migration_tools.py create-requirements
# Manual setup with generated configs
```

### 3. Setup New Platform

1. Create new project on target platform
2. Upload your code files
3. Copy generated platform files (Procfile, Dockerfile, etc.)
4. Set environment variables from platform_config.json

**Required Environment Variables:**
- `TELEGRAM_BOT_TOKEN` - Your bot token
- `DATABASE_URL` - New PostgreSQL database URL

### 4. Restore Data
```bash
# After new database is ready
python migration_tools.py restore backups/alt3r_backup_YYYYMMDD_HHMMSS.json
```

### 5. Verify Migration
```bash
python migration_tools.py verify-integrity
```

## Database Migration (PostgreSQL to Other)

### From PostgreSQL to PostgreSQL:
```bash
# Direct migration (easiest)
python migration_tools.py backup
python migration_tools.py restore backup_file.json
```

### From PostgreSQL to MySQL/MariaDB:
1. Backup data: `python migration_tools.py backup`
2. Update `models.py` for MySQL compatibility
3. Update `DATABASE_URL` format
4. Restore: `python migration_tools.py restore backup_file.json`

### From PostgreSQL to SQLite:
1. Backup data: `python migration_tools.py backup`
2. Update `models.py` for SQLite
3. Remove PostgreSQL-specific features
4. Restore: `python migration_tools.py restore backup_file.json`

## Platform-Specific Instructions

### Replit → Heroku
```bash
# 1. Backup
python migration_tools.py backup
python migration_tools.py create-heroku
python migration_tools.py create-requirements

# 2. Create Heroku app
heroku create your-alt3r-bot
heroku addons:create heroku-postgresql:hobby-dev

# 3. Set environment variables
heroku config:set TELEGRAM_BOT_TOKEN=your_token

# 4. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 5. Restore data
heroku run python migration_tools.py restore backups/your_backup.json
```

### Replit → Railway
```bash
# 1. Backup and prepare
python migration_tools.py backup
python migration_tools.py export-config
python migration_tools.py create-requirements

# 2. Create Railway project, connect GitHub repo
# 3. Add PostgreSQL service
# 4. Set environment variables from platform_config.json
# 5. Deploy automatically via GitHub
# 6. Restore data via Railway terminal
```

### Replit → Docker/VPS
```bash
# 1. Backup and prepare
python migration_tools.py backup
python migration_tools.py create-dockerfile
python migration_tools.py create-requirements

# 2. Build and run Docker container
docker build -t alt3r-bot .
docker run -d --name alt3r-bot \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e DATABASE_URL=your_postgres_url \
  alt3r-bot

# 3. Restore data
docker exec alt3r-bot python migration_tools.py restore backup_file.json
```

## Zero-Downtime Migration

For seamless migration without service interruption:

1. **Setup new platform** with same bot token (don't start yet)
2. **Backup data** from current platform
3. **Restore data** to new platform
4. **Test new deployment** (temporarily change bot token for testing)
5. **Switch DNS/webhook** or stop old bot and start new one
6. **Verify everything works** on new platform
7. **Cleanup old platform**

## Disaster Recovery

If something goes wrong:

```bash
# Quick restore to previous state
python migration_tools.py restore backups/latest_backup.json

# Or restore specific backup
python migration_tools.py restore backups/alt3r_backup_20250803_120000.json
```

## Automated Backup Schedule

Add to your platform's cron or scheduler:

```bash
# Daily backup (recommended)
0 2 * * * cd /app && python migration_tools.py backup

# Weekly cleanup (keep last 30 days)
0 3 * * 0 cd /app && find backups/ -name "*.json" -mtime +30 -delete
```

## File Structure for Migration

Your bot needs these files for any platform:

**Core Files:**
- `main.py` - Main bot code
- `models.py` - Database models
- `database_manager.py` - Database operations
- `translations.py` - Translation system
- `keep_alive.py` - Keep-alive service

**Migration Files:**
- `migration_tools.py` - Migration utilities
- `requirements.txt` - Python dependencies
- `backups/` - Data backups

**Platform-Specific (auto-generated):**
- `Dockerfile` - For Docker deployments
- `Procfile` - For Heroku
- `runtime.txt` - For Heroku
- `deployment_configs/` - Platform configurations

## Troubleshooting

**"Migration failed"**
- Check DATABASE_URL format
- Verify network connectivity
- Ensure target database exists

**"Data integrity check failed"**
- Restore from backup
- Check database permissions
- Verify table structure

**"Environment variables missing"**
- Copy from platform_config.json
- Double-check variable names
- Restart application after setting

**"Bot not responding"**
- Check TELEGRAM_BOT_TOKEN
- Verify webhook/polling settings
- Check application logs

## Support

Your Alt3r bot is now fully portable and migration-ready. All data can be safely moved between platforms without losing users, photos, or preferences.