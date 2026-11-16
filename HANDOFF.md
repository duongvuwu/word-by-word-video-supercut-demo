# Bàn giao demo Phase 1

## Đã có

- [Demo MP4](phase1-demo/demo.mp4), [manifest](phase1-demo/manifest.json), [renderer Python](phase1-demo/render.py) và [các đoạn nguồn](phase1-demo/sources/). Renderer dùng FFmpeg để cắt từ theo timestamp gán tay, ghép thành bốn câu với 18 mục trong manifest và giữ tốc độ lời nói gốc.
- Audio AAC stereo 48 kHz dài **7.145 giây**. Video H.264 1080p gồm **214 khung ở 30 fps**. Lệnh trong [README của demo](phase1-demo/README.md) đã tái tạo MP4 trùng SHA-256. README cũng ghi nguồn, giấy phép CC BY-SA 3.0, biên từng từ và mốc nối.
- Câu thoại hiện tại: “Where are you heading next? To meet my companion today. Shall we go? Yes, our train leaves soon.”

## Khi chỉnh tiếp

- Dùng bản này làm mốc. Nghe và xem cả bốn câu để kiểm tra độ rõ, nhịp và đồng bộ hình tiếng. Ưu tiên “are/you” ở 0.410–0.780 s, “To/meet” ở 2.165 s, đổi giọng ở 3.735 s và “leaves” ở 6.400–6.555 s.
- Khoảng nghỉ “go/Yes” ở 5.055–5.365 s dùng 310 ms âm nền nguồn sau khi bỏ đoạn có tiếng lách tách đo được. Nghe lại khoảng này khi chỉnh nhịp.
- Ghi từ hoặc mối nối cụ thể cùng mốc giây trước khi đổi manifest. Trường hợp lệch hình tiếng khoảng 60 ms chưa tái hiện. Nếu gặp lại, lưu media, manifest, lệnh chạy và các mốc A/V đo được để đối chiếu.
- Phase 1 dùng timestamp thủ công. ASR và tìm từ tự động là bước phát triển sau. Xem [AGENTS.md](AGENTS.md) để biết cách kiểm tra và bàn giao thay đổi.
