import shutil
import os
from langchain_community.document_loaders import PyPDFLoader
import tempfile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import uuid
from models import embeddings, llm

async def training(file,departmant):
    unique_id=uuid.uuid4()
    temp_dir=create_temp_directory()
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path=save_file_to_temp_directory(file, temp_dir)
    loader = PyPDFLoader(temp_file_path)
    documents = loader.load_and_split()
    for doc in documents:
         doc.metadata['department'] = departmant
         doc.metadata['filename'] = str(file.filename)
    
    print("Document info",len(documents))
    print("Document details",(documents))
    docs=split_docs(documents, file.filename)
    persist_local_directory=os.path.join(departmant+ "/" + str(file.filename))
    print("Chunking completed for document info",len(docs))

    def add_documents_to_chroma(docs, department, persist_local_directory):
    
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db_v1",  # Where to save data locally, remove if not necessary
        )
        
        for doc in docs:
            doc.metadata["department"] = department
            doc.metadata["filename"] = str(file.filename)
        batch_size = 50
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i:i + batch_size]  # Get the current batch
            batch_ids = [str(uuid.uuid4()) for _ in batch_docs]  # Generate unique IDs for the batch

            vector_store.add_documents(documents=batch_docs, ids=batch_ids)

    persist_local_directory = "chroma_db"
    add_documents_to_chroma(docs, departmant, persist_local_directory)

    print("chromadb created successfully.")
    

def split_docs(documents, filename, chunk_size=700, chunk_overlap=120):
     if documents is None:
          print("No documents to split")
          return None
     splitter= RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
     chunks=splitter.split_documents(documents)
     for chunk in documents:
          chunk.page_content="    Document Name = " +filename + "\n   " + chunk.page_content +"\n    Document Name =" +filename
          print(chunk.page_content)
    #  return chunks
     return documents
     
def create_temp_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        print("temp dir:",temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def save_file_to_temp_directory(file, temp_dir):
    
        temp_file_path=os.path.join(temp_dir, file.filename)
        with open(temp_file_path, 'wb') as f:
            shutil.copyfileobj(file.file,f)
    
        return temp_file_path