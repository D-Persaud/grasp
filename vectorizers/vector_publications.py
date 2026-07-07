from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
import pandas as pd
import time


def store_publications(csv_path,batch_folder_path,batch_format,file_encoding,):

    documents = []

    csv = pd.read_csv(csv_path)
    for index in range(len(csv.name)):
        batch_file = csv.name[index].replace(".pdf",batch_format)
        batch_path = batch_folder_path / batch_file
        with open(batch_path, "r", encoding=file_encoding) as batch_extract:
            documents.append(
                Document(
                    page_content=batch_extract.read(),
                    metadata={
                        "source": batch_file,
                        "publication title": csv.title[index]
                    }
                )
            )

    print("=====-Finished Storing Publications-=====")
    
    return documents

def vectorize_publications(documents,embedding_model,collection_name,persist_directory,chunk_size,chunk_overlap,batch_size,batch_starting_range):

    embeddings = OllamaEmbeddings(model=embedding_model)
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True
    )
    all_splits = text_splitter.split_documents(documents)
    print("=====Finished Splitting!=====")


    BATCH_SIZE = batch_size       
    ids = []
    for i in range(batch_starting_range, len(all_splits), BATCH_SIZE):
        batch = all_splits[i:i + BATCH_SIZE]
        ids.extend(vector_store.add_documents(documents=batch))
        print(f"Stored {min(i + BATCH_SIZE, len(all_splits))}/{len(all_splits)}")
        time.sleep(0.1)    

    print("=====Finished Storing=====")


def main():
    # Defining Paths
    home_dir = Path.home()
    pubs_storage_path = home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG' / 'Publications Storage'
    csv_path = pubs_storage_path / 'csv' / 'publications.csv'
    txt_folder_path = pubs_storage_path / 'txts'

    vectorize_publications(
        documents=store_publications(
            csv_path=csv_path,
            batch_folder_path=txt_folder_path,
            batch_format=".txt",
            file_encoding="utf-8"
        ),
        embedding_model="mxbai-embed-large",
        collection_name="gazette_collection",
        persist_directory="./chroma_langchain_db_txts",
        chunk_size=1000,
        chunk_overlap=200,
        batch_size=100,
        batch_starting_range=0
    )


if __name__ == "__main__":
    main()
