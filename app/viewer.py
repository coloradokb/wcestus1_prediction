import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

class Viewer:
    DATE = 'Date'
    #BARRELS_DS = 'wcest1_multivariate_features.csv'
    BARRELS_PRED_DS = 'univariate_weekly_pred.csv'
    #BARRELS_PRED_DS = 'univariate_weekly_pred_50_100.csv'
    BARRELS_ACTUAL_DS = 'wcestus1_latest.csv'
    

    def __init__(self, display_model,layout="wide"):
        self.display_model = display_model
        st.set_page_config(
            layout = layout
        )


    #@st.cache
    def load_data(self,nrows):
        df = pd.read_csv('../data/'+self.BARRELS_ACTUAL_DS, header=0,
                           infer_datetime_format=True, delimiter=';',
                           parse_dates=[self.DATE], index_col=[self.DATE])
        df = df.fillna(0)
        df = df[len(df)-nrows:]
        #df = df.sort_index(ascending=False)
        #df['ERR'] = pd.to_numeric(df.WCESTUS1) - pd.to_numeric(df.PREDICTION)
        return df

    def load_pred_data(self):
            df = pd.read_csv('../data/predictions/'+self.BARRELS_PRED_DS, header=0,
                             infer_datetime_format=True, delimiter=';',
                             parse_dates=[self.DATE], index_col=[self.DATE]
                            )
            df = df.fillna(0)
            return df
            
    def merge_actual_and_pred(self,actual_df,pred_df):
        #st.write(actual_df,pred_df)
        df = pd.merge(actual_df, pred_df, on='Date', how='outer')
        df = df.sort_index(ascending=False)
        df['ERR'] = pd.to_numeric(df.WCESTUS1) - pd.to_numeric(df.Prediction)
        #st.write(df)
        return df

    def graph_barrels_and_snp(self):
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        
        path=os.path.abspath(os.path.join(".", os.pardir))
        st.write(os.path.abspath(os.path.join(".", os.pardir)))
        
        all_barrel_df = pd.read_csv(path+'/data/all_eia_stock_sheet_latest.csv', header=0,
                                    infer_datetime_format=True, delimiter=';',
                                    parse_dates=['Date'], index_col=['Date'])
        
        all_barrel_df['week_of_year'] = all_barrel_df.index.week
        all_barrel_df['year'] = all_barrel_df.index.year
        all_barrel_df['year_plus_week'] = (all_barrel_df.index.year).astype('string') + '-' + (all_barrel_df.index.week).astype('string')
        all_barrel_df = all_barrel_df['2019-01-01':'2021-01-01']
        
        s_and_p_df = pd.read_csv(path+'/data/s_and_p_weekly.csv',header=0,
                                 infer_datetime_format=True, delimiter=',',
                                 parse_dates=['Date'] ,index_col=['Date'])
        s_and_p_df['week_of_year'] = s_and_p_df.index.week
        s_and_p_df['year'] = s_and_p_df.index.year
        s_and_p_df['year_plus_week'] = (s_and_p_df.index.year).astype('string') + '-' + (s_and_p_df.index.week).astype('string')
        s_and_p_df = s_and_p_df['2019-01-01':'2021-01-01']
        #st.write(s_and_p_df.index)    
        st.write(all_barrel_df.tail(10))
        st.write(s_and_p_df.tail(10))
        
        
        
        combo_df = pd.merge(all_barrel_df, s_and_p_df, on='year_plus_week', how='outer')
        combo_df = combo_df.sort_index(ascending=False)
        #combo_df = combo_df.set_index('year_plus_week')
        combo_df = combo_df[['Open','WCESTUS1','WCRSTUS1','WCESTP31','WTTSTUS1']]
        st.write(combo_df.transpose())
        combo_df = pd.DataFrame(scaler.fit_transform(combo_df), columns=combo_df.columns, index=combo_df.index)

        st.write(combo_df)
        st.line_chart(combo_df)
        
    def mat_graph(self,data):
        arr = np.random.normal(1, 1, size=100)
        plt.hist(arr, bins=20)
        return st.pyplot()
    
    def err_data(self,df):
        #df['ERR'] = pd.to_numeric(df.WCESTUS1) - pd.to_numeric(df.PREDICTION)
        df = df.sort_index(ascending=False)
        #st.write(df.ERR[:len(df)-45])
        return df.ERR[:len(df)-45]
    
    def display_data(self,data):
        df_err = data.ERR
        new_d = data.drop(columns='ERR')
        st.title("WCESTUS1 DATA / PREDICTIONS")
        col1, col2= st.beta_columns(2)
        with col1:
            st.subheader('Barrels (100K)')
            st.line_chart(new_d)
        
        with col2:
            st.dataframe(data.fillna('-')) #clean up the NaN from df view
            #self.mat_graph(None)
        
        st.subheader("Prediction/Err")
        err_data = data.ERR
        col4,col5 = st.beta_columns(2)
        #with col3:
        #    st.write(err_data)
        with col4:
            st.bar_chart(err_data)
        with col5:
            st.write(err_data.describe())
            
        
        

    def create_histogram(self,data):
        hist_values = np.histogram(data[DATE], bins=24, range=(0, 24))[0]

n_rows = 52
vc = Viewer('univ')
x  = vc.load_data(n_rows)
y  = vc.load_pred_data()
#print(x.tail())
#vc.display_data(x)
comparison_df = vc.merge_actual_and_pred(x,y)
vc.display_data(comparison_df)
comparison_df.to_csv("/tmp/all_pred.csv",sep=',', encoding='utf-8')
vc.graph_barrels_and_snp()