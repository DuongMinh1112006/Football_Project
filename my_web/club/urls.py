from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_home, name = 'club-home'),
    path('Matches/', views.matches_list, name='matches'),
    path('Standing/', views.standing, name = 'standing'),
    path('<str:club_name>/', views.club_detail, name='club_detail'),
    path('<str:club_name>/stadium/<str:stadium_name>/', views.stadium, name = 'stadium'),
    path('<str:club_name>/player/<str:player_name>/', views.player_detail, name = 'player_detail'),

]