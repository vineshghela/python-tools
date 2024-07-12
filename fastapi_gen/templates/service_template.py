from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from app import schemas
from app.models.{module} import {schema_class_camel}
from app.crud.{module} import crud_{schema_class_non_caps}

class {class_name}:
    @staticmethod
    def create_{table_name}(db: Session, {table_name}: schemas.{schema_class_camel}Create) -> {schema_class_camel}:
        return crud_{table_name}.create_{table_name}(db=db, {table_name}={table_name})

    @staticmethod
    def get_{table_name}(db: Session, {table_name}_id: UUID) -> {schema_class_camel}:
        return crud_{table_name}.get_{table_name}(db=db, {table_name}_id={table_name}_id)

    @staticmethod
    def get_{table_name_plural}(db: Session, skip: int, limit: int) -> List[{schema_class_camel}]:
        return crud_{table_name}.get_{table_name_plural}(db=db, skip=skip, limit=limit)

    @staticmethod
    def update_{table_name}(db: Session, {table_name}_id: UUID, {table_name}_update: schemas.{schema_class_camel}Update) -> {schema_class_camel}:
        return crud_{table_name}.update_{table_name}(db=db, {table_name}_id={table_name}_id, {table_name}_update={table_name}_update)

    @staticmethod
    def delete_{table_name}(db: Session, {table_name}_id: UUID) -> {schema_class_camel}:
        return crud_{table_name}.delete_{table_name}(db=db, {table_name}_id={table_name}_id)
