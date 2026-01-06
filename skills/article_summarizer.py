#!/usr/bin/env python3
"""
文章总结技能工具
可以总结各种格式的文章和文本内容
"""

import argparse
import os
import re
from pathlib import Path


class ArticleSummarizer:
    def __init__(self):
        self.language = "chinese"  # 默认输出中文总结
    
    def read_article(self, file_path: str) -> str:
        """读取文章内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取文件失败: {e}"
    
    def extract_title(self, content: str, filename: str) -> str:
        """从内容或文件名提取标题"""
        # 尝试从内容中提取标题
        lines = content.split('\n')
        for line in lines[:10]:  # 只检查前10行
            line = line.strip()
            if line and not line.startswith('**[') and not line.startswith('#'):
                # 移除可能的时间戳和格式符号
                clean_title = re.sub(r'\*\*\[[^\]]+\]\*\*', '', line).strip()
                if len(clean_title) > 5 and len(clean_title) < 200:
                    return clean_title
        
        # 如果没有找到合适的标题，使用文件名
        title = filename.replace('.md', '').replace('.txt', '').replace('_', ' ')
        return title
    
    def extract_key_points(self, content: str, max_points: int = 8) -> list:
        """提取关键要点"""
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # 移除时间戳和格式符号
            clean_line = re.sub(r'\*\*\[[^\]]+\]\*\*', '', stripped).strip()
            clean_line = re.sub(r'^[#*]+\s*', '', clean_line).strip()
            
            # 只保留有意义的句子
            if len(clean_line) > 20 and len(clean_line) < 300:
                # 避免重复
                if clean_line not in key_points:
                    key_points.append(clean_line)
                    if len(key_points) >= max_points:
                        break
        
        return key_points
    
    def extract_keywords(self, content: str) -> list:
        """提取关键词"""
        # 移除时间戳和格式符号
        clean_content = re.sub(r'\*\*\[[^\]]+\]\*\*', '', content)
        clean_content = re.sub(r'[,\.!?:;()"\'\[\]]', ' ', clean_content)
        
        words = clean_content.split()
        
        # 找出有意义的词（长度>5的词，包含大写字母的词，或数字组合）
        keywords = []
        for word in words:
            word = word.strip()
            if len(word) > 5 and not word.startswith('http'):
                # 可能是关键词的条件
                if (any(c.isupper() for c in word) or 
                    any(c.isdigit() for c in word) or 
                    len(word) > 8):
                    if word.lower() not in ['this', 'that', 'about', 'they', 'would', 'could']:
                        keywords.append(word)
        
        # 去重并限制数量
        unique_keywords = list(set(keywords))[:15]
        return unique_keywords
    
    def generate_summary(self, content: str, title: str, detailed: bool = True) -> str:
        """生成文章总结"""
        key_points = self.extract_key_points(content)
        keywords = self.extract_keywords(content)
        
        # 统计基本信息
        lines = content.split('\n')
        meaningful_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 10]
        word_count = len(content.split())
        
        summary = f"# {title}\n\n"
        summary += "## 文章总结\n\n"
        
        if detailed:
            summary += "### 基本信息\n"
            summary += f"- **内容长度**: {word_count} 个单词\n"
            summary += f"- **主要内容数**: {len(meaningful_lines)} 条\n\n"
            
            if keywords:
                summary += "### 关键词\n"
                summary += ", ".join(keywords[:10]) + "\n\n"
            
            summary += "### 核心观点\n"
            for i, point in enumerate(key_points[:6], 1):
                # 限制每点长度
                if len(point) > 150:
                    point = point[:150] + "..."
                summary += f"{i}. {point}\n"
            
            if len(key_points) > 6:
                summary += f"\n*...还有 {len(key_points) - 6} 个观点...*\n"
            
            summary += "\n### 主要启示\n"
            summary += "- 该内容提供了相关主题的深度见解和实用信息\n"
            summary += "- 涵盖了技术/商业/行业的重要发展趋势\n"
            summary += "- 为相关从业者和学习者提供了宝贵的参考价值\n"
        
        else:
            summary += "### 简要总结\n"
            summary += f"这是一篇包含{word_count}个单词的文章，主要讨论了相关主题。\n\n"
            
            if key_points:
                summary += "### 主要观点\n"
                for i, point in enumerate(key_points[:3], 1):
                    if len(point) > 100:
                        point = point[:100] + "..."
                    summary += f"{i}. {point}\n"
        
        summary += "\n---\n\n*此总结由自动工具生成*"
        
        return summary
    
    def process_article(self, input_path: str, output_path: str = None, detailed: bool = True) -> str:
        """处理单篇文章"""
        if not os.path.exists(input_path):
            return f"错误: 文件不存在 - {input_path}"
        
        content = self.read_article(input_path)
        if not content or content.startswith("读取文件失败"):
            return "无法读取文章内容"
        
        filename = os.path.basename(input_path)
        title = self.extract_title(content, filename)
        summary = self.generate_summary(content, title, detailed)
        
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                return f"✓ 总结已生成: {output_path}"
            except Exception as e:
                return f"保存失败: {e}"
        
        return summary
    
    def process_directory(self, dir_path: str, output_dir: str = None, detailed: bool = True) -> dict:
        """处理整个目录"""
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        if not os.path.exists(dir_path):
            print(f"错误: 目录不存在 - {dir_path}")
            return results
        
        # 支持的文件格式
        supported_extensions = ['.md', '.txt', '.en.md']
        
        # 查找所有文章文件
        articles = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    # 跳过已经总结过的文件
                    if 'summary' in file.lower():
                        continue
                    articles.append(os.path.join(root, file))
        
        if not articles:
            print(f"在 {dir_path} 中没有找到可总结的文章")
            return results
        
        print(f"找到 {len(articles)} 篇文章待总结...")
        
        for article_path in articles:
            try:
                # 确定输出路径
                if output_dir:
                    filename = os.path.basename(article_path)
                    summary_filename = filename.replace('.md', '_summary.md')
                    output_path = os.path.join(output_dir, summary_filename)
                else:
                    output_path = article_path.replace('.md', '_summary.md')
                
                result = self.process_article(article_path, output_path, detailed)
                
                if result.startswith("✓"):
                    results["success"] += 1
                    print(result)
                else:
                    results["failed"] += 1
                    print(f"✗ {result}")
                    
            except Exception as e:
                results["failed"] += 1
                print(f"✗ 处理失败 {article_path}: {e}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="智能文章总结工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 总结单篇文章
  python article_summarizer.py article.md
  
  # 总结文章并指定输出文件
  python article_summarizer.py article.md -o summary.md
  
  # 总结整个目录的文章
  python article_summarizer.py -d articles/
  
  # 生成简要总结
  python article_summarizer.py article.md --brief
  
  # 总结到指定目录
  python article_summarizer.py -d articles/ -o summaries/
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='输入文件或目录路径'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='总结整个目录的文章'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件或目录路径'
    )
    
    parser.add_argument(
        '--brief',
        action='store_true',
        help='生成简要总结而非详细总结'
    )
    
    parser.add_argument(
        '--print',
        action='store_true',
        help='直接输出总结到终端而不保存文件'
    )
    
    args = parser.parse_args()
    
    summarizer = ArticleSummarizer()
    
    if args.directory:
        # 目录模式
        results = summarizer.process_directory(
            args.directory, 
            args.output, 
            not args.brief
        )
        print(f"\n总结完成: 成功 {results['success']}, 失败 {results['failed']}, 跳过 {results['skipped']}")
        
    elif args.input:
        # 单文件模式
        if args.print:
            summary = summarizer.process_article(args.input, None, not args.brief)
            print(summary)
        else:
            output_path = args.output
            if not output_path:
                # 默认在原文件同目录下生成 _summary.md 文件
                output_path = args.input.replace('.md', '_summary.md')
            
            result = summarizer.process_article(args.input, output_path, not args.brief)
            print(result)
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()