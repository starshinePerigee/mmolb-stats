from random import shuffle, randint

import pandas as pd

from sim import params, Team, play_game


class League:
    def __init__(self):
        self.teams = [Team(i + 1) for i in range(params.LEAGUE_SIZE)]
        # shuffle(self.teams)

    def generate_matchups(self) -> list[tuple[Team, Team]]:
        sorted_teams = sorted(self.teams, key=lambda t: t.wins)
        matchups: list[tuple[Team, Team]] = []
        allocated = {t: False for t in self.teams}

        for i, team in enumerate(sorted_teams):
            if allocated[team]:
                continue
            # pull range and sort; keep in mind all teams above have already been allocated
            candidate_teams = sorted_teams[i + 1 : i + params.MATCHMAKING_SPREAD + 1]
            viable_teams = list(filter(lambda t: not allocated[t], candidate_teams))
            if not viable_teams:
                raise ValueError(f"Error matchmaking on iteration {i}")
            shuffle(viable_teams)
            match = viable_teams[0]
            matchups += [(team, match)]
            allocated[team] = True
            allocated[match] = True
        return matchups

    def run_season(self):
        for g in range(params.GAME_COUNT):
            for matchup in self.generate_matchups():
                if randint(0, 1):
                    play_game(matchup[0], matchup[1])
                else:
                    play_game(matchup[0], matchup[1])

    def to_dataframes(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        team_df = pd.DataFrame([team.stat_dict() for team in self.teams])
        player_df = pd.DataFrame([player.stat_dict() for team in self.teams for player in team.players])
        return team_df, player_df


"""
How random is "generate_matchups" anyway?

Not amazingly. Given 1 million 100-team matchup generations with a matchup window of 10,
here's the total count for team distances:

1: 4051625
2: 4181747
3: 4335851
4: 4521570
5: 4724376
6: 4979594
7: 5263295
8: 5588526
9: 5963519
10: 6389897

Clearly, it's more likely to match on the far edge, which makes logical sense -
to be picked, a team must both be picked and not picked on previous rounds. 

l = League()
d = {i: 0 for i in range(1, params.MATCHMAKING_SPREAD + 1)}

for i in range(params.ITERATIONS):
    if i % 10000 == 0:
        print(i)
    m = l.generate_matchups()
    for g in m:
        d[g[1].t_id - g[0].t_id] += 1
for i, v in d.items():
    print(f"{i}: {v}")

"""


if __name__ == "__main__":
    l = League()
    l.run_season()
    for df in l.to_dataframes():
        print(df)

