import chromadb
from pathlib import Path
import argparse


def chroma_test(db_path = Path.home() / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG' / 'chroma_langchain_db_txts'):
    client = chromadb.PersistentClient(
        path=db_path
    )
    return client.heartbeat()

def get_sys_args():
    parser = argparse.ArgumentParser(
        prog='Chroma db persistent storage tester',
        description='Tests whether a chroma vector database is functioning correctly by returning a heartbeat function result',
        epilog='Note: You can path to the home directory by inputing the tilde or \'~\' symbol. For Example: ~/path/to/your/vectordb')
    
    parser.add_argument('db_path')

    args = parser.parse_args()
    
    return Path(args.db_path).expanduser()

def main():
    db_path = get_sys_args()
    heartbeat = chroma_test(db_path=db_path)
    print(heartbeat)

if __name__ == "__main__":
    main()