import logging
from datetime import datetime
import streamlit as st
from typing import Final

from app.agents.graphql import run_graphql_agent_with_log
from app.agents.vegalite import run_vegalite_agent_with_log
from app.models.message import MessageSchema, MessageType, MessageRole
from app.cube import get_df_by_query


@st.cache_data
def _get_df_by_query(query):
    return get_df_by_query(query)


def show(message: MessageSchema) -> None:
    with st.chat_message(message.role.value):
        writer = st
        if message.expander_text:
            writer = st.expander(message.expander_text)
        match message.type:
            case MessageType.GRAPHQL:
                writer.code(message.content, language="graphql")
            case _:
                writer.write(message.content)


# ----- config -----
st.set_page_config(
    page_title="PoC of AI Analyzer",
)
st.title("PoC of AI Analyzer")

# ----- initialize -----
if "messages" not in st.session_state:
    st.session_state.messages = []
messages: list[MessageSchema] = st.session_state.messages

if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d%H%M%S")
logging.basicConfig(filename=f"logs/{st.session_state.session_id}.log", level="INFO")

st.caption(f"Session ID: {st.session_state.session_id}")

# ----- chat -----
for message in messages:
    with st.chat_message(message.role.value):
        if message.type == MessageType.GRAPHQL:
            st.code(message.content, language="graphql")
        else:
            st.write(message.content)

if prompt := st.chat_input("Ask anything about data analysis"):
    prompt_message = MessageSchema(
        role=MessageRole.USER, type=MessageType.PLAIN, content=prompt
    )
    show(prompt_message)
    messages.append(prompt_message)

    with st.spinner("Generating GraphQL Query..."):
        query = run_graphql_agent_with_log(prompt).output
    query_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.GRAPHQL,
        content=query,
        expander_text="Show GraphQL Query",
    )
    show(query_message)
    messages.append(query_message)

    df = _get_df_by_query(query)
    df_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.OTHER,
        content=df,
        expander_text="Show DataFrame",
    )
    show(df_message)
    messages.append(df_message)

    with st.spinner("Generating Vega-Lite JSON..."):
        vegalite = run_vegalite_agent_with_log(prompt, df).output.model_dump()
    vegalite_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.OTHER,
        content=vegalite,
        expander_text="Show Vega-Lite JSON",
    )
    show(vegalite_message)
    messages.append(vegalite_message)

    st.vega_lite_chart(df, vegalite)
