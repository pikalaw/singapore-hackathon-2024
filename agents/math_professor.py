from functions import math
from goog.agent import agent


async def math_professor(request: str) -> str:
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
        tools=[
            math.math,
            math.diff_date,
        ],
        model_name="gemini-1.5-flash-latest",
    )
