from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Metadata with naming convention for constraints
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship to RestaurantPizza
    restaurant_pizzas = relationship(
        "RestaurantPizza", back_populates="restaurant", cascade="all, delete-orphan"
    )

    # Association proxy to access pizzas directly
    pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serialization rules to prevent circular references
    serialize_rules = ("-restaurant_pizzas.restaurant", "-pizzas.restaurant_pizzas")

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationship to RestaurantPizza
    restaurant_pizzas = relationship(
        "RestaurantPizza", back_populates="pizza", cascade="all, delete-orphan"
    )

    # Serialization rules to prevent circular references
    serialize_rules = ("-restaurant_pizzas.pizza", "-restaurants.restaurant_pizzas")

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign keys
    restaurant_id = db.Column(db.Integer, ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey("pizzas.id"), nullable=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")

    # Serialization rules to prevent circular references
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # Custom validation for price
    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    # Custom to_dict method for serialization
    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
        }

        if only:
            if "pizza" in only and self.pizza:
                data["pizza"] = self.pizza.to_dict()
            if "restaurant" in only and self.restaurant:
                data["restaurant"] = self.restaurant.to_dict()

        return data

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
