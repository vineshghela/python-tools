# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

def format_and_clean_html(html_content):
    # Parse HTML content
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove elements with no content
    for element in soup.find_all():
        if not element.text.strip() and not element.contents and (element.get('id') or element.get('class')):
            element.decompose()

    # Remove empty tags
    for element in soup.find_all():
        if not element.text.strip() and not element.contents:
            element.decompose()

    # Fix spacing issues
    formatted_html = soup.prettify()

    return formatted_html

def read_and_clean_html(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    cleaned_html = format_and_clean_html(html_content)

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_html)

# Example usage
input_file_path = 'unformatted.html'
output_file_path = 'formatted.html'
read_and_clean_html(input_file_path, output_file_path)
