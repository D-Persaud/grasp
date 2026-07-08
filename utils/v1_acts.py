from pypdf import PdfReader
from pathlib import WindowsPath, Path
import csv
import argparse
from os import listdir,rename


def parse_pdf_actsinfo(csv_path,pdf_folder_path):

    pdfs = [e for e in listdir(path=pdf_folder_path) if e.endswith(".pdf")]

    ##Loop
    for pdf in range(len(pdfs)):
        pdf_path = pdf_folder_path / pdfs[pdf]
        reader = PdfReader(pdf_path)
        pdf_text_list = []
        if len(reader.pages) >= 10:
            for _ in range(10):
                pdf_text_list.append(reader.pages[_].extract_text())
        else:
            for _ in range(len(reader.pages)):
                pdf_text_list.append(reader.pages[_].extract_text())
        # prompt=" ".join(pdf_text_list)
    ## Getting act name and number
        front_page_text = "".join(pdf_text_list[0].splitlines()).strip()
        log_position = int(front_page_text.upper().find('GUYANA')) + 6
        chapter_position = int(front_page_text.upper().find('CHAPTER'))
        act_name = front_page_text[log_position:chapter_position].strip()
        act_number = front_page_text[chapter_position + 7:chapter_position + 13].strip()
    ## Getting act description
        full_text = " ".join(pdf_text_list)
        act_desc_start = int(full_text.lower().find('an act to'))
        act_desc_end = int(full_text.lower().find('[',act_desc_start))
        act_desc = full_text[act_desc_start:act_desc_end]
        act_desc = act_desc.splitlines()
        act_desc = "".join(act_desc).strip()

    ## Writing to the csv
        with open(csv_path, 'a', newline='') as acts_csv:
            act_writer = csv.writer(acts_csv,quoting=csv.QUOTE_STRINGS)
            act_writer.writerow([act_name.upper(),act_number,act_desc])
    ## Renaming the file
        rename(pdf_path,f"{act_number.replace(':','-')}"+".pdf")

    print("\n\n==========Finished Writing to csv!==========\n")

def get_sys_args():
    parser = argparse.ArgumentParser(
            prog='Acts PDF to csv field parser',
            description='Parses Act Name, Desc, and Chapter number from the Acts PDFs',
            epilog='Note: You can path to the home directory by inputing the tilde or \'~\' symbol. For Example: ~/path/to/your/pdffolder ~/path/to/your/csv')
    
    parser.add_argument('pdf_folder')
    parser.add_argument('csv_path')

    args = parser.parse_args()
    
    return Path(args.pdf_folder).expanduser(),Path(args.csv_path).expanduser()

def main():
    pdf_folder_path,csv_path = get_sys_args()

    parse_pdf_actsinfo(
        csv_path=csv_path,
        pdf_folder_path=pdf_folder_path
    )

if __name__ == "__main__":
    main()

