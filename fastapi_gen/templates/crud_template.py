from sqlalchemy.orm import Session
from uuid import UUID
from uuid import uuid4
from app.models import {schema_class_camel}
from app.schemas.{schema_module} import {schema_update_class}, {schema_create_class}

def create_{table_name}(db: Session, {table_name}: {schema_create_class}):
    db_{table_name} = {schema_class_camel}(**{table_name}.dict())
    db.add(db_{table_name})
    db.commit()
    db.refresh(db_{table_name})
    return db_{table_name}

def get_{table_name}(db: Session, {table_name}_id: UUID):
    return db.query({schema_class_camel}).filter({schema_class_camel}.id == {table_name}_id).first()

def get_{table_name_plural}(db: Session, skip: int = 0, limit: int = 10):
    return db.query({schema_class_camel}).offset(skip).limit(limit).all()

def update_{table_name}(db: Session, {table_name}_id: UUID, {table_name}_update: {schema_update_class}):
    db_{table_name} = get_{table_name}(db, {table_name}_id)
    if not db_{table_name}:
        return None
    for key, value in {table_name}_update.dict().items():
        setattr(db_{table_name}, key, value)
    db.commit()
    db.refresh(db_{table_name})
    return db_{table_name}

def delete_{table_name}(db: Session, {table_name}_id: UUID):
    db_{table_name} = get_{table_name}(db, {table_name}_id)
    if not db_{table_name}:
        return None
    db.delete(db_{table_name})
    db.commit()
    return db_{table_name}
