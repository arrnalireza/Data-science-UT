# FIFA World Cup 2026 Match Prediction & Tournament Simulation

## Overview

This project is an end-to-end machine learning pipeline for predicting FIFA World Cup 2026 matches and simulating the entire tournament using Monte Carlo simulation.

The system combines historical international football match results, FIFA rankings, squad statistics, and Elo ratings to train an ensemble of gradient boosting models. The trained models are then used to simulate thousands of tournament iterations and estimate each team's probability of reaching every stage of the competition.

The project also integrates MLflow for experiment tracking, model versioning, and artifact management.

---

## Features

- Automated data import into MySQL
- Data cleaning and preprocessing
- Feature engineering
- Time-aware cross validation (TimeSeriesSplit)
- Hyperparameter tuning using GridSearchCV
- Ensemble learning with:
  - XGBoost
  - LightGBM
  - CatBoost
- Optimized ensemble weights
- Monte Carlo World Cup simulation
- Elo rating updates during simulation
- Head-to-head statistics
- Automatic visualization generation
- MLflow experiment tracking
- Model persistence

---

## Project Structure

```
project/
│
├── data/
│   ├── raw csv files
│   ├── tournament_groups.csv
│   └── monte_carlo_predictions.csv
│
├── saved_models/
│
├── visualization.py
├── simulate.py
├── perfect_pipeline.py
├── helpers.py
├── feature_engineering.py
├── model_training.py
├── database_connection.py
├── database_loader.py
├── perfect_config.py
├── main.py
└── requirements.txt
```

---

## Machine Learning Pipeline

The training pipeline consists of:

1. Import raw datasets into MySQL
2. Load historical data
3. Data preprocessing
4. Feature engineering
5. Prepare training data
6. Hyperparameter tuning
7. Model training
8. Time-series cross validation
9. Ensemble weight optimization
10. Evaluation
11. Model saving

---

## Engineered Features

Examples of generated features include:

- FIFA Ranking
- FIFA Points
- Elo Rating
- Elo Difference
- Elo Win Probability
- Ranking Difference
- Ranking Tier
- Team Market Value
- Average Squad Age
- Last 5 Match Win Rate
- Last 5 Goal Difference
- Head-to-Head Statistics
- Home Advantage
- Days of Rest
- Match Importance
- Friendly/Tournament Indicator

---

## Models

Three gradient boosting regressors are trained independently.

- XGBoost Regressor
- LightGBM Regressor
- CatBoost Regressor

Their predictions are combined using optimized ensemble weights obtained from out-of-fold predictions.

---

## Tournament Simulation

After training, the project simulates the FIFA World Cup using Monte Carlo simulation.

Each simulation includes:

- Group Stage
- Round of 32
- Round of 16
- Quarter Finals
- Semi Finals
- Third Place Match
- Final

Team statistics such as Elo ratings and recent form are updated dynamically throughout the tournament.

The simulation is repeated thousands of times to estimate:

- Qualification probability
- Quarter-final probability
- Semi-final probability
- Final probability
- Championship probability

---

## MLflow Integration

MLflow is used to track:

- Hyperparameters
- Ensemble weights
- Evaluation metrics
- Feature list
- Trained models
- Simulation outputs

To launch the MLflow UI:

```bash
mlflow ui
```

---

## Visualizations

The project automatically generates visualizations including:

- Prediction vs Actual
- Residual Plot
- Feature Importance
- Tournament Probability Charts
- Simulation Statistics

---

## Configuration

Project settings are stored in `perfect_config.py`.

Examples include:

- Number of CV splits
- Random seed
- Monte Carlo iterations
- Elo parameters
- Database configuration
- File paths

---

## Running the Project

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure MySQL

Update the database settings inside:

```
perfect_config.py
```

### 3. Run

```bash
python main.py
```

---

## Outputs

The project generates:

- Trained models
- MLflow experiments
- Prediction metrics
- Tournament probabilities
- Simulation CSV
- Visualizations

---

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- LightGBM
- CatBoost
- SQLAlchemy
- MySQL
- MLflow
- Matplotlib

---

## License

This project is intended for educational and research purposes.