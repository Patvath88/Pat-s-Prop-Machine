import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelog, leaguegamefinder, teamgamelog
from nba_api.stats.static import players, teams
from datetime import datetime
from tqdm import tqdm

SEASON = "2024-25"
WINDOW_RECENT = 5
WINDOW_LONG = 20

# --- Helper functions ---
def get_player_id(name):
    all_players = players.get_players()
    matches = [p for p in all_players if p['full_name'] == name]
    if matches:
        return matches[0]['id']
    else:
        raise ValueError(f"Player {name} not found")

def get_team_id(name):
    all_teams = teams.get_teams()
    matches = [t for t in all_teams if t['full_name'] == name]
    if matches:
        return matches[0]['id']
    else:
        raise ValueError(f"Team {name} not found")

def get_player_games(player_id):
    df = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON).get_data_frames()[0]
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE')
    return df

def get_team_games(team_id):
    df = teamgamelog.TeamGameLog(team_id=team_id, season=SEASON).get_data_frames()[0]
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values('GAME_DATE')
    return df

def calculate_adjustments(player_name, opponent_name, home=True):
    try:
        player_id = get_player_id(player_name)
        opp_team_id = get_team_id(opponent_name)

        # Player stats
        df_player = get_player_games(player_id)
        df_player = df_player.sort_values('GAME_DATE')

        recent_avg = df_player['PTS'].tail(WINDOW_RECENT).mean()
        long_avg = df_player['PTS'].tail(WINDOW_LONG).mean()
        recent_form_adj = recent_avg / long_avg if long_avg > 0 else 1.0

        minutes_proj = df_player['MIN'].tail(1).values[0] if not df_player.empty else 30
        stat_per_min = df_player['PTS'].tail(WINDOW_RECENT).mean() / minutes_proj if minutes_proj > 0 else 0.7

        usage_adj = 1.0  # placeholder

        # Opponent defensive adjustment
        df_opp = get_team_games(opp_team_id)
        opp_pts_allowed_per_game = df_opp['PTS'].mean()
        league_pts_allowed = 110  # can replace with actual league avg
        opp_def_adj = opp_pts_allowed_per_game / league_pts_allowed

        # Pace adjustment
        league_pace = 100  # placeholder
        opp_pace = 101  # placeholder, can improve with real pace
        pace_adj = opp_pace / league_pace

        home_adj = 1.03 if home else 0.97

        return {
            'player_name': player_name,
            'opponent_name': opponent_name,
            'minutes_proj': minutes_proj,
            'stat_per_min': stat_per_min,
            'recent_form_adj': recent_form_adj,
            'usage_adj': usage_adj,
            'opp_def_adj': opp_def_adj,
            'pace_adj': pace_adj,
            'home_adj': home_adj
        }
    except Exception as e:
        print(f"Error for {player_name}: {e}")
        return None

# --- Main daily workflow ---
def get_todays_games():
    # Pull all NBA games scheduled today
    today = datetime.today().strftime('%m/%d/%Y')
    df_games = leaguegamefinder.LeagueGameFinder(date_from_nullable=today, date_to_nullable=today).get_data_frames()[0]
    return df_games

def main():
    df_games_today = get_todays_games()
    results = []

    print(f"Found {len(df_games_today)} games today.")

    # Loop over games
    for idx, row in tqdm(df_games_today.iterrows(), total=len(df_games_today)):
        player_name = row['PLAYER_NAME']
        team_name = row['TEAM_NAME']
        opp_name = row['OPPONENT_TEAM_NAME']
        home = True if row['MATCHUP'].endswith('vs.') else False

        adj = calculate_adjustments(player_name, opp_name, home)
        if adj:
            results.append(adj)

    df_output = pd.DataFrame(results)
    df_output.to_csv('daily_player_adjustments.csv', index=False)
    print("✅ Daily adjustments CSV saved: daily_player_adjustments.csv")

if __name__ == "__main__":
    main()
