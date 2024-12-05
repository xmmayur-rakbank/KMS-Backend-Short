import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, List
from pydantic import BaseModel
from training import training
from chat import chatting
from delete import deleting, deleteAll
from feedback import feedbackSave
from list import listing, listChunks

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

class FeedbackRequest(BaseModel):
    SessionId: str
    MessageId: str
    Question: str
    Answer: str
    Textual_Feedback : str
    Numerical_Feedback : int
    reason: str

@app.post("/feedback/")
async def feedback(feedbackRequest: FeedbackRequest):
    try:
        print(feedbackRequest)
        answer = await feedbackSave(feedbackRequest.SessionId, feedbackRequest.MessageId, feedbackRequest.Answer, feedbackRequest.Question, feedbackRequest.Textual_Feedback, feedbackRequest.Numerical_Feedback,feedbackRequest.reason)
        return answer
    except Exception as e:
        print(f"Exception in chat() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")

@app.post("/deleteFile/")
async def delete(filename: Annotated[str, Form()], username: Annotated[str, Form()]):
    try:
        await deleting(filename, username)
        return "deleted successfully"
    except Exception as e:
        print(f"Exception in training() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")
 
@app.post("/deleteAll/")
async def delete(username: Annotated[str, Form()]):
    try:
        await deleteAll(username)
        return "deleted successfully"
    except Exception as e:
        print(f"Exception in training() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")

@app.get("/list/")
async def list():
    try:
        results = await listing()
        return results
    except Exception as e:
        print(f"Exception in training() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")
 
@app.post("/listChunks/")
async def listchunks(file : Annotated[str, Form()]):
    try:
        results = await listChunks(file)
        return results
    except Exception as e:
        print(f"Exception in training() : {e}")
        raise HTTPException(status_code=500, detail=f"Something Went Wrong! Please try again!! {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app)