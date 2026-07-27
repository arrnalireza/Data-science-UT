import os
import joblib
from perfect_config import pipeline_config

def save_models(best_xgb, best_lgb, best_cat, filepath: str = pipeline_config.model_path):
    """Saves the fitted models to disk using joblib."""
    models_dict = {
        "xgb": best_xgb,
        "lgb": best_lgb,
        "cat": best_cat
    }
    joblib.dump(models_dict, filepath)

def load_models(filepath: str = pipeline_config.model_path) -> tuple:
    models_dict = joblib.load(filepath)
    return models_dict["xgb"], models_dict["lgb"], models_dict["cat"]

def models_exist(filepath: str = pipeline_config.model_path) -> bool:
    return os.path.exists(filepath)