import altair as alt
import logging
import requests
import streamlit as st

from app.agents.graphql import graphql_agent
from app.agents.vegalite import vegalite_agent
from app.models.message import MessageSchema, MessageType, MessageRole
from app.constants import CUBE_API

logger = logging.getLogger("ai-analyzer")


@st.cache_data()
def get_data_by_query(query: str) -> dict:
    response = requests.post(f"{CUBE_API}/graphql", json={"query": query})
    dict_ = response.json()
    # TODO: impl retry logic
    if dict_.get("data") is None:
        logger.info(f"status_code: {response.status_code}")
        logger.info(f"text: {response.text}")
    return dict_


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
        with st.spinner("Just a moment..."):
            output = vegalite_agent.run_sync(prompt).output
            schema = output.model_dump_json()
        st.code(schema, language="json")
        st.write("Chart Preview:")
        # chart = alt.Chart().from_json(schema)
        chart = alt.Chart().from_dict(output.model_dump())
        st.vega_lite_chart(chart.to_dict())

    messages.append(
        MessageSchema(role=MessageRole.ASSISTANT, type=MessageType.JSON, content=schema)
    )
