import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List
from pydantic import BaseModel
from training import training
from chat import chatting


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    try:
        return {"Hello": "Hello from API"}
    except Exception as e:
        return {"message": str(e)}
    
@app.post("/train/")
async def train(departmant: Annotated[str, Form()], pdf_files: List[UploadFile]):
    try:
        for file in pdf_files:
            await training(file, departmant)
        return "training successful"
    except Exception as e:
        print(f"Exception in training() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")
    
class ChatMessage(BaseModel):
    user: str
    assistant: str
    conversationId: str
    messageId: str
    

class ChatRequest(BaseModel):
    Query: str
    ChatHistory: List[ChatMessage] 

@app.post("/chat/")
async def chat(username:str, departmant: list[str] , chatRequest: ChatRequest, is_followup: bool):
    try:
        print(chatRequest)
        answer = await chatting(chatRequest.Query, departmant, chatRequest, is_followup, username)
        return answer
    except Exception as e:
        print(f"Exception in chat() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")



if __name__ == "__main__":
    uvicorn.run(app)