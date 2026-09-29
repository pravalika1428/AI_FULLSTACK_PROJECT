import ollama
import streamlit as st
st.title(":rainbow[SWEETY HERE!!!🎀]")
with st.sidebar:
    personalities = {
        "kid": "Give the answers like you are explaining to a 5 year old kid. Give the answer in 2-3 lines only.",
        "professor": "You are an IIT professor. Explain the topics using correct terminology. Give me answers in 2-3 lines only."
    }
    personality = st.selectbox("Select a personality", personalities.keys())
if "messages" not in st.session_state:
    st.session_state.messages=[]
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
question=st.chat_input("ask question:🤔")

        

if question:
    with st.chat_message("user"):
        st.write("user:",question)


    st.session_state.messages.append({"role":"user",
                 "content":question})
    with st.spinner("Thinking...🥱"):
        response=ollama.chat(
            model="llama3.2:3b",
            messages=
            st.session_state.messages
        )
    with st.chat_message("assistant"):

        st.write("AI:",response["message"]["content"])
    st.session_state.messages.append({"role":"assistant",
                 "content":response["message"]["content"]})


with st.sidebar:
    st.header("Chat Settings⚙️")
    if st.button("Clear Chat🗑️"):
        st.session_state.messages = []
        st.success("Chat cleared successfully!!")
    uploaded_file=st.file_uploader("upload a file...📁")
    if uploaded_file is not None:
        st.write("file uploaded successfully✅")
        context=uploaded_file.read().decode("utf-8")
        if st.button("Display"):
            st.text(context)
st.balloons()

