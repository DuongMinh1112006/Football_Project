import os
import django
import requests

from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_web.settings')
django.setup()

from club.models import Club, Stadium


def run():
    url = "https://v3.football.api-sports.io/teams"
    querystring = {
        "league": "39",
        "season": "2024"
    }

    headers = {
        "x-apisports-key": os.getenv('API_KEY'),
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
    except Exception as e:
        print(f"Lỗi mạng: {e}")
        return

    if not data.get('response'):
        print(f"Lỗi API: {data.get('errors')}")
        return

    for item in data['response']:
        team = item['team']
        team_id = team['id']
        team_name = team['name']
        founded = team.get('founded')
        logo = team.get('logo')

        venue = item['venue']
        stadium_id = venue.get('id')
        stadium_name = venue.get('name', 'Chưa cập nhật')

        try:
            Club.objects.update_or_create(
                club_id=team_id,
                defaults={
                    'club_name': team_name,
                    'club_founded': founded,
                    'club_stadium': stadium_name,  # Cột này trong Club sếp đang để CharField
                    'club_logo': logo
                }
            )
            print(f"Đã lưu Club: {team_name}")

            if stadium_id:
                capacity = venue.get('capacity')
                address = venue.get('address')
                city = venue.get('city')
                surface = venue.get('surface')
                image = venue.get('image')

                Stadium.objects.update_or_create(
                    stadium_id=stadium_id,
                    defaults={
                        'name': stadium_name,
                        'capacity': capacity,
                        'address': address,
                        'city': city,
                        'surface': surface,
                        'image': image,
                        'club_id': team_id
                    }
                )
                print(f"   -> Đã lưu Stadium: {stadium_name}")
            else:
                print(f"   -> ⚠Bỏ qua Stadium của {team_name} vì API không trả về ID sân bóng.")

        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu đội {team_name}: {e}")


if __name__ == '__main__':
    run()