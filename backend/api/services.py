import os
import sys
from PIL import Image
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
from django.http import HttpResponse

load_dotenv(find_dotenv())

try: 
    API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    sys.stderr.write("Error: GEMINI_API_KEY not found in environment variables. Please set it.")
    # Using placeholder will allow initalization, but calls will fail until user provides a real key.
    genai.configure(api_key="placeholder_key")

def engineering_prompt_for_gemini(question: str, example_data, example_solution: str):
    """
    Creates a prompt to feed into an AI based on a question, data, and solution.
    
    Args:
        question: What you want the AI to do with the information provided.
        example_data: The data.
        example_solution: The solution you want the AI to conclude from the data provided.
    
    Returns:
        Prompt containing the question, example data, and example solution to feed
        to the AI.
    """
    return

def generate_content_from_gemini(
        prompt: str, 
        context_filepath: str = "",
        system_instruction: str = "",
) -> str:
    """
    Calls the Gemini API to generate content based on a user prompt,
    and optional system instructions, and file context.

    The model used is 'gemini-2.5-pro'.
    TODO: Test out the other models to pick the best one for our use.

    Args:
        prompt: The user query to send to the model.
        context_filepath: Optional filepath to a file to include as context. Currently only supports image and PDF files as context.
        TODO: made this function very general, not sure what file types we want to add as context
        system_instruction: Optional instruction to guide the model's behavior.

    Returns:
        The generated text content, or an error message.
    """

    model_name = 'gemini-2.5-pro'
    context_file = ''

    try:
        if context_filepath.endswith('.pdf'):
            with open(context_filepath, 'rb') as pdf_file:
                context_file = HttpResponse(pdf_file.read(), content_type='application/pdf')
                pdf_file.close()
        elif context_filepath:
            try:
                context_file = Image.open(context_filepath)
            except Exception as e:
                print(f"--- Error opening image file: {e} ---")

        print(f"--- Calling Gemini API with model: {model_name} ---")

        reponse = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        ).generate_content(
            contents=[prompt, context_file]
        )

        return reponse.text

    except Exception as e:
        print(f"--- API Call Failed ---")
        return f"An error occurred during generation: {e}"