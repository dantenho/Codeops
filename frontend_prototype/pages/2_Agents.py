import streamlit as st


def show():
    st.header("Agent Management")
    st.write("Manage your CrewAI agents here.")

    with st.expander("Add New Agent"):
        st.text_input("Agent Name")
        st.text_area("Role Description")
        st.button("Create Agent")

if __name__ == "__main__":
    show()
