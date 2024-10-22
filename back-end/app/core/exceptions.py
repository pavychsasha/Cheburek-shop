import uuid
from fastapi import HTTPException


class ProductNameDuplicationError(HTTPException):
    def __init__(self, name: str):
        # Using status code 409 (Conflict) for duplication errors
        super().__init__(
            status_code=409,
            detail=f"Product with name '{name}' already exists.",
        )
        self.name = name


class ProductNotFoundError(HTTPException):
    def __init__(self, product_id: uuid.UUID):
        # Using status code 404 (Not Found) for missing resources
        super().__init__(
            status_code=404,
            detail=f"Product with id '{product_id}' was not found",
        )
        self.product_id = product_id


class ProductCartNotFoundError(HTTPException):
    def __init__(self, product_id: uuid.UUID):
        # Using status code 404 (Not Found) for missing resources
        super().__init__(
            status_code=404,
            detail=f"Product with id '{product_id}' was not found.",
        )
        self.product_id = product_id


class InvalidSortFieldError(HTTPException):
    def __init__(self, field: str):
        # Using status code 400 (Bad Request) for invalid input errors
        super().__init__(
            status_code=400,
            detail=f"'{field}' is not a valid field for sorting.",
        )
        self.field = field


class InvalidProductOrderError(HTTPException):
    def __init__(self, order: str):
        # Using status code 400 (Bad Request) for invalid input errors
        super().__init__(
            status_code=400,
            detail=f"'{order}' is not a valid field for ordering.",
        )
        self.order = order


class InvalidUuidError(HTTPException):
    def __init__(self, uuid_str: str):
        # Using status code 400 (Bad Request) for invalid input errors
        super().__init__(
            status_code=400,
            detail=f"'{uuid_str}' is not a valid.",
        )
        self.uuid_str = uuid_str


class ZeroOrNegativeCartItemCountError(HTTPException):
    def __init__(self, item_count: int):
        # Using status code 400 (Bad Request) for invalid input errors
        super().__init__(
            status_code=400,
            detail=f"item count {item_count}' need to be greater than 0",
        )
        self.item_count = item_count


class ZeroProductsOrderError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail=f"Cart should contain products",
        )


class LanguageNotFoundError(HTTPException):
    def __init__(self, language_code: str):
        super().__init__(
            status_code=404,
            detail=f"language code {language_code}' was not found",
        )
        self.language_code = language_code