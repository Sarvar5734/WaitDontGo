#!/usr/bin/env python3
"""
Safe startup script for Alt3r Bot
Ensures only one instance runs and handles cleanup
"""

import os
import sys
import time
import subprocess
from process_manager import process_manager

def main():
    print("🚀 Alt3r Bot Safe Startup Script")
    print("=" * 40)
    
    # Kill any existing instances
    print("Step 1: Checking for existing bot instances...")
    killed_count = process_manager.kill_existing_instances()
    if killed_count > 0:
        print(f"   Killed {killed_count} existing instances")
        time.sleep(2)  # Give processes time to fully terminate
    else:
        print("   No existing instances found")
    
    # Clean up any stale lock files
    print("Step 2: Cleaning up lock files...")
    try:
        if process_manager.lock_file.exists():
            process_manager.lock_file.unlink()
            print("   Removed stale lock file")
        if process_manager.pid_file.exists():
            process_manager.pid_file.unlink()
            print("   Removed stale PID file")
    except:
        pass
    
    print("   Lock files cleaned")
    
    # Start the bot
    print("Step 3: Starting Alt3r Bot...")
    try:
        # Use subprocess to start main.py
        result = subprocess.run([sys.executable, "main.py"], 
                              cwd=os.getcwd(),
                              check=False)
        
        if result.returncode == 0:
            print("✅ Bot started successfully")
        else:
            print(f"❌ Bot exited with code {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⚠️  Startup interrupted by user")
        print("Cleaning up...")
        process_manager.release_lock()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        process_manager.release_lock()
        sys.exit(1)

if __name__ == "__main__":
    main()