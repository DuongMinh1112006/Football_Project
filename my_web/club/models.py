
from django.db import models
from django.contrib.auth.models import User

class Club(models.Model):
    club_id = models.IntegerField(primary_key=True)
    club_name = models.CharField (max_length = 100)
    club_founded = models.IntegerField(null = True, blank = True)
    club_stadium = models.CharField(max_length = 100)
    club_logo = models.CharField(max_length = 500, null = True, blank = True)

    def __str__(self):
        return self.club_name


class Stadium(models.Model):
    stadium_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length = 100)
    capacity = models.IntegerField(null = True, blank = True)
    address = models.CharField(max_length = 200,null = True, blank = True)
    city = models.CharField(max_length = 100,null = True, blank = True)
    surface = models.CharField(max_length = 100,null = True, blank = True)
    image = models.CharField(max_length = 500,null = True, blank = True)

    club = models.OneToOneField('Club', on_delete = models.SET_NULL, null = True, blank = True)

    def __str__(self):
        return self.name


class Player(models.Model):
    player_id = models.IntegerField(primary_key = True)
    player_name = models.CharField(max_length = 100)
    player_age = models.IntegerField(null = True, blank = True)
    player_birth_date = models.DateField( null = True, blank = True)
    player_birth_place = models.CharField(max_length=100, null = True, blank = True)
    player_nationality = models.CharField(max_length = 100)
    player_height = models.CharField(max_length = 50, null = True, blank = True)
    player_weight = models.CharField(max_length = 50, null = True, blank = True)
    player_photo = models.CharField(max_length=500, null=True, blank=True)


    def __str__(self):
        return self.player_name

class Contract(models.Model):
    player = models.ForeignKey("Player", on_delete = models.CASCADE, null=True, blank=True)
    club = models.ForeignKey("Club", on_delete = models.CASCADE, null=True, blank=True)
    season = models.CharField(max_length=20, default="2024/2025")
    position = models.CharField(max_length=50, null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player.player_name} - {self.club.club_name} ({self.season})"


class Fixture(models.Model):
    fixture_id = models.IntegerField(primary_key = True)
    home_team = models.ForeignKey('Club', on_delete = models.CASCADE, related_name = "home_matches")
    away_team = models.ForeignKey('Club', on_delete = models.CASCADE, related_name = "away_matches")
    match_date = models.DateField(null = True, blank = True)

    home_score = models.IntegerField(null = True, blank = True)
    away_score = models.IntegerField(null = True, blank = True)

    round_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.home_team.club_name}| {self.home_score} - {self.away_score} | {self.away_team.club_name}"


class PlayerFixture(models.Model):

    fixture = models.ForeignKey('Fixture', on_delete=models.CASCADE, related_name='player_stats')
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='fixture_stats')

    rating = models.CharField(max_length=10, null=True, blank=True)  # API-Football thường trả về chuỗi như "7.5"
    minutes = models.IntegerField(default=0, null=True, blank=True)

    goals = models.IntegerField(default=0, null=True, blank=True)
    assists = models.IntegerField(default=0, null=True, blank=True)
    yellow_card = models.IntegerField(default=0, null=True, blank=True)
    red_card = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        unique_together = ('fixture', 'player')

    def __str__(self):
        return f"Cầu thủ {self.player.player_name} - Trận {self.fixture.fixture_id}"



class Standing(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='standings')

    round_name = models.CharField(max_length=100)

    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)

    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)

    points = models.IntegerField(default=0)

    class Meta:
        unique_together = ('club', 'round_name')

    def __str__(self):
        return f"{self.club.club_name} | {self.round_name} | {self.points} "

