import pandas as pd
import chromadb
import uuid


class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        try:
            self.data = pd.read_csv(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Portfolio file not found at: {file_path}")
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=row["Techstack"],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        # Ensure skills is not empty and contains valid data
        if not skills or not isinstance(skills, list) or len(skills) == 0:
            return []  # Return an empty list if no valid skills are provided

        # Query ChromaDB with the skills as query_texts
        try:
            results = self.collection.query(query_texts=skills, n_results=2)
            return results.get('metadatas', [])
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return []
