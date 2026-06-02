import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=VehicleTelematicsDB;"
    "Trusted_Connection=yes;"
)

print("Kết nối thành công!")

conn.close()