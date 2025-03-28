from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .models import EnglishWord

def add_words_to_db(request):
    # Faylni ochish va o'qish
    with open("word.txt", "r", encoding="utf-8") as file:
        words = file.read().strip().split("\n")

    # So‘zlarni saqlash
    added_count = 0
    for word in words:
        word = word.strip()
        if word:
            obj, created = EnglishWord.objects.get_or_create(text=word)
            if created:
                added_count += 1

    print(f"{added_count} ta yangi so'z qo'shildi!")
    return HttpResponse("ok")