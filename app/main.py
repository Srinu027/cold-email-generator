import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")
    url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
    submit_button = st.button("Submit")
    if submit_button:
        try:
            # Load data from the URL
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)

            # Load portfolio data
            portfolio.load_portfolio()

            # Extract jobs from the cleaned text
            jobs = llm.extract_jobs(data)
            if not jobs:
                st.warning("No jobs found on the provided URL.")
                return

            # Generate emails for each job
            for job in jobs:
                skills = job.get('skills', [])
                if not skills:
                    st.warning(f"No skills found for the role: {job.get('role', 'Unknown Role')}. Skipping...")
                    continue

                # Query portfolio links based on skills
                links = portfolio.query_links(skills)

                # Write a cold email
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
