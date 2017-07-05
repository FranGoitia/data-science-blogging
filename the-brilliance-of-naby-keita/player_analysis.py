import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  # noqa
from sqlalchemy.sql import func
from sklearn.cluster import AgglomerativeClustering

from model import create_session
from model.overview import League
from model.personnel import Player
from model.stats import PlayerMatchStats

Session = create_session()


TEMPLATES = {
    'Midfielder': ['goals', 'shots_ot', 'dribbles_won', 'big_chances_created',
                   'acc_through_balls', 'key_passes', 'assists', 'tackles_won_adj', 'interceptions_adj',
                   'blocks'],
}


LABELS = {
    'goals': 'goals',
    'shots_ot': 'shots_ot',
    'dribbles_won': 'dribbles',
    'big_chances_created': 'big_chances_cr',
    'acc_through_balls': 'through_blls',
    'key_passes': 'key_p',
    'assists': 'assists',
    'tackles_won_adj': 'tackles',
    'interceptions_adj': 'ints',
    'blocks': 'blocks',
    'errors_to_goal': 'err_to_goals',
}

METRICS = [
    'goals',
    'shots',
    'shots_ot',
    'shots_off',
    'shots_blocked',
    'shots_on_post',
    'shots_headers',
    'dribbles_won',
    'dribbles_lost',
    'big_chances_created',
    'tackled',
    'untackled',
    'fouled',
    'offsides',
    'turnovers',
    'passes',
    'acc_passes',
    'pass_acc',
    'long_balls',
    'acc_long_balls',
    'long_balls_acc',
    'through_balls',
    'acc_through_balls',
    'through_balls_acc',
    'headed_passes',
    'acc_headed_passes',
    'headed_passes_acc',
    'key_passes',
    'assists',
    'crosses',
    'acc_crosses',
    'cross_acc',
    'key_crosses',
    'crosses_assists',
    'corners',
    'tackles_won',
    'tackles_won_adj',
    'tackles_lost',
    'interceptions',
    'interceptions_adj',
    'clearances',
    'clearances_adj',
    'passed_by',
    'unpassed',
    'blocks',
    'blocked_shots',
    'blocked_shots_adj',
    'blocked_crosses',
    'blocked_passes',
    'aerials_won',
    'aerials_lost',
    'fouls_committed',
    'fouls_suffered',
    'saves',
    'claims',
    'punches',
    'errors_to_shot',
    'errors_to_goal',
    'yellow_cards',
    'red_cards',
    'clean_sheet',
    'goals_against',
    'missed_penalties',
    'saved_penalties',
    'mins_played',
]

NEGATIVE_METRICS = ['passed_by', 'errors_to_goal', 'errors_to_shot']


class PlayerAnalysis:

    def __init__(self, players_df, player, player_league, leagues):
        self.players_df = players_df.loc[players_df['league_id'].isin(leagues)]
        self.players_df = self.players_df.loc[self.players_df['player_positions'].apply(lambda x: x is not None and len(set(x).intersection(set(['MC', 'DMC', 'AMC']))) > 0)]
        self.players_df = self.players_df.loc[self.players_df['mins_played'] > 1200]
        self.players_df['player_name_season'] = self.players_df.apply(lambda x: x['player_name'] + ' ' + x['league_season'], axis=1)
        self.player = player
        self.player_league = player_league
        self._normalization()

    def _normalization(self):
        for col in self.players_df.columns:
            if col in METRICS and col != 'mins_played':
                if col in NEGATIVE_METRICS:
                    self.players_df[col] = self.players_df[col] * (-1)
                self.players_df[col] = self.players_df[col] / self.players_df['mins_played'] * 90
                self.players_df[col+'_nu'] = (self.players_df[col] - self.players_df[col].mean()) / self.players_df[col].std()
                self.players_df[col+'_pr'] = self.players_df[col].rank(pct=True)

    def plot_stats(self):
        player_df = (self.players_df[self.players_df['player_id'] == self.player.id]).round(2)
        pr_metrics_x = [m+'_pr' for m in TEMPLATES[self.player.position_type]]
        pr_metrics_y = [player_df[s].iloc[0] for s in pr_metrics_x]
        metrics_y = [player_df[m].iloc[0] for m in TEMPLATES[self.player.position_type]]

        fig, ax = plt.subplots()
        width = 0.75
        idxs = np.arange(len(pr_metrics_y))
        ax.barh(idxs, pr_metrics_y, width)
        ax.set_yticks(idxs+width/8)
        ax.set_yticklabels([LABELS[m] for m in TEMPLATES[self.player.position_type]], minor=False)
        for i, m in enumerate(pr_metrics_y):
            ax.text(m - 0.05, i - .125, str(metrics_y[i]), ha='center')

        plt.title('{p} - {l} {s}'.format(p=self.player.name, l=self.player_league.name, s=self.player_league.season))
        plt.xlabel('Percentiles')
        plt.show()

    def clusterize(self):
        kmeans = AgglomerativeClustering(n_clusters=30)
        metrics = [m+'_pr' for m in TEMPLATES[self.player.position_type]]
        pls_stats = self.players_df[metrics].as_matrix()
        kmeans.fit_predict(pls_stats)
        for idx, (df_idx, _) in enumerate(self.players_df.iterrows()):
            self.players_df.set_value(df_idx, 'cluster', kmeans.labels_[idx])

        player_cluster = self.players_df[self.players_df['player_name'] == self.player.name]['cluster'].iloc[0]
        cluster = self.players_df[self.players_df['cluster'] == player_cluster]
        h = sns.heatmap(data=cluster[metrics], cmap='RdYlGn', linewidths=.05,
                        xticklabels=[LABELS[m] for m in TEMPLATES[self.player.position_type]],
                        yticklabels=cluster['player_name_season'].values, cbar=False)
        h.set_yticklabels(h.get_yticklabels(), rotation=-360)
        plt.show()

    def threshold_analysis(self, tolerance):
        player_df = self.players_df[(self.players_df['player_name'] == self.player.name) & (self.players_df['league_id'] == self.player_league.id)]
        df = self.players_df
        for col in TEMPLATES[self.player.position_type]:
            col_threshold = player_df[col].values[0] * (1 - tolerance.get(col, 0))
            df = df.loc[df[col] >= col_threshold]

        metrics = [m+'_pr' for m in TEMPLATES[self.player.position_type]]
        h = sns.heatmap(data=df[metrics], cmap='RdYlGn', linewidths=.05,
                        xticklabels=[LABELS[m] for m in TEMPLATES[self.player.position_type]],
                        yticklabels=df['player_name_season'].values, cbar=False)
        h.set_yticklabels(h.get_yticklabels(), rotation=-360)
        plt.show()


def get_dataframe(player):
    stats = TEMPLATES[player.position_type].copy()
    stats += ['mins_played']
    cols = [PlayerMatchStats.player_id, Player.name, Player.positions, PlayerMatchStats.league_id, League.name, League.season] + \
        [func.sum(getattr(PlayerMatchStats, m)) for m in stats]
    query = Session.query(*cols).join(PlayerMatchStats.player).join(PlayerMatchStats.league)
    query = query.group_by(PlayerMatchStats.player_id, Player.name, Player.positions, PlayerMatchStats.league_id, League.name, League.season)
    df = pd.read_sql(query.statement, Session.connection())
    df.columns = ['player_id', 'player_name', 'player_positions', 'league_id', 'league_name', 'league_season'] + stats
    return df


def naby_keita_profile():
    player = Session.query(Player).filter_by(name='Naby Keita').one()
    league = Session.query(League).filter_by(name='Bundesliga', season='2016-2017').one()
    df = get_dataframe(player)
    leagues = [l.id for l in Session.query(League) if l.season in ['2015-2016', '2016-2017']]
    analysis = PlayerAnalysis(df, player, league, leagues)
    analysis.plot_stats()
    analysis.clusterize()
    analysis.threshold_analysis({'dribbles_won': 1, 'tackles_won_adj': 1, 'interceptions_adj': 1, 'blocks': 1, 'errors_to_goal': 1})
    analysis.threshold_analysis({'dribbles_won': 1, 'goals': 1, 'shots_ot': 1, 'big_chances_created': 1,
                                 'acc_through_balls': 1, 'key_passes': 1, 'assists': 1,
                                 'dribbles_won': 1, 'interceptions_adj': 0.1})


if __name__ == '__main__':
    naby_keita_profile()
