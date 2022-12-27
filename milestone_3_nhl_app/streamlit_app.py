import streamlit as st
import pandas as pd
import numpy as np
import json
from ift6758.client import serving_client
from ift6758.client import game_client

#General template for your streamlit app. 
#Feel free to experiment with layout and adding functionality!
#Just make sure that the required functionality is included as well


# Setting the app title
st.title("Hockey Visualization App")
sc = serving_client.ServingClient(ip='serving',port = 4000)
gc = game_client.Game_Client()

with st.sidebar:
    # This sidebar uses Serving Client for the model Download
    #workspace = st.text_input('Workspace', '')
    #model = st.text_input('Model', '')
    #version = st.text_input('Version', '')
    
    workspace = st.selectbox(
    "Work space",
    ("ift6758-22-team2","only one workspace")
    )
    model = st.selectbox(
    "Model",
    ("logreg-with-angle","logreg-with-distance","logreg-with-distance-and-angle",
    "mlp-classifier-final","xgb-best","xgb-best-final")
    )
    version = st.selectbox(
    "Version",
    ("1.0.0", "only one version")
    )
    if st.button('Get Model'):
        #if model changed, tracker will be cleared, so no interference of seen data between models
        with open('tracker.json', 'w') as outfile:
            data = {}
            json.dump(data, outfile)
        sc.download_registry_model(workspace=workspace,model=model,version=version)
        st.write('Model Downloaded')

def ping_game_id(game_id):
    df, live, period, timeLeft, home, away, home_score, away_score = gc.ping_game(game_id)
    with st.container():
        home_xG = 0
        away_xG = 0
        
        st.subheader("Game " + str(game_id) + ": " + str(home + " vs " + away))
        if live:
            st.write('Period ' + str(period) + ' - ' + timeLeft + ' left')
        else:
            st.write('Game already ended, total number of periods: ' + str(period))
        if len(df)!=0:
            y = sc.predict(df)
            df_y = pd.DataFrame(y.items())
            df['xG'] = df_y.iloc[:,1]
            
            home_xG = df.loc[df['home'] == df['team'],['xG']].sum()['xG']
            away_xG = df.loc[df['away'] == df['team'],['xG']].sum()['xG']
            
        
        f = open('tracker.json')
        data = json.load(f)
        if 'home_xG' in data[str(game_id)]:
            temp_home_xG = data[str(game_id)]['home_xG']
            temp_away_xG = data[str(game_id)]['away_xG']
            data[str(game_id)]['home_xG'] = temp_home_xG+home_xG 
            data[str(game_id)]['away_xG'] = temp_away_xG+away_xG
        else:
            data[str(game_id)]['home_xG'] = home_xG 
            data[str(game_id)]['away_xG'] = away_xG
        
        home_xG = data[str(game_id)]['home_xG']
        away_xG = data[str(game_id)]['away_xG']
        cols = st.columns(2)
        cols[0].metric(label=home + ' xG (actual)', value= str(home_xG) +" ("+str(home_score)+')', delta=home_score - home_xG)
        cols[1].metric(label=away + ' xG (actual)', value= str(away_xG) +" ("+str(away_score)+')', delta=away_score - away_xG)
        with open('tracker.json', 'w') as outfile:
            json.dump(data, outfile) 
        
        
        df=df.reset_index()
        df = df.drop('index', axis=1)  
        df = df.drop('level_0', axis=1)
        st.subheader("Data used for predictions (and predictions)")
        if len(df)!=0:
            st.table(df)
        else:
            st.write("We have seen all the events for",game_id)    
        
            
        
        pass
    
    
with st.container():
    # TODO: Add Game ID input
    game_id = st.text_input("specifies what game your tool will ping, eg 2021020329", '')
    if st.button('Ping game'):
        ping_game_id(game_id)    
