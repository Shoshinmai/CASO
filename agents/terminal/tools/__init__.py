from agents.terminal.tools.reading import read_file
from .discovery import list_directory, search_content, search_files
from .shell import run_terminal

TOOLS = [search_files, run_terminal, list_directory, search_content, read_file]
