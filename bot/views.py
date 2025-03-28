from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from aiogram import types
from django.conf import settings
from .utils import setup_bot
import json
import logging

# Create your views here.
from .models import EnglishWord

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def add_words_to_db(request):
    try:
        with open("word.txt", "r", encoding="utf-8") as file:
            words = {word.strip() for word in file if word.strip()}  # set comprehension

        # Bulk create using transaction
        with transaction.atomic():
            existing_words = set(EnglishWord.objects.values_list('text', flat=True))
            new_words = words - existing_words
            
            if new_words:
                EnglishWord.objects.bulk_create([
                    EnglishWord(text=word) for word in new_words
                ])
            
            added_count = len(new_words)

        return JsonResponse({
            'status': 'success',
            'message': f"{added_count} ta yangi so'z qo'shildi!",
            'added_count': added_count
        })

    except FileNotFoundError:
        return JsonResponse({
            'status': 'error',
            'message': "word.txt fayli topilmadi"
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
async def webhook_handler(request):
    """Process webhook updates from Telegram"""
    try:
        if request.method == 'POST':
            update_data = json.loads(request.body.decode())
            bot, dp = await setup_bot()
            
            update = types.Update(**update_data)
            await dp.process_update(update)
            
            return HttpResponse('OK')
        return HttpResponse('Method not allowed', status=405)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return HttpResponse(str(e), status=500)