import os
import json
from typing import Dict
from pdfminer.high_level import extract_text
import google.generativeai as genai
from google.generativeai import GenerativeModel


class CVProcessor:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = GenerativeModel('gemini-pro')

    def extract_text_from_pdf(self, pdf_file) -> str:
        try:
            text = extract_text(pdf_file)
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def parse_cv_with_genai(self, cv_text: str) -> Dict:
        prompt = """
        Parse the following CV text and extract these details in JSON format:
        - Full Name
        - Email
        - Phone
        - Skills (as a list)
        - Projects (as a list)
        - Work Experience (as a list of dictionaries with company, position, duration)
        - Education (as a list of dictionaries with institution, degree, year)

        CV Text:
        {cv_text}
        """

        response = self.model.generate_content(prompt.format(cv_text=cv_text))
        try:
            # Extract JSON from the response
            json_str = response.text.strip('```json\n').strip('```')
            return json.loads(json_str)
        except Exception as e:
            print(f"Error parsing GenAI response: {e}")
            return {}

    def match_cv_to_job(self, cv_parsed_data: Dict, job_requirements: str) -> float:
        prompt = f"""
        Compare the following CV data with job requirements and give a match percentage (0-100).
        Consider skills, experience, and education alignment.

        CV Data:
        {json.dumps(cv_parsed_data, indent=2)}

        Job Requirements:
        {job_requirements}

        Return only a number between 0 and 100.
        """

        response = self.model.generate_content(prompt)
        try:
            score = float(response.text.strip())
            return min(100, max(0, score))  # Ensure score is between 0 and 100
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return 0.0