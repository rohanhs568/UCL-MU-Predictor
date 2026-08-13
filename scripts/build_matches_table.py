from pathlib import Path
import re
import sqlite3

import pandas as pd


DOMESTIC_FOLDER = Path("data/raw/eu_domestic")
CL_FOLDER = Path("data/raw/cl")
DB_PATH = Path("data/processed/football.db")

DOMESTIC_LEAGUES = {
    "E0", "SC0", "D1", "SP1", "I1", "F1",
    "B1", "N1", "P1", "T1", "G1"
}


def season_from_filename(filename):
    match = re.search(r"(\d{4})(?:-to-|-)(\d{4})", filename)

    if match is None:
        raise ValueError(f"Could not read season from filename: {filename}")

    start_year = match.group(1)
    end_year = match.group(2)

    return f"{start_year}/{end_year[-2:]}"


def load_alias_lookup(connection):
    aliases = pd.read_sql_query(
        """
        SELECT alias, source, league, team_id
        FROM team_aliases
        """,
        connection
    )

    return {
        (row.alias, row.source, row.league): int(row.team_id)
        for row in aliases.itertuples(index=False)
    }


def load_team_name_lookup(connection):
    teams = pd.read_sql_query(
        """
        SELECT team_id, canonical_name
        FROM teams
        """,
        connection
    )

    return {
        int(row.team_id): row.canonical_name
        for row in teams.itertuples(index=False)
    }


def get_team_id(team_name, source, league, alias_lookup):
    key = (team_name, source, league)

    if key not in alias_lookup:
        raise ValueError(
            f"No team mapping found for: "
            f"name={team_name!r}, source={source!r}, league={league!r}"
        )

    return alias_lookup[key]


def build_domestic_matches(alias_lookup, team_name_lookup):
    matches = []

    for file_path in sorted(DOMESTIC_FOLDER.iterdir()):
        if file_path.suffix.lower() not in [".xls", ".xlsx"]:
            continue

        season = season_from_filename(file_path.name)
        workbook = pd.ExcelFile(file_path)

        for league in DOMESTIC_LEAGUES:
            if league not in workbook.sheet_names:
                continue

            df = workbook.parse(
                league,
                usecols=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
            )

            for row in df.itertuples(index=False):
                # One audited abandoned Greek match has no final score.
                if pd.isna(row.FTHG) or pd.isna(row.FTAG):
                    date = pd.to_datetime(row.Date, dayfirst=True)

                    known_abandoned_match = (
                        season == "2018/19"
                        and league == "G1"
                        and date.date().isoformat() == "2019-03-17"
                        and row.HomeTeam == "Panathinaikos"
                        and row.AwayTeam == "Olympiakos"
                    )

                    if known_abandoned_match:
                        continue

                    raise ValueError(
                        f"Unexpected missing score: "
                        f"{season}, {league}, {row.HomeTeam} v {row.AwayTeam}"
                    )

                date = pd.to_datetime(row.Date, dayfirst=True)

                home_id = get_team_id(
                    row.HomeTeam,
                    "football_data",
                    league,
                    alias_lookup
                )

                away_id = get_team_id(
                    row.AwayTeam,
                    "football_data",
                    league,
                    alias_lookup
                )

                matches.append({
                    "date": date.date().isoformat(),
                    "season": season,
                    "competition": league,
                    "home_team_id": home_id,
                    "away_team_id": away_id,
                    "home_team_name": team_name_lookup[home_id],
                    "away_team_name": team_name_lookup[away_id],
                    "home_goals": int(row.FTHG),
                    "away_goals": int(row.FTAG),
                    "source": "football_data",
                })

        workbook.close()

    return matches


def build_cl_matches(alias_lookup, team_name_lookup):
    matches = []

    for file_path in sorted(CL_FOLDER.glob("*.csv")):
        season = season_from_filename(file_path.name)

        df = pd.read_csv(
            file_path,
            usecols=[
                "date_GMT",
                "home_team_name",
                "away_team_name",
                "home_team_goal_count",
                "away_team_goal_count",
                "status",
            ]
        )

        df = df[df["status"].str.lower() == "complete"].copy()

        for row in df.itertuples(index=False):
            date_text = row.date_GMT.split(" - ")[0]
            date = pd.to_datetime(date_text, format="%b %d %Y")

            home_id = get_team_id(
                row.home_team_name,
                "footystats",
                "CL",
                alias_lookup
            )

            away_id = get_team_id(
                row.away_team_name,
                "footystats",
                "CL",
                alias_lookup
            )

            matches.append({
                "date": date.date().isoformat(),
                "season": season,
                "competition": "CL",
                "home_team_id": home_id,
                "away_team_id": away_id,
                "home_team_name": team_name_lookup[home_id],
                "away_team_name": team_name_lookup[away_id],
                "home_goals": int(row.home_team_goal_count),
                "away_goals": int(row.away_team_goal_count),
                "source": "footystats",
            })

    return matches


def save_matches(connection, matches):
    matches_df = pd.DataFrame(matches)

    matches_df = matches_df.sort_values(
        ["date", "competition", "home_team_id", "away_team_id"]
    ).reset_index(drop=True)

    matches_df.insert(0, "match_id", range(1, len(matches_df) + 1))

    duplicate_columns = [
        "date",
        "competition",
        "home_team_id",
        "away_team_id",
    ]

    duplicates = matches_df.duplicated(
        subset=duplicate_columns,
        keep=False
    )

    if duplicates.any():
        print(matches_df.loc[duplicates, duplicate_columns])
        raise ValueError("Duplicate matches found. Nothing was written to the database.")

    connection.execute("DROP TABLE IF EXISTS matches")

    connection.execute(
        """
        CREATE TABLE matches (
            match_id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            season TEXT NOT NULL,
            competition TEXT NOT NULL,
            home_team_id INTEGER NOT NULL,
            away_team_id INTEGER NOT NULL,
            home_team_name TEXT NOT NULL,
            away_team_name TEXT NOT NULL,
            home_goals INTEGER NOT NULL,
            away_goals INTEGER NOT NULL,
            source TEXT NOT NULL,
            FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
            FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
        )
        """
    )

    matches_df.to_sql(
        "matches",
        connection,
        if_exists="append",
        index=False
    )

    connection.commit()

    return matches_df


def main():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    alias_lookup = load_alias_lookup(connection)
    team_name_lookup = load_team_name_lookup(connection)

    domestic_matches = build_domestic_matches(
        alias_lookup,
        team_name_lookup
    )

    cl_matches = build_cl_matches(
        alias_lookup,
        team_name_lookup
    )

    all_matches = domestic_matches + cl_matches

    matches_df = save_matches(connection, all_matches)

    print(f"Created matches table with {len(matches_df)} rows.")
    print()
    print(matches_df.head())
    print()
    print(matches_df.tail())

    connection.close()


if __name__ == "__main__":
    main()
