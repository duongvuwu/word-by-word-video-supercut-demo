# Word-by-Word Video Supercut · Demo Phase 1

Demo ghép 18 từ từ hai video thành bốn câu thoại, giữ tốc độ lời nói gốc.

> Where are you heading next? To meet my companion today. Shall we go? Yes, our train leaves soon.

[Tải demo.mp4](demo.mp4) · [Xem manifest](manifest.json) · [Xem renderer](render.py)

Video H.264 1080p, 214 khung hình ở 30 fps. Audio AAC stereo 48 kHz, dài 7.145 giây.
Bản demo đã qua kiểm tra kỹ thuật. Khi tinh chỉnh, nghe lại các biên “are/you”,
“To/meet”, khoảng nghỉ “go/Yes” (5.055–5.365 s) và từ “leaves” (6.400–6.555 s).

## Chạy lại

Chuẩn bị Python 3.11 trở lên và FFmpeg 8 trở lên có `libx264`, kèm `ffprobe`,
trên `PATH`. Bản xuất trong repo được tạo với Python 3.12.9 và FFmpeg 9.0.2.
Từ thư mục gốc của repo, chạy trong PowerShell:

```powershell
Set-Location -LiteralPath phase1-demo
$run = Join-Path (Get-Location) ('.work/rerun-' + [Guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Force -Path $run
$env:TMP = $run
$env:TEMP = $run
$env:TMPDIR = $run
python -B .\render.py .\manifest.json (Join-Path $run 'rendered.mp4')
if ($LASTEXITCODE -ne 0) { throw 'Render failed' }
ffmpeg -hide_banner -nostdin -xerror -v error -n -i (Join-Path $run "rendered.mp4") -map 0:v:0 -map 0:a:0 -c copy -video_track_timescale 30000 -movie_timescale 30000 -metadata 'title=Phase 1 real-dialogue demo' -metadata 'artist=Valkaama Team / Tim Baumann; Wikimedia Foundation (speaker: Jimmy Wales)' -metadata 'copyright=Adaptation: CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/' -metadata 'comment=Valkaama — Valkaama Team / Tim Baumann. Source and license evidence: https://www.valkaama.com/index.php?l=en&page=valkaama. Download: https://www.valkaama.com/media/movie/Valkaama%28music-MichaelGeorgi%29.avi. CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/ | WalesAnniversaryAddress (Jimmy Wales 10th anniversary of Wikipedia address) — Wikimedia Foundation (speaker: Jimmy Wales). Source and license evidence: https://commons.wikimedia.org/wiki/File:WalesAnniversaryAddress.ogv. Download: https://upload.wikimedia.org/wikipedia/commons/b/b2/WalesAnniversaryAddress.ogv. CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/ | Changes: selected short excerpts, cut and assembled one clip per word; added 6 ms audio fades, mastered loudness and resampled to 48 kHz stereo; scaled/padded to 1920x1080 and converted video cadence to 30 fps. Speech at original speed. | Adaptation: CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/' -movflags +faststart (Join-Path $run "demo.mp4")
if ($LASTEXITCODE -ne 0) { throw 'Attribution remux failed' }
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $run 'demo.mp4')
```

## Nguồn và giấy phép

The adaptation is licensed [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Changes: selected short excerpts, cut and assembled one clip per word; added 6 ms audio fades, mastered loudness and resampled to 48 kHz stereo; scaled/padded to 1920x1080 and converted video cadence to 30 fps. Speech at original speed.

- **Valkaama**, Valkaama Team / Tim Baumann, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). [Source and license evidence](https://www.valkaama.com/index.php?l=en&page=valkaama) · [Original download](https://www.valkaama.com/media/movie/Valkaama%28music-MichaelGeorgi%29.avi).
- **WalesAnniversaryAddress (Jimmy Wales 10th anniversary of Wikipedia address)**, Wikimedia Foundation (speaker: Jimmy Wales), [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). [Source and license evidence](https://commons.wikimedia.org/wiki/File:WalesAnniversaryAddress.ogv) · [Original download](https://upload.wikimedia.org/wikipedia/commons/b/b2/WalesAnniversaryAddress.ogv).

Các đoạn nguồn được trích để tái tạo demo và có trong [sources/](sources/).
Wikimedia Commons ghi chú nhãn hiệu trong video nguồn. Ghi công không hàm ý
Wikimedia Foundation hoặc các tác giả bảo trợ bản demo.

## Mốc cắt và điểm nối

Each row is one clip. Input times use the local excerpt clock, with `format.start_time=0.000000` for all three files. Source and output intervals are start-inclusive and end-exclusive. Each output stop is the next word's audio join, except the last row, which marks the end. Sample and frame columns show cumulative boundaries as start–stop.

| # | Sentence | Word | Excerpt | Audio index | Source µs start–stop | Output audio s start–stop | 48 kHz samples | 30 fps frames |
|---:|---|---|---|---:|---:|---:|---:|---:|
| 1 | s1 | Where | `Valkaama_traveler_excerpt.mp4` | 1 | 23670000–24080000 | 0.000000–0.410000 | 0–19680 | 0–12 |
| 2 | s1 | are | `Valkaama_traveler_excerpt.mp4` | 1 | 24080000–24250000 | 0.410000–0.580000 | 19680–27840 | 12–17 |
| 3 | s1 | you | `Valkaama_traveler_excerpt.mp4` | 1 | 24250000–24450000 | 0.580000–0.780000 | 27840–37440 | 17–23 |
| 4 | s1 | heading | `Valkaama_traveler_excerpt.mp4` | 1 | 24450000–24870000 | 0.780000–1.200000 | 37440–57600 | 23–36 |
| 5 | s1 | next? | `Valkaama_traveler_excerpt.mp4` | 1 | 24870000–25570000 | 1.200000–1.900000 | 57600–91200 | 36–57 |
| 6 | s2 | To | `Valkaama_traveler_excerpt.mp4` | 1 | 31390000–31655000 | 1.900000–2.165000 | 91200–103920 | 57–65 |
| 7 | s2 | meet | `Valkaama_traveler_excerpt.mp4` | 1 | 31655000–32050000 | 2.165000–2.560000 | 103920–122880 | 65–77 |
| 8 | s2 | my | `Valkaama_traveler_excerpt.mp4` | 1 | 32050000–32365000 | 2.560000–2.875000 | 122880–138000 | 77–86 |
| 9 | s2 | companion | `Valkaama_traveler_excerpt.mp4` | 1 | 32365000–33225000 | 2.875000–3.735000 | 138000–179280 | 86–112 |
| 10 | s2 | today. | `WalesAnniversary_excerpt.mp4` | 1 | 22055000–22800000 | 3.735000–4.480000 | 179280–215040 | 112–134 |
| 11 | s3 | Shall | `Valkaama_train_excerpt.mp4` | 1 | 22665000–22785000 | 4.480000–4.600000 | 215040–220800 | 134–138 |
| 12 | s3 | we | `Valkaama_train_excerpt.mp4` | 1 | 22785000–22995000 | 4.600000–4.810000 | 220800–230880 | 138–144 |
| 13 | s3 | go? | `Valkaama_train_excerpt.mp4` | 1 | 22995000–23325000 | 4.810000–5.140000 | 230880–246720 | 144–154 |
| 14 | s4 | Yes, | `Valkaama_train_excerpt.mp4` | 1 | 24795000–25335000 | 5.140000–5.680000 | 246720–272640 | 154–170 |
| 15 | s4 | our | `Valkaama_train_excerpt.mp4` | 1 | 25335000–25630000 | 5.680000–5.975000 | 272640–286800 | 170–179 |
| 16 | s4 | train | `Valkaama_train_excerpt.mp4` | 1 | 25630000–26055000 | 5.975000–6.400000 | 286800–307200 | 179–192 |
| 17 | s4 | leaves | `Valkaama_train_excerpt.mp4` | 1 | 26055000–26210000 | 6.400000–6.555000 | 307200–314640 | 192–197 |
| 18 | s4 | soon. | `Valkaama_train_excerpt.mp4` | 1 | 26210000–26800000 | 6.555000–7.145000 | 314640–342960 | 197–214 |

## Sentence pauses

Estimated room tone spans use source measurements. The third pause crosses the clip 13/14 join at 5.140 s. The audio joins use the exact cut plan above.

| Pause | Source local s | Output audio s | Sample span | Length |
|---|---:|---:|---:|---:|
| s1 next? | 25.270–25.570 | 1.600–1.900 | 76800–91200 | 300 ms |
| s2 today. | 22.510–22.800 | 4.190–4.480 | 201120–215040 | 290 ms |
| s3 go? | 23.240–23.325 | 5.055–5.140 | 242640–246720 | 85 ms |
| Before s4 “Yes” | 24.795–25.020 | 5.140–5.365 | 246720–257520 | 225 ms |
| s4 soon. | 26.570–26.800 | 6.915–7.145 | 331920–342960 | 230 ms |

## SHA-256

| Tệp | SHA-256 |
|---|---|
| `demo.mp4` | `0eefcc514117af81e0539a9378e045f90db13cdf92d3236623f42571ab2cb836` |
| `manifest.json` | `c4342b7e708897b1463d1f1acf14fcf0e2d7509b33fa5a722fa7b32bbfe9b32b` |
| `render.py` | `40c2674ab7f6d02fdefb5c21228fe4965d28a947c7a8136ac51c64cd98376561` |
| `sources/Valkaama_traveler_excerpt.mp4` | `723324e5d1e8f4017b66b365e2c038e70e67d0a1f553547dda1eda97fb4a6b49` |
| `sources/Valkaama_train_excerpt.mp4` | `d8d17b67d7628f35b4b808aaa91e950c50c3b9d489455a5a615c08ff0816dfdc` |
| `sources/WalesAnniversary_excerpt.mp4` | `3827ce9a838a168b5628d53efae63b429aadedab29a80301ce416127043ba568` |
