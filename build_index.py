import json
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# 1. Load pest datasheets
with open("pests_region.json", "r") as f:
    records = json.load(f)

docs = []
for rec in records:
    # each rec has id, title, text, metadata
    docs.append(Document(page_content=rec["text"], metadata=rec["metadata"]))

# 2. Create embeddings
#    Uses a SBERT model under the hood
embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. Build FAISS index
index = FAISS.from_documents(docs, embed)

# 4. Persist index to disk
index.save_local("faiss_pest_region_index")
print("✅ FAISS index built and saved to ./faiss_pest_index")
