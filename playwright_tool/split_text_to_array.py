import re

def extract_texts(snippet):
    pattern = r"toContainText\('([^']+)'\)"
    return re.findall(pattern, snippet)

snippet = """
 await expect(page.locator('#action-popup')).toContainText('Non-Disclosure Agreement');
  await expect(page.locator('#action-popup')).toContainText('Articles of Association');
  await expect(page.locator('#action-popup')).toContainText('Board Resolutions');
  await expect(page.locator('#action-popup')).toContainText('Privacy Policy');
  await expect(page.locator('#action-popup')).toContainText('Data Protection Policy');
  await expect(page.locator('#action-popup')).toContainText('Acceptable Use Policy');
  await expect(page.locator('#action-popup')).toContainText('IT Data Security Policy');
  await expect(page.locator('#action-popup')).toContainText('Cookie Policy');
  await expect(page.locator('#action-popup')).toContainText('Key Terms');
"""

texts_array = extract_texts(snippet)
print(f' await checkFileExists(page,{texts_array})')


print("-----------checkFileExists -------- ")
def extractButton(snippet):
    pattern = r"getByRole\('row',\s*{ name:\s*'([^']+)' }\)"
    return re.findall(pattern, snippet)

snippet = """
     await page.getByRole('row', { name: 'Acceptable Use Policy' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Articles Of Association' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Cookie Policy Cookie Policy ' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Data Protection Policy' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Disclosure Letter Creating a' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Information Memorandum' }).getByRole('button').click();
  await page.getByRole('row', { name: 'It Data Security Policy' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Non-Disclosure Agreement' }).getByRole('button').click();
  await page.getByRole('row', { name: 'Privacy Policy' }).getByRole('button').click();
"""

texts_array = extractButton(snippet)
print(f' await clickButtonByRowName(page,{texts_array})')

print("-----------clickButtonByRowName -------- ")



def transform_input(snippet):
    pattern = r"await page\.getByPlaceholder\('([^']+)'\)\.fill\('([^']+)'\);"
    matches = re.findall(pattern, snippet)
    
    transformed_lines = []
    for field_name, value in matches:
        transformed_lines.append(f'await enterField(page, "{field_name}", "{value}")')
    
    return transformed_lines

print("-----------enterField -------- ")


text = """
Non-Disclosure Agreement	
1.0
Key Terms	
1.0
Compliance Checklist	
1.0
Articles of Association	
1.0
Board Resolutions	
1.0
Shareholders Resolutions	
1.0
Equity Subscription Agreement	
1.0
Equity Shareholders Agreement	
1.0
Privacy Policy	
1.0
Data Protection Policy	
1.0
Acceptable Use Policy	
1.0
IT Data Security Policy	
1.0
Cookie Policy
"""

# Split the text into an array
text_array = [line.strip() for line in text.split('\n') if line.strip() and '1.0' not in line]


print(text_array)


print("-----------convert to an array -------- ")