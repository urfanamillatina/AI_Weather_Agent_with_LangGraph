"""
streamlit_app.py
----------------
Optional UI runner for the LangGraph Weather Agent.

What it shows
-------------
• Text inputs for city and question
• Flags to send Email and/or WhatsApp
• Uses build_graph() and graph.invoke(...) under the hood
"""
import streamlit as st
from dotenv import load_dotenv
from agent_graph import build_graph, State

load_dotenv()
st.set_page_config(page_title="LangGraph Weather Agent", page_icon="🌦️", layout="centered")
st.title("🌦️ LangGraph AI Weather Agent")
st.caption("Ask about the weather. The agent fetches data, reasons with GPT, and can notify you via email/WhatsApp.")

city = st.text_input("City")
question = st.text_input("Your question", placeholder="Do I need an umbrella today?")
send_email_flag = st.checkbox("Also send to Email (.env required)", value=False)
send_whatsapp_flag = st.checkbox("Also send to WhatsApp/SMS (Twilio required)", value=False)

if st.button("Ask"):
    graph = build_graph()
    init: State = {
        "city": city,
        "question": question,
        "send_email_flag": send_email_flag,
        "send_whatsapp_flag": send_whatsapp_flag,
    }
    with st.spinner("Fetching weather and thinking..."):
        final_state = graph.invoke(init)
    st.info(final_state.get("weather_text"))
    st.success(final_state.get("answer"))
    st.toast("Done ✅", icon="✅")
