import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from decimal import Decimal, DecimalException
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FPS = 30
RATE = 48_000
US = 1_000_000
PCM = ['-f', 's16le', '-ar', str(RATE), '-ac', '2']
LOCAL_MEDIA = ['-protocol_whitelist', 'file', '-format_whitelist', 'mov,matroska,avi']


def run(tool, *args):
    local = ROOT / '.tools' / f'{tool}.exe'
    executable = local if local.is_file() else shutil.which(tool)
    if executable is None:
        raise ValueError(f'{tool} is required. Put it on PATH or in {ROOT / ".tools"}.')
    command = [str(executable), '-hide_banner']
    if tool == 'ffmpeg':
        command += ['-nostdin', '-xerror']
    result = subprocess.run([*command, *args], capture_output=True,
                            encoding='utf-8', errors='replace')
    if result.returncode:
        raise ValueError(f'{tool}: {result.stderr.strip() or result.returncode}')
    return result


def probe(path):
    return json.loads(run('ffprobe', '-v', 'error', *LOCAL_MEDIA, '-show_format',
                          '-show_streams', '-of', 'json', str(path)).stdout)


def project_path(path):
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise ValueError(f'Path must be inside the project: {path}')
    return resolved


def load_clips(manifest):
    data = json.loads(manifest.read_text(encoding='utf-8-sig'))
    clips = data.get('clips') if isinstance(data, dict) else None
    if not isinstance(clips, list) or not clips:
        raise ValueError('Manifest must contain a non-empty clips list.')

    sources = {}
    for number, clip in enumerate(clips, 1):
        try:
            path = project_path(manifest.parent / Path(clip['source']))
            audio, start, end = (clip[key] for key in ('audio_stream_index', 'start_us', 'end_us'))
            if any(type(value) is not int for value in (audio, start, end)):
                raise ValueError('audio_stream_index, start_us and end_us must be integers.')
            if not 0 <= start < end:
                raise ValueError(f'Expected 0 <= start_us < end_us, got {start} and {end}.')
            if not path.is_file():
                raise ValueError(f'Source file does not exist: {path}')
            if path not in sources:
                metadata = probe(path)
                streams = metadata['streams']
                video = next((s['index'] for s in streams if s['codec_type'] == 'video'
                              and not s.get('disposition', {}).get('attached_pic')), None)
                tracks = {s['index'] for s in streams if s['codec_type'] == 'audio'}
                try:
                    duration = Decimal(metadata['format']['duration'])
                    # Matroska reports the timeline endpoint; MP4 reports elapsed duration.
                    if 'matroska' in metadata['format']['format_name'].split(','):
                        duration -= Decimal(metadata['format'].get('start_time', '0'))
                    duration = int(duration * US)
                except (KeyError, DecimalException, OverflowError, ValueError):
                    raise ValueError('Source duration is unavailable.') from None
                sources[path] = video, tracks, duration
            video, tracks, duration = sources[path]
            if end > duration:
                raise ValueError(f'end_us {end} exceeds source duration_us {duration}.')
            if video is None:
                raise ValueError('Source has no playable video stream.')
            if audio not in tracks:
                raise ValueError(f'Stream {audio} is not audio. Available audio indices: {sorted(tracks)}.')
        except (KeyError, TypeError, ValueError, OSError) as error:
            raise ValueError(f'Clip {number}: {error}') from error
        yield path, video, audio, start, end


def seconds(us):
    return f'{us // US}.{us % US:06d}'


def ticks(us, rate):
    return (us * rate + US // 2) // US


def cut_clip(clip, video_path, audio_path, frames, samples):
    path, video, audio, start, end = clip
    duration = end - start
    fade = min(ticks(6_000, RATE), samples // 2)
    # Keep both streams on the seek-relative clock so a delayed track stays delayed.
    video_filter = (f'trim=end={seconds(duration)},fps={FPS}:start_time=0:eof_action=pass,'
                    'scale=1920:1080:force_original_aspect_ratio=decrease:'
                    'force_divisible_by=2:reset_sar=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,'
                    'format=yuv420p,tpad=stop_mode=clone:stop=-1')
    audio_filter = (f'atrim=end={seconds(duration)},aresample={RATE}:async=1:first_pts=0,'
                    f'aformat=channel_layouts=stereo,apad=whole_len={samples},'
                    f'atrim=end_sample={samples},afade=t=in:ns={fade},'
                    f'afade=t=out:ss={samples - fade}:ns={fade}')
    run('ffmpeg', '-v', 'error', '-abort_on', 'empty_output_stream', *LOCAL_MEDIA,
        '-ss', seconds(start), '-t', seconds(duration + 100_000), '-i', str(path),
        '-map', f'0:{video}', '-vf', video_filter, '-frames:v', str(frames),
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
        '-video_track_timescale', '30000', '-movie_timescale', '30000', str(video_path),
        '-map', f'0:{audio}', '-af', audio_filter, *PCM, '-c:a', 'pcm_s16le', str(audio_path))
    if audio_path.stat().st_size != samples * 4:
        raise ValueError('Decoded audio does not match the planned sample count.')


def mastering_filter(audio_path, samples):
    target = 'loudnorm=I=-16:TP=-1.5:LRA=11'
    if samples >= RATE * 4 // 10:
        log = run('ffmpeg', '-v', 'info', *PCM, '-i', str(audio_path),
                  '-af', f'{target}:print_format=json', '-f', 'null', '-').stderr
        start, end = log.rfind('{'), log.rfind('}')
        if 0 <= start < end:
            stats = json.loads(log[start:end + 1])
            metrics = [stats[name] for name in
                       ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')]
            if all(math.isfinite(float(value)) for value in metrics):
                keys = ('measured_I', 'measured_TP', 'measured_LRA', 'measured_thresh', 'offset')
                return target + ':linear=true:' + ':'.join(f'{k}={v}' for k, v in zip(keys, metrics))
    return 'aresample=192000,alimiter=limit=0.7943:level=0:latency=1'


def verify(path, frames, samples):
    streams = probe(path)['streams']
    video = next((s for s in streams if s['codec_type'] == 'video'), {})
    audio = next((s for s in streams if s['codec_type'] == 'audio'), {})
    if (video.get('codec_name'), video.get('nb_frames'), video.get('width'),
            video.get('height'), video.get('pix_fmt'), video.get('sample_aspect_ratio'),
            video.get('avg_frame_rate')) != ('h264', str(frames), 1920, 1080, 'yuv420p', '1:1', '30/1'):
        raise ValueError('Output video does not match the preset or planned frame count.')
    if (audio.get('codec_name'), audio.get('sample_rate'), audio.get('channels')) != ('aac', str(RATE), 2):
        raise ValueError('Output audio does not match the AAC stereo 48 kHz preset.')
    for stream, target in ((video, Fraction(frames, FPS)), (audio, Fraction(samples, RATE))):
        duration = stream['duration_ts'] * Fraction(stream['time_base'])
        if abs(duration - target) > Fraction(1, 1000) or abs(Fraction(stream['start_time'])) > Fraction(1, 1000):
            raise ValueError(f'Output {stream["codec_type"]} timing differs from the plan.')
    run('ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-')


def render(clips, output):
    elapsed = frames = samples = 0
    with tempfile.TemporaryDirectory(prefix='.render-', dir=output.parent) as directory:
        work = Path(directory)
        pcm = work / 'timeline.pcm'
        playlist = []
        with pcm.open('wb') as combined:
            for number, clip in enumerate(clips, 1):
                elapsed += clip[4] - clip[3]
                next_frames, next_samples = ticks(elapsed, FPS), ticks(elapsed, RATE)
                part = work / f'{number}.mp4'
                audio_part = work / 'part.pcm'
                try:
                    if next_frames == frames:
                        raise ValueError('The interval is too short to allocate a frame at 30 fps.')
                    cut_clip(clip, part, audio_part, next_frames - frames, next_samples - samples)
                    with audio_part.open('rb') as decoded:
                        shutil.copyfileobj(decoded, combined)
                    audio_part.unlink()
                except (OSError, ValueError) as error:
                    raise ValueError(f'Clip {number}: {error}') from error
                # Difference of rounded boundaries keeps concat rounding from accumulating.
                duration = (next_frames * US + FPS // 2) // FPS - (frames * US + FPS // 2) // FPS
                playlist.extend((f"file '{part.name}'", f'duration {seconds(duration)}'))
                frames, samples = next_frames, next_samples
        listing = work / 'video.ffconcat'
        listing.write_text('\n'.join(playlist) + '\n', encoding='ascii')
        temporary = work / 'output.mp4'
        master = mastering_filter(pcm, samples)
        # Dynamic loudnorm can jump in PTS. The assembled PCM sample count defines the clock.
        audio_filter = (f'{master},aresample={RATE},apad=whole_len={samples},'
                        f'atrim=end_sample={samples},asettb=1/{RATE},asetpts=N')
        run('ffmpeg', '-v', 'error', '-f', 'concat', '-safe', '1', '-i', str(listing),
            *PCM, '-i', str(pcm), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
            '-video_track_timescale', '30000', '-movie_timescale', '30000',
            '-af', audio_filter,
            '-c:a', 'aac', '-b:a', '192k', '-ar', str(RATE), '-ac', '2',
            '-movflags', '+faststart', str(temporary))
        verify(temporary, frames, samples)
        if os.name == 'nt':
            temporary.rename(output)  # Windows rename refuses an existing destination.
        else:
            os.link(temporary, output)
    print(f'{output} ({len(clips)} clips, {frames} frames, {seconds(elapsed)} s of cuts)')


def main():
    parser = argparse.ArgumentParser(description='Render an ordered manifest of video cuts to MP4.')
    parser.add_argument('manifest', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError(f'Output already exists: {args.output}')
        output = project_path(args.output)
        if output.suffix.lower() != '.mp4' or not output.parent.is_dir():
            raise ValueError('Output must be an .mp4 path in an existing project folder.')
        render(list(load_clips(project_path(args.manifest))), output)
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
