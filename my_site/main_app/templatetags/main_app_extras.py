from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def replace_price(html_content, price_value):
    """
    Заменяет placeholder {{STANDARD_PRICE}} или {{PRICE}} в HTML контенте на цену с валютой BYN.
    Если цена не указана, заменяет на "Price on request".
    
    Использование в шаблоне:
    {{ soft.description|replace_price:soft.standard_price }}
    
    В описании используйте placeholder: {{STANDARD_PRICE}} или {{PRICE}}
    Например: "The basic paid version costs {{STANDARD_PRICE}}"
    """
    if not html_content:
        return html_content
    
    # Преобразуем в строку, если это SafeString
    content_str = str(html_content) if html_content else ""
    
    if price_value:
        price_str = str(price_value).strip()
        # Если в цене уже есть BYN, используем как есть
        # Если есть RUB или другая валюта, заменяем на BYN
        if "BYN" in price_str.upper():
            price_text = price_str
        elif "RUB" in price_str.upper() or "RUBLES" in price_str.upper() or "RUBLE" in price_str.upper():
            # Удаляем старую валюту и добавляем BYN
            price_str = price_str.replace("RUB", "").replace("rub", "").replace("RUBLES", "").replace("rubles", "").replace("RUBLE", "").replace("ruble", "").strip()
            price_text = f"{price_str} BYN" if price_str else "Price on request"
        else:
            # Просто добавляем BYN
            price_text = f"{price_str} BYN"
    else:
        # Если цена не указана
        price_text = "Price on request"
    
    # Заменяем placeholder на реальную цену
    result = content_str.replace("{{STANDARD_PRICE}}", price_text)
    result = result.replace("{{PRICE}}", price_text)  # Альтернативный вариант
    
    return mark_safe(result)

