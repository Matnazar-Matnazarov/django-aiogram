"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from pathlib import Path
import sys
import asyncio
from aiogram import Bot
import aiohttp

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django application setup should be before any other imports
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Bot webhook setup
from django.conf import settings

async def set_webhook():
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        session = aiohttp.ClientSession(connector=connector)
        bot = Bot(token=settings.BOT_TOKEN, session=session)
        
        # Avvalgi webhook ni o'chirish
        await bot.delete_webhook()
        
        # Yangi webhook ni o'rnatish
        result = await bot.set_webhook(
            url=settings.WEBHOOK_URL,
            drop_pending_updates=True,
            allowed_updates=['message', 'edited_message', 'callback_query']
        )
        webhook_info = await bot.get_webhook_info()
        print(f"Webhook set: {result}")
        print(f"Webhook info: {webhook_info}")
        
        await bot.close()
        await session.close()
    except Exception as e:
        print(f"Error setting webhook: {e}")

# WSGI application ishga tushganda webhook ni o'rnatish
try:
    asyncio.run(set_webhook())
    print("Webhook setup completed")
except Exception as e:
    print(f"Failed to set webhook: {e}")

