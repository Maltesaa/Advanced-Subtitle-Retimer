import subprocess
import sys
import re


def run_command(command):
    try:
        return subprocess.check_output(command, encoding="utf-8")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def file_name_sorter(file_name: str) -> str:
    """Zero pads all numbers in a file name to 5 digits for sorting."""
    file_name_without_whitespace = re.sub(r'\s+', '', file_name)
    return re.sub(r'\d+', lambda match: match.group(0).zfill(5), file_name_without_whitespace.lower())
