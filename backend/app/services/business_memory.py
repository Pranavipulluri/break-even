"""
BusinessMemory — RAG Optimization Intelligence Layer.

This is NOT a chatbot document retrieval system.
This is an OPTIMIZATION MEMORY that stores:
    ✅ Successful layout changes
    ✅ Failed patches
    ✅ Campaign outcomes
    ✅ Conversion deltas
    ✅ Customer engagement patterns
    ✅ Industry-specific optimization results

Uses Gemini embeddings when online, with a fast local numpy cosine-similarity
fallback for offline development environments.
"""

import os
import logging
from datetime import datetime, timezone
import numpy as np
from app import mongo
import google.generativeai as genai
from flask import current_app

logger = logging.getLogger(__name__)

VECTOR_DIM = 768


class BusinessMemory:

    # ================================================================
    # Embedding generation
    # ================================================================

    @classmethod
    def _get_embedding(cls, text):
        """
        Generates a 768-dim vector embedding using Gemini's embedding model.
        Falls back to a local numpy token-frequency pseudo-vector when offline.
        """
        api_key = current_app.config.get("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                response = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document",
                )
                if "embedding" in response:
                    return response["embedding"]
            except Exception as e:
                logger.warning(f"Gemini embedding failed: {e}. Using local cosine fallback.")

        # Local fallback: simple token-frequency vector
        vec = np.zeros(VECTOR_DIM)
        words = str(text).lower().split()
        if not words:
            return vec.tolist()

        for word in words:
            idx = hash(word) % VECTOR_DIM
            vec[idx] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return vec.tolist()

    # ================================================================
    # Store optimization memory
    # ================================================================

    @classmethod
    def add_memory(
        cls,
        business_id,
        patch_name,
        reason,
        layout_used,
        metrics_before,
        metrics_after,
        conversion_gain,
        agent_name="BusinessCopilot",
        patch_outcome="success",
    ):
        """
        Stores an optimization event into the RAG memory database.

        Example memory: "Moving booking CTA above fold improved salon conversion by 18%"
        """
        try:
            b_id_str = str(business_id)

            memory_context = (
                f"Business ID: {b_id_str}. "
                f"Applied Patch: {patch_name}. "
                f"Reason: {reason}. "
                f"Layout configuration: {layout_used}. "
                f"Impact: Conversion went from {metrics_before}% to {metrics_after}%. "
                f"Delta gain: {conversion_gain}%. "
                f"Agent: {agent_name}. Outcome: {patch_outcome}."
            )

            vector = cls._get_embedding(memory_context)

            memory_doc = {
                "business_id": b_id_str,
                "patch_name": patch_name,
                "reason": reason,
                "layout_used": layout_used,
                "metrics_before": float(metrics_before),
                "metrics_after": float(metrics_after),
                "conversion_gain": float(conversion_gain),
                "agent_name": agent_name,
                "patch_outcome": patch_outcome,
                "vector": vector,
                "memory_context": memory_context,
                "created_at": datetime.now(timezone.utc),
            }

            mongo.db.business_memory.insert_one(memory_doc)
            logger.info(f"✅ Stored optimization memory for '{b_id_str}': {patch_name} ({patch_outcome})")
            return True
        except Exception as e:
            logger.error(f"Error adding RAG business memory: {e}")
            return False

    # ================================================================
    # Retrieve relevant memories via cosine similarity
    # ================================================================

    @classmethod
    def retrieve_relevant_memory(cls, business_id, query_phrase, limit=3):
        """
        Queries RAG memory for previous high-performing layouts and patches.
        Uses local numpy cosine similarity by default, integrates Atlas Vector Search
        when available.
        """
        try:
            b_id_str = str(business_id)
            query_vector = np.array(cls._get_embedding(query_phrase))

            # Fetch memories for this business, then global benchmarks
            cursor = mongo.db.business_memory.find({"business_id": b_id_str})
            memories = list(cursor)

            if not memories:
                cursor = mongo.db.business_memory.find()
                memories = list(cursor)

            if not memories:
                return []

            scored_memories = []
            qv_norm = np.linalg.norm(query_vector)

            for mem in memories:
                v = mem.get("vector")
                if not v or len(v) != VECTOR_DIM:
                    continue

                mv = np.array(v)
                mv_norm = np.linalg.norm(mv)

                # Cosine Similarity = dot(q, m) / (||q|| * ||m||)
                if qv_norm > 0 and mv_norm > 0:
                    similarity = float(np.dot(query_vector, mv) / (qv_norm * mv_norm))
                else:
                    similarity = 0.0

                scored_memories.append((similarity, mem))

            # Sort descending by similarity
            scored_memories.sort(key=lambda x: x[0], reverse=True)

            results = []
            for score, mem in scored_memories[:limit]:
                mem.pop("vector", None)
                mem.pop("_id", None)
                mem["similarity_score"] = round(score, 4)
                results.append(mem)

            logger.info(f"RAG search returned {len(results)} memories for query '{query_phrase[:60]}...'")
            return results
        except Exception as e:
            logger.error(f"Error searching RAG business memory: {e}")
            return []

    # ================================================================
    # Utility: Store a failed patch as negative memory
    # ================================================================

    @classmethod
    def add_failure_memory(cls, business_id, patch_name, reason, error_detail):
        """
        Records a failed patch attempt so the AI avoids repeating it.
        """
        return cls.add_memory(
            business_id=business_id,
            patch_name=patch_name,
            reason=reason,
            layout_used="N/A — patch failed before application",
            metrics_before=0,
            metrics_after=0,
            conversion_gain=0,
            agent_name="BusinessCopilot",
            patch_outcome=f"FAILED: {error_detail}",
        )
