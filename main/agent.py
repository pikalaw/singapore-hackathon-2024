import asyncio
from datetime import datetime
from devtools import debug
from goog.agent import agent
from pydantic import BaseModel, Field


async def alice(request: str) -> str:
    """Alice is an expert in flattery languages.

    Args:
        request: The request to Alice.

    Returns:
        The response from Alice.
    """
    print(f"Flattering the message: {request}.")
    return await agent(
        str,
        instruction="You are an expert with flattering languages. Please flatter me.",
        data=request,
    )


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


async def bob(request: str) -> str:
    """Bob is an expert in math. Can handle arithmetic operations and date differences.

    Args:
        request: The request to Bob.

    Returns:
        The response from Bob.
    """
    return await agent(
        str,
        instruction="You are an expert with math. Please solve this math problem.",
        data=request,
        tools=[add, subtract, multiply, divide, math, diff_date],
    )


async def send_mail(recipient: str, sender: str, subject: str, body: str) -> bool:
    """Sends an email.

    Args:
        recipient: The recipient of the email.
        sender: The sender of the email.
        subject: The subject of the email.
        body: The text of the email.

    Returns:
        True if the email was sent successfully.
    """
    print(
        f"Attempting to send an email to {recipient} from {sender} with subject {subject} saying {body}."
    )
    return True


async def carol(request: str) -> str:
    """Carol is an emailer.

    She can send email on behalf of others.

    Args:
        request: The request to Carol.

    Returns:
        The response from Carol.
    """
    return await agent(
        str,
        instruction="You are an expert with email. Please send an email on behalf of John to Bob.",
        data=request,
        tools=[send_mail],
    )


async def current_datetime() -> str:
    """Returns the current date and time.

    Returns:
        The current date and time.
    """
    print("Getting the current date and time.")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def dave(request: str) -> str:
    """Dave knows the current date and time. He also knows all dates for holidays and events.

    Args:
        request: The request to Dave.

    Returns:
        The response from Dave.
    """
    return await agent(
        str,
        instruction="""You have the clock to tell the current date and time.

Easter Dates:
Easter dates vary each year as it is based on the lunar calendar. Here are the dates for Easter Sunday:

2020: April 12
2021: April 4
2022: April 17
2023: April 9
2024: March 31
2025: April 20

Christmas Dates:
Christmas is always on December 25th every year.

2020: December 25
2021: December 25
2022: December 25
2023: December 25
2024: December 25
2025: December 25
""",
        data=request,
        tools=[current_datetime],
    )


class Date(BaseModel):
    """A date entity."""

    day: int = Field(
        description="the day of the month",
    )
    month: int = Field(
        description="the month of the year",
    )
    year: int = Field(
        description="the year",
    )


class Payment(BaseModel):
    """A payment entity."""

    amount: float = Field(
        description="the amount of the payment",
    )
    recipient: str = Field(
        description="the recipient of the payment",
    )
    date: Date = Field(
        description="the date of the payment",
    )


async def boss(work: str) -> Payment:
    return await agent(
        Payment,
        instruction="You are the boss. Please assign tasks to Alice, Bob, Carol, and Dave.",
        data=work,
        tools=[alice, bob, carol, dave],
    )


async def main() -> None:
    payment = await boss(
        f"Zoey will receive a payment in the sum of $18 for every day between Easter 2022 and Christmas 2024. "
        "Ascertain and total sum. "
        "Notify her via a flattering email informing her the total sum. "
        "Tell her you will sign the check today."
    )
    debug(payment)


if __name__ == "__main__":
    asyncio.run(main())
