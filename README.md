# wcestus1_prediction
My first try at timeseries forecasting. Using EAI data, attempt to predict the WCESTUS1 reserves level. This report is produced weekly (Thursday's at 8:30 a.m., Mountain.

Goal of this project is to predict using a simple, univariate LSTM model and a multivariate LSTM model. The multivariate will not only include other inventory indicators, weekly price per barrell data, but also 'outside data,' including unemployment data from the Fed (ICSA).

Early attempts of leveraging S&P numbers have been fruitless, however, considering how the markets at forward looking, this should be revisited.

The structure of this app will have a mix of notebooks and python files to retrieve data, try variations of models, and visualize.




CREDITS:
There too many to really mention, but portions of the project are modeled after:
Dr. Vytautas Bielinskas on youtube ==> https://www.youtube.com/watch?v=gSYiKKoREFI&t=320s
Jason Brownlee  ==> https://machinelearningmastery.com/how-to-develop-lstm-models-for-multi-step-time-series-forecasting-of-household-power-consumption/


