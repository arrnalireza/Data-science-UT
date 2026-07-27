import pandas as pd
import numpy as np
from helpers import normalize_series
from perfect_config import pipeline_config

def convert_to_usd(x, eur_to_usd):
    if pd.isna(x):
        return np.nan
    x = str(x).strip()
    multiplier = 1
    if x.endswith("k"):
        multiplier = 1000
        x = x[:-1]
    elif x.endswith("m"):
        multiplier = 1_000_000
        x = x[:-1]
    if x.startswith("€"):
        return float(x[1:]) * multiplier * eur_to_usd
    if x.startswith("$"):
        return float(x[1:]) * multiplier
    return np.nan

def clean_team_name(df):
    df["home_team"] = normalize_series(df["home_team"])
    df = df[df["home_team"].notna()].copy()
    df["away_team"] = normalize_series(df["away_team"])
    df = df[df["away_team"].notna()].copy()
    return df

def merge_fifa_rank(df, rank_df):
    rank_df = rank_df.sort_values("year").drop_duplicates(subset=["team", "year"], keep="first")
    rank_df = rank_df[["team", "year", "rank", "points"]]
    rank_df["team"] = normalize_series(rank_df["team"])
    rank_df = rank_df[rank_df["team"].notna()].copy()
    
    home_rank = rank_df.rename(columns={"team": "home_team", "rank": "home_rank", "points": "home_fifa_points"})
    df = df.merge(home_rank, on=["year", "home_team"], how="left")
    
    away_rank = rank_df.rename(columns={"team": "away_team", "rank": "away_rank", "points": "away_fifa_points"})
    df = df.merge(away_rank, on=["year", "away_team"], how="left")
    
    return df.dropna(subset=["home_rank", "away_rank"])

def merge_tm(df, tm_df):
    tm_df["team"] = normalize_series(tm_df["team"])
    tm_df = tm_df[tm_df["team"].notna()].copy()
    if "team_id" in tm_df.columns:
        tm_df = tm_df.drop(columns="team_id")
    
    tm_df = tm_df.sort_values(["team", "year"])
    tm_df["avg_age"] = tm_df.groupby("team")["avg_age"].transform(lambda x: x.interpolate())
    tm_df["avg_age"] = tm_df.groupby("team")["avg_age"].transform(lambda x: x.ffill())
    tm_df["avg_market_value"] = tm_df["avg_market_value"].apply(lambda v: convert_to_usd(v, pipeline_config.euro_to_usd))
    tm_df["avg_market_value"] = tm_df.groupby("team")["avg_market_value"].transform(lambda x: x.ffill())

    home_tm_df = tm_df.rename(columns={"team": "home_team", "avg_age": "home_avg_age", "avg_market_value": "home_avg_value"})
    df = df.merge(home_tm_df, on=["year", "home_team"], how="left")
    
    away_tm_df = tm_df.rename(columns={"team": "away_team", "avg_age": "away_avg_age", "avg_market_value": "away_avg_value"})
    df = df.merge(away_tm_df, on=["year", "away_team"], how="left")
    return df

def load_training_data(engine):
    results_df= pd.read_sql("SELECT * FROM results", con=engine)
    fifa_df= pd.read_sql("SELECT * FROM fifa_ranking", con=engine)
    tm_df= pd.read_sql("SELECT * FROM squad_stats", con=engine)
        
    results_df["date"] = pd.to_datetime(results_df["date"])
    results_df = results_df.sort_values(by="date")
    results_df["year"] = results_df["date"].dt.year
    results_df = results_df[results_df["year"] >= 1992].dropna(subset=["home_score", "away_score"])
    
    df = clean_team_name(results_df)
    df = merge_fifa_rank(df, fifa_df)
    df = merge_tm(df, tm_df)
    
    df["away_score"] = df["away_score"].astype(int)
    df["home_score"] = df["home_score"].astype(int)
    if "gd" in df.columns:
        df["gd"] = df["gd"].astype(int)
    print(f"[load_training_data] Merged shape: {df.shape}")
    return df

if __name__ == "__main__":
    df = load_training_data()
    print(df.head())