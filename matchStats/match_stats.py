import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import os

def scrape_and_save_match_data():
    # Get URL input
    url_input = input('Enter URL: ')
    url = url_input
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')

    # Load what we need in json_fotmob variable
    json_fotmob = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])

    # Extract all the data
    matchId = json_fotmob['props']['pageProps']['general']['matchId']
    matchRound = json_fotmob['props']['pageProps']['general']['matchRound']
    homeTeamName = json_fotmob['props']['pageProps']['general']['homeTeam']['name']
    homeTeamid = json_fotmob['props']['pageProps']['general']['homeTeam']['id']
    awayTeamName = json_fotmob['props']['pageProps']['general']['awayTeam']['name']
    awayTeamid = json_fotmob['props']['pageProps']['general']['awayTeam']['id']
    home_goals = json_fotmob['props']['pageProps']['header']['teams'][0]['score']
    away_goals = json_fotmob['props']['pageProps']['header']['teams'][1]['score']
    ball_possession_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][0]['stats'][0]
    ball_possession_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][0]['stats'][1]
    big_chances_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][4]['stats'][0]
    big_chances_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][4]['stats'][1]
    big_chances_missed_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][5]['stats'][0]
    big_chances_missed_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][5]['stats'][1]
    fouls_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][7]['stats'][0]
    fouls_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][7]['stats'][1]
    corners_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][8]['stats'][0]
    corners_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][0]['stats'][8]['stats'][1]
    total_shots_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][1]['stats'][0]
    total_shots_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][1]['stats'][1]
    shots_off_target_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][2]['stats'][0]
    shots_off_target_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][2]['stats'][1]
    shots_on_target_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][3]['stats'][0]
    shots_on_target_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][3]['stats'][1]
    blocked_shots_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][4]['stats'][0]
    blocked_shots_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][4]['stats'][1]
    hit_woodwork_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][5]['stats'][0]
    hit_woodwork_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][5]['stats'][1]
    shots_inside_box_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][6]['stats'][0]
    shots_inside_box_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][6]['stats'][1]
    shots_outside_box_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][7]['stats'][0]
    shots_outside_box_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][1]['stats'][7]['stats'][1]
    xG_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][1]['stats'][0]
    xG_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][1]['stats'][1]
    xG_open_play_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][2]['stats'][0]
    xG_open_play_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][2]['stats'][1]
    xG_set_play_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][3]['stats'][0]
    xG_set_play_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][3]['stats'][1]
    xG_non_penalty_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][4]['stats'][0]
    xG_non_penalty_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][4]['stats'][1]
    xGOT_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][5]['stats'][0]
    xGOT_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][2]['stats'][5]['stats'][1]
    passes_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][1]['stats'][0]
    passes_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][1]['stats'][1]
    accurate_passes_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][2]['stats'][0]
    accurate_passes_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][2]['stats'][1]
    own_half_passes_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][3]['stats'][0]
    own_half_passes_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][3]['stats'][1]
    opposition_half_passes_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][4]['stats'][0]
    opposition_half_passes_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][4]['stats'][1]
    accurate_long_passes_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][5]['stats'][0]
    accurate_long_passes_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][5]['stats'][1]
    accurate_crosses_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][6]['stats'][0]
    accurate_crosses_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][6]['stats'][1]
    throws_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][7]['stats'][0]
    throws_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][7]['stats'][1]
    touches_opp_box_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][8]['stats'][0]
    touches_opp_box_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][8]['stats'][1]
    offsides_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][9]['stats'][0]
    offsides_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][3]['stats'][9]['stats'][1]
    tackles_won_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][1]['stats'][0]
    tackles_won_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][1]['stats'][1]
    interceptions_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][2]['stats'][0]
    interceptions_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][2]['stats'][1]
    blocks_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][3]['stats'][0]
    blocks_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][3]['stats'][1]
    clearances_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][4]['stats'][0]
    clearances_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][4]['stats'][1]
    keeper_saves_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][5]['stats'][0]
    keeper_saves_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][4]['stats'][5]['stats'][1]
    duel_won_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][1]['stats'][0]
    duel_won_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][1]['stats'][1]
    ground_duels_won_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][2]['stats'][0]
    ground_duels_won_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][2]['stats'][1]
    aerial_won_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][3]['stats'][0]
    aerial_won_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][3]['stats'][1]
    dribbles_succeeded_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][4]['stats'][0]
    dribbles_succeeded_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][5]['stats'][4]['stats'][1]
    yellow_cards_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][6]['stats'][1]['stats'][0]
    yellow_cards_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][6]['stats'][1]['stats'][1]
    red_cards_home = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][6]['stats'][2]['stats'][0]
    red_cards_away = json_fotmob['props']['pageProps']['content']['stats']['Periods']['All']['stats'][6]['stats'][2]['stats'][1]

    # Create a dictionary with all the data
    match_data = {
        'matchId': matchId,
        'matchRound': matchRound,
        'homeTeamName': homeTeamName,
        'homeTeamid': homeTeamid,
        'awayTeamName': awayTeamName,
        'awayTeamid': awayTeamid,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'ball_possession_home': ball_possession_home,
        'ball_possession_away': ball_possession_away,
        'xG_home': xG_home,
        'xG_away': xG_away,
        'total_shots_home': total_shots_home,
        'total_shots_away': total_shots_away,
        'shots_on_target_home': shots_on_target_home,
        'shots_on_target_away': shots_on_target_away,
        'big_chances_home': big_chances_home,
        'big_chances_away': big_chances_away,
        'big_chances_missed_home': big_chances_missed_home,
        'big_chances_missed_away': big_chances_missed_away,
        'accurate_passes_home': accurate_passes_home,
        'accurate_passes_away': accurate_passes_away,
        'fouls_home': fouls_home,
        'fouls_away': fouls_away,
        'corners_home': corners_home,
        'corners_away': corners_away,
        'shots_off_target_home': shots_off_target_home,
        'shots_off_target_away': shots_off_target_away,
        'blocked_shots_home': blocked_shots_home,
        'blocked_shots_away': blocked_shots_away,
        'hit_woodwork_home': hit_woodwork_home,
        'hit_woodwork_away': hit_woodwork_away,
        'shots_inside_box_home': shots_inside_box_home,
        'shots_inside_box_away': shots_inside_box_away,
        'shots_outside_box_home': shots_outside_box_home,
        'shots_outside_box_away': shots_outside_box_away,
        'xG_open_play_home': xG_open_play_home,
        'xG_open_play_away': xG_open_play_away,
        'xG_set_play_home': xG_set_play_home,
        'xG_set_play_away': xG_set_play_away,
        'xG_non_penalty_home': xG_non_penalty_home,
        'xG_non_penalty_away': xG_non_penalty_away,
        'xGOT_home': xGOT_home,
        'xGOT_away': xGOT_away,
        'passes_home': passes_home,
        'passes_away': passes_away,
        'own_half_passes_home': own_half_passes_home,
        'own_half_passes_away': own_half_passes_away,
        'opposition_half_passes_home': opposition_half_passes_home,
        'opposition_half_passes_away': opposition_half_passes_away,
        'accurate_long_passes_home': accurate_long_passes_home,
        'accurate_long_passes_away': accurate_long_passes_away,
        'accurate_crosses_home': accurate_crosses_home,
        'accurate_crosses_away': accurate_crosses_away,
        'throws_home': throws_home,
        'throws_away': throws_away,
        'touches_opp_box_home': touches_opp_box_home,
        'touches_opp_box_away': touches_opp_box_away,
        'offsides_home': offsides_home,
        'offsides_away': offsides_away,
        'tackles_won_home': tackles_won_home,
        'tackles_won_away': tackles_won_away,
        'interceptions_home': interceptions_home,
        'interceptions_away': interceptions_away,
        'blocks_home': blocks_home,
        'blocks_away': blocks_away,
        'clearances_home': clearances_home,
        'clearances_away': clearances_away,
        'keeper_saves_home': keeper_saves_home,
        'keeper_saves_away': keeper_saves_away,
        'duel_won_home': duel_won_home,
        'duel_won_away': duel_won_away,
        'ground_duels_won_home': ground_duels_won_home,
        'ground_duels_won_away': ground_duels_won_away,
        'aerial_won_home': aerial_won_home,
        'aerial_won_away': aerial_won_away,
        'dribbles_succeeded_home': dribbles_succeeded_home,
        'dribbles_succeeded_away': dribbles_succeeded_away,
        'yellow_cards_home': yellow_cards_home,
        'yellow_cards_away': yellow_cards_away,
        'red_cards_home': red_cards_home,
        'red_cards_away': red_cards_away
    }

    # Create DataFrame from the dictionary
    df = pd.DataFrame([match_data])

    # Define the CSV filename
    csv_filename = '/home/axel/Code/Python/championship/matchStats/csv/fotmob_match_stats.csv'

    # Check if CSV file already exists
    if os.path.exists(csv_filename):
        # If file exists, append without header
        df.to_csv(csv_filename, mode='a', header=False, index=False)
        print(f"Data appended to existing file: {csv_filename}")
    else:
        # If file doesn't exist, create new file with header
        df.to_csv(csv_filename, mode='w', header=True, index=False)
        print(f"New file created: {csv_filename}")

    print(f"Match data for {homeTeamName} vs {awayTeamName} saved successfully!")

    return df

# Run the function
if __name__ == "__main__":
    try:
        result_df = scrape_and_save_match_data()
        print("\nDataFrame created:")
        print(result_df.head())
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check the URL and try again.")
