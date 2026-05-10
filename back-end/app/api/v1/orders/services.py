import uuid

from app.api.v1.products.services import ProductsService
from app.core.exceptions import ZeroProductsOrderError
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import (
    Order,
    OrderProductAssociation,
    Cart,
    CartItem,
    Product,
    Country,
    State,
    City,
    Address,
)
from app.core import helpers
from app.api.v1.cart.services import CartService

from app.core.schemas.orders import (
    OrderAddress,
    ContactData,
    OrderResponseModel,
    OrderResponse,
    OrderProductResponseModel,
    OrderAddressInfo,
    OrderStatus,
)


class OrderService:

    @classmethod
    async def get_orders(cls, session: AsyncSession):
        stmt = (
            select(Order)
            .options(
                joinedload(Order.products)
                .selectinload(OrderProductAssociation.product)
                .selectinload(Product.translations),
                joinedload(Order.products)
                .selectinload(OrderProductAssociation.product)
                .selectinload(Product.tag_links),
                joinedload(Order.address)
                .joinedload(Address.city)
                .joinedload(City.state)
                .joinedload(State.country),  # Load Address for the Order
            )
            .order_by(Order.created_at)
        )
        result = await session.execute(stmt)
        return result.unique().scalars().all()

    @classmethod
    async def get_order(cls, session: AsyncSession, order_id: uuid.UUID):
        stmt = (
            select(Order)
            .options(
                joinedload(Order.products)
                .selectinload(OrderProductAssociation.product)
                .selectinload(Product.translations),
                joinedload(Order.products)
                .selectinload(OrderProductAssociation.product)
                .selectinload(Product.tag_links),
                joinedload(Order.address)
                .joinedload(Address.city)
                .joinedload(City.state)
                .joinedload(State.country),  # Load Address for the Order
            )
            .order_by(Order.created_at)
            .filter_by(order_id=order_id)
        )
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

    @classmethod
    async def get_orders_response(
        cls, session: AsyncSession, language: str = "en"
    ) -> OrderResponse:
        orders = await cls.get_orders(session)
        order_response = list()
        for order in orders:
            product_response = []
            for product_order_association in order.products:
                price = product_order_association.price
                product_status = product_order_association.product_status
                category = product_order_association.category

                # deleted products
                if (
                    product_status == "deleted"
                    or product_order_association.product is None
                ):
                    product_id = None
                    name = product_order_association.name
                    image_src = product_order_association.image_src
                else:
                    product = product_order_association.product
                    localized_product = await ProductsService.localize_product(
                        product, language
                    )
                    product_id = product.product_id
                    image_src = product.image_src
                    name = localized_product.name

                product_response.append(
                    OrderProductResponseModel(
                        product_id=product_id,
                        product_status=product_status,
                        image_src=image_src,
                        price=price,  # allways keeping the same price as was during ordering
                        category=category,  # allways keeping the same category as was during ordering
                        name=name,
                        quantity=product_order_association.quantity,
                    )
                )

            address = order.address
            address_response = OrderAddressInfo(
                street_name=address.street_name,
                street_number=address.street_number,
                apartment_number=address.apartment_number,
                zip_code=address.zip_code,
                city=address.city.city_name,
                state=address.city.state.state_name,
                country=address.city.state.country.country_name,
                products=product_response,
            )
            order_response.append(
                OrderResponseModel(
                    order_id=order.order_id,
                    created_at=order.created_at,
                    user_id=order.user_id,
                    status=order.status,
                    email=order.email,
                    customer_notes=order.customer_notes,
                    admin_notes=order.admin_notes,
                    total_price=order.total_price,
                    total_count=order.total_count,
                    products=product_response,
                    address=address_response,
                )
            )

        return OrderResponse(orders=order_response)

    @classmethod
    async def add_address_to_order(
        cls, session: AsyncSession, order: Order, address: OrderAddress
    ):
        # Retrieve or create the Country, State, and City with immediate flushes
        country = await helpers.get_or_create(
            session=session, model=Country, country_name=address.country.lower()
        )
        await session.flush()  # Ensure country_id is available

        state = await helpers.get_or_create(
            session=session,
            model=State,
            state_name=address.state.lower(),
            country_id=country.country_id,
        )
        await session.flush()  # Ensure state_id is available

        city = await helpers.get_or_create(
            session=session,
            model=City,
            city_name=address.city.lower(),
            state_id=state.state_id,
        )
        await session.flush()  # Ensure city_id is available

        # Create Address instance with the newly generated city_id
        new_address = Address(
            street_name=address.street_name,
            street_number=address.street_number,
            apartment_number=address.apartment_number,
            zip_code=address.zip_code,
            city_id=city.city_id,
        )

        # Add and flush the new Address instance to get its address_id
        session.add(new_address)
        await session.flush()  # Address is flushed, so address_id is now set

        # Now assign the address_id to the Order
        order.address_id = new_address.address_id
        order.address = new_address  # Associate the Order with the Address object

        # Add and commit the Order to persist the relationship
        session.add(order)
        await session.commit()  # Commit all changes to ensure data integrity

    @classmethod
    async def add_products_to_order(
        cls,
        session: AsyncSession,
        order: Order,
        products: list[CartItem],
    ):
        """
        Add multiple products to an order.

        Args:
            session: The active database session.
            order: The order to which the products should be added.
            products_data: A list of dictionaries with 'product_id' and 'quantity'.

        Example of products_data:
        [
            {"product_id": <product_id_1>, "quantity": 2},
            {"product_id": <product_id_2>, "quantity": 1}
        ]
        """
        association_list = []
        for product in products:
            product_in_database = await ProductsService.get_product(
                session=session, product_id=product.product_id
            )
            # We prevent this behaviour in CartService, so raising exception on the first possible case
            CartService.check_products_quantity(
                product=product_in_database, cart_item_count=product.quantity
            )
            localized_product = await ProductsService.localize_product(
                product_in_database, "en"
            )
            association_list.append(
                OrderProductAssociation(
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=product.quantity,
                    name=localized_product.name,
                    price=product_in_database.price,
                    category=product_in_database.category,
                    image_src=product_in_database.image_src,
                )
            )

        session.add_all(association_list)
        await session.flush()

        order.total_count = sum(product.quantity for product in products)
        order.total_price = sum(
            product.price * product.quantity for product in products
        )
        session.add(order)
        await session.commit()

    @classmethod
    async def reduce_products_stock_quantity_after_order(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
    ):
        updated_products = []
        order = await cls.get_order(session, order_id)
        for order_product_association in order.products:
            product = order_product_association.product
            product.stock_quantity -= order_product_association.quantity
            updated_products.append(product)
        session.add_all(updated_products)
        await session.commit()

    @classmethod
    async def make_order(
        cls,
        contact_data: ContactData,
        address: OrderAddress,
        session: AsyncSession,
        mongo_cart: Cart,
    ):
        if not mongo_cart.items:
            raise ZeroProductsOrderError()

        # Step 1: Create Address and flush to get address_id
        country = await helpers.get_or_create(
            session=session, model=Country, country_name=address.country.lower()
        )
        await session.flush()  # Ensure country_id is available

        state = await helpers.get_or_create(
            session=session,
            model=State,
            state_name=address.state.lower(),
            country_id=country.country_id,
        )
        await session.flush()  # Ensure state_id is available

        city = await helpers.get_or_create(
            session=session,
            model=City,
            city_name=address.city.lower(),
            state_id=state.state_id,
        )
        await session.flush()  # Ensure city_id is available

        new_address = Address(
            street_name=address.street_name,
            street_number=address.street_number,
            apartment_number=address.apartment_number,
            zip_code=address.zip_code,
            city_id=city.city_id,
        )
        session.add(new_address)
        await session.flush()  # Address is flushed, so address_id is now set

        # Step 2: Now create the Order with the generated address_id
        new_order = Order(
            order_id=uuid.uuid4(),
            email=contact_data.email,
            customer_notes=contact_data.customer_notes,
            address_id=new_address.address_id,
        )
        session.add(new_order)
        await session.flush()  # Generate order_id

        # Step 3: Add products to the order
        await cls.add_products_to_order(
            session=session,
            products=mongo_cart.items,
            order=new_order,
        )

        # Step 4: Reduce product stock quantities
        await cls.reduce_products_stock_quantity_after_order(
            session=session, order_id=new_order.order_id
        )

        # Step 5: Clean up purchased cart and invalidate product cache
        await CartService.delete_cart_items(cart=mongo_cart)
        await ProductsService.invalidate_products_cache()

        # Commit everything at the end
        await session.commit()

    @classmethod
    async def delete_order(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
    ):
        stmt = delete(Order).filter(Order.order_id == order_id)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def update_order_status(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
        status: OrderStatus,
    ) -> Order:
        order = await cls.get_order(session=session, order_id=order_id)
        if order is None:
            raise ValueError("Order not found")
        order.status = status
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @classmethod
    async def update_order_notes(
        cls,
        session: AsyncSession,
        order_id: uuid.UUID,
        admin_notes: str | None,
    ) -> Order:
        order = await cls.get_order(session=session, order_id=order_id)
        if order is None:
            raise ValueError("Order not found")
        order.admin_notes = admin_notes
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order

    @classmethod
    async def delete_all_products(cls, session: AsyncSession):
        stmt = delete(Order)
        await session.execute(stmt)
        await session.commit()
