import pandas as pd
import streamlit as st
from cleaning.preprocess import getNumberOfDuplicateRows

def preprocessGetFirstNRowsOfDataAndMsg(df, msgToShow, numberOfRowsToShow,):
    st.subheader(msgToShow)
    st.dataframe(df.head(numberOfRowsToShow))

def preprocessGetMissingValTableOrMsg(data_variable,instance_type):
    if isinstance(data_variable, instance_type):
        st.subheader("Missing values found in this columns: ",)
        st.table(data_variable)
    else:
        st.error("No Missing Values Found!")

def preprocessGetDuplicateRowsCountMessageIfAny(df):
    total_duplicate_rows = getNumberOfDuplicateRows(df=df)
    if(total_duplicate_rows > 0):
        st.subheader(f"Number duplicate rows found : {total_duplicate_rows}")
    else : 
        st.error("No Duplicate Rows Found!")

