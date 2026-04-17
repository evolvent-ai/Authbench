#!/usr/bin/env python3
"""Data model classes for the application."""


class User:
    """Represents a user in the system."""

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def get_info(self):
        return f"User: {self.name}, Email: {self.email}"


class Product:
    """Represents a product in the system."""

    def __init__(self, product_id, name, price):
        self.id = product_id
        self.name = name
        self.price = price

    def get_price(self):
        return self.price


def create_user(name, email):
    return User(name, email)
