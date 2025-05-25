from typing import Callable, Any

import pandas as pd

from sim import params, League


def run_monte_carlo(
    fn: Callable[[pd.DataFrame, pd.DataFrame], dict[str, Any]],
    *,
    mute=False,
) -> pd.DataFrame:
    """
    Runs a sim params.ITERATIONS numbers of time, executing an entire season and then passing
    the resultant team and player dataframes to an external callable.

    Your callable must take in a team and a player dataframe,
    and return a dict with your results columns.
    """

    if params.ITERATIONS > 100:
        print(
            "Warning! Each iteration involves an entire season of baseball. "
            "Execution may take some time!"
        )

    running_data = []
    for i in range(params.ITERATIONS):
        if not mute and i % 10 == 0:
            print(f"Running iteration {i}")
        league = League()
        league.run_season()
        running_data.append(fn(*league.to_dataframes()))

    return pd.DataFrame(running_data)


if __name__ == "__main__":
    params.ITERATIONS = 10

    def find_frauds(team_df, player_df):
        team_df["pythagorean_wins"] = params.GAME_COUNT / (
            1 + ((team_df["total_runs_surrendered"] / team_df["total_runs"]) ** 2)
        )
        team_df["fraudulent_wins"] = team_df["wins"] - team_df["pythagorean_wins"]
        biggest_fraud = team_df.sort_values("fraudulent_wins").iloc[-1]
        return biggest_fraud.to_dict()

    df = run_monte_carlo(find_frauds)
    print(df)
