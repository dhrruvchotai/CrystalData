import pandas as pd
import numpy as np
import streamlit as st

#GET MISSING VALUE COLUMN NAMES DF
def getMissingValuesContainingColsWithCountOrMsg(df):
    missing_counts_all_cols = df.isnull().sum()
    missing_cols_with_counts = missing_counts_all_cols[missing_counts_all_cols > 0]

    if(len(missing_cols_with_counts) > 0):
        return pd.DataFrame({
            "Column Name": missing_cols_with_counts.index,
            "Missing Count": missing_cols_with_counts.values
        })
    else : "No Missing Values Containing Columns Found!"

#HANDLE MISSING VALUES IN EACH COLUMN
def handleMissingValues(df,fill_missing_values_cols_options):
    for col,method in fill_missing_values_cols_options.items():
        if(method == "Drop Column"):
            df.drop(columns=[col], inplace = True)
        elif(method == "Drop Rows"):
            df.dropna(subset =[col], inplace = True)
        elif(method == "Fill With Mean"):
            df[col].fillna(df[col].mean(), inplace = True)
        elif (method == 'Fill With Median'):
            df[col].fillna(df[col].median(), inplace = True)
        elif (method == 'Fill With Mode'):
            df[col].fillna(df[col].mode()[0], inplace = True) 
    return df

#GET NUMBER OF DUPLICATE ROWS
def getNumberOfDuplicateRows(df):
    return df.duplicated().sum()

#REMOVE DUPLICATE ROWS
def removeDuplicateRows(df):
    df.drop_duplicates(inplace=True)
    return df

#GET NUMERICAL AND CATEGORICAL COLUMNS FROM DATA
#NOT ABLE TO FILTER PROPERLY
def getNumericColumnNamesFromData(df):
    return df.select_dtypes(include = ['number']).columns.to_list()
#NOT ABLE TO FILTER PROPERLY
def getCategoricalColumnNamesFromData(df):
    return df.select_dtypes(include = ['object', 'category']).columns.to_list()

#GET NUMERICAL AND CATEGORICAL COLS WITH FILTER
#FILTERS PROPERLY
def getNumericalAndCategoricalColumnNamesFromData(df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=5):
    numerical_cols = getNumericColumnNamesFromData(df)
    categorical_cols = getCategoricalColumnNamesFromData(df)

    #IN ANY NUMERICAL COLUMN NUMBER OF UNIQUE VALUES IS LESS THAN 5 THEN PUT IT UNDER THE CATEGORICAL COLUMN
    #EXAMPLE : Survived and Pclass in titanic 
    #They are categorical but detected under numerical by inbuilt method(because has numerical but has categories) soo will manually detect them
    col_names_to_move_from_numerical_to_categorical = []
    for col_name in numerical_cols:
        #dropna = True avoids counting NAN value in the nunique
        number_of_unique_values_in_col = df[col_name].nunique(dropna=True)
        if(number_of_unique_values_in_col <= min_unique_values_threshold_to_convert_from_numerical_to_categorical):
            col_names_to_move_from_numerical_to_categorical.append(col_name)
    
    numerical_cols = [col_name for col_name in numerical_cols if col_name not in col_names_to_move_from_numerical_to_categorical]
    for col_name in col_names_to_move_from_numerical_to_categorical:
        if col_name not in categorical_cols:
            categorical_cols.append(col_name)

    return numerical_cols,categorical_cols

def getTableOfNumericalAndCategoricalColumnsInDataOrMsg(df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=5):
    numerical_cols,categorical_cols = getNumericalAndCategoricalColumnNamesFromData(df=df, min_unique_values_threshold_to_convert_from_numerical_to_categorical=min_unique_values_threshold_to_convert_from_numerical_to_categorical)

    # Sooo To Create DataFrame we need same no.of rows in both cols
    # but everytime this will not happen that number of numerical and categorical cols are same in dataset that use uploaded sooo we need to do something...
    # will create max number of rows from the max len out of cols
    max_len = max(len(numerical_cols), len(categorical_cols))
    #in the remaining cells i append NAN
    numerical_cols += [np.nan] * (max_len - len(numerical_cols))
    categorical_cols += [np.nan] * (max_len - len(categorical_cols))
    if(max_len == 0):
        return 'No Numerical Or Categorical Columns Found!!'
    else:
        return pd.DataFrame({
        'Numerical Column Names' : numerical_cols,
        'Categorical Column Names' : categorical_cols
        }
    )