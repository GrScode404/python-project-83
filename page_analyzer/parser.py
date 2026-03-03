from typing import Optional

from bs4 import BeautifulSoup
from requests import Response


def extract_page_data(response: Response) -> dict:

    status_code = response.status_code
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    h1 = soup.find('h1')
    title = soup.find('title')
    description = soup.find('meta', attrs={'name': 'description'})
    
    h1_text = _extract_text(h1, max_length=255)
    title_text = _extract_text(title, max_length=255)
    description_text = _extract_meta_content(description, max_length=255)
    
    return {
        'status_code': status_code,
        'h1': h1_text,
        'title': title_text,
        'description': description_text,
    }


def _extract_text(element, max_length: int = 255) -> Optional[str]:

    if element:
        text = element.get_text(strip=True)
        return text[:max_length] if text else None
    return None


def _extract_meta_content(element, max_length: int = 255) -> Optional[str]:

    if element and 'content' in element.attrs:
        content = element['content'].strip()
        return content[:max_length] if content else None
    return None
