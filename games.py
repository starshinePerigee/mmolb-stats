from random import random

from params import STAT_WEIGHTS, WEIGHT_WEIGHT, AVERAGE_HITRATE, ITERATIONS


class Player:
    def __init__(
        self,
        team: int,
        scale_min: float = 0,
        scale_max: float = 1,
        is_pitcher: bool = False,
    ):
        self.team = team
        self.scale = (scale_min + scale_max) / 2
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

    def stat_dict(self) -> dict[str, float | int | bool]:
        d = {"team": self.team, "scale": self.scale}
        d.update({f"attr_{a}": v for a, v in enumerate(self.attributes)})
        d.update(
            {"at_bats": self.at_bats, "hits": self.hits, "is_pitcher": self.is_pitcher}
        )
        return d


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
        team_id: int,
        base_min: float = 0,
        base_max: float = 1,
        good_min: float = 0,
        good_max: float = 1,
    ):
        self.t_id = team_id
        self.seed_stats = {
            "base_min": base_min,
            "base_max": base_max,
            "good_min": good_min,
            "good_max": good_max,
        }

        self.pitchers = [Player(self.t_id, good_min, good_max)] + [
            Player(self.t_id, base_min, base_max, True) for __ in range(4)
        ]
        self.batters = [Player(self.t_id, good_min, good_max)] + [
            Player(self.t_id, base_min, base_max) for __ in range(9)
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

    def stat_dict(self) -> dict[str, float | int | bool]:
        d = self.seed_stats.copy()
        d.update(
            {
                "games": self.games,
                "wins": self.games,
                "total_runs": self.runs,
                "total_runs_surrendered": self.runs_surrendered,
            }
        )
        for i, p in enumerate(self.pitchers):
            d.update({f"p{i}_{k}": v for k, v in p.stat_dict().items()})
        for i, b in enumerate(self.pitchers):
            d.update({f"b{i}_{k}": v for k, v in b.stat_dict().items()})
        return d

    def __hash__(self):
        return self.t_id

    def __str__(self):
        return f"Team {self.t_id:03}"

    def __repr__(self):
        return f"<{self}>"


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


"""
How unfair is this simulation?

across 1 million games, a 1-2 stat team beats a 0-1 stat team 96.7% of the time, with an average run diff of 11.7.
a 0.1 - 1.1 team beata  0-1 stat team 60.2% of the time, with an average run diff of 1.28

"""


if __name__ == "__main__":
    a_wins = 0
    a_runs = 0
    b_runs = 0
    a = Team(1, 0.1, 1.1)
    b = Team(2, 0, 1)
    for i in range(ITERATIONS):
        if i % 100 == 0:
            a_wins += a.wins
            a_runs += a.runs
            b_runs += b.runs
            a = Team(1, 0.1, 1.1)
            b = Team(2, 0, 1)
        if i % 10000 == 0:
            print(i)
        play_game(a, b)
    a_wins += a.wins
    a_runs += a.runs
    b_runs += b.runs
    print(
        f"{a_wins} wins, with a {(a_runs-b_runs)/1_000_000} run diff {a_runs} - {b_runs}"
    )
