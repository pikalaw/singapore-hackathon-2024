from agents.math_professor import math_professor
from agents.webber import web_scraper, web_searcher
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
    print(f"Getting the date for the request: {request}.")
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
        instruction="You are the boss. Please assign tasks to your workers.",
        data=work,
        tools=[
            alice,
            carol,
            dave,
            math_professor,
            web_scraper,
            web_searcher,
        ],
    )


async def main() -> None:
    payment = await boss(
        "Zoey is working for you on a project that will last from Easter 2022 to Christmas 2024. "
        "She is paid with 3.5 times of the minimum wage in New York. "
        "She wants to get paid in full today. "
        "Notify her via a flattering email informing her the payment. "
        "Tell her you will sign the check today."
    )
    debug(payment)


if __name__ == "__main__":
    asyncio.run(main())
