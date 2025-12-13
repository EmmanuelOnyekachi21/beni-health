import pandas as pd


def read_csv(file):
    """
    Read CSV or Excel file and return pandas DataFrame
    """
    file = file.name.lower()

    if file.endswith('.csv'):
        return pd.read_csv(file)
    elif file_name.endswith(('.xls', '.xlsx')):
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")
