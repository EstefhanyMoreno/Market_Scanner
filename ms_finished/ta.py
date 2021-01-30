import pandas as pd
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import talib as ta
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")


def SMA(close,sPeriod,lPeriod):
    shortSMA = ta.SMA(close,sPeriod)
    longSMA = ta.SMA(close,lPeriod)
    smaSell = ((shortSMA <= longSMA) & (shortSMA.shift(1) >= longSMA.shift(1)))
    smaBuy = ((shortSMA >= longSMA) & (shortSMA.shift(1) <= longSMA.shift(1)))

    return smaSell,smaBuy,shortSMA,longSMA
def RSI(close,timePeriod): 
    rsi = ta.RSI(close,timePeriod)
    rsiSell = (rsi>70) & (rsi.shift(1)<=70)
    rsiBuy = (rsi<30) & (rsi.shift(1)>=30)
    return rsiSell,rsiBuy, rsi
def Stoch(close,high,low):
    slowk, slowd = ta.STOCH(high, low, close)
    stochSell = ((slowk < slowd) & (slowk.shift(1) > slowd.shift(1))) & (slowd > 80)
    stochBuy = ((slowk > slowd) & (slowk.shift(1) < slowd.shift(1))) & (slowd < 20)
    return stochSell,stochBuy, slowk,slowd

def runAllTA(data):
    
    price = data['Close']
    high = data['High']
    low = data['Low']
    shortPeriod= 14   
    longPeriod=200
    # Simple Moving Average calcs
    smaSell,smaBuy,shortSMA,longSMA = SMA(price,shortPeriod,longPeriod)
    # Do the RSI calcs
    rsiSell,rsiBuy,rsi = RSI(price,shortPeriod)
    # and now the stochastics 
    stochSell,stochBuy,slowk,slowd = Stoch(price, high, low)    

    # Now collect buy and sell Signal timestamps into a single df
    sigTimeStamps = pd.concat([smaSell, smaBuy, stochSell, stochBuy, rsiSell, rsiBuy],axis=1)
    sigTimeStamps.columns=['SMA Sell','SMA Buy','Stoch Sell','Stoch Buy','RSI Sell','RSI Buy']
    signals = sigTimeStamps.loc[sigTimeStamps['SMA Sell'] | sigTimeStamps['Stoch Sell'] |
                         sigTimeStamps['RSI Sell'] | sigTimeStamps['SMA Buy'] | 
                         sigTimeStamps['Stoch Buy'] | sigTimeStamps['RSI Buy']]
    
    # Compare final signal Timestamp with latest data TimeStamp
    if (data.index[-1]==signals.index[-1]):
        final = signals.iloc[-1]
        # filter out the signals set to True and send to ChatBot
        #signal = final.loc[final]
        #signalTime = signal.name.strftime("%Y-%m-%dT%H:%M:%S")
        #indicators = signal.loc[signal].index
        #sendSignaltoChatBot(myRIC, signalTime, indicators)
    signals['Price']= data['Close']
    return signals

def TA(ticker):
    data= yf.download(tickers= ticker, period='1d', interval='1m')
    df=runAllTA(data)
    df['SMA']=''
    df['Stoch']=''
    df['RSI']=''
    for i in range(len(df)):
        if df['SMA Sell'][i]== True:
            df['SMA'][i]='SELL'
        elif df['SMA Buy'][i]== True:
            df['SMA'][i]='BUY'
        else:
            df['SMA'][i]='...'
    for i in range(len(df)):
        if df['Stoch Sell'][i]== True:
            df['Stoch'][i]='SELL'
        elif df['Stoch Buy'][i]== True:
            df['Stoch'][i]='BUY'
        else:
            df['Stoch'][i]='...'
    for i in range(len(df)):
        if df['RSI Sell'][i]== True:
            df['RSI'][i]='SELL'
        elif df['RSI Buy'][i]== True:
            df['RSI'][i]='BUY'
        else:
            df['RSI'][i]='...'
    df.drop(['SMA Sell', 'SMA Buy', 'Stoch Sell', 'Stoch Buy', 'RSI Sell', 'RSI Buy'],
     axis=1, inplace= True)
    df=df.sort_values(by= 'Datetime', ascending= False)
    print(df)
    return df

