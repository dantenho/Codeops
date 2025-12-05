import streamlit as st

st.set_page_config(
    page_title="CodeAgents Prototype",
    page_icon="🤖",
    layout="wide"
)

st.title("CodeAgents Prototype")

st.sidebar.success("Select a page above.")

st.markdown("""
## Welcome to CodeAgents

This is a prototype for the CodeAgents platform.

### Modules
- **Frontend**: Streamlit
- **Organizator**: CrewAI
- **Nodes**: ComfyUI, LoRa, etc.
""")
