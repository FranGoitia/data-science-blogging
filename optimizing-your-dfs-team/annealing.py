import random
import itertools as it
from simanneal import Annealer


class Annealing(Annealer):

    def __init__(self, state, tactic, budget, pls_by_positions):
        self.budget = budget
        self.tactic = tactic
        self.pls_by_positions = pls_by_positions
        super(Annealing, self).__init__(state)

    def move(self):
        """Replace a player in a random position in tactic"""
        while True:
            pos = self._move_position()
            idx = random.randint(0, len(self.state[pos]) - 1)
            out_player = self.state[pos][idx]
            new_player = random.choice(self.pls_by_positions[pos])
            if self._is_allowed(new_player, out_player, pos):
                self.state[pos][idx] = new_player
                break

    def _move_position(self):
        p = random.random()
        gks = self.tactic['Goalkeeper']
        dfs = self.tactic['Defender']
        mds = self.tactic['Midfielder']
        if p <= gks/11:
            return 'Goalkeeper'
        elif p > gks/11 and p <= (gks+dfs)/11:
            return 'Defender'
        elif p > (gks+dfs)/11 and p <= (gks+dfs+mds)/11:
            return 'Midfielder'
        else:
            return 'Forward'

    def _is_allowed(self, new_player, out_player, pos):
        raise NotImplementedError

    def energy(self):
        return - sum(pl['valuation'] for pl in it.chain.from_iterable(self.state.values()))


class GDTAnnealing(Annealing):

    def __init__(self, state, tactic, budget, pls_by_positions):
        super(GDTAnnealing, self).__init__(state, tactic, budget, pls_by_positions)

    def _is_allowed(self, new_player, out_player, pos):
        stars = [pl for pl in it.chain.from_iterable(self.state.values()) if pl['club'] == 'Estrellas']
        star_replacement = out_player['club'] == 'Estrellas' and new_player['club'] == 'Estrellas'
        is_on_team = new_player['id'] in set(map(lambda pl: pl['id'], self.state[pos]))
        teammate_in_pos = new_player['club'] in set(map(lambda pl: pl['club'], self.state[pos]))-set(out_player['club'])
        state_budget = sum(pl['price'] for pl in it.chain.from_iterable(self.state.values()))
        state_budget = state_budget - out_player['price'] + new_player['price']
        return not is_on_team and not teammate_in_pos and state_budget <= self.budget and (new_player['club'] != 'Estrellas' or (len(stars) == 0 or star_replacement))
