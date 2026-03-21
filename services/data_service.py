import pandas as pd


def read_file(file):
    if file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            file.seek(0)
            df = pd.read_csv(file, encoding='latin1')
    else:
        df = pd.read_excel(file)
    return df


def get_data_quality(df):
    duplicates = int(df.duplicated().sum())
    missing = int(df.isnull().sum().sum())

    outlier_count = 0
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        outlier_count += int(outliers)

    total_cells = df.shape[0] * df.shape[1]
    quality_score = round(100 - ((missing + duplicates) / total_cells * 100), 1)

    return {
        'rows': int(df.shape[0]),
        'columns': int(df.shape[1]),
        'missing': missing,
        'duplicates': duplicates,
        'outliers': outlier_count,
        'quality_score': quality_score,
        'column_names': list(df.columns)
    }