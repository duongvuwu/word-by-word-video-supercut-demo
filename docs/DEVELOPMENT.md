# Phát triển renderer

## Pipeline

1. [render.py](../phase1-demo/render.py) đọc `clips`, dùng `ffprobe` kiểm tra đường dẫn, stream và thời lượng nguồn. Thứ tự trong mảng `clips` là thứ tự ghép.
2. Với từng clip, FFmpeg cắt video và audio từ cùng mốc, giữ offset giữa các stream. Hình được co theo tỷ lệ và thêm viền cho khung 1920×1080. Tiếng được đưa về PCM stereo 48 kHz và áp fade tối đa 6 ms ở mỗi đầu.
3. Renderer làm tròn mỗi **biên thời gian tích lũy** theo mẫu audio 48 kHz và khung hình 30 fps. Số mẫu và khung của mỗi clip là hiệu của hai biên liên tiếp. Sau khi ghép, renderer chuẩn hóa âm lượng cả câu và mã hóa AAC một lần.
4. Renderer kiểm tra định dạng, thời lượng và khả năng giải mã trước khi ghi MP4 đích. Mỗi lần chạy cần một đường dẫn đầu ra mới.

## Sửa manifest

Một clip tối thiểu có dạng sau. Xem [manifest của demo](../phase1-demo/manifest.json) để biết cách ghép nhiều clip và lưu thông tin nguồn.

```json
{
  "clips": [
    {
      "word": "Where",
      "source": "sources/Valkaama_traveler_excerpt.mp4",
      "audio_stream_index": 1,
      "start_us": 23670000,
      "end_us": 24080000
    }
  ]
}
```

- Đường dẫn `source` tương đối tính từ thư mục của manifest. Renderer yêu cầu manifest, nguồn và MP4 đầu ra nằm trong `phase1-demo/`, nơi chứa `render.py`. Thư mục chứa MP4 đầu ra phải tồn tại.
- `audio_stream_index` là chỉ số tuyệt đối trong kết quả `ffprobe` và phải trỏ tới một stream audio. `word` chỉ là nhãn đọc cho người sửa.
- Mốc cắt là khoảng nửa mở `[start_us, end_us)`, tính bằng microsecond nguyên. Mốc 0 là `format.start_time` của nguồn, mặc định 0 khi thiếu. Ví dụ trên cắt 410 ms từ 23.670 đến 24.080 giây trên timeline của đoạn nguồn.
- Nếu đổi video, probe lại thay vì dùng mặc định stream 1. Giữ thông tin tác giả, nguồn và giấy phép cho đoạn mới.

Từ `phase1-demo/`, xem trường thời gian và stream của một đoạn nguồn:

```powershell
ffprobe -v error -show_entries 'format=start_time,duration:stream=index,codec_type,start_time,time_base' -of json .\sources\Valkaama_traveler_excerpt.mp4
```

## Kiểm tra và xử lý lỗi

- Dựng vào tệp mới theo [README gốc](../README.md#dựng-thử-trên-máy). Với manifest demo hiện tại, kết quả là **214 khung hình ở 30 fps** và **342.960 mẫu audio mỗi kênh ở 48 kHz**. Nếu cần đúng SHA-256 của MP4 đã lưu, dùng [lệnh tái tạo đầy đủ](../phase1-demo/README.md#chạy-lại) với cùng nguồn và phiên bản công cụ.
- Nếu báo sai stream, đối chiếu `index` và `codec_type` trong kết quả probe. Nếu báo đường dẫn nằm ngoài dự án, kiểm tra vị trí thực tế của manifest, nguồn và thư mục đầu ra. Nếu clip quá ngắn để có một khung, điều chỉnh biên rồi kiểm tra lại mối nối.
- Nghe và xem trước khi chốt điểm cắt, đặc biệt ở các biên từ và chỗ đổi nguồn. Nếu gặp lệch hình tiếng, lưu nguồn, manifest và lệnh tái hiện, rồi đo mốc A/V sau giải mã trước khi sửa renderer. Độ dài buffer AAC có thể gồm padding cuối frame.
- Nếu thay điểm cắt hoặc nguồn của demo được lưu trong repo, cập nhật MP4, ghi công, mốc cần kiểm tra và SHA-256 trong [README của demo](../phase1-demo/README.md). Ghi kết quả đã xác minh vào [HANDOFF.md](../HANDOFF.md).
