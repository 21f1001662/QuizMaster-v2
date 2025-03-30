import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

def generate_mcq_question(existing_questions: str = "", context: str = ""):
    """
    Generate an MCQ question using Gemini AI
    Args:
        existing_questions: String containing existing question texts to avoid duplicates
    Returns:
        Dictionary containing the MCQ question data
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a prompt for generating an MCQ question
        prompt = f"""
        Generate a multiple choice question in JSON format with the following structure:
        {{
            "type": "mcq",
            "question_text": "The question text",
            "correct_marks": 4,
            "incorrect_marks": -1,
            "options": [
                {{
                    "text": "Option 1",
                    "is_correct": false
                }},
                {{
                    "text": "Option 2",
                    "is_correct": true
                }},
                {{
                    "text": "Option 3",
                    "is_correct": false
                }},
                {{
                    "text": "Option 4",
                    "is_correct": false
                }}
            ]
        }}
        
        Make it a general knowledge question. Ensure the question is unique and not similar to these existing questions:
        {existing_questions}
        The question should be related to the following context:
        {context}
        
        Return only the JSON object, no additional text.
        """
        
        # Generate the response
        response = model.generate_content(prompt)
        # Get the response text from the first part
        response_text = response.parts[0].text
        json_str = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        
        # Parse the response as JSON
        question_data = json.loads(json_str)
        return question_data
        
    except Exception as e:
        print(f"Error generating MCQ question: {str(e)}")
        return None

def generate_numeric_question(existing_questions: str = "", context: str = ""):
    """
    Generate a numeric question using Gemini AI
    Args:
        existing_questions: String containing existing question texts to avoid duplicates
    Returns:
        Dictionary containing the numeric question data
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a prompt for generating a numeric question
        prompt = f"""
        Generate a numeric question in JSON format with the following structure:
        {{
            "type": "numeric",
            "question_text": "The question text",
            "answer_lower_bound": 9.8,
            "answer_upper_bound": 9.81,
            "correct_marks": 4.0,
            "incorrect_marks": -1
        }}
        
        Make it a question that requires a numeric answer with a small range of acceptable values.
        The question should be related to the following context:
        {context}
        Ensure the question is unique and not similar to these existing questions:
        {existing_questions}
        
        Return only the JSON object, no additional text. 
        """
        
        # Generate the response
        response = model.generate_content(prompt)
        # Get the response text from the first part
        response_text = response.parts[0].text
        json_str = re.sub(r'```json\s*|\s*```', '', response_text).strip()
        
        # Parse the response as JSON
        question_data = json.loads(json_str)
        return question_data
        
    except Exception as e:
        print(f"Error generating numeric question: {str(e)}")
        return None 