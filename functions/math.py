from datetime import datetime


async def add(a: float, b: float) -> float:
    """Adds two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    print(f"Adding {a} and {b}.")
    return a + b


async def subtract(a: float, b: float) -> float:
    """Subtracts one number from another.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference between the two numbers.
    """
    print(f"Subtracting {b} from {a}.")
    return a - b


async def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of the two numbers.
    """
    print(f"Multiplying {a} by {b}.")
    return a * b


async def divide(a: float, b: float) -> float:
    """Divides one number by another.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The result of dividing the two.
    """
    print(f"Dividing {a} by {b}.")
    return a / b


async def math(expression: str) -> float:
    """Evaluates a mathematical expression.

    Args:
        expression: The mathematical expression to evaluate.

    Returns:
        The result of the mathematical expression.
    """
    print(f"Evaluating the expression: {expression}.")
    return eval(expression)


async def diff_date(a: str, b: str) -> int:
    """Calculates the difference between two dates.

    Args:
        a: The first date in YYYY-MM-DD.
        b: The second date in YYYY-MM-DD.

    Returns:
        The number of days from a to b.
    """
    print(f"Calculating the difference between {a} and {b}.")
    date_format = "%Y-%m-%d"
    date_a = datetime.strptime(a, date_format).date()
    date_b = datetime.strptime(b, date_format).date()

    return (date_a - date_b).days
