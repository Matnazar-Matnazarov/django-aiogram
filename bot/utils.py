from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from django.conf import settings
from asgiref.sync import sync_to_async
from accounts.models import CustomUser, Role
from bot.models import Chat, EnglishWord
from deep_translator import GoogleTranslator
from gtts import gTTS
import logging
import os
import asyncio
from typing import Optional
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_session():
    """Create aiohttp session with PythonAnywhere proxy"""
    if not settings.DEBUG:
        connector = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(connector=connector)
    return None

async def setup_bot():
    """Initialize bot and dispatcher"""
    try:
        storage = MemoryStorage()
        session = await get_session()
        
        if session:
            bot = Bot(token=settings.BOT_TOKEN, session=session)
        else:
            bot = Bot(token=settings.BOT_TOKEN)
            
        dp = Dispatcher(bot, storage=storage)
        
        # Register handlers
        dp.register_message_handler(send_welcome, commands=["start"])
        dp.register_message_handler(handle_text_messages)
        
        # Set webhook in production
        if not settings.DEBUG:
            webhook_info = await bot.get_webhook_info()
            if webhook_info.url != settings.WEBHOOK_URL:
                await bot.delete_webhook()
                await bot.set_webhook(url=settings.WEBHOOK_URL)
                logger.info(f"Webhook set to {settings.WEBHOOK_URL}")
        
        return bot, dp
        
    except Exception as e:
        logger.error(f"Error setting up bot: {e}")
        if session:
            await session.close()
        raise

@sync_to_async
def get_user_or_create(telegram_id: int, user_data: dict) -> CustomUser:
    """Get or create user asynchronously"""
    user = CustomUser.objects.filter(telegram_id=telegram_id).first()
    if not user:
        user = CustomUser.objects.create(
            telegram_id=telegram_id,
            username=user_data.get('username'),
            full_name=user_data.get('full_name'),
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            phone_number=user_data.get('phone_number')
        )
    return user

async def send_welcome(message: types.Message):
    """Handle /start command"""
    user = await get_user_or_create(
        message.from_user.id,
        {
            'username': message.from_user.username,
            'full_name': message.from_user.full_name,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        }
    )
    
    await message.reply(
        f"Assalomu alaykum! Uzbek-English lug'at botiga xush kelibsiz {user.full_name}!"
    )
    await message.answer(
        "Siz bu botda uzbekchadan englishga tarjima qilasiz va englishchani ayta olishingiz uchun "
        "mp3 fayl ham tashlanadi\nSizga bu botda yana kuniga 10 ta lug'at tashlanadi"
    )

@sync_to_async
def get_random_words(count: int = 10) -> list:
    """Get random words from database"""
    return list(EnglishWord.objects.all()[:count].values_list('text', flat=True))

async def create_voice_file(text: str, filename: str) -> Optional[str]:
    """Create voice file from text"""
    try:
        tts = gTTS(text, lang="en")
        tts.save(filename)
        return filename
    except Exception as e:
        logger.error(f"Error creating voice file: {e}")
        return None

async def send_audio_message(message: types.Message, filename: str):
    """Helper function to send audio file"""
    try:
        # Audio faylni MP3 formatda yuborish
        with open(filename, 'rb') as audio:
            await message.answer_voice(
                types.InputFile(audio, filename=filename),
                caption="Audio message"
            )
    except Exception as e:
        logger.error(f"Error sending audio: {e}")

async def handle_text_messages(message: types.Message):
    """Handle text messages"""
    try:
        user = await get_user_or_create(
            message.from_user.id,
            {
                'username': message.from_user.username,
                'full_name': message.from_user.full_name,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )
        
        if not user.is_active:
            await message.reply("Bloklangansiz")
            return

        text = message.text
        chat = await sync_to_async(Chat.objects.get_or_create)(user=user)
        await chat[0].async_add_message(text)

        if (user.role == Role.ADMIN and text == "lugat") or (user.role == Role.SUPERADMIN and text == "lugat"):
            words = await get_random_words()
            translated_text = ""
            words_for_voice = ""
            
            for word in words:
                translation = GoogleTranslator(source="en", target="uz").translate(text=word)
                translated_text += f"{word} --- {translation}\n"
                words_for_voice += f"{word}\n\n\n\n"

            voice_filename = f"voice_{message.message_id}.mp3"
            if await create_voice_file(words_for_voice, voice_filename):
                try:
                    # Aktiv foydalanuvchilarni olish
                    active_users = await sync_to_async(list)(CustomUser.objects.filter(is_active=True))
                    
                    for active_user in active_users:
                        try:
                            # Har bir foydalanuvchi uchun xabar yuborish
                            await message.bot.send_message(
                                chat_id=active_user.telegram_id, 
                                text=translated_text
                            )
                            
                            # Voice message yuborish
                            with open(voice_filename, 'rb') as audio:
                                await message.bot.send_voice(
                                    chat_id=active_user.telegram_id,
                                    voice=types.InputFile(audio),
                                    caption="Audio message"
                                )
                                
                        except Exception as e:
                            logger.error(f"Error sending message to user {active_user.telegram_id}: {e}")
                            if "Chat not found" in str(e):
                                # Agar chat topilmasa, foydalanuvchini noaktiv qilish
                                active_user.is_active = False
                                await sync_to_async(active_user.save)()
                            continue
                            
                finally:
                    # Har qanday holatda ham faylni o'chirish
                    if os.path.exists(voice_filename):
                        os.remove(voice_filename)
                        
                await message.reply("Lug'atlar barcha aktiv foydalanuvchilarga yuborildi!")
            
        else:
            # Oddiy tarjima logikasi...
            translated_text = GoogleTranslator(source="uz", target="en").translate(text=text)
            await message.reply(translated_text)
            
            voice_filename = f"voice_{message.message_id}.mp3"
            try:
                tts = gTTS(text=translated_text, lang="en")
                tts.save(voice_filename)
                
                with open(voice_filename, 'rb') as audio:
                    await message.answer_voice(
                        types.InputFile(audio),
                        caption="Audio message"
                    )
            except Exception as e:
                logger.error(f"Error creating/sending voice: {e}")
            finally:
                if os.path.exists(voice_filename):
                    os.remove(voice_filename)

    except Exception as e:
        logger.error(f"Error handling message: {e}")
        admin = await sync_to_async(CustomUser.objects.filter(role=Role.ADMIN).first)()
        if admin:
            await message.bot.send_message(admin.telegram_id, f"Error: {e}")

async def start_bot():
    """Start the bot in appropriate mode"""
    try:
        bot, dp = await setup_bot()
        
        if settings.DEBUG:
            # Local development - use polling
            await dp.start_polling()
        else:
            # Production - return dispatcher for webhook
            logger.info("Bot started in webhook mode")
            return dp
            
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
        raise
    finally:
        if not settings.DEBUG and 'bot' in locals():
            session = await bot.get_session()
            if session:
                await session.close()
