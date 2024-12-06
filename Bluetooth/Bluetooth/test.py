# Load the text file containing chunks
with open("D:\MSA\Fall 2024\Grad I\Code\chunks.txt", 'r', encoding='utf-8') as f:
    chunks = f.readlines()

# Generate embeddings for each chunk
embeddings = []
for chunk in chunks:
    print(chunk)