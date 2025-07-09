# initial page will ask for a pdf upload

# it will parse this and then display chapters


import os
from dotenv import load_dotenv
import json

import pdf_utils
from llm_utils import learning_assistant

import streamlit as st
from st_ant_tree import st_ant_tree
from pprint import pprint

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

st.title('AI Learning Assistant')

# Define tree data
tree_data = [
    {
        "value": "parent_1",
        "title": "Parent 1",
        "children": [
            {"value": "child_1", "title": "Child 1"},
            {"value": "child_2", "title": "Child 2"},
        ],
    },
    {"value": "parent_2", "title": "Parent 2"},
]

with open("uploaded_pdfs/Agents_v8.pdf/toc.json", "r") as file:
    tree = json.load(file)

pprint(tree)

# Use the component
selected_values = st_ant_tree(
    treeData=tree_data,
    treeCheckable=True,
    allowClear=True
)


with st.empty():

    uploaded_pdf = st.file_uploader("Upload a PDF to study", type = "pdf")

    if uploaded_pdf is not None:

        doc = pdf_utils.doc(uploaded_pdf)
        doc.save() # so we can access later

        toc = pdf_utils.toc(doc.path)
        toc.save() # so we can access later


        parsed_toc = toc.parsed_toc

        #la = learning_assistant(doc.path, gemini_api_key)

        st.subheader(f"Lets study {doc.name}!")
        st.divider()

with st.empty():
    if uploaded_pdf is not None:
        section = st.selectbox(options = ["first", "second", "third"], 
                                label = "Section to study",
                                index = None)
        if section is not None:

            st.write(f"Generating lesson for section: **{section}**")

            #section_explanation = la.explain_section(section)

            #st.write(section_explanation)

st.divider()

print("end of script\n")