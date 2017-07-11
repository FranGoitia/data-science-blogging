from collections import defaultdict


class Knapsack:

    def optimize(self, players, tactic, budget, value=0, formation=defaultdict(tuple), cache={}):
        if self.get_in_cache(players, tactic, budget, value, formation, cache):
            return self.get_in_cache(players, tactic, budget, value, formation, cache)
        # base cases
        if len(players) == 0:
            return players, tactic, budget, value, formation
        cur_player = players[0]
        # no room in tactic for player or no budget
        if (tactic[cur_player['position']] - 1 < 0) or (budget - cur_player['price'] < 0):
            rv = self.optimize(players[1:], tactic, budget, value, formation)
            self.insert_to_cache(players, tactic, budget, value, formation, cache, rv)
            return rv
        # formation is full
        if (len(set(tactic.values()))) == 0 and (tactic[0] == 0):
            return players, tactic, budget, value, formation, cache
        # recursive cases
        else:
            # player is added to formation
            w_tactic = tactic.copy()
            w_tactic[cur_player['position']] -= 1
            w_formation = formation.copy()
            w_formation[cur_player['position']] += (frozenset(cur_player.items()),)
            _, _, _, w_value, _ = rv_w = self.optimize(players[1:], w_tactic, budget - cur_player['price'],
                                                       value + cur_player['valuation'], w_formation)
            # player is not added to formation
            _, _, _, o_value, _ = rv_o = self.optimize(players[1:], tactic, budget, value, formation)
            # return decision with more value
            if w_value > o_value:
                self.insert_to_cache(players, tactic, budget, value, formation, cache, rv_w)
            else:
                self.insert_to_cache(players, tactic, budget, value, formation, cache, rv_o)
            return self.get_in_cache(players, tactic, budget, value, formation, cache)

    @staticmethod
    def get_in_cache(players, tactic, budget, value, formation, cache):
        return cache.get((tuple(map(lambda x: frozenset(x.items()), players)),
                         frozenset(tactic.items()), budget, value,
                         frozenset(formation.items())))

    @staticmethod
    def insert_to_cache(players, tactic, budget, value, formation, cache, rv):
        cache[(tuple(map(lambda x: frozenset(x.items()), players)), frozenset(tactic.items()),
               budget, value, frozenset(formation.items()))] = rv
