import streamlit as st
import pandas as pd


st.title("DataSet Cleaning - CRYSTAL DATA")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("First 5 rows of dataset : ")
    st.dataframe(df.head())

