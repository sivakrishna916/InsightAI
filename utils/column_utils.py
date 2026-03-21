import pandas as pd


def is_id_column(col_name, series):
    id_keywords = ['id', 'code', 'number', 'num', 'no', 'key', 'index',
                   'zip', 'phone', 'postal', 'pin', 'sku', 'ref', 'invoice']
    col_lower = col_name.lower().replace(' ', '')
    if any(keyword in col_lower for keyword in id_keywords):
        return True
    if series.nunique() == len(series):
        return True
    if series.dtype in ['int64', 'float64']:
        if series.min() > 1000 and series.max() < 999999 and series.nunique() > 100:
            sample = series.dropna().head(10)
            if all(1000 <= v <= 99999 for v in sample):
                return True
    return False


def get_best_numeric_cols(df):
    priority_keywords = ['sales', 'revenue', 'profit', 'amount', 'price',
                         'cost', 'quantity', 'total', 'income', 'discount']
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    filtered = [col for col in numeric_cols if not is_id_column(col, df[col])]
    priority = []
    others = []
    for col in filtered:
        if any(kw in col.lower() for kw in priority_keywords):
            priority.append(col)
        else:
            others.append(col)
    result = priority + others
    return result if result else numeric_cols


def get_best_categorical_cols(df):
    priority_keywords = ['category', 'region', 'segment', 'type', 'status',
                         'department', 'product', 'country', 'city', 'state',
                         'gender', 'grade', 'class', 'group', 'brand']
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    smart_cols = []
    for col in categorical_cols:
        if is_id_column(col, df[col]):
            continue
        unique_ratio = df[col].nunique() / len(df)
        if unique_ratio > 0.5:
            continue
        date_keywords = ['date', 'time', 'year', 'month', 'day']
        if any(keyword in col.lower() for keyword in date_keywords):
            continue
        smart_cols.append(col)
    priority = []
    others = []
    for col in smart_cols:
        if any(kw in col.lower() for kw in priority_keywords):
            priority.append(col)
        else:
            others.append(col)
    return priority + others


def get_date_col(df):
    date_keywords = ['date', 'time', 'year', 'month', 'day']
    for col in df.columns:
        if any(keyword in col.lower() for keyword in date_keywords):
            try:
                df[col] = pd.to_datetime(df[col])
                return col
            except:
                pass
    return None