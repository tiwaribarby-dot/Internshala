import os
from langgraph.graph import StateGraph
from typing import TypedDict, Optional
from database import SessionLocal, Interaction
from datetime import datetime, timedelta
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# -------- STATE --------
class AgentState(TypedDict):
    user_input: str
    extracted: dict
    response: str


# -------- LLM CALL --------
def call_llm(prompt):
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return completion.choices[0].message.content


# -------- TOOL 1: Extract --------
def extract_data(state: AgentState):
    prompt = f"""
    Extract structured data from this:
    "{state['user_input']}"

    Return JSON:
    {{
        "hcp_name": "",
        "interaction_type": "",
        "date": "",
        "topics": "",
        "notes": ""
    }}
    """
    result = call_llm(prompt)

    import json
    try:
        extracted = json.loads(result)
    except:
        extracted = {}

    return {"extracted": extracted}


# -------- TOOL 2: Log Interaction --------
def log_interaction(state: AgentState):
    db = SessionLocal()
    data = state["extracted"]

    interaction = Interaction(
        hcp_name=data.get("hcp_name"),
        interaction_type=data.get("interaction_type"),
        date=datetime.utcnow(),
        topics=data.get("topics"),
        notes=data.get("notes"),
    )

    db.add(interaction)
    db.commit()
    db.close()

    return {"response": "Interaction logged successfully."}


# -------- TOOL 3: Edit --------
def edit_interaction(state: AgentState):
    db = SessionLocal()
    data = state["extracted"]

    obj = db.query(Interaction).filter(
        Interaction.hcp_name == data.get("hcp_name")
    ).first()

    if obj:
        obj.topics = data.get("topics", obj.topics)
        obj.notes = data.get("notes", obj.notes)
        db.commit()

    db.close()
    return {"response": "Interaction updated."}


# -------- TOOL 4: Search --------
def search_hcp(state: AgentState):
    db = SessionLocal()
    name = state["user_input"]

    results = db.query(Interaction).filter(
        Interaction.hcp_name.contains(name)
    ).all()

    db.close()

    return {
        "response": f"Found {len(results)} records for {name}"
    }


# -------- TOOL 5: Summarize --------
def summarize_meeting(state: AgentState):
    text = state["user_input"]

    summary = call_llm(f"Summarize this meeting:\n{text}")
    return {"response": summary}


# -------- TOOL 6: Follow-up --------
def schedule_followup(state: AgentState):
    follow_date = datetime.utcnow() + timedelta(days=7)
    return {"response": f"Suggested follow-up: {follow_date.date()}"}


# -------- GRAPH --------
builder = StateGraph(AgentState)

builder.add_node("extract", extract_data)
builder.add_node("log", log_interaction)

builder.set_entry_point("extract")
builder.add_edge("extract", "log")

graph = builder.compile()


def run_agent(user_input: str):
    result = graph.invoke({
        "user_input": user_input
    })
    return result.get("response", "Done")
