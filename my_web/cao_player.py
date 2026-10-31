import os
import django
import requests
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_web.settings')
django.setup()

from club.models import Club, Player, Contract


def fetch_players_for_club(club_id, season_year="2024"):
    try:
        club_obj = Club.objects.get(club_id=club_id)
    except Club.DoesNotExist:
        print(f"Lỗi: Không tìm thấy CLB có club_id = {club_id} trong Database của sếp! Hãy cào CLB trước.")
        return

    url = "https://v3.football.api-sports.io/players"
    headers = {
        'x-rapidapi-key': os.getenv('API_KEY')
    }

    current_page = 1
    total_pages = 1
    count = 0

    while current_page <= total_pages:
        querystring = {"team": club_id, "season": season_year, "page": current_page}
        print(f"Đang xử lý trang {current_page} / {total_pages} ...")

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code != 200:
            print(f"Lỗi gọi API, mã lỗi: {response.status_code}")
            break

        data = response.json()

        paging = data.get('paging', {})
        total_pages = paging.get('total', 1)

        players_list = data.get('response', [])

        if not players_list:
            print(f"Không có dữ liệu trả về cho trang {current_page}!")
            break

        for item in players_list:
            p_info = item['player']

            stats = item['statistics'][0] if item['statistics'] else {}
            games = stats.get('games', {})

            player_obj, created = Player.objects.update_or_create(
                player_id=p_info['id'],
                defaults={
                    'player_name': p_info.get('name'),
                    'player_birth_date': p_info.get('birth', {}).get('date'),
                    'player_birth_place': p_info.get('birth', {}).get('place'),
                    'player_nationality': p_info.get('nationality'),
                    'player_height': p_info.get('height'),
                    'player_weight': p_info.get('weight'),
                    'player_photo': p_info.get('photo'),
                }
            )

            Contract.objects.update_or_create(
                player=player_obj,
                club=club_obj,
                season=season_year,
                defaults={
                    'position': games.get('position'),
                    'number': games.get('number'),
                }
            )
            count += 1

        current_page += 1

    print(f"Thành công! Đã đồng bộ tổng cộng {count} cầu thủ cho CLB: {club_obj.club_name}\n")


if __name__ == '__main__':
    fetch_players_for_club(club_id=66, season_year="2024")