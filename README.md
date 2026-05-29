<<<<<<< HEAD
# DOANCSDLPT
=======
# Hệ Thống Xác Thực Tái Tạo Dữ Liệu Viễn Thông Xe (Vehicle Telemetry)

Hệ thống mô phỏng quá trình phân mảnh dữ liệu (Data Fragmentation) và xác thực kịch bản tái cấu trúc không mất mát thông tin (Lossless Join/Reconstruction) đối với dữ liệu nhật ký hành trình xe thông minh.

## 1. Kiến Trúc Phân Mảnh Dữ Liệu
Hệ thống tự động sinh ra một tập dữ liệu gốc gồm **10.000 bản ghi** (nhật ký xe) với 6 thuộc tính: `Timestamp`, `VIN`, `Speed`, `FuelLevel`, `Location`, `EngineTemp`. Sau đó, dữ liệu được phân rã theo hai mô hình phân tán:

* **Phân mảnh ngang (Horizontal Partitioning):** Chia dữ liệu thành 4 phân đoạn từ `H1` đến `H4` (mỗi phân đoạn 2.500 dòng) dựa trên phạm vi mã định danh xe (`VIN`).
* **Phân mảnh dọc (Vertical Partitioning):** Chia nhỏ các phân đoạn ngang thành 2 nhóm thuộc tính:
    * **V1 (Operational Data - Dữ liệu vận hành):** Gồm `Timestamp`, `VIN`, `Speed`, `FuelLevel`, `Location`.
    * **V2 (Diagnostic Data - Dữ liệu chẩn đoán):** Gồm `Timestamp`, `VIN`, `EngineTemp`.
    * *Lưu ý:* Cả hai phân đoạn dọc đều giữ lại cặp thuộc tính khóa `(Timestamp, VIN)` để làm cơ sở thực hiện phép toán kết hợp.

---

## 2. Kịch Bản Thử Nghiệm Lỗi & Tái Cấu Trúc
Để minh chứng khả năng giám sát tính toàn vẹn dữ liệu, kịch bản thực hiện:
1.  Xóa ngẫu nhiên **5 dòng** dữ liệu trong phân đoạn `H2` để tạo ra tệp lỗi `H2_damaged.csv`.
2.  Chạy **Trình xác thực tái cấu trúc (Reconstruction Script)**:
    * Thực hiện phép **Hợp ngang (Horizontal Union):** $H1 \cup H2\_damaged \cup H3 \cup H4$.
    * Thực hiện phép **Kết dọc (Vertical Natural Join):** $V1 \bowtie V2$ dựa trên cặp khóa chính `(Timestamp, VIN)`.
3.  **Kết quả đầu ra:** Hệ thống so khớp tự động với tập dữ liệu gốc ban đầu, phát hiện điều kiện kết nối bị tổn thất (**Lossless Join Check: FAIL**) và trích xuất chính xác danh sách, vị trí của 5 bản ghi bị thiếu hụt.

---

## 3. Cấu Trúc Thư Mục Đầu Ra (Output)
Sau khi thực thi tệp tin `vehicle_telemetry_final.py`, hệ thống tự động khởi tạo thư mục `output/` chứa 14 tệp tin CSV phục vụ kiểm thử:
* `full_dataset.csv`: Tập dữ liệu 10.000 dòng nguyên bản.
* `H1.csv`, `H2.csv`, `H3.csv`, `H4.csv`: Các phân đoạn ngang chuẩn (chưa bị can thiệp).
* `H2_damaged.csv`: Phân đoạn ngang H2 bị khuyết 5 bản ghi ngẫu nhiên.
* `Hx_V1_operational.csv`: Các phân đoạn dọc chứa thông số vận hành thời gian thực ($x \in [1, 4]$).
* `Hx_V2_diagnostic.csv`: Các phân đoạn dọc chứa thông số nhiệt độ động cơ phục vụ chẩn đoán ($x \in [1, 4]$).

---

## 4. Hướng Dẫn Triển Khai Trên VS Code

### Điều kiện tiên quyết
* Máy tính đã cài đặt **Python 3.x**.
* Đã cài đặt **Visual Studio Code (VS Code)**.

### Các bước thực hiện
1.  Mở thư mục chứa tệp `vehicle_telemetry_final.py` bằng phần mềm VS Code.
2.  Mở cửa sổ Terminal trong VS Code bằng tổ hợp phím: `Ctrl + \`` (hoặc `Cmd + \`` nếu dùng macOS).
3.  Khởi chạy kịch bản Python bằng cách nhập lệnh sau và nhấn `Enter`:
    ```bash
    python vehicle_telemetry_final.py
    ```
4.  Sau khi màn hình Terminal hiển thị bảng báo cáo phân tích chi tiết và danh sách 5 dòng bị lỗi, hãy kiểm tra thư mục `output/` vừa được sinh ra để xem toàn bộ các file dữ liệu phân mảnh dạng `.csv`.
>>>>>>> 3065f15 (update)
