import os
from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from embedding import GeminiAIEmbeddings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import yaml
import re
import numpy as np

CONFIG_FILE = 'config.yaml'

with open(CONFIG_FILE, 'r') as config_file:
    config = yaml.load(config_file,Loader=yaml.FullLoader)
_ = load_dotenv(find_dotenv())

import logging

# Set higher logging levels for noisy libraries
logging.getLogger('chromadb').setLevel(logging.WARNING)
logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7890'
    
# 获取 folder_path 下所有文件路径，储存在 file_paths 里
def generate_path(folder_path: str = 'knowledge_base') -> list:
    file_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
    return file_paths

def generate_loaders(file_paths: list) -> list:
    loaders = []
    for file_path in file_paths:
        file_type = file_path.split('.')[-1]
        if file_type == 'pdf':
            loaders.append(PyMuPDFLoader(file_path))
        elif file_type == 'md':
            loaders.append(UnstructuredMarkdownLoader(file_path))
    return loaders

def exec_load(loaders: list) -> list:
    texts = []
    for loader in loaders:
        original = loader.load()
        for doc in original:
            # Remove literal "\n" occurrences.
            doc.page_content = re.sub(r"\\n", " ", doc.page_content)
        texts.extend(original)
    return texts

def slice_docs(texts):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    return text_splitter.split_documents(texts)

class VectorDB:
    embedding = GeminiAIEmbeddings()
    persist_directory = 'vector_database/chroma'
    slice = 20

    def __init__(self, sliced_docs: list):
        assert sliced_docs is not None, "sliced_docs must not be None"
        self.vectordb = Chroma.from_documents(
            documents=sliced_docs[:self.slice],
            embedding=self.embedding,
            persist_directory=self.persist_directory  # Persist database on disk.
        )

    def persist(self):
        self.vectordb.persist()
        print(f"向量库中存储的数量：{self.vectordb._collection.count()}")

    def sim_search(self, query, k=3):
        sim_docs = self.vectordb.similarity_search(query, k=k)
        for i, sim_doc in enumerate(sim_docs, start=1):
            print(f"检索到的第{i}个内容: \n{sim_doc.page_content[:1000]}", end="\n--------------\n")
        return sim_docs

    def mmr_search(self, query, k=3):
        mmr_docs = self.vectordb.max_marginal_relevance_search(query, k=k)
        for i, mmr_doc in enumerate(mmr_docs, start=1):
            print(f"MMR 检索到的第{i}个内容: \n{mmr_doc.page_content[:1000]}", end="\n--------------\n")
        return mmr_docs

    def hybrid_search(self, query, k=3, dedup_threshold=0.95):
        """
        Hybrid search method that:
        1. Retrieves extra candidates using dense similarity search.
        2. Re-ranks using TF-IDF similarity.
        3. Deduplicates results to ensure the returned contexts are distinct.
        """
        candidate_docs = self.vectordb.max_marginal_relevance_search(query, k=k * 5)
        candidate_texts = [doc.page_content for doc in candidate_docs]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(candidate_texts)
        query_vec = vectorizer.transform([query])
        
        # Calculate cosine similarity scores between each candidate and the query.
        cosine_scores = (tfidf_matrix * query_vec.T).toarray().flatten()

        # Get indices sorted by TF-IDF cosine score in descending order.
        ranked_indices = np.argsort(cosine_scores)[::-1]

        # Deduplicate: iterate over ranked candidates and select documents that are not too similar.
        selected_indices = []
        for idx in ranked_indices:
            if not selected_indices:
                selected_indices.append(idx)
            else:
                current_vector = tfidf_matrix[idx]
                selected_vectors = tfidf_matrix[selected_indices]
                similarities = cosine_similarity(current_vector, selected_vectors)
                if similarities.max() < dedup_threshold:
                    selected_indices.append(idx)
            if len(selected_indices) == k:
                break

        hybrid_docs = [candidate_docs[i] for i in selected_indices]
        for i, doc in enumerate(hybrid_docs, start=1):
            print(f"Hybrid 检索到的第{i}个内容: \n{doc.page_content[:1000]}", end="\n--------------\n")
        return hybrid_docs

def The_RAG_Process(question):
    file_paths = generate_path()
    loaders = generate_loaders(file_paths)
    texts = exec_load(loaders)
    sliced_docs = slice_docs(texts)
    vdb = VectorDB(sliced_docs)
    vdb.persist()

    # doc_list = vdb.mmr_search(question)

    doc_list = vdb.hybrid_search(question, k=3, dedup_threshold=0.90)

    prompt = "Here is the user's question:\n" + question + "\nAnd here are some context information retreived:\n"
    for i, doc in enumerate(doc_list, start=1):
        prompt += f"Context information No.{i}:\n"
        prompt += doc.page_content[:1000] + "\n"
    
    print(prompt)
    return prompt
