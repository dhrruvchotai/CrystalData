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
from cleaning.preprocess import applyScalingOnNumericalColumns
import plotly.figure_factory as ff
from cleaning.encoding import get_categorical_columns, apply_label_encoding, apply_one_hot_encoding
from cleaning.pipeline_generator import generate_pipeline_code
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="CRYSTAL Data - Dataset Cleaning", layout="wide")

col1,col2,col3 = st.columns([3,7,1])
with col2:
    st.title("Dataset Cleaning - CRYSTAL Data")

# Initialize Session State
if 'df' not in st.session_state:
    st.session_state['df'] = None
if 'pipeline_steps' not in st.session_state:
    st.session_state['pipeline_steps'] = []

def add_pipeline_step(step):
    st.session_state['pipeline_steps'].append(step)

uploaded_file = st.file_uploader("**Upload a CSV file**", type=["csv"],)

if uploaded_file:
    # Only load if not already loaded or if a new file is uploaded
    # (Simple check: if df is None, load. If user uploads new file, streamlit reruns, 
    # but we need to detect if it's a *new* file. 
    # For simplicity, if uploaded_file changes, we reload. 
    # But Streamlit handles file uploader state. If we want to persist changes, 
    # we should load once and then work on session_state['df'].)
    
    # We use a hash of the file to detect changes or just check if it's the same object
    # But simpler: If st.session_state['df'] is None, load it.
    # If user wants to reset, they can reload the page or we provide a reset button.
    
    if st.session_state['df'] is None:
        with st.spinner("Detecting Encoding and Separator from Data...."):
            # FOR DETECTING ENCODING OF DATASET AND SETTING ENCODING ACCORDINGLY WHILE READING CSV FILE
            raw_data = uploaded_file.read(2048)
            result = chardet.detect(raw_data)
            data_encoding = result['encoding']
            uploaded_file.seek(0)

            #NOW DETECT SEPARATOR
            try:
                sample = uploaded_file.read(2048).decode(encoding=data_encoding, errors='Ignore')
                uploaded_file.seek(0)
                sniffed_sample = csv.Sniffer().sniff(sample=sample)
                separator = sniffed_sample.delimiter
            except Exception:
                # print(f"An error occurred while detecting separator of uploaded file : {Exception}")
                separator = ","

        #READ CSV
        try:
            st.session_state['df'] = pd.read_csv(uploaded_file, encoding=data_encoding, sep=separator)
            st.session_state['original_df'] = st.session_state['df'].copy() # Keep original
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.session_state['df'] = pd.read_csv(uploaded_file, encoding="latin1", sep=separator)


    df = st.session_state['df']

    st.markdown("---")
    

    #TO MAKE THE TEXT FOR DOWNLOADING REPORT CENTER
    is_generate_data_analysis_report_button_clicked = False
    col1,col2,col3, = st.columns([2.4,5.2,0.4])
    with col2:
        st.subheader("Generate And Download Data Analysis Report : ")
    #TO MAKE GENERATE REPORT BUTTON CENTER
    col1, col2, col3 = st.columns([2.9,3,1])
    with col2:
        #GENERATE Y DATA PROFILING ANALYSIS AND OPEN FILE IN NEW TAB
        if(st.button('Generate Data Analysis Report')):
            is_generate_data_analysis_report_button_clicked = True
            with st.spinner("Generating Data Analysis Report...."):
                profReport = ProfileReport(df=df, title='Data Analysis Report')
                data_analysis_report = profReport.to_html()

    if is_generate_data_analysis_report_button_clicked:
        st.success('Data Analysis Report generated successfully!')
       
        #TO MAKE THE DOWNLOAD REPORT BUTTON CENTER
        col1,col2,col3 = st.columns([2.8,3,1])
        with col2:
            st.download_button(
                label = 'Download Data Analysis Report',
                data=data_analysis_report,
                file_name="data_analysis_report.html",
                mime='text/html'
            )

    st.markdown("---")
    #SHOW SHAPE OF DATA AND FIRST 5 ROWS
    st.info(f"Shape of Data is : {df.shape}")
    preprocessGetFirstNRowsOfDataAndMsg(df=df, msgToShow="First 5 rows of Dataset : ",numberOfRowsToShow=5)
    
    st.markdown("---")
    col1,col2,col3 = st.columns([2.3,4,0.6])
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
                key = f"missing_{col}",
            )
        #TO MAKE BUTTON IN CENTER
        col1, col2, col3 = st.columns([3,3,1])
        with col2:
            #BUTTON TO PERFORM OPERATION THAT WE SELECTED FROM DROP DOWN FOR ALL COLS
            if(st.button("Perform Selected Operation")):
                
                # Track steps before modifying df
                for col, method in missing_values_col_handle_options.items():
                    if method != "Do Nothing":
                        step = {'type': 'impute', 'column': col}
                        if method == "Drop Column":
                            step = {'type': 'drop_columns', 'columns': [col]}
                        elif method == "Drop Rows":
                            step = {'type': 'drop_rows', 'columns': [col]}
                        elif method == "Fill With Mean":
                            step['strategy'] = 'mean'
                        elif method == "Fill With Median":
                            step['strategy'] = 'median'
                        elif method == "Fill With Mode":
                            step['strategy'] = 'mode'
                        add_pipeline_step(step)

                df = handleMissingValues(df=df,fill_missing_values_cols_options=missing_values_col_handle_options)
                st.session_state['df'] = df # Update session state
                st.rerun()

    #TO MAKE BUTTON IN CENTER
    is_get_count_of_duplicate_rows_btn_pressed = False
    col1, col2, col3 = st.columns([2.983,3,1])
    with col2:
        #BUTTON FOR GETTING COUNT OF DUPLICATE ROWS
        if(st.button("Get Count Of Duplicate Rows")):
            is_get_count_of_duplicate_rows_btn_pressed = True
    if is_get_count_of_duplicate_rows_btn_pressed:
        preprocessGetDuplicateRowsCountMessageIfAny(df)

    #TO MAKE BUTTON IN CENTER
    is_remove_duplicate_rows_btn_pressed = False
    col1, col2, col3 = st.columns([3.15,3,1])
    with col2:
        #BUTTON FOR REMOVING DUPLICATE ROWS
        if(st.button('Remove Duplicate Rows')):
            is_remove_duplicate_rows_btn_pressed = True
            df = removeDuplicateRows(df=df)
            st.session_state['df'] = df
            add_pipeline_step({'type': 'remove_duplicates'})
    if is_remove_duplicate_rows_btn_pressed:
        st.success("Duplicate Rows Removed!")

    st.markdown("---")
    #TO SHOW TABLE FOR THE NUMERICAL AND CATEGORICAL VARIABLE COUNTS IN DATA OR SHOW MESSAGE
    st.subheader('Numerical and Categorical Columns in Data : ')
    preprocessGetTableForNumericAndCategoricalColumnsInDataOrMsg(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical= 10)

    numerical_cols, categorical_cols = getNumericalAndCategoricalColumnNamesFromData(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=10)

    #Univariate Analysis section
    st.markdown("---")
    col1,col2,col3 = st.columns([3,3,1])
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
    col1,col2,col3 = st.columns([2.9,4,1])
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
    col1,col2,col3 = st.columns([2.5,3,1])
    with col2:
        st.subheader("Outlier Detection & Removal")
    st.markdown("---")
    st.subheader("Outlier Detection & Removal : Boxplot")
    
    # Note: The outlier function in utils.py uses st.session_state.cleaned_df internally. 
    # We need to sync it with our main st.session_state['df']
    # For now, we pass df. If the user modifies it there, we should capture it.
    # However, the utils function returns the modified df.
    
    # To make it work smoothly with our main session state, we might need to update the utils function
    # or just assign the result back.
    # The utils function has its own buttons and logic. 
    # Let's trust it returns the modified df.
    
    # IMPORTANT: The utils function uses st.session_state.cleaned_df. 
    # We should probably initialize that with our current df if it's not set or if we want to sync.
    if "cleaned_df" not in st.session_state or st.session_state.cleaned_df is not df:
         st.session_state.cleaned_df = df

    df_outliers_handled = preprocessGetBoxplotPlottingSectionForOutlierDetection(df=df,numerical_cols=numerical_cols)
    
    if df_outliers_handled is not df:
        st.session_state['df'] = df_outliers_handled
        df = df_outliers_handled
        # Note: Outlier removal is hard to track in simple pipeline without custom code.
        # We'll skip adding it to pipeline_steps for now or add a comment.
    
    #CHECK NORMAL DISTRIBUTION
    st.markdown("---")
    col1,col2,col3 = st.columns([3.1,3,1])
    with col2:
        st.subheader("Normal Distribution")
    col1,col2,col3 = st.columns([1.35,3,1])
    with col2:
        if len(numerical_cols) > 0:
            y_col = st.selectbox("Select Column to plot kde Plot:",options=numerical_cols)
            fig = ff.create_distplot([df[y_col].fillna(df[y_col].median())],group_labels=[y_col],curve_type='kde',show_hist=False)
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.warning("No numerical columns for Normal Distribution check.")


    # ENCODING SECTION
    st.markdown("---")
    col1,col2,col3 = st.columns([3.4,3,1.8])
    with col2:
        st.subheader("Categorical Encoding")
    st.markdown("---")
    
    enc_cat_cols = get_categorical_columns(df)
    if enc_cat_cols:
        col1, col2 = st.columns(2)
        with col1:
            encoding_method = st.selectbox("Select Encoding Method", ["None", "Label Encoding", "One-Hot Encoding"])
        with col2:
            cols_to_encode = st.multiselect("Select Columns to Encode", enc_cat_cols)

        #ENCODING CATEGORICAL DATA
        is_apply_encoding_button_pressed = False
        is_apply_label_encoding_button_pressed = False
        is_apply_ohe_button_pressed = False
        col1,col2,col3 = st.columns([3.6,3,1.4])
        with col2:    
            if st.button("Apply Encoding"):
                is_apply_encoding_button_pressed = True
                if encoding_method == "Label Encoding" and cols_to_encode:
                    is_apply_label_encoding_button_pressed = True
                    df, _ = apply_label_encoding(df, cols_to_encode)
                    st.session_state['df'] = df
                    add_pipeline_step({'type': 'label_encoding', 'columns': cols_to_encode})

                elif encoding_method == "One-Hot Encoding" and cols_to_encode:
                    is_apply_ohe_button_pressed = True
                    df = apply_one_hot_encoding(df, cols_to_encode)
                    st.session_state['df'] = df
                    add_pipeline_step({'type': 'one_hot_encoding', 'columns': cols_to_encode})
                   
        if is_apply_encoding_button_pressed:
            if is_apply_label_encoding_button_pressed:
                st.success(f"Applied Label Encoding on {cols_to_encode}")
            
            elif is_apply_ohe_button_pressed:
                st.success(f"Applied One-Hot Encoding on {cols_to_encode}")
                

        
    else:
        st.info("No categorical columns available for encoding.")

    #STANDARDIZATION AND NORMALIZATION
    st.markdown("---")
    
    col1,col2 = st.columns([3.3,8])
    with col2:
        st.subheader("Feature Scaling (Standardization / Normalization)")
    st.markdown("---")

    # Re-fetch numerical cols as they might have changed after encoding
    numerical_cols, _ = getNumericalAndCategoricalColumnNamesFromData(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=10)

    selected_scaling_method_for_each_column = {}
    for col in numerical_cols:
        selected_scaling_method_for_each_column[col] = st.selectbox(
            f"Select Scaling method for {col} Column : ", 
            options=["None", "StandardScaler (Z-score)", "MinMaxScaler (0-1)", "RobustScaler (less affected by outliers)"],
            key=f"scale_{col}"
        )

    is_perform_scaling_button_pressed = False
    col1,col2,col3 = st.columns([3.2,3,1])
    with col2:
        if st.button("Perform Scaling on the Data"):
            is_perform_scaling_button_pressed = True
            df = applyScalingOnNumericalColumns(df=df,numerical_cols=numerical_cols,selected_scaling_method_for_each_column=selected_scaling_method_for_each_column)
            st.session_state['df'] = df
            
            # Track steps
            for col, method in selected_scaling_method_for_each_column.items():
                if method != "None":
                    add_pipeline_step({'type': 'scale', 'columns': [col], 'method': method})
            
            
    if is_perform_scaling_button_pressed:
        st.success("Data successfully Scaled using selected Scaling methods for each Column.")
        preprocessGetFirstNRowsOfDataAndMsg(df=df,numberOfRowsToShow=5,msgToShow="First 5 rows of Data after Scaling : ")


    # TRAIN TEST SPLIT
    st.markdown("---")
    col1,col2,col3 = st.columns([3.9,3,1.8])
    with col2:
        st.subheader("Train / Test Split")
    st.markdown("---")
    
    target_col = st.selectbox("Select Target Column", df.columns)
    test_size = st.slider("Test Size", 0.1, 0.5, 0.2)
    random_state = st.number_input("Random State", value=42, step=1)

    col1,col2,col3 = st.columns([4.4,3,1.5])
    with col2:
        if st.button("Split Data"):
            try:
                X = df.drop(columns=[target_col])
                y = df[target_col]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
                
                st.success(f"Data Split Successfully! Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")
                
                # Prepare downloads
                train_df = pd.concat([X_train, y_train], axis=1)
                test_df = pd.concat([X_test, y_test], axis=1)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button("Download Train Data", train_df.to_csv(index=False), "train.csv", "text/csv")
                with c2:
                    st.download_button("Download Test Data", test_df.to_csv(index=False), "test.csv", "text/csv")
                    
            except Exception as e:
                st.error(f"Error splitting data: {e}")

    # PIPELINE GENERATION
    st.markdown("---")
    col1,col2,col3 = st.columns([3.68,3,1.8])
    with col2:
        st.subheader("Generate Pipeline Code")
    col1,col2,col3 = st.columns([3.9,3,1.8])
    with col2:
        if st.button("Generate Sklearn Pipeline Code"):
            pipeline_code = generate_pipeline_code(st.session_state['pipeline_steps'])
            st.code(pipeline_code, language='python')
            st.download_button("Download Pipeline Code", pipeline_code, "pipeline.py", "text/plain")
    
    # Final Download
    st.markdown("---")
    col1,col2,col3 = st.columns([4.16,3,1.8])
    with col2:
        st.download_button("Download Processed Data", df.to_csv(index=False), "processed_data.csv", "text/csv")

