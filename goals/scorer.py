import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import os
import time
from datetime import datetime

def fetch_match_data(url, team_type='home'):
    """
    Scrape team goals from a FotMob match URL
    Args:
        url: FotMob match URL
        team_type: 'home' or 'away'
    Returns a list of goal scorer names
    """
    try:
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')

        # Load JSON data from NEXT_DATA script
        script_tag = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        if not script_tag or not script_tag.contents:
            print(f"Could not find NEXT_DATA script tag for {team_type} team")
            return []

        json_fotmob = json.loads(script_tag.contents[0])

        # Navigate to team goals based on team_type
        try:
            if team_type == 'home':
                goals_data = json_fotmob['props']['pageProps']['header']['events']['homeTeamGoals']
            else:  # away
                goals_data = json_fotmob['props']['pageProps']['header']['events']['awayTeamGoals']

            goal_scorers = list(goals_data.keys())
            print(f"{team_type.capitalize()} team goals found: {goal_scorers}")
            return goal_scorers

        except KeyError as e:
            print(f"Could not find {team_type} team goals data. Key error: {e}")
            print(f"This might be a 0-0 game or the data structure is different for {team_type} team")
            return []

    except requests.RequestException as e:
        print(f"Error fetching URL for {team_type} team: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {team_type} team: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error for {team_type} team: {e}")
        return []

def save_goals_to_csv(goal_scorers, match_url, csv_filename, team_type):
    """
    Save goal scorers to CSV file with match information
    """
    if not goal_scorers:
        print(f"No goals to save for {team_type} team in this match")
        goal_scorers = ['No goals']

    # Create DataFrame with current match data
    current_match_data = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for scorer in goal_scorers:
        current_match_data.append({
            'timestamp': timestamp,
            'match_url': match_url,
            'goal_scorer': scorer,
        })

    df_current = pd.DataFrame(current_match_data)

    # Save to CSV
    df_current.to_csv(csv_filename, index=False)
    print(f"{team_type.capitalize()} team goals saved to {csv_filename}")
    print(f"Total matches recorded for {team_type}: {len(df_current['match_url'].unique())}")

    return df_current

def scrape_goal_scorer_data(url, goal_scorer, team_type='home'):
    """
    Scrape data for a specific goal scorer from the given URL
    Args:
        url: FotMob match URL
        goal_scorer: Name of the goal scorer
        team_type: 'home' or 'away'
    Returns tuple: (scorer_data, match_round, team_id)
    """
    try:
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')
        json_data = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])

        # Get match round and team ID based on team_type
        match_round = json_data['props']['pageProps']['general']['matchRound']

        if team_type == 'home':
            team_id = json_data['props']['pageProps']['general']['homeTeam']['id']
            team_goals = json_data['props']['pageProps']['header']['events']['homeTeamGoals']
        else:  # away
            team_id = json_data['props']['pageProps']['general']['awayTeam']['id']
            team_goals = json_data['props']['pageProps']['header']['events']['awayTeamGoals']

        # Check if the goal scorer exists in the data
        if goal_scorer in team_goals:
            return team_goals[goal_scorer], match_round, team_id
        else:
            print(f"Goal scorer '{goal_scorer}' not found in {team_type} team data")
            return None, match_round, team_id

    except Exception as e:
        print(f"Error scraping data for {goal_scorer} ({team_type} team): {str(e)}")
        return None, None, None

def process_goal_scorers_csv(csv_file_path, url, output_csv_path, team_type='home', goal_scorer_column='goal_scorer'):
    """
    Process CSV file with goal scorers and create a new CSV with scraped data
    """
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Error reading CSV file for {team_type} team: {str(e)}")
        return

    # Check if the goal scorer column exists
    if goal_scorer_column not in df.columns:
        print(f"Column '{goal_scorer_column}' not found in {team_type} team CSV file")
        print(f"Available columns: {list(df.columns)}")
        return

    # Get unique goal scorers (remove duplicates and NaN values)
    goal_scorers = df[goal_scorer_column].dropna().unique()
    print(f"Found {len(goal_scorers)} unique {team_type} team goal scorers: {list(goal_scorers)}")

    # List to store all dataframes
    all_dataframes = []

    # Variables to store match info (will be the same for all scorers from the same match)
    match_round = None
    team_id = None

    # Process each goal scorer
    for scorer in goal_scorers:
        print(f"Processing {team_type} team scorer: {scorer}")

        # Scrape data for this goal scorer
        scorer_data, current_match_round, current_team_id = scrape_goal_scorer_data(url, scorer, team_type)

        # Store match info from the first successful scrape
        if match_round is None and current_match_round is not None:
            match_round = current_match_round
            team_id = current_team_id

        if scorer_data is not None:
            # Convert the data to a DataFrame
            if isinstance(scorer_data, dict):
                scorer_df = pd.DataFrame([scorer_data])
            elif isinstance(scorer_data, list):
                scorer_df = pd.DataFrame(scorer_data)
            else:
                scorer_df = pd.DataFrame({'value': [scorer_data]})

            # Add columns to identify which goal scorer this data belongs to and match info
            scorer_df['goal_scorer'] = scorer
            scorer_df['matchRound'] = match_round

            # Use appropriate team ID column name
            if team_type == 'home':
                scorer_df['HomeTeamId'] = team_id
            else:
                scorer_df['AwayTeamId'] = team_id

            # Add to our list of dataframes
            all_dataframes.append(scorer_df)

            # Add a small delay to be respectful to the server
            time.sleep(0.5)
        else:
            # Even if no scorer data, we can still add a row with match info
            if match_round is not None and team_id is not None:
                scorer_data = {
                    'goal_scorer': scorer,
                    'matchRound': match_round,
                }

                if team_type == 'home':
                    scorer_data['HomeTeamId'] = team_id
                else:
                    scorer_data['AwayTeamId'] = team_id

                scorer_df = pd.DataFrame([scorer_data])
                all_dataframes.append(scorer_df)
            print(f"No data found for {team_type} team scorer: {scorer}")

    # Combine all dataframes
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)

        # Append to existing CSV file or create new one if it doesn't exist
        try:
            if os.path.exists(output_csv_path):
                final_df.to_csv(output_csv_path, mode='a', header=False, index=False)
                print(f"{team_type.capitalize()} team data appended successfully to {output_csv_path}")
            else:
                final_df.to_csv(output_csv_path, index=False)
                print(f"New file created and {team_type} team data saved to {output_csv_path}")

            print(f"Final {team_type} team dataset shape: {final_df.shape}")
            print(f"Match Round: {match_round}")
            print(f"{team_type.capitalize()} Team ID: {team_id}")

        except Exception as e:
            print(f"Error saving {team_type} team CSV file: {str(e)}")
    else:
        print(f"No data was successfully scraped for any {team_type} team goal scorer")

def process_team_data(url, team_type):
    """
    Process data for a specific team (home or away)
    """
    print(f"\n=== PROCESSING {team_type.upper()} TEAM ===")
    print("-" * 50)

    # Define file paths based on team type
    if team_type == 'home':
        list_players_csv = '/home/axel/Code/Python/championship/goals/csv/listHomePlayers.csv'
        scorers_csv = '/home/axel/Code/Python/championship/goals/csv/homeScorers.csv'
    else:  # away
        list_players_csv = '/home/axel/Code/Python/championship/goals/csv/listAwayPlayers.csv'
        scorers_csv = '/home/axel/Code/Python/championship/goals/csv/awayScorers.csv'

    print(f"Step 1: Scraping {team_type} team goal scorers")
    print("-" * 30)

    # Step 1: Scrape goals from the match and save to appropriate CSV
    goal_scorers = fetch_match_data(url, team_type)

    if not goal_scorers or goal_scorers == ['No goals']:
        print(f"No {team_type} team goal scorers found, but continuing with processing...")

    df_goals = save_goals_to_csv(goal_scorers, url, list_players_csv, team_type)

    print(f"\nStep 2: Processing {team_type} team goal scorer details")
    print("-" * 30)

    # Step 2: Process the CSV file and get detailed data
    process_goal_scorers_csv(
        csv_file_path=list_players_csv,
        url=url,
        output_csv_path=scorers_csv,
        team_type=team_type,
        goal_scorer_column='goal_scorer'
    )

    print(f"\n{team_type.capitalize()} team processing completed!")
    print(f"Goal scorers list saved to: {list_players_csv}")
    print(f"Detailed scorer data saved to: {scorers_csv}")

def main():
    """
    Main function to run both home and away team scrapers in sequence
    """
    print("Combined FotMob Scraper - Home & Away Teams")
    print("=" * 60)

    # Get URL input from user
    url_input = input('\nEnter FotMob match URL: ').strip()

    if not url_input:
        print("Please enter a valid URL")
        return

    print(f"\nScraping match data from: {url_input}")
    print("=" * 60)

    # Process both home and away teams
    process_team_data(url_input, 'home')
    process_team_data(url_input, 'away')

    print(f"\n" + "=" * 60)
    print("SCRAPING COMPLETED FOR BOTH TEAMS!")
    print("=" * 60)
    print("Files created/updated:")
    print("- Home team goal scorers: /home/axel/Code/Python/championship/goals/csv/listHomePlayers.csv")
    print("- Home team detailed data: /home/axel/Code/Python/championship/goals/csv/homeScorers.csv")
    print("- Away team goal scorers: /home/axel/Code/Python/championship/goals/csv/listAwayPlayers.csv")
    print("- Away team detailed data: /home/axel/Code/Python/championship/goals/csv/awayScorers.csv")

if __name__ == "__main__":
    main()
