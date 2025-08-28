import pandas as pd
def get_missing_values_containing_cols(df):
    missing_cols = df.columns[df.isnull().any()].tolist()
    return ", ".join(map(lambda colName : colName, missing_cols))