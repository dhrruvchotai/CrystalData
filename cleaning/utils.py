import pandas as pd
import streamlit as st

def preprocessGetFirstNRowsOfDataAndMsg(df, msgToShow, numberOfRowsToShow,):
    st.subheader(msgToShow)
    st.dataframe(df.head(numberOfRowsToShow))

def preprocessGetMissingValTableOrMsg(data_variable,instance_type):
    if isinstance(data_variable, instance_type):
        st.subheader("Missing values found in this columns: ",)
        st.table(data_variable)
    else:
        st.error("No Missing Values Found!")
    
