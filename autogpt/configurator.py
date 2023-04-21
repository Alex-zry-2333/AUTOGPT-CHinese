"""Configurator module."""
import click
from colorama import Back, Fore, Style

from autogpt import utils
from autogpt.config import Config
from autogpt.logs import logger
from autogpt.memory import get_supported_memory_backends

CFG = Config()


def create_config(
    continuous: bool,
    continuous_limit: int,
    ai_settings_file: str,
    skip_reprompt: bool,
    speak: bool,
    debug: bool,
    gpt3only: bool,
    gpt4only: bool,
    memory_type: str,
    browser_name: str,
    allow_downloads: bool,
    skip_news: bool,
) -> None:
    """Updates the config object with the given arguments.

    Args:
        continuous (bool): Whether to run in continuous mode
        continuous_limit (int): The number of times to run in continuous mode
        ai_settings_file (str): The path to the ai_settings.yaml file
        skip_reprompt (bool): Whether to skip the re-prompting messages at the beginning of the script
        speak (bool): Whether to enable speak mode
        debug (bool): Whether to enable debug mode
        gpt3only (bool): Whether to enable GPT3.5 only mode
        gpt4only (bool): Whether to enable GPT4 only mode
        memory_type (str): The type of memory backend to use
        browser_name (str): The name of the browser to use when using selenium to scrape the web
        allow_downloads (bool): Whether to allow Auto-GPT to download files natively
        skips_news (bool): Whether to suppress the output of latest news on startup
    """
    CFG.set_debug_mode(False)
    CFG.set_continuous_mode(False)
    CFG.set_speak_mode(False)

    if debug:
        logger.typewriter_log("Debug模式: ", Fore.GREEN, "开启")
        CFG.set_debug_mode(True)

    if continuous:
        logger.typewriter_log("持续模式: ", Fore.RED, "开启")
        logger.typewriter_log(
            "警告: ",
            Fore.RED,
            "不推荐使用持续模式. 此模式存在风险，可能会让你的AI持续执行下去"
            "并执行没有被你授权的指令动作"
            "使用需谨慎，自负风险。",
        )
        CFG.set_continuous_mode(True)

        if continuous_limit:
            logger.typewriter_log(
                "持续限额: ", Fore.GREEN, f"{continuous_limit}"
            )
            CFG.set_continuous_limit(continuous_limit)

    # Check if continuous limit is used without continuous mode
    if continuous_limit and not continuous:
        raise click.UsageError("--continuous-limit can only be used with --continuous")

    if speak:
        logger.typewriter_log("语音模式: ", Fore.GREEN, "开启")
        CFG.set_speak_mode(True)

    if gpt3only:
        logger.typewriter_log("GPT3.5模式: ", Fore.GREEN, "开启")
        CFG.set_smart_llm_model(CFG.fast_llm_model)

    if gpt4only:
        logger.typewriter_log("GPT4模式: ", Fore.GREEN, "开启")
        CFG.set_fast_llm_model(CFG.smart_llm_model)

    if memory_type:
        supported_memory = get_supported_memory_backends()
        chosen = memory_type
        if chosen not in supported_memory:
            logger.typewriter_log(
                "只支持一下记忆后台模式: ",
                Fore.RED,
                f"{supported_memory}",
            )
            logger.typewriter_log("默认至: ", Fore.YELLOW, CFG.memory_backend)
        else:
            CFG.memory_backend = chosen

    if skip_reprompt:
        logger.typewriter_log("跳过重新指令: ", Fore.GREEN, "开启")
        CFG.skip_reprompt = True

    if ai_settings_file:
        file = ai_settings_file

        # Validate file
        (validated, message) = utils.validate_yaml_file(file)
        if not validated:
            logger.typewriter_log("文件校验失败", Fore.RED, message)
            logger.double_check()
            exit(1)

        logger.typewriter_log("使用AI配置文件:", Fore.GREEN, file)
        CFG.ai_settings_file = file
        CFG.skip_reprompt = True

    if browser_name:
        CFG.selenium_web_browser = browser_name

    if allow_downloads:
        logger.typewriter_log("本地下载:", Fore.GREEN, "开启")
        logger.typewriter_log(
            "警告: ",
            Fore.YELLOW,
            f"{Back.LIGHTYELLOW_EX}Auto-GPT将开启下载并存储文件至你的本地电脑中。{Back.RESET} "
            + "建议您仔细监控它下载的任何文件。",
        )
        logger.typewriter_log(
            "警告: ",
            Fore.YELLOW,
            f"{Back.RED + Style.BRIGHT}请始终记住，永远不要打开您不确定的文件！{Style.RESET_ALL}",
        )
        CFG.allow_downloads = True

    if skip_news:
        CFG.skip_news = True
