import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from collections import Counter
import seaborn as sn
import pickle
import os
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from tidyData import tidy_data, split_data
from sklearn.svm import LinearSVC
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
from comet_ml.api import API
from comet_ml import Experiment



def preprocess(df):
    train_val_df = df

    ## Selecting only the columns from Q4
    columns = ['game_period', 'x', 'y', 'distanceNet_or_shotDistance', 'goal', 'shot_angle_absolute', 
               'shotType', 'last_event', 'last_x', 'last_y', 'game_seconds', 'time_from_last_event', 
               'distance_from_last_event', 'rebound', 'speed', 'time_since_powerplay_started', 
               'nbFriendly_non_goalie_skaters', 'nbOpposing_non_goalie_skaters', 'change_in_shot_angle']

    data = train_val_df[columns]

    ## Proper datatype casting of columns
    cols_dtype_change = ['x', 'y', 'last_x', 'last_y', 'distance_from_last_event', 
                         'speed', 'sum_x', 'distanceNet_or_shotDistance']
    for col in cols_dtype_change:
        if col in data.columns:
            data[col] = data[col].astype('float')
        if 'game_period' in data.columns:
            data['game_period'] = data['game_period'].astype('str')
            
    # COMET_API_KEY = os.environ.get("COMET_API_KEY", None)
    
    #COMET_API_KEY = ''
    #with open('./COMET_API_KEY.txt', 'r') as file:
    #    COMET_API_KEY = file.read().rstrip()

    # experiment = Experiment(
    #     api_key=COMET_API_KEY,
    #     project_name="nhl-analytics",
    #     workspace="ift6758-22-team2", 
    # )
    COMET_API_KEY = os.environ.get("COMET_API_KEY")
    api = API(str(COMET_API_KEY))

    experiment = api.get("ift6758-22-team2/nhl-analytics/xgb_preprocess")

    experiment.download_model('xgb_preprocess', output_path="./", expand=True)
    preprocessor = pickle.load(open('pre_pipe.sav','rb'))
    
    data = preprocessor.transform(data)      
    
    return pd.DataFrame(data)


def transform(X_val):
    # Using the mask of features selected from training data
    # Check `AdvancedModel.ipynb` to verify selected features
    features = X_val.loc[::,X_val.columns!='goal'].loc[:,[False,  True,  
        True,  True,  True, False,  True,  True,  True,  True,  True,  
        True,  True,  True,  True,  True,  True,  True,  True,  True,  
        True, False,  True,  True,  True,  True,  True, True, False, 
        False, False,  True,  True, False, False, False, False, False, 
        False, False,  True,  True,  True, True,  False, False]]
    return features