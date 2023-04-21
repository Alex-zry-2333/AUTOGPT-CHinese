"""File operations for AutoGPT"""
from __future__ import annotations

import os
import os.path
from typing import Generator

import requests
from colorama import Back, Fore
from requests.adapters import HTTPAdapter, Retry

from autogpt.commands.command import command
from autogpt.config import Config
from autogpt.spinner import Spinner
from autogpt.utils import readable_file_size
from autogpt.workspace import WORKSPACE_PATH, path_in_workspace

CFG = Config()
LOG_FILE = "file_logger.txt"
LOG_FILE_PATH = WORKSPACE_PATH / LOG_FILE


def check_duplicate_operation(operation: str, filename: str) -> bool:
    """Check if the operation has already been performed on the given file

    Args:
        operation (str): The operation to check for
        filename (str): The name of the file to check for

    Returns:
        bool: True if the operation has already been performed on the file
    """
    log_content = read_file(LOG_FILE)
    log_entry = f"{operation}: {filename}\n"
    return log_entry in log_content


def log_operation(operation: str, filename: str) -> None:
    """Log the file operation to the file_logger.txt

    Args:
        operation (str): The operation to log
        filename (str): The name of the file the operation was performed on
    """
    log_entry = f"{operation}: {filename}\n"

    # Create the log file if it doesn't exist
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("文件操作记录器 ")

    append_to_file(LOG_FILE, log_entry, shouldLog=False)


def split_file(
    content: str, max_length: int = 4000, overlap: int = 0
) -> Generator[str, None, None]:
    """
    Split text into chunks of a specified maximum length with a specified overlap
    between chunks.

    :param content: The input text to be split into chunks
    :param max_length: The maximum length of each chunk,
        default is 4000 (about 1k token)
    :param overlap: The number of overlapping characters between chunks,
        default is no overlap
    :return: A generator yielding chunks of text
    """
    start = 0
    content_length = len(content)

    while start < content_length:
        end = start + max_length
        if end + overlap < content_length:
            chunk = content[start : end + overlap - 1]
        else:
            chunk = content[start:content_length]

            # Account for the case where the last chunk is shorter than the overlap, so it has already been consumed
            if len(chunk) <= overlap:
                break

        yield chunk
        start += max_length - overlap


@command("read_file", "Read file", '"filename": "<filename>"')
def read_file(filename: str) -> str:
    """Read a file and return the contents

    Args:
        filename (str): The name of the file to read

    Returns:
        str: The contents of the file
    """
    try:
        filepath = path_in_workspace(filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"错误: {str(e)}"


def ingest_file(
    filename: str, memory, max_length: int = 4000, overlap: int = 200
) -> None:
    """
    Ingest a file by reading its content, splitting it into chunks with a specified
    maximum length and overlap, and adding the chunks to the memory storage.

    :param filename: The name of the file to ingest
    :param memory: An object with an add() method to store the chunks in memory
    :param max_length: The maximum length of each chunk, default is 4000
    :param overlap: The number of overlapping characters between chunks, default is 200
    """
    try:
        print(f"操作文件 {filename}")
        content = read_file(filename)
        content_length = len(content)
        print(f"文件长度: {content_length} 字符")

        chunks = list(split_file(content, max_length=max_length, overlap=overlap))

        num_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            print(f"注入chunk {i + 1} / {num_chunks} 至记忆")
            memory_to_add = (
                f"文件名: {filename}\n" f"内容分块#{i + 1}/{num_chunks}: {chunk}"
            )

            memory.add(memory_to_add)

        print(f"完成注入 {num_chunks} chunks 从 {filename}.")
    except Exception as e:
        print(f"注入文件错误 '{filename}': {str(e)}")


@command("write_to_file", "写入文件", '"filename": "<filename>", "text": "<text>"')
def write_to_file(filename: str, text: str) -> str:
    """Write text to a file

    Args:
        filename (str): The name of the file to write to
        text (str): The text to write to the file

    Returns:
        str: A message indicating success or failure
    """
    if check_duplicate_operation("write", filename):
        return "Error: File has already been updated."
    try:
        filepath = path_in_workspace(filename)
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        log_operation("write", filename)
        return "文件写入成功."
    except Exception as e:
        return f"错误: {str(e)}"


@command(
    "append_to_file", "追加至文件", '"filename": "<filename>", "text": "<text>"'
)
def append_to_file(filename: str, text: str, shouldLog: bool = True) -> str:
    """Append text to a file

    Args:
        filename (str): The name of the file to append to
        text (str): The text to append to the file

    Returns:
        str: A message indicating success or failure
    """
    try:
        filepath = path_in_workspace(filename)
        with open(filepath, "a") as f:
            f.write(text)

        if shouldLog:
            log_operation("append", filename)

        return "文件追加成功."
    except Exception as e:
        return f"错误: {str(e)}"


@command("delete_file", "删除文件", '"filename": "<filename>"')
def delete_file(filename: str) -> str:
    """Delete a file

    Args:
        filename (str): The name of the file to delete

    Returns:
        str: A message indicating success or failure
    """
    if check_duplicate_operation("delete", filename):
        return "错误: 文件已经删除."
    try:
        filepath = path_in_workspace(filename)
        os.remove(filepath)
        log_operation("delete", filename)
        return "文件删除成功."
    except Exception as e:
        return f"错误: {str(e)}"


@command("search_files", "搜索文件", '"directory": "<directory>"')
def search_files(directory: str) -> list[str]:
    """Search for files in a directory

    Args:
        directory (str): The directory to search in

    Returns:
        list[str]: A list of files found in the directory
    """
    found_files = []

    if directory in {"", "/"}:
        search_directory = WORKSPACE_PATH
    else:
        search_directory = path_in_workspace(directory)

    for root, _, files in os.walk(search_directory):
        for file in files:
            if file.startswith("."):
                continue
            relative_path = os.path.relpath(os.path.join(root, file), WORKSPACE_PATH)
            found_files.append(relative_path)

    return found_files


@command(
    "download_file",
    "下载文件",
    '"url": "<url>", "filename": "<filename>"',
    CFG.allow_downloads,
    "错误: 你没有被授权下载文件到本地.",
)
def download_file(url, filename):
    """Downloads a file
    Args:
        url (str): URL of the file to download
        filename (str): Filename to save the file as
    """
    safe_filename = path_in_workspace(filename)
    try:
        message = f"{Fore.YELLOW}下载文件中 {Back.LIGHTBLUE_EX}{url}{Back.RESET}{Fore.RESET}"
        with Spinner(message) as spinner:
            session = requests.Session()
            retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            total_size = 0
            downloaded_size = 0

            with session.get(url, allow_redirects=True, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("Content-Length", 0))
                downloaded_size = 0

                with open(safe_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Update the progress message
                        progress = f"{readable_file_size(downloaded_size)} / {readable_file_size(total_size)}"
                        spinner.update_message(f"{message} {progress}")

            return f'成功下载文件并储存至: "{filename}"! (Size: {readable_file_size(total_size)})'
    except requests.HTTPError as e:
        return f"下载文件过程中遇到一个HTTP错误: {e}"
    except Exception as e:
        return "错误: " + str(e)
