import streamlit as st
import pandas as pd
from cleaning.utils import preprocessGetMissingValTableOrMsg,preprocessGetFirstNRowsOfDataAndMsg
from cleaning.preprocess import getMissingValuesContainingColsWithCountOrMsg,handleMissingValues

st.title("DataSet Cleaning - CRYSTAL DATA")

uploaded_file = st.file_uploader("**Upload a CSV file**", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader(f"Shape of Data is : {df.shape}")
    preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="First 5 rows of dataset : ",numberOfRowsToShow=5)

    
    missing_values_cols_with_counts_or_message = getMissingValuesContainingColsWithCountOrMsg(df = df)
    preprocessGetMissingValTableOrMsg(data_variable=missing_values_cols_with_counts_or_message, instance_type=pd.DataFrame)


    if isinstance(missing_values_cols_with_counts_or_message, pd.DataFrame):
        missing_values_col_handle_options = {}
        for col in missing_values_cols_with_counts_or_message["Column Name"]:
            missing_values_col_handle_options[col] = st.selectbox(
                label = f"Choose How To Handle Missing Values in {col} Column : ",
                options = ["Do Nothing", "Drop Column", "Drop Rows", "Fill With Mean", "Fill With Median", "Fill With Mode"],
                key = col
            )
        if(st.button("Perform Selected Operation")):
            df = handleMissingValues(df=df,fill_missing_values_cols_options=missing_values_col_handle_options)
            preprocessGetMissingValTableOrMsg(data_variable=getMissingValuesContainingColsWithCountOrMsg(df), instance_type = pd.DataFrame)
            st.subheader(f"After Performing Operations Shape Of Data is : {df.shape}")
            preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="After Performing Operations First 2 rows of dataset : ",numberOfRowsToShow=2)


