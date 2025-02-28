import pandas as pd
import chromadb
import uuid
import logging

# Configure logging
logging.basicConfig(filename='app.log', level=logging.ERROR)


class Portfolio:
    def __init__(self, file_path="app/resource/my_portfolio.csv"):
        self.file_path = file_path
        try:
            self.data = pd.read_csv(file_path)
            # Validate required columns
            if "Techstack" not in self.data.columns or "Links" not in self.data.columns:
                raise ValueError("CSV file must contain 'Techstack' and 'Links' columns.")

            # Clean Techstack column: Remove leading/trailing whitespace and normalize formatting
            self.data["Techstack"] = self.data["Techstack"].apply(
                lambda x: ", ".join([tech.strip() for tech in x.split(",")])
            )
        except FileNotFoundError:
            logging.error(f"Portfolio file not found at: {file_path}")
            raise FileNotFoundError(f"Portfolio file not found at: {file_path}")
        except Exception as e:
            logging.error(f"Error loading portfolio data: {e}")
            raise ValueError(f"Error loading portfolio data: {e}")

        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            try:
                # Batch insert for better performance
                documents = []
                metadatas = []
                ids = []
                for _, row in self.data.iterrows():
                    documents.append(row["Techstack"])
                    metadatas.append({"links": row["Links"]})
                    ids.append(str(uuid.uuid4()))
                self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            except Exception as e:
                logging.error(f"Error loading portfolio into ChromaDB: {e}")
                raise ValueError(f"Error loading portfolio into ChromaDB: {e}")

    def query_links(self, skills, n_results=2):
        # Ensure skills is not empty and contains valid data
        if not skills or not isinstance(skills, list) or len(skills) == 0:
            logging.warning("No valid skills provided for querying ChromaDB.")
            return []

        try:
            results = self.collection.query(query_texts=skills, n_results=n_results)
            return results.get('metadatas', [])
        except Exception as e:
            logging.error(f"Error querying ChromaDB: {e}")
            return []