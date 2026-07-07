from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

def vector_search(search_query,embedding_model,collection_name,persist_directory):
    embeddings = OllamaEmbeddings(model=embedding_model)
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,  # Where to save data locally, remove if not necessary
    )

    results = vector_store.similarity_search_with_score(search_query)
    return results[0]


def main():
    EMBEDDING_MODEL = "mxbai-embed-large"
    COLLECTION_NAME = "constitution_acts_collection"
    PERSIST_DIRECTORY = "./chroma_langchain_db_txts"

    search_query = input("What do you want to know from the constitution? ")
    doc, score = vector_search(
        search_query=search_query,
        embedding_model=EMBEDDING_MODEL,
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIRECTORY
    )

    print(f"Score: {score}\n")
    print(doc)
    
if __name__ == "__main__":
    main()