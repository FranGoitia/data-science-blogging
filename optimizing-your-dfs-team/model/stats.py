#!/usr/bin/env python
from sqlalchemy import (Column, Integer, ForeignKey, UniqueConstraint,
                        Index, Date, Boolean)
from sqlalchemy.types import Float
from sqlalchemy.orm import relationship

from model import Base, enums
from model.overview import Match


class TeamMatchStats(Base):
    __tablename__ = 'teams_matches_stats'

    id = Column(Integer, primary_key=True)
    match_id = Column(ForeignKey('matches.id'), index=True, nullable=False)
    match = relationship('Match', backref='teams_stats')
    date = Column(Date, nullable=False)
    league_id = Column(ForeignKey('leagues.id'), index=True, nullable=False)
    league = relationship('League')
    team_id = Column(ForeignKey('teams.id'), index=True, nullable=False)
    team = relationship('Team', backref='matches_stats')
    loc = Column(enums.locations, index=True)

    subs = Column(Integer, default=0)
    # offensive
    goals = Column(Integer, default=0)
    shots = Column(Integer, default=0)
    shots_ot = Column(Integer, default=0)
    shots_off = Column(Integer, default=0)
    shots_blocked = Column(Integer, default=0)
    shots_on_post = Column(Integer, default=0)
    shots_headers = Column(Integer, default=0)
    dribbles_won = Column(Integer, default=0)
    dribbles_lost = Column(Integer, default=0)
    big_chances_created = Column(Integer, default=0)
    tackled = Column(Integer, default=0)
    untackled = Column(Integer, default=0)
    fouled = Column(Integer, default=0)
    offsides = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    possession = Column(Float)

    # passing
    passes = Column(Integer, default=0)
    acc_passes = Column(Integer, default=0)
    pass_acc = Column(Float)
    long_balls = Column(Integer, default=0)
    acc_long_balls = Column(Integer, default=0)
    long_balls_acc = Column(Float)
    through_balls = Column(Integer, default=0)
    acc_through_balls = Column(Integer, default=0)
    through_balls_acc = Column(Float)
    headed_passes = Column(Integer, default=0)
    acc_headed_passes = Column(Integer, default=0)
    headed_passes_acc = Column(Float)
    key_passes = Column(Integer, default=0)
    crosses = Column(Integer, default=0)
    acc_crosses = Column(Integer, default=0)
    cross_acc = Column(Float)
    key_crosses = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    passes_assists = Column(Integer, default=0)
    crosses_assists = Column(Integer, default=0)

    corners = Column(Integer, default=0)

    # defensive
    tackles_won = Column(Integer, default=0)
    tackles_lost = Column(Integer, default=0)
    tackles_won_adj = Column(Float, default=0)
    interceptions = Column(Integer, default=0)
    interceptions_adj = Column(Float, default=0)
    clearances = Column(Integer, default=0)
    clearances_adj = Column(Float, default=0)
    passed_by = Column(Integer, default=0)
    unpassed = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    blocked_shots_adj = Column(Float, default=0)
    blocked_shots = Column(Integer, default=0)
    blocked_crosses = Column(Integer, default=0)
    blocked_passes = Column(Integer, default=0)
    aerials_won = Column(Integer, default=0)
    aerials_lost = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)
    fouls_suffered = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    claims = Column(Integer, default=0)
    punches = Column(Integer, default=0)
    saved_penalties = Column(Integer, default=0)
    missed_penalties = Column(Integer, default=0)
    scored_penalties = Column(Integer, default=0)
    errors_to_shot = Column(Integer, default=0)
    errors_to_goal = Column(Integer, default=0)
    clean_sheet = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)

    # disciplinary
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    UniqueConstraint(match_id, team_id)
    Index('teams_m_st_crit_idx', team_id, league_id, loc, date)


class PlayerMatchStats(Base):
    __tablename__ = 'players_matches_stats'

    id = Column(Integer, primary_key=True)
    match_id = Column(ForeignKey('matches.id'), index=True, nullable=False)
    match = relationship('Match', backref='pls_stats')
    date = Column(Date, nullable=False)
    league_id = Column(ForeignKey('leagues.id'), index=True, nullable=False)
    league = relationship('League')
    player_id = Column(ForeignKey('players.id'), index=True, nullable=False)
    player = relationship('Player', backref='matches_stats')
    loc = Column(enums.locations, index=True)

    mins_played = Column(Float)
    subbed_in = Column(Boolean)
    subbed_out = Column(Boolean)
    # offensive
    goals = Column(Integer, default=0)
    shots = Column(Integer, default=0)
    shots_ot = Column(Integer, default=0)
    shots_off = Column(Integer, default=0)
    shots_blocked = Column(Integer, default=0)
    shots_on_post = Column(Integer, default=0)
    shots_headers = Column(Integer, default=0)
    dribbles_won = Column(Integer, default=0)
    dribbles_lost = Column(Integer, default=0)
    big_chances_created = Column(Integer, default=0)
    tackled = Column(Integer, default=0)
    untackled = Column(Integer, default=0)
    fouled = Column(Integer, default=0)
    offsides = Column(Integer, default=0)
    turnovers = Column(Integer, default=0)
    possession = Column(Float)

    # passing
    passes = Column(Integer, default=0)
    acc_passes = Column(Integer, default=0)
    pass_acc = Column(Float)
    long_balls = Column(Integer, default=0)
    acc_long_balls = Column(Integer, default=0)
    long_balls_acc = Column(Float)
    through_balls = Column(Integer, default=0)
    acc_through_balls = Column(Integer, default=0)
    through_balls_acc = Column(Float)
    headed_passes = Column(Integer, default=0)
    acc_headed_passes = Column(Integer, default=0)
    headed_passes_acc = Column(Float)
    key_passes = Column(Integer, default=0)

    crosses = Column(Integer, default=0)
    acc_crosses = Column(Integer, default=0)
    cross_acc = Column(Float)
    key_crosses = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    passes_assists = Column(Integer, default=0)
    crosses_assists = Column(Integer, default=0)

    corners = Column(Integer, default=0)

    # defensive
    tackles_won = Column(Integer, default=0)
    tackles_won_adj = Column(Float, default=0)
    tackles_lost = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    interceptions_adj = Column(Float, default=0)
    clearances = Column(Integer, default=0)
    clearances_adj = Column(Float, default=0)
    passed_by = Column(Integer, default=0)
    unpassed = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    blocked_shots_adj = Column(Float, default=0)
    blocked_shots = Column(Integer, default=0)
    blocked_crosses = Column(Integer, default=0)
    blocked_passes = Column(Integer, default=0)
    aerials_won = Column(Integer, default=0)
    aerials_lost = Column(Integer, default=0)
    fouls_committed = Column(Integer, default=0)
    fouls_suffered = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    claims = Column(Integer, default=0)
    punches = Column(Integer, default=0)
    saved_penalties = Column(Integer, default=0)
    missed_penalties = Column(Integer, default=0)
    scored_penalties = Column(Integer, default=0)
    errors_to_shot = Column(Integer, default=0)
    errors_to_goal = Column(Integer, default=0)
    clean_sheet = Column(Integer, default=0)
    goals_against = Column(Integer, default=0)

    # disciplinary
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)

    wh_points = Column(Float)

    UniqueConstraint(match_id, player_id)
    Index('pls_m_st_crit_idx', player_id, league_id, loc, date)


class PlayerValuation(Base):
    __tablename__ = 'players_valuations'

    id = Column(Integer, primary_key=True)
    week = Column(Integer)
    league_id = Column(ForeignKey('leagues.id'), index=True)
    league = relationship('League')
    player_id = Column(ForeignKey('players.id'), index=True)
    player = relationship('Player')
    valuation = Column(Float)

    UniqueConstraint(week, league_id, player_id)
    Index('pls_pts', week, league_id, player_id)
