#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Более точное исправление кодировки в django.po
Исправляет двойную кодировку Windows-1251 -> UTF-8
"""
import sys
import os
import re

def fix_po_file(file_path):
    """Исправляет кодировку в .po файле"""
    
    # Читаем файл как байты
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # Создаем резервную копию
    backup_path = file_path + '.backup2'
    with open(backup_path, 'wb') as f:
        f.write(raw_data)
    print(f"Создана резервная копия: {backup_path}")
    
    # Пробуем декодировать как UTF-8 с обработкой ошибок
    try:
        text = raw_data.decode('utf-8')
    except UnicodeDecodeError:
        # Если не получается, пробуем latin1
        text = raw_data.decode('latin1', errors='replace')
    
    # Функция для исправления одной строки msgstr
    def fix_msgstr_line(line):
        # Ищем строки вида msgstr "поврежденный текст"
        match = re.match(r'^(msgstr\s+")(.*)(")$', line)
        if not match:
            return line
        
        prefix = match.group(1)
        content = match.group(2)
        suffix = match.group(3)
        
        # Проверяем, содержит ли строка поврежденную кодировку
        # Поврежденные строки содержат символы типа "Рџ", "Р ", "Р°" и т.д.
        # Но не содержат нормальную кириллицу
        has_corrupted = 'Р' in content and any(ord(c) > 127 for c in content)
        has_normal_cyrillic = any('\u0430' <= c <= '\u044f' or c in 'ёЁ' for c in content)
        
        if has_corrupted and not has_normal_cyrillic:
            try:
                # Кодируем в latin1 (сохраняет байты), затем декодируем как windows-1251
                fixed_content = content.encode('latin1').decode('windows-1251')
                return prefix + fixed_content + suffix
            except (UnicodeDecodeError, UnicodeEncodeError) as e:
                print(f"Ошибка исправления строки: {e}")
                return line
        return line
    
    # Обрабатываем файл построчно
    lines = text.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Проверяем только строки msgstr
        if line.strip().startswith('msgstr "'):
            fixed_lines.append(fix_msgstr_line(line))
        else:
            fixed_lines.append(line)
    
    # Объединяем обратно
    fixed_text = '\n'.join(fixed_lines)
    
    # Сохраняем исправленный файл
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_text)
    
    print(f"Файл {file_path} исправлен!")
    return True

if __name__ == '__main__':
    po_file = os.path.join('locale', 'ru', 'LC_MESSAGES', 'django.po')
    if os.path.exists(po_file):
        fix_po_file(po_file)
    else:
        print(f"Файл {po_file} не найден!")
        sys.exit(1)


