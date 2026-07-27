import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
OUTPUT_DIR = "outputs"


def create_output_folder():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def plot_champion_probability(results):
    top = results.sort_values("champion%",ascending=False).head(15)
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=top,
        x="team",
        y="champion%"
    )
    plt.title("World Cup Champion Probability - Monte Carlo Simulation",fontsize=16)
    plt.ylabel("Probability (%)")
    plt.xlabel("")
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/champion_probability.png",
        dpi=300
    )
    plt.close()

def plot_survival_curves(results):

    stages= [
        "group_stage%",
        "r32%",
        "r16%",
        "qf%",
        "sf%",
        "champion%"
    ]
    plt.figure(figsize=(12, 7))
    top= results.sort_values("champion%",ascending=False).head(10)


    for _, row in top.iterrows():
        plt.plot(
            stages,
            row[stages],
            marker="o",
            linewidth=2,
            label=row["team"]
        )
    plt.title("Tournament Survival Probability Curves",fontsize=16)
    plt.ylabel("Probability (%)")
    plt.xlabel("Tournament Stage")
    plt.xticks(rotation=20)
    plt.grid(alpha=0.3)
    plt.legend(bbox_to_anchor=(1.05,1),loc="upper left")
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/survival_curves.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

def plot_stage_heatmap(results):
    stages= [
        "group_stage%",
        "r32%",
        "r16%",
        "qf%",
        "sf%",
        "champion%"
    ]
    data= (results.sort_values("champion%", ascending=False).head(20).set_index("team")[stages])
    plt.figure(figsize=(10,8))
    sns.heatmap(
        data,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd"
    )
    plt.title("Tournament Progression Probability Heatmap", fontsize=16)
    plt.xlabel("")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/simulation_heatmap.png",
        dpi=300
    )
    plt.close()

def plot_model_metrics(metrics):
    if all(isinstance(v, (int, float, np.number)) for v in metrics.values()):
        df= pd.DataFrame({
                "Metric": list(metrics.keys()),
                "Value": list(metrics.values())
            })

        plt.figure(figsize=(8,5))
        sns.barplot(
            data=df,
            x="Metric",
            y="Value"
        )
        plt.title("Model Evaluation Metrics")
        plt.grid(
            axis="y",
            alpha=0.3
        )
        plt.tight_layout()
        plt.savefig(
            f"{OUTPUT_DIR}/model_metrics.png",
            dpi=300
        )
        plt.close()
    else:
        df = pd.DataFrame(metrics).T
        plt.figure(figsize=(10,6))
        df.plot(
            kind="bar",
            figsize=(10,6)
        )
        plt.title(
            "Model Evaluation Metrics Comparison"
        )
        plt.ylabel("Score")
        plt.xticks(rotation=0)
        plt.grid(
            axis="y",
            alpha=0.3
        )
        plt.tight_layout()
        plt.savefig(
            f"{OUTPUT_DIR}/model_metrics.png",
            dpi=300
        )
        plt.close()

def plot_residuals(y_true, y_pred):
    residuals= y_true - y_pred
    plt.figure(figsize=(10,5))
    sns.histplot(
        residuals,
        bins=40,
        kde=True
    )
    plt.axvline(0, linestyle="--")
    plt.title("Goal Difference Prediction Residual Distribution")
    plt.xlabel("Actual - Predicted")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/residual_distribution.png",
        dpi=300
    )
    plt.close()

def plot_actual_vs_predicted(y_true, y_pred):
    plt.figure(figsize=(7,7))
    plt.scatter(
        y_true,
        y_pred,
        alpha=0.5
    )
    minimum=min(
        min(y_true),
        min(y_pred)
    )
    maximum=max(
        max(y_true),
        max(y_pred)
    )
    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        linestyle="--"
    )
    plt.xlabel("Actual Goal Difference")
    plt.ylabel("Predicted Goal Difference")
    plt.title("Actual vs Predicted Goal Difference")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/actual_vs_prediction.png",
        dpi=300
    )
    plt.close()

def plot_feature_importance(model, feature_names):

    if not hasattr(model, "feature_importances_"):
        return
    importance= pd.DataFrame({
            "feature": feature_names,
            "importance": model.feature_importances_
        })
    importance= (importance.sort_values("importance", ascending=False).head(20))
    plt.figure(figsize=(10,8))
    sns.barplot(
        data=importance,
        y="feature",
        x="importance"
    )
    plt.title("Top 20 Feature Importance")
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/feature_importance.png",
        dpi=300
    )
    plt.close()

def plot_champion_distribution(results):
    plt.figure(figsize=(12,5))
    sns.histplot(
        results["champion%"],
        bins=20,
        kde=True
    )
    plt.title("Distribution of Champion Probabilities")
    plt.xlabel("Champion Probability (%)")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/champion_distribution.png",
        dpi=300
    )
    plt.close()

def plot_model_vs_ranking(results, team_features):
    team_features_df= pd.DataFrame([
            {
                "team": team,
                **features
            }
            for team, features in team_features.items()
        ]
    )
    df= results.merge(
        team_features_df[["team", "rank"]],
        on="team",
        how="inner"
    )
    plt.figure(figsize=(9,7))
    plt.scatter(
        df["rank"],
        df["champion%"],
        s=120
    )
    for _, row in df.iterrows():
        plt.text(
            row["rank"],
            row["champion%"],
            row["team"],
            fontsize=8
        )
    plt.gca().invert_xaxis()
    plt.xlabel("FIFA Ranking (lower is better)")
    plt.ylabel("Model Champion Probability (%)")
    plt.title("Model Prediction vs FIFA Ranking")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        f"{OUTPUT_DIR}/model_vs_fifa.png",
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

def create_all_plots(
        simulation_results,
        metrics=None,
        y_true=None,
        y_pred=None,
        model=None,
        feature_names=None,
        team_features=None
):
    create_output_folder()
    plot_champion_probability(simulation_results)
    plot_survival_curves(simulation_results)
    plot_stage_heatmap(simulation_results)
    plot_champion_distribution(simulation_results)
    if team_features is not None:
        plot_model_vs_ranking(simulation_results, team_features)
    if metrics:
        plot_model_metrics(metrics)
    if y_true is not None and y_pred is not None:
        plot_residuals(y_true, y_pred)
        plot_actual_vs_predicted(y_true, y_pred)
    if model is not None and feature_names is not None:
        plot_feature_importance(model, feature_names)
