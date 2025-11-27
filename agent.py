from agent import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
import os
import asyncio
from dotenv import load_dotenv

# Import the tools from tools.py
from tools import extract_text_from_pdf, read_user_profile, update_user_profile

# Load environment
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# External Gemini Client
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta", # Corrected base_url
    timeout=60.0, # Added timeout
)

# Model Configuration
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", # Corrected model name
    openai_client=external_client,
)

# Runner configuration
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True  # As per instructions
)

# --- Main function to run the agent ---
async def main(file_path: str, quiz_type: str, num_questions: int):
    """
    Runs the StudyNotesAgent to process the PDF and returns the result.
    """
    print(f"Agent main function called with file_path: {file_path}, quiz_type: {quiz_type}, num_questions: {num_questions}")

    # --- Dynamic Instructions based on Quiz Type and Number of Questions ---
    base_instructions = (
        "You are an expert AI assistant for students. Your goal is to help users study more effectively. "
        "1. First, use the `extract_text_from_pdf` tool to read the content of the PDF file specified by the user. "
        "2. After extracting the text, create a concise, easy-to-understand summary of the key points. "
        f"3. Following the summary, generate a quiz with exactly {num_questions} questions based on the content. "
    )

    if quiz_type == "True/False":
        quiz_instructions = (
            "4. The quiz must be a 'True/False' quiz. **Crucially, format your final output *exactly* as follows:**\n"
            "---SUMMARY---\n\n<Your summary here>\n\n"
            "---QUIZ---\n\n"
            "```json\n"
            "[\n"
            "  {\n"
            '    "question": "Is the sky blue?",\n'
            '    "options": ["True", "False"],\n'
            '    "answer": "True"\n'
            "  }\n"
            "]\n"
            "```"
        )
    else: # Default to Multiple Choice
        quiz_instructions = (
            "4. The quiz must be a 'Multiple Choice' quiz with 4 options per question. **Crucially, format your final output *exactly* as follows:**\n"
            "---SUMMARY---\n\n<Your summary here>\n\n"
            "---QUIZ---\n\n"
            "```json\n"
            "[\n"
            "  {\n"
            '    "question": "What is the capital of France?",\n'
            '    "options": ["London", "Berlin", "Paris", "Madrid"],\n'
            '    "answer": "Paris"\n'
            "  }\n"
            "]\n"
            "```"
        )

    full_instructions = base_instructions + quiz_instructions
    
    # --- Define Agent with Dynamic Instructions ---
    study_agent = Agent(
        name="StudyNotesAgent",
        instructions=full_instructions,
        model=model,
        tools=[extract_text_from_pdf, read_user_profile, update_user_profile],
    )
    
    # The prompt given to the agent, including the path to the file
    prompt = f"Please process the document located at the following path: {file_path}"
    print(f"Agent prompt: {prompt}")

    print("Calling Runner.run...")
    # Run the agent
    result = await Runner.run(study_agent, prompt, run_config=config)
    print("Runner.run completed.")

    # Return the final output to be displayed in the UI
    if result and result.final_output:
        print("Agent returned a final output.")
        return result.final_output
    
    print("Agent did not return a final output or result was None.")
    return None

if __name__ == "__main__":
    # This part is for local testing of the agent, e.g., from the command line.
    # You would need to provide a sample file path and quiz type.
    # Example: asyncio.run(main("path/to/your/test.pdf", "Multiple Choice", 5))
    # The primary execution is now through app.py
    print("Agent module run directly. This should typically be called from app.py.")
    pass