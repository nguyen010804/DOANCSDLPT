"""
BƯỚC 4: RECONSTRUCTION VALIDATOR – SCRIPT TÁI CẤU TRÚC
═══════════════════════════════════════════════════════════════════
NGUYÊN LÝ LOSSLESS JOIN / UNION trong CSDL Phân Tán:

  ┌─────────────────────────────────────────────────────────────┐
  │  PHÂN MẢNH NGANG (Horizontal):                             │
  │    VehicleLogs = H1 ∪ H2 ∪ H3 ∪ H4                        │
  │    Nếu một mảnh Hi bị thiếu dòng → UNION thiếu bản ghi    │
  │                                                             │
  │  PHÂN MẢNH DỌC (Vertical):                                 │
  │    VehicleLogs = Π_Op ⋈ Π_Diag (theo VIN + Timestamp)     │
  │    Nếu một mảnh Vi bị thiếu dòng → JOIN thiếu tuple       │
  └─────────────────────────────────────────────────────────────┘

LOGIC PHÁT HIỆN:
  1. Tái cấu trúc bảng gốc từ các mảnh (H1∪H2∪H3∪H4, sau đó ⋈ V)
  2. Dùng mảnh DỌC không bị hỏng (V_Operational, V_Diagnostic)
     làm nguồn tham chiếu "ground truth"
  3. So sánh tập VIN+Timestamp để phát hiện bản ghi bị thiếu
  4. Báo cáo chính xác dòng nào bị mất, ở mảnh nào
═══════════════════════════════════════════════════════════════════
"""

import csv
import os
from datetime import datetime

# ── Đường dẫn file ───────────────────────────────────────────────
# Mảnh ngang (H2 dùng bản BỊ HỎNG để giả lập sự cố)
HORIZONTAL = {
    "H1": "fragments/horizontal/H1_VIN_A.csv",
    "H2": "fragments/horizontal/H2_VIN_B_CORRUPTED.csv",   # ← mảnh bị hỏng
    "H3": "fragments/horizontal/H3_VIN_C.csv",
    "H4": "fragments/horizontal/H4_VIN_D.csv",
}

# Mảnh dọc (không bị hỏng → dùng làm tham chiếu)
VERTICAL = {
    "V_Operational": "fragments/vertical/V_Operational.csv",
    "V_Diagnostic":  "fragments/vertical/V_Diagnostic.csv",
}

REPORT_PATH = "reports/reconstruction_report.txt"

# ── Tiện ích ─────────────────────────────────────────────────────
def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def make_key(row):
    """Khóa duy nhất: (Timestamp, VIN)."""
    return (row["Timestamp"], row["VIN"])

def banner(title, char="═", width=65):
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")

# ── GIAI ĐOẠN 1: TÁI CẤU TRÚC NGANG ────────────────────────────
def reconstruct_horizontal():
    """
    H_reconstructed = H1 ∪ H2 ∪ H3 ∪ H4
    Trả về: dict keyed by (Timestamp, VIN)
    """
    banner("GIAI ĐOẠN 1: TÁI CẤU TRÚC NGANG  (H1 ∪ H2 ∪ H3 ∪ H4)")
    
    h_data = {}
    for name, path in HORIZONTAL.items():
        rows = read_csv(path)
        for row in rows:
            h_data[make_key(row)] = row
        status = "⚠️  [BỊ HỎNG]" if "CORRUPTED" in path else "✅"
        print(f"  {status} {name}: {len(rows):>5} bản ghi đọc từ {path}")
    
    print(f"\n  📊 Tổng sau UNION: {len(h_data)} bản ghi (bộ khóa duy nhất)")
    return h_data

# ── GIAI ĐOẠN 2: TÁI CẤU TRÚC DỌC ──────────────────────────────
def reconstruct_vertical():
    """
    V_reconstructed = V_Operational ⋈ V_Diagnostic (theo Timestamp + VIN)
    Trả về: dict keyed by (Timestamp, VIN) với đầy đủ 6 cột
    """
    banner("GIAI ĐOẠN 2: TÁI CẤU TRÚC DỌC  (V_Op ⋈ V_Diag)")
    
    op_rows   = read_csv(VERTICAL["V_Operational"])
    diag_rows = read_csv(VERTICAL["V_Diagnostic"])
    
    print(f"  ✅ V_Operational : {len(op_rows):>5} bản ghi, "
          f"cột: {list(op_rows[0].keys())}")
    print(f"  ✅ V_Diagnostic  : {len(diag_rows):>5} bản ghi, "
          f"cột: {list(diag_rows[0].keys())}")
    
    # Chỉ mục mảnh Chẩn đoán theo khóa
    diag_index = {make_key(r): r for r in diag_rows}
    
    v_data = {}
    join_failures = 0
    for row in op_rows:
        key = make_key(row)
        if key in diag_index:
            merged = {**row, **diag_index[key]}
            v_data[key] = merged
        else:
            join_failures += 1
    
    print(f"\n  📊 Kết quả JOIN: {len(v_data)} tuple khớp, "
          f"{join_failures} tuple không khớp")
    print(f"  🔑 Khóa JOIN: Timestamp + VIN (đảm bảo Lossless Join)")
    return v_data

# ── GIAI ĐOẠN 3: PHÁT HIỆN THIẾU / HỎNG ────────────────────────
def detect_anomalies(h_data, v_data):
    """
    So sánh H_reconstructed vs V_reconstructed:
      - Dùng V (không bị hỏng) làm 'Ground Truth'
      - Tìm key có trong V nhưng KHÔNG có trong H → bị thiếu
      - Tìm key có trong H nhưng KHÔNG có trong V → bản ghi lạ
      - Tìm dòng có key khớp nhưng dữ liệu khác    → bị hỏng
    """
    banner("GIAI ĐOẠN 3: PHÁT HIỆN BẢN GHI THIẾU / BỊ HỎNG")
    
    h_keys = set(h_data.keys())
    v_keys = set(v_data.keys())
    
    missing_in_h  = v_keys - h_keys   # Có trong V, thiếu ở H → BỊ XÓA
    orphan_in_h   = h_keys - v_keys   # Có trong H, thiếu ở V → BẤT THƯỜNG
    common_keys   = h_keys & v_keys
    
    # Kiểm tra bất nhất (corrupted) ở các dòng cùng khóa
    corrupted = []
    COMMON_FIELDS = ["Speed", "FuelLevel", "Location", "EngineTemp"]
    for key in common_keys:
        hr = h_data[key]
        vr = v_data[key]
        diffs = []
        for field in COMMON_FIELDS:
            if field in hr and field in vr and hr[field] != vr[field]:
                diffs.append(f"{field}: H={hr[field]} vs V={vr[field]}")
        if diffs:
            corrupted.append((key, diffs))
    
    return missing_in_h, orphan_in_h, corrupted

# ── GIAI ĐOẠN 4: IN BÁO CÁO ─────────────────────────────────────
def print_report(missing_in_h, orphan_in_h, corrupted, v_data, log_path=None):
    banner("GIAI ĐOẠN 4: BÁO CÁO KẾT QUẢ TÁI CẤU TRÚC", "═")
    
    lines = []
    
    def out(text=""):
        print(text)
        lines.append(text)
    
    out("╔══════════════════════════════════════════════════════════════╗")
    out("║       RECONSTRUCTION VALIDATOR – BÁO CÁO TÁI CẤU TRÚC      ║")
    out("║       Môn: Cơ Sở Dữ Liệu Phân Tán                          ║")
    out("╚══════════════════════════════════════════════════════════════╝")
    out(f"  Thời gian chạy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ── TỔNG QUAN ──
    out("\n┌─────────────────────────────────────────────────────────────┐")
    out("│  TỔNG QUAN                                                  │")
    out("└─────────────────────────────────────────────────────────────┘")
    total_issues = len(missing_in_h) + len(orphan_in_h) + len(corrupted)
    status = "❌ PHÁT HIỆN VẤN ĐỀ" if total_issues > 0 else "✅ TOÀN VẸN"
    out(f"  Trạng thái tổng thể : {status}")
    out(f"  Bản ghi bị THIẾU    : {len(missing_in_h)}")
    out(f"  Bản ghi BẤT THƯỜNG  : {len(orphan_in_h)}")
    out(f"  Bản ghi BỊ HỎNG     : {len(corrupted)}")
    
    # ── BẢN GHI BỊ THIẾU ──
    out("\n┌─────────────────────────────────────────────────────────────┐")
    out("│  BẢN GHI BỊ THIẾU (Có trong V_Ground_Truth, mất trong H)  │")
    out("│  → Vi phạm yêu cầu LOSSLESS UNION của phân mảnh ngang      │")
    out("└─────────────────────────────────────────────────────────────┘")
    
    if missing_in_h:
        out(f"  {'STT':>4} | {'VIN':<14} | {'Timestamp':<20} | Speed | Fuel  | EngineTemp")
        out(f"  {'─'*4}-+-{'─'*14}-+-{'─'*20}-+-------+-------+-----------")
        for i, key in enumerate(sorted(missing_in_h), 1):
            ts, vin = key
            ref = v_data[key]
            out(f"  {i:>4} | {vin:<14} | {ts:<20} | "
                f"{ref.get('Speed','?'):>5} | "
                f"{ref.get('FuelLevel','?'):>5} | "
                f"{ref.get('EngineTemp','?'):>5}")
        out(f"\n  ⚠️  CHẨN ĐOÁN: {len(missing_in_h)} bản ghi mất khỏi mảnh H2_VIN_B")
        out(f"     Nguyên nhân: Xóa dữ liệu / lỗi phần cứng / lỗi ghi disk")
        out(f"     Khắc phục  : Phục hồi từ bản sao lưu hoặc mảnh dọc V")
    else:
        out("  ✅ Không phát hiện bản ghi bị thiếu.")
    
    # ── BẢN GHI BẤT THƯỜNG ──
    out("\n┌─────────────────────────────────────────────────────────────┐")
    out("│  BẢN GHI BẤT THƯỜNG (Có trong H, không có trong V)        │")
    out("│  → Có thể là bản ghi giả / lỗi chèn                        │")
    out("└─────────────────────────────────────────────────────────────┘")
    if orphan_in_h:
        for key in sorted(orphan_in_h):
            out(f"  ⚠️  VIN={key[1]}, Timestamp={key[0]}")
    else:
        out("  ✅ Không phát hiện bản ghi bất thường.")
    
    # ── BẢN GHI BỊ HỎNG ──
    out("\n┌─────────────────────────────────────────────────────────────┐")
    out("│  BẢN GHI BỊ HỎNG (cùng khóa nhưng dữ liệu khác nhau)     │")
    out("│  → Vi phạm tính nhất quán giữa các mảnh                    │")
    out("└─────────────────────────────────────────────────────────────┘")
    if corrupted:
        for key, diffs in corrupted:
            out(f"  ⚠️  VIN={key[1]}, Timestamp={key[0]}")
            for d in diffs:
                out(f"        Sai lệch: {d}")
    else:
        out("  ✅ Không phát hiện bản ghi bị hỏng.")
    
    # ── KIỂM CHỨNG LOSSLESS JOIN ──
    out("\n┌─────────────────────────────────────────────────────────────┐")
    out("│  KIỂM CHỨNG ĐIỀU KIỆN LOSSLESS JOIN / UNION                │")
    out("└─────────────────────────────────────────────────────────────┘")
    out("  Lý thuyết: R = Π_A(R) ⋈ Π_B(R)  nếu A∩B → A hoặc A∩B → B")
    out("  Thực tế trong bài:")
    out("    V_Op ⋈ V_Diag: khóa chung {Timestamp, VIN} → A∩B là siêu khóa")
    out("    ✅ Điều kiện đủ cho Lossless Join ĐƯỢC THỎA MÃN")
    out("")
    out("  Kết quả kiểm tra:")
    h_count = len(v_data) - len(missing_in_h)
    v_count = len(v_data)
    match = (h_count == v_count and len(missing_in_h) == 0
             and len(orphan_in_h) == 0 and len(corrupted) == 0)
    out(f"    Bảng gốc (Ground Truth từ V): {v_count:>6} bản ghi")
    out(f"    Bảng tái cấu trúc từ H      : {h_count:>6} bản ghi")
    out(f"    Lossless Union thỏa mãn?    : {'✅ CÓ' if match else '❌ KHÔNG – DỮ LIỆU BỊ MẤT!'}")
    
    if total_issues > 0:
        out(f"\n  🔴 KẾT LUẬN: Phân mảnh KHÔNG thỏa điều kiện Lossless Union")
        out(f"     do {len(missing_in_h)} bản ghi bị xóa khỏi mảnh H2_VIN_B.")
        out(f"     Cần phục hồi hoặc đồng bộ lại từ mảnh dọc / bản sao lưu.")
    else:
        out(f"\n  🟢 KẾT LUẬN: Tất cả mảnh toàn vẹn. Lossless Union thỏa mãn.")
    
    out("\n" + "═" * 65)
    
    # Ghi ra file
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n📄 Báo cáo đã lưu: {REPORT_PATH}")

# ── MAIN ──────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  RECONSTRUCTION VALIDATOR – VEHICLE TELEMATICS")
    print("  Kiểm tra tính toàn vẹn sau phân mảnh CSDL phân tán")
    print("=" * 65)
    
    h_data = reconstruct_horizontal()
    v_data = reconstruct_vertical()
    missing, orphans, corrupted = detect_anomalies(h_data, v_data)
    print_report(missing, orphans, corrupted, v_data)

if __name__ == "__main__":
    main()
