"""
agent_graph.py
---------------
A minimal **LangGraph**-powered agent that:
  1) Fetches weather (tool node)
  2) Uses OpenAI to reason and craft a friendly answer (reasoning node)
  3) Sends notifications via Email/WhatsApp (action node)

Why LangGraph?
--------------
LangGraph (by the LangChain team) provides a clean way to build **stateful, modular,
event-driven AI systems**. You define a **State** (shared memory), connect **nodes**
(discrete steps), and wire them with **edges** (flow). The runtime executes the graph
while passing the evolving state along the pipeline.
"""
import os
from typing import TypedDict, Dict, Any
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from openai import OpenAI
from weather_tool import get_weather, format_weather_text
from notify_tool import send_email, send_whatsapp

class State(TypedDict, total=False):
    """
    The shared state that flows through the graph. Nodes can read/write keys.
    Keys:
      city:                Input city name
      question:            User's natural-language question
      weather:             Raw structured weather dict (from tool)
      weather_text:        Human-readable weather summary
      answer:              Final LLM-composed answer
      send_email_flag:     Whether to send email notification
      send_whatsapp_flag:  Whether to send WhatsApp/SMS notification
    """
    city: str
    question: str
    weather: Dict[str, Any]
    weather_text: str
    answer: str
    send_email_flag: bool
    send_whatsapp_flag: bool

# Load environment and initialize OpenAI client once at import time
load_dotenv()
oai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Node 1: Fetch weather -------------------------------------------------
def node_fetch_weather(state: State) -> State:
    """
    Tool node: call OpenWeatherMap and attach both structured data and a readable summary
    back into the LangGraph state. This node is pure I/O + formatting.
    """
    city = state.get("city", "").strip()
    w = get_weather(city)
    wt = format_weather_text(w) if w else "No weather data."
    return {"weather": w, "weather_text": wt}

# ---- Node 2: Reason with GPT ----------------------------------------------
def node_reason(state: State) -> State:
    """
    Reasoning node: combine user's question with the weather summary and produce a
    concise, helpful answer using OpenAI (gpt-4o-mini). This is intentionally short
    for workshop speed and clarity.
    """
    question = state.get("question", "Give a helpful weather summary.")
    wt = state.get("weather_text", "No weather data.")
    prompt = f"""You are a concise, friendly weather assistant.
    Use the provided weather info to answer in 1-2 sentences.
    Weather info: {wt}
    User question: {question}
    """
    resp = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.4 #deterministic
    )
    answer = resp.choices[0].message.content.strip()
    return {"answer": answer}

# ---- Node 3: Notify via Email/WhatsApp ------------------------------------
def node_notify(state: State) -> State:
    """
    Action node: optionally deliver the final answer to email and/or WhatsApp, based
    on flags provided at the start. Side-effectful by design.
    """
    ans = state.get("answer", "")
    if state.get("send_email_flag"):
        send_email(ans)
    if state.get("send_whatsapp_flag"):
        send_whatsapp(ans)
    return {}

def build_graph():
    """
    Build and compile the LangGraph StateGraph.
    Flow: fetch_weather -> reason -> notify -> END
    """
    g = StateGraph(State)
    g.add_node("fetch_weather", node_fetch_weather)  # Node registration
    g.add_node("reason", node_reason)
    g.add_node("notify", node_notify)

    g.set_entry_point("fetch_weather")               # Entry point
    g.add_edge("fetch_weather", "reason")            # Deterministic edges
    g.add_edge("reason", "notify")
    g.add_edge("notify", END)                        # End of pipeline

    return g.compile()

if __name__ == "__main__":
    # Example single-run for quick local testing
    graph = build_graph()
    init: State = {
        "city": os.getenv("DEMO_CITY","Mumbai"),
        "question": os.getenv("DEMO_Q","Do I need an umbrella today?"),
        "send_email_flag": True,
        "send_whatsapp_flag": False
    }
    final_state = graph.invoke(init)
    print("⛅ Weather:", final_state.get("weather_text"))
    print("🤖 Agent:", final_state.get("answer"))
    print("✅ Notifications sent (if configured).")
