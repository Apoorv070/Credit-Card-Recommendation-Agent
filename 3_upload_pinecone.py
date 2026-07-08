#This way of data preperation i will do in jupyeter - notebook since pinecodn i am not able to connect form my local pc
# import json
# import os
# import requests
# from sentence_transformers import SentenceTransformer
# from config import CHUNKS_FILE, PINECONE_API_KEY, PINECONE_INDEX_NAME

# def load_chunks():
#     """Load chunks from JSON file"""
#     with open(CHUNKS_FILE, 'r') as f:
#         chunks = json.load(f)
#     print(f"✓ Loaded {len(chunks)} chunks from {CHUNKS_FILE}")
#     return chunks

# def generate_embeddings(chunks):
#     """Generate embeddings using sentence-transformers"""
    
#     print(f"\nGenerating embeddings for {len(chunks)} chunks...")
#     print("  Loading embedding model (first time takes ~1 min)...")
    
#     # Use lightweight embedding model
#     model = SentenceTransformer('all-MiniLM-L6-v2')
    
#     texts = [chunk['chunk_text'] for chunk in chunks]
    
#     print(f"  Encoding {len(texts)} chunks...")
#     embeddings = model.encode(texts, show_progress_bar=True)
    
#     print(f"✓ Generated {len(embeddings)} embeddings")
#     return embeddings.tolist()

# def upload_to_pinecone(chunks, embeddings):
#     """Upload chunks and embeddings to Pinecone using REST API"""
    
#     # Pinecone REST API endpoint
#     api_url = f"https://api.pinecone.io/vectors/upsert"
    
#     headers = {
#         "Api-Key": PINECONE_API_KEY,
#         "Content-Type": "application/json"
#     }
    
#     print(f"\n✓ Pinecone API configured for index: {PINECONE_INDEX_NAME}")
    
#     # Prepare vectors for upload
#     vectors_to_upsert = []
    
#     print(f"\nPreparing {len(chunks)} vectors for upload...")
    
#     for chunk, embedding in zip(chunks, embeddings):
#         vector_metadata = {
#             "chunk_id": chunk['chunk_id'],
#             "card_name": chunk['card_name'],
#             "pdf_file": chunk['pdf_file'],
#             "page_number": chunk['page_number'],
#             "chunk_text": chunk['chunk_text'],
#             "chunk_length": chunk['chunk_length']
#         }
        
#         vectors_to_upsert.append({
#             "id": chunk['chunk_id'],
#             "values": embedding,
#             "metadata": vector_metadata
#         })
    
#     # Upload in batches
#     batch_size = 50
#     print(f"\nUploading to Pinecone in batches of {batch_size}...")
    
#     for i in range(0, len(vectors_to_upsert), batch_size):
#         batch = vectors_to_upsert[i:i+batch_size]
        
#         payload = {
#             "index": PINECONE_INDEX_NAME,
#             "vectors": batch
#         }
        
#         try:
#             response = requests.post(api_url, headers=headers, json=payload)
#             if response.status_code == 200:
#                 print(f"  ✓ Uploaded batch {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
#             else:
#                 print(f"  ⚠ Batch {i//batch_size + 1} status: {response.status_code}")
#         except Exception as e:
#             print(f"  ⚠ Error uploading batch: {str(e)}")
    
#     print(f"\n✓ Successfully uploaded {len(vectors_to_upsert)} vectors to Pinecone")

# def verify_pinecone_index(chunks):
#     """Verify Pinecone index (basic check)"""
    
#     print(f"\nVerifying Pinecone index...")
#     print(f"  Total chunks uploaded: {len(chunks)}")
    
#     if chunks:
#         test_chunk = chunks[0]['chunk_text'][:100]
#         print(f"  Sample chunk: '{test_chunk}...'")
    
#     print(f"\n✓ Pinecone index ready for RAG retrieval")

# if __name__ == "__main__":
#     print("=" * 60)
#     print("STEP 3: Upload Chunks to Pinecone (REST API + Sentence-Transformers)")
#     print("=" * 60)
    
#     # Check API key
#     if not PINECONE_API_KEY:
#         print("❌ ERROR: PINECONE_API_KEY not found in .env")
#         exit(1)
    
#     print(f"✓ API keys loaded")
#     print(f"  Embedding Model: all-MiniLM-L6-v2 (local)")
#     print(f"  Pinecone Index: {PINECONE_INDEX_NAME}")
#     print()
    
#     # Load chunks
#     chunks = load_chunks()
    
#     # Generate embeddings
#     embeddings = generate_embeddings(chunks)
    
#     # Upload to Pinecone
#     upload_to_pinecone(chunks, embeddings)
    
#     # Verify
#     verify_pinecone_index(chunks)
    
#     print("\n" + "=" * 60)
#     print("✓ Data ingestion pipeline complete!")
#     print("=" * 60)
#     print("\nNext: Week 2 - RAG Retrieval Testing")