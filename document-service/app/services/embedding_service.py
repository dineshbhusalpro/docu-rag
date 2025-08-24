import requests
from typing import List
import asyncio
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.local_model = None
        
    def _get_local_model(self):
        """Lazy load local embedding model"""
        if self.local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer(settings.EMBEDDING_MODEL)
                print(f"Loaded local model: {settings.EMBEDDING_MODEL}")
            except Exception as e:
                print(f"Failed to load local model: {e}")
                raise Exception(f"Local embedding model failed to load: {str(e)}")
        return self.local_model
    
    def _get_hf_headers(self):
        """Prepare HuggingFace API headers"""
        if not settings.HUGGINGFACE_API_KEY:
            raise Exception("HuggingFace API key not provided")
        return {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    async def _get_huggingface_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using HuggingFace Inference API (via requests)"""
        url = settings.API_EMBEDDING_MODEL_URL.format(model=settings.EMBEDDING_MODEL)
        headers = self._get_hf_headers()

        embeddings = []
        for text in texts:
            try:
                response = requests.post(url, headers=headers, json={"inputs": text})
                
                if response.status_code == 503:
                    # Model still loading on server, retry after wait
                    print("Model is loading, waiting 20 seconds...")
                    await asyncio.sleep(20)
                    response = requests.post(url, headers=headers, json={"inputs": text})

                response.raise_for_status()
                data = response.json()

                # Handle token-level embeddings (list of lists)
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], list):
                        import numpy as np
                        embedding = np.mean(data, axis=0).tolist()
                    else:
                        embedding = data
                    embeddings.append(embedding)
                else:
                    raise Exception(f"Unexpected embedding format: {type(data)}")

            except Exception as e:
                raise Exception(
                    f"HuggingFace API error for text '{text[:50]}...': {str(e)}"
                )

        return embeddings

    # def _get_hf_client(self):
    #     """Lazy load HuggingFace Inference client"""
    #     if self.hf_client is None:
    #         try:
    #             from huggingface_hub import InferenceClient
    #             self.hf_client = InferenceClient(token=settings.HUGGINGFACE_API_KEY)
    #             print("Initialized HuggingFace Inference client")
    #         except Exception as e:
    #             print(f"Failed to initialize HF client: {e}")
    #             raise Exception(f"HuggingFace client initialization failed: {str(e)}")
    #     return self.hf_client

    # async def _get_huggingface_embeddings(self, texts: List[str]) -> List[List[float]]:
    #     """Generate embeddings using HuggingFace Inference API"""
    #     if not settings.HUGGINGFACE_API_KEY:
    #         raise Exception("HuggingFace API key not provided")
        
    #     try:
    #         client = self._get_hf_client()
            
    #         # Process embeddings
    #         embeddings = []
    #         for text in texts:
    #             try:
    #                 # Use feature extraction for embeddings
    #                 embedding = client.feature_extraction(
    #                     text=text,
    #                     model=settings.EMBEDDING_MODEL
    #                 )
                    
    #                 # Handle different response formats
    #                 if isinstance(embedding, list):
    #                     if len(embedding) > 0 and isinstance(embedding[0], list):
    #                         # Token-level embeddings, take mean
    #                         import numpy as np
    #                         embedding = np.mean(embedding, axis=0).tolist()
    #                     embeddings.append(embedding)
    #                 else:
    #                     raise Exception(f"Unexpected embedding format: {type(embedding)}")
                        
    #             except Exception as e:
    #                 if "loading" in str(e).lower():
    #                     # Model is loading, wait and retry
    #                     print(f"Model loading, waiting 20 seconds...")
    #                     await asyncio.sleep(20)
    #                     embedding = client.feature_extraction(
    #                         text=text,
    #                         model=settings.EMBEDDING_MODEL
    #                     )
    #                     if isinstance(embedding, list) and len(embedding) > 0:
    #                         if isinstance(embedding[0], list):
    #                             import numpy as np
    #                             embedding = np.mean(embedding, axis=0).tolist()
    #                         embeddings.append(embedding)
    #                     else:
    #                         raise Exception("Model still not ready after retry")
    #                 else:
    #                     raise Exception(f"HuggingFace API error for text '{text[:50]}...': {str(e)}")
            
    #         return embeddings
                
    #     except Exception as e:
    #         if "HuggingFace" in str(e):
    #             raise
    #         raise Exception(f"HuggingFace API request failed: {str(e)}")

    def _get_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        try:
            model = self._get_local_model()
            embeddings = model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Local embedding generation failed: {str(e)}")

    async def get_embedding(self, text: str, embedding_provider: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.get_embeddings([text], embedding_provider)
        return embeddings[0] if embeddings else []

    async def get_embeddings(self, texts: List[str], embedding_provider: str) -> List[List[float]]:
        """Generate embeddings based on configuration"""
        print(f"🧠 Generating embeddings using {embedding_provider}")
        if not texts:
            print(f"No texts provided to generate embeddings")
            return []
        
        try:
            if embedding_provider == "huggingface_api":
                if not settings.HUGGINGFACE_API_KEY:
                    raise Exception(f"No API key provided for HuggingFace API usage. Try local model instead.")
                
                print(f"Using HuggingFace Inference API for {len(texts)} texts")
                return await self._get_huggingface_embeddings(texts)
            else:
                print(f"Using local model for {len(texts)} texts")
                # Run local model in thread pool to avoid blocking
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._get_local_embeddings, texts
                )
                
        except Exception as e:
            raise Exception(f"Embeddings Generation failed: {str(e)}")
