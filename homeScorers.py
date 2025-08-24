import pandas as pd
import requests
import json
from bs4 import BeautifulSoup as bs
import time

def scrape_goal_scorer_data(url, goal_scorer):
    """
    Scrape data for a specific goal scorer from the given URL
    """
    try:
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')
        json_data = json.loads(soup.find('script', attrs={'id': '__NEXT_DATA__'}).contents[0])

        # Navigate to the specific path and get data for the goal scorer
        home_team_goals = json_data['props']['pageProps']['header']['events']['homeTeamGoals']

        # Check if the goal scorer exists in the data
        if goal_scorer in home_team_goals:
            return home_team_goals[goal_scorer]
        else:
            print(f"Goal scorer '{goal_scorer}' not found in data")
            return None

    except Exception as e:
        print(f"Error scraping data for {goal_scorer}: {str(e)}")
        return None

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

    # Process each goal scorer
    for scorer in goal_scorers:
        print(f"Processing: {scorer}")

        # Scrape data for this goal scorer
        scorer_data = scrape_goal_scorer_data(url, scorer)

        if scorer_data is not None:
            # Convert the data to a DataFrame
            if isinstance(scorer_data, dict):
                # If it's a dictionary, create a single-row DataFrame
                scorer_df = pd.DataFrame([scorer_data])
            elif isinstance(scorer_data, list):
                # If it's a list, create a DataFrame from the list
                scorer_df = pd.DataFrame(scorer_data)
            else:
                # If it's a simple value, create a DataFrame with one column
                scorer_df = pd.DataFrame({'value': [scorer_data]})

            # Add a column to identify which goal scorer this data belongs to
            scorer_df['goal_scorer'] = scorer

            # Add to our list of dataframes
            all_dataframes.append(scorer_df)

            # Add a small delay to be respectful to the server
            time.sleep(0.5)
        else:
            print(f"No data found for {scorer}")

    # Combine all dataframes
    if all_dataframes:
        final_df = pd.concat(all_dataframes, ignore_index=True)

        # Save to new CSV file
        try:
            final_df.to_csv(output_csv_path, index=False)
            print(f"Data saved successfully to {output_csv_path}")
            print(f"Final dataset shape: {final_df.shape}")
            print(f"Columns in final dataset: {list(final_df.columns)}")
        except Exception as e:
            print(f"Error saving CSV file: {str(e)}")
    else:
        print("No data was successfully scraped for any goal scorer")

# Example usage
if __name__ == "__main__":
    # Configuration
    input_csv_file = "your_input_file.csv"  # Replace with your CSV file path
    output_csv_file = "goal_scorer_data.csv"  # Output file name
    target_url = "https://www.fotmob.com/es/matches/liverpool-vs-afc-bournemouth/2he69q#4813374"  # Replace with your target URL
    column_name = "goal_scorer"  # Replace if your column has a different name

    # Process the data
    process_goal_scorers_csv(
        csv_file_path='/home/axel/Code/Python/championship/csv/test9.csv',
        url=target_url,
        output_csv_path='/home/axel/Code/Python/championship/csv/test10.csv',
        goal_scorer_column=column_name
    )

    # Optional: Display the first few rows of the result
    try:
        result_df = pd.read_csv(output_csv_file)
        print("\nFirst 5 rows of the result:")
        print(result_df.head())
    except:
        print("Could not display results")
