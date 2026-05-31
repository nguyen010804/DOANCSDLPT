# 🚗 Trình Kiểm Tra Tái Tạo – Hệ Thống Viễn Thông Xe

> **Đề tài #7 – Reconstruction Validator: "Vehicle Telematics"**  
> Môn học: Cơ Sở Dữ Liệu Phân Tán | Học viện CNBCVT

---

## Mục lục

- [Đề tài làm gì?](#đề-tài-làm-gì)
- [Yêu cầu](#yêu-cầu)
- [Cách chạy](#cách-chạy)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Lược đồ dữ liệu](#lược-đồ-dữ-liệu)
- [Chiến lược phân mảnh](#chiến-lược-phân-mảnh)
- [Kịch bản tái tạo](#kịch-bản-tái-tạo)
- [Kết quả mẫu](#kết-quả-mẫu)
- [Cơ sở lý thuyết](#cơ-sở-lý-thuyết)

---

## Đề tài làm gì?

Hệ thống mô phỏng một **cơ sở dữ liệu phân tán** lưu trữ nhật ký xe hơi. Tập dữ liệu 10.000 bản ghi được **phân mảnh** và lưu trên nhiều nút ảo. Khi một nút bị mất dữ liệu, script tự động phát hiện **chính xác những bản ghi nào bị thiếu**.

**Giải thích đơn giản:**

```
Dữ liệu 10.000 xe  →  Chia thành 4 tập nhỏ (theo số VIN)
                    →  Mỗi tập lại chia 2 theo loại cột
                    →  Xóa 5 dòng bất kỳ trong 1 tập
                    →  Ráp lại và kiểm tra: thiếu dòng nào?
```

---

## Yêu cầu

- **Python 3.7+**
- **Không cần cài thêm thư viện** — chỉ dùng thư viện chuẩn Python

---

## Cách chạy

**Bước 1:** Mở terminal trong VS Code (`` Ctrl + ` ``)

**Bước 2:** Điều hướng đến thư mục chứa file

```bash
cd đường/dẫn/đến/thư/mục
```

**Bước 3:** Chạy script chính

```bash
python vehicle_telemetry_final.py
```

**Bước 4:** Xem kết quả xuất ra trong thư mục `output/`

---

## Cấu trúc thư mục

```
📁 project/
├── vehicle_telemetry_final.py       ← Script chính (chạy file này)
├── README.md                        ← File hướng dẫn này
└── 📁 output/                       ← Tự động tạo sau khi chạy
    ├── VehicleLogs_original.csv     ← Tập dữ liệu gốc (10.000 dòng)
    ├── H1.csv                       ← Mảnh ngang 1: VIN #1 – #2.500
    ├── H2.csv                       ← Mảnh ngang 2: VIN #2.501 – #5.000
    ├── H2_damaged.csv               ← H2 sau khi xóa 5 dòng (mô phỏng sự cố)
    ├── H3.csv                       ← Mảnh ngang 3: VIN #5.001 – #7.500
    ├── H4.csv                       ← Mảnh ngang 4: VIN #7.501 – #10.000
    ├── H1_V1_operational.csv        ← Mảnh dọc: dữ liệu vận hành của H1
    ├── H1_V2_diagnostic.csv         ← Mảnh dọc: dữ liệu chẩn đoán của H1
    ├── H2_V1_operational.csv
    ├── H2_V2_diagnostic.csv
    ├── H3_V1_operational.csv
    ├── H3_V2_diagnostic.csv
    ├── H4_V1_operational.csv
    └── H4_V2_diagnostic.csv
```

---

## Lược đồ dữ liệu

Bảng `VehicleLogs` gồm **10.000 dòng × 6 cột**, mỗi dòng là 1 lần ghi nhật ký xe cách nhau 1 phút:

| Cột | Kiểu | Miền giá trị | Mô tả |
|-----|------|--------------|-------|
| `Timestamp` | DATETIME | 2024-01-01 → 2024-07-10 | Thời điểm ghi nhật ký |
| `VIN` | VARCHAR(10) | WMI + 6 số + ký tự | Số nhận dạng xe — khóa chính |
| `Speed` | INT | 0 – 180 | Tốc độ (km/h) |
| `FuelLevel` | FLOAT | 5.0 – 100.0 | Nhiên liệu còn lại (%) |
| `Location` | VARCHAR | 10 thành phố VN | Thành phố ghi nhật ký |
| `EngineTemp` | INT | 70 – 130 | Nhiệt độ động cơ (°C) |

---

## Chiến lược phân mảnh

### Phân mảnh ngang (Horizontal Fragmentation)

Chia theo **hàng** — mỗi mảnh chứa đủ 6 cột nhưng chỉ một phần số xe:

| Mảnh | Phạm vi VIN | Số dòng | Nút mô phỏng |
|------|-------------|---------|--------------|
| H1 | #0000001 – #0002500 | 2.500 | Node 1 |
| H2 | #0002501 – #0005000 | 2.500 | Node 2 ⚠️ bị sự cố |
| H3 | #0005001 – #0007500 | 2.500 | Node 3 |
| H4 | #0007501 – #0010000 | 2.500 | Node 4 |

**Điều kiện tái tạo:** `VehicleLogs = H1 ∪ H2 ∪ H3 ∪ H4`

**3 điều kiện đúng đắn:**
- ✅ **Tính đầy đủ:** Mọi bản ghi thuộc đúng một mảnh
- ✅ **Tính tái tạo:** UNION cho lại bảng gốc
- ✅ **Tính rời nhau:** Các mảnh không chồng lấp nhau

### Phân mảnh dọc (Vertical Fragmentation)

Chia theo **cột** — mỗi mảnh chứa tất cả các hàng nhưng chỉ một số cột:

| Mảnh | Các cột | Mục đích |
|------|---------|----------|
| `Hx_V1_operational` | Timestamp, VIN, Speed, FuelLevel, Location | Giám sát vận hành thời gian thực |
| `Hx_V2_diagnostic` | Timestamp, VIN, EngineTemp | Kiểm tra sức khỏe động cơ |

> 💡 Cả V1 và V2 đều chứa `(Timestamp, VIN)` làm **khóa nối** để ghép lại.  
> **Điều kiện tái tạo:** `Hx = V1 ⋈(Timestamp,VIN) V2`

---

## Kịch bản tái tạo

Script chạy **4 bài kiểm tra** theo thứ tự:

### Bài 1 — Hợp nhất ngang (UNION)
```
H1 ∪ H2_damaged ∪ H3 ∪ H4
Kỳ vọng : 10.000 dòng
Thực tế :  9.995 dòng  →  ✗ THẤT BẠI (thiếu 5 dòng)
```

### Bài 2 — Phát hiện bản ghi thiếu
So sánh kết quả UNION với dataset gốc bằng phép trừ tập hợp trên khóa `(Timestamp, VIN)`:

```python
merged_keys = {(r["Timestamp"], r["VIN"]) for r in merged}
missing     = [r for r in original if (r["Timestamp"], r["VIN"]) not in merged_keys]
# → In ra chính xác 5 bản ghi bị thiếu với đầy đủ thông tin
```

### Bài 3 — Kết hợp dọc (JOIN V1 ⋈ V2)
```
V1_damaged ⋈(Timestamp,VIN) V2_damaged
Kỳ vọng : 2.500 dòng
Thực tế :  2.495 dòng  →  ✗ THẤT BẠI (JOIN không đầy đủ)
```

### Bài 4 — Xác minh mảnh nguyên vẹn
```
H1: JOIN = 2.500 / 2.500  →  ✓ THÀNH CÔNG
H3: JOIN = 2.500 / 2.500  →  ✓ THÀNH CÔNG
H4: JOIN = 2.500 / 2.500  →  ✓ THÀNH CÔNG
```

---

## Kết quả mẫu

```
══════════════════════════════════════════════════════════════
  BÁO CÁO TỔNG KẾT – Lossless Join / Union
══════════════════════════════════════════════════════════════
  [✗ THẤT BẠI]   UNION ngang   H1 ∪ H2 ∪ H3 ∪ H4
  [✗ THẤT BẠI]   JOIN dọc      V1 ⋈ V2  (H2)
  [✗ THẤT BẠI]   Số bản ghi đầy đủ (= 10.000)
  [✓ THÀNH CÔNG] H1 / H3 / H4 nguyên vẹn

  KẾT LUẬN: Lossless Join/Union → KHÔNG THỎA MÃN
  Đoạn bị hỏng   : H2
  Số dòng mất    : 5
  VIN bị thiếu   : JH4002995F, 1HG003370Q, 2T1004201P, ...

  HƯỚNG PHỤC HỒI:
    1. Khôi phục H2.csv từ bản sao lưu (backup)
    2. Phát lại redo-log để tái tạo lại 5 bản ghi bị mất
══════════════════════════════════════════════════════════════
```

---

## Cơ sở lý thuyết

Đề tài minh họa trực tiếp các khái niệm từ sách **Özsu & Valduriez – Principles of Distributed Database Systems (3rd ed., 2011)**:

| Khái niệm | Tham chiếu | Áp dụng trong đề tài |
|-----------|------------|----------------------|
| Phân mảnh ngang | §4.2 | Chia VehicleLogs thành H1–H4 theo VIN |
| Phân mảnh dọc | §4.3 | Chia cột thành V1 (vận hành) và V2 (chẩn đoán) |
| Lossless Join | §4.1.2 | Kiểm tra UNION và JOIN có bằng bảng gốc không |
| Tính đầy đủ | §4.1.1 | Mọi bản ghi thuộc đúng một mảnh ngang |
| Tính rời nhau | §4.1.1 | Các mảnh ngang không chồng lấp nhau |
| Mô hình sự cố | §1.3 | Xóa ngẫu nhiên 5 dòng mô phỏng hỏng dữ liệu |

---

## Thông tin nhóm

| | |
|--|--|
| **Môn học** | Cơ Sở Dữ Liệu Phân Tán |
| **Đề tài** | #7 – Reconstruction Validator: Vehicle Telematics |
| **Thành viên** | [Điền tên] – [MSSV] |
| **Ngày nộp** | Tháng 6 / 2025 |
