"""
BƯỚC 1: SINH DỮ LIỆU
Tạo file CSV VehicleLogs với 10.000 dòng
Cột: Timestamp, VIN, Speed, FuelLevel, Location, EngineTemp
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# Danh sách thành phố/địa điểm Việt Nam mô phỏng
LOCATIONS = [
    "10.8231,106.6297",  # Ho Chi Minh City
    "21.0285,105.8542",  # Ha Noi
    "16.0544,108.2022",  # Da Nang
    "10.0452,105.7469",  # Can Tho
    "12.2388,109.1967",  # Nha Trang
    "11.9404,108.4583",  # Da Lat
    "20.8449,106.6881",  # Hai Phong
    "10.9460,108.4419",  # Phan Thiet
]

def generate_vin(index):
    """
    Tạo VIN theo 4 dải (A, B, C, D) để phân mảnh ngang sau này:
      - H1: VIN-A0001 → VIN-A2500  (index 1–2500)
      - H2: VIN-B0001 → VIN-B2500  (index 2501–5000)
      - H3: VIN-C0001 → VIN-C2500  (index 5001–7500)
      - H4: VIN-D0001 → VIN-D2500  (index 7501–10000)
    """
    if index <= 2500:
        return f"VIN-A{index:04d}"
    elif index <= 5000:
        return f"VIN-B{(index - 2500):04d}"
    elif index <= 7500:
        return f"VIN-C{(index - 5000):04d}"
    else:
        return f"VIN-D{(index - 7500):04d}"

def generate_row(index, base_time):
    """Sinh một bản ghi log xe."""
    timestamp = base_time + timedelta(minutes=index * 3)
    vin = generate_vin(index)
    speed = round(random.uniform(0, 120), 1)          # km/h
    fuel_level = round(random.uniform(5, 100), 1)      # %
    location = random.choice(LOCATIONS)
    engine_temp = round(random.uniform(70, 110), 1)    # °C
    return [timestamp.strftime("%Y-%m-%d %H:%M:%S"), vin, speed, fuel_level, location, engine_temp]

def main():
    base_time = datetime(2024, 1, 1, 0, 0, 0)
    output_path = "data/VehicleLogs.csv"

    print("=" * 60)
    print("BƯỚC 1: SINH DỮ LIỆU VehicleLogs (10.000 dòng)")
    print("=" * 60)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "VIN", "Speed", "FuelLevel", "Location", "EngineTemp"])
        for i in range(1, 10001):
            writer.writerow(generate_row(i, base_time))

    print(f"✅ Đã tạo: {output_path}")
    print(f"   - Tổng số dòng dữ liệu: 10.000")
    print(f"   - Cột: Timestamp, VIN, Speed, FuelLevel, Location, EngineTemp")
    print(f"   - Dải VIN:")
    print(f"       H1 → VIN-A0001 đến VIN-A2500 (2.500 xe)")
    print(f"       H2 → VIN-B0001 đến VIN-B2500 (2.500 xe)")
    print(f"       H3 → VIN-C0001 đến VIN-C2500 (2.500 xe)")
    print(f"       H4 → VIN-D0001 đến VIN-D2500 (2.500 xe)")

if __name__ == "__main__":
    main()
