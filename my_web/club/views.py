from django.shortcuts import render,get_object_or_404
from .models import Club, Player, Contract, Standing, Fixture


def club_home(request):
    context = {
        'clubs': Club.objects.all()
    }
    return render(request, "club/club_home.html", context)


def club_detail(request, club_name):

    club = get_object_or_404(Club, club_name=club_name)

    contract = Contract.objects.filter(club=club).select_related('player')

    context = {
        'club': club,
        'contracts': contract
    }
    return render(request, "club/club_detail.html", context)

def player_detail(request, club_name ,player_name):
    club = get_object_or_404(Club, club_name=club_name)

    contract = get_object_or_404(Contract, club=club, player__player_name = player_name)
    context = {
        'contract' : contract
    }
    return render(request, "club/player_detail.html", context)

def stadium(request, club_name,  stadium_name):
    club = Club.objects.get(club_name=club_name)
    stadium_obj = club.stadium
    context = {
        'club_name' : club_name,
        'stadium' : stadium_obj
    }
    return render(request, "club/stadium.html", context)


def standing(request):

    all_rounds = Standing.objects.values_list('round_name', flat=True).distinct()

    if all_rounds:
        latest_round = list(all_rounds)[-1]
        standings = Standing.objects.filter(round_name=latest_round).order_by(
            '-points',
            '-goal_difference',
            '-goals_for'
        )
    else:
        latest_round = "NO data"
        standings = []

    context = {
        'standings': standings,
        'current_round': latest_round
    }
    return render(request, 'club/standing.html', context)

def matches_list(request):
    matches = Fixture.objects.select_related('home_team', 'away_team').all()
    context = {
        'matches' : matches
    }
    return render(request, 'club/matches.html', context)