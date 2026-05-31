# 🚗 Vehicle Telematics – Reconstruction Validator

Mô phỏng hệ thống **cơ sở dữ liệu phân tán** cho nhật ký xe hơi.  
Script tự động phân mảnh dữ liệu, giả lập sự cố mất dữ liệu, rồi chạy kịch bản tái tạo để xác định **chính xác bản ghi nào bị thiếu**.

---

## Yêu cầu

- Python 3.7+
- Không cần cài thêm thư viện nào

---

## Cách chạy

```bash
python vehicle_telemetry_final.py
```

Kết quả tự động lưu vào thư mục `output/` được tạo cùng thư mục.

---

## Tập dữ liệu

Bảng `VehicleLogs` — **10.000 dòng × 6 cột**, mỗi dòng là 1 lần ghi nhật ký xe cách nhau 1 phút.

| Cột | Kiểu | Mô tả |
|-----|------|-------|
| `Timestamp` | DATETIME | Thời điểm ghi (từ 2024-01-01, cách nhau 1 phút) |
| `VIN` | VARCHAR(10) | Số nhận dạng xe — khóa chính |
| `Speed` | INT (0–180) | Tốc độ (km/h) |
| `FuelLevel` | FLOAT (5–100) | Nhiên liệu còn lại (%) |
| `Location` | VARCHAR | Thành phố ghi nhật ký |
| `EngineTemp` | INT (70–130) | Nhiệt độ động cơ (°C) |

---

## Cách phân mảnh

### Phân mảnh ngang — chia theo hàng (VIN range)

Bảng được chia thành **4 mảnh bằng nhau**, mỗi mảnh 2.500 dòng, lưu trên 1 nút riêng:

```
H1.csv  →  VIN #00001 – #02500   (Node 1)
H2.csv  →  VIN #02501 – #05000   (Node 2)  ← nút bị mô phỏng sự cố
H3.csv  →  VIN #05001 – #07500   (Node 3)
H4.csv  →  VIN #07501 – #10000   (Node 4)
```

Điều kiện tái tạo: `VehicleLogs = H1 ∪ H2 ∪ H3 ∪ H4`

### Phân mảnh dọc — chia theo cột

Mỗi mảnh ngang tiếp tục được chia thành 2 nhóm cột theo mục đích sử dụng:

```
Hx_V1_operational.csv  →  Timestamp, VIN, Speed, FuelLevel, Location
Hx_V2_diagnostic.csv   →  Timestamp, VIN, EngineTemp
```

Cả V1 và V2 đều giữ `(Timestamp, VIN)` làm khóa nối.  
Điều kiện tái tạo: `Hx = V1 ⋈(Timestamp, VIN) V2`

---

## Kịch bản tái tạo

Script xóa ngẫu nhiên **5 dòng từ mảnh H2** để mô phỏng sự cố, sau đó chạy 4 bài kiểm tra:

**Bài 1 — UNION ngang**
```
H1 ∪ H2_damaged ∪ H3 ∪ H4 = 9.995 dòng  ≠  10.000  →  THẤT BẠI
```

**Bài 2 — Phát hiện bản ghi thiếu**  
Dùng phép trừ tập hợp trên khóa `(Timestamp, VIN)` để tìm đúng 5 bản ghi bị mất, in ra toàn bộ thông tin.

```python
merged_keys = {(r["Timestamp"], r["VIN"]) for r in merged}
missing     = [r for r in original if (r["Timestamp"], r["VIN"]) not in merged_keys]
```

**Bài 3 — JOIN dọc V1 ⋈ V2**
```
V1_damaged ⋈ V2_damaged = 2.495 dòng  ≠  2.500  →  THẤT BẠI
```

**Bài 4 — Kiểm tra mảnh nguyên vẹn**
```
H1: JOIN = 2.500 / 2.500  →  THÀNH CÔNG
H3: JOIN = 2.500 / 2.500  →  THÀNH CÔNG
H4: JOIN = 2.500 / 2.500  →  THÀNH CÔNG
```

---

## Kết quả mẫu khi chạy

```
══════════════════════════════════════════════════════════════
  BÁO CÁO TỔNG KẾT – Lossless Join / Union
══════════════════════════════════════════════════════════════
  [✗ THẤT BẠI]   UNION ngang   H1 ∪ H2 ∪ H3 ∪ H4
  [✗ THẤT BẠI]   JOIN dọc      V1 ⋈ V2  (H2)
  [✗ THẤT BẠI]   Số bản ghi đầy đủ (= 10.000)
  [✓ THÀNH CÔNG] H1 / H3 / H4 nguyên vẹn

  KẾT LUẬN: Lossless Join/Union → KHÔNG THỎA MÃN
  Đoạn bị hỏng : H2
  Số dòng mất  : 5

  HƯỚNG PHỤC HỒI:
    1. Khôi phục H2.csv từ bản sao lưu (backup)
    2. Phát lại redo-log để tái tạo lại 5 bản ghi bị mất
══════════════════════════════════════════════════════════════
```

---

## Cấu trúc output/

```
output/
├── VehicleLogs_original.csv          ← Dữ liệu gốc 10.000 dòng
├── H1.csv / H2.csv / H3.csv / H4.csv ← 4 mảnh ngang
├── H2_damaged.csv                    ← H2 sau khi mất 5 dòng
├── H1_V1_operational.csv             ← Mảnh dọc: vận hành
├── H1_V2_diagnostic.csv              ← Mảnh dọc: chẩn đoán
└── ... (tương tự cho H2, H3, H4)
```

---

## Lý thuyết áp dụng

Đề tài triển khai trực tiếp lý thuyết từ **Özsu & Valduriez – Principles of Distributed Database Systems (3rd ed.)**:

- **§4.2** Phân mảnh ngang — chia theo VIN range, thỏa mãn tính đầy đủ, tái tạo, rời nhau
- **§4.3** Phân mảnh dọc — chia theo ái lực thuộc tính, khóa chính được nhân bản
- **§4.1.2** Lossless Join — điều kiện cốt lõi bị vi phạm khi mất dữ liệu

---

*Môn học: Cơ Sở Dữ Liệu Phân Tán | Đề tài #7 | 2025*
