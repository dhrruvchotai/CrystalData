import pandas as pd
import streamlit as st

def getMissingValuesContainingColsWithCountOrMsg(df):
    missing_counts_all_cols = df.isnull().sum()
    missing_cols_with_counts = missing_counts_all_cols[missing_counts_all_cols > 0]

    if(len(missing_cols_with_counts) > 0):
        return pd.DataFrame({
            "Column Name": missing_cols_with_counts.index,
            "Missing Count": missing_cols_with_counts.values
        })
    else : "No Missing Values Containing Columns Found!"


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

def getNumberOfDuplicateRows(df):
    return df.duplicated().sum()