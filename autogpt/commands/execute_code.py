"""Execute code in a Docker container"""
import os
import subprocess

import docker
from docker.errors import ImageNotFound

from autogpt.commands.command import command
from autogpt.config import Config
from autogpt.workspace import WORKSPACE_PATH, path_in_workspace

CFG = Config()


@command("execute_python_file", "Execute Python File", '"filename": "<filename>"')
def execute_python_file(filename: str) -> str:
    """Execute a Python file in a Docker container and return the output

    Args:
        filename (str): The name of the file to execute

    Returns:
        str: The output of the file
    """
    file = filename
    print(f"执行文件 '{file}' 在workspace中 '{WORKSPACE_PATH}'")

    if not file.endswith(".py"):
        return "错误: 无效的文件格式. 只允许 .py 文件."

    file_path = path_in_workspace(file)

    if not os.path.isfile(file_path):
        return f"错误: 文件 '{file}' 不存在."

    if we_are_running_in_a_docker_container():
        result = subprocess.run(
            f"python {file_path}", capture_output=True, encoding="utf8", shell=True
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return f"错误: {result.stderr}"

    try:
        client = docker.from_env()

        # You can replace this with the desired Python image/version
        # You can find available Python images on Docker Hub:
        # https://hub.docker.com/_/python
        image_name = "python:3-alpine"
        try:
            client.images.get(image_name)
            print(f"图片 '{image_name}' 在本地找到了")
        except ImageNotFound:
            print(f"图片 '{image_name}' 在本地没有找到, 从Docker Hub中提取")
            # Use the low-level API to stream the pull response
            low_level_client = docker.APIClient()
            for line in low_level_client.pull(image_name, stream=True, decode=True):
                # Print the status and progress, if available
                status = line.get("status")
                progress = line.get("progress")
                if status and progress:
                    print(f"{status}: {progress}")
                elif status:
                    print(status)

        container = client.containers.run(
            image_name,
            f"python {file}",
            volumes={
                os.path.abspath(WORKSPACE_PATH): {
                    "bind": "/workspace",
                    "mode": "ro",
                }
            },
            working_dir="/workspace",
            stderr=True,
            stdout=True,
            detach=True,
        )

        container.wait()
        logs = container.logs().decode("utf-8")
        container.remove()

        # print(f"Execution complete. Output: {output}")
        # print(f"Logs: {logs}")

        return logs

    except docker.errors.DockerException as e:
        print(
            "在container无法执行脚本. 如果没有安装docker，请安装 https://docs.docker.com/get-docker/"
        )
        return f"错误: {str(e)}"

    except Exception as e:
        return f"错误: {str(e)}"


@command(
    "execute_shell",
    "执行Shell命令, 只允许非互动式命令",
    '"command_line": "<command_line>"',
    CFG.execute_local_commands,
    "你无法执行本地shell命令. 如需执行"
    " shell 命令, EXECUTE_LOCAL_COMMANDS 需要设置为 'True' "
    "在你的config中. 请不要试图绕过限制。",
)
def execute_shell(command_line: str) -> str:
    """Execute a shell command and return the output

    Args:
        command_line (str): The command line to execute

    Returns:
        str: The output of the command
    """

    if not CFG.execute_local_commands:
        return (
            "你无法执行本地shell命令. 如需执行"
            " shell 命令, EXECUTE_LOCAL_COMMANDS 需要设置为 'True' "
            "在你的config中. 请不要试图绕过限制。"
        )
    current_dir = os.getcwd()
    # Change dir into workspace if necessary
    if str(WORKSPACE_PATH) not in current_dir:
        os.chdir(WORKSPACE_PATH)

    print(f"执行命令 '{command_line}' 中，在working directory '{os.getcwd()}'")

    result = subprocess.run(command_line, capture_output=True, shell=True)
    output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    # Change back to whatever the prior working dir was

    os.chdir(current_dir)


@command(
    "execute_shell_popen",
    "执行Shell命令, 只允许非互动式命令",
    '"command_line": "<command_line>"',
    CFG.execute_local_commands,
    "你无法执行本地shell命令. 如需执行"
    " shell 命令, EXECUTE_LOCAL_COMMANDS 需要设置为 'True' "
    "在你的config中. 请不要试图绕过限制。",
)
def execute_shell_popen(command_line) -> str:
    """Execute a shell command with Popen and returns an english description
    of the event and the process id

    Args:
        command_line (str): The command line to execute

    Returns:
        str: Description of the fact that the process started and its id
    """
    current_dir = os.getcwd()
    # Change dir into workspace if necessary
    if str(WORKSPACE_PATH) not in current_dir:
        os.chdir(WORKSPACE_PATH)

    print(f"执行命令 '{command_line}' 中，在working directory '{os.getcwd()}'")

    do_not_show_output = subprocess.DEVNULL
    process = subprocess.Popen(
        command_line, shell=True, stdout=do_not_show_output, stderr=do_not_show_output
    )

    # Change back to whatever the prior working dir was

    os.chdir(current_dir)

    return f"子进程已启动，PID 为:'{str(process.pid)}'"


def we_are_running_in_a_docker_container() -> bool:
    """Check if we are running in a Docker container

    Returns:
        bool: True if we are running in a Docker container, False otherwise
    """
    return os.path.exists("/.dockerenv")
