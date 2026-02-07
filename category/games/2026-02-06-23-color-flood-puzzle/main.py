#!/usr/bin/env python3
"""
Color Flood Puzzle Game Launcher

This script launches a local web server to run the Color Flood Puzzle game.
The game itself is written in pure HTML/CSS/JavaScript and runs in the browser.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path


def main():
    """Start a local web server and open the game in the default browser."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    # Check if index.html exists
    if not (script_dir / "index.html").exists():
        print("Error: index.html not found!")
        sys.exit(1)

    PORT = 8000

    # Create a custom handler to serve files
    handler = http.server.SimpleHTTPRequestHandler

    # Suppress log messages for cleaner output
    # handler.log_message = lambda *args: None

    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"Color Flood Puzzle Game")
        print(f"Starting server at {url}")
        print(f"Press Ctrl+C to stop the server")

        # Open the browser after a short delay
        def open_browser():
            webbrowser.open(url)

        # Use a timer to open browser after server starts
        import threading
        browser_thread = threading.Timer(1.0, open_browser)
        browser_thread.daemon = True
        browser_thread.start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
