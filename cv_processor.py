import os
import json
from typing import Dict
from pdfminer.high_level import extract_text
import google.generativeai as genai
from google.generativeai import GenerativeModel
import groq


class CVProcessor:
    def __init__(self):
        # Google AI API setup
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=google_api_key)
        self.model = GenerativeModel('gemini-2.0-flash-exp')

        # Groq API setup
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.groq_client = groq.Groq(api_key=groq_api_key)

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
        You are a CV matching assistant. Analyze the following CV against the job requirements.
        Provide a detailed analysis and then calculate a final match percentage.

        Evaluate and explain each component:
        1. Skills Match (40% of total):
        - List matching skills
        - Identify missing critical skills
        - Calculate skills match percentage

        2. Experience Relevance (30% of total):
        - Analyze relevance of past roles
        - Consider years of experience
        - Calculate experience match percentage

        3. Project Alignment (20% of total):
        - Evaluate project relevance to role
        - Consider project complexity
        - Calculate project match percentage

        4. Education Fit (10% of total):
        - Compare education requirements
        - Consider relevant certifications
        - Calculate education match percentage

        CV Data:
        {json.dumps(cv_parsed_data, indent=2)}

        Job Requirements:
        {job_requirements}

        After analysis, conclude with:
        FINAL_SCORE: [number between 0-100]
        """

        try:
            # Use Groq API with deepseek-r1-distill-llama-70b model
            completion = self.groq_client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="deepseek-r1-distill-llama-70b",
                temperature=0.1,  # Lower temperature for more consistent numerical output
            )

            # Get the full response
            response_text = completion.choices[0].message.content.strip()

            # Print the detailed analysis

            print(response_text)


            # Extract the final score
            import re

            # First try to find FINAL_SCORE pattern
            score_pattern = re.compile(r'FINAL_SCORE:\s*(\d+(?:\.\d+)?)')
            score_match = score_pattern.search(response_text)

            if score_match:
                score = float(score_match.group(1))
            else:
                # If no FINAL_SCORE found, look for the last number in the text
                # This assumes the final score is typically mentioned last
                numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', response_text)
                if numbers:
                    # Take the last number found as it's likely the final score
                    score = float(numbers[-1])
                else:
                    print("Could not extract valid score from response")
                    return 0.0

            # Print the extracted score for verification
            print(f"\nExtracted Score: {score}")

            return min(100, max(0, score))  # Ensure score is between 0 and 100

        except Exception as e:
            print(f"Error calculating match score: {e}")
            return 0.0