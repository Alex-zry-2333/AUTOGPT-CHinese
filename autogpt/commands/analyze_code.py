"""Code evaluation module."""
from __future__ import annotations

from autogpt.commands.command import command
from autogpt.llm import call_ai_function


@command(
    "analyze_code",
    "分析代码",
    '"code": "<full_code_string>"',
)
def analyze_code(code: str) -> list[str]:
    """
    A function that takes in a string and returns a response from create chat
      completion api call.

    Parameters:
        code (str): Code to be evaluated.
    Returns:
        A result string from create chat completion. A list of suggestions to
            improve the code.
    """

    function_string = "def analyze_code(code: str) -> list[str]:"
    args = [code]
    description_string = (
        "分析给出的代码并列出一系列优化建议。"
    )

    return call_ai_function(function_string, args, description_string)
