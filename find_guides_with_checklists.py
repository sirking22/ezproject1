#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Поиск гайдов с чеклистами
"""

import asyncio
import os
import re
from dotenv import load_dotenv
from notion_client import AsyncClient

# Загружаем переменные окружения
load_dotenv()

GUIDES_DB = "47c6086858d442ebaeceb4fad1b23ba3"

async def find_guides_with_checklists():
    """Ищет гайды с чеклистами"""
    
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    
    print("🔍 ПОИСК ГАЙДОВ С ЧЕКЛИСТАМИ")
    print("=" * 60)
    
    try:
        # Получаем все гайды
        response = await client.databases.query(
            database_id=GUIDES_DB,
            page_size=100
        )
        
        guides = response.get('results', [])
        print(f"📚 Найдено гайдов: {len(guides)}")
        
        guides_with_checklists = []
        
        for i, guide in enumerate(guides[:5]):  # Проверяем первые 5
            guide_id = guide['id']
            guide_title = guide['properties'].get('Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Без названия')
            
            print(f"\n{i+1}. 📖 {guide_title}")
            print(f"   🆔 ID: {guide_id}")
            
            try:
                # Получаем блоки гайда
                blocks = await client.blocks.children.list(block_id=guide_id)
                
                if not blocks.get('results'):
                    print("   ⚠️ Блоки не найдены")
                    continue
                
                # Извлекаем текст
                guide_text = []
                for block in blocks.get('results', []):
                    block_type = block['type']
                    
                    if block_type == 'paragraph':
                        rich_text = block['paragraph'].get('rich_text', [])
                        if rich_text:
                            guide_text.append(rich_text[0]['text']['content'])
                    elif block_type == 'heading_2':
                        rich_text = block['heading_2'].get('rich_text', [])
                        if rich_text:
                            guide_text.append(f"## {rich_text[0]['text']['content']}")
                    elif block_type == 'heading_3':
                        rich_text = block['heading_3'].get('rich_text', [])
                        if rich_text:
                            guide_text.append(f"### {rich_text[0]['text']['content']}")
                    elif block_type == 'to_do':
                        rich_text = block['to_do'].get('rich_text', [])
                        checked = block['to_do'].get('checked', False)
                        if rich_text:
                            checkbox = "[x]" if checked else "[ ]"
                            guide_text.append(f"- {checkbox} {rich_text[0]['text']['content']}")
                    elif block_type == 'bulleted_list_item':
                        rich_text = block['bulleted_list_item'].get('rich_text', [])
                        if rich_text:
                            guide_text.append(f"- {rich_text[0]['text']['content']}")
                
                full_text = "\n".join(guide_text)
                print(f"   📝 Символов: {len(full_text)}")
                
                # Ищем чеклисты
                patterns = [
                    r'## ✅ Чеклист качества:(.*?)(?=##|\Z)',
                    r'## 📋 Чеклист:(.*?)(?=##|\Z)',
                    r'## ✅ Чеклист:(.*?)(?=##|\Z)',
                    r'### Чеклист:(.*?)(?=###|\Z)',
                    r'чеклист',
                    r'checklist',
                ]
                
                has_checklist = False
                for pattern in patterns:
                    if re.search(pattern, full_text, re.IGNORECASE):
                        has_checklist = True
                        break
                
                if has_checklist:
                    print("   ✅ ЧЕКЛИСТ НАЙДЕН!")
                    guides_with_checklists.append({
                        'id': guide_id,
                        'title': guide_title,
                        'text': full_text
                    })
                    
                    # Показываем найденные чеклисты
                    for pattern in patterns[:4]:  # Только основные паттерны
                        matches = re.findall(pattern, full_text, re.DOTALL | re.IGNORECASE)
                        for match in matches:
                            if match.strip():
                                items = re.findall(r'- \[ \] (.*?)(?=\n- \[ \]|\n##|\n###|\Z)', match, re.DOTALL)
                                if items:
                                    print(f"   📋 Найдено пунктов: {len(items)}")
                                    for j, item in enumerate(items[:3]):  # Показываем первые 3
                                        print(f"      {j+1}. {item.strip()}")
                                    if len(items) > 3:
                                        print(f"      ... и еще {len(items)-3}")
                else:
                    print("   ❌ Чеклист не найден")
                
            except Exception as e:
                print(f"   ❌ Ошибка чтения: {e}")
        
        print(f"\n🎯 РЕЗУЛЬТАТЫ:")
        print(f"✅ Гайдов с чеклистами: {len(guides_with_checklists)}")
        
        if guides_with_checklists:
            print("\n📋 ДОСТУПНЫЕ ГАЙДЫ С ЧЕКЛИСТАМИ:")
            for guide in guides_with_checklists:
                print(f"• {guide['title']} ({guide['id']})")
            
            return guides_with_checklists[0]  # Возвращаем первый найденный
        
        return None
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(find_guides_with_checklists()) 