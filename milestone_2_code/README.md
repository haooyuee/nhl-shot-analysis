# IFT6758 Project Milestone 2
The `Milestone-2` of this project extracts different features using various feature engineering techniques and also builds predictive models on the NHL "play-by-play" data. Our models reach ~93% accuracy in predicting the outcome(goal/not goal) from different features obtained from the data. 

## Overview
- We extract raw play-by-play data using the different functionalities created in Milestone 1
- We create several basic features from the raw data like `shotDistance`, `shot_angle`, etc. 
- We build our baseline models using `Logistic Regression` with the features we have created
- We further create new and advanced features like `rebound`, `speed`, etc. and also bonus features like `Time since the power-play started`
- We create advanced models using XGBoost with these features and gain an accuract of ~93% val. accuracy
- We experiment with several other predictive algorithms like MLP, Random Forest, etc. for the task
- We report all our findings on [comet.ml](https://www.comet.com/ift6758-22-team2/nhl-analytics/view/new/experiments) for reproducibility.

## Steps
To reproduce the project, run the following notebooks in the given order:
- `DataAcquisition_m2.ipynb` (Acquires data from NHL API and stores them in local)
- `FeatureEngineering1.ipynb` (Adds basic features like `shotDistance`, `shot_angle`, etc.)
- `BaselineModel.ipynb` (Builds baslines using Logistic Regression)
- `tidyData.ipynb` (Adds advanced features like `rebound`, `speed`, etc.)
- `AdvancedModel.ipynb` (Builds advanced models using XGBoost + cross-validation + feature selection)
- `Q6_BestShot_Knn.ipynb` (Performs KNN algorithm on the data)
- `Q6_BestShot_Mlp_Classifier.ipynb` (Performs MLP algorithm on the data)
- `Q6_BestShot_Random_forest.ipynb` (Performs Random Forest algorithm on the data)
- `Q6_BestShot_Compare.ipynb` (Compares performance on all models)
- `Q7_Evaluate_on_testset.ipynb` (Produces final evaluation on the test data)