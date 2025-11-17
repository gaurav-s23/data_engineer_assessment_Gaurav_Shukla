# src/etl.py
import argparse
import json
from tqdm import tqdm
import pandas as pd
from sqlalchemy import (
    Table, Column, BigInteger, Text, Float, MetaData, VARCHAR
)
from sqlalchemy.dialects.mysql import DOUBLE, BIGINT, TEXT
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from db import init_engine
from utils import read_field_config, build_table_map


# infer SQL column types
def infer_col_type(series: pd.Series):
    try:
        s = series.dropna()
        if s.empty:
            return TEXT
        if pd.api.types.is_integer_dtype(s):
            return BIGINT
        if pd.api.types.is_float_dtype(s):
            return DOUBLE

        max_len = int(s.astype(str).map(len).max())
        if max_len <= 255:
            return VARCHAR(max(32, min(255, max_len)))
        return TEXT
    except Exception:
        return TEXT


# create tables based only on Field Config
def create_tables_from_config(engine, table_map, sample_df=None):
    created = {}
    metadata = MetaData()

    table_order = list(table_map.keys())
    if "property" in table_order:
        table_order.remove("property")
        table_order = ["property"] + table_order

    for table_name in table_order:
        cols = table_map[table_name]

        col_defs = [Column("id", BigInteger, primary_key=True, autoincrement=True)]

        if table_name != "property":
            col_defs.append(Column("property_id", BigInteger, nullable=True))

        for c in cols:
            if c in ("id", "property_id"):
                continue

            if sample_df is not None and c in sample_df.columns:
                ctype = infer_col_type(sample_df[c])
            else:
                ctype = TEXT

            col_defs.append(Column(c, ctype))

        tbl = Table(
            table_name,
            metadata,
            *col_defs,
            mysql_engine="InnoDB",
            extend_existing=True
        )
        tbl.create(engine, checkfirst=True)
        created[table_name] = tbl

    # add FK constraints
    with engine.connect() as conn:
        for tbl_name in created:
            if tbl_name == "property":
                continue
            try:
                conn.execute(
                    f"""
                    ALTER TABLE `{tbl_name}`
                    ADD CONSTRAINT `fk_{tbl_name}_property`
                    FOREIGN KEY (`property_id`)
                    REFERENCES `property`(`id`)
                    ON DELETE CASCADE;
                    """
                )
            except Exception:
                pass

    return created


# extract simple scalar fields
def flatten_top(record, cols):
    out = {}
    for c in cols:
        if c in record and not isinstance(record[c], (list, dict)):
            out[c] = record[c]
    return out


# insert wrapper
def insert_row(session, table, row):
    res = session.execute(table.insert().values(**row))
    session.flush()
    try:
        pk = res.inserted_primary_key[0]
    except:
        pk = None
    return pk


# ------------------------- MAIN ETL ------------------------- #
def main(jsonl_path, config_path):
    engine = init_engine()

    print("\nLoading field config...")
    df_cfg = read_field_config(config_path)
    table_map = build_table_map(df_cfg)
    print("Tables defined in config:", table_map.keys())

    print("Reading sample rows for type inference...")
    sample = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i > 200:
                break
            try:
                sample.append(json.loads(line))
            except:
                pass

    sample_df = pd.json_normalize(sample) if sample else pd.DataFrame()

    print("Creating DB tables (from Field Config only)...")
    created = create_tables_from_config(engine, table_map, sample_df)

    from sqlalchemy.orm import Session as SASession
    session = SASession(bind=engine)

    print("Starting ETL insert...\n")
    rows_processed = 0

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in tqdm(f):
            if not line.strip():
                continue

            try:
                rec = json.loads(line)
            except:
                continue

            # ----------------- PROPERTY INSERT ---------------- #
            prop_cols = table_map.get("property", [])
            prop_row = flatten_top(rec, prop_cols)

            prop_id = None
            try:
                prop_id = insert_row(session, created["property"], prop_row)
            except Exception as e:
                print("\n❌ Property insert ERROR:", e)
                print("Row:", prop_row)
                session.rollback()
                continue

            # ----------------- CHILD TABLE INSERTS ------------ #
            for tbl, cols in table_map.items():
                if tbl == "property":
                    continue

                topval = rec.get(tbl)

                if isinstance(topval, list):
                    for item in topval:
                        if not isinstance(item, dict):
                            continue
                        row = {c: item.get(c) for c in cols if c in item and not isinstance(item[c], (list, dict))}
                        row["property_id"] = prop_id

                        try:
                            insert_row(session, created[tbl], row)
                        except Exception as e:
                            print(f"\n❌ Insert error in `{tbl}` (list item):", e)
                            print("Row:", row)
                            session.rollback()

                elif isinstance(topval, dict):
                    row = {c: topval.get(c) for c in cols if c in topval and not isinstance(topval[c], (list, dict))}
                    if row:
                        row["property_id"] = prop_id
                        try:
                            insert_row(session, created[tbl], row)
                        except Exception as e:
                            print(f"\n❌ Insert error in `{tbl}` (dict):", e)
                            print("Row:", row)
                            session.rollback()

                else:
                    row = flatten_top(rec, cols)
                    if row:
                        row["property_id"] = prop_id
                        try:
                            insert_row(session, created[tbl], row)
                        except Exception as e:
                            print(f"\n❌ Insert error in `{tbl}` (scalar):", e)
                            print("Row:", row)
                            session.rollback()

            try:
                session.commit()
            except Exception as e:
                print("\n❌ Commit ERROR:", e)
                session.rollback()

            rows_processed += 1

    print(f"\nETL finished. Rows processed: {rows_processed}\n")


# CLI
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    main(args.jsonl, args.config)
