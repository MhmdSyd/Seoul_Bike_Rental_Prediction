# ==========================================importing libaray==================================== #
import os
import pickle
import numpy as np
import pandas as pd
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date
import warnings

# =========================================ignore function================================== #
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.realpath('__file__')))

# =======================================load the vectorizer from disk============================ #
filename = 'output/Xgb_model.pkl'
model = pickle.load(open(filename, 'rb'))


# ======================================get season from date===================================== #
def season_of_date(date_UTC):
    year = str(date_UTC.year)
    seasons = {'spring': pd.date_range(start= year +'-03-21 00:00:00', end=year + '-06-20 00:00:00'),
               'summer': pd.date_range(start= year + '-06-21 00:00:00', end= year + '-09-22 00:00:00'),
               'autumn': pd.date_range(start= year + '-09-23 00:00:00', end= year + '-12-20 00:00:00')}
    if date_UTC in seasons['spring']:
        return 'spring'
    if date_UTC in seasons['summer']:
        return 'summer'
    if date_UTC in seasons['autumn']:
        return 'autumn'
    else:
        return 'winter'

# ==========================================day_night_label===================================== #
get_label_day_night = lambda hour : 0 if (hour<7) else(1)

# ==========================================day_name of week=================================== #
get_working_day = lambda week_day: 0 if (week_day in ['Saturday', 'Sunday']) else(1)

# ===============================create one hote encode for day name=============================#
def get_week_day_list(week_day):
    day_dict = {'Friday':0, 'Monday':0, 'Saturday':0,
                'Sunday':0, 'Thursday':0, 'Tuesday':0, 'Wednesday':0}
    day_dict[week_day] = 1
    return [*day_dict.values()]

# ===============================create one hote encode for season=============================#
def get_season_list(season):
    season_dict = {'autumn':0, 'spring':0, 'summer':0, 'winter':0}
    season_dict[season] = 1
    return [*season_dict.values()]

# =======================================prediction method=====================================#
def prediction(date_value, hour, temp, humidity, wind_speed, visiabilty, solar, rain, holiday, Function_Day):
    date_value = pd.to_datetime(date_value, format="%Y-%m-%d", utc=True)
    day = date_value.day
    month = date_value.month
    week_day = date_value.day_name()
    season = season_of_date(date_value)
    label_day_night = get_label_day_night(hour)
    Working_Day = get_working_day(week_day)
    
    day_list = get_week_day_list(week_day)

    season_list = get_season_list(season)
    
    input_array = np.array([day, label_day_night, month, hour, temp, humidity,
                             wind_speed, visiabilty, solar, rain, holiday, 
                             Function_Day,Working_Day]+day_list+season_list)
    
    my_prediction = np.array([model.predict(input_array.reshape(1,-1))], dtype='int')

    return str(my_prediction[0][0])

# ===============================================Testing method======================================== #

def input_test(date_value, hour, temp, humidity, wind_speed, visiabilty, solar, rain, holiday, Function_Day):
    
    try:
        if not(all([str(type(x))!="<class 'NoneType'>" for x in [hour, temp, humidity, wind_speed, visiabilty, solar, rain]])):
            Ex = ValueError()
            Ex.strerror = "Make Sure you enter all values."
            raise Ex
            
        if not (type(hour)==int and hour in range(24)):
            Ex = ValueError()
            Ex.strerror = "Hour Value must be within 0 and 23."
            raise Ex
        if not(temp >= -20 and temp <= 50):
            Ex = ValueError()
            Ex.strerror = "Temperature Value should be in range -20 to 50."
            raise Ex
            
        if not(humidity >= 0 and humidity <= 100):
            Ex = ValueError()
            Ex.strerror = "Humidity Value should be precentage in range 0 to 100."
            raise Ex
        
        if not(wind_speed >= 0 and wind_speed <= 10):
            Ex = ValueError()
            Ex.strerror = "Wind Speed Value should be in range 0 to 10."
            raise Ex
            
        if not(visiabilty >= 0 and visiabilty <= 2000):
            Ex = ValueError()
            Ex.strerror = "Visiabilty Value should be in range 0 to 2000."
            raise Ex
        
        if not(solar >= 0 and solar <= 5):
            Ex = ValueError()
            Ex.strerror = "Solar Value should be in range 0 to 5."
            raise Ex
        
        if not(rain >= 0 and rain <= 40):
            Ex = ValueError()
            Ex.strerror = "RainFall Value should be in range 0 to 40."
            raise Ex
        try:    
            output = prediction(date_value, hour, temp, humidity, wind_speed, visiabilty, solar, rain, holiday, Function_Day)
        except:
            Ex = ValueError()
            Ex.strerror = "Model Can't predict these values."
            raise Ex
            
    except ValueError as e:
        output = e.strerror
        
    return output

# ===================================================dictionary================================== #
Holiday_dict = {'Holiday':0, 'No Holiday':1}
Holiday_option = [{'label':key, 'value':value} for key, value in Holiday_dict.items()]

Function_dict = {'No':0, 'Yes':1}
Function_option = [{'label':key, 'value':value} for key, value in Function_dict.items()]

# ================================================Text field========================================== #
def drawText():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("Predict Rental in Seoul"),
                ], style={'textAlign': 'center'}) 
            ])
        ),
    ])

# ===============================================list field========================================= #
def drawlist(label_dict,text):
    return dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label(text),
                dbc.Select(
                    id=text,
                    options=label_dict,
                    value=[*label_dict[-1].values()][-1],
                    style={'color':'#aaa',}
                ),
                html.Br(),
            ],)

        ], width=6),
    ], justify="center", align='center')

# ===================================================input field==================================== #
def drawInput(input_id, text):
    return dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label(text.split("(")[0]),
                dbc.Input(id=input_id, placeholder=text, type="number", size="md", style={'color':'#fff'}),
                html.Br()
            ]),

        ], width=6),
    ], justify="center", align='center')

# ================================================button field==================================== #
def drawButton(id_value, value):
    return html.Div([
        dbc.Button(id=id_value, children=value, color="secondary", type='submit', size='md', n_clicks=0),
        html.Br()
    ], className="d-grid gap-1 col-6 mx-auto",)

# =======================================date field========================================== #
def drawDateTime(id_value):
    return dbc.Row([
        dbc.Col([
            html.Div([
                dbc.Label("Date Picker"),
                
                html.Div([ 
                    dcc.DatePickerSingle(
                        id=id_value,
                        min_date_allowed=date(2017, 8, 5),
                        max_date_allowed=date(2022, 9, 19, ),
                        initial_visible_month=date(2021, 11, 6),
                        date=date(2021, 11, 6),
                        style={'width':'100%'}
                    )]),
                html.Br()

            ])
        ], width=6)
    ], justify="center", align='center')
   
# ============================================output=========================================== #    
def drawOutput():
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Div([
                    html.P(children="Prediction will be appear Here!",
                           id='Output',
                           style={'text-align':'center'})
                ]),
                html.Br(),
            ]),

        ], width=6),
    ], justify="center", align='center')


# ===============================================Design Dash =================================== #
external_stylesheets = [dbc.themes.SLATE]

app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                update_title='Loading...',
                title='Seoul Bike Rental'
)

server = app.server


# ====================================Start of Design================================= #
app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
# =======================================Header======================================== #
            dbc.Row([
                dbc.Col([
                    drawText()
                ], width=8)
            ], justify="center", align='center'),
            
            html.Br(),
            
# ====================================Input=========================================== #
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.Div([
                                drawDateTime('datetime'),
                                drawInput('Hour', 'Hour(24)'),
                                drawInput('Temperature', 'Temperature(°C)'),
                                drawInput('humidity', 'Humidity(%)'),
                                drawInput('wind_speed', 'Wind speed (m/s)'),
                                drawInput('visability', 'Visibility (10m)'),
                                drawInput('solar', 'Solar Radiation (MJ/m2)'),
                                drawInput('rainfall', 'Rainfall(mm)'),
                                drawlist(Holiday_option, 'Holiday'),
                                drawlist(Function_option, 'Functioning_Day'),
                                drawOutput(),
                                drawButton('Input', 'Predict')
                            ]) 
                        ])
                    ),
                ], width=8),
            ], justify="center", align='center'),

        ]), color = 'dark',
    )
])

# ===============================================Callback method=============================== #
@app.callback(
    Output('Output', 'children'),
    Input('Input', 'n_clicks'),
    State('datetime', 'date'),
    State('Hour', 'value'),
    State('Temperature', 'value'),
    State('humidity', 'value'),
    State('wind_speed', 'value'),
    State('visability', 'value'),
    State('solar', 'value'),
    State('rainfall', 'value'),
    State('Holiday', 'value'),
    State('Functioning_Day', 'value'),
    
)
# ===============================================Update Output=============================== #
def update_output(n_click,date_value, hour, temp, humidity, wind_speed, visiabilty, solar, rain, holiday, Function_Day):
    if n_click == 0:
        output  = "Prediction will be appear Here!"
    else:
        output = input_test(date_value, hour, temp, humidity, wind_speed, visiabilty, solar, rain, int(holiday), int(Function_Day))
    return output


# ==========================================Run Code========================================== #
if __name__ == '__main__':
    app.run_server(debug=True)