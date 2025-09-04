#!/usr/bin/env python3
"""
FotMob Match Data Scraper
Scrapes match data from FotMob URLs and saves shot data to CSV files
"""

import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
import os
import re
from pathlib import Path


def extract_match_name_from_url(url):
    """
    Extract the match name from FotMob URL
    Example: https://www.fotmob.com/es/matches/liverpool-vs-arsenal/2tmaz7#4813399
    Returns: liverpool-vs-arsenal
    """
    # Parse the URL to get the match name part
    match = re.search(r'/matches/([^/]+)/', url)
    if match:
        return match.group(1)
    else:
        # Fallback to a generic name if pattern doesn't match
        return "match-data"


def get_unique_filename(base_path, match_name):
    """
    Generate a unique filename by adding a number suffix if file already exists
    """
    csv_dir = Path(base_path)
    csv_dir.mkdir(parents=True, exist_ok=True)

    # Start with the base filename
    filename = f"{match_name}.csv"
    filepath = csv_dir / filename

    # If file exists, add incrementing number
    counter = 1
    while filepath.exists():
        filename = f"{match_name}-{counter}.csv"
        filepath = csv_dir / filename
        counter += 1

    return filepath


def scrape_fotmob_match(url):
    """
    Main function to scrape FotMob match data
    """
    try:
        # Make request to the URL
        print(f"Fetching data from: {url}")
        r = requests.get(url)
        r.raise_for_status()  # Raise an exception for bad status codes

        # Parse HTML content
        soup = bs(r.content, 'html.parser')

        # Find and load JSON data
        json_script = soup.find('script', attrs={'id': '__NEXT_DATA__'})
        if not json_script:
            raise ValueError("Could not find __NEXT_DATA__ script in the page")

        json_fotmob = json.loads(json_script.contents[0])

        # Extract match metadata
        general = json_fotmob['props']['pageProps']['general']
        header = json_fotmob['props']['pageProps']['header']
        content = json_fotmob['props']['pageProps']['content']

        # Extract required fields
        match_data = {
            'matchId': general['matchId'],
            'matchRound': general['matchRound'],
            'homeTeamName': general['homeTeam']['name'],
            'homeTeamId': general['homeTeam']['id'],
            'awayTeamName': general['awayTeam']['name'],
            'awayTeamId': general['awayTeam']['id'],
            'matchDate': general['matchTimeUTCDate'],
            'home_goals': header['teams'][0]['score'],
            'away_goals': header['teams'][1]['score']
        }

        # Create DataFrame from shots data
        df_shots = pd.DataFrame(content['shotmap']['shots'])

        # Add match metadata to each row in df_shots
        for key, value in match_data.items():
            df_shots[key] = value

        # Reorder columns to have match metadata first
        metadata_cols = list(match_data.keys())
        shot_cols = [col for col in df_shots.columns if col not in metadata_cols]
        df_shots = df_shots[metadata_cols + shot_cols]

        return df_shots, match_data

    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None, None
    except KeyError as e:
        print(f"Error extracting data: Missing key {e}")
        print("The page structure might have changed or the URL might be invalid")
        return None, None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None


def main():
    """
    Main execution function
    """
    # Get URL input from user
    url_input = input('Enter FotMob URL: ').strip()

    if not url_input:
        print("No URL provided. Exiting.")
        return

    # Scrape the data
    df_shots, match_data = scrape_fotmob_match(url_input)

    if df_shots is None:
        print("Failed to scrape data. Exiting.")
        return

    # Extract match name from URL
    match_name = extract_match_name_from_url(url_input)
    print(f"Match identified: {match_name}")

    # Set the output directory
    csv_directory = "/home/axel/Code/Python/championship/shots/csv/"

    # Get unique filename
    output_path = get_unique_filename(csv_directory, match_name)

    # Save to CSV
    df_shots.to_csv(output_path, index=False)
    print(f"Data successfully saved to: {output_path}")

    # Print summary
    print("\n=== Match Summary ===")
    print(f"Match ID: {match_data['matchId']}")
    print(f"Round: {match_data['matchRound']}")
    print(f"{match_data['homeTeamName']} {match_data['home_goals']} - {match_data['away_goals']} {match_data['awayTeamName']}")
    print(f"Date: {match_data['matchDate']}")
    print(f"Total shots recorded: {len(df_shots)}")


if __name__ == "__main__":
    main()
