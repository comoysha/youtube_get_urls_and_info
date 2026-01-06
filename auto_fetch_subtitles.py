#!/usr/bin/env python3
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def read_channels(channel_file: str) -> list[str]:
    channels = []
    with open(channel_file, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url and not url.startswith("#"):
                channels.append(url)
    return channels


def extract_handle(channel_url: str) -> str:
    if "search_query=20vc" in channel_url:
        return "20vc"
    match = re.search(r"@([^/?#]+)", channel_url)
    if match:
        return match.group(1)
    return "unknown"


def get_channel_videos(channel_url: str, limit: int, csv_dir: str, incremental: bool = False) -> str:
    handle = extract_handle(channel_url)
    csv_path = os.path.join(csv_dir, f"{handle}.csv")
    
    # 设置代理环境变量
    env = os.environ.copy()
    env['https_proxy'] = 'http://127.0.0.1:7897'
    env['http_proxy'] = 'http://127.0.0.1:7897'
    env['all_proxy'] = 'socks5://127.0.0.1:7897'
    
    cmd = [
        sys.executable,
        "download_youtube_channel_list.py",
        "--channel-url", channel_url,
        "--limit", str(limit),
        "--output", csv_path,
        "--append"  # 默认使用追加模式
    ]
    
    if incremental:
        cmd.append("--incremental")
    
    subprocess.run(cmd, check=True, env=env)
    return csv_path


def download_srt_files(csv_path: str, srt_base_dir: str) -> None:
    channel_name = Path(csv_path).stem
    srt_dir = os.path.join(srt_base_dir, channel_name, "srt")
    
    # 设置代理环境变量
    env = os.environ.copy()
    env['https_proxy'] = 'http://127.0.0.1:7897'
    env['http_proxy'] = 'http://127.0.0.1:7897'
    env['all_proxy'] = 'socks5://127.0.0.1:7897'
    
    # 创建临时脚本来下载 SRT（只下载新的）
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(f'''#!/usr/bin/env python3
import csv
import subprocess
import os
import glob

csv_path = "{csv_path}"
srt_dir = "{srt_dir}"
os.makedirs(srt_dir, exist_ok=True)

# 获取已存在的视频ID
existing_videos = set()
for srt_file in glob.glob(os.path.join(srt_dir, "*.srt")):
    # 从文件名提取视频ID，例如: "Video Title [videoId].en.srt"
    filename = os.path.basename(srt_file)
    if "[" in filename and "]" in filename:
        video_id = filename.split("[")[1].split("]")[0]
        existing_videos.add(video_id)

urls = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        url = row.get("webpage_url", "").strip()
        if url:
            # 提取视频ID
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
                if video_id not in existing_videos:
                    urls.append(url)

for url in urls:
    try:
        cmd = [
            "yt-dlp",
            "--proxy", "http://127.0.0.1:7897",
            "--write-subs", 
            "--write-auto-subs",
            "--sub-format", "srt",
            "--skip-download",
            "--paths", f"subtitle:{{srt_dir}}",
            url
        ]
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        pass
''')
        temp_script = f.name
    
    try:
        subprocess.run([sys.executable, temp_script], check=True, env=env)
    finally:
        os.unlink(temp_script)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automatically fetch latest video subtitles from YouTube channels."
    )
    parser.add_argument(
        "--channels",
        default="channels.txt",
        help="File containing YouTube channel URLs (one per line).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of latest videos to fetch from each channel.",
    )
    parser.add_argument(
        "--csv-dir",
        default="youtube_dump",
        help="Directory to save channel CSV files.",
    )
    parser.add_argument(
        "--srt-dir",
        default="youtube_subtitles",
        help="Base directory for SRT subtitle files.",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only download new videos not already downloaded.",
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.channels):
        print(f"Error: Channels file not found: {args.channels}", file=sys.stderr)
        return 1
    
    os.makedirs(args.csv_dir, exist_ok=True)
    os.makedirs(args.srt_dir, exist_ok=True)
    
    channels = read_channels(args.channels)
    if not channels:
        print("No channels found in channels file.", file=sys.stderr)
        return 1
    
    for channel_url in channels:
        try:
            print(f"\nProcessing channel: {channel_url}")
            csv_path = get_channel_videos(channel_url, args.limit, args.csv_dir, args.incremental)
            download_srt_files(csv_path, args.srt_dir)
            print(f"✓ Completed: {extract_handle(channel_url)}")
        except subprocess.CalledProcessError as exc:
            print(f"✗ Failed: {channel_url} (exit {exc.returncode})", file=sys.stderr)
    
    print(f"\n✓ All subtitles saved to: {args.srt_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())