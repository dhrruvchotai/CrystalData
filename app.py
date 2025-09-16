#for detecting charset of csv files
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import chardet
from cleaning.utils import preprocessGetMissingValTableOrMsg,preprocessGetFirstNRowsOfDataAndMsg,preprocessGetDuplicateRowsCountMessageIfAny
from cleaning.preprocess import getMissingValuesContainingColsWithCountOrMsg,handleMissingValues, removeDuplicateRows
from ydata_profiling import ProfileReport

st.title("DataSet Cleaning - CRYSTAL Data")

uploaded_file = st.file_uploader("**Upload a CSV file**", type=["csv"])


if uploaded_file:
    #FOR DETECTING ENCODING OF DATASET AND SETTING ENCODING ACCORDINGLY WHILE READING CSV FILE
    #read method is used for reading raw bytes for detecting encoding of dataset
    # raw_data = uploaded_file.read()
    # result = chardet.detect(raw_data)
    # data_encoding = result['encoding']
    # uploaded_file.seek(0)


    #READ CSV
    df = pd.read_csv(uploaded_file, encoding="latin")

    #GENERATE Y DATA PROFILING ANALYSIS AND OPEN FILE IN NEW TAB
    if(st.button('Generate Data Analysis Report')):
        with st.spinner("Generating Data Analysis Report...."):
            profReport = ProfileReport(df=df, title='Data Analysis Report')
            #SAVING IS NEEDED FOR SHOWING IN APP OR SHOWING IN NEW TAB FOR PROVIDING DOWNLOAD NO NEED
            # os.makedirs('outputs', exist_ok=True)
            # profReport.to_file('outputs/profile_report.html')
            data_analysis_report = profReport.to_html()
            st.success('Data Analysis Report generated successfully!')

         #SAVING AND READING THEN IS NEEDED FOR SHOWING IN APP OR SHOWING IN NEW TAB FOR PROVIDING DOWNLOAD NO NEED
        # with open('outputs/profile_report.html', 'rb') as f:
        #     data_analysis_report_bytes = f.read()

        st.download_button(
            label = 'Download Data Analysis Report',
            data=data_analysis_report,
            file_name="profile_report.html",
            mime='text/html'
        )

        #SHOW REPORT IN APP
        # with open('outputs/profile_report.html', 'r', encoding='utf-8') as f:
        #     data_analysis_report_html = f.read()
        #     components.html(data_analysis_report_html, height=800, scrolling=True)


        # PROVIDE LINK TO OPEN REPORT IN NEW TAB (NOT WORKING)
        # generated_report_path = './outputs/profile_report.html'
        # generated_report_url = f"./{generated_report_path}"
        # st.markdown(f"[Open Data Analysis Report]({generated_report_path})", unsafe_allow_html=True)

    #SHOW SHAPE OF DATA AND FIRST 5 ROWS
    st.subheader(f"Shape of Data is : {df.shape}")
    preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="First 5 rows of dataset : ",numberOfRowsToShow=5)
    
    #SHOW MISSING VALUES COL AND COUNT TABLE IF ANY OTHERWISE SHOW MSG
    missing_values_cols_with_counts_or_message = getMissingValuesContainingColsWithCountOrMsg(df = df)
    preprocessGetMissingValTableOrMsg(data_variable=missing_values_cols_with_counts_or_message, instance_type=pd.DataFrame)

    #SHOW DROP DOWN FOR MISSING VALUES FILLING OR DROPPING ROW COL(NUMERICAL OR CATEGORICAL)
    if isinstance(missing_values_cols_with_counts_or_message, pd.DataFrame):
        missing_values_col_handle_options = {}
        for col in missing_values_cols_with_counts_or_message["Column Name"]:
            if df[col].dtype in ['int64', 'float64']:
                options = ["Do Nothing", "Drop Column", "Drop Rows", "Fill With Mean", "Fill With Median", "Fill With Mode"]
            else :
                options = ["Do Nothing", "Drop Column", "Drop Rows", "Fill With Mode"]
            missing_values_col_handle_options[col] = st.selectbox(
                label = f"Choose How To Handle Missing Values in {col} Column : ",
                options = options,
                key = col,
            )
        #BUTTON TO PERFORM OPERATION THAT WE SELECTED FROM DROP DOWN FOR ALL COLS
        if(st.button("Perform Selected Operation")):
            df = handleMissingValues(df=df,fill_missing_values_cols_options=missing_values_col_handle_options)
            preprocessGetMissingValTableOrMsg(data_variable=getMissingValuesContainingColsWithCountOrMsg(df), instance_type = pd.DataFrame)
            st.subheader(f"After Performing Operations Shape Of Data is : {df.shape}")
            preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="After Performing Operations First 3 rows of dataset : ",numberOfRowsToShow=3)

    #BUTTON FOR GETTING COUNT OF DUPLICATE ROWS
    if(st.button("Get Count Of Duplicate Rows")):
        preprocessGetDuplicateRowsCountMessageIfAny(df)

    #BUTTON FOR REMOVING DUPLICATE ROWS
    if(st.button('Remove Duplicate Rows')):
        removeDuplicateRows(df=df)
        preprocessGetDuplicateRowsCountMessageIfAny(df)
        



