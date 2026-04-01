from django.urls import path
from . import views

urlpatterns = [
    path('',               views.show_biodata,    name='show_biodata'),
    path('auth/login',     views.oauth_login,     name='oauth_login'),
    path('auth/callback',  views.oauth_callback,  name='oauth_callback'),
    path('auth/logout',    views.oauth_logout,    name='oauth_logout'),
    path('api/save-theme', views.save_theme,      name='save_theme'),
]