import streamlit as st
from agents.graphql import graphql_agent
from models.message import MessageSchema, MessageType, MessageRole


# ----- config -----
st.set_page_config(
    page_title="PoC of AI Analyzer",
)
st.title("PoC of AI Analyzer")

# ----- initialize -----
if "messages" not in st.session_state:
    st.session_state.messages = []
messages: list[MessageSchema] = st.session_state.messages

# ----- chat -----
for message in messages:
    with st.chat_message(message.role.value):
        if message.type == MessageType.GRAPHQL:
            st.code(message.content, language="graphql")
        else:
            st.write(message.content)

if prompt := st.chat_input("Ask anything about data analysis"):
    with st.chat_message(MessageRole.USER.value):
        st.markdown(prompt)
    messages.append(
        MessageSchema(role=MessageRole.USER, type=MessageType.MESSAGE, content=prompt)
    )

    with st.chat_message(MessageRole.ASSISTANT.value):
        query = graphql_agent.run_sync(prompt).output
        response = st.code(query, language="graphql")

    messages.append(
        MessageSchema(
            role=MessageRole.ASSISTANT, type=MessageType.GRAPHQL, content=query
        )
    )
