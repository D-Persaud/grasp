import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
import csv
import pandas as pd
from pypdf import PdfReader
from os import listdir, rename
import ocrmypdf
from ocrmypdf import OcrOptions
from ocrmypdf.exceptions import DpiError
from pypdfium2._helpers.misc import PdfiumError

def gazette_url_grabber(PAGE_NUMBER:int,PAGE_SIZE:int):
    BASE = "https://egazette.officialgazette.gov.gy"

    pub_api = requests.get(f"{BASE}/api/publications?page={PAGE_NUMBER}&pageSize={PAGE_SIZE}")
    api_json = pub_api.json()
    url_dict = {
        "name": [],
        "title": [],
        "downloadUrl": []
    }
    for _ in api_json["publications"]:
        url_dict["name"].append(_["name"])
        url_dict["title"].append(_["title"])
        url_dict["downloadUrl"].append(_["downloadUrl"])
    if url_dict["name"] == [] and url_dict["title"] == [] and url_dict["downloadUrl"] == []:
        raise EOFError
    return url_dict

def pub_csv_writer():
    PAGE_NUMBER=41
    try:
        while True:
            PAGE_NUMBER+=1
            csv_dict = gazette_url_grabber(PAGE_NUMBER=PAGE_NUMBER,PAGE_SIZE=12)
            with open("publications.csv", "a", newline="",encoding="utf-8") as pub_csv:
                fieldnames = ["name","title","downloadUrl"]
                writer = csv.DictWriter(pub_csv, fieldnames=fieldnames)
                for e in range(len(csv_dict["downloadUrl"])):
                    writer.writerow({
                        "name": csv_dict["name"][e],
                        "title": csv_dict["title"][e],
                        "downloadUrl": csv_dict["downloadUrl"][e]
                    })
                print(f"=====Page {PAGE_NUMBER} Done!=====")
    except EOFError:
        print("\n=====There are no more publications to scrub!=====\n")

def dl_pub_pdfs(csv_path,pub_storage):
    BASE = "https://egazette.officialgazette.gov.gy"
    pub_csv = pd.read_csv(csv_path)
    for e in range(len(pub_csv.downloadUrl)):
        response_pdf = requests.get(f"{BASE}/{pub_csv.downloadUrl[e]}")
        response_pdf.raise_for_status()
        # for chunk in response_pdf.iter_content(chunk_size=8192):
        #     if chunk:
        #         print(chunk)
        pdf_path = pub_storage / f"{pub_csv.name[e]}.pdf"
        with open(pdf_path,"wb") as f:
            f.write(response_pdf.content)
        print(f"====={pub_csv.title[e]} Done! ({e}/{len(pub_csv.downloadUrl)})=====")


def pub_pypdf(csv_path,pub_storage):
    pub_csv = pd.read_csv(csv_path)
    for e in range(len(pub_csv.name)):
        pdf_path = pub_storage / 'pdfs' / pub_csv.name[e]
        reader = PdfReader(pdf_path)
        txt_path = pub_storage / 'txts' / f"{pub_csv.name[e].replace(".pdf",".txt")}"
        for page in range(len(reader.pages)):
            with open(txt_path, "a", encoding="utf-8") as f:
                text = reader.pages[page].extract_text(extraction_mode="plain")
                f.write(text)
        print(f"====={pub_csv.title[e]} Finished Converting to .txt! ({e+1}/{len(pub_csv.name)})")
                
        break    

def pub_pdf_ocr(csv_path,pub_storage):
    pub_csv = pd.read_csv(csv_path)
    pdf_folder = pub_storage / 'pdfs'
    txt_path = pub_storage / 'txts'
    # pdf_path = pdf_folder / pub_csv.name[0]
    for e in range(595,len(pub_csv.name)):
        try:
            pdf_path = pdf_folder / pub_csv.name[e]
            options = OcrOptions(
                input_file=pdf_path,
                output_file=pdf_path,
                deskew=False,
                languages=['eng'],
                progress_bar=False,
                redo_ocr=True
            )
            ocrmypdf.ocr(options)
            print(f"====={pub_csv.title[e]} Finished! {e+1}/{len(pub_csv.name)}")
        except DpiError,PdfiumError:
            error_txt = txt_path / 'errors.txt'
            with open(error_txt, "a", encoding="utf-8") as f:
                ERROR_MESSAGE = f"{pub_csv.title[e]} ERROR!"
                f.write(ERROR_MESSAGE)
                print(ERROR_MESSAGE)
                pass
            ...
    ... 
    ## The files were accidentally name .pdf.pdf so this script renamed them
    # pdfs = [e for e in listdir(pdf_folder) if e.endswith(".pdf.pdf")]
    # print(len(pdfs))
    # for e in range(len(pdfs)):
    #     try:
    #         pdf_path = pdf_folder / pdfs[e]
    #         print(pdf_path)
    #         new_path = pdf_folder / pdfs[e].replace(".pdf.pdf",".pdf")
    #         rename(pdf_path,new_path)
    #         print(f"====={pub_csv.title[e]} Finished Renaming!=====")
    #     except FileExistsError:
    #         pass

    ## This script checked for missing files
    # for e in range(len(pub_csv.name)):
    #     pdf_path = pub_storage / 'pdfs' / pub_csv.name[e]
    #     try:
    #         with open(pdf_path) as f:
    #             ...
    #     except FileNotFoundError:
    #         print(e)
    #         break

def main():
    # session = requests.Session()
    # session.headers.update({
    #     "User-Agent": "Mozilla/5.0",
    #     "Accept": "application/json"
    #     }
    # )
    home_dir = Path.home()
    project_path = home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG'
    pub_storage = project_path / 'Publications Storage'
    csv_path = pub_storage / 'csv' / 'publications.csv'
    pub_pdf_ocr(csv_path=csv_path,pub_storage=pub_storage)
    # pub_pypdf(csv_path=csv_path,pub_storage=pub_storage)
    # dl_pub_pdfs(csv_path=csv_path,pub_storage=pub_storage)

if __name__ == "__main__":
    main()