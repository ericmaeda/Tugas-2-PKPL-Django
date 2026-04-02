from django.db import models

class Theme(models.Model):
    bg_color   = models.CharField(max_length=7, default='#000000')
    card_color = models.CharField(max_length=7, default='#171717')
    text_color = models.CharField(max_length=7, default='#FFFFFF')
    accent     = models.CharField(max_length=7, default='#A5CDFE')
    font       = models.CharField(max_length=50, default='Poppins')