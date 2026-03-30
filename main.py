from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, Interaction
from agent import run_agent

app = FastAPI()


# -------- DB Dependency --------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------- SCHEMA --------
class InteractionCreate(BaseModel):
    hcp_name: str
    interaction_type: str
    date: str
    topics: str
    notes: str


class ChatInput(BaseModel):
    message: str


# -------- FORM LOG --------
@app.post("/log-form")
def log_form(data: InteractionCreate, db: Session = Depends(get_db)):
    obj = Interaction(
        hcp_name=data.hcp_name,
        interaction_type=data.interaction_type,
        topics=data.topics,
        notes=data.notes
    )
    db.add(obj)
    db.commit()
    return {"message": "Logged via form"}


# -------- CHAT LOG --------
@app.post("/chat")
def chat_log(input: ChatInput):
    response = run_agent(input.message)
    return {"response": response}


# -------- FETCH --------
@app.get("/interactions")
def get_all(db: Session = Depends(get_db)):
    return db.query(Interaction).all()
