import io
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from langchain.schema import Document

# 1) Helpers to fetch & extract text from HTML or PDF
def fetch_html_text(url: str) -> str:
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # remove scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose()
    return "\n".join(soup.stripped_strings)

def fetch_pdf_text(url: str) -> str:
    resp = requests.get(url)
    resp.raise_for_status()
    reader = PdfReader(io.BytesIO(resp.content))
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


articles = [
    {
      "id": "spotted_wing_drosophila_ipm",
      "title": "SWD IPM in Raspberries and Blackberries",
      "url": "(Not Included the URL here) You can Input the URL here"
    },
    {
      "id": "brown_marmorated_stink_bug_fact_sheet",
      "title": "The Unwelcome House Guest: Brown Marmorated Stink Bug",
      "url": "(Not Included the URL here) You can Input the URL here"
    },
    {
      "id": "fall_armyworm_field_crop_update",
      "title": "Field Crop Update: Fall Armyworm Reports in Western NY",
      "url": "(Not Included the URL here) You can Input the URL here"
    }
]

# 3) Turn each into a RAG Document with full text
docs = []
for art in articles:
    url = art["url"]
    if url.lower().endswith(".pdf"):
        content = fetch_pdf_text(url)
    else:
        content = fetch_html_text(url)
    docs.append(
        Document(
            page_content=content,
            metadata={
              "id": art["id"],
              "title": art["title"],
              "source_url": url
            }
        )
    )

# 4) Index them
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
index = FAISS.from_documents(docs, embed)
index.save_local("faiss_pest_index_with_articles")
print("Indexed articles with full text!")
