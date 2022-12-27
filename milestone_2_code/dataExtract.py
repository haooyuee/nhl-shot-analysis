from turtle import st
import requests
import json
import pandas as pd
import os


class DataExtraction:

    def is_valid_game_id(self, year, game_type, game_id):
        '''
        To check if a generated game ID is valid or not
        returns: True or False
        '''
        
        season = year + str(int(year)+1)
        #print('===+'+game_id, season) 
        ##print will cause an error in main
        return game_id in self.get_game_ids(game_type, season)


    def download_via_api(self, filepath):
        '''
        To download a specific game and saving the JSON in the given `filepath`.
        game_id is extracted from the `filepath`. Returns the extracted JSON.
        returns: dict 
        '''
        
        game_id = os.path.split(filepath)[-1][:-5]
        response_API = requests.get('https://statsapi.web.nhl.com/api/v1/game/'+str(game_id)+'/feed/live/')
        if response_API.status_code == 200:
            response = response_API.json()

            with open(filepath, "w") as outfile:
                json.dump(response, outfile, indent=4)  
            return response


    def fetch_raw_json(self, filepath):
        '''
        To fetch the raw JSON as a dictionary given a `filepath`.
        returns: dict
        '''

        out = ''
        if not os.path.exists(filepath):
            out = self.download_via_api(filepath)
        else:
            with open(filepath, 'r') as file:
                data = file.read()
            out = json.loads(data)

        return out


    def generate_filepath(self, parent_dir, year, game_type, game_id):
        '''
        To generate the filepath given the year, game_type(regular or playoff), game_id
        returns: str
        '''

        game_type = game_type.upper()
        tmp_path = os.path.join(parent_dir, year, game_type)
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        return os.path.join(parent_dir, year, game_type, game_id) + '.json' 


    def get_game_ids(self,game_type:str,season:str):
        '''
        To get a list of game IDs from the NHL API
        returns: list
        '''

        sck=requests.get('https://statsapi.web.nhl.com/api/v1/schedule?season='+season)
        myjson = sck.json()
        data=myjson
        gid_r=[]
        dic={}
        for i in data['dates']:
            for j in i['games']:
                gid=0
                for x,y in j.items():
                    if x=='gamePk':
                        gid=y
                    if x=='gameType':
                        if y==game_type:
                            gid_r.append(str(gid))
                        break
        return gid_r               
        

    def download_all_json(self,year:str,game_type:str):
        '''
        To download all the game data from 2017 - 2020 for regular and playoff matches
        '''

        gyear = year +str(int(year)+1)
        game_id=self.get_game_ids(game_type,gyear)
        path=str(year)
        if not os.path.exists(os.path.join('data', year)):
            os.makedirs(os.path.join('data', year))
        # game_type = 'regular' if game_type=='R' else 'playoffs'

        for i in range(len(game_id)):
            filepath = self.generate_filepath('data', year, game_type, game_id[i])
            self.download_via_api(filepath)


    def fetch_data(self, year, game_type, game_number):
        '''
        To fetch the data given the year, game_type(regular or playoff), game_id
        returns: raw JSON
        '''

        game_id = year + '02' + game_number if game_type == 'R' else year + '03' + game_number
        if self.is_valid_game_id( year, game_type, game_id):
            filepath = self.generate_filepath('data', year, game_type, game_id)
            #print(filepath)
            raw_data = self.fetch_raw_json(filepath)

            #print(raw_data['liveData']['linescore']['teams']['home'])
            return raw_data

    


obj=DataExtraction()
# data = obj.fetch_data('2017','R', '0101')
# print(len(data['liveData']['plays']['allPlays']))
# year_list = ['2016', '2017', '2018', '2019', '2020'] 
# season_list = ['R', 'P']
# for year in year_list:
#     for season_type in season_list: 
#         print(year, season_type)
#         obj.download_all_json(year, season_type)

obj.download_all_json('2017', 'R')
obj.download_all_json('2017', 'P')