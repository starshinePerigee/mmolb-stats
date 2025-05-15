from random import random

from params import STAT_WEIGHTS, WEIGHT_WEIGHT, AVERAGE_HITRATE

class Player:
    def __init__(
            self, scale_min: float = 0, scale_max: float = 1, is_pitcher: bool = False
    ):
        self.attributes = [
            random() * (scale_max - scale_min) + scale_min
            for __ in range(len(STAT_WEIGHTS))
        ]
        self.at_bats = 0
        self.hits = 0
        self.is_pitcher = is_pitcher

    @property
    def weighted(self) -> float:
        return sum(x * y for x, y in zip(self.attributes, STAT_WEIGHTS))


def relative_rate(pitcher: Player, batter: Player) -> float:
    """Returns the hit rate of two players, with this player pitching"""
    ratio = (batter.weighted + WEIGHT_WEIGHT) / (pitcher.weighted + WEIGHT_WEIGHT)
    return ratio * AVERAGE_HITRATE


def pitch(pitcher: Player, batter: Player) -> bool:
    """Returns True if it's a hit"""
    pitcher.at_bats += 1
    batter.at_bats += 1
    is_hit = random() < relative_rate(pitcher, batter)
    if is_hit:
        pitcher.hits += 1
        batter.hits += 1
    return is_hit


class Team:
    def __init__(
            self,
            base_min: float = 0,
            base_max: float = 1,
            good_min: float = 0,
            good_max: float = 1,
    ):
        self.pitchers = [Player(good_min, good_max)] + [
            Player(base_min, base_max, True) for __ in range(4)
        ]
        self.batters = [Player(good_min, good_max)] + [
            Player(base_min, base_max) for __ in range(9)
        ]
        self.games = 0
        self.wins = 0
        self.runs = 0
        self.runs_surrendered = 0
        self.batting_order = 0
        self.pitching_order = 0

    def pitcher(self) -> Player:
        self.pitching_order = (self.pitching_order + 1) % len(self.pitchers)
        return self.pitchers[self.pitching_order]

    def batter(self) -> Player:
        self.batting_order = (self.batting_order + 1) % len(self.batters)
        return self.batters[self.batting_order]

    @property
    def players(self) -> list[Player]:
        return self.pitchers + self.batters


def play_half(hitting: Team, pitching: Team, pitcher: Player) -> int:
    score = 0
    for inning in range(1, 10):
        outs = 0
        while outs < 3:
            if pitch(pitcher, hitting.batter()):
                score += 1
            else:
                outs += 1
    hitting.runs += score
    pitching.runs_surrendered += score
    return score


def play_game(home: Team, away: Team) -> bool:
    home.batting_order = 0
    away.batting_order = 0
    home_score = play_half(home, away, away.pitcher())
    away_score = play_half(away, home, home.pitcher())
    if home_score == away_score:
        if random() < 0.5:
            home_score += 1
        else:
            away_score += 1

    home.games += 1
    away.games += 1
    if home_score > away_score:
        home.wins += 1
        return True
    else:
        away.wins += 1
        return False


if __name__ == "__main__":
    a = Team()
    b = Team()
    for i in range(100):
        play_game(a, b)
    print(f"{a.wins} wins.")



