# Hướng dẫn làm việc với repo

- Đọc [HANDOFF.md](HANDOFF.md) để nắm tiến độ và [hướng dẫn demo](phase1-demo/README.md) để biết cách chạy lại. Xác nhận Git root và xem diff hiện tại trước khi sửa.
- `phase1-demo/` chứa renderer, manifest, ba đoạn nguồn và MP4 mẫu. Dùng đường dẫn tương đối từ manifest để người khác có thể chạy sau khi clone. Giữ ghi công và giấy phép nguồn khi xuất lại.
- Khi sửa điểm cắt, dùng microsecond nguyên trong khoảng nửa mở `[start_us, end_us)` tính từ `ffprobe format.start_time`. `audio_stream_index` là chỉ số stream tuyệt đối. Khi sửa renderer, giữ offset giữa các stream và kiểm tra biên audio theo mẫu, biên video theo khung hình.
- Chạy `git diff --check` trước khi bàn giao. Khi sửa renderer hoặc manifest, chạy lại theo README vào một tệp mới và đối chiếu kết quả. So SHA-256 khi mục tiêu là tái tạo cùng đầu ra với cùng nguồn và môi trường.
- Khi cập nhật MP4, ghi rõ manifest, lệnh tái tạo và các đoạn cần nghe hoặc xem. Cập nhật `HANDOFF.md` bằng kết quả đã xác minh và bước tiếp theo.
