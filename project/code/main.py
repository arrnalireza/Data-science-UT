import pandas as pd
import mlflow
from visualization import create_all_plots
from perfect_pipeline import PerfectPipeline
from simulate import TournamentSimulator
from perfect_config import pipeline_config
from database_connection import get_engine
from helpers import compute_rolling_features,build_h2h_history, extract_latest_team_features
import mlflow

mlflow.set_tracking_uri("sqlite:///C:/Users/alireza/Desktop/arrn/data%20science/p/mlflow.db")
mlflow.set_experiment("world_cup")

def load_simulation_metadata(clean_df):
    groups_df= pd.read_csv(pipeline_config.groups_path_csv)
    groups= groups_df.groupby("group")["team"].apply(list).to_dict()
    clean_df_with_rolling = compute_rolling_features(clean_df)
    h2h_history= build_h2h_history(clean_df_with_rolling)
    team_features= extract_latest_team_features(clean_df_with_rolling)
    return groups, team_features, h2h_history


def main():
    print("WORLD CUP PREDICTION & SIMULATION")
    engine = get_engine()
    with mlflow.start_run(run_name="Ensemble_v1"):
        pipeline = PerfectPipeline()
        results = pipeline.execute()
        summary = pipeline.get_results()
        mlflow.log_param("training_rows", summary["training_shape"][0])
        mlflow.log_param("feature_count", summary["training_shape"][1])
        mlflow.log_param("target_size", summary["target_shape"])
        mlflow.log_dict(
            {"features": list(pipeline.X.columns)},
            "feature_names.json"
        )
        mlflow.log_param("xgb_weight", results["weights"][0])
        mlflow.log_param("lgb_weight", results["weights"][1])
        mlflow.log_param("cat_weight", results["weights"][2])
        for metric, value in summary["metrics"].items():
            mlflow.log_metric(metric, value)
        print("TRAINING SUMMARY\n")

        print(f"Training Data Shape: {summary['training_shape']}")
        print(f"Target Shape: {summary['target_shape']}")

        print(
            f"Ensemble Weights:"
            f"XGB={summary['weights'][0]:.4f},"
            f"LGB={summary['weights'][1]:.4f},"
            f"CAT={summary['weights'][2]:.4f}"
        )

        print("\nMetrics:")
        for metric, value in summary["metrics"].items():
            print(f"  {metric.upper()}: {value:.4f}")
        print("STARTING TOURNAMENT MONTE CARLO SIMULATION")
        groups, team_features, h2h_history= load_simulation_metadata(pipeline.df)
        simulator= TournamentSimulator(model_ensemble=results["models"], weights=results["weights"],)
        simulation_results = simulator.run_monte_carlo(
            groups=groups,
            team_features=team_features,
            h2h_history=h2h_history,
            output_dir=pipeline_config.simulation_output_dir,
            n_simulations=pipeline_config.simulation_num,
            db_engine=engine,
            table_name="monte_carlo_predictions",
            if_exists="replace",
        )
        simulation_results.to_csv(pipeline_config.simulation_csv, index=False)
        mlflow.log_artifact(pipeline_config.simulation_csv)
        print("\nTop 5 Champion Contenders:")
        print(simulation_results[["team", "qf%", "sf%", "champion%"]].head())
        create_all_plots(
            simulation_results=simulation_results,
            metrics=summary["metrics"],
            y_true=pipeline.y,
            y_pred=pipeline.ensemble_pred,
            model=results["models"][0],
            feature_names=list(pipeline.X.columns),
            team_features=team_features
        )
    print("ALL PROCESSES COMPLETE")
    return results, simulation_results

if __name__ == "__main__":
    main()