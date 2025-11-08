#for detecting charset of csv files
import os
import pandas as pd
import streamlit as st
#to show ydata profiling report in app
import streamlit.components.v1 as components
#to detect encoding
import chardet
#to detect separator
import csv
from cleaning.utils import preprocessGetMissingValTableOrMsg
from cleaning.utils import preprocessGetFirstNRowsOfDataAndMsg
from cleaning.utils import preprocessGetDuplicateRowsCountMessageIfAny
from cleaning.preprocess import getMissingValuesContainingColsWithCountOrMsg
from cleaning.preprocess import handleMissingValues
from cleaning.preprocess import removeDuplicateRows
from cleaning.preprocess import getNumericalAndCategoricalColumnNamesFromData
from cleaning.utils import preprocessGetMissingValuesBarGraphIfExists
from ydata_profiling import ProfileReport
from cleaning.utils import preprocessGetTableForNumericAndCategoricalColumnsInDataOrMsg
#PLOTLY FOR PLOTTING GRAPHS
import plotly.express as px
from cleaning.utils import preprocessGetHistogramPlottingSectionForUnivariateNumericalCols
from cleaning.utils import preprocessGetBarChartPlottingSectionForUnivariateCategoricalCols
from cleaning.utils import preprocessGetScatterPlotPlottingSectionForBivariateAndMultivariateNumericalVsNumerical
from cleaning.utils import preprocessGetHeatmapPlottingSectionForBivariateAndMultivariateCategoricalVsCategorical
from cleaning.utils import preprocessGetBoxplotPlottingSectionForOutlierDetection

st.title("DataSet Cleaning - CRYSTAL Data")

uploaded_file = st.file_uploader("**Upload a CSV file**", type=["csv"],)


if uploaded_file:
    with st.spinner("Detecting Encoding and Separator from Data...."):
        # FOR DETECTING ENCODING OF DATASET AND SETTING ENCODING ACCORDINGLY WHILE READING CSV FILE
        # read method is used for reading raw bytes for detecting encoding of dataset
        raw_data = uploaded_file.read(2048)
        result = chardet.detect(raw_data)
        data_encoding = result['encoding']
        uploaded_file.seek(0)

        #NOW DETECT SEPARATOR THAT WHICH OF THIS IS USED TO SEPARATE COLUMNS IN CSV(, ; | \t)
        try:
            sample = uploaded_file.read(2048).decode(encoding=data_encoding, errors='Ignore')
            uploaded_file.seek(0)
            sniffed_sample = csv.Sniffer().sniff(sample=sample)
            separator = sniffed_sample.delimiter
        except Exception:
            print(f"An error occurred while detecting separator of uploaded file : {Exception}")
            separator = ","

    #READ CSV
    df = pd.read_csv(uploaded_file, encoding="latin", sep=separator)

    st.markdown("---")
    #TO MAKE THE TEXT FOR DOWNLOADING REPORT CENTER
    is_generate_data_analysis_report_button_clicked = False
    col1,col2,col3, = st.columns([0.6,5.2,0.4])
    with col2:
        st.subheader("Generate And Download Data Analysis Report : ")
    #TO MAKE GENERATE REPORT BUTTON CENTER
    col1, col2, col3 = st.columns([2,3,1])
    with col2:
        #GENERATE Y DATA PROFILING ANALYSIS AND OPEN FILE IN NEW TAB
        if(st.button('Generate Data Analysis Report')):
            is_generate_data_analysis_report_button_clicked = True
            with st.spinner("Generating Data Analysis Report...."):
                profReport = ProfileReport(df=df, title='Data Analysis Report')
                # SAVING AND READING THEN IS NEEDED FOR SHOWING IN APP OR SHOWING IN NEW TAB FOR PROVIDING DOWNLOAD NO NEED
                # os.makedirs('outputs', exist_ok=True)
                # profReport.to_file('outputs/profile_report.html')
                # with open('outputs/profile_report.html', 'rb') as f:
                #     data_analysis_report_bytes = f.read()
                data_analysis_report = profReport.to_html()

    if is_generate_data_analysis_report_button_clicked:
        st.success('Data Analysis Report generated successfully!')
       
        #TO MAKE THE DOWNLOAD REPORT BUTTON CENTER
        col1,col2,col3 = st.columns([2,3,1])
        with col2:
            st.download_button(
                label = 'Download Data Analysis Report',
                data=data_analysis_report,
                file_name="data_analysis_report.html",
                mime='text/html'
            )

            # SHOW REPORT IN APP
            # with open('outputs/profile_report.html', 'r', encoding='utf-8') as f:
            #     data_analysis_report_html = f.read()
            #     components.html(data_analysis_report_html, height=800, scrolling=True)


            # PROVIDE LINK TO OPEN REPORT IN NEW TAB (NOT WORKING)
            # generated_report_path = './outputs/profile_report.html'
            # generated_report_url = f"./{generated_report_path}"
            # st.markdown(f"[Open Data Analysis Report]({generated_report_path})", unsafe_allow_html=True)

    st.markdown("---")
    #SHOW SHAPE OF DATA AND FIRST 5 ROWS
    st.info(f"Shape of Data is : {df.shape}")
    preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="First 5 rows of Dataset : ",numberOfRowsToShow=5)
    
    st.markdown("---")
    col1,col2,col3 = st.columns([0.8,4,0.6])
    with col2:
        st.subheader("Handle Missing Values & Duplicate Rows")
    st.markdown("---")
    #SHOW MISSING VALUES COL AND COUNT TABLE IF ANY OTHERWISE SHOW MSG
    missing_values_cols_with_counts_or_message = getMissingValuesContainingColsWithCountOrMsg(df = df)
    preprocessGetMissingValTableOrMsg(data_variable=missing_values_cols_with_counts_or_message, instance_type=pd.DataFrame)

    #For Empty Space (Temporary)
    st.subheader(" ")
    #SHOWING BAR GRAPH OF MISSING VALUES COLUMNS NAMES AND THEIR COUNTS
    preprocessGetMissingValuesBarGraphIfExists(data_variable=missing_values_cols_with_counts_or_message, instance_type=pd.DataFrame)

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
        #TO MAKE BUTTON IN CENTER
        is_selected_operation_performed = False
        col1, col2, col3 = st.columns([2.03,3,1])
        with col2:
            #BUTTON TO PERFORM OPERATION THAT WE SELECTED FROM DROP DOWN FOR ALL COLS
            if(st.button("Perform Selected Operation")):
                is_selected_operation_performed = True
                df = handleMissingValues(df=df,fill_missing_values_cols_options=missing_values_col_handle_options)
        if is_selected_operation_performed:
            preprocessGetMissingValTableOrMsg(data_variable=getMissingValuesContainingColsWithCountOrMsg(df), instance_type = pd.DataFrame)
            st.info(f"After Performing Selected Operations, Shape Of Data is : {df.shape}")
            preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="After Performing Operations, First 3 rows of dataset : ",numberOfRowsToShow=3)

    #TO MAKE BUTTON IN CENTER
    is_get_count_of_duplicate_rows_button_pressed = False
    col1, col2, col3 = st.columns([2,3,1])
    with col2:
        #BUTTON FOR GETTING COUNT OF DUPLICATE ROWS
        if(st.button("Get Count Of Duplicate Rows")):
            is_get_count_of_duplicate_rows_button_pressed = True
    if is_get_count_of_duplicate_rows_button_pressed:
        preprocessGetDuplicateRowsCountMessageIfAny(df)

    #TO MAKE BUTTON IN CENTER
    is_remove_duplicate_rows_button_pressed = False
    col1, col2, col3 = st.columns([2.2,3,1])
    with col2:
        #BUTTON FOR REMOVING DUPLICATE ROWS
        if(st.button('Remove Duplicate Rows')):
            is_remove_duplicate_rows_button_pressed = True
            df = removeDuplicateRows(df=df)
    if is_remove_duplicate_rows_button_pressed:
        st.info("Duplicate Rows Removed! (If any)")    
        st.subheader("After Removing Duplicate Rows : ")
        preprocessGetDuplicateRowsCountMessageIfAny(df)

    st.markdown("---")
    #TO SHOW TABLE FOR THE NUMERICAL AND CATEGORICAL VARIABLE COUNTS IN DATA OR SHOW MESSAGE
    st.subheader('Numerical and Categorical Columns in Data : ')
    preprocessGetTableForNumericAndCategoricalColumnsInDataOrMsg(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical= 10)

    numerical_cols, categorical_cols = getNumericalAndCategoricalColumnNamesFromData(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=10)

    #Univariate Analysis section
    st.markdown("---")
    col1,col2,col3 = st.columns([2,3,1])
    with col2:
        st.subheader("Univariate Analysis")
    st.markdown("---")

    #Histogram : Numerical (Numerical)
    st.subheader('Histogram : Numerical Columns')
    preprocessGetHistogramPlottingSectionForUnivariateNumericalCols(df=df, numerical_cols=numerical_cols)

    #Bar Chart : Categorical (Univariate)
    st.subheader("Bar Chart : Categorical Columns")
    preprocessGetBarChartPlottingSectionForUnivariateCategoricalCols(df=df,categorical_cols=categorical_cols)

    #Bivariate Analysis section
    st.markdown("---")
    col1,col2,col3 = st.columns([1.5,4,1])
    with col2:
        st.subheader("Bivariate & Multivariate Analysis")
    st.markdown("---")

    #Scatter : Numerical vs Numerical
    st.subheader("Plot : Numerical vs Numerical")
    preprocessGetScatterPlotPlottingSectionForBivariateAndMultivariateNumericalVsNumerical(df=df,numerical_cols=numerical_cols,categorical_cols=categorical_cols)

    #Heatmap : Categorical vs Categorical
    st.subheader("Plot : Categorical vs Categorical")
    preprocessGetHeatmapPlottingSectionForBivariateAndMultivariateCategoricalVsCategorical(df=df,categorical_cols=categorical_cols)

    #Outlier Detection & Removal
    st.markdown("---")
    col1,col2,col3 = st.columns([1.35,3,1])
    with col2:
        st.subheader("Outlier Detection & Removal")
    st.markdown("---")
    st.subheader("Outlier Detection & Removal : Boxplot")
    df = preprocessGetBoxplotPlottingSectionForOutlierDetection(df=df,numerical_cols=numerical_cols)
    


    #STANDARDIZATION AND NORMALIZATION
    st.markdown("---")
    
    col1,col2 = st.columns([0.65,8])
    with col2:
        st.subheader("Feature Scaling (Standardization / Normalization)")
    st.markdown("---")



            



