from pathlib import Path
import pandas as pd


data_folder_cl = Path("Data/raw/cl")
data_folder_dom = Path("Data/raw/eu_domestic")

team_name_league_source = set()

selected_leagues = [
    'E0', 'SC0', 'D1', 'I1', 'SP1',
    'F1', 'B1', 'N1', 'P1', 'T1', 'G1'
]

# domestic
for file_path in sorted(
    path for path in data_folder_dom.iterdir()
    if "2026-2027" not in path.name
):

    if file_path.suffix.lower() not in [".xls", ".xlsx"]:
        continue

    excel_file = pd.ExcelFile(file_path)

    for league in selected_leagues:
        df = excel_file.parse(league)

        for team_name in df['HomeTeam']:
            team_name_league_source.add((team_name, league, "football_data"))

        for team_name in df['AwayTeam']:
            team_name_league_source.add((team_name, league, "football_data"))


# cl
for file_path in sorted(
    path for path in data_folder_cl.iterdir()
    if "2026-to-2027" not in path.name
):

    if file_path.suffix.lower() != ".csv":
        continue

    df = pd.read_csv(file_path)

    for team_name in df['home_team_name']:
        team_name_league_source.add((team_name, "CL", "footystats"))

    for team_name in df['away_team_name']:
        team_name_league_source.add((team_name, "CL", "footystats"))


team_name_dict = {
    'team_name': [team_tuple[0] for team_tuple in team_name_league_source],
    'league': [team_tuple[1] for team_tuple in team_name_league_source],
    'source': [team_tuple[2] for team_tuple in team_name_league_source]
}

team_name_df = pd.DataFrame(team_name_dict)


# print(team_name_df.head())
# print(team_name_df.shape)

# print(team_name_df.isna().sum())

# print(
#     team_name_df.duplicated(
#         subset=['team_name', 'league', 'source']
#     ).sum()
# )

# print(team_name_df['source'].value_counts())
# print(team_name_df['league'].value_counts())

import sqlite3

connection = sqlite3.connect("Data/processed/football.db")

team_name_df.to_sql(
    "raw_team_names",
    connection,
    if_exists="replace",
    index=False
)

connection.close()