from datetime import datetime
from devtools import debug
from goog.agent import agent
from pydantic import BaseModel, Field


def alice(request: str) -> str:
    """Alice is an expert in flattery languages.

    Args:
        request: The request to Alice.

    Returns:
        The response from Alice.
    """
    print(f"Flattering the message: {request}.")
    return agent(
        str,
        instruction="You are an expert with flattering languages. Please flatter me.",
        data=request,
    )


def add(a: int, b: int) -> int:
    """Adds two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of the two numbers.
    """
    print(f"Adding {a} and {b}.")
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtracts one number from another.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The difference between the two numbers.
    """
    print(f"Subtracting {b} from {a}.")
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiplies two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The product of the two numbers.
    """
    print(f"Multiplying {a} by {b}.")
    return a * b


def divide(a: int, b: int) -> int:
    """Divides one number by another.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The quotient of the two numbers.
    """
    print(f"Dividing {a} by {b}.")
    return a // b


def diff_date(a: str, b: str) -> int:
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


def bob(request: str) -> str:
    """Bob is an expert in math.

    Args:
        request: The request to Bob.

    Returns:
        The response from Bob.
    """
    return agent(
        str,
        instruction="You are an expert with math. Please solve this math problem.",
        data=request,
        tools=[add, subtract, multiply, divide, diff_date],
    )


def send_mail(recipient: str, sender: str, subject: str, body: str) -> bool:
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


def carol(request: str) -> str:
    """Carol is an emailer.

    She can send email on behalf of others.

    Args:
        request: The request to Carol.

    Returns:
        The response from Carol.
    """
    return agent(
        str,
        instruction="You are an expert with email. Please send an email on behalf of John to Bob.",
        data=request,
        tools=[send_mail],
    )


def current_datetime() -> str:
    """Returns the current date and time.

    Returns:
        The current date and time.
    """
    print("Getting the current date and time.")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def dave(request: str) -> str:
    """Dave knows the current date and time. He also knows all dates for holidays and events.

    Args:
        request: The request to Dave.

    Returns:
        The response from Dave.
    """
    return agent(
        str,
        instruction="You have the clock to tell the current date and time.",
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


def boss(work: str) -> Payment:
    return agent(
        Payment,
        instruction="You are the boss. Please assign tasks to Alice, Bob, and Carol.",
        data=work,
        tools=[alice, bob, carol, dave],
    )


def main() -> None:
    payment = boss(
        f"Zoey will receive a payment in the sum of $18 for every day between Easter 2022 and Christmas 2024. "
        "Ascertain and total sum. "
        "Then, notify her via a flattering email informing her the total sum."
    )
    debug(payment)


if __name__ == "__main__":
    main()
