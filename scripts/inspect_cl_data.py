from pathlib import Path
import pandas as pd


data_folder = Path("Data/raw/cl")

def check_column_health():
    for file_path in (
        path for path in data_folder.iterdir()
        if "2026-to-2027" not in path.name
        ):
        print(file_path.name)
        df = pd.read_csv(file_path)

        print(len(df))

        print(df[['date_GMT', 'home_team_name', 'away_team_name', 'home_team_goal_count', 'away_team_goal_count']].dtypes)

        if (df['home_team_goal_count'].dropna() < 0).sum() != 0  or ((df['away_team_goal_count'].dropna() < 0).sum()):
            print("negative goals appear")
        else:
            print("goals positive!")

        if (df['home_team_goal_count'].dropna() % 1 != 0).sum() != 0 or (df['away_team_goal_count'].dropna() % 1 != 0).sum() != 0:
            print("fractional goals appear")
        else:
            print("goals whole!")

        print((df[['date_GMT', 'home_team_name', 'away_team_name', 'home_team_goal_count', 'away_team_goal_count']].isna().sum()))

def inspect_team_names():
    home_team_names = {}
    away_team_names = {}

    for file_path in sorted(
            path for path in data_folder.iterdir()
            if "2026-to-2027" not in path.name
            ):
    
            df = pd.read_csv(file_path)



            for team in df['home_team_name']:
                home_team_names[team] = 0

            for team in df['away_team_name']:
                away_team_names[team] = 0

    print(home_team_names)
    print(home_team_names == away_team_names)

    print(set(home_team_names.keys()).symmetric_difference(set(away_team_names.keys()))) 

if __name__ == "__main__":
    inspect_team_names()
