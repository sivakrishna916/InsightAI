import pandas as pd
import os

def read_file(file):
    try:
        # File type check
        allowed = ['.csv', '.xlsx', '.xls']
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            return None, "Invalid file type. Please upload CSV or Excel only."

        # File size check (max 50MB)
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 50 * 1024 * 1024:
            return None, "File too large. Maximum size is 50MB."

        if file.filename.endswith('.csv'):
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin1')

        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)

        else:
            raise ValueError("Unsupported file type. Please upload CSV or Excel.")

        if df.empty:
            raise ValueError("The uploaded file is empty.")

        if df.shape[0] > 100000:
            df = df.head(100000)

        return df, None

    except Exception as e:
        return None, str(e)

def get_data_quality(df):
    try:
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
    except Exception as e:
        return None