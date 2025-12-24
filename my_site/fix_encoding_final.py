#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Финальное исправление кодировки в django.po
Читает файл как бинарный, правильно декодирует и пересохраняет
"""
import sys
import os

def fix_po_file(file_path):
    """Исправляет кодировку в .po файле"""
    
    # Читаем файл как байты
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # Создаем резервную копию
    backup_path = file_path + '.backup_final'
    with open(backup_path, 'wb') as f:
        f.write(raw_data)
    print(f"Создана резервная копия: {backup_path}")
    
    # Пробуем разные способы декодирования
    # Метод 1: Пробуем декодировать как Windows-1251 напрямую
    try:
        text = raw_data.decode('windows-1251')
        print("Успешно декодирован как Windows-1251")
    except UnicodeDecodeError:
        try:
            # Метод 2: Декодируем как UTF-8, затем исправляем поврежденные части
            text = raw_data.decode('utf-8')
            # Если текст содержит повреждения, пробуем исправить
            if 'Рџ' in text or 'Р ' in text:
                # Это двойная кодировка - нужно декодировать обратно
                # Кодируем в latin1 (чтобы получить байты), затем декодируем как windows-1251
                try:
                    # Для каждой поврежденной строки пробуем исправить
                    import re
                    def fix_corrupted(match):
                        corrupted = match.group(1)
                        try:
                            # Кодируем поврежденный текст обратно в байты через latin1
                            bytes_data = corrupted.encode('latin1')
                            # Декодируем как windows-1251
                            fixed = bytes_data.decode('windows-1251')
                            return f'msgstr "{fixed}"'
                        except:
                            return match.group(0)
                    
                    # Ищем все msgstr с поврежденной кодировкой
                    pattern = r'msgstr "([^"]*Р[^"]*)"'
                    text = re.sub(pattern, fix_corrupted, text)
                except Exception as e:
                    print(f"Ошибка при исправлении: {e}")
                    # Если не получилось, пробуем другой метод
                    text = raw_data.decode('latin1', errors='replace')
        except UnicodeDecodeError:
            # Метод 3: Latin1 как последняя попытка
            text = raw_data.decode('latin1', errors='replace')
    
    # Сохраняем исправленный файл в UTF-8
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Файл {file_path} пересохранен в UTF-8!")
    
    # Проверяем результат
    with open(file_path, 'r', encoding='utf-8') as f:
        test_text = f.read()
        if 'Пожалуйста' in test_text or 'Консультация' in test_text:
            print("✓ Кодировка исправлена правильно!")
        else:
            print("⚠ Возможно, проблема осталась. Проверьте файл вручную.")
    
    return True

if __name__ == '__main__':
    po_file = os.path.join('locale', 'ru', 'LC_MESSAGES', 'django.po')
    if os.path.exists(po_file):
        fix_po_file(po_file)
    else:
        print(f"Файл {po_file} не найден!")
        sys.exit(1)


