import json
import sqlite3
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import DB_PATH
import os

class LocalRAGRetriever:
    """Local RAG retrieval using FAISS + SQLite (offline mode)"""
    
    CARD_NAME_MAPPING = {
        'Axis_Atlas': 'Axis Bank Atlas Credit Card',
        'HDFC_Infinia': 'HDFC Infinia',
        'HDFC_Regalia': 'HDFC Regalia Gold',
        'AmericanExpress_PlatinumTravel': 'American Express Platinum Travel Credit Card',
        'HDFC_DCB': 'HDFC Diners Club Black',
        'SBI_Cashback': 'SBI Cashback Credit Card'
    }
    
    def __init__(self, faiss_index_path='data/faiss_index.bin', 
                 chunks_mapping_path='data/chunks_mapping.json',
                 model_path='data/models/all-MiniLM-L6-v2',
                 db_path=DB_PATH):
        """Initialize FAISS index and load chunks"""
        
        print("Initializing Local RAG Retriever (Offline Mode)...")
        
        # Load FAISS index
        try:
            self.faiss_index = faiss.read_index(faiss_index_path)
            print(f"✓ FAISS index loaded: {faiss_index_path}")
        except Exception as e:
            print(f"❌ Error loading FAISS index: {str(e)}")
            raise
        
        # Load chunks mapping
        try:
            with open(chunks_mapping_path, 'r') as f:
                self.chunks = json.load(f)
            print(f"✓ Chunks mapping loaded: {len(self.chunks)} chunks")
        except Exception as e:
            print(f"❌ Error loading chunks mapping: {str(e)}")
            raise
        
        # Load SQLite database
        try:
            self.db_path = db_path
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            print(f"✓ SQLite database connected: {db_path}")
        except Exception as e:
            print(f"❌ Error connecting to SQLite: {str(e)}")
            raise
        
        # Load embedding model (offline)
        try:
            if os.path.exists(model_path):
                # Load from local cache
                self.model = SentenceTransformer(model_path)
                print(f"✓ Embedding model loaded (offline): {model_path}")
            else:
                # Fallback: try to load from cache
                print(f"⚠ Model not found at {model_path}")
                print(f"  Trying to load from HuggingFace cache...")
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print(f"✓ Embedding model loaded from cache")
        except Exception as e:
            print(f"❌ Error loading embedding model: {str(e)}")
            print(f"   Make sure model is downloaded and placed in {model_path}")
            raise
        
        print("\n✅ Local RAG Retriever initialized (Offline Mode)!\n")
    
    def normalize_card_name(self, card_name: str) -> str:
        """Normalize card name from chunks to database format"""
        return self.CARD_NAME_MAPPING.get(card_name, card_name)
    
    def retrieve_from_faiss(self, query, top_k=5):
        """Retrieve similar chunks from FAISS"""
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Search FAISS index
            distances, indices = self.faiss_index.search(
                query_embedding.astype('float32'), 
                top_k
            )
            
            # Retrieve chunks
            retrieved_chunks = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    retrieved_chunks.append({
                        'chunk_id': chunk['chunk_id'],
                        'card_name': chunk['card_name'],
                        'page_number': chunk['page_number'],
                        'chunk_text': chunk['chunk_text'],
                        'distance': float(distances[0][i])
                    })
            
            return retrieved_chunks
        
        except Exception as e:
            print(f"❌ Error in FAISS retrieval: {str(e)}")
            return []
    
    def retrieve_from_sqlite(self, card_name=None, spend_category=None):
        """Retrieve reward rules from SQLite"""
        
        try:
            query = "SELECT * FROM reward_rules WHERE 1=1"
            params = []
            
            if card_name:
                query += " AND card_name = ?"
                params.append(card_name)
            
            if spend_category:
                query += " AND spend_category = ?"
                params.append(spend_category)
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            # Get column names
            col_names = [desc[0] for desc in self.cursor.description]
            
            # Convert to list of dicts
            rules = []
            for row in results:
                rule_dict = dict(zip(col_names, row))
                rules.append(rule_dict)
            
            return rules
        
        except Exception as e:
            print(f"❌ Error in SQLite retrieval: {str(e)}")
            return []
    
    def hybrid_retrieve(self, query, card_name=None, top_k=5):
        """Hybrid retrieval: FAISS chunks + SQLite rules"""
        
        print(f"🔍 Query: {query}")
        print(f"   Card: {card_name if card_name else 'All cards'}\n")
        
        # Step 1: Retrieve context chunks from FAISS
        print("1️⃣ Retrieving context chunks from FAISS...")
        chunks = self.retrieve_from_faiss(query, top_k=top_k)
        print(f"   ✓ Retrieved {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"      [{i}] {chunk['card_name']}: {chunk['chunk_text'][:60]}...")
        
        # Step 2: Extract card names from chunks if not provided
        if not card_name:
            card_names = list(set([c['card_name'] for c in chunks]))
        else:
            card_names = [card_name]
        
        # Step 3: Retrieve structured rules from SQLite (with normalized names)
        print(f"\n2️⃣ Retrieving reward rules from SQLite...")
        all_rules = []
        normalized_card_names = []
        for card in card_names:
            normalized_name = self.normalize_card_name(card)
            normalized_card_names.append(normalized_name)
            rules = self.retrieve_from_sqlite(card_name=normalized_name)
            all_rules.extend(rules)
            print(f"   ✓ {card} ({normalized_name}): {len(rules)} rules found")
        
        return {
            'query': query,
            'context_chunks': chunks,
            'reward_rules': all_rules,
            'cards_involved': normalized_card_names
        }
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("LOCAL RAG RETRIEVER TEST (OFFLINE)")
    print("=" * 60)
    print()
    
    try:
        # Initialize retriever
        retriever = LocalRAGRetriever()
        
        # Test queries
        test_queries = [
            "Flight rewards on Axis Atlas",
            "Hotel transfer partners",
            "Annual fee conditions"
        ]
        
        for query in test_queries:
            print("\n" + "=" * 60)
            result = retriever.hybrid_retrieve(query, top_k=3)
            
            print(f"\n📊 Results Summary:")
            print(f"   Context chunks: {len(result['context_chunks'])}")
            print(f"   Reward rules: {len(result['reward_rules'])}")
            print(f"   Cards involved: {result['cards_involved']}")
            print("=" * 60)
        
        retriever.close()
        print("\n✅ Test complete!")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()