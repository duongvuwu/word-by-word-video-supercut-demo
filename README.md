# Word-by-Word Video Supercut

Dựng câu thoại mới bằng cách cắt từng từ từ video nguồn rồi ghép theo thứ tự trong manifest. Bản Phase 1 dùng timestamp gán tay và giữ tốc độ lời nói gốc.

> Where are you heading next? To meet my companion today. Shall we go? Yes, our train leaves soon.

[Mở demo MP4](phase1-demo/demo.mp4) · [Xem manifest](phase1-demo/manifest.json) · [Nguồn và giấy phép](phase1-demo/README.md#nguồn-và-giấy-phép)

Demo gồm 18 từ lấy từ hai video. Đầu ra H.264 1080p30 và AAC stereo 48 kHz, với 7.145 giây audio.

## Dựng thử trên máy

Cần Python 3.11 trở lên và FFmpeg 8 trở lên có `libx264`, kèm `ffprobe` trên `PATH`. Repo đã có các đoạn nguồn để chạy demo.

Sau khi clone, chạy từ thư mục gốc của repo trong PowerShell:

```powershell
Set-Location -LiteralPath phase1-demo
$run = New-Item -ItemType Directory -Force -Path (Join-Path '.work' ('quickstart-' + [Guid]::NewGuid().ToString('N')))
$env:TMP = $run.FullName
$env:TEMP = $run.FullName
$env:TMPDIR = $run.FullName
python -B .\render.py .\manifest.json (Join-Path $run.FullName 'rendered.mp4')
if ($LASTEXITCODE -ne 0) { throw 'Render failed' }
```

Lệnh tạo một MP4 thử trong `phase1-demo/.work/`. Để tái tạo đúng tệp demo, dùng [lệnh xuất kèm metadata ghi công và kiểm tra SHA-256](phase1-demo/README.md#chạy-lại).

## Đọc tiếp

| Tệp | Dùng khi |
|---|---|
| [HANDOFF.md](HANDOFF.md) | Xem tiến độ, các mốc cần nghe lại và việc tiếp theo. |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Hiểu pipeline, thay video nguồn hoặc sửa mốc cắt và kiểm tra bản xuất. |
| [AGENTS.md](AGENTS.md) | Xem quy ước sửa, kiểm tra và bàn giao. |
| [phase1-demo/README.md](phase1-demo/README.md) | Xem các điểm cắt, nguồn, giấy phép và cách tái tạo demo. |
