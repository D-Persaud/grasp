from pathlib import WindowsPath
from os import listdir, rename
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
folder_path = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG','Acts Storage') 
pdfs = listdir(path=folder_path)    
for pdf in range(len(pdfs)):
    source = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG','Acts Storage',pdfs[pdf])
    doc = converter.convert(source).document
    markdown_output = doc.export_to_markdown()
    with open(f"{pdfs[pdf].replace(".pdf",".md")}", "w", encoding="utf-8") as f:
        f.write(markdown_output)
    print(markdown_output)
    
