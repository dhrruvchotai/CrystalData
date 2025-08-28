import streamlit as st
import pandas as pd
from cleaning.preprocess import get_missing_values_containing_cols

st.title("DataSet Cleaning - CRYSTAL DATA")

uploaded_file = st.file_uploader("**Upload a CSV file**", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.markdown("First 5 rows of dataset : ")
    st.dataframe(df.head())

    st.subheader("Missing values containing columns are: ",)
    st.markdown(f"<h5 style='color:red;'>{get_missing_values_containing_cols(df)}</h5>",unsafe_allow_html = True)

