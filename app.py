import streamlit as st
from tabula import read_pdf
from tabulate import tabulate
import pandas as pd
import fitz 
import cohere

# Initialize OpenAI API (replace with your own API key)
cohere_api_key = '9fO95BVy8czaT6cHASo7ykpHVYHu0dpasyBJvB7W'
co = cohere.Client(cohere_api_key)
@st.cache_data
# Function to extract tables from the PDF
def extract_tables_from_pdf(pdf_path, start_page,end_page):
    pages = f"{start_page}-{end_page}"
    tables = read_pdf(pdf_path, pages=pages, multiple_tables=True)
    return tables

@st.cache_data
# Function to extract text from the PDF
def extract_text_from_pdf(pdf_path,start,end):
    try:
        text = ""
        with fitz.open(pdf_path) as pdf:
            for page_num in range(pdf.page_count):
                if page_num>=start  and page_num<end:
                    page = pdf.load_page(page_num)  # Correct way to load each page
                    text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return ""

def call_llm(prompt):
    try:
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=100000,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        st.error(f"Error with LLM: {e}")
        return ""

# Summarization function
def generate_summary(text):
    prompt = f"Summarize the following text:\n{text}"
    return call_llm(prompt)

# Insight generation function
def generate_insights(text):
    prompt = f"Generate key insights from the following text:\n{text}"
    return call_llm(prompt)

# Comparison function between two tables from two different PDFs
def generate_comparison(table1, table2):
    prompt = f"Compare the following tables from two different PDFs:\n\nTable from PDF 1:\n{table1}\n\nTable from PDF 2:\n{table2}"
    return call_llm(prompt)

# Streamlit UI
st.title("Multi-PDF Extractor and LLM Analyzer")

# File uploaders for two PDFs
uploaded_file_1 = st.file_uploader("Upload the TCS Report PDF file", type="pdf", key="pdf1")
uploaded_file_2 = st.file_uploader("Upload the Infosys Report PDF file", type="pdf", key="pdf2")

# Processing the PDFs if both are uploaded
if uploaded_file_1 and uploaded_file_2:
    # Save the uploaded PDF files
    with open("uploaded_pdf_1.pdf", "wb") as f:
        f.write(uploaded_file_1.getbuffer())
    with open("uploaded_pdf_2.pdf", "wb") as f:
        f.write(uploaded_file_2.getbuffer())

    # Extract text and tables from both PDFs
    st.write("Extracting content from both PDFs...")
    
    text_1 = extract_text_from_pdf("uploaded_pdf_1.pdf",11,307)
    tables_1 = extract_tables_from_pdf ("uploaded_pdf_1.pdf",11,307)
    
    text_2 = extract_text_from_pdf("uploaded_pdf_2.pdf",33,340)
    tables_2 = extract_tables_from_pdf("uploaded_pdf_2.pdf",33,340)

    # Display extracted text from both PDFs
    # st.subheader("Extracted Text from PDF 1")
    # st.text_area("Text from the first PDF:", text_1, height=200)
    
    # st.subheader("Extracted Text from PDF 2")
    # st.text_area("Text from the second PDF:", text_2, height=200)

    # # Display extracted tables from both PDFs
    # st.subheader("Extracted Tables from PDF 1")
    # for idx, table in enumerate(tables_1):
    #     if isinstance(table, pd.DataFrame):
    #         st.write(f"Table {idx + 1}:")
    #         st.write(tabulate(table, headers='keys', tablefmt='grid'))
    #     else:
    #         st.write(f"Table {idx + 1} is not a valid DataFrame.")

    # st.subheader("Extracted Tables from PDF 2")
    # for idx, table in enumerate(tables_2):
    #     if isinstance(table, pd.DataFrame):
    #         st.write(f"Table {idx + 1}:")
    #         st.write(tabulate(table, headers='keys', tablefmt='grid'))
    #     else:
    #         st.write(f"Table {idx + 1} is not a valid DataFrame.")

    # Summarize the extracted text
    if st.button("Generate Summary for PDF 1"):
        st.write("Generating summary for PDF 1...")
        summary_1 = generate_summary(text_1)
        st.subheader("Summary for PDF 1")
        st.write(summary_1)
    
    if st.button("Generate Summary for PDF 2"):
        st.write("Generating summary for PDF 2...")
        summary_2 = generate_summary(text_2)
        st.subheader("Summary for PDF 2")
        st.write(summary_2)

    # Generate insights
    if st.button("Generate Insights for PDF 1"):
        st.write("Generating insights for PDF 1...")
        insights_1 = generate_insights(text_1)
        st.subheader("Insights for PDF 1")
        st.write(insights_1)
    
    if st.button("Generate Insights for PDF 2"):
        st.write("Generating insights for PDF 2...")
        insights_2 = generate_insights(text_2)
        st.subheader("Insights for PDF 2")
        st.write(insights_2)

    # Compare tables between the two PDFs
    if len(tables_1) > 0 and len(tables_2) > 0:
        table_1 = tables_1[0].to_string(index=False)
        table_2 = tables_2[0].to_string(index=False)

        if st.button("Compare Table 1 from both PDFs"):
            st.write("Generating comparison between Table 1 from both PDFs...")
            comparison = generate_comparison(table_1, table_2)
            st.subheader("Comparison between Table 1 from PDF 1 and PDF 2")
            st.write(comparison)
    else:
        st.write("Not enough tables in both PDFs for comparison.")

else:
    st.write("Please upload two PDF files.")
