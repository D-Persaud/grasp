import requests
import argparse
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

def pub_csv_writer(csv_path):
    PAGE_NUMBER=0
    try:
        while True:
            PAGE_NUMBER+=1
            csv_dict = gazette_url_grabber(PAGE_NUMBER=PAGE_NUMBER,PAGE_SIZE=12)
            with open(csv_path, "a", newline="",encoding="utf-8") as pub_csv:
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
        pdf_path = pub_storage / f"{pub_csv.name[e]}"
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
    for e in range(len(pub_csv.name)):
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
            
    
    ## The files were accidentally named .pdf.pdf so this script renamed them
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

def get_sys_args():
    parser = argparse.ArgumentParser(
        prog='Gazette Webscraper and Parser',
        description='Webscrapes the API for the official egazette website for Guyana and parses the information into a csv',
        epilog='Note: You can path to the home directory by inputing the tilde or \'~\' symbol. For Example: ~/path/to/your/pdffolder ~/path/to/your/csv')
    

    parser.add_argument('pubs_folder')
    parser.add_argument('csv_path')
    parser.add_argument('-f', '--full', action='store_true')
    parser.add_argument('-d', '--download', action='store_true')
    parser.add_argument('-o', '--ocr', action='store_true')
    parser.add_argument('-t', '--txt', action='store_true')
    parser.add_argument('-c', '--csvwriter', action='store_true')

    args = parser.parse_args()
    
    return {"publications folder": Path(args.pubs_folder).expanduser(),
            "csv path": Path(args.csv_path).expanduser(),
            "is_full": args.full,
            "is_dl": args.download,
            "is_ocr": args.ocr,
            "is_txt": args.txt,
            "is_csvwriter": args.csvwriter
    }



def main():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
        }
    )

    args = get_sys_args()
    csv_path = args["csv path"]
    pub_storage = args["publications folder"]

    if args["is_full"] is True or args ["is_csvwriter"] is True:
        pub_csv_writer(csv_path=csv_path)
    if args["is_full"] is True or args["is_dl"] is True:
        dl_pub_pdfs(csv_path=csv_path,pub_storage=pub_storage)
    if args["is_full"] is True or args["is_ocr"] is True:
        pub_pdf_ocr(csv_path=csv_path,pub_storage=pub_storage)
    if args["is_full"] is True or args["is_txt"] is True:
        pub_pypdf(csv_path=csv_path,pub_storage=pub_storage)

if __name__ == "__main__":
    main()
