"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django application setup should be before any other imports
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Bot setup
import asyncio
from threading import Thread
from bot.utils import start_bot

def run_bot_forever():
    """Run bot in a new event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while True:
        try:
            loop.run_until_complete(start_bot())
        except Exception as e:
            print(f"Bot crashed: {e}")
            print("Restarting bot in 5 seconds...")
            loop.run_until_complete(asyncio.sleep(5))

# Start bot in a separate thread if not in test environment
bot_thread = Thread(target=run_bot_forever, daemon=True)
bot_thread.start()
