import os
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
import requests
#from requests import get
from dateutil.parser import parse as parsedate
#import wget


class DataGrabber:
    #source of barrel reserves
    EIA_DL_URL = 'http://ir.eia.gov/wpsr/psw09.xls'
    EIA_OUTFILE= '/tmp/psw09.xls'
    #source of historical pricing
    EIA_OIL_PRICE_URL = 'http://www.eia.gov/dnav/pet/hist_xls/RCLC1w.xls'
    EIA_OIL_PRICE_OUTFILE = '/tmp/RCLC1w.csv'


    def __init__(self):
        pass

    def download_eia_data(self,operation):
        """
            First check to see if file on server is newer than what we have on file system.
            If so, then download and process where necessary
        """
        #set initial timestamps in case of redirects
        file_time = parsedate('2000-01-01 00:00+00:00')
        url_time  = parsedate('2000-01-01 00:00+00:00')
        file_unix_time = file_time.strftime('%s')
        url_unix_time  = url_time.strftime('%s')
        
        
        if operation == 'reserves':
            url = self.EIA_DL_URL
            out = self.EIA_OUTFILE
        if operation == 'pricing':
            url = self.EIA_OIL_PRICE_URL
            out = self.EIA_OIL_PRICE_OUTFILE
            
        r = requests.head(url)#, allow_redirects=True)
        print(f'RET: {r}')
        if r.status_code == 301: #sometimes a permanent redirect is given. take header Location as url for Get
            url = r.headers['Location']
        else:
            url_time = r.headers['last-modified']
            url_date = parsedate(url_time)
            url_unix_time = url_date.strftime('%s')
            print(url_date.strftime('%s'))
            
        #check to see if file exists. If not, download
        if(os.path.isfile(out)):
            file_time = datetime.fromtimestamp(os.path.getmtime(out))
            file_unix_time = file_time.strftime('%s')
            print(f"Here: {file_time}")
        else:
            file_time = parsedate('2000-01-01 00:00+00:00')
            file_unix_time = file_time.strftime('%s')
            
        if (url_unix_time >= file_unix_time) or os.path.isfile(out) == False:
            response = requests.get(url)
            totalbits = 0
            if response.status_code == 200:
                with open(out, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            totalbits += 1024
                            f.write(chunk)
            print(f"Downloaded {operation} file = ",totalbits*1025,"KB...")
            return(1)
        else:
            print("Local file is latest.")
            return(1)
        

                        
    def process_eia_sheet(self):
        df = pd.read_excel(open(self.EIA_OUTFILE, 'rb'),
                                  skiprows=1,
                                  sheet_name='Data 6'
                                  #converters= {'Date': pd.to_datetime},
                                  #index_col='Date'
                                 )
        df = df.drop([0]) #remove desc
        df.rename(columns={'Sourcekey':'Date'},inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        #  df_new = df.rename(columns={'A': 'a'}, index={'ONE': 'one'})
        print(df.head())
        return df
    
    def process_oil_price_history(self):
        """
        This only processes one of the reports (weekly, Contract 1). Future considerations should be given to
        pulling all four and averaging.
        
        This method will download and create readable .csv file in the data directory. Filename = RCLCw1.csv
        """
        df = pd.read_excel(open(self.EIA_OIL_PRICE_OUTFILE, 'rb'),
                                  skiprows=1,
                                  sheet_name='Data 1'
                                  #converters= {'Date': pd.to_datetime},
                                  #index_col='Date'
                                 )
        df = df.drop([0]) #remove desc
        df.rename(columns={'Sourcekey':'Date'},inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')

        file_name = f"{os.path.realpath('../data')}/eia_pricing_latest.csv"
        df.to_csv(file_name, sep=';', encoding='utf-8')
    
    def get_eia_stocks_data(self,df):
        now = datetime.now()
        print ("Current date and time : ")
        print (now.strftime("%Y-%m-%d %H:%M:%S"))
        #date_string = (now.strftime("%Y_%m_%d_%H_%M_%S"))
        file_name = f"{os.path.realpath('../data')}/all_eia_stock_sheet_latest.csv"
        #df = df[start_date:]
        #df.datasheet()
        #all_sheet_df = df['WCESTUS1']
        df.index = df.index.strftime('%b %d, %Y') #revert format back to orig
        print(df.tail())
        
        #print (wcestus1_df.head(20),len(wcestus1_df))
        df.to_csv(file_name, sep=';', encoding='utf-8')
        #print(os.path.realpath('../data'))        
    
    def get_wcestus1_data(self,df,write_file=True):
        file_name = f"{os.path.realpath('../data')}/wcestus1_latest.csv"
        wcestus1_df = df['WCESTUS1']      
        #print (wcestus1_df.head(20),len(wcestus1_df))
        wcestus1_df.to_csv(file_name, sep=';', encoding='utf-8')
        #print(os.path.realpath('../data'))

        return wcestus1_df
         
        
    
    def get_weekly_unemployment_data(self,start_date,end_date):
        #this data comes in weekly. Looks to be off by one day when matching to EIA data
        #need to shift this data to match.  User of their API is next :)
        end_date   = '2020-12-31'
        start_date = '2010-01-01'
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=968&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=ICSA&scale=left&cosd={start_date}&coed={end_date}&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Weekly%2C%20Ending%20Saturday&fam=avg&fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date={end_date}&revision_date={end_date}&nd=1967-01-07"

        download_outfile_name = f"{os.path.realpath('../data')}/ICSA_current.csv"        

        outfile_name = f"{os.path.realpath('../data')}/ICSA_current_with_offset-1.csv"        
        response = requests.get(url)
        totalbits = 0
        try:
            if response.status_code == 200:
                with open(download_outfile_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            totalbits += 1024
                            f.write(chunk)
            print("Downloaded ",totalbits*1025,"KB...")
        except Exception as err:
            print(err)
        
        df = pd.read_csv(download_outfile_name,header=0,
                           infer_datetime_format=True, delimiter=',',
                           parse_dates=["DATE"], index_col=["DATE"])
        #pd.DatetimeIndex(montdist['date']) + pd.DateOffset(1)
        df['shifted_date'] = df.index + pd.Timedelta(days=-1)
        df.to_csv(outfile_name, sep=';', encoding='utf-8')

        print(df.tail(10))
        return df

dg = DataGrabber()
#dg.get_weekly_unemployment_data('','')
operation = 'pricing'
proc_new = dg.download_eia_data(operation)
if(proc_new == 1):
    if operation == 'reserves':
        datasheet = dg.process_eia_sheet()
        dg.get_eia_stocks_data(datasheet)
        dg.get_wcestus1_data(datasheet,None)
    if operation == 'pricing':
        datasheet = dg.process_oil_price_history()
        
   
