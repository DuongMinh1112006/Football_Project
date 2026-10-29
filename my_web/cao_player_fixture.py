import os
import django
import requests
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_web.settings')
django.setup()

from club.models import Fixture, Player, PlayerFixture

HEADERS = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': os.getenv('API_KEY')
}


def fetch_fixture_players():
    fixtures = Fixture.objects.filter(round_name = 'Regular Season - 1').all()

    print(f"Bắt đầu đồng bộ thông tin chi tiết cho {fixtures.count()} trận đấu...")

    for fixture in fixtures:
        print(f"Đang xử lý trận đấu ID: {fixture.fixture_id}...")

        url = f"https://v3.football.api-sports.io/fixtures/players?fixture={fixture.fixture_id}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Lỗi khi gọi API cho trận {fixture.fixture_id}")
            continue

        data = response.json()

        if not data.get('response'):
            print(f"Không có dữ liệu chi tiết cho trận {fixture.fixture_id}")
            continue

        for team_data in data['response']:
            for player_data in team_data['players']:
                player_info = player_data['player']

                stats = player_data['statistics'][0]

                player_id = player_info['id']

                try:
                    player_obj = Player.objects.get(pk=player_id)
                except Player.DoesNotExist:
                    continue

                games_data = stats.get('games', {})
                rating = games_data.get('rating')
                minutes = games_data.get('minutes')

                subs_data = stats.get('substitutes', {})
                min_in = subs_data.get('in')
                min_out = subs_data.get('out')

                goals_data = stats.get('goals', {})
                goals = goals_data.get('total') or 0
                assists = goals_data.get('assists') or 0

                cards_data = stats.get('cards', {})
                yellow_card = cards_data.get('yellow') or 0
                red_card = cards_data.get('red') or 0

                # Dùng update_or_create để không bị lỗi trùng lặp khi chạy lại script nhiều lần
                PlayerFixture.objects.update_or_create(
                    fixture=fixture,
                    player=player_obj,
                    defaults={
                        'rating': str(rating) if rating else None,
                        'minutes': minutes,
                        'min_in': min_in,
                        'min_out': min_out,
                        'goals': goals,
                        'assists': assists,
                        'yellow_card': yellow_card,
                        'red_card': red_card,
                    }
                )

        time.sleep(1)

    print("Thành công! Đã đồng bộ xong dữ liệu chi tiết các trận đấu.")


if __name__ == '__main__':
    fetch_fixture_players()