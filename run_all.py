"""
RUN_ALL.PY – Chạy toàn bộ pipeline từ đầu đến cuối
══════════════════════════════════════════════════════
  Bước 1: Sinh dữ liệu VehicleLogs (10.000 dòng)
  Bước 2: Phân mảnh ngang (H1–H4) + dọc (V_Op, V_Diag)
  Bước 3: Mô phỏng mất dữ liệu (xóa 5 dòng khỏi H2)
  Bước 4: Tái cấu trúc & kiểm tra Lossless Join/Union
══════════════════════════════════════════════════════
"""

import subprocess
import sys
import time

STEPS = [
    ("step1_generate_data.py",    "Sinh dữ liệu VehicleLogs"),
    ("step2_fragment.py",         "Phân mảnh ngang + dọc"),
    ("step3_simulate_deletion.py","Mô phỏng xóa 5 dòng"),
    ("step4_reconstruct_validate.py", "Tái cấu trúc & kiểm tra"),
]

def run_step(script, description, idx):
    print(f"\n{'━'*60}")
    print(f"  BƯỚC {idx}: {description}")
    print(f"  Script: {script}")
    print(f"{'━'*60}")
    t0 = time.time()
    result = subprocess.run([sys.executable, script], capture_output=False)
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n❌ LỖI ở bước {idx}! Dừng lại.")
        sys.exit(1)
    print(f"\n  ⏱  Hoàn thành trong {elapsed:.2f}s")

def main():
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  RECONSTRUCTION VALIDATOR – VEHICLE TELEMATICS          ║")
    print("║  Đề tài thi: Cơ Sở Dữ Liệu Phân Tán                   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    for i, (script, desc) in enumerate(STEPS, 1):
        run_step(script, desc, i)
    
    print(f"\n{'═'*60}")
    print("  ✅ HOÀN THÀNH TOÀN BỘ PIPELINE")
    print(f"{'═'*60}")
    print("\n  📁 Kết quả:")
    print("     data/VehicleLogs.csv              ← Bảng gốc 10.000 dòng")
    print("     fragments/horizontal/H1–H4*.csv   ← 4 mảnh ngang")
    print("     fragments/vertical/V_*.csv        ← 2 mảnh dọc")
    print("     fragments/horizontal/*CORRUPTED*  ← Mảnh H2 bị hỏng")
    print("     data/deleted_rows_log.csv         ← Log 5 dòng bị xóa")
    print("     reports/reports/reconstruction_report.txt ← Báo cáo tái cấu trúc")

if __name__ == "__main__":
    main()
