from pathlib import Path
import pandas as pd


data_folder = Path("Data/raw/eu_domestic")

selected_leagues = ['E0', 'SC0', 'D1', 'I1', 'SP1', 'F1', 'B1', 'N1', 'P1', 'T1', 'G1']

def check_nulls():
    for file_path in sorted(
    path for path in data_folder.iterdir()
    if "2026-2027" not in path.name
    ):

        if file_path.suffix.lower() not in [".xls", ".xlsx"]:
            continue

        print()
        print(file_path.name)

        excel_file = pd.ExcelFile(file_path)

        for league in selected_leagues:
            df = excel_file.parse(league)

            total_len = 0
            date_null_vals = 0
            ht_null_vals = 0
            at_null_vals = 0
            fthg_null_vals = 0
            ftag_null_vals = 0

            total_len = len(df)

            date_null_vals =  df['Date'].isna().sum()
            ht_null_vals =  df['HomeTeam'].isna().sum()
            at_null_vals =  df['AwayTeam'].isna().sum()
            fthg_null_vals =  df['FTHG'].isna().sum()
            ftag_null_vals =  df['FTAG'].isna().sum()

            print(league)
            print('total len = ' + str(total_len))
            print('missing values:')
            print('date ' + str(date_null_vals))
            print('hometeam ' + str(ht_null_vals))
            print('awayteam ' + str(at_null_vals))
            print('fthg_null_vals ' + str(fthg_null_vals))
            print('ftag_null_vals ' + str(ftag_null_vals))

def check_dtypes():
    for file_path in sorted(
        path for path in data_folder.iterdir()
        if "2026-2027" not in path.name
        ):
    
            if file_path.suffix.lower() not in [".xls", ".xlsx"]:
                continue
    
            print()
            print(file_path.name)
    
            excel_file = pd.ExcelFile(file_path)
    
            for league in selected_leagues:
                df = excel_file.parse(league)
                print(df[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dtypes)

                if (df['FTHG'].dropna() < 0).sum() != 0  or ((df['FTAG'].dropna() < 0).sum()):
                    print("negative goals appear")
                else:
                    print("goals positive!")

                if (df['FTHG'].dropna() % 1 != 0).sum() != 0 or (df['FTAG'].dropna() % 1 != 0).sum() != 0:
                    print("fractional goals appear")
                else:
                    print("goals whole!")

def inspect_team_names():
    home_team_names = {}
    away_team_names = {}

    for file_path in sorted(
            path for path in data_folder.iterdir()
            if "2026-2027" not in path.name
            ):
        
            if file_path.suffix.lower() not in [".xls", ".xlsx"]:
                continue
    
            excel_file = pd.ExcelFile(file_path)

            for league in selected_leagues:
                df = excel_file.parse(league)

                for team in df['HomeTeam']:
                    home_team_names[team] = 0

                for team in df['AwayTeam']:
                    away_team_names[team] =0

    print(home_team_names)
    print(home_team_names == away_team_names)






if __name__ == "__main__":
    inspect_team_names()