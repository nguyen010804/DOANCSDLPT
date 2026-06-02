import os
import pandas as pd
import pyodbc

DB_CONFIG = {
    "driver": "ODBC Driver 17 for SQL Server",
    "server": "localhost",
    "database": "VehicleTelematicsDB",
    "trusted_connection": "yes",
}

TABLE_SOURCES = {
    "VehicleLogs": {
        "path": "data/VehicleLogs.csv",
        "columns": ["Timestamp", "VIN", "Speed", "FuelLevel", "Location", "EngineTemp"],
    },
    "Vehicle_H1": {
        "path": "fragments/horizontal/H1_VIN_A.csv",
        "columns": ["Timestamp", "VIN", "Speed", "FuelLevel", "Location", "EngineTemp"],
    },
    "Vehicle_H2": {
        "path": "fragments/horizontal/H2_VIN_B.csv",
        "columns": ["Timestamp", "VIN", "Speed", "FuelLevel", "Location", "EngineTemp"],
    },
    "Vehicle_H3": {
        "path": "fragments/horizontal/H3_VIN_C.csv",
        "columns": ["Timestamp", "VIN", "Speed", "FuelLevel", "Location", "EngineTemp"],
    },
    "Vehicle_H4": {
        "path": "fragments/horizontal/H4_VIN_D.csv",
        "columns": ["Timestamp", "VIN", "Speed", "FuelLevel", "Location", "EngineTemp"],
    },
    "Vehicle_Operational": {
        "path": "fragments/vertical/V_Operational.csv",
        "columns": ["Timestamp", "VIN", "Speed", "FuelLevel", "Location"],
    },
    "Vehicle_Diagnostic": {
        "path": "fragments/vertical/V_Diagnostic.csv",
        "columns": ["Timestamp", "VIN", "EngineTemp"],
    },
}

DELETE_TABLES = list(TABLE_SOURCES.keys())


def build_connection_string(config):
    return (
        f"DRIVER={{{config['driver']}}};"
        f"SERVER={config['server']};"
        f"DATABASE={config['database']};"
        f"Trusted_Connection={config['trusted_connection']};"
    )


def read_csv_data(path, columns):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File không tồn tại: {path}")
    df = pd.read_csv(path, usecols=columns)
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Thiếu cột trong file {path}: {missing}")
    return df[columns]


def insert_rows(cursor, table, columns, rows):
    placeholders = ", ".join(["?" for _ in columns])
    column_list = ", ".join(columns)
    sql = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"
    cursor.executemany(sql, rows)


def main():
    connection_string = build_connection_string(DB_CONFIG)
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.fast_executemany = True

    print("Kết nối SQL Server thành công.")

    print("Xóa dữ liệu cũ...")
    for table in DELETE_TABLES:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    print("Đã xóa dữ liệu cũ khỏi các bảng.")

    for table, meta in TABLE_SOURCES.items():
        path = meta["path"]
        columns = meta["columns"]
        df = read_csv_data(path, columns)
        rows = list(df.itertuples(index=False, name=None))
        insert_rows(cursor, table, columns, rows)
        conn.commit()
        print(f"Đã import {table}: {len(rows)} bản ghi từ {path}")

    conn.close()
    print("Hoàn thành import dữ liệu vào SQL Server.")


if __name__ == "__main__":
    main()
