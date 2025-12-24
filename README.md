# YouTube 链接与字幕工具

用于导出频道视频列表到 CSV，并根据 CSV 中的 YouTube URL 下载 SRT 字幕的脚本。

## 依赖

- Python 3.10+
- PATH 中可用的 yt-dlp

## 脚本：download_youtube_channel_list.py

抓取频道视频列表并写入 CSV。

默认输出：`youtube_dump/<handle>.csv`，其中 `<handle>` 为频道 URL 中 `@` 后面的字符串。

示例：

```bash
python3 download_youtube_channel_list.py \
  --channel-url "https://www.youtube.com/@joerogan/videos" \
  --limit 50
```

参数：

- `--channel-url`（必填）：频道视频页 URL
- `--limit`：最多抓取数量
- `--append`：追加写入并避免重复 URL
- `--output`：自定义 CSV 路径（可选）

CSV 字段：

- title
- duration
- upload_date
- view_count
- webpage_url

## 脚本：download_youtube_srt_from_csv.py

根据 CSV 中的 URL 下载 SRT 字幕（可选同时下载视频）。

CSV 输入格式：

- 每行一个 URL
- 空行会被忽略
- 以 `#` 开头的行会被当作注释

示例：

```bash
python3 download_youtube_srt_from_csv.py \
  --csv youtube_url.csv \
  --srt-dir download_srt
```

参数：

- `--csv`：输入 CSV 路径（默认：`youtube_url.csv`）
- `--srt-dir`：SRT 输出目录
- `--video-dir`：视频输出目录
- `--with-video`：同时下载视频

## 说明

- 如果频道 URL 不包含 `@handle`，导出会报错，建议使用带 handle 的新式 URL。
- 下载与字幕提取由 `yt-dlp` 完成。
