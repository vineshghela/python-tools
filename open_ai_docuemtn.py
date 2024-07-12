import json
from openai import OpenAI
from docx import Document
from dotenv import load_dotenv
import os
import argparse

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable in the .env file.")

client = OpenAI(api_key=api_key)

def extract_text_from_docx(file_path):
    """
    Extracts and returns text from a .docx file located at file_path.
    """
    doc = Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        text.append(paragraph.text)
    return '\n'.join(text)

def compare_files(file1_path, file2_path):
    """
    Compares two .docx files using the OpenAI API and returns a summary of their similarities and differences.
    """

    # Extract text from both files
    text1 = extract_text_from_docx(file1_path)
    text2 = extract_text_from_docx(file2_path)

    # Create the prompt for the comparison
    prompt = (
        "I have two similar legal documents relevant to a legal transaction. Compare them on a semantic level with respect to their legal meaning. "
        "Return the response as a JSON object that includes the following details:\n"
        "1. Differences: A detailed list of differences, including clause numbers/references, descriptions, the legal implications of each difference, "
        "and an indication of which party each difference favors or disadvantages. Ensure that each difference is linked to its specific clause number or reference (e.g., 1, 2.1).\n"
        "2. Similarity Score: A score indicating how similar the documents are on a scale from 0 to 1.\n"
        "Use precise legal terminology and provide citations where applicable. Ensure that the comparison considers the legal nuances and implications of each clause.\n\n"
        "File 1: {file1_name}\n{text1}\n\n"
        "File 2: {file2_name}\n{text2}\n\n"
        "Ensure that the comparison is thorough and detailed, specifically highlighting the legal meanings and implications of the clauses in both documents, "
        "and include clause numbers and/or references for each difference identified.\n\n"
        "The JSON format should be as follows:\n"
        "{\n"
        '  "differences": [\n'
        '    {\n'
        '      "clause": "Clause number/reference",\n'
        '      "description": "Description of difference",\n'
        '      "legal_implication": "Legal implication of the difference",\n'
        '      "favor": "Party favored or disadvantaged by the difference"\n'
        '    }\n'
        '  ],\n'
        '  "similarity_score": 0.0\n'
        '}'
    ).format(file1_name=os.path.basename(file1_path), text1=text1, file2_name=os.path.basename(file2_path), text2=text2)

    # Calculate the required token count based on the prompt length
    prompt_tokens = len(client.encoding.encode(prompt))
    max_tokens = 4096 - prompt_tokens

    # Call the OpenAI API to get the comparison result
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a helpful legal assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.3
    )

    # Extract the content from the response
    result = response.choices[0].message['content'].strip()

    # Parse the JSON result
    comparison_result = json.loads(result)
    return comparison_result

# Example usage
parser = argparse.ArgumentParser(description='Compare two legal documents using the OpenAI API.')
parser.add_argument('file1', type=str, help='Path to the first document')
parser.add_argument('file2', type=str, help='Path to the second document')
args = parser.parse_args()

file1_path = args.file1
file2_path = args.file2

# Check if the input files exist
if not os.path.isfile(file1_path):
    raise ValueError(f"File not found: {file1_path}")

if not os.path.isfile(file2_path):
    raise ValueError(f"File not found: {file2_path}")

# Call the compare_files function and get the result
comparison_result = compare_files(file1_path, file2_path)

# Write the output data to a JSON file
output_file = "comparison_result.json"
with open(output_file, "w") as json_file:
    json.dump(comparison_result, json_file, indent=4)

print(f"Comparison result saved to {output_file}")

print("\nComparison Result:\n")
print(f"Similarity Score: {comparison_result['similarity_score']}")
print("\nDifferences:")
for diff in comparison_result['differences']:
    print(f"\nClause: {diff['clause']}")
    print(f"Description: {diff['description']}")
    print(f"Legal Implication: {diff['legal_implication']}")
    print(f"Favors: {diff['favor']}")