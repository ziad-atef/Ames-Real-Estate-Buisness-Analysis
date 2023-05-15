import pandas as pd
from sklearn.model_selection import train_test_split
from DataPreparation.Ingestion.Ingestion import read_data, visualize_data
from sklearn.preprocessing import LabelEncoder, RobustScaler
from imblearn.over_sampling import RandomOverSampler
import sys

# Full Preprocessing


def preprocess_data(df):

    # drop the ID column
    df.drop("Id", axis=1, inplace=True)

    # Impute data
    df_i = impute_data(df)

    # Handle outliers
    num_cols = [col for col in df_i.columns if df_i[col].dtype in [
        "int64", "float64"] and col != "SalePrice"]
    for col in num_cols:
        handle_outliers(df_i, col)

    # Feature Scaling
    rs = RobustScaler()
    num_cols = [col for col in df_i.columns if df_i[col].dtype in [
        "int64", "float64"] and col != "SalePrice"]
    df[num_cols] = rs.fit_transform(df[num_cols])

    # Encode data
    df_e = encode_data(df_i)

    # ToDo: Drop columns with low information gain
    useless_cols = [col for col in df_e.columns if df_e[col].nunique() == 2 and
                    (df_e[col].value_counts() / len(df_e) < 0.01).any(axis=None)]
    df_e.drop(useless_cols, axis=1, inplace=True)

    # Drop data with more than 10 unique values
    # ToDo: Remove after Implement other encoding techniques
    df_e.drop("Exterior1st", axis=1, inplace=True)
    df_e.drop("Exterior2nd", axis=1, inplace=True)

    # Split into training, validation and test sets
    train, val = train_test_split(df_e, test_size=0.25, random_state=45)

    # Split into X and y
    x_train = train.drop("Neighborhood", axis=1)
    y_train = train["Neighborhood"]
    x_val = val.drop("Neighborhood", axis=1)
    y_val = val["Neighborhood"]

    # Solve class imbalance problem usinf oversampling
    ros = RandomOverSampler(random_state=42)
    x_resampled, y_resampled = ros.fit_resample(
        x_train, y_train)
    return x_resampled, y_resampled, x_val, y_val

# Impute data


def impute_data(df):

    # I can drop PoolQC, MiscFeature, Alley and Fence features because they have more than 80% of missing values.
    df = df.drop(['Alley', 'PoolQC', 'Fence', 'MiscFeature'], axis=1)

    # Fill missing values with None (nan represents absence of basement/garage/fireplace)
    columns_None = ['BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2',
                    'GarageType', 'GarageFinish', 'GarageQual', 'FireplaceQu', 'GarageCond']
    df[columns_None] = df[columns_None].fillna("None")

    # Fill missing values with most frequent value (for columns with low number of missing values)
    columns_with_lowNA = ['MSZoning', 'Utilities', 'Exterior1st', 'Exterior2nd',
                          'MasVnrType', 'Electrical', 'KitchenQual', 'Functional', 'SaleType']

    # fill missing values for each column (using its own most frequent value)
    df[columns_with_lowNA] = df[columns_with_lowNA].fillna(df.mode().iloc[0])

    # Impute null values in MasVnrType and MasVnrArea columns with the mode and median respectively
    df["MasVnrArea"].fillna(df["MasVnrArea"].median(), inplace=True)

    # Impute null values in LotFrontage column with the median
    df["LotFrontage"].fillna(df["LotFrontage"].median(), inplace=True)

    # Impute null values in GarageYrBlt column with the year the house was sold minus 35 years
    df['GarageYrBlt'] = df['GarageYrBlt'].fillna(df['YrSold']-35)

    return df
# Encode data


def encode_data(df):

    binary_cols = [col for col in df.columns if df[col].dtype not in [
        "int64", "float64"] and df[col].nunique() == 2]
    print("columns having only 2 unique values:", len(binary_cols))
    print(binary_cols)
    for col in binary_cols:
        label_encoder(df, col)

    ohe_cols = [col for col in df.columns if df[col].dtype not in [
        "int64", "float64"] and 10 >= df[col].nunique() > 2]
    print("columns having only <=10 unique values:", len(ohe_cols))
    print(ohe_cols)
    df = one_hot_encoder(df, ohe_cols)

    other_cols = [col for col in df.columns if df[col].dtype not in [
        "int64", "float64"] and df[col].nunique() > 10]
    print("columns having only <=10 unique values:", len(other_cols))
    print(other_cols)
    # ToDo: Implement other encoding techniques

    labelencoder = LabelEncoder()
    df["Neighborhood"] = labelencoder.fit_transform(df["Neighborhood"])

    return df
# For binary columns only


def label_encoder(dataframe, binary_col):
    labelencoder = LabelEncoder()
    dataframe[binary_col] = labelencoder.fit_transform(dataframe[binary_col])
    return dataframe


def one_hot_encoder(dataframe, categorical_cols, drop_first=True):
    dataframe = pd.get_dummies(
        dataframe, columns=categorical_cols, drop_first=drop_first)
    return dataframe


def handle_outliers(df, col):
    quartile1 = df[col].quantile(0.5)
    quartile3 = df[col].quantile(0.95)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    df.loc[(df[col] < low_limit), col] = low_limit
    df.loc[(df[col] > up_limit), col] = up_limit
