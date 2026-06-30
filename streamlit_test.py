import streamlit as st
import pandas as pd
from pathlib import Path

# home_dir = Path.home()
# project_path = home_dir / 'Desktop' / 'Library' / 'Projects' / 'Constitution RAG'
# acts_storage = project_path / 'Acts Storage'
# pub_storage = project_path / 'Publications Storage'
# csv_path = pub_storage / 'csv' / 'publications.csv'

# csv = pd.read_csv(csv_path)
# print(type(csv))
# st.write("Here's our first attempt at using data to create a table:")
# st.write(csv)

# st.text_input("Your name", key="name")
# print(st.session_state.name)
# print("steve" in st.session_state.name)

st.title("Image Drag & Drop Uploader")

# The st.file_uploader natively supports drag and drop
uploaded_file = st.file_uploader("Drag and drop your image here", type=["png", "jpg", "jpeg"], key="IMAGE")
print(st.session_state.IMAGE)