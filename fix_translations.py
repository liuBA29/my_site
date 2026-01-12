#!/usr/bin/env python
# -*- coding: utf-8 -*-

file_path = r'my_site/locale/ru/LC_MESSAGES/django.po'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    
    # Исправляем "Instruction Manual" - если msgstr пустой
    if 'msgid "Instruction Manual"' in line:
        new_lines.append(line)
        i += 1
        if i < len(lines) and 'msgstr ""' in lines[i]:
            new_lines.append('msgstr "Инструкция"\n')
            i += 1
            continue
    
    # Исправляем "Download PDF Instruction" - убираем fuzzy и исправляем msgstr
    if 'msgid "Download PDF Instruction"' in line:
        # Пропускаем строки с fuzzy и комментариями перед msgid
        while i > 0 and (', fuzzy' in lines[i-1] or '#|' in lines[i-1]):
            if i > 0:
                i -= 1
                if new_lines:
                    new_lines.pop()
        
        # Добавляем правильный комментарий
        new_lines.append('#: .\\templates\\main_app\\business_soft_detail.html:119\n')
        new_lines.append('msgid "Download PDF Instruction"\n')
        new_lines.append('msgstr "Загрузить инструкцию в PDF"\n')
        i += 1
        # Пропускаем старые строки (msgstr с неправильной кодировкой)
        while i < len(lines) and ('msgstr' in lines[i] or lines[i].strip() == ''):
            i += 1
        continue
    
    new_lines.append(line)
    i += 1

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed!')
