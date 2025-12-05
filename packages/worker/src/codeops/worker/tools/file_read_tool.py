from crewai_tools import BaseTool


class FileReadTool(BaseTool):
    name: str = "File Read Tool"
    description: str = "Reads the content of a file."

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
