import os
import django
import re

# Kích hoạt môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_web.settings')
django.setup()

# Sếp nhớ kiểm tra lại xem model Fixture đang nằm ở app nào để import cho đúng nhé
from club.models import Club, Standing, Fixture


def get_round_number(round_str):
    """
    Hàm phụ trợ: Rút trích con số từ chuỗi tên vòng đấu để sắp xếp.
    Ví dụ: "Regular Season - 5" -> Lấy ra số 5
    """
    match = re.search(r'\d+', round_str)
    return int(match.group()) if match else 0


def run_tinh_diem():
    print("⏳ Bắt đầu tính toán Bảng xếp hạng theo vòng...")

    # 1. Lấy tất cả các trận đã đá (có tỷ số không bị rỗng)
    # Giả định cột tỷ số của sếp tên là home_score và away_score
    played_fixtures = Fixture.objects.filter(home_score__isnull=False, away_score__isnull=False)

    if not played_fixtures.exists():
        print("❌ Chưa có trận đấu nào có kết quả để tính điểm!")
        return

    # 2. Lấy danh sách các vòng đấu và sắp xếp từ Vòng 1 -> Vòng cuối
    rounds = set(played_fixtures.values_list('round_name', flat=True))
    sorted_rounds = sorted(list(rounds), key=get_round_number)

    # 3. Tạo một bộ nhớ tạm (Dictionary) để lưu điểm cộng dồn của 20 đội
    stats = {}
    for club in Club.objects.all():
        stats[club.club_id] = {
            'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
            'gf': 0, 'ga': 0, 'pts': 0
        }

    # 4. Quét từng vòng đấu để cộng điểm
    for round_name in sorted_rounds:
        print(f"  -> Đang chốt sổ: {round_name}")
        fixtures_in_round = played_fixtures.filter(round_name=round_name)

        # Tính toán kết quả cho các trận trong vòng này
        for f in fixtures_in_round:
            home_id = f.home_team_id
            away_id = f.away_team_id
            h_score = f.home_score
            a_score = f.away_score

            # Bỏ qua nếu ID đội bóng không tồn tại trong DB
            if home_id not in stats or away_id not in stats:
                continue

            # Cập nhật số trận & bàn thắng/thua
            stats[home_id]['played'] += 1
            stats[away_id]['played'] += 1

            stats[home_id]['gf'] += h_score
            stats[home_id]['ga'] += a_score
            stats[away_id]['gf'] += a_score
            stats[away_id]['ga'] += h_score

            # Cập nhật Điểm số và Thắng/Hòa/Thua
            if h_score > a_score:  # Đội nhà thắng
                stats[home_id]['won'] += 1
                stats[home_id]['pts'] += 3
                stats[away_id]['lost'] += 1
            elif h_score < a_score:  # Đội khách thắng
                stats[away_id]['won'] += 1
                stats[away_id]['pts'] += 3
                stats[home_id]['lost'] += 1
            else:  # Hòa
                stats[home_id]['drawn'] += 1
                stats[home_id]['pts'] += 1
                stats[away_id]['drawn'] += 1
                stats[away_id]['pts'] += 1

        # 5. Lưu cục dữ liệu cộng dồn vào Database cho vòng đấu hiện tại
        for club_id, data in stats.items():
            # Chỉ lưu những đội đã thực sự đá (tránh cào nhầm đội nghỉ thi đấu)
            if data['played'] > 0:
                Standing.objects.update_or_create(
                    club_id=club_id,
                    round_name=round_name,
                    defaults={
                        'played': data['played'],
                        'won': data['won'],
                        'drawn': data['drawn'],
                        'lost': data['lost'],
                        'goals_for': data['gf'],
                        'goals_against': data['ga'],
                        'goal_difference': data['gf'] - data['ga'],
                        'points': data['pts']
                    }
                )

    print("✅ Hoàn tất! Đã cập nhật xong Bảng Xếp Hạng vào Database.")


if __name__ == '__main__':
    run_tinh_diem()