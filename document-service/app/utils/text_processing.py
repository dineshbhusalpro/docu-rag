import PyPDF2
from typing import List, Dict, Any
import io
import re
import os

# Try to import and setup NLTK safely
try:
    import nltk
    # Download required NLTK data with error handling
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            print(f"Warning: Could not download NLTK data: {e}")
    NLTK_AVAILABLE = True
except ImportError:
    print("Warning: NLTK not available, falling back to basic sentence splitting")
    NLTK_AVAILABLE = False

# Try to import ML libraries safely
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.cluster import KMeans
    ML_AVAILABLE = True
except ImportError:
    print("Warning: ML libraries not available, semantic chunking disabled")
    ML_AVAILABLE = False

class TextProcessor:
    def __init__(self):
        self.sentence_model = None
    
    def _load_sentence_model(self):
        """Lazy load sentence transformer for semantic chunking"""
        if not ML_AVAILABLE:
            raise Exception("ML libraries not available for semantic chunking")
        
        if self.sentence_model is None:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Failed to load sentence model: {e}")
                raise
        return self.sentence_model

    async def extract_text(self, file_path: str) -> str:
        """Extract text from file"""
        try:
            if file_path.endswith('.pdf'):
                return await self._extract_from_pdf(file_path)
            elif file_path.endswith('.txt'):
                return await self._extract_from_txt(file_path)
            else:
                raise ValueError("Unsupported file type")
        except Exception as e:
            print(f"Text extraction error: {e}")
            raise

    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"PDF extraction error: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    async def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"Text file encoding error: {e}")
                raise Exception(f"Failed to read text file: {str(e)}")
        except Exception as e:
            print(f"Text extraction error: {e}")
            raise

    def create_chunks(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200, strategy: str = "fixed") -> List[Dict[str, Any]]:
        """Split text into chunks using different strategies"""
        try:
            if strategy == "fixed":
                return self._fixed_size_chunking(text, chunk_size, chunk_overlap)
            elif strategy == "sentence":
                if NLTK_AVAILABLE:
                    return self._sentence_based_chunking(text, chunk_size, chunk_overlap)
                else:
                    print("NLTK not available, falling back to fixed chunking")
                    return self._fixed_size_chunking(text, chunk_size, chunk_overlap)
            elif strategy == "semantic":
                if ML_AVAILABLE:
                    return self._semantic_chunking(text, chunk_size)
                else:
                    print("ML libraries not available, falling back to fixed chunking")
                    return self._fixed_size_chunking(text, chunk_size, chunk_overlap)
            elif strategy == "paragraph":
                return self._paragraph_based_chunking(text, chunk_size, chunk_overlap)
            elif strategy == "hybrid":
                if ML_AVAILABLE and NLTK_AVAILABLE:
                    return self._hybrid_chunking(text, chunk_size, chunk_overlap)
                else:
                    print("Advanced libraries not available, falling back to sentence chunking")
                    return self._sentence_based_chunking(text, chunk_size, chunk_overlap) if NLTK_AVAILABLE else self._fixed_size_chunking(text, chunk_size, chunk_overlap)
            else:
                raise ValueError(f"Unknown chunking strategy: {strategy}")
        except Exception as e:
            print(f"Chunking error with strategy {strategy}: {e}")
            # Always fall back to fixed chunking if anything fails
            return self._fixed_size_chunking(text, chunk_size, chunk_overlap)

    def _fixed_size_chunking(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
        """Fixed-size chunking with overlap"""
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                break_point = max(last_period, last_newline)
                
                if break_point > start:
                    end = break_point + 1
            
            chunk_content = text[start:end].strip()
            
            if chunk_content:
                chunks.append({
                    "content": chunk_content,
                    "start_char": start,
                    "end_char": end,
                    "chunk_index": chunk_index,
                    "strategy": "fixed",
                    "metadata": {
                        "chunk_size": chunk_size,
                        "overlap": chunk_overlap
                    }
                })
                chunk_index += 1
            
            start = max(start + chunk_size - chunk_overlap, end)
        
        return chunks

    def _sentence_based_chunking(self, text: str, target_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Sentence-aware chunking that respects sentence boundaries"""
        try:
            if NLTK_AVAILABLE:
                sentences = nltk.sent_tokenize(text)
            else:
                # Fallback: split by periods and exclamation marks
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() + '.' for s in sentences if s.strip()]
        except Exception as e:
            print(f"Sentence tokenization failed: {e}, using basic splitting")
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, sentence in enumerate(sentences):
            # If adding this sentence would exceed target size and we have content
            if len(current_chunk) + len(sentence) > target_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "content": current_chunk.strip(),
                    "start_char": current_start,
                    "end_char": current_start + len(current_chunk),
                    "chunk_index": chunk_index,
                    "strategy": "sentence",
                    "metadata": {
                        "sentences_count": len([s for s in current_chunk.split('.') if s.strip()]),
                        "target_size": target_size
                    }
                })
                chunk_index += 1
                current_chunk = sentence
                current_start = text.find(sentence)
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                    current_start = text.find(sentence)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "start_char": current_start,
                "end_char": current_start + len(current_chunk),
                "chunk_index": chunk_index,
                "strategy": "sentence",
                "metadata": {
                    "sentences_count": len([s for s in current_chunk.split('.') if s.strip()]),
                    "target_size": target_size
                }
            })
        
        return chunks

    def _paragraph_based_chunking(self, text: str, target_size: int, overlap: int) -> List[Dict[str, Any]]:
        """Paragraph-aware chunking"""
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, paragraph in enumerate(paragraphs):
            # If adding this paragraph would exceed target size and we have content
            if len(current_chunk) + len(paragraph) > target_size and current_chunk:
                # Save current chunk
                chunks.append({
                    "content": current_chunk.strip(),
                    "start_char": current_start,
                    "end_char": current_start + len(current_chunk),
                    "chunk_index": chunk_index,
                    "strategy": "paragraph",
                    "metadata": {
                        "paragraphs_count": len([p for p in current_chunk.split('\n\n') if p.strip()]),
                        "target_size": target_size
                    }
                })
                chunk_index += 1
                current_chunk = paragraph
                current_start = text.find(paragraph)
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
                    current_start = text.find(paragraph)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                "content": current_chunk.strip(),
                "start_char": current_start,
                "end_char": current_start + len(current_chunk),
                "chunk_index": chunk_index,
                "strategy": "paragraph",
                "metadata": {
                    "paragraphs_count": len([p for p in current_chunk.split('\n\n') if p.strip()]),
                    "target_size": target_size
                }
            })
        
        return chunks

    def _semantic_chunking(self, text: str, max_chunks: int = 20) -> List[Dict[str, Any]]:
        """Semantic chunking using sentence embeddings and clustering"""
        try:
            # Split into sentences
            if NLTK_AVAILABLE:
                sentences = nltk.sent_tokenize(text)
            else:
                sentences = re.split(r'[.!?]+', text)
                sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 2:
                return self._fixed_size_chunking(text, 1000, 200)
            
            # Get sentence embeddings
            model = self._load_sentence_model()
            embeddings = model.encode(sentences)
            
            # Determine optimal number of clusters
            n_clusters = min(max_chunks, max(2, len(sentences) // 5))
            
            # Cluster sentences
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Group sentences by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append((i, sentences[i]))
            
            chunks = []
            chunk_index = 0
            
            for cluster_id, sentence_pairs in clusters.items():
                # Sort by original sentence order
                sentence_pairs.sort(key=lambda x: x[0])
                cluster_sentences = [pair[1] for pair in sentence_pairs]
                cluster_text = " ".join(cluster_sentences)
                
                if cluster_text.strip():
                    # Find start and end positions
                    first_sentence = sentence_pairs[0][1]
                    last_sentence = sentence_pairs[-1][1]
                    
                    start_pos = text.find(first_sentence)
                    end_pos = text.find(last_sentence) + len(last_sentence)
                    
                    chunks.append({
                        "content": cluster_text.strip(),
                        "start_char": max(0, start_pos),
                        "end_char": min(len(text), end_pos),
                        "chunk_index": chunk_index,
                        "strategy": "semantic",
                        "metadata": {
                            "cluster_id": cluster_id,
                            "sentences_count": len(cluster_sentences),
                            "semantic_coherence": float(np.mean([
                                np.dot(embeddings[pair[0]], kmeans.cluster_centers_[cluster_id]) 
                                for pair in sentence_pairs
                            ]))
                        }
                    })
                    chunk_index += 1
            
            # Sort chunks by start position to maintain order
            chunks.sort(key=lambda x: x["start_char"])
            
            # Reindex chunks
            for i, chunk in enumerate(chunks):
                chunk["chunk_index"] = i
            
            return chunks
            
        except Exception as e:
            print(f"Semantic chunking failed: {e}, falling back to sentence-based")
            return self._sentence_based_chunking(text, 1000, 200)

    def _hybrid_chunking(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Dict[str, Any]]:
        """Hybrid approach combining multiple strategies"""
        try:
            # Start with semantic chunking for coherent topics
            semantic_chunks = self._semantic_chunking(text, max_chunks=10)
            
            chunks = []
            
            # Process each semantic chunk
            for sem_chunk in semantic_chunks:
                if len(sem_chunk["content"]) > chunk_size * 1.5:
                    # Split large semantic chunks using sentence-based chunking
                    sub_chunks = self._sentence_based_chunking(
                        sem_chunk["content"], 
                        chunk_size, 
                        chunk_overlap
                    )
                    
                    # Adjust positions and add hybrid metadata
                    for sub_chunk in sub_chunks:
                        sub_chunk["start_char"] += sem_chunk["start_char"]
                        sub_chunk["end_char"] += sem_chunk["start_char"]
                        sub_chunk["strategy"] = "hybrid"
                        sub_chunk["metadata"]["parent_semantic_cluster"] = sem_chunk["metadata"].get("cluster_id")
                        chunks.append(sub_chunk)
                else:
                    # Keep semantic chunk as is
                    sem_chunk["strategy"] = "hybrid"
                    sem_chunk["metadata"]["chunking_method"] = "semantic_preserved"
                    chunks.append(sem_chunk)
                    
        except Exception as e:
            print(f"Hybrid chunking fell back to sentence-based: {e}")
            chunks = self._sentence_based_chunking(text, chunk_size, chunk_overlap)
            for chunk in chunks:
                chunk["strategy"] = "hybrid_fallback"
        
        # Reindex all chunks
        for i, chunk in enumerate(chunks):
            chunk["chunk_index"] = i
            
        return chunks