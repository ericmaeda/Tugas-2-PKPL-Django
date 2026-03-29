from django.urls import path
from .views import show_biodata

urlpatterns = [
    path('', show_biodata, name='show_biodata')
]
