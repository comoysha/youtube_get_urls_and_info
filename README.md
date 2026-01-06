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

## 脚本：auto_fetch_subtitles.py

自动抓取多个频道的最新视频字幕。

示例：

```bash
# 抓取 channels.txt 中所有频道的最新 10 个视频字幕
python3 auto_fetch_subtitles.py

# 自定义抓取数量
python3 auto_fetch_subtitles.py --limit 20

# 增量模式：只下载新的视频字幕，跳过已下载的
python3 auto_fetch_subtitles.py --incremental
```

参数：

- `--channels`：频道列表文件（默认：`channels.txt`）
- `--limit`：每个频道抓取的最新视频数量（默认：10）
- `--csv-dir`：CSV 文件输出目录（默认：`youtube_dump`）
- `--srt-dir`：字幕文件基础目录（默认：`youtube_subtitles`）
- `--incremental`：只下载新视频，跳过已下载的字幕

目录结构：
```
youtube_subtitles/
├── 20vc/
│   └── srt/
├── joerogan/
│   └── srt/
└── a16z/
    └── srt/
```

## 脚本：srt_to_markdown.py

将 SRT 字幕文件转换为可读的 Markdown 格式。

示例：

```bash
# 转换特定频道的所有字幕
python3 srt_to_markdown.py --channel 20vcFund

# 转换所有频道的字幕
python3 srt_to_markdown.py

# 不包含时间戳
python3 srt_to_markdown.py --channel 20vcFund --no-timestamps
```

参数：

- `--channel`：指定频道名称（如：20vcFund、joerogan、a16z）
- `--base-dir`：字幕基础目录（默认：`youtube_subtitles`）
- `--no-timestamps`：移除输出中的时间戳

转换后目录结构：
```
youtube_subtitles/
├── 20vc/
│   ├── srt/
│   └── md/
├── joerogan/
│   ├── srt/
│   └── md/
└── a16z/
    ├── srt/
    └── md/
```

## 说明

- 如果频道 URL 不包含 `@handle`，导出会报错，建议使用带 handle 的新式 URL。
- 下载与字幕提取由 `yt-dlp` 完成。
- 网络问题可能需要配置代理或检查网络连接。
