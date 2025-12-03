import pandas as pd
from sklearn.preprocessing import LabelEncoder

def get_categorical_columns(df):
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def apply_label_encoding(df, columns):
    df_encoded = df.copy()
    encoders = {}
    for col in columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
        encoders[col] = le
    return df_encoded, encoders

def apply_one_hot_encoding(df, columns):
    df_encoded = pd.get_dummies(df, columns=columns, drop_first=False)
    # Convert bool columns to int (0/1) for better compatibility
    for col in df_encoded.columns:
        if df_encoded[col].dtype == 'bool':
            df_encoded[col] = df_encoded[col].astype(int)
    return df_encoded
