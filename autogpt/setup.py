"""Set up the AI and its goals"""
from colorama import Fore, Style

from autogpt import utils
from autogpt.config.ai_config import AIConfig
from autogpt.logs import logger


def prompt_user() -> AIConfig:
    """Prompt the user for input

    Returns:
        AIConfig: The AIConfig object containing the user's input
    """
    ai_name = ""
    # Construct the prompt
    logger.typewriter_log(
        "欢迎使用RealHossie的Auto-GPT中文版！",  # Welcome to Auto-GPT!
        Fore.GREEN, # Green
        "执行后缀 '--help' 获取更多信息。",    # run with '--help' for more information.
        speak_text=True,
    )

    logger.typewriter_log(
        "欢迎来到我的频道交流：https://www.youtube.com/@Hossie",
        Fore.LIGHTBLUE_EX,  # Light Blue
        speak_text=True,
    )

    logger.typewriter_log(
        "新建一个AI助手:",
        Fore.GREEN,
        "给你AI助手起一个名字和赋予它一个角色，什么都不输入将使用默认值。",
        speak_text=True,
    )

    # Get AI Name from User
    logger.typewriter_log(
        "你AI的名字叫: ", Fore.GREEN, "例如, '企业家-GPT'"
    )
    ai_name = utils.clean_input("AI名字: ")
    if ai_name == "":
        ai_name = "企业家-GPT"

    logger.typewriter_log(
        f"{ai_name} 在这儿呢!", Fore.LIGHTBLUE_EX, "我听从您的吩咐。", speak_text=True
    )

    # Get AI Role from User
    logger.typewriter_log(
        "描述你AI的角色: ",
        Fore.GREEN,
        "例如, '一个自动帮助你策划与经营业务的人工智能帮手，目标专注于提升你的净资产。'",
    )
    ai_role = utils.clean_input(f"{ai_name} 是: ")
    if ai_role == "":
        ai_role = "一个自动帮助你策划与经营业务的人工智能帮手，目标专注于提升你的净资产。"

    # Enter up to 5 goals for the AI
    logger.typewriter_log(
        "为你的AI定义最多5个目标: ",
        Fore.GREEN,
        "例如: \n提升净资产, 增长Twitter账户, 自动化策划与管理多条业务线'",
    )
    print("什么都不输入将加载默认值，输入结束后直接按回车。", flush=True)
    ai_goals = []
    for i in range(5):
        ai_goal = utils.clean_input(f"{Fore.LIGHTBLUE_EX}目标{Style.RESET_ALL} {i+1}: ")
        if ai_goal == "":
            break
        ai_goals.append(ai_goal)
    if not ai_goals:
        ai_goals = [
            "提升净资产",
            "增长Twitter账户",
            "自动化策划与管理多条业务线",
        ]

    return AIConfig(ai_name, ai_role, ai_goals)
