import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text
import validators
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR)


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    with st.sidebar:
        st.header("Input Options")
        url_input = st.text_input("Enter a URL:", value="https://jobs.nike.com/job/R-33460")
        greeting = st.text_input("Greeting", "Dear Hiring Manager")
        closing = st.text_input("Closing", "Best regards, Your Name")
        submit_button = st.button("Submit")

    if submit_button:
        if not validators.url(url_input):
            st.error("Please enter a valid URL.")
            return

        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            if not jobs:
                st.warning("No jobs found on the provided URL.")
                return

            emails = []
            progress_bar = st.progress(0)
            for i, job in enumerate(jobs):
                progress_bar.progress((i + 1) / len(jobs))
                skills = job.get('skills', [])
                if not skills:
                    st.warning(f"No skills found for the role: {job.get('role', 'Unknown Role')}. Skipping...")
                    continue
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links, greeting=greeting, closing=closing)
                emails.append(email)

                with st.expander(f"Email for Role: {job.get('role', 'Unknown Role')}"):
                    st.markdown(email)

            if emails:
                st.download_button(
                    label="Download Emails",
                    data="\n\n".join(emails),
                    file_name="cold_emails.txt",
                    mime="text/plain"
                )

        except Exception as e:
            logging.error(f"Error: {e}")
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)