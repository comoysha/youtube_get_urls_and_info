#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path


def parse_srt_time(time_str: str) -> tuple[int, int, int, int]:
    """Parse SRT timestamp to hours, minutes, seconds, milliseconds."""
    match = re.match(r'(\d+):(\d+):(\d+),(\d+)', time_str.strip())
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return 0, 0, 0, 0


def format_timestamp(hours: int, minutes: int, seconds: int, milliseconds: int) -> str:
    """Format timestamp for Markdown output."""
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def clean_text(text: str) -> str:
    """Clean subtitle text by removing common artifacts."""
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'\{[^}]+\}', '', text)  # Remove curly brace content
    text = re.sub(r'\[[^\]]+\]', '', text)  # Remove square bracket content
    text = text.strip()
    return text


def should_merge_subtitle(text: str) -> bool:
    """Check if subtitle should be merged with previous one."""
    text_lower = text.lower()
    # Don't merge if it ends with punctuation that suggests a complete thought
    if text.rstrip().endswith(('.', '!', '?', '。', '！', '？')):
        return False
    # Don't merge if it's too short (likely a sound effect or label)
    if len(text.strip()) < 3:
        return False
    return True


def convert_srt_to_markdown(srt_path: str, md_path: str, include_timestamps: bool = True) -> None:
    """Convert a single SRT file to Markdown format."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse SRT content
    blocks = re.split(r'\n\s*\n', content.strip())
    md_lines = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # Try to extract subtitle index and time info
        if lines[0].isdigit() and '-->' in lines[1]:
            text = ' '.join(lines[2:])
            text = clean_text(text)
            
            if not text:
                continue
            
            # Extract timestamp
            if include_timestamps:
                time_match = re.search(r'(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)', lines[1])
                if time_match:
                    start_time = parse_srt_time(time_match.group(1))
                    timestamp = format_timestamp(*start_time)
                    md_lines.append(f"**[{timestamp}]** {text}")
                else:
                    md_lines.append(text)
            else:
                md_lines.append(text)
        else:
            # Handle malformed blocks
            text = ' '.join(lines)
            text = clean_text(text)
            if text:
                md_lines.append(text)
    
    # Write Markdown file
    os.makedirs(os.path.dirname(md_path) or '.', exist_ok=True)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(md_lines) + '\n')


def process_directory(srt_dir: str, md_dir: str, include_timestamps: bool = True) -> int:
    """Process all SRT files in a directory."""
    srt_path = Path(srt_dir)
    if not srt_path.exists():
        print(f"Error: SRT directory not found: {srt_dir}", file=sys.stderr)
        return 0
    
    converted = 0
    for srt_file in srt_path.glob('*.srt'):
        md_file = srt_file.stem + '.md'
        md_path = os.path.join(md_dir, md_file)
        
        try:
            convert_srt_to_markdown(str(srt_file), md_path, include_timestamps)
            print(f"✓ Converted: {srt_file.name} -> {md_file}")
            converted += 1
        except Exception as e:
            print(f"✗ Failed: {srt_file.name} - {e}", file=sys.stderr)
    
    return converted


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert YouTube SRT subtitle files to readable Markdown format."
    )
    parser.add_argument(
        "--srt-dir",
        default=None,
        help="Directory containing SRT files (default: youtube_subtitles/<channel>/srt)",
    )
    parser.add_argument(
        "--md-dir",
        default=None,
        help="Output directory for MD files (default: youtube_subtitles/<channel>/md)",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help="Channel name to process (e.g., 20vc, a16z, joerogan)",
    )
    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Remove timestamps from output",
    )
    parser.add_argument(
        "--base-dir",
        default="youtube_subtitles",
        help="Base directory for subtitle files",
    )
    
    args = parser.parse_args()
    
    # Determine which directories to process
    if args.channel:
        # Process specific channel
        srt_dir = os.path.join(args.base_dir, args.channel, "srt")
        md_dir = os.path.join(args.base_dir, args.channel, "md")
        if args.srt_dir:
            srt_dir = args.srt_dir
        if args.md_dir:
            md_dir = args.md_dir
        
        converted = process_directory(srt_dir, md_dir, not args.no_timestamps)
        print(f"\n✓ Converted {converted} files from {args.channel}")
    else:
        # Process all channels
        base_path = Path(args.base_dir)
        if not base_path.exists():
            print(f"Error: Base directory not found: {args.base_dir}", file=sys.stderr)
            return 1
        
        total_converted = 0
        for channel_dir in base_path.iterdir():
            if channel_dir.is_dir():
                srt_dir = os.path.join(channel_dir, "srt")
                md_dir = os.path.join(channel_dir, "md")
                
                if os.path.exists(srt_dir):
                    print(f"\nProcessing channel: {channel_dir.name}")
                    converted = process_directory(srt_dir, md_dir, not args.no_timestamps)
                    total_converted += converted
        
        print(f"\n✓ Total converted: {total_converted} files")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())