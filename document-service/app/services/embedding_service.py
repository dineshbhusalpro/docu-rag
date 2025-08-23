from typing import List
import asyncio
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.local_model = None
        self.inference_client = None
        self.use_api = settings.USE_HUGGINGFACE_API and settings.HUGGINGFACE_API_KEY
        
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

    def _get_inference_client(self):
        """Lazy load HuggingFace inference client"""
        if self.inference_client is None:
            try:
                from huggingface_hub import InferenceClient
                self.inference_client = InferenceClient(
                    model=settings.EMBEDDING_MODEL,
                    token=settings.HUGGINGFACE_API_KEY
                )
                print(f"Initialized HuggingFace InferenceClient for: {settings.EMBEDDING_MODEL}")
            except Exception as e:
                print(f"Failed to initialize inference client: {e}")
                raise Exception(f"HuggingFace InferenceClient failed to initialize: {str(e)}")
        return self.inference_client

    async def _get_huggingface_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using HuggingFace InferenceClient"""
        if not settings.HUGGINGFACE_API_KEY:
            raise Exception("HuggingFace API key not provided")
        
        try:
            client = self._get_inference_client()
            all_embeddings = []
            
            # Process texts individually for better reliability
            for text in texts:
                try:
                    # Use the feature extraction endpoint
                    embedding = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: client.feature_extraction(text)
                    )
                    
                    # Handle different response formats
                    if isinstance(embedding, list):
                        if len(embedding) > 0:
                            # If it's a 2D array (batch), take the first
                            if isinstance(embedding[0], list):
                                all_embeddings.append(embedding[0])
                            # If it's already a 1D array
                            elif isinstance(embedding[0], (int, float)):
                                all_embeddings.append(embedding)
                            else:
                                raise Exception(f"Unexpected embedding format: {type(embedding[0])}")
                        else:
                            raise Exception("Empty embedding returned")
                    else:
                        raise Exception(f"Unexpected response type: {type(embedding)}")
                        
                except Exception as e:
                    if "Model is currently loading" in str(e) or "503" in str(e):
                        print(f"Model loading, waiting 10 seconds...")
                        await asyncio.sleep(10)
                        # Retry once
                        embedding = await asyncio.get_event_loop().run_in_executor(
                            None, 
                            lambda: client.feature_extraction(text)
                        )
                        if isinstance(embedding, list) and embedding:
                            all_embeddings.append(embedding[0] if isinstance(embedding[0], list) else embedding)
                        else:
                            raise Exception("Model still not ready after retry")
                    else:
                        raise Exception(f"HuggingFace API error for text '{text[:50]}...': {str(e)}")
            
            return all_embeddings
            
        except Exception as e:
            if "HuggingFace API error" in str(e):
                raise
            raise Exception(f"HuggingFace InferenceClient request failed: {str(e)}")

    def _get_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using local model"""
        try:
            model = self._get_local_model()
            embeddings = model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Local embedding generation failed: {str(e)}")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.get_embeddings([text])
        return embeddings[0] if embeddings else []

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings based on configuration"""
        if not texts:
            return []
        
        try:
            if self.use_api:
                print(f"Using HuggingFace InferenceClient for {len(texts)} texts")
                return await self._get_huggingface_embeddings(texts)
            else:
                print(f"Using local model for {len(texts)} texts")
                # Run local model in thread pool to avoid blocking
                return await asyncio.get_event_loop().run_in_executor(
                    None, self._get_local_embeddings, texts
                )
                
        except Exception as e:
            # Fallback strategy
            if self.use_api:
                print(f"HuggingFace InferenceClient failed: {e}, trying local model")
                try:
                    return await asyncio.get_event_loop().run_in_executor(
                        None, self._get_local_embeddings, texts
                    )
                except Exception as local_error:
                    raise Exception(f"Both API and local embedding failed. API: {str(e)}, Local: {str(local_error)}")
            else:
                print(f"Local model failed: {e}, trying HuggingFace InferenceClient")
                if settings.HUGGINGFACE_API_KEY:
                    try:
                        return await self._get_huggingface_embeddings(texts)
                    except Exception as api_error:
                        raise Exception(f"Both local and InferenceClient embedding failed. Local: {str(e)}, API: {str(api_error)}")
                else:
                    raise Exception(f"Local embedding failed and no API key provided: {str(e)}")

    async def get_embedding_info(self) -> dict:
        """Get information about the embedding service configuration"""
        info = {
            "primary_method": "HuggingFace InferenceClient" if self.use_api else "Local Model",
            "model": settings.EMBEDDING_MODEL,
            "embedding_dimension": settings.EMBEDDING_DIMENSION,
            "api_available": bool(settings.HUGGINGFACE_API_KEY),
            "local_model_loaded": self.local_model is not None,
            "inference_client_initialized": self.inference_client is not None,
            "fallback_enabled": True
        }
        
        # Test connectivity if using API
        if self.use_api:
            try:
                client = self._get_inference_client()
                # Quick test to see if the client is working
                test_result = await asyncio.get_event_loop().run_in_executor(
                    None, 
                    lambda: client.feature_extraction("test", model=settings.EMBEDDING_MODEL)
                )
                info["api_connectivity"] = "working"
                info["test_embedding_length"] = len(test_result[0]) if isinstance(test_result[0], list) else len(test_result)
            except Exception as e:
                info["api_connectivity"] = f"failed: {str(e)}"
        
        return info

    async def test_both_methods(self) -> dict:
        """Test both local and API methods for comparison"""
        test_text = "This is a test sentence for embedding comparison."
        results = {"test_text": test_text}
        
        # Test local method
        try:
            local_embedding = await asyncio.get_event_loop().run_in_executor(
                None, self._get_local_embeddings, [test_text]
            )
            results["local"] = {
                "status": "success",
                "embedding_length": len(local_embedding[0]),
                "sample": local_embedding[0][:5]
            }
        except Exception as e:
            results["local"] = {
                "status": "failed",
                "error": str(e)
            }
        
        # Test API method
        if settings.HUGGINGFACE_API_KEY:
            try:
                api_embedding = await self._get_huggingface_embeddings([test_text])
                results["api"] = {
                    "status": "success",
                    "embedding_length": len(api_embedding[0]),
                    "sample": api_embedding[0][:5]
                }
            except Exception as e:
                results["api"] = {
                    "status": "failed", 
                    "error": str(e)
                }
        else:
            results["api"] = {
                "status": "skipped",
                "reason": "No API key provided"
            }
        
        return results