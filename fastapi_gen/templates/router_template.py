from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app import schemas
from app.dependencies import get_db
from app.services.{module}.service_{table_name} import {schema_class_camel}Service
from app.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.{schema_class_camel})
def create_{table_name}(
    {table_name}: schemas.{schema_class_camel}Create,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    return {schema_class_camel}Service.create_{table_name}(db=db, {table_name}={table_name})

@router.get("/{table_name}_id", response_model=schemas.{schema_class_camel})
def read_{table_name}(
    {table_name}_id: UUID = Path(..., description="UUID of the {table_name}"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_{table_name} = {schema_class_camel}Service.get_{table_name}(db=db, {table_name}_id={table_name}_id)
    if db_{table_name} is None:
        raise HTTPException(status_code=404, detail=f"{model_name} not found")
    return db_{table_name}

@router.get("/", response_model=List[schemas.{schema_class_camel}])
def read_{table_name_plural}(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    return {schema_class_camel}Service.get_{table_name_plural}(db=db, skip=skip, limit=limit)

@router.put("/{table_name}_id", response_model=schemas.{schema_class_camel})
def update_{table_name}(
    {table_name}_id: UUID,
    {table_name}: schemas.{schema_class_camel}Update,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    return {schema_class_camel}Service.update_{table_name}(db=db, {table_name}_id={table_name}_id, {table_name}_update={table_name})

@router.delete("/{table_name}_id", response_model=schemas.{schema_class_camel})
def delete_{table_name}(
    {table_name}_id: UUID,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    return {schema_class_camel}Service.delete_{table_name}(db=db, {table_name}_id={table_name}_id)
