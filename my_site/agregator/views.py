import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

def book_list(request):
    query = request.GET.get('q', '').lower()  # получаем поисковый запрос

    url = "https://knigalit.ru/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = []

    for book in soup.select("ul.quadro > li"):
        title_tag = book.find("a", class_="bl triple")
        if title_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag["href"]
            if query in title.lower():
                books.append({
                    'title': title,
                    'link': f'https://knigalit.ru{link}'
                })

    return render(request, 'agregator/book_list.html', {
        'books': books,
        'query': query
    })
