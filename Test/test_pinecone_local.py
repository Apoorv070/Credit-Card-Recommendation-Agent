import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "credit-cards")

print("=" * 60)
print("PINECONE LOCAL ACCESS TEST")
print("=" * 60)

# Test 1: Check API key
print("\n1️⃣ Checking API key...")
if PINECONE_API_KEY:
    print(f"   ✓ API key found: {PINECONE_API_KEY[:10]}...")
else:
    print("   ❌ API key NOT found in .env")
    exit(1)

# Test 2: Initialize Pinecone
print("\n2️⃣ Initializing Pinecone...")
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print(f"   ✓ Pinecone initialized")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    exit(1)

# Test 3: Connect to index
print(f"\n3️⃣ Connecting to index: {PINECONE_INDEX_NAME}")
try:
    index = pc.Index(PINECONE_INDEX_NAME)
    print(f"   ✓ Index connected")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    exit(1)

# Test 4: Get index stats
print("\n4️⃣ Fetching index stats...")
try:
    stats = index.describe_index_stats()
    print(f"   ✓ Index stats retrieved:")
    print(f"      - Total vectors: {stats}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# Test 5: Generate test embedding and query
print("\n5️⃣ Testing vector search...")
try:
    print("   Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    test_query = "flight rewards on Axis Atlas"
    print(f"   Test query: '{test_query}'")
    
    embedding = model.encode(test_query)
    print(f"   Embedding dimension: {len(embedding)}")
    
    print(f"   Querying Pinecone...")
    results = index.query(vector=embedding.tolist(), top_k=3, include_metadata=True)
    
    print(f"\n   ✓ Query successful! Retrieved {len(results['matches'])} results:")
    
    for i, match in enumerate(results['matches'], 1):
        print(f"\n      [{i}] Score: {match['score']:.4f}")
        print(f"          ID: {match['id']}")
        if 'metadata' in match:
            print(f"          Card: {match['metadata'].get('card_name', 'N/A')}")
            print(f"          Page: {match['metadata'].get('page_number', 'N/A')}")
            text_preview = match['metadata'].get('chunk_text', '')[:80]
            print(f"          Text: {text_preview}...")
    
except Exception as e:
    print(f"   ❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ PINECONE LOCAL ACCESS TEST COMPLETE")
print("=" * 60)