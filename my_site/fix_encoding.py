#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для исправления кодировки в файле django.po
Проблема: файл содержит текст в неправильной кодировке (Windows-1251 прочитан как UTF-8)
"""
import sys
import os

def fix_po_file(file_path):
    """Исправляет кодировку в .po файле"""
    
    # Читаем файл как байты
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # Пробуем декодировать как UTF-8 и проверить, есть ли проблемы
    try:
        text = raw_data.decode('utf-8')
        # Проверяем, есть ли проблемы с кодировкой
        # Если текст содержит последовательности типа "РџРѕР¶Р°Р»СѓР№СЃС‚Р°", 
        # значит была двойная кодировка (Windows-1251 -> UTF-8)
        if 'Рџ' in text or 'Р ' in text:
            print("Обнаружена проблема с кодировкой (двойная кодировка)")
            # Пробуем исправить: декодируем как Windows-1251, затем кодируем в UTF-8
            try:
                # Сначала пробуем декодировать как Windows-1251
                text_cp1251 = raw_data.decode('windows-1251')
                # Теперь кодируем в UTF-8
                fixed_data = text_cp1251.encode('utf-8')
                # Сохраняем исправленный файл
                backup_path = file_path + '.backup'
                with open(backup_path, 'wb') as f:
                    f.write(raw_data)
                print(f"Создана резервная копия: {backup_path}")
                
                with open(file_path, 'wb') as f:
                    f.write(fixed_data)
                print(f"Файл {file_path} исправлен!")
                return True
            except (UnicodeDecodeError, UnicodeEncodeError) as e:
                print(f"Ошибка при попытке исправления через Windows-1251: {e}")
                return False
        else:
            print("Кодировка файла выглядит корректной")
            return False
    except UnicodeDecodeError:
        print("Ошибка декодирования UTF-8, пробуем другие кодировки...")
        # Пробуем другие кодировки
        for encoding in ['windows-1251', 'cp1251', 'latin1']:
            try:
                text = raw_data.decode(encoding)
                fixed_data = text.encode('utf-8')
                backup_path = file_path + '.backup'
                with open(backup_path, 'wb') as f:
                    f.write(raw_data)
                print(f"Создана резервная копия: {backup_path}")
                
                with open(file_path, 'wb') as f:
                    f.write(fixed_data)
                print(f"Файл {file_path} исправлен через кодировку {encoding}!")
                return True
            except (UnicodeDecodeError, UnicodeEncodeError):
                continue
        print("Не удалось определить кодировку файла")
        return False

if __name__ == '__main__':
    po_file = os.path.join('locale', 'ru', 'LC_MESSAGES', 'django.po')
    if os.path.exists(po_file):
        fix_po_file(po_file)
    else:
        print(f"Файл {po_file} не найден!")
        sys.exit(1)


