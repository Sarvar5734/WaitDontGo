#!/usr/bin/env python3
"""
Test script to verify no overlap occurs
"""

import sys
sys.path.append('.')

from process_manager import process_manager

print("🔍 Testing overlap prevention...")
print(f"Current PID: {process_manager.pid_file}")

# Try to acquire lock (should fail if main bot is running)
if process_manager.acquire_lock():
    print("❌ ERROR: Lock acquired when it should be blocked!")
    process_manager.release_lock()
    sys.exit(1)
else:
    print("✅ SUCCESS: Lock correctly blocked - no overlap possible")
    sys.exit(0)