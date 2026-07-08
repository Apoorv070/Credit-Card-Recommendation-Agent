import os
import json
import pdfplumber
from config import RAW_PDFS_FOLDER, CHUNKS_FILE, KEYWORDS, CHUNK_SIZE, CHUNK_OVERLAP

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF with page numbers using pdfplumber"""
    pages_text = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    pages_text.append({
                        "page_num": page_num,
                        "text": text
                    })
    except Exception as e:
        print(f"  ⚠ Error extracting {pdf_path}: {str(e)}")
    
    return pages_text

def chunk_text(text, chunk_size=1000, overlap=200):
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks

def has_relevant_keywords(chunk):
    """Check if chunk contains relevant keywords"""
    chunk_lower = chunk.lower()
    return any(keyword in chunk_lower for keyword in KEYWORDS)

def process_pdfs():
    """Process all PDFs in raw_pdfs folder"""
    
    all_chunks = []
    chunk_id_counter = 1
    
    pdf_files = [f for f in os.listdir(RAW_PDFS_FOLDER) if f.endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF files\n")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(RAW_PDFS_FOLDER, pdf_file)
        card_name = pdf_file.replace('.pdf', '')
        
        print(f"Processing: {pdf_file}")
        
        # Extract text
        pages_text = extract_text_from_pdf(pdf_path)
        print(f"  ✓ Extracted {len(pages_text)} pages")
        
        # Process each page
        page_chunks_count = 0
        for page_data in pages_text:
            page_num = page_data['page_num']
            text = page_data['text']
            
            # Split into chunks
            chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
            
            # Filter by keywords
            for chunk in chunks:
                if has_relevant_keywords(chunk):
                    chunk_metadata = {
                        "chunk_id": f"{card_name}_chunk_{chunk_id_counter}",
                        "card_name": card_name,
                        "pdf_file": pdf_file,
                        "page_number": page_num,
                        "chunk_text": chunk.strip(),
                        "chunk_length": len(chunk),
                        "timestamp": "2024-01-01"
                    }
                    all_chunks.append(chunk_metadata)
                    chunk_id_counter += 1
                    page_chunks_count += 1
        
        print(f"  ✓ Extracted {page_chunks_count} relevant chunks")
        print()
    
    return all_chunks

def save_chunks_to_json(chunks):
    """Save chunks to JSON file"""
    with open(CHUNKS_FILE, 'w') as f:
        json.dump(chunks, f, indent=2)
    
    print(f"✓ Saved {len(chunks)} chunks to {CHUNKS_FILE}")

def verify_chunks():
    """Verify chunks were saved correctly"""
    with open(CHUNKS_FILE, 'r') as f:
        chunks = json.load(f)
    
    print(f"\n✓ Chunks verification:")
    print(f"  Total chunks: {len(chunks)}")
    
    # Group by card
    by_card = {}
    for chunk in chunks:
        card = chunk['card_name']
        by_card[card] = by_card.get(card, 0) + 1
    
    print(f"  Chunks per card:")
    for card, count in sorted(by_card.items()):
        print(f"    - {card}: {count} chunks")
    
    # Sample chunk
    if chunks:
        print(f"\n  Sample chunk:")
        sample = chunks[0]
        print(f"    ID: {sample['chunk_id']}")
        print(f"    Card: {sample['card_name']}")
        print(f"    Page: {sample['page_number']}")
        print(f"    Text preview: {sample['chunk_text'][:100]}...")

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 2: PDF Chunking with Keyword Filtering")
    print("=" * 60)
    print()
    
    # Process PDFs
    chunks = process_pdfs()
    
    # Save to JSON
    save_chunks_to_json(chunks)
    
    # Verify
    verify_chunks()
    
    print("\n" + "=" * 60)
    print("✓ PDF chunking complete!")
    print(f"Chunks file: {CHUNKS_FILE}")
    print("=" * 60)