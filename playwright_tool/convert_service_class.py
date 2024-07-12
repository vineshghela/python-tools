import os
import re
from pathlib import Path

def convert_service_class(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Match the method names and the corresponding CRUD functions
    pattern = re.compile(r"def (\w+)\(db: Session, (\w+): (.+?)\) -> (.+?):\n\s+return (\w+)\(db=db, (\w+)=\2\)")

    def wrap_with_error_handling(match):
        method_name = match.group(1)
        param_name = match.group(2)
        param_type = match.group(3)
        return_type = match.group(4)
        crud_function = match.group(5)
        crud_param = match.group(6)

        if method_name.startswith("create"):
            return f"""def {method_name}(db: Session, {param_name}: {param_type}) -> {return_type}:
    try:
        return {crud_function}(db=db, {crud_param}={param_name})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""
        
        if method_name.startswith("get") and "s" not in method_name:
            return f"""def {method_name}(db: Session, {param_name}_id: UUID) -> {return_type}:
    db_{param_name} = {crud_function}(db=db, {param_name}_id={param_name}_id)
    if not db_{param_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{return_type} not found")
    return db_{param_name}
"""

        if method_name.startswith("get") and "s" in method_name:
            return f"""def {method_name}(db: Session, skip: int, limit: int) -> List[{return_type}]:
    try:
        return {crud_function}(db=db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""

        if method_name.startswith("update"):
            return f"""def {method_name}(db: Session, {param_name}_id: UUID, {param_name}_update: {param_type}) -> {return_type}:
    db_{param_name} = {crud_function.split('_')[1]}_{crud_function.split('_')[2]}(db=db, {param_name}_id={param_name}_id)
    if not db_{param_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{return_type} not found")
    
    try:
        return {crud_function}(db=db, {param_name}_id={param_name}_id, {param_name}_update={param_name}_update)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""

        if method_name.startswith("delete"):
            return f"""def {method_name}(db: Session, {param_name}_id: UUID) -> {return_type}:
    db_{param_name} = {crud_function.split('_')[1]}_{crud_function.split('_')[2]}(db=db, {param_name}_id={param_name}_id)
    if not db_{param_name}:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{return_type} not found")
    
    try:
        return {crud_function}(db=db, {param_name}_id={param_name}_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
"""

    # Replace the methods in the content
    content = re.sub(pattern, wrap_with_error_handling, content)

    # Add the necessary imports if not present
    if "from fastapi import HTTPException, status" not in content:
        content = "from fastapi import HTTPException, status\n" + content

    with open(file_path, 'w') as file:
        file.write(content)

def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                convert_service_class(file_path)

# Update the directory path to your service classes directory
directory_path = "service"
process_directory(directory_path)
