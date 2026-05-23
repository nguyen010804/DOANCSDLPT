"""
BƯỚC 3: MÔ PHỎNG MẤT DỮ LIỆU
─────────────────────────────────────────────────────────────────
Xóa ngẫu nhiên 5 dòng khỏi mảnh ngang H2 (VIN-B)
để kiểm tra khả năng phát hiện của Reconstruction Script.

File bị tác động: fragments/horizontal/H2_VIN_B.csv
Kết quả lưu tại:  fragments/horizontal/H2_VIN_B_CORRUPTED.csv
Log xóa lưu tại:  data/deleted_rows_log.csv  (để đối chiếu sau)
─────────────────────────────────────────────────────────────────
"""

import csv
import random
import os

random.seed(99)  # seed cố định để kết quả có thể tái hiện

SOURCE_FRAGMENT = "fragments/horizontal/H2_VIN_B.csv"
CORRUPTED_OUTPUT = "fragments/horizontal/H2_VIN_B_CORRUPTED.csv"
DELETION_LOG    = "data/deleted_rows_log.csv"
NUM_DELETIONS   = 5

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(rows, fieldnames, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    print("=" * 60)
    print("BƯỚC 3: MÔ PHỎNG MẤT DỮ LIỆU")
    print("=" * 60)

    rows = read_csv(SOURCE_FRAGMENT)
    fieldnames = list(rows[0].keys())

    print(f"📂 Đọc mảnh: {SOURCE_FRAGMENT}")
    print(f"   Số bản ghi ban đầu: {len(rows)}")

    # Chọn ngẫu nhiên 5 chỉ số dòng cần xóa
    indices_to_delete = sorted(random.sample(range(len(rows)), NUM_DELETIONS))
    deleted_rows = [rows[i] for i in indices_to_delete]

    print(f"\n🗑️  Xóa ngẫu nhiên {NUM_DELETIONS} dòng:")
    print(f"{'Chỉ số':>8} | {'VIN':<14} | {'Timestamp':<20} | Speed | Fuel")
    print("-" * 65)
    for idx, row in zip(indices_to_delete, deleted_rows):
        print(f"   [{idx:>4}] | {row['VIN']:<14} | {row['Timestamp']:<20} | "
              f"{row['Speed']:>5} | {row['FuelLevel']:>4}")

    # Tạo bản sao bị xóa
    remaining = [r for i, r in enumerate(rows) if i not in indices_to_delete]
    write_csv(remaining, fieldnames, CORRUPTED_OUTPUT)

    # Ghi log các dòng đã xóa (để Reconstruction Script đối chiếu)
    write_csv(deleted_rows, fieldnames, DELETION_LOG)

    print(f"\n✅ Đã tạo mảnh bị hỏng:  {CORRUPTED_OUTPUT}")
    print(f"   Số bản ghi còn lại:    {len(remaining)}")
    print(f"   Số bản ghi bị xóa:     {NUM_DELETIONS}")
    print(f"📋 Log dòng đã xóa lưu tại: {DELETION_LOG}")
    print(f"\n⚠️  LƯU Ý: file log chỉ dùng để ĐỐI CHIẾU KẾT QUẢ,")
    print(f"   Script tái cấu trúc KHÔNG được đọc file này!")

if __name__ == "__main__":
    main()
