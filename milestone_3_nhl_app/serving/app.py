"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import sklearn
import pandas as pd
import joblib
import pickle
from xgboost import XGBClassifier
from comet_ml.api import API


import ift6758


LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")


app = Flask(__name__)

model = None
curr_model = None
COMET_API_KEY = None
COMET_API_KEY = os.environ.get("COMET_API_KEY")

@app.before_first_request
def before_first_request():
    """
    Hook to handle any initialization before the first request (e.g. load model,
    setup logging handler, etc.)
    """
    global COMET_API_KEY
    
    # TODO: setup basic logging configuration
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    app.logger.info("Before first request...")
    
    #with open('../COMET_API_KEY.txt', 'r') as f:
    #    COMET_API_KEY = f.read()

    # TODO: any other initialization before the first request (e.g. load default model)
    if os.path.isfile('xgb_best.sav'):
        model = pickle.load(open('xgb_best.sav','rb'))
        app.logger.info('Model loaded!')
    else:
        api = API(str(COMET_API_KEY))
        api.download_registry_model("ift6758-22-team2", "xgb-best-final", "1.0.0")
        model = pickle.load(open('xgb_best.sav','rb'))
        app.logger.info('Model loaded!')



@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    # TODO: read the log file specified and return the data
    # raise NotImplementedError("TODO: implement this endpoint")
    
    file = open('flask.log', 'r')
    response = file.read().splitlines()
    file.close()
    
    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The comet API key should be retrieved from the ${COMET_API_KEY} environment variable.

    Recommend (but not required) json with the schema:

        {
            workspace: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    global model
    global curr_model
    global COMET_API_KEY
    
    
    # Get POST json data
    json = request.get_json()
    app.logger.info(json)
    
    #with open('../COMET_API_KEY.txt', 'r') as file:
    #    COMET_API_KEY = file.read().rstrip()
    
    json = request.get_json()
    app.logger.info(json)
    curr_model = json['model']
    if json['model'] == "xgb-best-final":
        model_name = "xgb_best.sav"
    else:
        model_name = "logreg_dist_angle.sav"
    app.logger.info(model_name)

    # TODO: check to see if the model you are querying for is already downloaded

    # TODO: if yes, load that model and write to the log about the model change.  
    # eg: app.logger.info(<LOG STRING>)
    
    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model

    # Tip: you can implement a "CometMLClient" similar to your App client to abstract all of this
    # logic and querying of the CometML servers away to keep it clean here

    if curr_model == "xgb-best-final":
        if(os.path.isfile('xgb_best.sav')):
            model = pickle.load(open('xgb_best.sav','rb'))
            app.logger.info("Model present!")
        else:
            app.logger.info("Model not present! Downloading model...")
            api = API(str(COMET_API_KEY))
            api.download_registry_model(json['workspace'], json['model'], json['version'],output_path="./", expand=True)
            model = pickle.load(open('xgb_best.sav','rb'))

    else:
        if(os.path.isfile(model_name)):
            model = pickle.load(open(model_name, 'rb')) 
            app.logger.info(model_name)
            app.logger.info("Model present!")
        else:
            app.logger.info("Model not present! Downloading model...")
            api = API(str(COMET_API_KEY))
            api.download_registry_model(json['workspace'], json['model'], json['version'],output_path="./", expand=True)
            model = pickle.load(open(model_name, 'rb')) 

    response = 'SUCCESS: '+ model_name + ' is loaded!'

    app.logger.info(response)
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # app.logger.info('Heloooooooooo!!!!!!')
    global curr_model

    # Get POST json data
    json = request.get_json()
    app.logger.info(json)
    
    
    if curr_model == 'xgb-best-final':
        X = json['X_xgb']
    else:
        X = json['X_logreg']
    
    data = pd.DataFrame(X)
    response = pd.Series(model.predict_proba(data)[::,1])
    # print('11111')

    # TODO:
    # data = pd.DataFrame(json)
    # print('2222222')
    
    # print('3333')
    app.logger.info(response)
    return response.to_json()  # response must be json serializable!
