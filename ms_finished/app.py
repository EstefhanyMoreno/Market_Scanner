import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import yfinance as yf
from bbma import *
from taprueba import *

df= pd.read_csv('/Users/estefhanymorenovega/Market_Scanner/ms_finished/sip.csv')
df['id'] = df['Symbol']
df.set_index('id', inplace=True, drop=False)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, prevent_initial_callbacks=True, external_stylesheets=external_stylesheets)

colors = {
    'background': 'rgb(15, 15, 15)',
    'text': '#16760C',
    'text2': '#DFEEDE'
}
#---------------------------------------------------------------------------------------------------------
# LAYOUT
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Market Scanner ®',
        style={'color': colors['text']}
    ),

    html.Div(children= '___________________________Tools for Day Trading  ', style={
        'color': colors['text'],
        'fontWeight': 'bold'}
    ),

    html.H4(children='Watchlist',style={
        'color': colors['text2']} 
    ), 

    html.Div(children= 'Selected stocks based on volatility, liquidity and market capitalization', style={
        'color': colors['text2']}
    ),
    
    dash_table.DataTable(
        id='datatable-row-ids',
        columns=[
            {'name': i, 'id': i, 'deletable': True} for i in df.columns
            # omit the id column
            if i != 'id'
        ],
        data=df.to_dict('records'),
        style_data_conditional=(
             [
  
               {
            'if': {
            'filter_query': '{Gap($)} < -1',
            'column_id': 'Gap($)',
                    },
            'fontWeight': 'bold',
            'color': 'red'
                     },
                {
            'if': {
            'filter_query': '{Gap($)} >1',
            'column_id': 'Gap($)',
                    },
                     #'backgroundColor': 'hotpink',
            'fontWeight': 'bold',
            'color': 'green'
                     },
                {
                    'if': {
                        'column_type': 'text'
                    },
                    'textAlign': 'left'
                },

                # Format active cells *********************************
                {
                    'if': {
                        'state': 'active'  # 'active' | 'selected'
                    },
                    'border': '3px solid rgb(0, 116, 217)'
                },
                ]),

        sort_action="native",       # enables data to be sorted per-column by user or not ('none')
        column_selectable="multi",  # allow users to select 'multi' or 'single' columns
        #row_selectable="single",     # allow users to select 'multi' or 'single' rows
        #selected_columns=[],        # ids of columns that user selects
        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto',
            'color': '#44494D',
            'backgroundColor': 'rgb(15, 15, 15)',
            #'fontWeight': 'bold',
            'fontFamily': 'Arial'
        },
        style_header={
        'backgroundColor': 'rgb(72, 85, 126)',
        'fontWeight': 'bold',
        'fontSize': 16,
        'fontFamily': 'Arial',
        'textAlign': 'center'
        }),
    
    html.H4(children='Live price evolution',style={
        'color': colors['text2']} 
    ),

    html.Div(children= 'Candlestick chart, Volume, Moving Avarage and Bollinger Bands', style={
        'color': colors['text2']}
    ),

    dcc.Interval(
    	id='my_interval',
                n_intervals=0,       # number of times the interval was activated
                interval=60*1000,   # update every 2 minutes
    ),
    dcc.Graph(id="world_finance"),
    #html.Div(id='candlestick_container'),
    html.H4(children='Technical Analysis',style={
        'color': colors['text2']} 
    ),
    html.Div(children= 'Recommendations based on Technical Analysis', style={
        'color': colors['text2']}
    ),
    dcc.Markdown(children= '''**SMA**: The Simple Moving Average is technical analysis tool
     that smooths out price data by creating a constantly updated average price. ''',
        style={
        'color': colors['text2']}
    ),
     dcc.Markdown(children= '''**Stoch**: Stochastics is a momentum indicator. The premise of stochastics is that when a stock trends upwards,
      its closing price tends to trade at the high end of the day's range or price action. ''',
        style={
        'color': colors['text2']}
    ),
    dcc.Markdown(children= '''**RSI**:The Relative Strength Index is a momentum indicator that measures the magnitude of recent price changes
     to evaluate overbought or oversold conditions in the price of a stock.''',
        style={
        'color': colors['text2']}
    ),
    html.Div(id='table-container')
     ])
#---------------------------------------------------------------------------------------------------------
#CALLBACKS
@app.callback(
    Output(component_id='world_finance', component_property='figure'),
    [Input(component_id='datatable-row-ids', component_property='active_cell'),
     Input(component_id='my_interval', component_property='n_intervals')
    ])

def live_candlestick(ticker, n):
    df1 = yf.download(tickers= ticker['row_id'], period='1d', interval='1m')
    #Interval required 1 minute
    t= ticker['row_id'] #symbol

#Graph
    INCREASING_COLOR = '#54CC23'
    DECREASING_COLOR = '#E43A15'
    data = [ dict(
    type = 'candlestick',
    open = df1.Open,
    high = df1.High,
    low = df1.Low,
    close = df1.Close,
    x = df1.index,
    yaxis = 'y2',
    name = f'{t}',
    increasing = dict( line = dict( color = INCREASING_COLOR ) ),
    decreasing = dict( line = dict( color = DECREASING_COLOR ) ),
) ]
    
    layout=dict()
    fig = dict( data=data, layout=layout )
    fig['layout'] = dict()
    fig['layout']['plot_bgcolor'] = 'rgb(15, 15, 15)'
    fig['layout']['paper_bgcolor'] = 'rgb(15, 15, 15)'
    fig['layout']['xaxis'] = dict( rangeselector = dict( visible = True ) )
    fig['layout']['yaxis'] = dict( domain = [0, 0.2], showticklabels = False )
    fig['layout']['yaxis2'] = dict( domain = [0.2, 0.8] )
    fig['layout']['legend'] = dict( orientation = 'h', y=0.9, x=0.3, yanchor='bottom' )
    fig['layout']['margin'] = dict( t=40, b=40, r=40, l=40 )
    fig['layout']['title'] = f'{t} live share price evolution'
  

    rangeselector=dict(
    visibe = True,
    x = 0, y = 0.9,
    bgcolor = 'rgba(150, 200, 250, 0.4)',
    font = dict( size = 13 ),
    buttons=list([
            dict(count=15, label="15m", step="minute", stepmode="backward"),
            dict(count=45, label="45m", step="minute", stepmode="backward"),
            dict(count=1, label="HTD", step="hour", stepmode="todate"),
            dict(count=3, label="3h", step="hour", stepmode="backward"),
            dict(step="all")
                ])
           )
    
    fig['layout']['xaxis']['rangeselector'] = rangeselector
        
        #Moving average
    mv_y = movingaverage(df1.Close)
    mv_x = list(df1.index)

        # Clip the ends
    mv_x = mv_x[5:-5]
    mv_y = mv_y[5:-5]

    fig['data'].append( dict( x=mv_x, y=mv_y, type='scatter', mode='lines', 
                         line = dict( width = 1 ),
                         marker = dict( color = '#558dc2' ),
                         yaxis = 'y2', name='Moving Average' ) )
        
    colors = []

    for i in range(len(df1.Close)):
        if i != 0:
            if df1.Close[i] > df1.Close[i-1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
            
        
    fig['data'].append( dict( x=df1.index, y=df1.Volume,                         
                         marker=dict( color=colors ),
                         type='bar', yaxis='y', name='Volume' ) )
        
        #Bollinger bands
    bb_avg, bb_upper, bb_lower = bbands(df1.Close)

    fig['data'].append( dict( x=df1.index, y=bb_upper, type='scatter', yaxis='y2', 
                         line = dict( width = 1 ),
                         marker=dict(color='#ccc'), hoverinfo='none', 
                         legendgroup='Bollinger Bands', name='Bollinger Bands') )

    fig['data'].append( dict( x=df1.index, y=bb_lower, type='scatter', yaxis='y2',
                         line = dict( width = 1 ),
                         marker=dict(color='#ccc'), hoverinfo='none',
                         legendgroup='Bollinger Bands', showlegend=False ) )

#Show
    return (fig)

@app.callback(
    Output(component_id='table-container', component_property='children'),
    [Input(component_id='datatable-row-ids', component_property='active_cell'),
     Input(component_id='my_interval', component_property='n_intervals')
    ])

def ta_table(ticker, n):
	df2= TA(ticker['row_id'])
	return [
        dash_table.DataTable(
        	id= 'strategy-ticker',
        	columns=[
            {'name': i, 'id': i, 'deletable': True} for i in df2.columns
            # omit the id column
            if i != 'id'
        ],
            data=df2.to_dict('records'),
            style_data_conditional=(
              [
  
                {
             'if': {
             'filter_query': '{SMA} = BUY',
             'column_id': 'SMA',
                     },
             'fontWeight': 'bold',
             'color': 'white',
             'backgroundColor': 'green',
             'textAlign':'center'
                      },

                  {
             'if': {
             'filter_query': '{Stoch} = BUY',
             'column_id': 'Stoch',
                     },
             'fontWeight': 'bold',
             'color': 'white',
             'backgroundColor': 'green',
             'textAlign':'center'
                      },

                 {
             'if': {
             'filter_query': '{RSI} = BUY',
             'column_id': 'RSI',
                     },
             'fontWeight': 'bold',
             'color': 'white',
             'backgroundColor': 'green',
             'textAlign':'center'
                      },

                   {
             'if': {
             'filter_query': '{SMA} = SELL',
             'column_id': 'SMA',
                     },
             'fontWeight': 'bold',
             'color': 'white',
             'backgroundColor': 'red',
             'textAlign':'center'
                      },

                  {
             'if': {
             'filter_query': '{Stoch} = SELL',
             'column_id': 'Stoch',
                     },
             'fontWeight': 'bold',
             'color': 'white',
             'backgroundColor': 'red',
             'textAlign':'center'
                      },

                 {
             'if': {
             'filter_query': '{RSI} = SELL',
             'column_id': 'RSI',
                     },
             'fontWeight': 'bold',
             'color': 'white',
             'backgroundColor': 'red',
             'textAlign':'center'
                      },
            ]),

        style_cell={                # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95 , 'padding': '5px'
        },
        style_as_list_view=True,
        style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto',
            'color': '#44494D',
            'backgroundColor': 'rgb(15, 15, 15)',
            #'fontWeight': 'bold',
            'fontFamily': 'Arial'
        },
        style_header={
        'backgroundColor': 'rgb(72, 85, 126)',
        'fontWeight': 'bold',
        'fontSize': 18,
        'fontFamily': 'Arial',
        'textAlign': 'center'
        }
           
        )
    ]

#---------------------------------------------------------------------------------------------------------  
if __name__ == '__main__':
    app.run_server(debug=True)