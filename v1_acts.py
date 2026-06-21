from pypdf import PdfReader
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel, Field
from pathlib import WindowsPath, Path
import csv
from os import listdir,rename

llm="qwen3:4b"
model = init_chat_model(
    model=llm,
    model_provider="ollama",
    temperature=0,
    timeout=300,
    max_tokens=25000,
    reasoning=True
)

SYSTEM_PROMPT="""
You are an expert at extracting the Act Name, Chapter number and Act Description from a given text.

Note: sometimes the text will extend beyond the Act Description, usually don't take into account anything after it.

The act description is something directly within the text to be extracted, it's not a summary for *you* to create.
This is BEFORE any sections within the act. It is always denoted by "An Act to...." or "An Act for..."
An example would be:
An Act to continue in force the Statutes, Acts, and
Ordinances heretofore passed, enacted, or ordained by
the Governor or Lieutenant-Governor and Court of
Policy of the Colonies of Essequibo and Demerara, or
by the Governor or Lieutenant- Governor and Court of
Policy of the United Colony of Demerara and
Essequibo, and by the Governor or Lieutenant-
Governor and Court of Policy of Berbice, or by the
Governor or Lieutenant-Governor and Council of
Government of the Colony of Berbice, respectively.
Keep in mind this is just an example for your reference and not to be replicated directly
"""

class ActsInfo(BaseModel):
    act_name: str = Field(description="The Name of the Act specified in the text")
    chapter_number: str = Field(description="The Chapter number specified in the text")
    act_desc: str = Field(description="The description of the act given in the text")

structured_llm = model.with_structured_output(ActsInfo)


#For Windows
csv_path = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG', 'acts.csv')
folder_path = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG')
pdfs = [e for e in listdir(path=folder_path) if e.endswith(".pdf")]
##Loop
for pdf in range(len(pdfs)):
    pdf_path = WindowsPath('c:/', 'Users', 'denny','Desktop','Library','Projects','Constitution RAG',pdfs[pdf])
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

# ## Prompting the LLM
#     result = structured_llm.invoke([
#         SystemMessage(content=SYSTEM_PROMPT),
#         HumanMessage(content=f"Extract the Act Name, Chapter number, and Act Description from: {prompt}"),
#     ])

#     print("\n\n==========Extraction Done!==========\n", result)

## Writing to the csv
    with open(csv_path, 'a', newline='') as acts_csv:
        act_writer = csv.writer(acts_csv,quoting=csv.QUOTE_STRINGS)
        act_writer.writerow([act_name.upper(),act_number,act_desc])
## Renaming the file
    rename(pdf_path,f"{act_number.replace(':','-')}"+".pdf")

print("\n\n==========Finished Writing to csv!==========\n")



