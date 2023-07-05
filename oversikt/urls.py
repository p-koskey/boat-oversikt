from . import views
from django.urls import path

app_name = 'oversikt'

urlpatterns = [
    path('', views.scraped_data_view, name='scraped_data'),
]