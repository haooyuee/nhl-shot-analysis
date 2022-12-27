import json
import pandas as pd
import os

#Tidy data for one single game, hepler function of tidy_data
def tidy_one_game_data(raw_data: dict):
     '''
     To extract the features wanted from one game into a pandas dataframe, helper function of tidyData
     returns: pd.DataFrame, or None if liveData doesn't exist
     '''
    
    if 'liveData' not in raw_data:
        return None
    
    df = pd.DataFrame(columns=['gameID_eventID', 'period', 'dateTime', 'gameID', 'team', 'goal', 'x', 'y', 'shooter', 'goalie', 'shotType', 'emptyNet', 'strength', 'gameType','home','away', 'season'])
    types = ['Shot', 'Goal']
    gameID = raw_data['gamePk']
    gameType = raw_data['gameData']['game']['type']
    home = raw_data['gameData']['teams']['home']['name']
    away = raw_data['gameData']['teams']['away']['name']
    season = raw_data['gameData']['game']['season']
    i = 0
    
    #For each play, if event is type of 'Shot' or 'Goal', acquire the features needed
    for play in raw_data['liveData']['plays']['allPlays']:
        if play['result']['event'] in types:
            about = play['about']
            gameID_eventID = str(gameID)+'_'+str(about['eventId'])
            period = about['period']
            dateTime = about['dateTime']
            team = play['team']['name']
            goal = False
            shooter = ''
            goalie = ''
            emptyNet = ''
            strength = ''
            
            if play['result']['event'] == 'Goal':
                goal = True
                emptyNet = play['result'].get('emptyNet', None)
                strength = play['result'].get('strength',None).get('name', None)
                for player in play['players']:
                    if player['playerType'] == 'Scorer':
                        shooter = player['player']['fullName']
                    if player['playerType'] == 'Goalie':
                        goalie =  player['player']['fullName']
            else:
                for player in play['players']:
                    if player['playerType'] == 'Shooter':
                        shooter = player['player']['fullName']
                    if player['playerType'] == 'Goalie':
                        goalie =  player['player']['fullName']
            x = play['coordinates'].get('x', None)
            y = play['coordinates'].get('y',None)
            shotType = play['result'].get('secondaryType',None)
            
            df.loc[i] = [gameID_eventID, period, dateTime, gameID, team, goal, x, y, shooter, goalie, shotType, emptyNet, strength, gameType,home,away, season]
            i += 1
            
    return df

#Read all JSON files inside the dir_path (nested or not), return a dataframe containing wanted features
#from the dataset formed by these JSON files.
def tidy_data(dir_path: str) -> pd.DataFrame:
     '''
     To extract the features wanted from all games stored in the JSON files of directory dir_path (nested or not) into a pandas dataframe
     returns: pd.DataFrame
     '''
    
    df = pd.DataFrame()
    init = True
    
    for dir, subdirs, files in os.walk(dir_path):
           for name in files:
                file_path = os.path.join(dir, name)
                with open(file_path, 'r') as file:
                    data = file.read()
                raw_data = json.loads(data)
                
                #In case if the first game has no liveData
                if init:
                    df = tidy_one_game_data(raw_data)
                    if df is not None:
                        init = False
                else:
                    new_df = tidy_one_game_data(raw_data)
                    if new_df is not None:
                        df = pd.concat([df, new_df],ignore_index=True)
    #write the dataframe to CSV so we don't have to re-run this code everytime
    df_tidy.to_csv('data/tidy.csv', index=False)                     
    return df

#df_tidy = tidy_data('data')