from sentence_transformers import SentenceTransformer
import chromadb
model = SentenceTransformer("all-MiniLM-L6-v2")
file_name = "sample.txt"
with open(file_name, "r") as file:
    text = file.read()
#chunking
chunks = []
chunk_size = 100
chunk_overlap=20
step = chunk_size - chunk_overlap
for i in range(0, len(text), chunk_size):
    chunk = text[i:i+chunk_size] #(0 - 100) (100 - 200)
    chunks.append(chunk)
#for i in range(len(chunks)):
    #print(f"Chunk {i + 1} -> {chunks[i]}")
#embedding
embeddings = model.encode(chunks)
print(len(embeddings))
print(embeddings.shape)