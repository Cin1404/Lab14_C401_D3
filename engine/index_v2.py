import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

load_dotenv(override=True)

# =============================================================================
# CẤU HÌNH
# =============================================================================

# Đường dẫn đến docs nội bộ của Lab14
DOCS_DIR = Path(__file__).parent.parent / "data" / "docs"
CHROMA_DB_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 400       # tokens (ước lượng bằng số ký tự / 4)
CHUNK_OVERLAP = 80     # tokens overlap

# =============================================================================
# LOGIC XỬ LÝ VĂN BẢN (REUSED FROM LAB08)
# =============================================================================

def preprocess_document(raw_text: str, filename: str) -> Dict[str, Any]:
    lines = raw_text.strip().split("\n")
    metadata = {
        "source": filename,
        "department": "unknown",
        "effective_date": "unknown",
        "access": "internal",
    }
    content_lines = []
    header_done = False

    for line in lines:
        if not header_done:
            if line.startswith("Source:"): metadata["source"] = line.replace("Source:", "").strip()
            elif line.startswith("Department:"): metadata["department"] = line.replace("Department:", "").strip()
            elif line.startswith("Effective Date:"): metadata["effective_date"] = line.replace("Effective Date:", "").strip()
            elif line.startswith("Access:"): metadata["access"] = line.replace("Access:", "").strip()
            elif line.startswith("==="):
                header_done = True
                content_lines.append(line)
            else:
                header_done = True
                content_lines.append(line)
        else:
            content_lines.append(line)

    cleaned_text = re.sub(r"\n{3,}", "\n\n", "\n".join(content_lines))
    return {"text": cleaned_text, "metadata": metadata}

def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    text = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks = []
    sections = re.split(r"(===.*?===)", text)

    current_section = "General"
    current_section_text = ""

    for part in sections:
        if re.match(r"===.*?===", part):
            if current_section_text.strip():
                chunks.extend(_split_by_size(current_section_text.strip(), base_metadata, current_section))
            current_section = part.strip("= ").strip()
            current_section_text = ""
        else:
            current_section_text += part

    if current_section_text.strip():
        chunks.extend(_split_by_size(current_section_text.strip(), base_metadata, current_section))
    return chunks

def _split_by_size(text: str, base_metadata: Dict, section: str) -> List[Dict[str, Any]]:
    chunk_chars = CHUNK_SIZE * 4
    overlap_chars = CHUNK_OVERLAP * 4
    meta = {**base_metadata, "section": section}
    
    if len(text) <= chunk_chars:
        return [{"text": text, "metadata": meta.copy()}]

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_chars, len(text))
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"text": chunk_text, "metadata": meta.copy()})
        if end >= len(text): break
        start = end - overlap_chars
    return chunks

# =============================================================================
# INDEXING
# =============================================================================

class LabIndexer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        self.collection = self.chroma_client.get_or_create_collection(
            name="lab14_docs",
            metadata={"hnsw:space": "cosine"}
        )

    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            input=text, 
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def build_index(self):
        print(f"🚀 Đang xây dựng Index từ: {DOCS_DIR}")
        doc_files = sorted(DOCS_DIR.glob("*.txt"))
        
        all_ids = []
        all_embeddings = []
        all_documents = []
        all_metadatas = []
        all_chunks_data = [] # Dung de tra ve cho generator

        for filepath in doc_files:
            print(f"  - Xử lý: {filepath.name}")
            raw_text = filepath.read_text(encoding="utf-8")
            doc = preprocess_document(raw_text, filepath.name)
            chunks = chunk_document(doc)
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filepath.stem}_{i}"
                emb = self.get_embedding(chunk["text"])
                
                all_ids.append(chunk_id)
                all_embeddings.append(emb)
                all_documents.append(chunk["text"])
                all_metadatas.append(chunk["metadata"])
                
                all_chunks_data.append({
                    "id": chunk_id,
                    "text": chunk["text"],
                    "metadata": chunk["metadata"]
                })

        self.collection.upsert(
            ids=all_ids,
            embeddings=all_embeddings,
            documents=all_documents,
            metadatas=all_metadatas
        )
        print(f"✅ Đã lưu {len(all_ids)} chunks vào ChromaDB.")
        return all_chunks_data

    def get_all_chunks(self) -> List[Dict]:
        """Lấy toàn bộ dữ liệu chunks đã index."""
        results = self.collection.get(include=["documents", "metadatas"])
        chunks = []
        for i in range(len(results["ids"])):
            chunks.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
        return chunks

    def search(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """Tìm kiếm các chunk liên quan nhất trong ChromaDB."""
        query_embedding = self.get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results

if __name__ == "__main__":
    indexer = LabIndexer()
    indexer.build_index()
