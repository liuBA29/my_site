# main_app/context_processors.py

from django.conf import settings
from .models import Project, FreeSoftware, BusinessSoftware
import json


def seo_keywords(request):
    """
    Context processor для динамических SEO ключевых слов
    на основе проектов и программ из базы данных
    """
    # Получаем все проекты
    projects = Project.objects.all()[:10]  # Ограничиваем для производительности
    
    # Собираем ключевые слова из названий проектов
    project_keywords = []
    tech_keywords = set()
    
    for project in projects:
        # Добавляем название проекта как ключевое слово
        project_keywords.append(project.title)
        
        # Извлекаем технологии из tech_stack
        if project.tech_stack:
            techs = [tech.strip() for tech in project.tech_stack.split(',')]
            tech_keywords.update(techs)
    
    # Получаем названия программ
    free_soft_names = list(FreeSoftware.objects.values_list('name', flat=True)[:5])
    business_soft_names = list(BusinessSoftware.objects.values_list('name', flat=True)[:5])
    
    # Базовые ключевые слова
    base_keywords = [
        "web development",
        "Python",
        "Django",
        "portfolio",
        "freelancer",
        "Liubov Kovaleva",
        "LiuBA29",
        "website development",
        "Django developer",
        "Python developer",
        "web applications",
        "Django Channels",
        "PostgreSQL",
        "Redis",
        "Docker",
        "API integration",
        "Telegram bot",
        "CRM development",
        "business software",
        "free software"
    ]
    
    # Объединяем все ключевые слова
    all_keywords = base_keywords + project_keywords + list(tech_keywords) + free_soft_names + business_soft_names
    
    # Убираем дубликаты и ограничиваем количество
    unique_keywords = list(dict.fromkeys(all_keywords))[:30]  # Максимум 30 ключевых слов
    
    # Формируем строку ключевых слов
    keywords_string = ", ".join(unique_keywords)
    
    # Формируем JSON массив для knowsAbout в структурированных данных
    tech_stack_json = json.dumps(list(tech_keywords)[:15] if tech_keywords else [
        "Python", "Django", "Web Development", "Docker", "PostgreSQL", 
        "Redis", "JavaScript", "HTML5", "CSS3"
    ])
    
    return {
        'seo_keywords': keywords_string,
        'seo_project_names': project_keywords[:10],  # Для использования в описаниях
        'seo_tech_stack': list(tech_keywords)[:15],  # Технологии для описаний
        'seo_tech_stack_json': tech_stack_json,  # JSON для структурированных данных
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),  # Google Analytics ID
    }

