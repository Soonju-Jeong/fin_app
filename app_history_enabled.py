import streamlit as st
import json
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

client = OpenAI()

def query_converter(query, data, company_name):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "developer",
                "content": f"""You are a helpful financial assistant that takes financial data and answers user questions based on that. Also try to generate a small summary for the generated answer. Make sure the answer is in a human tone and doesn't sound like a chatbot.
                Here is your company: {company_name}
                Here is {company_name}'s financial data: {data}
                """
            },
            {
                "role": "user",
                "content": f"Here is your NLQ: {query}"
            }
        ]
    )
    return response.choices[0].message.content

def metric_generator(query, data, company_name):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "developer",
                "content": f"""You are a helpful financial assistant that takes financial data and returns financial metrics along with their values that are relevant to answer the user query in JSON format. Your task is to only return metrics and their values. Do not generate anything else or answer the user query.
                Make sure to return a nested dictionary for financial metrics that have different values in different years.
                Here is your company: {company_name}
                Here is {company_name}'s financial data: {data}
                """
            },
            {
                "role": "user",
                "content": f"Here is your query: {query}"
            }
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

st.set_page_config(layout="wide")
st.title("OPEN-DART Company AI Query Assistant")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

company_option = st.selectbox(
    label="Select one company to ask questions",
    options=["Hanwha Aerospace", "Hyundai Mobi", "Kakao", "LG Chem", "LG electronic", "NAVER", "s company", "Samsung Biologic", "samsung", "SK hyni"],
    index=None
)

if company_option:
    file_path = f"/Users/pushpanjali/small_poc/open_dart/fs_data_pushp/{company_option}_data.json"
    with open(file_path, "r") as f:
        data = json.load(f)
    context = json.dumps(data, indent=2)

    st.sidebar.subheader("💬 Chat History")
    for chat in st.session_state.chat_history:
        st.sidebar.markdown(f"**You:** {chat['query']}")
        st.sidebar.markdown(f"**Assistant:** {chat['response']}")

    query = st.text_input("Ask a question about the company's financials")

    if query:
        col1, col2 = st.columns([0.7, 0.3], gap="medium", border=False)

        with col1:
            st.header("Answer:")
            resp = query_converter(query, context, company_option)
            st.markdown(resp)

            # Save chat history
            st.session_state.chat_history.append({"query": query, "response": resp})

        with col2:
            st.header("Relevant Financial Metrics:")
            metrices = json.loads(metric_generator(query, context, company_option))
            for category, yearly_data in metrices.items():
                try:
                    df = pd.DataFrame.from_dict(yearly_data, orient="index", columns=[category])
                    df.index.name = "Year"
                    # df = df.sort_index(ascending=False).fillna(0)
                    df = df.replace('', pd.NA)
                    df = df.apply(pd.to_numeric, errors='coerce')
                    print(df.info())
                    print("-----------------")
                    st.subheader(category)
                    try :
                        st.dataframe(df, use_container_width=True)
                    except :
                        st.write(df)
                except:
                    pass
