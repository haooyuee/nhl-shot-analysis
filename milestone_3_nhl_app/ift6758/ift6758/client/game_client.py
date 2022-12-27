import os
import math
import requests
import pandas as pd
import logging
import numpy as np
import json
import json
from tidyData import tidy_one_game_data, add_new_features

logger = logging.getLogger(__name__)

#removed if not so that tracker won't accumulate after each run of app
with open('tracker.json', 'w') as outfile:
    data = {}
    json.dump(data, outfile)


class Game_Client:
    def __init__(self):

        logger.info(f"Initializing ClientGame; base URL: ")
        
  
    
    def ping_game(self,gameId: str) -> pd.DataFrame:
        live = True
        
        #for testing live update
        #first ping game with below two lines
        #f = open('2019020001_partial.json')
        #Extract_Data = json.load(f)
        
        #Do not rerun the app
        #then comment above two lines, uncomment below two lines and ping game again, to see the difference
        #f = open('2019020001_full.json')
        #Extract_Data = json.load(f)
        
        
        #comment below two lines and uncomment above to test for live update using partial data of 201920001
        Extract_Data = requests.get("https://statsapi.web.nhl.com/api/v1/game/"+gameId+"/feed/live/")
        Extract_Data = Extract_Data.json()
        
        if 'gameData' in Extract_Data and 'datetime' in Extract_Data['gameData'] and 'endDateTime' in Extract_Data['gameData']['datetime']:
            live = False
        current = Extract_Data['liveData']['plays']['currentPlay']['about']
        period = current['period']
        timeLeft = current['periodTimeRemaining']
        home_score = current['goals']['home']
        away_score = current['goals']['away']
        df=tidy_one_game_data(Extract_Data)
        df=add_new_features(df)
        df = df.drop(['sum_x'], axis=1)
        home = df['home'].values[0]
        away = df['away'].values[0]
        
        f = open('tracker.json')
        data = json.load(f)
        old_idx=0
        if gameId in data:
            old_idx=data[str(gameId)]['idx']
            data[str(gameId)]['idx'] = len(df)
        else:
            data[str(gameId)] = {}
            data[str(gameId)]['idx'] = len(df)
        with open('tracker.json', 'w') as outfile:
            json.dump(data, outfile) 
        df = df.reset_index().drop('index', axis=1)[old_idx:]        
        # df[df['team']==df['home']],df[df['team']==df['away']] 
        return df, live, period, timeLeft, home, away, home_score, away_score

# if __name__ == "__main__":

#     Client=Game_Client()
#     df_h,df_a=Client.ping_game("2021020329")
#     print(df_h)
#     print(df_a)
