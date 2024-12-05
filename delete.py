from langchain_chroma import Chroma
from models import embeddings

async def deleting(filename, username):
    try:
        chroma_db_instance = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db_v1",
        )
        
        print(chroma_db_instance.get())
        all_docs = chroma_db_instance.get()
        x=all_docs['metadatas']
        y=all_docs['ids']

        indexlist=[]
        
        for index, obj in enumerate(all_docs['metadatas']):
            print(f"Index: {index}, Object: {obj}")
            file=obj["filename"]
            if(obj["filename"]==filename):
                indexlist.append(index)

        indexlistids=[]
        for index,value in enumerate(all_docs['ids']):
            if(index  in indexlist):
                indexlistids.append(value )

        chroma_db_instance.delete(ids=indexlistids)       
        return f'{username} deleted file {filename} successfully.'
    except Exception as e:
        print(e)


async def deleteAll( username):
    try:
        chroma_db_instance = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory="./chroma_langchain_db_v1",
        )
        
        print(chroma_db_instance.get())
        all_docs = chroma_db_instance.get()
        x=all_docs['metadatas']
        y=all_docs['ids']

        indexlist=[]
        
        for index, obj in enumerate(all_docs['metadatas']):
            print(f"Index: {index}, Object: {obj}")
            file=obj["filename"]
            indexlist.append(index)

        indexlistids=[]
        for index,value in enumerate(all_docs['ids']):
            if(index  in indexlist):
                indexlistids.append(value)

        chroma_db_instance.delete(ids=indexlistids)       
        return f'{username} deleted all files successfully.'
    except Exception as e:
        print(e)