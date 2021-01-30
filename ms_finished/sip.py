import warnings
warnings.filterwarnings("ignore")
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import talib as ta
import time

def KM_TO0(string):
    if 'K' in string:
        num=float(string.replace('K', ''))*1000
    else:
        num=float(string.replace('M', ''))*1000000
    return num

def stocks_in_play():
    url ='https://www.marketwatch.com/tools/screener/premarket'
    req = requests.get(url)
    print(req)
    sopa = BeautifulSoup(req.content, 'html.parser')
    
    #Web scraping headings
    div=sopa.find_all('div',{'class':'group group--elements'})
    headings= div[0].find_all('th',{'class':'table__heading'})
    headings_clean= [i.text for i in headings]
    #Web scraping table
    values= div[0].find_all('td',{'class':'table__cell'})
    values_text=[i.text for i in values]
    values_clean= [i.replace('\n', '') for i in values_text]
    values2= div[1].find_all('td',{'class':'table__cell'})
    values2_text=[i.text for i in values2]
    values2_clean= [i.replace('\n', '') for i in values2_text]
    values3= div[2].find_all('td',{'class':'table__cell'})
    values3_text=[i.text for i in values3]
    values3_clean= [i.replace('\n', '') for i in values3_text]
    #Dividing the info to put it in a df
    data= values_clean +values2_clean +values3_clean 
    chunks = [data[x:x+6] for x in range(0, len(data), 6)]
    #Df creation
    df= pd.DataFrame(data= chunks, columns= headings_clean)
    #Data cleaning and transformation
    df['PremarketPrice']= [i.replace(',', '') for i in df['PremarketPrice'] ]
    df['PremarketPrice']= [float(i.replace('$', '')) for i in df['PremarketPrice'] ]
    df['PremarketVol']=[i.replace(',', '') for i in df['PremarketVol']]
    df['PremarketVol']= df['PremarketVol'].apply(KM_TO0) #Function to create 0
    df['PremarketChg']=df['PremarketChg'].astype('float')
    df['PremarketChg %']=[(float(i.replace('%', ''))/100) for i in df['PremarketChg %']]
    
    #Selection criteria
    #First criteria
    c1=[] 
    for i in range(len(df)):
        if df['PremarketChg %'][i]> 0.2 or df['PremarketChg %'][i]<0.2:
            c1.append(df['Symbol'][i])
    #Second criteria
    c2=[]
    for i in range(len(df)):
        if df['PremarketVol'][i]> 50000 :
            c2.append(df['Symbol'][i])
    #Third criteria
    df['averageVolume']= 1 # Just to create that column
    # I didn't have that column in my df so I created it
    for i in range(len(df)):
        try:
            aux= yf.Ticker(df['Symbol'][i]) #Api yahoo finance
            df['averageVolume'][i]=aux.get_info()['averageVolume']
        except:
            pass
    c3=[]
    for i in range(len(df)):
        if df['averageVolume'][i]> 500000 :
            c3.append(df['Symbol'][i])
    #Fourth criteria
    df['Average True Range']=1 # Just to create that column
    df['Average True Range']=df['Average True Range'].astype('float64')
    for i in range(len(df)):
        try:
            aux= yf.Ticker(df['Symbol'][i]).history(period='5d')
            df['Average True Range'][i]= round((aux['High']- aux['Low']).mean(),3)
        except:
            pass
    #Acording to the author stocks usually behave "the same" for around 5 days
    c4=[]
    for i in range(len(df)):
        if df['Average True Range'][i]> 0.7 :
            c4.append(df['Symbol'][i])
    #Fith criteria
    df['Market Cap']= 1 # Just to create that column
    for i in range(len(df)):
        try:
            aux= yf.Ticker(df['Symbol'][i])
            df['Market Cap'][i]= aux.get_info()['marketCap']
        except:
            pass
    #Creating a column for market capitalization
    c5=[]
    for i in range(len(df)):
        if df['PremarketPrice'][i]> 5 and df['PremarketPrice'][i]<200 :
            c5.append(df['Symbol'][i])
    c6=[]
    for i in range(len(df)):
        if df['Market Cap'][i]> 500000000 and df['Market Cap'][i]<10000000000 : #No big caps
            c6.append(df['Symbol'][i])
    
    #To avoid repetition
    set1=set(c1)
    set2=set(c2)
    set3=set(c3)
    set4=set(c4)
    set5=set(c5)
    set6=set(c6)
    #Chosing the stocks that check every selection criteria
    stocks_in_play= list(set((set.intersection(set1,set2,set3,set4,set5,set6))))
    stocks_in_play
    
    #Creating the dataframe that will display information about the stocks in play
    df2=df[df['Symbol'].isin(stocks_in_play)].reset_index(drop=True)
    columns_names=['Symbol', 'Price($)','Gap($)','Vol pre-market','Float(Shares)', 'Avg True($)','Avg Vol','Company Name']
    df_sip= pd.DataFrame(columns= columns_names)
    df_sip['Symbol']= df2['Symbol']
    for i in range(len(df_sip)):
        df_sip['Company Name'][i]= df2[df2['Symbol']==df_sip['Symbol'][i]]['Company Name'][i]
    for i in range(len(df_sip)):
        df_sip['Price($)'][i]= df2[df2['Symbol']==df_sip['Symbol'][i]]['PremarketPrice'][i]
    for i in range(len(df_sip)):
        df_sip['Gap($)'][i]= df2[df2['Symbol']==df_sip['Symbol'][i]]['PremarketChg'][i]
    for i in range(len(df_sip)):
        df_sip['Avg True($)'][i]= round(df2[df2['Symbol']==df_sip['Symbol'][i]]['Average True Range'][i],3)
    for i in range(len(df_sip)):
        df_sip['Avg Vol'][i]= df2[df2['Symbol']==df_sip['Symbol'][i]]['averageVolume'][i]
    for i in range(len(df_sip)):
        df_sip['Vol pre-market'][i]= df2[df2['Symbol']==df_sip['Symbol'][i]]['PremarketVol'][i]
    for i in range(len(df2)):
        aux= yf.Ticker(df2['Symbol'][i])
        df_sip['Float(Shares)'][i]= aux.get_info()['floatShares']

    #archivo= df_sip.to_csv(f'Market_Scanner/sip.csv', index= False)
    #print(df_sip)
    return df_sip

#stocks_in_play()
