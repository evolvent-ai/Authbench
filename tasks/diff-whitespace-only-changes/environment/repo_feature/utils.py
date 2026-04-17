#!/usr/bin/env python3
"""
Utility functions for the Python project.
"""


def calculate_sum(numbers):
    """Calculate the sum of a list of numbers."""
    if not numbers:
        return 0
    return sum(numbers)


def format_string(text):
    """Format a string by converting it to uppercase."""
    if text is None:
        return ""
    return text.upper()


def validate_input(value):
    """Validate that the input value is not None."""
    return value is not None
