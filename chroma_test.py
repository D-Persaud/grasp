import chromadb
from pathlib import Path
home_dir = Path.home()
client = chromadb.PersistentClient(
    path= home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG' / 'chroma_langchain_db_txts'
)
print(client.heartbeat())