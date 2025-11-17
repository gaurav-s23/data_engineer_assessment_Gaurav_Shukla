# src/utils.py
import pandas as pd

def read_field_config(path: str) -> pd.DataFrame:
    """
    Read Field Config and return a dataframe with columns:
      - Column Name
      - Target Table
    Expects the excel to have these columns (case-insensitive).
    """
    df = pd.read_excel(path, engine='openpyxl')
    # normalize header names (strip)
    df.columns = [c.strip() for c in df.columns]
    # ensure required columns exist
    possible_colname = None
    possible_table = None
    for c in df.columns:
        lc = c.lower()
        if 'column' in lc and 'name' in lc:
            possible_colname = c
        if 'target' in lc and 'table' in lc:
            possible_table = c
        if c.lower() in ('column name', 'column_name'):
            possible_colname = c
        if c.lower() in ('target table', 'target_table', 'target'):
            possible_table = c

    if possible_colname is None or possible_table is None:
        raise ValueError(f"Field Config missing required columns. Found columns: {df.columns.tolist()}")

    df = df.rename(columns={possible_colname: 'Column Name', possible_table: 'Target Table'})
    # trim values
    df['Column Name'] = df['Column Name'].astype(str).str.strip()
    df['Target Table'] = df['Target Table'].astype(str).str.strip()
    return df[['Column Name', 'Target Table']]

def build_table_map(df_config):
    """
    Return dict: { target_table_name: [column_name, ...] }
    Keeps insertion order of columns as in config.
    """
    table_map = {}
    for _, r in df_config.iterrows():
        tbl = r['Target Table']
        col = r['Column Name']
        table_map.setdefault(tbl, []).append(col)
    return table_map
