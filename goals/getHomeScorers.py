import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import os
import time
from datetime import datetime

def fetch_match_data(url):
    """
    Scrape home team goals from a FotMob match URL
    Returns a list of goal scorer names
    """
    try:
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')

        # Load JSON data from NEXT_DATA script
        script_tag = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        if not script_tag or not script_tag.contents:
            print("Could not find NEXT_DATA script tag")
            return []

        json_fotmob = json.loads(script_tag.contents[0])

        # Navigate to home team goals
        try:
            home_goals_data = json_fotmob['props']['pageProps']['header']['events']['homeTeamGoals']
            goal_scorers = list(home_goals_data.keys())
            print(f"Home team goals found: {goal_scorers}")
            return goal_scorers

        except KeyError as e:
            print(f"Could not find home team goals data. Key error: {e}")
            print("This might be a 0-0 game or the data structure is different")
            return []

    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def save_goals_to_csv(goal_scorers, match_url, csv_filename):
    """
    Save goal scorers to CSV file with match information
    """
    if not goal_scorers:
        print("No goals to save for this match")
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
    df_combined = df_current

    # Save to CSV
    df_combined.to_csv(csv_filename, index=False)
    print(f"Goals saved to {csv_filename}")
    print(f"Total matches recorded: {len(df_combined['match_url'].unique())}")

    return df_combined

def scrape_goal_scorer_data(url, goal_scorer):
    """
    Scrape data for a specific goal scorer from the given URL
    Returns tuple: (scorer_data, match_round, home_team_id)
    """
    try:
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')
        json_data = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])

        # Get match round and home team ID
        match_round = json_data['props']['pageProps']['general']['matchRound']
        home_team_id = json_data['props']['pageProps']['general']['homeTeam']['id']

        # Navigate to the specific path and get data for the goal scorer
        home_team_goals = json_data['props']['pageProps']['header']['events']['homeTeamGoals']

        # Check if the goal scorer exists in the data
        if goal_scorer in home_team_goals:
            return home_team_goals[goal_scorer], match_round, home_team_id
        else:
            print(f"Goal scorer '{goal_scorer}' not found in data")
            return None, match_round, home_team_id

    except Exception as e:
        print(f"Error scraping data for {goal_scorer}: {str(e)}")
        return None, None, None

def process_goal_scorers_csv(csv_file_path, url, output_csv_path, goal_scorer_column='goal_scorer'):
    """
    Process CSV file with goal scorers and create a new CSV with scraped data
    """
    # Read the CSV file
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return

    # Check if the goal scorer column exists
    if goal_scorer_column not in df.columns:
        print(f"Column '{goal_scorer_column}' not found in CSV file")
        print(f"Available columns: {list(df.columns)}")
        return

    # Get unique goal scorers (remove duplicates and NaN values)
    goal_scorers = df[goal_scorer_column].dropna().unique()
    print(f"Found {len(goal_scorers)} unique goal scorers: {list(goal_scorers)}")

    # List to store all dataframes
    all_dataframes = []

    # Variables to store match info (will be the same for all scorers from the same match)
    match_round = None
    home_team_id = None

    # Process each goal scorer
    for scorer in goal_scorers:
        print(f"Processing: {scorer}")

        # Scrape data for this goal scorer
        scorer_data, current_match_round, current_home_team_id = scrape_goal_scorer_data(url, scorer)

        # Store match info from the first successful scrape
        if match_round is None and current_match_round is not None:
            match_round = current_match_round
            home_team_id = current_home_team_id

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
            scorer_df['HomeTeamId'] = home_team_id

            # Add to our list of dataframes
            all_dataframes.append(scorer_df)

            # Add a small delay to be respectful to the server
            time.sleep(0.5)
        else:
            # Even if no scorer data, we can still add a row with match info
            if match_round is not None and home_team_id is not None:
                scorer_df = pd.DataFrame({
                    'goal_scorer': [scorer],
                    'matchRound': [match_round],
                    'HomeTeamId': [home_team_id]
                })
                all_dataframes.append(scorer_df)
            print(f"No data found for {scorer}")

    # Combine all dataframes
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)

        # Append to existing CSV file or create new one if it doesn't exist
        try:
            if os.path.exists(output_csv_path):
                final_df.to_csv(output_csv_path, mode='a', header=False, index=False)
                print(f"Data appended successfully to {output_csv_path}")
            else:
                final_df.to_csv(output_csv_path, index=False)
                print(f"New file created and data saved to {output_csv_path}")

            print(f"Final dataset shape: {final_df.shape}")
            print(f"Match Round: {match_round}")
            print(f"Home Team ID: {home_team_id}")

        except Exception as e:
            print(f"Error saving CSV file: {str(e)}")
    else:
        print("No data was successfully scraped for any goal scorer")

def main():
    """
    Main function to run both scrapers in sequence
    """
    print("Combined FotMob Scraper")
    print("=" * 50)

    # File paths
    listhomeplayers_csv = '/home/axel/Code/Python/championship/csv/listHomePlayers.csv'
    homescorers_csv = '/home/axel/Code/Python/championship/csv/homeScorers.csv'

    # Get URL input from user
    url_input = input('\nEnter FotMob match URL: ').strip()

    if not url_input:
        print("Please enter a valid URL")
        return

    print(f"\n=== STEP 1: Scraping goal scorers ===")
    print(f"Scraping match: {url_input}")
    print("-" * 50)

    # Step 1: Scrape goals from the match and save to listHomePlayers.csv
    goal_scorers = fetch_match_data(url_input)

    if not goal_scorers:
        print("No goal scorers found. Exiting...")
        return

    df_goals = save_goals_to_csv(goal_scorers, url_input, listhomeplayers_csv)

    print(f"\n=== STEP 2: Processing goal scorer details ===")
    print("-" * 50)

    # Step 2: Process the CSV file and get detailed data
    process_goal_scorers_csv(
        csv_file_path=listhomeplayers_csv,
        url=url_input,
        output_csv_path=homescorers_csv,
        goal_scorer_column='goal_scorer'
    )

    print(f"\n=== COMPLETED ===")
    print(f"Goal scorers list saved to: {listhomeplayers_csv}")
    print(f"Detailed scorer data saved to: {homescorers_csv}")

if __name__ == "__main__":
    main()
