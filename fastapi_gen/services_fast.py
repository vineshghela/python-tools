import re
import os


def camel_case(name):
    components = name.split('_')
    return ''.join(x.capitalize() for x in components)

def generate_file(table_name, module_name,template_file, output_prefix, output_folder):
    # Read the template file
    with open(template_file, 'r') as file:
        template = file.read()

    # Define replacements for all operations
    replacements = {
        'table_name': table_name,
        'table_name_plural': f"{table_name}s",
        'model_name': table_name.capitalize(),
        'module': f"{module_name}",  # Adjust based on your schema module path
        'schema_module': f"{module_name}.{table_name}",  # Adjust based on your schema module path
        'schema_class': f"{table_name.capitalize()}",
        'schema_class_non_caps': f"{table_name}",
        'schema_create_class': f"{camel_case(table_name)}Create",
        'schema_update_class': f"{camel_case(table_name)}Update",
        'schema_class_camel' : camel_case(table_name),
        'class_name': f"{camel_case(table_name)}Service",
        'service_module': f"services_{table_name}",
        'service_class': f"{table_name.capitalize()}Service"
    }

    # Replace placeholders in the template
    for key, value in replacements.items():
        template = template.replace('{' + key + '}', value)

    # Replace any remaining placeholders
    template = re.sub(r'\{.*?\}', '', template)

    # Define the output file path and name
    output_filename = os.path.join(output_folder, f"{output_prefix}_{table_name}.py")

    # Write the generated content to the output file
    with open(output_filename, 'w') as file:
        file.write(template)

    print(f"File '{output_filename}' has been generated.")

def main():
    # Get input from the user
    table_name = input("Enter the table name: ")
    module_name = input("Enter the module name: ")

    # Define template files and their corresponding output prefixes
    templates = [
        ('templates/crud_template.py', 'crud'),
        ('templates/router_template.py', 'router'),
        ('templates/service_template.py', 'service'),
        ('templates/main_template.py', 'main'),
        ('templates/init_template.py', 'init')
    ]

    # Create a folder for generated files if it doesn't exist
    output_folder = 'generated_files'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Generate files for each template
    for template_file, output_prefix in templates:
        if os.path.exists(template_file):
            generate_file(table_name, module_name,template_file, output_prefix, output_folder)
        else:
            print(f"Template file '{template_file}' not found.")

if __name__ == "__main__":
    main()