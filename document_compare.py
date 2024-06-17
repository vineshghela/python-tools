from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from docx import Document
import fitz  # PyMuPDF
import os
import difflib
import re

# Initialize the sentence transformer model
model = SentenceTransformer('bert-base-nli-mean-tokens')

def read_file(file_path):
    """Reads the content of a file based on its extension"""
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
    """Reads the content of a text file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_docx(file_path):
    """Reads the content of a .docx file"""
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

def read_pdf(file_path):
    """Reads the content of a PDF file"""
    doc = fitz.open(file_path)
    full_text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text.append(page.get_text())
    return '\n'.join(full_text)

def get_embedding(text):
    """Generates the embedding for a given text using the sentence transformer model"""
    return model.encode(text)

def calculate_similarity(embedding1, embedding2):
    """Calculates cosine similarity between two embeddings"""
    return cosine_similarity([embedding1], [embedding2])[0][0]

def classify_similarity(score, threshold_identical=0.95, threshold_similar=0.85):
    """Classify similarity score into categories"""
    if score >= threshold_identical:
        return 'identical'
    elif score >= threshold_similar:
        return 'similar'
    else:
        return 'different'

def compare_documents(file1_path, file2_path):
    """Compares two documents paragraph by paragraph and returns their similarity scores and differences"""
    content1 = read_file(file1_path)
    content2 = read_file(file2_path)
    
    paragraphs1 = content1.split('\n')
    paragraphs2 = content2.split('\n')
    
    similarity_scores = []
    differences = []
    
    for p1, p2 in zip(paragraphs1, paragraphs2):
        norm_p1 = normalize_text(p1)
        norm_p2 = normalize_text(p2)
        similarity_score = calculate_similarity(get_embedding(norm_p1), get_embedding(norm_p2))
        similarity_scores.append(similarity_score)
        
        diff = list(difflib.ndiff([p1], [p2]))
        differences.append((similarity_score, diff))
    
    return similarity_scores, differences, content1, content2

def normalize_text(text):
    """Normalize text by removing excessive whitespace and ensuring consistent formatting."""
    # Remove extra spaces, newlines, and tabs
    normalized_text = re.sub(r'\s+', ' ', text)
    # Remove leading and trailing spaces
    normalized_text = normalized_text.strip()
    return normalized_text

def generate_html_report(similarity_scores, differences, output_file, content1, content2):
    """Generates an HTML report showing semantic similarity and highlighting changes in red"""
    html_content = """
    <html>
    <head>
        <style>
            .insert {{color: green;}}
            .delete {{color: red;}}
            .identical {{color: green;}}
            .similar {{color: yellow;}}
            .different {{color: red;}}
        </style>
    </head>
    <body>
        <h2>Document Comparison Report</h2>
        <h3>Paragraph Similarity Scores:</h3>
        <ul>
            {similarity_list}
        </ul>
        <h3>Documents Meaning Comparison: {meaning_status}</h3>
        <h3>Differences:</h3>
        <pre>{diff_html}</pre>
    </body>
    </html>
    """
    
    # Prepare HTML for differences highlighting
    similarity_list = ""
    diff_html = ""
    for score, diff in differences:
        similarity_class = classify_similarity(score)
        similarity_list += f'<li class="{similarity_class}">Similarity Score: {score:.2f}</li>\n'
        for line in diff:
            if line.startswith('+ '):
                diff_html += f'<span class="insert">{line[2:]}</span><br>\n'
            elif line.startswith('- '):
                diff_html += f'<span class="delete">{line[2:]}</span><br>\n'
            else:
                diff_html += f'{line[2:]}<br>\n'
    
    # Determine if documents have the same meaning overall
    if all(score >= 0.85 for score in similarity_scores):
        meaning_status = "The documents have the same meaning."
    else:
        meaning_status = "The documents do not have the same meaning."
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content.format(similarity_list=similarity_list, meaning_status=meaning_status, diff_html=diff_html))

if __name__ == "__main__":
    file1_path = 'doc1.pdf'
    file2_path = 'Non Disclosure Agmt (52).docx'
    output_html = 'document_comparison_report.html'

    if os.path.exists(file1_path) and os.path.exists(file2_path):
        similarity_scores, differences, content1, content2 = compare_documents(file1_path, file2_path)
        generate_html_report(similarity_scores, differences, output_html, content1, content2)
        print(f"Comparison report saved to {output_html}")
    else:
        print("One or both of the file paths do not exist. Please check the paths and try again.")
