class Params:
    CURRENT_ITERATION = -1
    ITERATIONS = 1000
    MULTIPROCESSING_POOL_SIZE = 10

    STAT_WEIGHTS = [0.6, 0.3, 0.1, 0.0]
    GOODNESS_WEIGHT = 0.7
    AVERAGE_HITRATE = 0.2

    # hitrate for a 1.0 batter vs a 0.1 pitcher:
    # 1 + GOODNESS_WEIGHT / 0.1 + GOODNESS_WEIGHT WEIGHT / AVERAGE_HITRATE

    LEAGUE_SIZE = 100
    MATCHMAKING_SPREAD = 6
    GAME_COUNT = 100

    def __init__(self, current_iteration: int = 0):
        self.current_iteration = current_iteration

    # oh god don't look at this it's toxic
    def __getstate__(self):
        d = {k: v for k, v in Params.__dict__.items() if k[0] != "_"}
        d.update(self.__dict__)
        return d

    def __setstate__(self, state):
        for attr in dir(Params):
            if attr in state and attr[0] != "_":
                setattr(Params, attr, state[attr])
        self.__dict__ = state
        Params.CURRENT_ITERATION = self.current_iteration
