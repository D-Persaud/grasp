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

def vectorize_2(acts_storage,pubs_storage,roc_storage,proj_path):

    acts_csv_path = acts_storage / 'csv' / 'updated_acts.csv'
    pubs_csv_path = pubs_storage / 'csv' / 'publications.csv'

    acts_md_path = acts_storage / 'md' / 'from_txt' 
    pubs_md_path = pubs_storage / 'md' / 'from_txt'
    roc_md_path = roc_storage / 'md' / 'from_pdf'

    acts_csv = pd.read_csv(acts_csv_path)
    pubs_csv = pd.read_csv(pubs_csv_path)

    documents = []

    ## Acts Loop

    # print(len(acts_csv.act_chapter))

    # x = listdir(acts_md_path)
    # print(len(x))
 
    # for e in range(len(x)):
    #     y = x[e].replace("-",":").strip(".md")
    #     if y not in acts_csv.act_chapter.values:
    #         print(y)

    for e in range(len(acts_csv.act_chapter)):
        act_name = acts_csv.act_name[e]
        act_number = acts_csv.act_chapter[e]
        act_description = acts_csv.act_description[e]

        md_file = act_number
        md_file = md_file.replace(":","-") + ".md"
        act_md = acts_md_path / md_file


        with open(act_md, "r", encoding="utf-8") as txt_extract:
            documents.append(
                Document(
                    page_content=txt_extract.read(),
                    metadata={"source": md_file, 
                            "act name": act_name,
                            "act number": act_number,
                            "act description": act_description,
                    }
                )
            )

    print("=====Finished Loading Acts=====")

    ## Publications Loop

    for e in range(len(pubs_csv.name)):
        md_file = pubs_csv.name[e]
        md_file = md_file.replace(".pdf",".md")
        pub_md = pubs_md_path / md_file

        with open(pub_md, "r", encoding="utf-8") as txt_extract:
            documents.append(
                Document(
                    page_content=txt_extract.read(),
                    metadata={"source": md_file, 
                            "publication title": pubs_csv.title[e],
                    }
                )
            )

    print("=====Finished Loading Publications=====")

    roc_files = listdir(roc_md_path)
    for e in range(len(roc_files)):
        md_file = roc_files[e]
        roc_md = roc_md_path / md_file
        with open(roc_md, "r", encoding="utf-8") as txt_extract:
            documents.append(
                Document(
                    page_content=txt_extract.read(),
                    metadata={"source": md_file, 
                    }
                )
            )

    vector_store = Chroma(
        collection_name="constitution_collection",
        embedding_function=embeddings,
        persist_directory="./chroma_langchain_db_const", 
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(documents)
    print("=====Finished Splitting!=====")

    BATCH_SIZE = 100      
    ids = []
    for i in range(0, len(all_splits), BATCH_SIZE):
        batch = all_splits[i:i + BATCH_SIZE]
        ids.extend(vector_store.add_documents(documents=batch))
        print(f"Stored {min(i + BATCH_SIZE, len(all_splits))}/{len(all_splits)}")
        time.sleep(0.1)       

    print("=====Finished Storing=====")


def main():
    home_dir = Path.home()
    proj_path = home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG'
    acts_storage = proj_path / 'Acts Storage'
    pubs_storage = proj_path / 'Publications Storage'
    roc_storage = proj_path / 'Rules of Court Storage'
    vectorize_2(acts_storage=acts_storage,pubs_storage=pubs_storage,roc_storage=roc_storage,proj_path=proj_path)


if __name__ == "__main__":
    main()