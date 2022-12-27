import json
import pandas as pd
import os
import numpy as np
import math


def add_new_features(df):

    #Milestone 2 added by haooyuee
    def add_columes(df_tidy_m2):
        '''
        Add columes:
            - distanceNet
            - angleNet
            - goal (0 or 1)
            - emptyNet (0 or 1; assume NaNs are 0)
        '''
        #get_distanceNet
        rink=df_tidy_m2.groupby(['gameID', 'team', 'game_period'])['x'].sum().reset_index()
        rink['team_side']=np.where(rink['x'] >= 0, 'left', 'right')
        rink = rink.rename(columns={'x':'sum_x'})
        df = pd.merge(df_tidy_m2, rink, on=['gameID', 'team', 'game_period'],how='left').reset_index()

        leftNetCoX = -89
        rightNetCoX = 89
        df['distanceNet_or_shotDistance'] = np.where(
            df['team_side'] == 'right', 
            ((df_tidy_m2['x'] - leftNetCoX)**2 + (df_tidy_m2['y'] - 0)**2)**0.5, 
            ((df_tidy_m2['x'] - rightNetCoX)**2 + (df_tidy_m2['y'] - 0)**2)**0.5
            )

        #get_angleNet
        #df['angleNet_or_shotAngleWithSign'] = np.where(
            #df['team_side'] == "right", 
            #np.arcsin(df.y/df.distanceNet_or_shotDistance)*-180/math.pi,
            #np.arcsin(df.y/df.distanceNet_or_shotDistance)*180/math.pi
            #)
        #some zero will be show as +0.0 or -0.0, we replace its by 0
        #df['angleNet_or_shotAngleWithSign'] = df['angleNet_or_shotAngleWithSign'].replace(0,0)
        
        def calculate_shot_angle(y,distance,atk_side):
            if y==0 or distance==0:
                return 0
            if atk_side=='right':
                angle=np.arcsin(y/distance)*-180/math.pi
            else:
                angle=np.arcsin(y/distance)*180/math.pi  
            return angle
        df['angleNet_or_shotAngleWithSign'] = df.apply(lambda row: calculate_shot_angle(row['y'],row['distanceNet_or_shotDistance'],row['team_side']), axis=1)


        
        # df['emptyNet'] = df['emptyNet'].replace(np.nan,0)
        df['emptyNet']=df['emptyNet'] .replace('', np.nan, regex=True)
        df['emptyNet'] = df['emptyNet'].replace(np.nan,0)
        df['emptyNet'] = df['emptyNet'].replace(True,1)
        df['emptyNet'] = df['emptyNet'].replace(False,0)

        #goal = 0 or 1
        df['goal'] = df['goal'].replace(True,1)
        df['goal'] = df['goal'].replace(False,0)
        return df
        
# Milestone 2 added by Myyank
    def add_shot_angle(df):

        def calculate_shot_angle(x,y,atk_side):
            if x is None or y is None:
                return 0
            if y==0:
                return 0
            if atk_side=='right':
                angle=np.arctan(np.abs(y) / abs(x+89))
            else:
                angle = np.arctan(np.abs(y) / abs(x-89))   
            return np.rad2deg(angle)
        df['shot_angle_absolute'] = df.apply(lambda row: calculate_shot_angle(row['x'],row['y'],row['team_side']), axis=1)
        return df
        
    df=add_columes(df)
    df=add_shot_angle(df)
    
    
    
    # Milestone 2 added by Yi Cong Li
    def add_change_shot_angle(df):
        #last shot angle for calculaiton of change in angle of rebound shots
        df['last_shot_angle'] = df['shot_angle_absolute'].shift()
        def calculate_change_shot_angle(rebound,y1,y2,shot_angle1, shot_angle2):
            if not rebound:
                return 0
            if y1 is None or y2 is None or shot_angle1 is None or shot_angle2 is None:
                return 0
            if y1 * y2 >= 0:
                return np.abs(shot_angle1 - shot_angle2)
            else:
                return 180 - shot_angle1 - shot_angle2
        
        df['change_in_shot_angle'] = df.apply(lambda row: calculate_change_shot_angle(row['rebound'],row['last_y'],row['y'],row['last_shot_angle'], row['shot_angle_absolute']), axis=1)
        df = df.drop(['last_shot_angle'], axis = 1)
        return df

    df=add_change_shot_angle(df)
    return df


#Tidy data for one single game, hepler function of tidy_data
def tidy_one_game_data(raw_data: dict):
    if 'liveData' not in raw_data:
        return None
    
    df = pd.DataFrame(columns=['gameID_eventID', 'game_period', 'dateTime', 'gameID', 'team', 'goal', 'x', 'y', 'shooter', 'goalie', 'shotType', 'emptyNet', 'strength', 'gameType','home','away', 'season','last_event','last_x','last_y','game_seconds','time_from_last_event','distance_from_last_event','rebound','speed','time_since_powerplay_started','nbFriendly_non_goalie_skaters','nbOpposing_non_goalie_skaters'])
    types = ['Shot', 'Goal']
    gameID = raw_data['gamePk']
    gameType = raw_data['gameData']['game']['type']
    home = raw_data['gameData']['teams']['home']['name']
    away = raw_data['gameData']['teams']['away']['name']
    season = raw_data['gameData']['game']['season']
    
    penalties_index = raw_data['liveData']['plays']['penaltyPlays']
    minorPenaltyTime1 = []
    minorPenaltyTime2 = []
    doubleMinorPenaltyTime1 = []
    doubleMinorPenaltyTime2 = []
    majorPenaltyTime1 = []
    majorPenaltyTime2 = []
    reservedPenalty1 = []
    reservedPenalty2 = []
    nbPlayerDown1 = 0
    nbPlayerDown2 = 0
    team1 = home
    team2 = away
    powerPlayTime = 0
    i = 0
    #For each play, 
    for index,play in enumerate(raw_data['liveData']['plays']['allPlays']):
        about = play['about']
        period = about['period']
        period_time = about['periodTime']
        #remove finished penalty and serve reserved penalty
        #for team 1
        gamePlayTime = (period-1)*20+(int(period_time.split(':')[0])*60)+int(period_time.split(':')[1])
        if minorPenaltyTime1 or doubleMinorPenaltyTime1 or majorPenaltyTime1:
            for ls in [minorPenaltyTime1, doubleMinorPenaltyTime1, majorPenaltyTime1]:
                if ls and ls[-1] <= gamePlayTime:
                    ls.pop()
                    if ls != doubleMinorPenaltyTime1:
                        nbPlayerDown1 -= 1
                        if reservedPenalty1:
                            r = reservedPenalty1.pop()
                            if r == 0:
                                penaltyTime = gamePlayTime + 2 * 60
                                minorPenaltyTime1.insert(0, penaltyTime)
                                nbPlayerDown1 += 1
                            if r == 1:
                                penaltyTime = gamePlayTime + 2 * 60
                                doubleMinorPenaltyTime1.insert(0, penaltyTime)
                                penaltyTime += 2 * 60
                                doubleMinorPenaltyTime1.insert(0, penaltyTime)
                                nbPlayerDown1 += 1
                            if r == 2:
                                penaltyTime = gamePlayTime + 5 * 60
                                majorPenaltyTime1.insert(0, penaltyTime)
                                nbPlayerDown1 += 1
                    elif len(doubleMinorPenaltyTime1) % 2 == 0:
                        nbPlayerDown1 -= 1
                        if reservedPenalty1:
                            r = reservedPenalty1.pop()
                            if r == 0:
                                penaltyTime = gamePlayTime + 2 * 60
                                minorPenaltyTime1.insert(0, penaltyTime)
                                nbPlayerDown1 += 1
                            if r == 1:
                                penaltyTime = gamePlayTime + 2 * 60
                                doubleMinorPenaltyTime1.insert(0, penaltyTime)
                                penaltyTime += 2 * 60
                                doubleMinorPenaltyTime1.insert(0, penaltyTime)
                                nbPlayerDown1 += 1
                            if r == 2:
                                penaltyTime = gamePlayTime + 5 * 60
                                majorPenaltyTime1.insert(0, penaltyTime)
                                nbPlayerDown1 += 1
        #for team 2                        
        if minorPenaltyTime2 or doubleMinorPenaltyTime2 or majorPenaltyTime2:
            for ls in [minorPenaltyTime2, doubleMinorPenaltyTime2, majorPenaltyTime2]:
                if ls and ls[-1] <= gamePlayTime:
                    ls.pop()
                    if ls != doubleMinorPenaltyTime2:
                        nbPlayerDown2 -= 1
                        if reservedPenalty2:
                            r = reservedPenalty2.pop()
                            if r == 0:
                                penaltyTime = gamePlayTime + 2 * 60
                                minorPenaltyTime2.insert(0, penaltyTime)
                                nbPlayerDown2 += 1
                            if r == 1:
                                penaltyTime = gamePlayTime + 2 * 60
                                doubleMinorPenaltyTime2.insert(0, penaltyTime)
                                penaltyTime += 2 * 60
                                doubleMinorPenaltyTime2.insert(0, penaltyTime)
                                nbPlayerDown2 += 1
                            if r == 2:
                                penaltyTime = gamePlayTime + 5 * 60
                                majorPenaltyTime2.insert(0, penaltyTime)
                                nbPlayerDown2 += 1
                    elif len(doubleMinorPenaltyTime2) % 2 == 0:
                        nbPlayerDown2 -= 1
                        if reservedPenalty2:
                            r = reservedPenalty2.pop()
                            if r == 0:
                                penaltyTime = gamePlayTime + 2 * 60
                                minorPenaltyTime2.insert(0, penaltyTime)
                                nbPlayerDown2 += 1
                            if r == 1:
                                penaltyTime = gamePlayTime + 2 * 60
                                doubleMinorPenaltyTime2.insert(0, penaltyTime)
                                penaltyTime += 2 * 60
                                doubleMinorPenaltyTime2.insert(0, penaltyTime)
                                nbPlayerDown2 += 1
                            if r == 2:
                                penaltyTime = gamePlayTime + 5 * 60
                                majorPenaltyTime2.insert(0, penaltyTime)
                                nbPlayerDown2 += 1
                                
        #manage newly served penalty
        if play['about']['eventIdx'] in penalties_index and play['result']['event'] == "Penalty":
            penalty_minutes = play['result']['penaltyMinutes']
            penaltyTime = gamePlayTime + penalty_minutes * 60
            if play['team']['name'] == team1:
                if nbPlayerDown1 < 2:
                    nbPlayerDown1 += 1
                    if penalty_minutes < 4:
                        minorPenaltyTime1.insert(0,penaltyTime)
                    elif penalty_minutes == 4:
                        doubleMinorPenaltyTime1.insert(0,penaltyTime-120)
                        doubleMinorPenaltyTime1.insert(0,penaltyTime)
                    else:
                        majorPenaltyTime1.insert(0,penaltyTime)
                else:
                    if penalty_minutes < 4:
                        reservedPenalty1.insert(0,0)
                    elif penalty_minutes == 4:
                        reservedPenalty1.insert(0,1)
                    else:
                        reservedPenalty1.insert(0,2)
            else:
                if nbPlayerDown2 < 2:
                    nbPlayerDown2 += 1
                    if penalty_minutes < 4:
                        minorPenaltyTime2.insert(0,penaltyTime)
                    elif penalty_minutes == 4:
                        doubleMinorPenaltyTime2.insert(0,penaltyTime-120)
                        doubleMinorPenaltyTime2.insert(0,penaltyTime)
                    else:
                        majorPenaltyTime2.insert(0,penaltyTime)
                else:
                    if penalty_minutes < 4:
                        reservedPenalty2.insert(0,0)
                    elif penalty_minutes == 4:
                        reservedPenalty2.insert(0,1)
                    else:
                        reservedPenalty2.insert(0,2)
        
        #manage and verify power-play
        if nbPlayerDown1 != nbPlayerDown2 and powerPlayTime == 0:
            powerPlayTime = gamePlayTime
        if nbPlayerDown1 == nbPlayerDown2 and powerPlayTime != 0:
            powerPlayTime = 0
        
        #if event is type of 'Shot' or 'Goal', acquire the features needed    
        if play['result']['event'] in types:
            gameID_eventID = str(gameID)+'_'+str(about['eventId'])
            dateTime = about['dateTime']
            team = play['team']['name']
            goal = False
            shooter = ''
            goalie = ''
            emptyNet = ''
            strength = ''
            
            if play['result']['event'] == 'Goal':
                
                #release penalized players if power-play
                if nbPlayerDown1 != nbPlayerDown2:
                    if team == team1:
                        if minorPenaltyTime2 and doubleMinorPenaltyTime2:
                            if minorPenaltyTime2[-1] <= doubleMinorPenaltyTime2[-1]:
                                minorPenaltyTime2.pop()
                                nbPlayerDown2 -= 1
                            else:
                                doubleMinorPenaltyTime2.pop()
                                if len(doubleMinorPenaltyTime2) % 2 == 0:
                                    nbPlayerDown2 -= 1
                    if team == team2:
                        if minorPenaltyTime1 and doubleMinorPenaltyTime1:
                            if minorPenaltyTime1[-1] <= doubleMinorPenaltyTime1[-1]:
                                minorPenaltyTime1.pop()
                                nbPlayerDown1 -= 1
                            else:
                                doubleMinorPenaltyTime1.pop()
                                if len(doubleMinorPenaltyTime1) % 2 == 0:
                                    nbPlayerDown1 -= 1
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

            # Milestone2 added by myyank
            # Game seconds

            period_time = about['periodTime']
            game_time= (period-1)*20+(int(period_time.split(':')[0])*60)+int(period_time.split(':')[1])
            # Last event type
            prev = raw_data['liveData']['plays']['allPlays'][index - 1]
            last_event=prev['result']['event'] 
            if index==0:
                last_event=''

            # Coordinates of the last event (x, y, separate columns)
            last_x= prev['coordinates'].get('x', None)
            last_y = prev['coordinates'].get('y', None)

            #Time from the last event (seconds)

            last_about=prev['about']
            last_period=prev['about']['period']
            last_period_time=last_about['periodTime']
            prev_game_time=(last_period-1)*20+(int(last_period_time.split(':')[0])*60)+int(last_period_time.split(':')[1])
            time_from_last_event = gamePlayTime - prev_game_time

            # Distance from the last event
            if x is not None and y is not None and last_x is not None and last_y is not None:
                distance_from_last_event = np.linalg.norm(np.array([x, y]) - np.array([last_x,last_y]))      
            else:
                 distance_from_last_event=None    
            # Rebound
            if last_event=='Shot' and play['result']['event']=='Shot':
                rebound=True
            else:
                rebound=False

            #speed 
            if distance_from_last_event is not None and game_time-prev_game_time !=0:
                speed= distance_from_last_event/(game_time-prev_game_time)
            else:
                speed=None   
                
            #time since start of power-play
            time_of_powerplay = gamePlayTime - powerPlayTime
            if powerPlayTime == 0:
                time_of_powerplay = 0
            
            #number of skaters of each team on the ice
            if team == team1:
                friendly_skaters = 5 - nbPlayerDown1
                opposing_skaters = 5 - nbPlayerDown2
            else:
                friendly_skaters = 5 - nbPlayerDown2
                opposing_skaters = 5 - nbPlayerDown1
                
            df.loc[i] = [gameID_eventID, period, dateTime, gameID, team, goal, x, y, shooter, goalie, shotType, emptyNet, strength, gameType,home,away, season,last_event,last_x,last_y,game_time,time_from_last_event,distance_from_last_event,rebound,speed,time_of_powerplay, friendly_skaters, opposing_skaters]
            i += 1
    
    df.dropna(axis=0, subset= ['x', 'y'], inplace=True)
    # df = add_new_features(df)
    # df = df.drop(['sum_x'], axis=1)
    return df

#Read all JSON files inside the dir_path (nested or not), return a dataframe containing wanted features
#from the dataset formed by these JSON files.
def tidy_data(dir_path: str) -> pd.DataFrame:
    df = pd.DataFrame()
    init = True
    
    #if the path is not a directory path
    if dir_path.endswith('.json'):
        with open(dir_path, 'r') as file:
            data = file.read()
        raw_data = json.loads(data)
        df = tidy_one_game_data(raw_data)
        df = add_new_features(df)
        df = df.drop(['sum_x'], axis=1)
        return df
                
    for dir, subdirs, files in os.walk(dir_path):
           for name in files:
                if name[0] == '.': 
                    continue
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
                        
    df = add_new_features(df)
    df = df.drop(['sum_x'], axis=1)
    return df



#Milestone 2 added by haooyuee
 
def split_data(df):
    '''
    split dataset and testset:
        dataset: 2015/16-2018/19 regular season data
        testset: all of the 2019/20 season data
    '''
    df_dataset = df[(df['season'] != '20192020') & (df['gameType'] == 'R')]
    df_testset = df[df['season'] == '20192020']
    #use the 2015/16 - 2018/19 regular season data to create your training and validation sets
    df_dataset.to_csv('df_dataset.csv',index=False)
    df_testset.to_csv('df_testset.csv',index=False)
    print('dataset saved as <df_dataset.csv>')
    print('df_testset saved as <df_testset.csv>')
    return df_dataset, df_testset



#df_tidy = tidy_data('data')
#df_tidy=add_new_features(df_tidy)
# print(df_tidy)
# df_tidy.to_csv('tidy_data/complete_dataset.csv')
# print(df_tidy[df_tidy['gameID']=='2015030111'])