"""
BƯỚC 2: PHÂN MẢNH DỮ LIỆU (Fragmentation)
─────────────────────────────────────────────────────────────────
PHÂN MẢNH NGANG (Horizontal Fragmentation) – theo dải VIN:
  H1: VIN bắt đầu bằng 'VIN-A' → 2.500 bản ghi
  H2: VIN bắt đầu bằng 'VIN-B' → 2.500 bản ghi
  H3: VIN bắt đầu bằng 'VIN-C' → 2.500 bản ghi
  H4: VIN bắt đầu bằng 'VIN-D' → 2.500 bản ghi

PHÂN MẢNH DỌC (Vertical Fragmentation) – theo nhóm thuộc tính:
  V_Operational  (Dữ liệu Vận hành):  Timestamp, VIN, Speed, FuelLevel, Location
  V_Diagnostic   (Dữ liệu Chẩn đoán): Timestamp, VIN, EngineTemp

  *** Khóa chung (VIN + Timestamp) xuất hiện ở CẢ HAI mảnh dọc
      → đảm bảo điều kiện Lossless Join (kết nối không mất dữ liệu) ***
─────────────────────────────────────────────────────────────────
"""

import csv
import os

DATA_PATH = "data/VehicleLogs.csv"
H_DIR = "fragments/horizontal"
V_DIR = "fragments/vertical"

# ── Định nghĩa phân mảnh ─────────────────────────────────────────
HORIZONTAL_FRAGMENTS = {
    "H1_VIN_A": lambda vin: vin.startswith("VIN-A"),
    "H2_VIN_B": lambda vin: vin.startswith("VIN-B"),
    "H3_VIN_C": lambda vin: vin.startswith("VIN-C"),
    "H4_VIN_D": lambda vin: vin.startswith("VIN-D"),
}

VERTICAL_FRAGMENTS = {
    # Dữ liệu Vận hành – theo dõi chuyển động xe thời gian thực
    "V_Operational":  ["Timestamp", "VIN", "Speed", "FuelLevel", "Location"],
    # Dữ liệu Chẩn đoán – trạng thái kỹ thuật động cơ
    "V_Diagnostic":   ["Timestamp", "VIN", "EngineTemp"],
}

def read_csv(path):
    """Đọc toàn bộ CSV → list[dict]."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(rows, fieldnames, path):
    """Ghi list[dict] ra CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def horizontal_fragment(rows):
    """
    Phân mảnh ngang theo dải VIN.
    Điều kiện phân mảnh:
      σ(VIN LIKE 'VIN-A%') → H1
      σ(VIN LIKE 'VIN-B%') → H2
      σ(VIN LIKE 'VIN-C%') → H3
      σ(VIN LIKE 'VIN-D%') → H4

    Tính đúng đắn (Correctness):
      H1 ∪ H2 ∪ H3 ∪ H4 = VehicleLogs (Union hoàn chỉnh)
      H_i ∩ H_j = ∅ ∀ i≠j   (Không giao nhau – Disjoint)
    """
    print("\n📂 PHÂN MẢNH NGANG (Horizontal Fragmentation)")
    print("   Điều kiện: phân chia theo dải VIN (A/B/C/D)")
    print("-" * 50)

    all_fieldnames = list(rows[0].keys())
    fragment_counts = {}

    for name, condition in HORIZONTAL_FRAGMENTS.items():
        subset = [r for r in rows if condition(r["VIN"])]
        path = f"{H_DIR}/{name}.csv"
        write_csv(subset, all_fieldnames, path)
        fragment_counts[name] = len(subset)
        print(f"   ✅ {name}: {len(subset):>5} bản ghi → {path}")

    total = sum(fragment_counts.values())
    print(f"\n   📊 Tổng kiểm tra: {total} bản ghi "
          f"({'✅ KHỚP' if total == len(rows) else '❌ LỖI'} với gốc {len(rows)})")
    return fragment_counts

def vertical_fragment(rows):
    """
    Phân mảnh dọc theo nhóm thuộc tính.
    
    Điều kiện Lossless Join:
      Π_Operational(VehicleLogs) ⋈ Π_Diagnostic(VehicleLogs)
      Kết nối theo khóa chung: VIN + Timestamp
      → Kết quả phải bằng đúng VehicleLogs gốc (không thêm/mất tuple)
    
    Thuộc tính bắt buộc trong CẢ HAI mảnh: Timestamp, VIN (khóa chung)
    """
    print("\n📂 PHÂN MẢNH DỌC (Vertical Fragmentation)")
    print("   Khóa chung (join key): Timestamp + VIN")
    print("-" * 50)

    for name, fields in VERTICAL_FRAGMENTS.items():
        subset = [{k: r[k] for k in fields} for r in rows]
        path = f"{V_DIR}/{name}.csv"
        write_csv(subset, fields, path)
        print(f"   ✅ {name}: {len(subset):>5} bản ghi, cột: {fields}")
        print(f"             → {path}")

def main():
    print("=" * 60)
    print("BƯỚC 2: PHÂN MẢNH DỮ LIỆU VehicleLogs")
    print("=" * 60)

    rows = read_csv(DATA_PATH)
    print(f"📥 Đã đọc {len(rows)} bản ghi từ {DATA_PATH}")

    horizontal_fragment(rows)
    vertical_fragment(rows)

    print("\n✅ Phân mảnh hoàn tất!")
    print("   Cấu trúc thư mục:")
    print("   fragments/")
    print("   ├── horizontal/")
    for name in HORIZONTAL_FRAGMENTS:
        print(f"   │   ├── {name}.csv")
    print("   └── vertical/")
    for name in VERTICAL_FRAGMENTS:
        print(f"       ├── {name}.csv")

if __name__ == "__main__":
    main()
