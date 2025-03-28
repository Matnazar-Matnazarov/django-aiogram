from django.urls import path
from .views import add_words_to_db

urlpatterns = [
    path("add-words/", add_words_to_db, name="add_words_to_db"),
]