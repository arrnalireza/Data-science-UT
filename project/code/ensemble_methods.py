import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def optimize_weights(oof_xgb: np.ndarray, oof_lgb: np.ndarray, oof_cat: np.ndarray, y: pd.Series):
    def ensemble_mse(weights):
        w = np.abs(weights) / (np.sum(np.abs(weights)) + 1e-9)
        preds = w[0] * oof_xgb + w[1] * oof_lgb + w[2] * oof_cat
        return mean_squared_error(y, preds)
    initial_weights = np.array([1.0, 1.0, 1.0])
    res = minimize(ensemble_mse, initial_weights, method="Nelder-Mead", options={"maxiter": 5000})
    best_weights = np.abs(res.x) / np.sum(np.abs(res.x))    
    return best_weights

def compute_ensemble(oof_xgb: np.ndarray, oof_lgb: np.ndarray, oof_cat: np.ndarray, weights: np.ndarray):
    ensemble_pred= weights[0]*oof_xgb + weights[1]*oof_lgb + weights[2]*oof_cat
    return ensemble_pred

def evaluate_ensemble(ensemble_pred: np.ndarray, y: pd.Series):
    mse= mean_squared_error(y, ensemble_pred)
    mae= mean_absolute_error(y, ensemble_pred)
    r2= r2_score(y, ensemble_pred)
    metrics = {"mse": mse, "mae": mae, "r2": r2}
    return metrics
