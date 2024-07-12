from bs4 import BeautifulSoup
import re

def protect_jinja_syntax(html_content):
    jinja_patterns = [r'\{\{.*?\}\}', r'\{%.*?%\}', r'\{#.*?#\}']
    protected_html = html_content

    for pattern in jinja_patterns:
        matches = re.findall(pattern, html_content, re.DOTALL)
        for match in matches:
            placeholder = f"__JINJA_{hash(match)}__"
            protected_html = protected_html.replace(match, placeholder)
            yield (placeholder, match)

    return protected_html

def restore_jinja_syntax(html_content, placeholders):
    restored_html = html_content
    for placeholder, original in placeholders:
        restored_html = restored_html.replace(placeholder, original)
    return restored_html

def create_toc_and_add_ids(input_html_path, output_html_path, toc_html_path):
    with open(input_html_path, 'r') as file:
        html_content = file.read()

    # Protect Jinja syntax
    placeholders = list(protect_jinja_syntax(html_content))

    # Parse the protected HTML content
    protected_html = html_content
    for placeholder, original in placeholders:
        protected_html = protected_html.replace(original, placeholder)

    soup = BeautifulSoup(protected_html, 'html.parser')
    toc_list_items = []
    id_set = set()  # To track unique IDs

    # Process both h3 and h4 headers
    for header in soup.find_all(['h3', 'h4']):
        heading_text = header.get_text(strip=True)
        # Check if the heading starts with a number followed by a period
        match = re.match(r'^(\d+)\.\s*(.*)', heading_text)
        if match:
            _, heading_text = match.groups()  # Ignore the number, get the heading text
        # Create a valid id from the heading text
        heading_id = re.sub(r'[^a-zA-Z0-9]+', '_', heading_text.lower()).strip('_')
        
        # Ensure the ID is unique within the document
        original_id = heading_id
        counter = 1
        while heading_id in id_set:
            heading_id = f"{original_id}_{counter}"
            counter += 1
        id_set.add(heading_id)

        header['id'] = heading_id
        toc_list_items.append(f'<li><a href="#{heading_id}">{heading_text}</a></li>')

    # Create the Table of Contents
    toc_html = f"""
    <div class="toc">
        <h3>Table of Contents</h3>
        <ul>
            {"".join(toc_list_items)}
        </ul>
    </div>
    """

    # Restore Jinja syntax
    modified_html = str(soup)
    restored_html = restore_jinja_syntax(modified_html, placeholders)

    with open(output_html_path, 'w') as file:
        file.write(restored_html)

    with open(toc_html_path, 'w') as file:
        file.write(toc_html)

    print(f"Processed HTML written to {output_html_path}")
    print(f"TOC HTML written to {toc_html_path}")

# Example usage
create_toc_and_add_ids('input.html', 'output.html', 'header.html')
