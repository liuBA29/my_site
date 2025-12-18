#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для исправления кодировки в файле django.po
Исправляет двойную кодировку (Windows-1251 прочитан как UTF-8)
"""
import sys
import os
import re

def fix_double_encoding(text):
    """Исправляет двойную кодировку: Windows-1251 -> UTF-8 -> исправление"""
    # Находим все поврежденные строки msgstr с кириллицей
    # Поврежденный текст содержит символы типа "РџРѕР¶Р°Р»СѓР№СЃС‚Р°"
    
    def decode_fixed(match):
        """Декодирует поврежденную строку"""
        damaged = match.group(1)
        try:
            # Декодируем как UTF-8 (получаем байты)
            bytes_data = damaged.encode('latin1')  # Latin1 сохраняет байты как есть
            # Декодируем как Windows-1251
            fixed = bytes_data.decode('windows-1251')
            return f'msgstr "{fixed}"'
        except (UnicodeDecodeError, UnicodeEncodeError):
            return match.group(0)  # Возвращаем как есть, если не получилось
    
    # Ищем все msgstr с поврежденной кодировкой
    # Паттерн: msgstr "Р..." (кириллица, которая выглядит как поврежденная)
    pattern = r'msgstr "([Р-яЁё\s\-\.\,\!\?\;\(\)\:\"\'\%\d\w]+)"'
    
    def fix_line(match):
        full_match = match.group(0)
        content = match.group(1)
        
        # Проверяем, содержит ли строка поврежденную кодировку
        # Поврежденные строки содержат символы типа "Рџ", "Р ", "Р°" и т.д.
        if 'Р' in content and any(c in content for c in ['Рџ', 'Р ', 'Р°', 'РІ', 'Рѕ']):
            try:
                # Кодируем в Latin1 (сохраняет байты как есть), затем декодируем как Windows-1251
                fixed_content = content.encode('latin1').decode('windows-1251')
                return f'msgstr "{fixed_content}"'
            except (UnicodeDecodeError, UnicodeEncodeError):
                return full_match
        return full_match
    
    # Применяем исправление ко всем msgstr строкам
    fixed_text = re.sub(pattern, fix_line, text)
    
    return fixed_text

def fix_po_file(file_path):
    """Исправляет кодировку в .po файле"""
    
    # Читаем файл
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except UnicodeDecodeError:
        # Если не получается прочитать как UTF-8, пробуем другие кодировки
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        # Пробуем latin1 (сохраняет все байты)
        text = raw_data.decode('latin1')
    
    # Проверяем, есть ли повреждения
    if 'Рџ' not in text and 'Р ' not in text:
        print("Файл не содержит очевидных проблем с кодировкой")
        return False
    
    # Создаем резервную копию
    backup_path = file_path + '.backup'
    with open(backup_path, 'wb') as f:
        with open(file_path, 'rb') as original:
            f.write(original.read())
    print(f"Создана резервная копия: {backup_path}")
    
    # Исправляем кодировку
    fixed_text = fix_double_encoding(text)
    
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

