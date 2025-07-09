from google import genai
from google.genai import types
from google.api_core import retry

import json
from pydantic import BaseModel

import os
from dotenv import load_dotenv

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(genai.models.Models.generate_content)

# Pydantic model to structure the JSON response
class QuizContent(BaseModel):
    question_number: int
    question: str
    exemplar_answer: str

class QuizReview(BaseModel):
    question_number: int
    correct: bool
    reason: str

# Main class to interact with llm
class learning_assistant:

    def __init__(self, pdf_path, google_api_key, google_model = 'gemini-2.0-flash'):
        """
        """
        
        self.google_model = google_model
        self.client = genai.Client(api_key=google_api_key)
        self.uploaded_pdf = self.client.files.upload(file=pdf_path)

    def execute_prompt(self, prompt, config):
        """
        """

        response = self.client.models.generate_content(
            model = self.google_model,
            config = config,
            contents = prompt
        )

        return response.text

    def explain_section(self, section: str):
        """
        Uses a google llm to generate a summarised explanation of the selected section

        Args:
            section (str): name of the pdf section currently being studied.

        Returns:
            explanation (str): summarised explanation of the selected section
        """
        
        with open("prompts/explain_section.txt", "r") as prompt_template:
            prompt_template = prompt_template.read()
        
        prompt_template = prompt_template.format(selected_section = section)

        prompt = [prompt_template, self.uploaded_pdf]

        config = types.GenerateContentConfig(
            temperature=0.5,
        )

        explanation = self.execute_prompt(prompt, config)

        return explanation

    def create_quiz_content(self, section):
        """
        Uses a google llm to generate questions and exemplar answers based on the selected section

        Args:
            section (str): name of the pdf section currently being studied.

        Returns:
            quiz_content (list[dict]): A list of dictionaries, each representing a quiz question
        """

        with open("prompts/create_quiz_content.txt", "r") as prompt_template:
            prompt_template = prompt_template.read()
        
        prompt_template = prompt_template.format(selected_section = section)

        prompt = [prompt_template, self.uploaded_pdf]

        config = types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type= "application/json",
            response_schema=list[QuizContent],
        )

        quiz_content = self.execute_prompt(prompt, config)
        quiz_content = json.loads(quiz_content)

        return quiz_content


    def review_quiz_response(self, section, attempted_quiz):
        """
        Uses a google llm to review the user's answers to the generated quiz questions

        Args:
            section (str): name of the pdf section currently being studied.
            attempted_quiz (list[dict]): list of dictionaries, each representing an attempted quiz question

        Returns:
            quiz_review (list[dict]): list of dictionaries, each representing a reviewed quiz question
        """

        with open("prompts/review_user_answers.txt", "r") as prompt_template:
            prompt_template = prompt_template.read()
        
        attempted_quiz_prompt = ""

        for question in attempted_quiz:
            attempted_quiz_prompt += f"""
            Question {question['question_number']}: {question['question']}
            Model answer: {question['exemplar_answer']}
            User answer: {question['user_answer']}
            """

        prompt_template = prompt_template.format(selected_section = section, attempted_quiz = attempted_quiz_prompt)

        prompt = [prompt_template, self.uploaded_pdf]

        config = types.GenerateContentConfig(
            temperature=0.5,
            response_mime_type= "application/json",
            response_schema=list[QuizReview],
        )

        quiz_review = self.execute_prompt(prompt, config)
        quiz_review = json.loads(quiz_review)

        return quiz_review


# Best testing framework of all time.
"""
test_assistant = learning_assistant("uploaded_pdfs/Prompt Engineering_v7/doc.pdf", gemini_api_key)

test_explanation = test_assistant.explain_section("Sampling controls")
print(test_explanation)

test_quiz_content = test_assistant.create_quiz_content("Sampling controls")
print(test_quiz_content)


sample_attempt = [
    {'exemplar_answer': 'Temperature, top-K, and top-P are the most common '
                        'configuration settings.',
    'question': 'What are the three most common configuration settings that '
                'determine how predicted token probabilities are processed to '
                'choose a single output token?',
    'question_number': 1,
    'user_answer': 'Tuna, Salmon and Bass'},
    {'exemplar_answer': 'Temperature controls the degree of randomness in token '
                        'selection.',
    'question': 'What does temperature control in token selection?',
    'question_number': 2,
    'user_answer': 'The level of randomness in token selection'},
    {'exemplar_answer': 'Top-K sampling selects the top K most likely tokens.',
    'question': 'What sampling setting selects the top K most likely tokens from '
                "the model's predicted distribution?",
    'question_number': 3,
    'user_answer': 'Top P sampling'}
    ]

test_quiz_review = test_assistant.review_quiz_response("Sampling controls", sample_attempt)
print(test_quiz_review)
"""