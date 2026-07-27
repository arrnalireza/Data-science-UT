import pandas as pd
from collections import defaultdict
from perfect_config import pipeline_config

def classify_tournament(tournament: str):
    t= tournament.lower()
    if any(k in t for k in pipeline_config.qualifier_keyword):
        return "q"
    if any(k in t for k in pipeline_config.worldcup_keyword):
        return "w"
    if any(k in t for k in pipeline_config.tournament_keyword):
        return "t"
    return "f"


def normalize_series(series: pd.Series):
    renamed = series.map(lambda x: pipeline_config.renames.get(x, x))
    return renamed.where(renamed.isin(pipeline_config.valid_fifa_names))

def compute_rolling_features(clean_df: pd.DataFrame):
    """Computes pre-match rolling 5-match winrates and average goal differences safely."""
    clean_df= clean_df.copy()
    home_df= clean_df[["date", "home_team", "home_res", "gd"]].copy()
    away_df= clean_df[["date", "away_team", "home_res", "gd"]].copy()
    away_df.columns= ["date", "team", "res", "sd"]
    home_df.columns= ["date", "team", "res", "sd"]
    away_df["res"]= 1 - away_df["res"]
    away_df["sd"]= -away_df["sd"]
    team_df = pd.concat([home_df, away_df]).sort_values(["team", "date"])
    team_df["rolling_winrate"] = team_df.groupby("team")["res"].transform(
        lambda x: x.shift(1).rolling(5, min_periods=1).mean()
    )
    team_df["rolling_avg_sd"] = team_df.groupby("team")["sd"].transform(
        lambda x: x.shift(1).rolling(5, min_periods=1).mean()
    )
    team_df= team_df.drop(columns=["sd", "res"])
    team_df= team_df.drop_duplicates(subset=["team", "date"], keep="last")
    df_merged= clean_df.merge(
        team_df,
        left_on=["date", "home_team"],
        right_on=["date", "team"],
        how="left",
    ).rename(
        columns={
            "rolling_winrate": "home_last5_winrate",
            "rolling_avg_sd": "home_last5_avg_sd",
        }
    ).drop(
        columns=["team"]
    )
    df_merged= df_merged.merge(
        team_df,
        left_on=["date", "away_team"],
        right_on=["date", "team"],
        how="left",
    ).rename(
        columns={
            "rolling_winrate": "away_last5_winrate",
            "rolling_avg_sd": "away_last5_avg_sd",
        }
    ).drop(
        columns=["team"]
    )
    df_merged["home_last5_winrate"] = df_merged["home_last5_winrate"].fillna(0.5)
    df_merged["away_last5_winrate"] = df_merged["away_last5_winrate"].fillna(0.5)
    df_merged["home_last5_avg_sd"] = df_merged["home_last5_avg_sd"].fillna(0.0)
    df_merged["away_last5_avg_sd"] = df_merged["away_last5_avg_sd"].fillna(0.0)
    return df_merged


def build_h2h_history(clean_df: pd.DataFrame):
    """Builds a historical head-to-head match dictionary mapped by team pairs."""
    h2h_history = defaultdict(lambda: defaultdict(list))
    for row in clean_df.itertuples(index=False):
        home, away, gd = row.home_team, row.away_team, row.gd
        h2h_history[home][away].append(gd)
        h2h_history[away][home].append(-gd)
    return h2h_history


def extract_latest_team_features(clean_df: pd.DataFrame):
    """Extracts the most recent feature snapshot for every unique team in clean_df."""
    team_features= {}
    df_sorted= clean_df.sort_values("date")
    unique_teams= pd.concat([df_sorted["home_team"], df_sorted["away_team"]]).unique()
    for team in unique_teams:
        home_rows = df_sorted[df_sorted["home_team"] == team]
        away_rows = df_sorted[df_sorted["away_team"] == team]
        last_home = home_rows.iloc[-1] if len(home_rows) > 0 else None
        last_away = away_rows.iloc[-1] if len(away_rows) > 0 else None
        if last_home is not None and last_away is not None:
            row_is_home = last_home["date"] >= last_away["date"]
        elif last_home is not None:
            row_is_home = True
        else:
            row_is_home = False

        if row_is_home:
            row = last_home
            prefix = "home_"
        else:
            row = last_away
            prefix = "away_"
        post_winrate_col = f"{prefix}post_last5_winrate"
        post_sd_col = f"{prefix}post_last5_avg_sd"
        winrate_col = f"{prefix}last5_winrate"
        sd_col = f"{prefix}last5_avg_sd"
        last5_winrate_val= (row[winrate_col] if winrate_col in row else row.get(post_winrate_col, 0.5))
        last5_sd_val = row[sd_col] if sd_col in row else row.get(post_sd_col, 0.0)

        post_winrate_val= (
            row[post_winrate_col]
            if post_winrate_col in row
            else last5_winrate_val
        )
        post_sd_val= row[post_sd_col] if post_sd_col in row else last5_sd_val

        team_features[team]= {
            "elo": (row["elo_home_pre"] if row_is_home else row["elo_away_pre"]),
            "rank": row[f"{prefix}rank"],
            "fifa_points": row[f"{prefix}fifa_points"],
            "rank_tier": row[f"{prefix}rank_tier"],
            "last5_winrate": last5_winrate_val,
            "last5_avg_sd": last5_sd_val,
            "post_last5_winrate": post_winrate_val,
            "post_last5_avg_sd": post_sd_val,
            "avg_age": row[f"{prefix}avg_age"],
            "avg_value": row[f"{prefix}avg_value"],
            "last_match_date": row["date"],
        }
    return team_features

