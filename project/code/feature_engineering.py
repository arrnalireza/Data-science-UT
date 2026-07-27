import pandas as pd
import numpy as np
from collections import defaultdict
from perfect_config import pipeline_config
from helpers import classify_tournament
from elo import add_elo


def rank_tier(rank):
    if rank <= 15:
        return 1
    elif rank <= 40:
        return 2
    elif rank <= 80:
        return 3
    else:
        return 4


def add_rank(df):
    df["home_rank_tier"]= df["home_rank"].apply(rank_tier)
    df["away_rank_tier"]= df["away_rank"].apply(rank_tier)
    df["home_rank"]= df["home_rank"].astype("Int64")
    df["away_rank"]= df["away_rank"].astype("Int64")
    df["rank_diff"]= df["away_rank"] - df["home_rank"]
    return df


def add_winrate(df: pd.DataFrame):
    df= df.copy()
    home_df= df[["date", "home_team", "home_res", "gd"]].copy()
    home_df.columns= ["date", "team", "res", "sd"]

    away_df = df[["date", "away_team", "home_res", "gd"]].copy()
    away_df.columns= ["date", "team", "res", "sd"]
    away_df["res"]= 1 - away_df["res"]
    away_df["sd"]= -away_df["sd"]
    team_df = pd.concat([home_df, away_df]).sort_values(["team", "date"])
    team_df["last5_winrate"] = team_df.groupby("team")["res"].transform(
        lambda x: x.shift(1).rolling(5, min_periods=1).mean()
    )
    team_df["last5_avg_sd"] = team_df.groupby("team")["sd"].transform(
        lambda x: x.shift(1).rolling(5, min_periods=1).mean()
    )
    teams_features = team_df[["date", "team", "last5_winrate", "last5_avg_sd"]]
    teams_features = teams_features.drop_duplicates(subset=["date", "team"], keep="last")
    df= df.merge(
        teams_features,
        left_on=["date", "home_team"],
        right_on=["date", "team"],
        how="left",
    ).rename(
        columns={
            "last5_winrate": "home_last5_winrate",
            "last5_avg_sd": "home_last5_avg_sd",
        }
    )
    if "team" in df.columns:
        df = df.drop(columns=["team"])
    df= df.merge(
        teams_features,
        left_on=["date", "away_team"],
        right_on=["date", "team"],
        how="left",
    ).rename(
        columns={
            "last5_winrate": "away_last5_winrate",
            "last5_avg_sd": "away_last5_avg_sd",
        }
    )
    if "team" in df.columns:
        df = df.drop(columns=["team"])
    df["home_last5_winrate"] = df["home_last5_winrate"].fillna(0.5)
    df["away_last5_winrate"] = df["away_last5_winrate"].fillna(0.5)
    df["home_last5_avg_sd"] = df["home_last5_avg_sd"].fillna(0.0)
    df["away_last5_avg_sd"] = df["away_last5_avg_sd"].fillna(0.0)
    return df


def add_basic_features(df):
    df["gd"]= (df["home_score"]-df["away_score"])
    df["home_res"]= np.where((df["gd"] > 0), 1, np.where(df["gd"] == 0, 0.5, 0))
    df= add_rank(df)
    df= add_winrate(df)
    df["match_type"]= df["tournament"].map(classify_tournament)
    df["match_type_ordinal"]= df["match_type"].map(pipeline_config.match_type_order).astype(int)
    df["is_friendly"]= (df["match_type"] == "f").astype(int)
    return df


def add_advanced_features(df):
    df= df.copy()
    df["elo_diff"]= df["elo_home_pre"]-df["elo_away_pre"]
    elo_home_eff = df["elo_home_pre"]+df["neutral"].apply(lambda n: 0 if n else pipeline_config.home_advantage)
    df["elo_win_prob"]= 1/(1 + 10**((df["elo_away_pre"] - elo_home_eff) / 400.0))
    df["fifa_points_diff"]= df["home_fifa_points"] - df["away_fifa_points"]
    df["rank_ratio"]= df["away_rank"] / df["home_rank"]
    df["tier_diff"]= df["away_rank_tier"] - df["home_rank_tier"]
    df["winrate_diff"]= df["home_last5_winrate"] - df["away_last5_winrate"]
    df["avg_sd_diff"]= df["home_last5_avg_sd"] - df["away_last5_avg_sd"]
    df["value_diff"]= df["home_avg_value"] - df["away_avg_value"]
    df["value_ratio"]= df["home_avg_value"] / df["away_avg_value"].replace(0, np.nan)
    df["age_diff"]= df["home_avg_age"] - df["away_avg_age"]

    h2h_history= defaultdict(list)
    last_match_date= {}
    h2h_home_winrate= []
    h2h_avg_sd= []
    h2h_total= []
    home_days_rest= []
    away_days_rest= []
 
    for row in df.itertuples(index=False):
        home= row.home_team
        away= row.away_team
        date= row.date

        key= tuple(sorted([home, away]))
        past= h2h_history[key]
        is_home_key= (home == key[0])
        if len(past)== 0:
            h2h_home_winrate.append(np.nan)
            h2h_avg_sd.append(np.nan)
            h2h_total.append(0)
        elif len(past) < 5:
            last5 = past[-len(past):]
            wins = sum((1 if sd > 0 else 0) for sd in last5) if is_home_key else sum((1 if sd < 0 else 0) for sd in last5)
            h2h_home_winrate.append(wins / len(last5))
            raw_avg = np.mean(last5)
            h2h_avg_sd.append(raw_avg if is_home_key else -raw_avg)
            h2h_total.append(len(past))
        else:
            last5= past[-5:]
            wins= sum((1 if sd > 0 else 0) for sd in last5) if is_home_key else sum((1 if sd < 0 else 0) for sd in last5)
            h2h_home_winrate.append(wins/len(last5))
            raw_avg= np.mean(last5)
            h2h_avg_sd.append(raw_avg if is_home_key else -raw_avg)
            h2h_total.append(len(past))
 
        if home in last_match_date:
            home_days_rest.append(min(pipeline_config.max_rest_day, (date - last_match_date[home]).days))
        else:
            home_days_rest.append(pipeline_config.max_rest_day)
 
        if away in last_match_date:
            away_days_rest.append(min(pipeline_config.max_rest_day, (date - last_match_date[away]).days))
        else:
            away_days_rest.append(pipeline_config.max_rest_day)
            
        sd = row.gd
        if key[0] == home:
            h2h_history[key].append(sd)
        else:
            h2h_history[key].append(-sd)
        last_match_date[home] = date
        last_match_date[away] = date
 
    df["h2h_last5_home_winrate"] = h2h_home_winrate
    df["h2h_last5_avg_gd"] = h2h_avg_sd
    df["h2h_total_matches"] = h2h_total
    df["h2h_is_first_meeting"] = (df["h2h_total_matches"] == 0).astype(int)
    df["home_days_rest"] = home_days_rest
    df["away_days_rest"] = away_days_rest
    df["rest_diff"] = df["home_days_rest"] - df["away_days_rest"]
    df["h2h_last5_home_winrate"] = df["h2h_last5_home_winrate"].fillna(0.5)
    df["h2h_last5_avg_gd"] = df["h2h_last5_avg_gd"].fillna(0.0)
    return df

def run_feature_pipeline(df: pd.DataFrame):
    df_processed= df.copy()
    df_processed= add_basic_features(df_processed)
    df_processed= add_elo(df_processed)
    df_processed= add_advanced_features(df_processed)
    return df_processed
