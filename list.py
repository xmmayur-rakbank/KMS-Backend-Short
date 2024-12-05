from langchain_chroma import Chroma
from models import embeddings

async def listing():
    try:
        chroma_db_instance = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db_v1",  # Where to save data locally, remove if not necessary
        )
        
        print(chroma_db_instance.get())
        
        all_docs = chroma_db_instance.get()
        x=all_docs['metadatas']
        y=all_docs['ids']

        indexlist=[]
        # set = {""}
        # Departmentset = {""}
        Finallist = []
        Finallist = []
        unique_pairs = set()
        File_set = set()
        for index, obj in enumerate(all_docs['metadatas']):
            print(f"Index: {index}, Object: {obj}")
            file=obj["filename"]
            department=obj["department"]
            Finallist.append([file,department])
            pair = (file, department)
            File_set.add(file)
            if pair not in unique_pairs:
                unique_pairs.add(pair) 
                Finallist.append([file, department])
        print(File_set)
        return File_set
    except Exception as e:
        print(e)


async def listChunks(filename):
    try:
        chroma_db_instance = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db_v1",  # Where to save data locally, remove if not necessary
        )
        
        print(chroma_db_instance.get())
        
        all_docs = chroma_db_instance.get()
        x=all_docs['metadatas']
        y=all_docs['ids']

        indexlist=[]
        Finallist = []
        Finallist = []
        unique_pairs = set()
        File_set = set()
        for index, obj in enumerate(all_docs['metadatas']):
            print(f"Index: {index}, Object: {obj}")
            file=obj["filename"]
            department=obj["department"]
            if(file==filename):
                Finallist.append((index))
        list1=[]
        for index, obj in enumerate(all_docs['documents']):
            if(index in Finallist):
                list1.append(obj)
        print(list1)
        return list1
    except Exception as e:
        print(e)