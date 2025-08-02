"""
Keep-alive service for the Telegram bot
Provides a simple HTTP server to keep the bot running
"""

import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import logging

logger = logging.getLogger(__name__)

class KeepAliveHandler(BaseHTTPRequestHandler):
    """HTTP request handler for keep-alive service"""
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        response = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Alt3r Bot - Keep Alive</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    max-width: 500px;
                    margin: 0 auto;
                }
                .status {
                    background: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 20px;
                    display: inline-block;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧠 Alt3r Dating Bot</h1>
                <div class="status">✅ Bot is Running</div>
                <p>Neurodivergent Dating Bot for Telegram</p>
                <p>Connecting neurodivergent individuals worldwide</p>
                <hr>
                <p><small>Keep-alive service active</small></p>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(response.encode())
    
    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = '{"status": "ok", "message": "Alt3r bot is alive"}'
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP Server"""
    allow_reuse_address = True
    daemon_threads = True

def run_keep_alive_server():
    """Run the keep-alive HTTP server"""
    try:
        server = ThreadedHTTPServer(('0.0.0.0', 8000), KeepAliveHandler)
        logger.info("Keep-alive server started on port 8000")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Keep-alive server error: {e}")
        time.sleep(5)
        run_keep_alive_server()  # Restart on error

def start_keep_alive():
    """Start the keep-alive service in a separate thread"""
    keep_alive_thread = threading.Thread(target=run_keep_alive_server, daemon=True)
    keep_alive_thread.start()
    logger.info("Keep-alive service thread started")

def keep_alive_ping():
    """Periodic ping to keep the service alive"""
    import requests
    import time
    
    while True:
        try:
            time.sleep(300)  # Wait 5 minutes
            requests.get("http://localhost:8000", timeout=10)
            logger.info("Keep-alive ping successful")
        except Exception as e:
            logger.warning(f"Keep-alive ping failed: {e}")

if __name__ == "__main__":
    # Run keep-alive server directly
    logging.basicConfig(level=logging.INFO)
    run_keep_alive_server()
