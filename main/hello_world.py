import google.generativeai as genai


def send_message(recipient: str, text: str) -> bool:
    """Sends a message to the recipient.

    Args:
      recipient: The recipient of the message.
      text: The text of the message.

    Returns:
      True if the message was sent successfully.
    """
    print(f"I sent a message to {recipient} saying {text}.")
    return True


model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=genai.GenerationConfig(
        temperature=0.7,
    ),
    system_instruction="Be cute.",
    tools=[
        genai.types.Tool([send_message]),
    ],
)
response = model.generate_content(contents="Send a message to John saying hello.")
print(response)
