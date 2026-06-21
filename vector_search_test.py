from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(model="mxbai-embed-large")
vector_store = Chroma(
    collection_name="constitution_acts_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db_txts",  # Where to save data locally, remove if not necessary
)

input_text = input("What do you want to know from the constitution? ")
results = vector_store.similarity_search_with_score(input_text)
doc, score = results[0]
print(f"Score: {score}\n")
print(doc)