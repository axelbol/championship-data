import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import os

def extract_stat_value_by_category(stats_list, category_index, stat_key, sub_key='value'):
    """
    Extract a specific stat value from a specific category in the nested stats structure

    Parameters:
    - stats_list: The nested list/dict structure from the 'stats' column
    - category_index: The index of the category (0=Top stats, 1=Attack, 2=Defense, 3=Duels)
    - stat_key: The name of the stat to extract (e.g., 'Touches')
    - sub_key: Either 'value' or 'total' for stats like 'Accurate crosses'

    Returns:
    - The extracted value or None if not found
    """
    if not stats_list or not isinstance(stats_list, list):
        return None

    if category_index >= len(stats_list):
        return None

    category = stats_list[category_index]
    if isinstance(category, dict) and 'stats' in category:
        if stat_key in category['stats']:
            stat_info = category['stats'][stat_key].get('stat', {})
            return stat_info.get(sub_key, None)
    return None

def extract_match_name_from_url(url):
    """
    Extract match name from FotMob URL for CSV filename
    Example: https://www.fotmob.com/es/matches/liverpool-vs-arsenal/2tmaz7#4813399 -> liverpool-vs-arsenal
    """
    pattern = r'/matches/([^/]+)/'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        # Fallback: try to extract from URL path
        parts = url.split('/')
        for part in parts:
            if 'vs' in part or '-' in part:
                return part.split('#')[0]  # Remove any fragment
    return "match_data"  # Default fallback

def get_unique_filename(directory, base_filename):
    """
    Generate a unique filename by adding a number suffix if the file already exists

    Parameters:
    - directory: The directory where the file will be saved
    - base_filename: The original filename (e.g., 'liverpool-vs-arsenal.csv')

    Returns:
    - A unique filename that doesn't exist in the directory
    """
    # Split filename and extension
    name, ext = os.path.splitext(base_filename)

    # Check if original filename exists
    full_path = os.path.join(directory, base_filename)
    if not os.path.exists(full_path):
        return base_filename

    # If it exists, find the next available number
    counter = 1
    while True:
        new_filename = f"{name}-{counter}{ext}"
        new_full_path = os.path.join(directory, new_filename)
        if not os.path.exists(new_full_path):
            return new_filename
        counter += 1

def main():
    # Get URL input
    url_input = input('Enter URL: ')
    url = url_input

    # Make request and parse
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')

    # Load what we need in json_fotmob variable
    json_fotmob = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])

    # Extract match information
    matchId = json_fotmob['props']['pageProps']['general']['matchId']
    matchRound = json_fotmob['props']['pageProps']['general']['matchRound']
    homeTeamName = json_fotmob['props']['pageProps']['general']['homeTeam']['name']
    homeTeamid = json_fotmob['props']['pageProps']['general']['homeTeam']['id']
    awayTeamName = json_fotmob['props']['pageProps']['general']['awayTeam']['name']
    awayTeamid = json_fotmob['props']['pageProps']['general']['awayTeam']['id']
    matchDate = json_fotmob['props']['pageProps']['general']['matchTimeUTCDate']
    home_goals = json_fotmob['props']['pageProps']['header']['teams'][0]['score']
    away_goals = json_fotmob['props']['pageProps']['header']['teams'][1]['score']

    # Create DataFrame
    df_players = pd.DataFrame(json_fotmob['props']['pageProps']['content']['playerStats'])
    df_players_T = df_players.T
    df_players_T.reset_index(drop=True, inplace=True)
    df_players_T = df_players_T.drop(['shotmap', 'funFacts', 'isPotm'], axis=1)

    # Add match information columns to the dataframe
    df_players_T['matchId'] = matchId
    df_players_T['matchRound'] = matchRound
    df_players_T['homeTeamName'] = homeTeamName
    df_players_T['homeTeamid'] = homeTeamid
    df_players_T['awayTeamName'] = awayTeamName
    df_players_T['awayTeamid'] = awayTeamid
    df_players_T['matchDate'] = matchDate
    df_players_T['home_goals'] = home_goals
    df_players_T['away_goals'] = away_goals

    # Your existing stats (category 0 - Top stats)
    existing_stats_to_extract = [
        ('FotMob rating', 'FotMob_rating', 'value'),
        ('Minutes played', 'Minutes_played', 'value'),
        ('Goals', 'Goals', 'value'),
        ('Assists', 'Assists', 'value'),
        ('Total shots', 'Total_shots', 'value'),
        ('Accurate passes', 'Accurate_passes_value', 'value'),
        ('Accurate passes', 'Accurate_passes_total', 'total'),
        ('Chances created', 'Chances_created', 'value'),
        ('Expected assists (xA)', 'Expected_assists_xA', 'value'),
        ('xG + xA', 'xG_plus_xA', 'value'),
        ('Fantasy points', 'Fantasy_points', 'value'),
        ('Defensive actions', 'Defensive_actions', 'value')
    ]

    # New stats to extract with their category indices
    new_stats_to_extract = [
        # Attack stats (category 1)
        (1, 'Touches', 'touches', 'value'),
        (1, 'Touches in opposition box', 'touches_opp_box', 'value'),
        (1, 'Passes into final third', 'passes_into_final_third', 'value'),
        (1, 'Accurate crosses', 'accurate_crosses_value', 'value'),
        (1, 'Accurate crosses', 'accurate_crosses_total', 'total'),
        (1, 'Accurate long balls', 'long_balls_accurate_value', 'value'),
        (1, 'Accurate long balls', 'long_balls_accurate_total', 'total'),
        (1, 'Dispossessed', 'dispossessed', 'value'),

        # Defense stats (category 2)
        (2, 'Tackles won', 'tackles_succeeded_value', 'value'),
        (2, 'Tackles won', 'tackles_succeeded_total', 'total'),
        (2, 'Blocks', 'shot_blocks', 'value'),
        (2, 'Clearances', 'clearances', 'value'),
        (2, 'Headed clearance', 'headed_clearance', 'value'),
        (2, 'Interceptions', 'interceptions', 'value'),
        (2, 'Recoveries', 'recoveries', 'value'),
        (2, 'Dribbled past', 'dribbled_past', 'value'),

        # Duels stats (category 3)
        (3, 'Duels won', 'duel_won', 'value'),
        (3, 'Duels lost', 'duel_lost', 'value'),
        (3, 'Ground duels won', 'ground_duels_won_value', 'value'),
        (3, 'Ground duels won', 'ground_duels_won_total', 'total'),
        (3, 'Aerial duels won', 'aerials_won_value', 'value'),
        (3, 'Aerial duels won', 'aerials_won_total', 'total'),
        (3, 'Was fouled', 'fouls_received', 'value'),
        (3, 'Fouls committed', 'fouls_committed', 'value')
    ]

    # Extract existing stats using the original function (for backward compatibility)
    for stat_key, column_name, sub_key in existing_stats_to_extract:
        df_players_T[column_name] = df_players_T['stats'].apply(
            lambda x: extract_stat_value_by_category(x, 0, stat_key, sub_key)
        )

    # Extract new stats using the category-specific function
    for category_index, stat_key, column_name, sub_key in new_stats_to_extract:
        df_players_T[column_name] = df_players_T['stats'].apply(
            lambda x: extract_stat_value_by_category(x, category_index, stat_key, sub_key)
        )

    # Display all new columns created
    all_new_columns = [col[1] for col in existing_stats_to_extract] + [col[2] for col in new_stats_to_extract]
    print("All columns created:")
    print(all_new_columns)

    # Display sample of the extracted data
    print(f"\nSample of extracted data (showing first 5 rows):")
    print(df_players_T[all_new_columns].head())

    # Check for missing data
    print(f"\nMissing data summary:")
    for col in all_new_columns:
        null_count = df_players_T[col].isnull().sum()
        total_count = len(df_players_T)
        percentage = (null_count / total_count) * 100
        print(f"{col}: {null_count}/{total_count} missing values ({percentage:.1f}%)")

    # Extract match name from URL and create CSV filename
    match_name = extract_match_name_from_url(url)
    base_csv_filename = f"{match_name}.csv"
    csv_directory = "/home/axel/Code/Python/championship/playerStats/csv/"

    # Create directory if it doesn't exist
    os.makedirs(csv_directory, exist_ok=True)

    # Get unique filename to prevent overwriting
    unique_csv_filename = get_unique_filename(csv_directory, base_csv_filename)
    csv_path = os.path.join(csv_directory, unique_csv_filename)

    # Save DataFrame to CSV
    df_players_T.to_csv(csv_path, index=False)
    print(f"\nDataFrame saved to: {csv_path}")
    print(f"Shape of saved DataFrame: {df_players_T.shape}")

    # Show if filename was modified
    if unique_csv_filename != base_csv_filename:
        print(f"Note: Original filename '{base_csv_filename}' already existed.")
        print(f"File saved with unique name: '{unique_csv_filename}'")

if __name__ == "__main__":
    main()
