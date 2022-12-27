# IFT6758_Project_Milestone-1 - Team 2
This project explores and analyses the NHL "play-by-play" data. We try to find answers to different analytical questions through our analyses and also produce reproducible figures support the results. 

# Overview
- We use modular methods defined in `dataExtract.py` to extract raw data from the [NHL API](https://gitlab.com/dword4/nhlapi)
- We generate an interactive plot that helps to visualize events in a given game
- We clean the raw data in JSON format and store it in a more easily workable format - dataframes
- We use the clean data to analyse aggregate and play-by-play data and create interactive visualizations.

# Steps
To reproduce the project, run the following notebooks in the given order:
- `DataAcquisition.ipynb` (Acquires data from NHL API and stores them in local)
- `InteractiveDebuggingTool.ipynb` (Generates an interactive tool to visualize events in a game)
- `tidyData.ipynb` (Cleans the data and creates a consolidated dataframe of the games)
- `SimpleVisualizations.ipynb` (Creates simple visualizations to analyse aggregate data)
- `advancedVisualizations.ipynb` (Creates advanced interactive visualizations using Plotly)
