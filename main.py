import streamlit as st
from constants.role import Role
from pydantic_ai import Agent


@st.cache_resource
def get_agent(model: str):
    return Agent(model, instructions="Be concise, reply with one sentence.")


MODEL = "openai:gpt-4.1-mini"

agent = get_agent(MODEL)

# ----- config -----
st.set_page_config(
    page_title="PoC of AI Analyzer",
)
st.title("PoC of AI Analyzer")

# ----- initialize -----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----- chat -----
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask anything about data analysis"):
    with st.chat_message(Role.USER.value):
        st.markdown(prompt)
    st.session_state.messages.append({"role": Role.USER.value, "content": prompt})

    with st.chat_message(Role.ASSISTANT.value):
        response = agent.run_sync(prompt)
        st.write(response.output)
    st.session_state.messages.append(
        {"role": Role.ASSISTANT.value, "content": response.output}
    )
