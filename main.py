import logging
from datetime import datetime

import pandas as pd
import streamlit as st

from app.agents.router import run_router_agent_with_log
from app.models.message import MessageSchema, MessageType, MessageRole
from app.agents.router import UnableToProceedRequest


def _show(message: MessageSchema) -> None:
    match message.type:
        case MessageType.GRAPHQL:
            st.code(message.content, language="graphql")
        case MessageType.CHART:
            df, vegalite = message.content
            st.vega_lite_chart(df, vegalite)
        case _:
            st.write(message.content)


def show(message: MessageSchema) -> None:
    with st.chat_message(message.role.value):
        if message.expander_text is not None:
            with st.expander(message.expander_text):
                _show(message)
        else:
            _show(message)


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
    logging.basicConfig(
        filename=f"logs/{st.session_state.session_id}.log",
        level=logging.INFO,
        force=True,  # required in streamlit
    )

st.caption(f"Session ID: {st.session_state.session_id}")

# ----- chat -----
for message in messages:
    show(message)

if prompt := st.chat_input("Ask anything about data analysis"):
    prompt_message = MessageSchema(
        role=MessageRole.USER, type=MessageType.PLAIN, content=prompt
    )
    show(prompt_message)
    messages.append(prompt_message)

    with st.spinner("Generating..."):
        response = run_router_agent_with_log(prompt)

    if isinstance(response.output, UnableToProceedRequest):
        unable_message = MessageSchema(
            role=MessageRole.ASSISTANT,
            type=MessageType.PLAIN,
            content=f"Unable to proceed: {response.output.reason}",
        )
        show(unable_message)
        messages.append(unable_message)
        st.stop()

    query_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.GRAPHQL,
        content=response.output.graphql,
        expander_text="Show GraphQL Query",
    )
    show(query_message)
    messages.append(query_message)

    df = pd.DataFrame(response.output.data)
    df_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.OTHER,
        content=df,
        expander_text="Show DataFrame",
    )
    show(df_message)
    messages.append(df_message)

    vegalite = response.output.vegalite.model_dump()
    vegalite_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.OTHER,
        content=vegalite,
        expander_text="Show Vega-Lite JSON",
    )
    show(vegalite_message)
    messages.append(vegalite_message)

    chart_message = MessageSchema(
        role=MessageRole.ASSISTANT,
        type=MessageType.CHART,
        content=(df, vegalite),
    )
    show(chart_message)
    messages.append(chart_message)
