from PyPDF2 import PdfReader
from agents import function_tool # Changed from function_tool
import json

USER_DATA_FILE = "user_data.json"

@function_tool # Changed from function_tool
def read_user_profile():
    """Reads the user profile from the JSON file."""
    try:
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

@function_tool # Changed from function_tool
def update_user_profile(key: str, value: str):
    """Updates a key-value pair in the user profile."""
    data = read_user_profile()
    data[key] = value
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@function_tool # Changed from function_tool
def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts all text from a given PDF file.
    
    Args:
        file_path: The absolute or relative path to the PDF file.
        
    Returns:
        A single string containing all the extracted text.
    """
    print(f"DEBUG: Extracting text from PDF: {file_path}")
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        print(f"DEBUG: Successfully extracted {len(text)} characters from {file_path}")
        return text
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return "Error: The specified file was not found."
    except Exception as e:
        print(f"ERROR: An error occurred while reading the PDF {file_path}: {e}")
        return f"An error occurred while reading the PDF: {e}"