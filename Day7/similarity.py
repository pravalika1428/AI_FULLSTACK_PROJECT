import chromadb,ollama,streamlit as st
#model= SentenceTransformer("all-MiniLM-L6-v2")
st.title("TALK WITH SAMMY")
with st.sidebar:
    uploaded_file=st.file_uploder("Upload a file")
    if uploaded_file:
        text=uploaded_file.read().decode("utf-8")
        with st.expander("Preview"):
            st.text(text)
#file_name="sample.txt"
#with open(file_name,"r") as file:
    #text=file.read()
#chunking
        chunks=[]
        chunk_size=100
        chunk_overlap=20
        step=chunk_size-chunk_overlap #100-20=80
        for i in range(0,len(text),step):
            chunk=text[i:i+chunk_size] #(0-100)(80-180)(160-260)
            chunks.append(chunk)
        #for i in range(len(chunks)):
            #print(f"Chunk{i+1} -> {chunks[i]}")

        #embedding
        embeddings = model.encode(chunks)
        #print(embeddings[0])
        #print(len(embeddings))
        #print(embeddings.shape)

        #Vector DB
        client=chromadb.PersistentClient(path="./chroma_db")
        collection= client.get_or_create_collection(name="My_Documents")
        ids=[]
        for i in range(len(chunks)):
            ids.append(f"{file_name}_{i}")
        collection.add(
            documents=chunks,
            ids=ids,
            embeddings=embeddings.tolist()
        )
#results=collection.get()
#chunk1=collection.get(ids=['sample.txt_0'])
#print(chunk1)

#Query Phase
question= st.chat_input("Ask a question")
if question:
    q_embedding = model.encode(question)
    top_k=3
    results=collection.query(
        query_embeddings=[q_embedding.tolist()],
        n_results=top_k
    )
    retrieved_chunks=(results['documents'][0])
    retrieved_ids=results["ids"][0]
    #print(retrieved_chunks)
    #for i in range(len(results['documents'][0])):
    #   print(f"Chunk{i+1}")
    #   print(results['documents'][0][i])
    context='\n'.join(retrieved_chunks)
    #print(context)

    #prompt
    prompt = f'''
    Answer the question using the context given below only. 
    Question:{question}
    Context:{context}
    Answer:
    '''
    #print(prompt)
    response=ollama.chat(
        model="llama3.2:3b",
        messages=[{"role":"user","content":prompt}]
    )
    st.write(response["message"]["content"])