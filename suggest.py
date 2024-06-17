import os
import re
import difflib
import fitz  # PyMuPDF
from docx import Document
import requests

# Initialize your API key
CLAUDE_API_KEY = "your_anthropic_claude_api_key"

def read_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.docx':
        return read_docx(file_path)
    elif file_extension.lower() == '.txt':
        return read_txt(file_path)
    elif file_extension.lower() == '.pdf':
        return read_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def read_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text.append(page.get_text())
    return '\n'.join(full_text)

def get_embedding_claude(text):
    # Placeholder for actual API call to Claude for embedding generation
    response = requests.post(
        'https://api.anthropic.com/v1/embedding',
        headers={'Authorization': f'Bearer {CLAUDE_API_KEY}'},
        json={'text': text}
    )
    response.raise_for_status()
    return response.json()['embedding']

def calculate_similarity(embedding1, embedding2):
    # Placeholder for actual similarity calculation using Claude
    return cosine_similarity([embedding1], [embedding2])[0][0]

def are_meaning_same(content1, content2):
    normalized_content1 = normalize_text(content1)
    normalized_content2 = normalize_text(content2)
    
    embedding1 = get_embedding_claude(normalized_content1)
    embedding2 = get_embedding_claude(normalized_content2)
    
    similarity_score = calculate_similarity(embedding1, embedding2)
    similarity_threshold = 0.85
    
    return similarity_score >= similarity_threshold

def compare_documents(file1_path, file2_path):
    content1 = read_file(file1_path)
    content2 = read_file(file2_path)
    
    similarity_score = calculate_similarity(get_embedding_claude(normalize_text(content1)), get_embedding_claude(normalize_text(content2)))
    
    diff = difflib.ndiff(content1.splitlines(), content2.splitlines())
    differences = '\n'.join(diff)
    
    return similarity_score, differences, content1, content2

def normalize_text(text):
    normalized_text = re.sub(r'\s+', ' ', text)
    normalized_text = normalized_text.strip()
    return normalized_text

def generate_html_report(similarity_score, differences, output_file, content1, content2):
    html_content = """
    <html>
    <head>
        <style>
            .insert {{color: green;}}
            .delete {{color: red;}}
        </style>
    </head>
    <body>
        <h2>Document Comparison Report</h2>
        <h3>Similarity Score: {similarity_score}</h3>
        <h3>Documents Meaning Comparison: {meaning_status}</h3>
        <h3>Differences:</h3>
        <pre>{diff_html}</pre>
    </body>
    </html>
    """
    
    if are_meaning_same(content1, content2):
        meaning_status = "The documents have the same meaning."
    else:
        meaning_status = "The documents do not have the same meaning."
    
    diff_html = ""
    for line in differences.split('\n'):
        if line.startswith('+ '):
            diff_html += f'<span class="insert">{line}</span><br>\n'
        elif line.startswith('- '):
            diff_html += f'<span class="delete">{line}</span><br>\n'
        else:
            diff_html += f'{line}<br>\n'
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content.format(similarity_score=similarity_score, meaning_status=meaning_status, diff_html=diff_html))

if __name__ == "__main__":
    file1_path = 'doc1.pdf'
    file2_path = 'Non Disclosure Agmt (52).docx'
    output_html = 'document_comparison_report.html'

    if os.path.exists(file1_path) and os.path.exists(file2_path):
        similarity_score, differences, content1, content2 = compare_documents(file1_path, file2_path)
        generate_html_report(similarity_score, differences, output_html, content1, content2)
        print(f"Comparison report saved to {output_html}")
    else:
        print("One or both of the file paths do not exist. Please check the paths and try again.")
