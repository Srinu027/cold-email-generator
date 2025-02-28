import os
import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR)

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )

    def extract_jobs(self, cleaned_text):
        if not cleaned_text or not isinstance(cleaned_text, str):
            logging.error("Invalid input for extract_jobs: cleaned_text must be a non-empty string.")
            raise ValueError("Invalid input: cleaned_text must be a non-empty string.")

        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            Extract job postings from the scraped text and return them in JSON format with the following keys:
            - `role`: Job title.
            - `experience`: Required experience level.
            - `skills`: List of required skills.
            - `description`: Detailed job description.
            Only return valid JSON without any preamble.
            """
        )
        chain_extract = prompt_extract | self.llm
        try:
            res = chain_extract.invoke(input={"page_data": cleaned_text})
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except Exception as e:
            logging.error(f"Failed to parse jobs: {e}")
            raise ValueError(f"Failed to parse jobs: {e}")

        # Ensure each job has a 'skills' key, even if it's empty
        if isinstance(res, list):
            for job in res:
                job.setdefault('skills', [])
        else:
            res.setdefault('skills', [])
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links, greeting="Dear Hiring Manager", closing="Best regards, Mohan"):
        if not job or not isinstance(job, dict):
            logging.error("Invalid input for write_mail: job must be a non-empty dictionary.")
            raise ValueError("Invalid input: job must be a non-empty dictionary.")
        if not links or not isinstance(links, list):
            logging.error("Invalid input for write_mail: links must be a non-empty list.")
            raise ValueError("Invalid input: links must be a non-empty list.")

        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            ### INSTRUCTION:
            Write a cold email as Mohan, a business development executive at AtliQ. Highlight AtliQ's capabilities
            in fulfilling the client's needs based on the job description. Include relevant links from the portfolio.
            Use the following greeting and closing lines:
            Greeting: {greeting}
            Closing: {closing}
            Do not provide a preamble.
            """
        )
        chain_email = prompt_email | self.llm
        try:
            res = chain_email.invoke({
                "job_description": str(job),
                "link_list": ", ".join(links),
                "greeting": greeting,
                "closing": closing
            })
            return res.content
        except Exception as e:
            logging.error(f"Failed to generate email: {e}")
            raise ValueError(f"Failed to generate email: {e}")