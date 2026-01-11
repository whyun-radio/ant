#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单直接的 Markdown 到 Discuz BBCode 转换，确保中文字符不丢失
"""

def remove_emoji(text):
    """移除 emoji"""
    text = text.replace('👉', '')
    text = text.replace('👈', '')
    return text

def convert_markdown_to_bbcode(text):
    """转换 Markdown 到 BBCode"""
    # 移除 emoji
    text = remove_emoji(text)
    
    lines = text.split('\n')
    result = []
    in_code_block = False
    code_content = []
    code_lang = ''
    in_quote = False
    quote_content = []
    in_list = False
    list_items = []
    
    for line in lines:
        original_line = line
        
        # 处理代码块
        if line.strip().startswith('```'):
            if in_code_block:
                # 结束代码块
                code_text = '\n'.join(code_content)
                if code_lang:
                    result.append(f'[code={code_lang}]{code_text}[/code]')
                else:
                    result.append(f'[code]{code_text}[/code]')
                code_content = []
                code_lang = ''
                in_code_block = False
            else:
                # 开始代码块
                lang_part = line.strip()[3:].strip()
                code_lang = lang_part if lang_part else ''
                in_code_block = True
            continue
        
        if in_code_block:
            code_content.append(line)
            continue
        
        # 处理引用
        if line.strip().startswith('>'):
            if not in_quote:
                in_quote = True
                quote_content = []
            quote_line = line.lstrip('>').lstrip()
            quote_content.append(quote_line)
            continue
        else:
            if in_quote:
                quote_text = '\n'.join(quote_content)
                result.append(f'[quote]{process_inline(quote_text)}[/quote]')
                quote_content = []
                in_quote = False
        
        # 处理标题
        if line.startswith('#'):
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
            if level > 0 and level <= 6:
                content = line[level:].strip()
                content = process_inline(content)
                if level == 1:
                    result.append(f'[size=6][b]{content}[/b][/size]')
                elif level == 2:
                    result.append(f'[size=5][b]{content}[/b][/size]')
                elif level == 3:
                    result.append(f'[size=4][b]{content}[/b][/size]')
                elif level == 4:
                    result.append(f'[size=3][b]{content}[/b][/size]')
                else:
                    result.append(f'[size=3][b]{content}[/b][/size]')
                continue
        
        # 处理列表
        stripped = line.lstrip()
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                in_list = True
                list_items = []
            content = stripped[2:].strip()
            list_items.append(process_inline(content))
            continue
        elif stripped and stripped[0].isdigit() and '. ' in stripped[:5]:
            parts = stripped.split('. ', 1)
            if len(parts) == 2 and parts[0].isdigit():
                if not in_list:
                    in_list = True
                    list_items = []
                content = parts[1].strip()
                list_items.append(process_inline(content))
                continue
        
        if in_list:
            if list_items:
                result.append('[list]')
                result.extend(list_items)
                result.append('[/list]')
            list_items = []
            in_list = False
        
        # 跳过表格分隔线
        if '|' in line and '---' in line:
            continue
        
        # 普通行
        processed = process_inline(line)
        result.append(processed)
    
    # 处理未关闭的块
    if in_code_block:
        code_text = '\n'.join(code_content)
        if code_lang:
            result.append(f'[code={code_lang}]{code_text}[/code]')
        else:
            result.append(f'[code]{code_text}[/code]')
    
    if in_quote:
        quote_text = '\n'.join(quote_content)
        result.append(f'[quote]{process_inline(quote_text)}[/quote]')
    
    if in_list:
        if list_items:
            result.append('[list]')
            result.extend(list_items)
            result.append('[/list]')
    
    # 清理多余空行
    final = []
    prev_empty = False
    for line in result:
        if not line.strip():
            if not prev_empty:
                final.append('')
            prev_empty = True
        else:
            final.append(line)
            prev_empty = False
    
    return '\n'.join(final)

def process_inline(text):
    """处理行内格式"""
    import re
    
    # 先处理代码（避免被其他格式影响）
    def replace_code(m):
        return f'[code]{m.group(1)}[/code]'
    text = re.sub(r'`([^`\n]+)`', replace_code, text)
    
    # 处理图片（先处理，避免 URL 中的下划线被误识别）
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'[img]\2[/img]', text)
    
    # 处理链接（排除图片）
    text = re.sub(r'(?<!\!)\[([^\]]+)\]\(([^)]+)\)', r'[url=\2]\1[/url]', text)
    
    # 处理粗体 **text** 或 __text__
    text = re.sub(r'\*\*([^*\n]+?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'__([^_\n]+?)__', r'[b]\1[/b]', text)
    
    # 处理斜体 *text* 或 _text_
    # 但要避免处理已经在 BBCode 标签内的内容（如 [img]...[/img]）
    def process_with_protection(text):
        # 保护 BBCode 标签内的内容
        protected = {}
        tag_pattern = r'\[(img|url|code|b|i)[^\]]*\](.*?)\[/\1\]'
        
        def protect(m):
            key = f'__PROTECTED_{len(protected)}__'
            protected[key] = m.group(0)
            return key
        
        # 先保护所有 BBCode 标签
        text = re.sub(tag_pattern, protect, text, flags=re.DOTALL)
        
        # 处理斜体
        text = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'[i]\1[/i]', text)
        # 对于下划线，只处理不在路径中的（路径通常包含 /）
        text = re.sub(r'(?<![/\w])_([^_\n/]+?)_(?![/\w])', r'[i]\1[/i]', text)
        
        # 恢复保护的内容
        for key, value in protected.items():
            text = text.replace(key, value)
        
        return text
    
    text = process_with_protection(text)
    
    return text

def main():
    input_file = r'E:\kuaipan\code\markdown\ant\text\balun_custom.md'
    output_file = r'E:\kuaipan\code\markdown\ant\text\balun_custom_discuz.txt'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    bbcode = convert_markdown_to_bbcode(content)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(bbcode)
    
    print('转换完成！')

if __name__ == '__main__':
    main()
