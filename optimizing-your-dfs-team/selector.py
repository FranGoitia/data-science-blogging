import json
import random
import itertools as it
from collections import defaultdict, OrderedDict
from sqlalchemy import and_
from sqlalchemy.sql import func

from model import create_session
from model.personnel import Player
from model.stats import PlayerMatchStats
from analytics.fantasy.knapsack import Knapsack
from analytics.fantasy.annealing import GDTAnnealing

Session = create_session()

POSITIONS = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']


class Selector:

    def __init__(self):
        self.players_db = {pl.id: pl for pl in Session.query(Player).all()}

    def select(self, tactic, algorithm):
        tactic_setup = OrderedDict([(pos, tactic[pos]) for pos in POSITIONS])
        players = self._sort_players(matches_filter=True, availability_filter=True)
        starters, value, cost = self._select_starters(tactic, players, algorithm)
        self._show_selection(tactic_setup, starters, cost, value, 'STARTERS')
        budget_remaining = self.total_budget - cost
        print("budget remaining:", budget_remaining)
        bench, bench_value, bench_cost = self._select_bench(starters, players, 'knapsack', budget_remaining)
        self._show_selection('-', bench, bench_cost, bench_value, 'BENCH')

        print('\n')
        print('Total Value:', (value + bench_value) * -1)
        print('Total Cost:', cost + bench_cost)

    def _select_starters(self, tactic, players, algorithm):
        if algorithm == 'knapsack':
            players, tactic, cost, value, team = Knapsack().optimize(players, tactic, self.total_budget)
        elif algorithm == 'annealing':
            random.shuffle(players)
            pls_by_positions = defaultdict(list)
            for pl in players:
                pls_by_positions[pl['position']].append(pl)

            initial_team = defaultdict(list)
            for position, pls_needed in tactic.items():
                for _ in range(pls_needed):
                    while True:
                        player = random.choice(pls_by_positions[position])
                        if player not in initial_team[position]:
                            initial_team[position].append(player)
                            break

            team, value, cost = self._annealing(initial_team, tactic, self.total_budget - self.bench_budget, pls_by_positions)

        return team, value, cost

    def _select_bench(self, starters, all_players, algorithm, budget_remaining):
        starters_ids = set(pl['id'] for pos in starters.values() for pl in pos)
        players_available = list(filter(lambda p: p['id'] not in starters_ids, all_players))
        players_available = list(filter(lambda p: p['price'] - 2000000 < budget_remaining, players_available))
        pls_by_positions = defaultdict(list)
        for pl in players_available:
            pls_by_positions[pl['position']].append(pl)

        gk = starters['Goalkeeper'][0]
        gk_sub = sorted(filter(lambda pl: pl['position'] == 'Goalkeeper' and pl['club'] == gk['club'] and pl['id'] != gk['id'],
                               self._sort_players(matches_filter=False, availability_filter=False)),
                        key=lambda p: p['valuation'])[-1]
        tactic = {'Goalkeeper': 0, 'Defender': 1, 'Midfielder': 1, 'Forward': 1}
        budget_remaining_2 = budget_remaining - gk_sub['price']
        if algorithm == 'knapsack':
            _, _, budget_remaining_2, value, bench = Knapsack().optimize(players_available[:100], tactic, budget_remaining_2)
            cost = budget_remaining - budget_remaining_2
            for pos, pls in bench.items():
                bench[pos] = [dict(pls[0])]
            bench['Goalkeeper'] = [gk_sub]
        elif algorithm == 'annealing':
            initial_team = {}
            for pos in POSITIONS:
                initial_team[pos] = [sorted(pls_by_positions[pos], key=lambda x: x['price'])[0]]
            bench, value, cost = self._annealing(initial_team, tactic, budget_remaining, pls_by_positions)

        return bench, value * -1, cost

    def _sort_players(self, matches_filter, availability_filter):
        pls_matches_amount = dict(Session.query(PlayerMatchStats.player_id, func.count(self.points_column)
            ).filter(and_(PlayerMatchStats.player_id.in_(self.pls_dfs_mapper.values()), self.points_column is not None)
            ).group_by(PlayerMatchStats.player_id))

        def has_enough_matches(player):
            return pls_matches_amount.get(player['id']) and pls_matches_amount.get(player['id']) > 7

        def value_player(player):
            if player['valuation'] is not None and player['price'] is not None:
                return player['valuation']
            return 0

        pls_key_data = self._get_pls_key_data()
        players = pls_key_data.values()
        if matches_filter:
            players = filter(has_enough_matches, players)
        if availability_filter:
            players = filter(self._is_available, players)
        return sorted(players, key=value_player, reverse=True)

    def _is_available(self, player):
        raise NotImplementedError

    def _get_pls_key_data(self):
        """return key info por selecting players (position, valuation and price)"""
        pls_points = self._get_pls_points()
        pls_key_data = {}
        for player_gdt_id, player_dfs in self.dfs_data.items():
            player_id = self.pls_dfs_mapper.get(int(player_gdt_id))
            if player_id:
                player = self.players_db[player_id]
                pls_key_data[player_id] = {'position': player.position_type, 'valuation': pls_points.get(player_id),
                                           'price': player.grandt_value, 'id': player_id, 'club': player_dfs['club'],
                                           'name': player.name, 'availability': player.availability}
        return pls_key_data

    def _get_pls_points(self):
        pls_points = Session.query(PlayerMatchStats.player_id, func.avg(self.points_column)
            ).filter(PlayerMatchStats.player_id.in_(self.pls_dfs_mapper.values())
            ).group_by(PlayerMatchStats.player_id)
        return dict(pls_points)

    def _annealing(self, initial_team, tactic, budget, pls_by_positions):
        raise NotImplementedError

    @staticmethod
    def _show_selection(tactic, team, budget, value, type_):
        print('\n')
        print(' {t}'.format(t=type_))
        print('tactic:', tactic)
        print('budget:', budget)
        print('value:', value * (-1))
        for pos in POSITIONS:
            for pl in team[pos]:
                print(pos, pl['name'], pl['club'], pl['valuation'], pl['price'])
            print('___________________')


class GranDT(Selector):

    def __init__(self):
        super(GranDT, self).__init__()
        self.country = 'Argentina'
        self.league = 'Primera División'
        self.season = '2016-2017'
        self.players_db = {pl.id: pl for pl in Session.query(Player).all()}
        self.dfs_data = json.load(open('data/players/grandt.json'))
        self.pls_dfs_mapper = {pl.grandt_id: pl.id for pl in Session.query(Player).all()}
        self.points_column = PlayerMatchStats.gdt_points
        self.total_budget = 75000000
        self.bench_budget = 7000000

    def _is_available(self, player):
        return player['availability'] == 'Starter' or (player['club'] == 'Estrellas' and player['availability'] == 'Bench')

    def _annealing(self, initial_team, tactic, budget, pls_by_positions):
        a = GDTAnnealing(initial_team, tactic, budget, pls_by_positions)
        a.save_state_on_exit = False
        auto_schedule = a.auto(minutes=10)
        auto_schedule['updates'] = 100
        a.set_schedule(auto_schedule)
        team, value = a.anneal()

        budget = sum([pl['price'] for pl in it.chain.from_iterable(team.values())])
        return team, value, budget


def main():
    print('--------------------')
    GranDT().select(tactic={'Goalkeeper': 1, 'Defender': 3, 'Midfielder': 3,
                            'Forward': 4}, algorithm='annealing')
    print('--------------------')
    GranDT().select(tactic={'Goalkeeper': 1, 'Defender': 4, 'Midfielder': 2,
                            'Forward': 4}, algorithm='annealing')
    print('--------------------')


if __name__ == '__main__':
    main()
