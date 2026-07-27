import pandas as pd

def prepare_training_data(df: pd.DataFrame):
    metadata_cols= [
        "date", "home_team", "away_team", "city", "country",
        "tournament", "match_type", "home_res", "home_score",
        "away_score", "year", "gd", "id", "Unnamed: 0"
    ]
    clean_df= df[df["year"]>2003].dropna()
    cols_to_drop= [col for col in metadata_cols if col in clean_df.columns]
    X= clean_df.drop(columns=cols_to_drop, errors="ignore")
    y= clean_df["gd"] if "gd" in clean_df.columns else None
    return X, y

def prepare_features_for_prediction(df: pd.DataFrame) -> pd.DataFrame:
    if "gd" in df.columns:
        df = df.drop(columns=["gd"], errors="ignore")    
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    if "away_score" in df.columns:
        df["away_score"] = df["away_score"].astype(int)
    if "home_score" in df.columns:
        df["home_score"] = df["home_score"].astype(int)
    if "gd" in df.columns:
        df["gd"] = df["gd"].astype(int)    
    return df
