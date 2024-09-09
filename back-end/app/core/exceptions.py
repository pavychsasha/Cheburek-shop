from pydantic import BaseModel
from typing import Optional
from fastapi import HTTPException, status


class ProductNameDuplicationError(HTTPException):
    def __init__(self, name: str):
        # Customize the error message and response code here
        super().__init__(
            status_code=400, detail=f"Product with name '{name}' already exists."
        )
        self.name = name
