from pathlib import WindowsPath, Path
from os import listdir, rename
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
home_dir = Path.home()
project_path = home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG'
folder_path = project_path / 'Acts Storage'
pdfs = listdir(path=folder_path)    
for pdf in range(len(pdfs)):
    source = folder_path / pdfs[pdf]
    doc = converter.convert(source).document
    markdown_output = doc.export_to_markdown()
    with open(f"{pdfs[pdf].replace(".pdf",".md")}", "w", encoding="utf-8") as f:
        f.write(markdown_output)
    print(markdown_output)
    
