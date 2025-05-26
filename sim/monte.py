from typing import Callable, Any
from multiprocessing import Pool

import pandas as pd

from sim import params, League


def quick_season(iteration: int = 0):
    l = League()
    l.run_season()
    return l.to_dataframes()


def run_monte_carlo(
    fn: Callable[[pd.DataFrame, pd.DataFrame], dict[str, Any]],
) -> pd.DataFrame:
    """
    Runs a sim params.ITERATIONS numbers of time, executing an entire season and then passing
    the resultant team and player dataframes to an external callable.

    Your callable must take in a team and a player dataframe,
    and return a dict with your results columns.
    """

    if params.ITERATIONS > 1000:
        print(
            f"Warning! Iterations are currently set to {params.ITERATIONS}! "
            "Each iteration involves an entire season of baseball. "
            "Execution may take some time!"
        )

    with Pool(processes=params.MULTIPROCESSING_POOL_SIZE) as pool:
        results = pool.map(quick_season, range(params.ITERATIONS))

    return pd.DataFrame([fn(*result) for result in results])


if __name__ == "__main__":
    params.ITERATIONS = 1000

    def find_frauds(team_df, player_df):
        team_df["pythagorean_wins"] = params.GAME_COUNT / (
            1 + ((team_df["total_runs_surrendered"] / team_df["total_runs"]) ** 2)
        )
        team_df["fraudulent_wins"] = team_df["wins"] - team_df["pythagorean_wins"]
        biggest_fraud = team_df.sort_values("fraudulent_wins").iloc[-1]
        return biggest_fraud.to_dict()

    df = run_monte_carlo(find_frauds)
    print(df.sort_values("fraudulent_wins", ascending=False))
