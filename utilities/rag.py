from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import os
import asyncio

class RAG:
    def __init__(self):
        self.language = None
        self.index_dir = None
        self.model_name = None
        self.embedder = None
        self.documents = None
        self.document_embeddings = None
        self.index = None
        self.index_path = None

    def get_model_name(self):
        if self.language and self.language.lower() == 'persian':
            return 'HooshvareLab/bert-fa-base-uncased'
        else:
            return 'all-MiniLM-L6-v2'

    def split_docs(self, documents, chunk_size=1000, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)
        return docs

    async def build_index_from_folder(self, folder_path, language='english', index_dir="faiss_indices"):
        self.language = language
        self.index_dir = index_dir
        self.model_name = self.get_model_name()
        self.embedder = HuggingFaceEmbeddings(model_name=self.model_name)
        
        # Load documents from the folder
        loader = DirectoryLoader(folder_path, glob="**/*.txt", show_progress=True)
        documents = loader.load()
        self.documents = self.split_docs(documents)
        
        # Create embeddings
        self.document_embeddings = self.embedder.embed_documents(self.documents)
        
        # Build and save the FAISS index
        self.index = faiss.IndexFlatL2(self.document_embeddings.shape[1])
        self.index.add(self.document_embeddings)
        db_sentence_transformer = await FAISS.afrom_documents(self.documents, self.embedder)
        os.makedirs(self.index_dir, exist_ok=True)
        self.index_path = os.path.join(self.index_dir, "faiss_index")
        db_sentence_transformer.save_local(self.index_path)
        return self.index_path

    def load_index(self, index_path, language):
        self.language = language
        self.model_name = self.get_model_name()
        self.embedder = HuggingFaceEmbeddings(model_name=self.model_name)
        
        self.index_path = index_path
        new_db = FAISS.load_local(self.index_path, self.embedder, allow_dangerous_deserialization=True)
        self.index = new_db.index
        self.documents = new_db.documents
        return new_db

    def search(self, query, top_k=5, index_path=None, language=None):
        if index_path and language:
            self.load_index(index_path, language)
        
        if not self.index:
            raise ValueError("Index is not loaded. Please provide a valid index path and language.")
        
        query_embedding = self.embedder.embed_query(query)
        distances, indices = self.index.search(query_embedding, top_k)
        print("distances:", distances)
        print("_" * 50)
        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append((idx, self.documents[idx]))
        return results

    def print_search_results(self, results):
        if not results:
            print("No results found.")
            return
        
        print(f"{'Rank':<5} {'Distance':<10} {'Document Content'}")
        print("="*60)
        
        for rank, (idx, doc) in enumerate(results):
            distance = idx
            print(f"{rank+1:<5} {distance:<10} {doc[:500]}...")

# Usage example
async def main():
    folder_path = r'C:\\Users\\admin\\Desktop\\Rag_for_chat_bot\\Test_folder'
    language = 'persian'  # Change to 'persian' if needed
    
    rag = RAG()
    
    # Build and save the index from a folder of documents
    index_path = await rag.build_index_from_folder(folder_path, language)
    print(f"Index saved at: {index_path}")
    
    # Load the index and search
    query = "می تونی چالش های ماشین بردار پشتیان رو بگی ؟"
    results = rag.search(query, top_k=5, index_path=index_path, language=language)
    
    # Print search results
    rag.print_search_results(results)

# Run the example
asyncio.run(main())
