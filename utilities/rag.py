import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rich.console import Console
from rich.text import Text


class RAG:
    def __init__(self):
        self.language = None
        self.index_dir = None
        self.model_name = None
        self.embedder = None
        self.documents = None
        self.index = None
        self.index_path = None

    def get_model_name(self):
        return 'HooshvareLab/bert-fa-base-uncased' if self.language and self.language.lower() == 'persian' else 'all-MiniLM-L6-v2'

    def split_docs(self, documents, chunk_size=1000, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.split_documents(documents)

    async def build_index_from_folder(self, folder_path, language='english', index_dir="faiss_indices"):
        self.language = language
        self.index_dir = index_dir
        self.model_name = self.get_model_name()
        self.embedder = SentenceTransformer(self.model_name)

        # Load documents from the folder
        loader = DirectoryLoader(folder_path, glob="**/*.txt", show_progress=True)
        documents = loader.load()
        self.documents = self.split_docs(documents)

        # Encode the documents
        document_texts = [doc.page_content for doc in self.documents]
        document_embeddings = self.embedder.encode(document_texts, convert_to_numpy=True)

        # Build the FAISS index
        index = faiss.IndexFlatL2(document_embeddings.shape[1])
        index.add(document_embeddings)
        self.index = index

        # Save the FAISS index
        os.makedirs(self.index_dir, exist_ok=True)
        self.index_path = os.path.join(self.index_dir, "faiss_index")
        faiss.write_index(self.index, self.index_path)
        return self.index_path

    def load_index(self, index_path, language):
        self.language = language
        self.model_name = self.get_model_name()
        self.embedder = SentenceTransformer(self.model_name)

        self.index_path = index_path
        self.index = faiss.read_index(self.index_path)
        return self.index

    def search(self, query, top_k=5, index_path=None, language=None):
        if index_path and language:
            self.load_index(index_path, language)

        if not self.index:
            raise ValueError("Index is not loaded. Please provide a valid index path and language.")

        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        _, indices = self.index.search(query_embedding, top_k)
        # print(_)
        matching_docs = [self.documents[i] for i in indices[0]]
        return matching_docs

    def decode_search_results(self, results):
        decoded_results = []
        for result in results:
            decoded_results.append({
                "content": result.page_content,
            })
        return decoded_results

    def print_search_results(self, results):
        if not results:
            print("No results found.")
            return

        print(f"{'Rank':<5} {'Document Content'}")
        print("="*80)
        # print(results)
        for rank, result in enumerate(results):
            persian_print(f"{rank+1:<5} {result.metadata.get('source')} : \n {result.page_content}")

    def generate_answer(self, question, context):
        # This method should contain the logic to generate an answer given the question and context.
        # For example, if you use a pre-trained language model to generate the answer:
        prompt = f"""متن پیدا شده: {context}
        تنها با توجه به متن بالا یه سوال پاسخ بده
        سوال: {question} """
        # Implement your own answer generation logic here
        answer = prompt  # Replace with the actual call to your chatbot model
        return answer

    def rag(self, question, top_k=5):
        retrieved_docs = self.search(question, top_k)
        combined_context = " ".join([doc.page_content for doc in retrieved_docs])
        answer = self.generate_answer(question, combined_context)
        return answer




def persian_print(persian_text):
    console = Console()
    # Create a Text object with styling
    styled_text = Text(persian_text, style="bold green")

    # Print the styled Persian text
    console.print(styled_text)

# Usage example
async def main():
    folder_path = r'/content'
    language = 'persian'  # Change to 'persian' if needed

    rag = RAG()

    # Build and save the index from a folder of documents
    index_path = await rag.build_index_from_folder(folder_path, language)
    print(f"Index saved at: {index_path}")

    # Load the index and search
    query = "Code Assist"
    search_results = rag.search(query, top_k=5, index_path=index_path, language=language)
    rag.print_search_results(search_results)

    # Example usage for RAG
    Question = rag.rag(query)
    persian_print(f"{Question}\nAnswer:")



import nest_asyncio
nest_asyncio.apply()
import asyncio
asyncio.run(main())