from django.shortcuts import render,get_object_or_404, redirect
from .models import Club, Player, Contract, Standing, Fixture
from django.contrib import messages
from django.db import connection


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
    sql = """
        SELECT 
            c.club_name,
            c.club_logo,
            COUNT(f.fixture_id) AS played,
            COALESCE(SUM(CASE WHEN (f.home_team_id = c.club_id AND f.home_score > f.away_score) OR (f.away_team_id = c.club_id AND f.away_score > f.home_score) THEN 1 ELSE 0 END), 0) AS won,
            COALESCE(SUM(CASE WHEN f.home_score = f.away_score AND f.home_score IS NOT NULL THEN 1 ELSE 0 END), 0) AS drawn,
            COALESCE(SUM(CASE WHEN (f.home_team_id = c.club_id AND f.home_score < f.away_score) OR (f.away_team_id = c.club_id AND f.away_score < f.home_score) THEN 1 ELSE 0 END), 0) AS lost,
            COALESCE(SUM(CASE WHEN f.home_team_id = c.club_id THEN f.home_score ELSE f.away_score END), 0) AS goals_for,
            COALESCE(SUM(CASE WHEN f.home_team_id = c.club_id THEN f.away_score ELSE f.home_score END), 0) AS goals_against,
            COALESCE(SUM(CASE WHEN f.home_team_id = c.club_id THEN f.home_score - f.away_score ELSE f.away_score - f.home_score END), 0) AS goal_difference,
            COALESCE(SUM(CASE 
                WHEN (f.home_team_id = c.club_id AND f.home_score > f.away_score) OR (f.away_team_id = c.club_id AND f.away_score > f.home_score) THEN 3
                WHEN f.home_score = f.away_score AND f.home_score IS NOT NULL THEN 1 
                ELSE 0 
            END), 0) AS points
        FROM club_club c
        LEFT JOIN club_fixture f ON c.club_id = f.home_team_id OR c.club_id = f.away_team_id
        GROUP BY c.club_id, c.club_name, c.club_logo
        ORDER BY points DESC, goal_difference DESC, goals_for DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        # Lấy tên cột từ SQL (club_name, points, goal_difference...)
        columns = [col[0] for col in cursor.description]
        # Ép dữ liệu thành danh sách Dictionary để HTML dễ đọc
        standings = [dict(zip(columns, row)) for row in cursor.fetchall()]

    context = {
        'standings': standings,
        'current_round': 'Live Data'  # Báo cáo realtime
    }
    return render(request, 'club/standing.html', context)



def matches_list(request):
    matches = Fixture.objects.select_related('home_team', 'away_team').all()
    context = {
        'matches' : matches
    }
    return render(request, 'club/matches.html', context)




def add_fixture(request):
    if request.method == 'POST':
        home_club = request.POST.get('home_team')
        away_club = request.POST.get('away_team')
        home_goals = request.POST.get('home_score')
        away_goals = request.POST.get('away_score')
        round_match = f"Regular Season - {request.POST.get('round_name')}"
        match_date = request.POST.get('match_date')

        with connection.cursor() as cursor:
            cursor.execute("SELECT COALESCE(MAX(fixture_id), 0) + 1 FROM club_fixture")
            new_id = cursor.fetchone()[0]
            sql = """
                INSERT INTO club_fixture (fixture_id, home_team_id, away_team_id, home_score, away_score, round_name, match_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            if home_club == away_club:
                messages.error(request, "Đội nhà và đội khách phải khác nhau!")
                return redirect('/add-fixture/')
            elif Fixture.objects.filter(home_team = home_club, away_team = away_club):
                messages.error(request, "Hai đội đã đối đầu với nhau!")
                return redirect('/add-fixture/')

            cursor.execute(sql, [new_id, home_club, away_club, home_goals, away_goals, round_match, match_date])

        return redirect('/Standing/')

    clubs = Club.objects.all().order_by('club_name')
    return render(request, 'club/add_fixture.html', {'clubs': clubs})


def add_player_stat(request):
    if request.method == 'POST':
        fixture_id = request.POST.get('fixture')
        player_id = request.POST.get('player')
        goals = request.POST.get('goals') or 0
        assists = request.POST.get('assists') or 0
        yellow_card = request.POST.get('yellow_card') or 0
        minutes = request.POST.get('minutes') or 0
        red_card = request.POST.get('red_card') or 0
        rating = request.POST.get('rating') or 0

        with connection.cursor() as cursor:

            sql = """
                INSERT INTO club_playerfixture (fixture_id, player_id, rating, goals, assists, minutes, yellow_card, red_card)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (fixture_id, player_id) 
                DO UPDATE SET 
                    rating = EXCLUDED.rating,
                    goals = EXCLUDED.goals,
                    assists = EXCLUDED.assists,
                    minutes = EXCLUDED.minutes,
                    yellow_card = EXCLUDED.yellow_card,
                    red_card = EXCLUDED.red_card;
            """

            if int(yellow_card) > 2:
                messages.error(request, "Số lượng thẻ vàng không thể lớn hơn 2")
                return redirect('/add-player-stat/')
            if int(red_card) > 1:
                messages.error(request, "Số lượng thẻ đỏ không thể lớn hơn 1")
                return redirect('/add-player-stat/')
            if int(minutes) > 90:
                messages.error(request, "Số phút không vượt quá 90")
                return redirect('/add-player-stat/')

            cursor.execute(sql, [fixture_id, player_id, rating, goals, assists, minutes, yellow_card, red_card])

        return redirect('/add-player-stat/')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.fixture_id, c1.club_name AS home, c2.club_name AS away, f.round_name
            FROM club_fixture f
            JOIN club_club c1 ON f.home_team_id = c1.club_id
            JOIN club_club c2 ON f.away_team_id = c2.club_id
            ORDER BY f.fixture_id DESC
        """)
        fixtures = cursor.fetchall()

        cursor.execute("""
            SELECT p.player_id, p.player_name, c.club_name
            FROM club_player p
            JOIN club_contract ct ON p.player_id = ct.player_id
            JOIN club_club c ON ct.club_id = c.club_id  
            ORDER BY c.club_name, p.player_name
        """)
        players = cursor.fetchall()


    return render(request, 'club/add_player_stat.html', {
        'fixtures': fixtures,
        'players': players
    })


def search_page(request):
    query = request.GET.get('q', '')
    position = request.GET.get('pos', '')
    results = []

    if query or position:
        with connection.cursor() as cursor:
            sql = """
                SELECT 
                    p.player_photo,
                    p.player_name, 
                    c.club_logo,
                    c.club_name,
                    COALESCE(SUM(pf.goals), 0) AS total_goals,
                    COALESCE(SUM(pf.assists), 0) AS total_assists,
                    COALESCE(SUM(pf.minutes), 0) AS total_minutes,
                    ct.position
                FROM club_player p
                JOIN club_contract ct ON p.player_id = ct.player_id
                JOIN club_club c ON ct.club_id = c.club_id
                LEFT JOIN club_playerfixture pf ON p.player_id = pf.player_id
                WHERE 1=1
            """
            params = []

            if query:
                sql += " AND (p.player_name ILIKE %s OR c.club_name ILIKE %s)"
                search_term = f'%{query}%'
                params.extend([search_term, search_term])

            if position:
                sql += " AND ct.position ILIKE %s"
                params.append(position)

            sql += """
                GROUP BY p.player_name, c.club_name, ct.position, p.player_photo, c.club_logo
                ORDER BY total_goals DESC, p.player_name
            """

            cursor.execute(sql, params)
            results = cursor.fetchall()

    return render(request, 'club/search.html', {
        'results': results,
        'query': query,
        'pos': position
    })


def goals(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                p.player_name, 
                p.player_photo, 
                ct.position,
                c.club_logo,
                COALESCE(SUM(pf.goals), 0) AS total_goals
            FROM club_player p
            JOIN club_contract ct ON p.player_id = ct.player_id
            JOIN club_club c ON ct.club_id = c.club_id
            JOIN club_playerfixture pf ON p.player_id = pf.player_id
            GROUP BY p.player_name, p.player_photo, ct.position, c.club_logo
            HAVING SUM(pf.goals) > 0
            ORDER BY total_goals DESC
            LIMIT 20
        """
        cursor.execute(sql)
        results = cursor.fetchall()

    return render(request, 'club/goals.html', {'results': results})

def assists(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                p.player_name, 
                p.player_photo, 
                ct.position,
                c.club_logo,
                COALESCE(SUM(pf.assists), 0) AS total_assists
            FROM club_player p
            JOIN club_contract ct ON p.player_id = ct.player_id
            JOIN club_club c ON ct.club_id = c.club_id
            JOIN club_playerfixture pf ON p.player_id = pf.player_id
            GROUP BY p.player_name, p.player_photo, ct.position, c.club_logo
            HAVING SUM(pf.assists) > 0
            ORDER BY total_assists DESC
            LIMIT 20
        """
        cursor.execute(sql)
        results = cursor.fetchall()

    return render(request, 'club/assists.html', {'results': results})

def rating(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                p.player_name, 
                p.player_photo, 
                ct.position,
                c.club_logo,
                COALESCE(ROUND(AVG(CAST(pf.rating AS NUMERIC)), 1), 0) AS avg_rating
            FROM club_player p
            JOIN club_contract ct ON p.player_id = ct.player_id
            JOIN club_club c ON ct.club_id = c.club_id
            JOIN club_playerfixture pf ON p.player_id = pf.player_id
            GROUP BY p.player_name, p.player_photo, ct.position, c.club_logo
            ORDER BY avg_rating DESC
            LIMIT 50
        """
        cursor.execute(sql)
        results = cursor.fetchall()

    return render(request, 'club/avg_rating.html', {'results': results})

def yellow_card(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                p.player_name, 
                p.player_photo, 
                ct.position,
                c.club_logo,
                COALESCE(SUM(pf.yellow_card), 0) AS total_yellow_card
            FROM club_player p
            JOIN club_contract ct ON p.player_id = ct.player_id
            JOIN club_club c ON ct.club_id = c.club_id
            JOIN club_playerfixture pf ON p.player_id = pf.player_id
            GROUP BY p.player_name, p.player_photo, ct.position, c.club_logo
            HAVING SUM(pf.yellow_card) > 0
            ORDER BY total_yellow_card DESC
            LIMIT 20
        """
        cursor.execute(sql)
        results = cursor.fetchall()

    return render(request, 'club/yellow_card.html', {'results': results})


def red_card(request):
    with connection.cursor() as cursor:
        sql = """
            SELECT 
                p.player_name, 
                p.player_photo, 
                ct.position,
                c.club_logo,
                COALESCE(SUM(pf.red_card), 0) AS total_red_card
            FROM club_player p
            JOIN club_contract ct ON p.player_id = ct.player_id
            JOIN club_club c ON ct.club_id = c.club_id
            JOIN club_playerfixture pf ON p.player_id = pf.player_id
            GROUP BY p.player_name, p.player_photo, ct.position, c.club_logo
            HAVING SUM(pf.red_card) > 0
            ORDER BY total_red_card DESC
            LIMIT 20
        """
        cursor.execute(sql)
        results = cursor.fetchall()

    return render(request, 'club/red_card.html', {'results': results})


def report_dashboard(request):
    return render(request, 'club/dashboard.html')