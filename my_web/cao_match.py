import os
import django
import requests
from django.utils.dateparse import parse_datetime
from django.db.utils import IntegrityError
from dotenv import load_dotenv
load_dotenv()

# ==========================================
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_web.settings')
django.setup()


from club.models import Fixture, Club


def run():
    url = "https://v3.football.api-sports.io/fixtures"
    querystring = {
        "league": "39",
        "season": "2024",
        "round": "Regular Season - 1"
    }

    headers = {
        "x-apisports-key": 'b02cc19027cb67ab71a703f63bb5b4f0'
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
    except Exception as e:
        print(f"Lỗi mạng hoặc không thể kết nối API: {e}")
        return

    if not data.get('response'):
        errors = data.get('errors', 'Không rõ lý do')
        print(f" API không trả về dữ liệu. Lỗi: {errors}")
        return

    for match in data.get('response', []):
        fixture_id = match['fixture']['id']
        round_name = match['league']['round']

        raw_date = match['fixture']['date']
        match_date = parse_datetime(raw_date)

        home_team_id = match['teams']['home']['id']
        away_team_id = match['teams']['away']['id']

        home_score = match['goals']['home']
        away_score = match['goals']['away']

        try:
            Fixture.objects.update_or_create(
                fixture_id=fixture_id,
                defaults={
                    'home_team_id': home_team_id,
                    'away_team_id': away_team_id,
                    'match_date': match_date,
                    'home_score': home_score,
                    'away_score': away_score,
                    'round_name': round_name
                }
            )
            print(f"✅ Đã lưu thành công trận: {fixture_id}")

        except IntegrityError:
            print(
                f" GÃY KHÓA NGOẠI trận {fixture_id}: Đội {home_team_id} hoặc {away_team_id} chưa có trong bảng Club!")
        except Exception as e:
            print(f"❌ Lỗi không xác định ở trận {fixture_id}: {e}")


if __name__ == '__main__':
    run()