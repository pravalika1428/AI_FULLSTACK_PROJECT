import streamlit as st
import chromadb
import ollama

from faq_data import FAQS


# -----------------------------
# Configuration
# -----------------------------

CHAT_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "nomic-embed-text"

DATABASE_PATH = "chroma_db"
COLLECTION_NAME = "college_faq"


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="College FAQ Chatbot",
    page_icon="🎓",
    layout="centered"
)


# -----------------------------
# Custom CSS
# -----------------------------

st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 38px;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .subtitle {
            text-align: center;
            color: gray;
            margin-bottom: 30px;
        }

        .info-box {
            padding: 15px;
            border-radius: 10px;
            background-color: #f0f2f6;
            margin-bottom: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Title
# -----------------------------

st.markdown(
    '<div class="main-title">🎓 College FAQ Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ask questions about college facilities, admissions, exams, placements and more.</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Create ChromaDB
# -----------------------------

@st.cache_resource
def create_collection():

    client = chromadb.PersistentClient(
        path=DATABASE_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Add FAQ data only if collection is empty
    if collection.count() == 0:

        documents = []
        ids = []
        embeddings = []

        for index, faq in enumerate(FAQS):

            text = (
                f"Question: {faq['question']}\n"
                f"Answer: {faq['answer']}"
            )

            response = ollama.embeddings(
                model=EMBEDDING_MODEL,
                prompt=text
            )

            documents.append(text)
            ids.append(str(index))
            embeddings.append(response["embedding"])

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings
        )

    return collection


# -----------------------------
# Load Collection
# -----------------------------

try:

    collection = create_collection()

except Exception as e:

    st.error(
        "Unable to connect to Ollama. "
        "Make sure Ollama is running and the required models are installed."
    )

    st.code(
        "ollama pull llama3.2:3b\n"
        "ollama pull nomic-embed-text"
    )

    st.stop()


# -----------------------------
# Generate Answer
# -----------------------------

def generate_answer(question):

    # Create embedding for user question
    response = ollama.embeddings(
        model=EMBEDDING_MODEL,
        prompt=question
    )

    query_embedding = response["embedding"]

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        return "Sorry, I could not find relevant information."

    context = "\n\n".join(documents)

    # Prompt for LLM
    prompt = f"""
You are a helpful College FAQ Chatbot.

Answer the user's question using ONLY the information
provided in the context below.

If the answer is not available in the context,
say that you do not have that information.

Do not invent college information.

Context:
{context}

User Question:
{question}

Give a clear and simple answer.
"""

    # Generate response
    result = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return result["message"]["content"]


# -----------------------------
# Suggested Questions
# -----------------------------

st.markdown("### 💡 Try asking")

suggestions = [
    "What courses are offered?",
    "Does the college provide hostel facilities?",
    "How does the placement process work?",
    "What are the library timings?",
    "Is attendance compulsory?",
    "How can I apply for admission?"
]

cols = st.columns(2)

for index, question in enumerate(suggestions):

    if cols[index % 2].button(
        question,
        use_container_width=True
    ):
        st.session_state["selected_question"] = question


# -----------------------------
# Chat Input
# -----------------------------

question = st.chat_input(
    "Ask your college-related question..."
)


# Use selected suggestion
if "selected_question" in st.session_state:

    question = st.session_state.pop(
        "selected_question"
    )


# -----------------------------
# Chat History
# -----------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -----------------------------
# Process Question
# -----------------------------

if question:

    # Display user question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    # Generate chatbot response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                answer = generate_answer(question)

                st.markdown(answer)

            except Exception as e:

                answer = (
                    "Sorry, something went wrong while "
                    "processing your question."
                )

                st.error(answer)

                st.caption(str(e))


    # Save response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )