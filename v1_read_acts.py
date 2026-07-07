import pandas as pd 
from pathlib import Path
import argparse

#Path defaults to what i used to build the project initially
def acts_csv_formatting(
        in_csv_path = Path.home() / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG' / 'Acts Storage' / 'csv' / 'acts.csv',
        out_csv_path = Path.home() / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG' / 'Acts Storage' / 'csv' / 'updated_acts.csv'
        ):
    
    csv = pd.read_csv(in_csv_path)

    # This essentially sorts out the act chapters in ascending order while accounting for possible floating point formatting errors
    csv.act_chapter = csv.act_chapter.map(lambda act_chapter: act_chapter.replace(":",".").replace("A",""))
    csv.act_chapter = csv.act_chapter.astype("float64")
    csv = csv.sort_values(by=["act_chapter"], ascending=True)
    csv.act_chapter = csv.act_chapter.astype("str")
    csv.act_chapter = csv.act_chapter.map(lambda act_chapter: act_chapter.replace(".",":"))
    csv.act_chapter = csv.act_chapter.map(lambda act_chapter: act_chapter.replace(":1",":10") if act_chapter.endswith(":1") else act_chapter)

    csv.to_csv(path_or_buf=out_csv_path, index=False,quoting=1)

def get_sys_args():
    parser = argparse.ArgumentParser(
                    prog='Acts CSV Formatter',
                    description='Formats the fetched csv of the acts of Guyana: Reorders acts based on their Chapter Numbers',
                    epilog='Note: You can path to the home directory by inputing the tilde or \'~\' symbol. For Example: ~/path/to/your/csvfile ~/path/to/your/newcsvfile')
    
    parser.add_argument('input_file')
    parser.add_argument('output_file')

    args = parser.parse_args()

    if not args.input_file.endswith(".csv"):
        args.input_file = args.input_file + ".csv"
    
    if not args.output_file.endswith(".csv"):
        args.output_file = args.output_file + ".csv"

    input_file = Path(args.input_file).expanduser()
    output_file = Path(args.output_file).expanduser()

    return input_file,output_file

def main():

    in_csv_path,out_csv_path = get_sys_args()

    acts_csv_formatting(
        in_csv_path=in_csv_path,
        out_csv_path=out_csv_path,
        )


if __name__ == "__main__":
    main()