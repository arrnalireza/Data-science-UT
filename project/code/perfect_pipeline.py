from load_data_db import load_training_data
from data_prep import prepare_training_data, handle_missing_values
from model_training import setup_models, fit_models, cross_validate
from ensemble_methods import optimize_weights, compute_ensemble, evaluate_ensemble
from database_connection import get_engine
from model_io import save_models, load_models, models_exist
from import_features_to_db import import_raw_csvs
from feature_engineering import run_feature_pipeline


class PerfectPipeline:
    def __init__(self):
        self.df= None
        self.X= None
        self.y= None
        self.models= None
        self.oof_preds= None
        self.weights= None
        self.ensemble_pred= None
        self.metrics= None
        self.engine= get_engine()

    def load(self):
        print("Loading data...")
        import_raw_csvs()
        self.df = load_training_data(self.engine)
        print("✓ Data loaded")
        return self

    def preprocess(self):
        print("Preprocessing data...")
        self.df = handle_missing_values(self.df)
        self.df = run_feature_pipeline(self.df)
        self.X, self.y = prepare_training_data(self.df)
        print("✓ Preprocessing completed")
        return self
    
    def setup_models(self):
        print("Setting up models...")
        if models_exist():
            print("✓ Existing models found")
            return self
        xgb_grid, lgb_grid, cat_grid = setup_models()
        self.models = (xgb_grid, lgb_grid, cat_grid)
        print("✓ Models initialized")
        return self
    
    def fit_models(self) -> "PerfectPipeline":
        print("Training models...")
        if models_exist():
            best_xgb, best_lgb, best_cat = load_models()
            self.models = (best_xgb, best_lgb, best_cat)
            print("✓ Models loaded from disk")
            return self
        best_xgb, best_lgb, best_cat = fit_models(self.X, self.y, *self.models)
        self.models = (best_xgb, best_lgb, best_cat)
        save_models(best_xgb, best_lgb, best_cat)
        print("✓ Training completed")
        return self
    
    def cross_validate(self):
        print("Running cross-validation...")
        oof_xgb, oof_lgb, oof_cat = cross_validate(self.X, self.y, *self.models)
        self.oof_preds = (oof_xgb, oof_lgb, oof_cat)
        print("✓ Cross-validation completed")
        return self
    
    def optimize_ensemble(self):
        print("Optimizing ensemble weights...")
        oof_xgb, oof_lgb, oof_cat = self.oof_preds
        self.weights = optimize_weights(oof_xgb, oof_lgb, oof_cat, self.y)
        print("✓ Ensemble optimized")
        return self
    
    def ensemble_predict(self):
        print("Computing ensemble predictions...")
        oof_xgb, oof_lgb, oof_cat = self.oof_preds
        self.ensemble_pred = compute_ensemble(oof_xgb, oof_lgb, oof_cat, self.weights)
        print("✓ Predictions generated")
        return self
    
    def evaluate(self):
        print("Evaluating model...")
        self.metrics = evaluate_ensemble(self.ensemble_pred, self.y)
        print("✓ Evaluation completed")
        return self
    
    def execute(self):
        print("PERFECT PIPELINE EXECUTION STARTED")
        
        self.load()
        self.preprocess()
        self.setup_models()
        self.fit_models()
        self.cross_validate()
        self.optimize_ensemble()
        self.ensemble_predict()
        self.evaluate()

        print("PERFECT PIPELINE EXECUTION COMPLETED")
        
        return {
            "data": self.df,
            "X": self.X,
            "y": self.y,
            "models": self.models,
            "weights": self.weights,
            "metrics": self.metrics,
            "engine": self.engine
        }
    
    def get_results(self) -> dict:
        return {
            "training_shape": self.X.shape if self.X is not None else None,
            "target_shape": self.y.shape if self.y is not None else None,
            "weights": self.weights.tolist() if self.weights is not None else None,
            "metrics": self.metrics
        }


if __name__ == "__main__":
    pipeline = PerfectPipeline()
    results = pipeline.execute()
    print("\nResults Summary:")
    print(pipeline.get_results())
