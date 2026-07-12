from pathlib import WindowsPath, Path
from os import listdir
from docling.document_converter import DocumentConverter
import argparse


def batch_pdf_md(pdf_folder,md_folder):
    converter = DocumentConverter()

    pdfs = listdir(path=pdf_folder)    
    for pdf in range(len(pdfs)):
        source = pdf_folder / pdfs[pdf]

        doc = converter.convert(source).document
        markdown_output = doc.export_to_markdown()

        md_file = pdfs[pdf].replace(".pdf",".md")
        md_path = md_folder / md_file
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_output)
        print(f"====={pdf+1}/{len(pdfs)} Complete!=====")

def get_sys_args():
    parser = argparse.ArgumentParser(
                prog='pdf to md converter',
                description='pdf to md batch script using docling',
                epilog='Note: You can path to the home directory by inputing the tilde or \'~\' symbol. For Example: ~/path/to/your/pdffolder ~/path/to/your/mdfolder')
    
    parser.add_argument('pdf_folder')
    parser.add_argument('md_folder')

    args = parser.parse_args()
    
    return Path(args.pdf_folder).expanduser(),Path(args.md_folder).expanduser()

def main():
    pdf_folder,md_folder = get_sys_args()

    batch_pdf_md(
        pdf_folder=pdf_folder,
        md_folder=md_folder
    )


if __name__ == "__main__":
    main()
