#!/usr/bin/env python3
"""
Process Manager for Alt3r Bot
Ensures only one bot instance runs at a time
"""

import os
import sys
import time
import signal
import psutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ProcessManager:
    def __init__(self, process_name="alt3r_bot"):
        self.process_name = process_name
        self.pid_file = Path(f"/tmp/{process_name}.pid")
        self.lock_file = Path(f"/tmp/{process_name}.lock")
        
    def kill_existing_instances(self):
        """Kill any existing bot instances"""
        killed_count = 0
        current_pid = os.getpid()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Skip current process
                    if proc.info['pid'] == current_pid:
                        continue
                        
                    # Check if it's a Python process running main.py
                    if (proc.info['name'] and 'python' in proc.info['name'].lower() and
                        proc.info['cmdline'] and any('main.py' in cmd for cmd in proc.info['cmdline'])):
                        
                        logger.info(f"Killing existing bot instance: PID {proc.info['pid']}")
                        proc.kill()
                        proc.wait(timeout=5)  # Wait up to 5 seconds for process to die
                        killed_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except psutil.TimeoutExpired:
                    # Force kill if graceful kill didn't work
                    try:
                        proc.kill()
                        killed_count += 1
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Error killing existing instances: {e}")
            
        if killed_count > 0:
            logger.info(f"Killed {killed_count} existing bot instance(s)")
            time.sleep(2)  # Give processes time to fully terminate
            
        return killed_count
        
    def acquire_lock(self):
        """Acquire exclusive lock to prevent multiple instances"""
        try:
            current_pid = os.getpid()
            
            # Check if lock already exists and if process is still running
            if self.lock_file.exists():
                try:
                    with open(self.lock_file, 'r') as f:
                        old_pid = int(f.read().strip())
                    
                    # If it's the same process (re-entry), allow it
                    if old_pid == current_pid:
                        logger.info(f"Lock already held by current process (PID: {current_pid})")
                        return True
                    
                    # Check if the old process is still running
                    if psutil.pid_exists(old_pid):
                        logger.error(f"Another instance is already running (PID: {old_pid})")
                        return False
                    else:
                        logger.info(f"Removing stale lock file (PID {old_pid} no longer exists)")
                        self.lock_file.unlink()
                        if self.pid_file.exists():
                            self.pid_file.unlink()
                            
                except (ValueError, FileNotFoundError, OSError):
                    # Invalid or corrupted lock file, remove it
                    try:
                        self.lock_file.unlink()
                        if self.pid_file.exists():
                            self.pid_file.unlink()
                    except:
                        pass
            
            # Kill any existing instances that might not have lock files
            killed_count = self.kill_existing_instances()
            
            # Wait a moment after killing processes
            if killed_count > 0:
                import time
                time.sleep(1)
            
            # Create new lock files
            with open(self.lock_file, 'w') as f:
                f.write(str(current_pid))
                
            with open(self.pid_file, 'w') as f:
                f.write(str(current_pid))
                
            logger.info(f"Process lock acquired successfully (PID: {current_pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acquire process lock: {e}")
            return False
    
    def release_lock(self):
        """Release the process lock"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
            if self.pid_file.exists():
                self.pid_file.unlink()
            logger.info("Process lock released")
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.release_lock()
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Register cleanup on normal exit
        import atexit
        atexit.register(self.release_lock)

# Global instance
process_manager = ProcessManager("alt3r_bot")