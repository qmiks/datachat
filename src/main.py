import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from date_a_scientist import DateAScientist
from PIL import Image
import IPython
from io import BytesIO
import hashlib

# --- Page Configuration ---
st.set_page_config(page_title="📊 Data Q&A Chatbot", page_icon="💬", layout="wide")

# --- Sidebar for Settings ---
st.sidebar.title("🔧 Settings")
#st.sidebar.write("Ask questions and generate visualizations about your dataset.")
api_key = st.sidebar.text_input("🔑 Enter OpenAI API Key", type="password")


# --- Chat History Order Setting ---
invert_order = st.sidebar.checkbox("Invert Chat History Order", value=True)

# --- Show/Hide Dataframe Setting ---
show_dataframe = st.sidebar.checkbox("Show Dataframe", value=True)

# --- Clear Chat History Button ---
if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.session_state.user_query = ""

# --- Predefined Dataframes ---
predefined_dfs = {
    "Sample Data 1": pd.DataFrame(
        [
            {"name": "Alice", "age": 25, "city": "New York"},
            {"name": "Bob", "age": 30, "city": "Los Angeles"},
            {"name": "Charlie", "age": 35, "city": "Chicago"},
        ]
    ),
    "Sample Data 2": pd.DataFrame(
        [
            {"product": "A", "price": 10, "quantity": 100},
            {"product": "B", "price": 20, "quantity": 150},
            {"product": "C", "price": 30, "quantity": 200},
        ]
    ),
}

# --- Select Predefined Dataframe ---
selected_df_name = st.sidebar.selectbox("Select a predefined dataframe", list(predefined_dfs.keys()))
selected_df = predefined_dfs[selected_df_name]

# --- File Upload ---
st.sidebar.subheader("📂 Upload Your CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

# --- Load Data ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ File uploaded successfully!")
    st.session_state.df = df  # Store the uploaded dataframe in session state
else:
    # Use selected predefined dataframe if no file is uploaded
    if "df" in st.session_state:
        df = st.session_state.df
    else:
        df = selected_df

# --- Initialize DateAScientist ---
if api_key:
    ds = DateAScientist(
        df=df,
        llm_openai_api_token=api_key
    )
else:
    ds = None

# --- Title & Dataset Display ---
st.title("📊 Data Q&A Chatbot with AI-Generated Responses")
st.write("Ask questions and get insights or visualizations from the dataset below.")
if show_dataframe:
    st.dataframe(df)

# --- Initialize Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Input ---
st.subheader("📝 Ask a Question:")
user_query = st.text_input("Type your question (e.g., 'Show me the age distribution.')", key="user_query")

# --- Process User Query ---
if user_query and ds:
    response = ds.chat(user_query)

    # Store chat history
    st.session_state.chat_history.append({"user": user_query, "ai": response})



# --- Display Chat History ---
st.subheader("📜 Chat History")
chat_container = st.container()
with chat_container:
    chat_history = st.session_state.chat_history
    if invert_order:
        chat_history = reversed(chat_history)
    for idx, chat in enumerate(chat_history):
        st.markdown(f"🧑 **You**: {chat['user']}")
        if isinstance(chat['ai'], IPython.core.display.Image):
            # Save the image to a BytesIO buffer
            buffer = BytesIO()
            buffer.write(chat['ai'].data)
            image_data = buffer.getvalue()
            st.image(image_data, caption="Generated Visualization")
        elif isinstance(chat['ai'], pd.DataFrame):
            st.dataframe(chat['ai'])
            query_hash = hashlib.md5(chat['user'].encode()).hexdigest()
            if st.button("Set as Current Dataset", key=f"set_dataset_{query_hash}_{idx}"):
                st.session_state.df = chat['ai']
                st.experimental_set_query_params(rerun="true")
        else:
            st.markdown(f"🤖 **AI**: {chat['ai']}")
        st.write("---")  # Divider

# --- Update DataFrame if Set as Current Dataset is clicked ---
if "df" in st.session_state:
    df = st.session_state.df
    st.sidebar.success("✅ Current dataset updated!")
