import chromadb
import ollama, streamlit as st
model = "nomic-embed-text"
st.balloons()
st.title("TALK WITH SWEETY🎀")
if "messages" not in st.session_state:
     st.session_state.messages=[]
with st.sidebar:
    st.header("Chat Settings⚙️")
    personalities = {
            "kid": "Give the answers like you are explaining to a 5 year old kid. Give the answer in 2-3 lines only.",
            "professor": "You are an IIT professor. Explain the topics using correct terminology. Give me answers in 2-3 lines only."
        }
    personality = st.selectbox("Select a personality", personalities.keys())
    top_k = st.slider("Select no of top results", min_value=1, max_value=5, value=3)
    uploaded_file=st.file_uploader("upload a file...📁")
    if uploaded_file is not None:
        st.write("file uploaded successfully✅")
        text=uploaded_file.read().decode("utf-8")
        if st.button("Display"):
            st.text(text)
# chunking
        chunks = []
        chunk_size = 100
        chunk_overlap = 20
        step = chunk_size - chunk_overlap   # 100 - 20 = 80
        for i in range(0, len(text), step):
            chunk = text[i:i+chunk_size]  # (0 - 100)(80 - 180)(160 - 260)....
            chunks.append(chunk)
# print(len(chunk[0]))
# for i in range(len(chunks)):
#   print(f"chunk{i+1} -> {chunks[i]}")

# Embedding
        embeddings = []
        for chunk in chunks:
            response = ollama.embed(
                model="nomic-embed-text",
                input=chunk
            )
            embeddings.append(response["embeddings"][0])
# print(embeddings[0])
# print(len(embeddings))

# Vector DB
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="My_Documents")
        ids = []
        for i in range(len(chunks)):
            ids.append(f"{uploaded_file.name}_{i}")

        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist()
        )
    
# res = collection.get()
# print(res)
# chunk1 = collection.get(ids=['0'])
# print(chunk1)

# query phase
    st.subheader("Chat options")
    with st.container():
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.success("Chat history deleted...")
    with st.expander("Chat History"):
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

question = st.chat_input("Ask a question: ")
if question:
    if uploaded_file:
        st.write(question)
        q_embedding = model.encode(question)
        results = collection.query(
            query_embeddings=[q_embedding.tolist()],
            n_results=top_k
        )
        retrieved_chunks = (results['documents'][0])
        retrieved_ids = results["ids"][0]
        context = '\n'.join(retrieved_chunks)
        prompt = f'''
        Answer the question using the context given below only.
        Question: {question}
        Context: {context}
        Answer:
        '''
        question_response = ollama.embed(
            model="nomic-embed-text",
            input=question
        )
        q_embedding = question_response["embeddings"][0]
        top_k = 3
        results = collection.query(
            query_embeddings = [q_embedding],
            n_results = top_k
        )
        retrieved_chunks = (results['documents'][0])
        retrieved_ids = results["ids"][0]

        #print(retrieved_chunks)
        # for i in range(len(results['documents'][0])):
        #     print(f"Chunk {i+1}")
        #     print(results['documents'][0][i])
        context= '\n'.join(retrieved_chunks)
        # print(context)
        #prompt
        # print(prompt)
        response = ollama.chat(
            model = "llama3.2:3b",
            messages =[{"role" : "user",
            "content" : prompt}]
        )
        st.session_state.messages(response["message"]["content"])
    else:
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

        