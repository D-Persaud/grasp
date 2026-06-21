from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool
from pathlib import WindowsPath, Path
from os import listdir
import pandas as pd
import time
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

def main():
    # Defining Paths
    home_dir = Path.home()
    acts_storage_path = home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG' / 'Acts Storage'
    csv_path = acts_storage_path / 'csv' / 'updated_acts.csv'
    txt_folder_path = acts_storage_path / 'txts'

    # Extracting a list of all txt files in the directory
    txts = [e for e in listdir(txt_folder_path) if e.endswith(".txt")]
    txts = sorted(txts)

    # Defining csv variable to extract with pandas
    csv = pd.read_csv(csv_path)

    # Defining empty document list to append Document objects to 
    documents = []

    # For loop that loops over all text files in the directory
    for _ in range(len(txts)):
    
    ## Defining paths to each text file based off of the loop
        txt_path = (WindowsPath(txt_folder_path, txts[_]))

    ## Extracting the Act Numbers from the csv with the express condition that the respective txt file exists
        act_number = "".join([e for e in csv.act_chapter if e == f"{txts[_].replace("-",":").replace(".txt","")}"])

    ### Extracts csv Index based off of the aforementioned act number
        act_index = csv.act_chapter[csv.act_chapter == "".join(act_number)].index.start

    #### Uses csv index to find respective csv variables
        act_name = csv.act_name[act_index]
        act_description = csv.act_description[act_index]
        if act_number != f"{txts[_].replace("-",":").replace(".txt","")}":
            print(f"WARNING {_+1}/{len(txts)}, {act_number}, {txts[_]} MISMATCHED")
        with open(txt_path, "r", encoding="utf-8") as txt_extract:
            documents.append(
                Document(
                    page_content=txt_extract.read(),
                    metadata={"source": f"{txts[_]}", 
                            "act name": act_name,
                            "act number": act_number,
                            "act description": act_description,
                    }
                )
            )

    print("=====Finished Loading Docs=====")

    vector_store = Chroma(
        collection_name="constitution_acts_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db_txts",  # Where to save data locally, remove if not necessary
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(documents)
    print("=====Finished Splitting!=====")

    ids = vector_store.add_documents(documents=all_splits)
    BATCH_SIZE = 100          # if you still hit the error, drop to 50 or 25
    ids = []
    for i in range(0, len(all_splits), BATCH_SIZE):
        batch = all_splits[i:i + BATCH_SIZE]
        ids.extend(vector_store.add_documents(documents=batch))
        print(f"Stored {min(i + BATCH_SIZE, len(all_splits))}/{len(all_splits)}")
        time.sleep(0.1)        # lets TIME_WAIT sockets drain between batches

    print("=====Finished Storing=====")

if __name__ == "__main__":
    main()
