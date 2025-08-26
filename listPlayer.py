import requests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import os
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

            # Extract goal scorer names (keys)
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
        # Still save an entry to track 0-0 games
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

    # Code to append to existing CSV
    # Check if CSV file exists
    '''
    if os.path.exists(csv_filename):
        # Load existing data and append new data
        df_existing = pd.read_csv(csv_filename)
        df_combined = pd.concat([df_existing, df_current], ignore_index=True)
    else:
        # Create new DataFrame
        df_combined = df_current
    '''
    # Code to rewrite CSV file
    df_combined = df_current

    # Save to CSV
    df_combined.to_csv(csv_filename, index=False)
    print(f"Goals saved to {csv_filename}")
    print(f"Total matches recorded: {len(df_combined['match_url'].unique())}")

    return df_combined

def main():
    """
    Main function to run the scraper
    """
    print("FotMob Home Team Goals Scraper")
    print("=" * 40)

    csv_filename = '/home/axel/Code/Python/championship/csv/listPlayers.csv'


    # new code
    url_input = input('\nEnter FotMob match URL (or "quit" to exit): ').strip()
    print(f"\nScraping match: {url_input}")
    print("-" * 50)
     # Scrape goals from the match
    goal_scorers = fetch_match_data(url_input)
    # Save to CSV
    df = save_goals_to_csv(goal_scorers, url_input, csv_filename)
    # end new code

    '''
    while True:
        # Get URL input from user
        url_input = input('\nEnter FotMob match URL (or "quit" to exit): ').strip()

        if url_input.lower() in ['quit', 'q', 'exit']:
            print("Exiting scraper...")
            break

        if not url_input:
            print("Please enter a valid URL")
            continue

        print(f"\nScraping match: {url_input}")
        print("-" * 50)

        # Scrape goals from the match
        goal_scorers = fetch_match_data(url_input)

        # Save to CSV
        df = save_goals_to_csv(goal_scorers, url_input, csv_filename)

        # Display current season summary
        # print(f"\nSeason Summary:")
        # print(f"Total goals: {len(df[df['goal_scorer'] != 'No goals'])}")
        # print(f"Total matches: {len(df['match_url'].unique())}")

        # Show top scorers
        if len(df[df['goal_scorer'] != 'No goals']) > 0:
            top_scorers = df[df['goal_scorer'] != 'No goals']['goal_scorer'].value_counts().head(5)
            print(f"\nTop scorers:")
            for scorer, goals in top_scorers.items():
                print(f"  {scorer}: {goals} goals")

        continue_scraping = input("\nScrape another match? (y/n): ").lower()
        if continue_scraping not in ['y', 'yes']:
            break

    print(f"\nFinal data saved in: {csv_filename}")
    '''

if __name__ == "__main__":
    main()
