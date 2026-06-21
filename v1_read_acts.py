import pandas as pd 
from pathlib import WindowsPath

csv_path = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG', 'acts.csv')
csv = pd.read_csv(csv_path)
csv.act_chapter = csv.act_chapter.map(lambda _: _.replace(":",".").replace("A",""))
csv.act_chapter = csv.act_chapter.astype("float64")
csv = csv.sort_values(by=["act_chapter"], ascending=True)
csv.act_chapter = csv.act_chapter.astype("str")
csv.act_chapter = csv.act_chapter.map(lambda _: _.replace(".",":"))
csv.act_chapter = csv.act_chapter.map(lambda _: _.replace(":1",":10") if _.endswith(":1") else _)
csv_path = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG', 'updated_acts.csv')
csv.to_csv(path_or_buf=csv_path, index=False,quoting=1)