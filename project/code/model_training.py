import numpy as np
import pandas as pd
import mlflow
import mlflow.xgboost
import mlflow.lightgbm
import mlflow.catboost
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from perfect_config import pipeline_config


def setup_models():
    xgb_param_grid= {
        "n_estimators": [400, 600],
        "max_depth": [4, 6],
        "learning_rate": [0.05],
        "subsample": [0.85],
        "colsample_bytree": [0.8],
        "min_child_weight": [1],
        "gamma": [0.0],
    }

    lgb_param_grid= {
        "n_estimators": [400],
        "num_leaves": [31, 63],
        "learning_rate": [0.03, 0.05],
        "subsample": [0.8],
        "colsample_bytree": [0.85],
        "min_child_samples": [10],
    }

    cat_param_grid= {
        "depth": [4, 6],
        "learning_rate": [0.03, 0.05],
        "iterations": [400, 600],
    }

    tscv= TimeSeriesSplit(n_splits=pipeline_config.n_splits)
    xgb_grid= GridSearchCV(
        XGBRegressor(random_state=pipeline_config.random_state, n_jobs=-1),
        param_grid=xgb_param_grid,
        cv=tscv,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
    )
    lgb_grid= GridSearchCV(
        LGBMRegressor(random_state=pipeline_config.random_state, n_jobs=-1),
        param_grid=lgb_param_grid,
        cv=tscv,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
        verbose=0
    )
    cat_grid= GridSearchCV(
        CatBoostRegressor(random_state=pipeline_config.random_state, verbose=0),
        param_grid=cat_param_grid,
        cv=tscv,
        scoring="neg_mean_squared_error",
        n_jobs=-1,
    )
    return xgb_grid, lgb_grid, cat_grid


def fit_models(
    X: pd.DataFrame,
    y: pd.Series,
    xgb_grid: GridSearchCV,
    lgb_grid: GridSearchCV,
    cat_grid: GridSearchCV
):

    xgb_grid.fit(X, y)
    lgb_grid.fit(X, y)
    cat_grid.fit(X, y)
    mlflow.log_params({f"xgb_{k}": v for k, v in xgb_grid.best_params_.items()})
    mlflow.log_params({f"lgb_{k}": v for k, v in lgb_grid.best_params_.items()})
    mlflow.log_params({f"cat_{k}": v for k, v in cat_grid.best_params_.items()})
    mlflow.log_metric("xgb_best_cv_mse", -xgb_grid.best_score_)
    mlflow.log_metric("lgb_best_cv_mse", -lgb_grid.best_score_)
    mlflow.log_metric("cat_best_cv_mse", -cat_grid.best_score_)
    best_xgb= xgb_grid.best_estimator_
    best_lgb= lgb_grid.best_estimator_
    best_cat= cat_grid.best_estimator_

    mlflow.xgboost.log_model(best_xgb, artifact_path="xgboost_model")
    mlflow.lightgbm.log_model(best_lgb, artifact_path="lightgbm_model")
    mlflow.catboost.log_model(best_cat, artifact_path="catboost_model")
    return best_xgb, best_lgb, best_cat


def cross_validate(
    X: pd.DataFrame,
    y: pd.Series,
    best_xgb,
    best_lgb,
    best_cat
):

    tscv= TimeSeriesSplit(n_splits=pipeline_config.n_splits)
    oof_xgb= np.zeros(len(X))
    oof_lgb= np.zeros(len(X))
    oof_cat= np.zeros(len(X))

    for train_idx, val_idx in tscv.split(X):
        X_train, X_val= X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val= y.iloc[train_idx], y.iloc[val_idx]

        xgb_model= best_xgb
        xgb_model.fit(X_train, y_train)
        oof_xgb[val_idx]= xgb_model.predict(X_val)

        lgb_model= best_lgb
        lgb_model.fit(X_train, y_train)
        oof_lgb[val_idx]= lgb_model.predict(X_val)

        cat_model= best_cat
        cat_model.fit(X_train, y_train)
        oof_cat[val_idx]= cat_model.predict(X_val)
        
    return oof_xgb, oof_lgb, oof_cat