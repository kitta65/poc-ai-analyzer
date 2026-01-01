import logging
from datetime import datetime
import streamlit as st
from typing import Final

from app.agents.graphql import run_graphql_agent_with_log
from app.agents.vegalite import run_vegalite_agent_with_log
from app.models.message import MessageSchema, MessageType, MessageRole
from app.cube import get_df_by_query

EXPANDER_TEXT: Final[str] = "See log details"


@st.cache_data
def _get_df_by_query(query):
    return get_df_by_query(query)


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
        elif message.type == MessageType.LOG:
            with st.expander(EXPANDER_TEXT):
                st.write(message.content)
        else:
            st.write(message.content)

if prompt := st.chat_input("Ask anything about data analysis"):
    with st.chat_message(MessageRole.USER.value):
        st.markdown(prompt)
    messages.append(
        MessageSchema(role=MessageRole.USER, type=MessageType.PLAIN, content=prompt)
    )

    with st.chat_message(MessageRole.ASSISTANT.value):
        with st.spinner("Generating graphql..."):
            graphql_result = run_graphql_agent_with_log(prompt)
            query = graphql_result.output

        with st.expander(EXPANDER_TEXT):
            all_messages = graphql_result.all_messages()
            st.code(str(all_messages), language="json")
        messages.append(
            MessageSchema(
                role=MessageRole.ASSISTANT,
                type=MessageType.LOG,
                content=all_messages,
            )
        )

    with st.chat_message(MessageRole.ASSISTANT.value):
        st.code(query, language="graphql")
        messages.append(
            MessageSchema(
                role=MessageRole.ASSISTANT,
                type=MessageType.GRAPHQL,
                content=query,
            )
        )

        df = _get_df_by_query(query)
        st.write(df)
        with st.spinner("Generating Vega-Lite JSON..."):
            schema = run_vegalite_agent_with_log(prompt, df).output.model_dump()
        st.write(schema)
        st.vega_lite_chart(df, schema)
