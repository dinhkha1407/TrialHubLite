# HƯỚNG DẪN DEPLOY APP LÊN STREAMLIT COMMUNITY CLOUD 🚀

Tài liệu này hướng dẫn chi tiết cách đưa ứng dụng **TrialHub Lite** lên internet miễn phí bằng Streamlit Cloud.

---

## BƯỚC 1: CHUẨN BỊ FILE (Đã làm tự động cho bạn)

Tôi đã tạo sẵn các file cần thiết trong thư mục dự án của bạn:
1.  `requirements.txt`: Chứa danh sách các thư viện cần cài đặt (`streamlit`, `pandas`, `openpyxl`, `pytz`).
2.  `.gitignore`: Cấu hình để Git bỏ qua các file rác, nhưng **giữ lại** `trialhub.db` để có dữ liệu ban đầu.
3.  `README.md`: Giới thiệu dự án.

**Lưu ý về Database (`trialhub.db`):**
-   File database này sẽ được đẩy lên GitHub.
-   Khi deploy, Streamlit Cloud sẽ tải nó về và sử dụng.
-   **QUAN TRỌNG**: Vì Streamlit Cloud là *Ephemeral* (tạm thời), sau 1 thời gian không sử dụng hoặc khi app reboot, các thay đổi mới trên database *trên Cloud* có thể bị reset về trạng thái ban đầu của file `trialhub.db` trên GitHub.
-   **Giải pháp cho Lite App**: Chúng ta vẫn dùng SQLite cho đơn giản, nhưng hãy nhớ thường xuyên dùng chức năng **"Backup DB"** trên app để tải dữ liệu về máy.

---

## BƯỚC 2: ĐẨY CODE LÊN GITHUB

Bạn cần có tài khoản GitHub. Nếu chưa có, hãy đăng ký tại [github.com](https://github.com/).

### Cách 1: Dùng Github Desktop (Dễ nhất)
1.  Tải và cài đặt **GitHub Desktop**.
2.  Mở GitHub Desktop -> Chọn **File** -> **Add local repository**.
3.  Trỏ đường dẫn đến thư mục `e:\TrialHubLite\TrialHubLite`.
4.  Nhấn **Add repository**.
5.  Nó sẽ hỏi "This directory does not appear to be a Git repository", chọn **Create a repository**.
6.  Điền tên (ví dụ: `TrialHub-Lite`), nhấn **Create repository**.
7.  Nhấn **Publish repository** trên thanh công cụ.
8.  Chọn "Keep this code private" (nếu muốn bảo mật) hoặc bỏ chọn (công khai).
9.  Nhấn **Publish**.

### Cách 2: Dùng Git Bash hoặc Terminal (Rất tốt)
Mở **Git Bash** tại thư mục dự án (Chuột phải > Git Bash Here) và chạy:
```bash
git init
git add .
git commit -m "First commit - TrialHub Lite ready for deploy"
# Tạo repo mới trên github.com rồi copy đường dẫn https://...
git branch -M main
git remote add origin <LINK_REPO_CUA_BAN>
git push -u origin main
```

---

## BƯỚC 3: DEPLOY TRÊN STREAMLIT CLOUD

1.  Truy cập [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng tài khoản GitHub.
2.  Nhấn nút **"New app"** (hoặc "Create app").
3.  Điền thông tin:
    -   **Repository**: Chọn repo bạn vừa tạo (ví dụ: `TrialHub-Lite`).
    -   **Branch**: `main` (mặc định).
    -   **Main file path**: `streamlit_app.py`.
4.  Nhấn nút **"Deploy!"**.
5.  Chờ khoảng 1-2 phút để hệ thống cài đặt thư viện (`requirements.txt`) và khởi động app.
6.  🎉 **Hoàn tất!** Bạn sẽ nhận được một đường link dạng `https://trialhub-lite-xyz.streamlit.app` để gửi cho mọi người.

---

## CẬP NHẬT APP & TÍNH NĂNG MỚI (BONUS)

Sau khi deploy, mỗi khi bạn muốn sửa code hoặc thêm tính năng:

1.  **Sửa code trên máy tính** (Local).
2.  **Test thử**: Chạy `streamlit run streamlit_app.py` để đảm bảo không lỗi.
3.  **Đẩy code lên GitHub**:
    -   Mở GitHub Desktop.
    -   Review các file thay đổi.
    -   Nhập mô tả (Summary) ví dụ: "Thêm màu cho nút bấm".
    -   Nhấn **Commit to main**.
    -   Nhấn **Push origin**.
4.  **Tự động cập nhật**:
    -   Streamlit Cloud sẽ tự động phát hiện code mới và update app của bạn trong vòng 30-60 giây. Không cần làm gì thêm!

---

## XỬ LÝ SỰ CỐ THƯỜNG GẶP

### 1. Lỗi "ModuleNotFoundError"
-   **Nguyên nhân**: Thiếu tên thư viện trong `requirements.txt`.
-   **Sửa**: Thêm tên thư viện (ví dụ `matplotlib`) vào file `requirements.txt`, commit và push lên GitHub.

### 2. Dữ liệu nhập trên Cloud bị mất sau khi App Reboot
-   **Nguyên nhân**: Đặc tính của Streamlit Community Cloud (không lưu file vĩnh viễn).
-   **Sửa**:
    1.  Dùng nút **Backup DB** trong Sidebar cuối ngày làm việc.
    2.  Nếu muốn dữ liệu bền bỉ vĩnh viễn trên Cloud miễn phí, cần kết nối Google Sheets (phức tạp hơn, cần dùng `st.secrets`). Với bản **Lite** này, việc Backup thủ công là giải pháp đơn giản nhất.
