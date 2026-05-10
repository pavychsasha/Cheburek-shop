from typing import List, Optional
import uuid
from pydantic import ConfigDict, Field
from beanie import Document, Link


class CartItem(Document):
    model_config = ConfigDict(populate_by_name=True)

    product_id: uuid.UUID
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0, alias="count")
    total_price: float = Field(..., ge=0)

    class Settings:
        name = "cart_items"


class Cart(Document):
    session_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None
    items: List[Link[CartItem]] = Field(default_factory=list)
    total_count: int = Field(default=0, ge=0)
    total_price: float = Field(default=0, ge=0)

    class Settings:
        name = "carts"


class StoreSettings(Document):
    settings_key: str = Field(default="default")
    base_currency: str = Field(default="UAH")
    default_currency: str = Field(default="UAH")
    supported_currencies: list[str] = Field(
        default_factory=lambda: ["UAH", "USD", "EUR"]
    )
    currency_rates: dict[str, float] = Field(
        default_factory=lambda: {"UAH": 1.0, "USD": 0.024, "EUR": 0.022}
    )
    currency_symbols: dict[str, str] = Field(
        default_factory=lambda: {"UAH": "\u20b4", "USD": "$", "EUR": "\u20ac"}
    )
    product_languages: list[str] = Field(default_factory=lambda: ["en", "ukr"])
    auto_translate_products: bool = Field(default=True)

    class Settings:
        name = "store_settings"


all_document_models = [CartItem, Cart, StoreSettings]
