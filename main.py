"""
main.py
-------
CLI entrypoint for the LangGraph Weather Agent.

What this file does
-------------------
• Loads environment (.env) so API keys are available
• Builds the LangGraph via build_graph()
• Prompts for input city/question and notification flags
• Invokes the graph and prints results
"""
from dotenv import load_dotenv
from agent_graph import build_graph, State

def run_cli():
    load_dotenv()
    graph = build_graph()  # Compile the graph once
    print("🌦️ LangGraph AI Weather Agent")
    city = input("City: ").strip()
    question = input("Your question (e.g., Do I need an umbrella?): ").strip()
    send_email = input("Send to Email? (y/N): ").strip().lower() == "y"
    send_wa = input("Send to WhatsApp? (y/N): ").strip().lower() == "y"

    init: State = {
        "city": city,
        "question": question,
        "send_email_flag": send_email,
        "send_whatsapp_flag": send_wa
    }
    final_state = graph.invoke(init)
    print("⛅ Weather:", final_state.get("weather_text"))
    print("🤖 Agent:", final_state.get("answer"))
    print("✅ Done.")

if __name__ == "__main__":
    run_cli()
