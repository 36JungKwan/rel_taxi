# AI Taxi Driver

Ứng dụng Streamlit mô phỏng bài toán Taxi MDP với môi trường 5x5, chướng ngại vật, và hành khách cần được đón/trả.

## Yêu cầu

- Python 3.9+
- streamlit
- numpy
- pandas

## Cài đặt

1. Tạo môi trường ảo (khuyến nghị):

```bash
python -m venv .venv
```

2. Kích hoạt môi trường:

- Windows PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- Windows CMD:
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

3. Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
streamlit run rel_taxi.py
```

## Mô tả

- Tab `🔬 Phân Tích Bộ Não AI` hiển thị giá trị và chính sách tối ưu của thuật toán Value Iteration.
- Tab `🎮 Chơi Trực Tiếp (Tài Xế Thực Tập)` cho phép bạn điều khiển taxi và so sánh với hành vi AI.

## Ghi chú

- Ứng dụng sử dụng `st.cache_data` để giảm thời gian tính toán khi thay đổi hệ số suy giảm gamma.
- Nếu muốn thay đổi gameplay, bạn có thể chỉnh sửa file `rel_taxi.py`.
