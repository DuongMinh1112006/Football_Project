from django.urls import path
from . import views

urlpatterns = [
    path('', views.club_home, name = 'club-home'),
    path('Matches/', views.matches_list, name='matches'),
    path('Standing/', views.standing, name = 'standing'),
    path('add-fixture/', views.add_fixture, name='add_fixture'),
    path('add-player-stat/', views.add_player_stat, name='add_player_stat'),
    path('search/', views.search_page, name='search_page'),
    path('report/goals/', views.goals, name='goals'),
    path('report/assists/', views.assists, name='assists'),
    path('report/rating', views.rating, name='rating'),
    path('report/yellow_card', views.yellow_card, name='yellow_card'),
    path('report/red_card', views.red_card, name='red_card'),
    path('report/', views.report_dashboard, name='report_dashboard'),
    path('<str:club_name>/', views.club_detail, name='club_detail'),
    path('<str:club_name>/stadium/<str:stadium_name>/', views.stadium, name = 'stadium'),
    path('<str:club_name>/player/<str:player_name>/', views.player_detail, name = 'player_detail'),

]