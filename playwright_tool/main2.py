import re

def extract_texts(snippet):
    pattern = r"toContainText\('([^']+)'\)"
    return re.findall(pattern, snippet)

def extract_buttons(snippet):
    pattern = r"getByRole\('row',\s*{ name:\s*'([^']+)' }\)"
    return re.findall(pattern, snippet)

def transform_fields(snippet):
    pattern = r"await page\.getByPlaceholder\('([^']+)'\)\.fill\('([^']+)'\);"
    matches = re.findall(pattern, snippet)
    
    transformed_lines = []
    for field_name, value in matches:
        transformed_lines.append(f'await enterField(page, "{field_name}", "{value}"),')
    
    return "\n  ".join(transformed_lines)

def transform_special_actions(snippet):
    lines = snippet.split('\n')
    for line in lines:
        line = line.strip()  # Remove leading and trailing whitespaces
        if line.startswith("await page.getByRole('button', { name: 'Finsh Now' }).click();"):
            return 'await finishNow(page)'
    return ""
def process_file_content(content):
    lines = content.split('\n')
    transformed_content = []
    
    to_contain_texts_buffer = []
    check_file_exists_buffer = []
    fill_party_details_buffer = []
    skip_next_line = False  # Flag to skip the next line
    
    for line in lines:
        if skip_next_line:  # Skip the current line
            skip_next_line = False
            continue
        
        # Check and transform toContainText lines
        if "toContainText" in line:
            to_contain_texts_buffer.append(line)
        else:
            if to_contain_texts_buffer:
                extracted_texts = extract_texts("\n".join(to_contain_texts_buffer))
                if extracted_texts:
                    transformed_content.append(f'await checkFileExists(page, {extracted_texts})')
                to_contain_texts_buffer = []

            # Check and transform getByRole('row') lines
            if "getByRole('row'" in line:
                check_file_exists_buffer.append(line)
            else:
                if check_file_exists_buffer:
                    extracted_buttons = extract_buttons("\n".join(check_file_exists_buffer))
                    if extracted_buttons:
                        transformed_content.append(f'await clickButtonByRowName(page, {extracted_buttons})')
                    check_file_exists_buffer = []

                # Check and transform getByPlaceholder lines
                if "getByPlaceholder" in line and ".fill" in line:
                    transformed_fields = transform_fields(line)
                    if transformed_fields:
                        transformed_content.append(transformed_fields)
                        continue
                elif "getByPlaceholder" in line and ".click" in line:
                    continue

                # Check and transform lines for filling party details
                if "await page.locator('[data-testid=\"issuer\"]').click();" in line:
                    skip_next_line = True  # Skip the next line
                elif "await page.getByRole('button', { name: 'Close' }).click();" in line:
                    transformed_content.append(line)  # Include this line in the output
                    continue  # Continue processing after this line
                
                # Check and transform special action lines
                transformed_special_action = transform_special_actions(line)
                if transformed_special_action:
                    transformed_content.append(transformed_special_action)
                    continue
                
                transformed_content.append(line)
    
    # Handle remaining buffered lines
    if to_contain_texts_buffer:
        extracted_texts = extract_texts("\n".join(to_contain_texts_buffer))
        if extracted_texts:
            transformed_content.append(f'await checkFileExists(page, {extracted_texts})')

    if check_file_exists_buffer:
        extracted_buttons = extract_buttons("\n".join(check_file_exists_buffer))
        if extracted_buttons:
            transformed_content.append(f'await clickButtonByRowName(page, {extracted_buttons})')
    
    return "\n".join(transformed_content)




def write_transformed_content_to_file(transformed_content, output_file):
    with open(output_file, 'w') as f:
        f.write(transformed_content)

# Example file content
file_content = """
  await expect(page.locator('#action-popup')).toContainText('Documents Hub');
  await expect(page.locator('#action-popup')).toContainText('Board Resolutions');
  await expect(page.locator('#action-popup')).toContainText('Key Terms');
"""

# Process the file content
transformed_file_content = process_file_content(file_content)

# Specify the output file path
output_file = 'transformed_script.py'

# Write the transformed content to the output file
write_transformed_content_to_file(transformed_file_content, output_file)

print(f"Transformed content has been written to {output_file}")