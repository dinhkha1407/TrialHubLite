# TrialHub Lite 🚀

Ứng dụng quản lý lịch Trial cho MindX (Phiên bản Lite).

## Tính năng

- **Dashboard**: Thống kê số lượng trial, trạng thái, tỷ lệ chuyển đổi.
- **Danh sách Trial**: Xem, tìm kiếm, lọc và chỉnh sửa trực tiếp dữ liệu trial.
- **Thêm Trial mới**: Form nhập liệu nhanh chóng.
- **Import/Export**: Nhập dữ liệu từ Excel/CSV và xuất báo cáo.
- **Database**: Sử dụng SQLite (`trialhub.db`) để lưu trữ dữ liệu bền vững.

## Cài đặt và Chạy (Local)

1.  Cài đặt thư viện:
    ```bash
    pip install -r requirements.txt
    ```

2.  Chạy ứng dụng:
    ```bash
    streamlit run streamlit_app.py
    ```

## Deploy lên Streamlit Cloud

1.  Push code lên Github.
2.  Truy cập [share.streamlit.io](https://share.streamlit.io).
3.  Chọn "New app" -> Chọn repo -> Chọn file `streamlit_app.py`.
4.  Nhấn "Deploy".
