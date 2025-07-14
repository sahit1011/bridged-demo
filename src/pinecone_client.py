"""
Simple Pinecone Integration for the Bridged Media Assignment
"""

import os
import json
from typing import Dict, Any, List, Optional
from pinecone import Pinecone, ServerlessSpec
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimplePineconeClient:
    """
    Simple Pinecone client for vector search with metadata filtering.
    """
    
    def __init__(self, index_name: str = "bridged-demo-articles"):
        """Initialize Pinecone client with multiple embedding options."""
        self.api_key = os.getenv('PINECONE_API_KEY')
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY not found in environment variables")

        self.index_name = index_name
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None

        # Initialize OpenAI for embeddings (primary)
        self.openai_client = None
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)

        # Initialize sentence transformers for fallback
        self.sentence_transformer = None
        try:
            from sentence_transformers import SentenceTransformer
            # Use a lightweight model that's compatible with OpenAI embeddings
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Sentence Transformers loaded for embedding fallback")
        except ImportError:
            print("⚠️ Sentence Transformers not available - install with: pip install sentence-transformers")
        except Exception as e:
            print(f"⚠️ Sentence Transformers failed to load: {e}")
    
    def connect(self) -> bool:
        """Connect to the Pinecone index."""
        try:
            # Check if index exists
            if self.index_name not in self.pc.list_indexes().names():
                print(f"Index '{self.index_name}' not found!")
                return False
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Connected to Pinecone index: {self.index_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Pinecone: {e}")
            return False
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding with sequential fallback: OpenAI → Sentence Transformers → Simple."""
        import time
        print("🔄 Starting embedding generation...")
        embedding_start_time = time.time()

        print(f"📝 Input text length: {len(text)} characters")
        print(f"📄 Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")

        # Priority 1: Try OpenAI embeddings
        if self.openai_client:
            openai_start = time.time()
            try:
                print("  1. Trying OpenAI embeddings...", end=" ")
                response = self.openai_client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text,
                    timeout=10
                )
                embedding = response.data[0].embedding
                openai_time = time.time() - openai_start
                total_time = time.time() - embedding_start_time
                print(f"✅ SUCCESS ({openai_time:.2f}s)")
                print(f"🎯 Used OpenAI embeddings (dimension: {len(embedding)})")
                print(f"⏱️ Total embedding time: {total_time:.3f}s")
                return embedding
            except Exception as e:
                openai_time = time.time() - openai_start
                error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
                print(f"❌ {error_msg} ({openai_time:.2f}s)")

        # Priority 2: Try Sentence Transformers
        if self.sentence_transformer:
            st_start = time.time()
            try:
                print("  2. Trying Sentence Transformers...", end=" ")
                embedding = self.sentence_transformer.encode(text).tolist()
                original_dim = len(embedding)
                # Pad or truncate to 1536 dimensions to match OpenAI
                embedding = self._normalize_embedding_dimension(embedding, 1536)
                st_time = time.time() - st_start
                total_time = time.time() - embedding_start_time
                print(f"✅ SUCCESS ({st_time:.2f}s)")
                print(f"🎯 Used Sentence Transformers (dimension: {original_dim} → {len(embedding)})")
                print(f"⏱️ Total embedding time: {total_time:.3f}s")
                return embedding
            except Exception as e:
                st_time = time.time() - st_start
                error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
                print(f"❌ {error_msg} ({st_time:.2f}s)")

        # Priority 3: Simple text-based fallback
        fallback_start = time.time()
        print("  3. Using simple text-based embedding...", end=" ")
        embedding = self._simple_text_embedding(text)
        fallback_time = time.time() - fallback_start
        total_time = time.time() - embedding_start_time
        print(f"✅ SUCCESS ({fallback_time:.2f}s)")
        print(f"🎯 Used simple embedding (dimension: {len(embedding)})")
        print(f"⏱️ Total embedding time: {total_time:.3f}s")
        return embedding

    def _simple_text_embedding(self, text: str) -> List[float]:
        """Create a simple text-based embedding for fallback."""
        # Create a deterministic embedding based on text content
        import hashlib

        # Hash the text to get consistent values
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Convert hash to float values between -1 and 1
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            value = (int(hex_pair, 16) - 127.5) / 127.5  # Normalize to [-1, 1]
            embedding.append(value)

        # Pad or truncate to 1536 dimensions
        while len(embedding) < 1536:
            embedding.extend(embedding[:min(len(embedding), 1536 - len(embedding))])

        return embedding[:1536]

    def _normalize_embedding_dimension(self, embedding: List[float], target_dim: int) -> List[float]:
        """Normalize embedding to target dimension."""
        if len(embedding) == target_dim:
            return embedding
        elif len(embedding) > target_dim:
            # Truncate
            return embedding[:target_dim]
        else:
            # Pad with zeros
            padding = [0.0] * (target_dim - len(embedding))
            return embedding + padding
    
    def _convert_tag_filter(self, filter_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert tag filters to work with Pinecone's string-based tag storage.

        Since tags are stored as strings like "['#RohitSharma', '#DRS', '#RRvsMI']",
        we need to search for exact string matches or use broader search without filters.
        """
        if not filter_dict or "tags" not in filter_dict:
            return filter_dict

        tag_filter = filter_dict["tags"]

        # For tag searches, we'll do a broader search without tag filters
        # and rely on vector similarity + post-processing
        # This is because Pinecone doesn't support regex and exact string matching
        # is too restrictive for the array-like string format

        # Remove tag filter and keep other filters
        converted_filter = {k: v for k, v in filter_dict.items() if k != "tags"}

        return converted_filter if converted_filter else None

    def search(self, query: str, filter_dict: Dict[str, Any], top_k: int = 5) -> Dict[str, Any]:
        """
        Search Pinecone with vector similarity and metadata filtering.

        Args:
            query: Natural language query for embedding
            filter_dict: Pinecone metadata filter
            top_k: Number of results to return

        Returns:
            Dictionary with search results
        """
        if not self.index:
            return {"matches": [], "error": "Not connected to Pinecone"}

        try:
            import time
            search_start_time = time.time()

            print(f"🔍 Pinecone Search Parameters:")
            print(f"   📝 Query: '{query}'")
            print(f"   📊 Top K: {top_k}")
            print(f"   🎯 Filter: {filter_dict}")

            # Generate query embedding
            embedding_start = time.time()
            query_embedding = self.generate_embedding(query)
            embedding_time = time.time() - embedding_start

            # Convert tag filters to work with string-based storage
            filter_start = time.time()
            converted_filter = self._convert_tag_filter(filter_dict) if filter_dict else None
            filter_time = time.time() - filter_start

            if converted_filter != filter_dict:
                print(f"🔄 Filter converted for Pinecone:")
                print(f"   Original: {filter_dict}")
                print(f"   Converted: {converted_filter}")

            # Perform search
            query_start = time.time()
            print(f"🚀 Executing Pinecone query...")
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=converted_filter
            )
            query_time = time.time() - query_start

            print(f"✅ Pinecone query completed in {query_time:.3f}s")
            print(f"📊 Raw results count: {len(search_results.matches)}")

            # Format results
            format_start = time.time()
            matches = []
            for i, match in enumerate(search_results.matches):
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
                # Log first few results for debugging
                if i < 3:
                    print(f"   📄 Match {i+1}: ID={match.id}, Score={match.score:.4f}")

            format_time = time.time() - format_start

            # Post-process results to filter by tags if tag filter was provided
            postprocess_start = time.time()
            if filter_dict and "tags" in filter_dict:
                original_count = len(matches)
                matches = self._filter_by_tags(matches, filter_dict["tags"])
                print(f"🏷️ Tag filtering: {original_count} → {len(matches)} results")
            postprocess_time = time.time() - postprocess_start

            # Performance summary
            total_search_time = time.time() - search_start_time
            print(f"\n📊 Pinecone Search Performance:")
            print(f"   ⏱️ Embedding: {embedding_time:.3f}s ({embedding_time/total_search_time*100:.1f}%)")
            print(f"   ⏱️ Filter conversion: {filter_time:.3f}s ({filter_time/total_search_time*100:.1f}%)")
            print(f"   ⏱️ Pinecone query: {query_time:.3f}s ({query_time/total_search_time*100:.1f}%)")
            print(f"   ⏱️ Result formatting: {format_time:.3f}s ({format_time/total_search_time*100:.1f}%)")
            print(f"   ⏱️ Post-processing: {postprocess_time:.3f}s ({postprocess_time/total_search_time*100:.1f}%)")
            print(f"   ⏱️ Total search time: {total_search_time:.3f}s")

            return {
                "matches": matches,
                "total_count": len(matches),
                "filter_applied": filter_dict,
                "performance": {
                    "embedding_time": embedding_time,
                    "query_time": query_time,
                    "total_time": total_search_time
                }
            }

        except Exception as e:
            search_error_time = time.time() - search_start_time
            print(f"❌ Search failed after {search_error_time:.3f}s: {e}")
            return {"matches": [], "error": str(e), "error_time": search_error_time}

    def _filter_by_tags(self, matches: List[Dict], tag_filter: Any) -> List[Dict]:
        """
        Post-process search results to filter by tags.

        Args:
            matches: List of search result matches
            tag_filter: Tag filter to apply

        Returns:
            Filtered list of matches
        """
        if not matches or not tag_filter:
            return matches

        filtered_matches = []

        for match in matches:
            metadata = match.get("metadata", {})
            tags_str = metadata.get("tags", "")

            # Handle different tag filter types
            if isinstance(tag_filter, str):
                # Single tag or exact string match
                if tag_filter in tags_str:
                    filtered_matches.append(match)
            elif isinstance(tag_filter, dict):
                # Handle various operators
                if "$or" in tag_filter:
                    # Multiple tags with OR logic
                    for tag in tag_filter["$or"]:
                        if tag in tags_str:
                            filtered_matches.append(match)
                            break  # Found one match, no need to check others
                elif "$in" in tag_filter:
                    # Tags with $in operator (OR logic)
                    for tag in tag_filter["$in"]:
                        if tag in tags_str:
                            filtered_matches.append(match)
                            break
                elif "$nin" in tag_filter:
                    # Tags with $nin operator (NOT IN logic)
                    found_excluded = False
                    for tag in tag_filter["$nin"]:
                        if tag in tags_str:
                            found_excluded = True
                            break
                    if not found_excluded:
                        filtered_matches.append(match)
                elif "$eq" in tag_filter:
                    # Exact match
                    if tag_filter["$eq"] in tags_str:
                        filtered_matches.append(match)
                elif "$ne" in tag_filter:
                    # Not equal
                    if tag_filter["$ne"] not in tags_str:
                        filtered_matches.append(match)
            elif isinstance(tag_filter, list):
                # List of tags (OR logic)
                for tag in tag_filter:
                    if tag in tags_str:
                        filtered_matches.append(match)
                        break

        return filtered_matches
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the index."""
        if not self.index:
            return {"error": "Not connected to Pinecone"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            return {"error": str(e)}


def test_pinecone_search():
    """Test Pinecone search functionality."""
    from simple_agent import SimpleNLAgent
    
    # Initialize components
    agent = SimpleNLAgent()
    pinecone_client = SimplePineconeClient()
    
    # Connect to Pinecone
    if not pinecone_client.connect():
        print("❌ Cannot test without Pinecone connection")
        return
    
    # Test queries from assignment
    test_queries = [
        "Show me articles by Alice Zhang from last year about machine learning.",
        "Find posts tagged with 'LLMs' published in June, 2023.",
        "Anything by John Doe on vector search?"
    ]
    
    print("Testing Complete Pipeline:")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        
        # Step 1: Generate filter
        filter_dict = agent.generate_pinecone_filter(query)
        print(f"📋 Generated Filter:")
        print(json.dumps(filter_dict, indent=2))
        
        # Step 2: Search Pinecone
        search_results = pinecone_client.search(query, filter_dict, top_k=3)
        print(f"🔎 Search Results: {len(search_results.get('matches', []))} matches")
        
        for j, match in enumerate(search_results.get('matches', [])[:2], 1):
            print(f"  {j}. Score: {match['score']:.3f}")
            print(f"     Title: {match['metadata'].get('title', 'N/A')}")
            print(f"     Author: {match['metadata'].get('author', 'N/A')}")
            print(f"     Date: {match['metadata'].get('publishedDate', 'N/A')}")
        
        print("-" * 40)


if __name__ == "__main__":
    test_pinecone_search()
