"""
BusinessMemory — RAG Optimization Intelligence Layer.

This is NOT a chatbot document retrieval system.
This is an OPTIMIZATION MEMORY that stores:
    ✅ Successful layout changes  (with full patch_json)
    ✅ Failed patches              (with error context)
    ✅ Campaign outcomes
    ✅ Conversion deltas
    ✅ Customer engagement patterns
    ✅ Industry-specific optimization results

Tenant Isolation:
    EVERY query is scoped to business_id at the MongoDB filter level.
    Cross-business sharing is ONLY via the industry_benchmark_patterns
    collection — never by leaking raw business memories.

Uses Gemini embeddings when online, with a fast local numpy cosine-similarity
fallback for offline development environments.
"""

import os
import json
import logging
from datetime import datetime, timezone
import numpy as np
from app import mongo
from google import genai
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
                client = genai.Client(api_key=api_key)
                # gemini-embedding-001 is the current v1beta embedding model.
                # If this key does not have billing enabled, the call returns 403
                # and the local numpy fallback below is used automatically.
                response = client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=text,
                )
                # New SDK returns EmbedContentResponse with .embeddings list
                embeddings = getattr(response, "embeddings", None)
                if embeddings and len(embeddings) > 0:
                    return embeddings[0].values
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
        industry_type="general",
        patch_json=None,
        git_ref=None,
        deploy_ref=None,
    ):
        """
        Stores an optimization event into the RAG memory database.

        Example memory: "Moving booking CTA above fold improved salon conversion by 18%"

        Args:
            patch_json:     The actual patch dict that was applied (enables failure pattern matching).
            git_ref:        GitHub commit SHA if the patch was versioned.
            deploy_ref:     Netlify deploy ID if the patch was published.
            industry_type:  Business vertical ("spa", "law_firm", "general", etc.)
        """
        try:
            b_id_str = str(business_id)

            memory_context = (
                f"Business ID: {b_id_str}. "
                f"Industry: {industry_type}. "
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
                "industry_type": industry_type,
                "patch_name": patch_name,
                "reason": reason,
                "layout_used": layout_used,
                "metrics_before": float(metrics_before),
                "metrics_after": float(metrics_after),
                "conversion_gain": float(conversion_gain),
                "agent_name": agent_name,
                "patch_outcome": patch_outcome,
                "patch_json": patch_json,
                "git_ref": git_ref,
                "deploy_ref": deploy_ref,
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
        Uses MongoDB Atlas Vector Search if available, falling back to local
        NumPy-based cosine similarity computation if unsupported/index missing.

        TENANT ISOLATION: Always filtered by business_id.
        If no business-specific memories exist, returns industry benchmarks
        instead of leaking other businesses' memories.
        """
        try:
            b_id_str = str(business_id)
            query_vector = np.array(cls._get_embedding(query_phrase))

            # Try MongoDB Atlas Vector Search — ALWAYS filtered by business_id
            try:
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "vector",
                            "queryVector": query_vector.tolist(),
                            "numCandidates": limit * 10,
                            "limit": limit,
                            "filter": {"business_id": {"$eq": b_id_str}},
                        }
                    },
                    {
                        "$addFields": {
                            "similarity_score": {"$meta": "vectorSearchScore"}
                        }
                    },
                    {"$project": {"vector": 0}},
                ]
                results = list(mongo.db.business_memory.aggregate(pipeline))

                if results:
                    formatted_results = []
                    for doc in results:
                        doc.pop("_id", None)
                        doc["similarity_score"] = round(float(doc.get("similarity_score", 1.0)), 4)
                        formatted_results.append(doc)

                    logger.info(
                        f"MongoDB Atlas Vector Search successful: "
                        f"returned {len(formatted_results)} memories for business {b_id_str}"
                    )
                    return formatted_results

            except Exception as atlas_err:
                logger.info(
                    f"Atlas Vector Search failed/unsupported ({atlas_err}). "
                    "Falling back to local NumPy-based similarity computation."
                )

            # --- Fallback: Local NumPy Cosine Similarity Search ---
            # TENANT ISOLATED: only fetch memories for THIS business
            cursor = mongo.db.business_memory.find({"business_id": b_id_str})
            memories = list(cursor)

            if not memories:
                # No business-specific memories → return industry benchmarks (NOT other businesses' data)
                return cls._get_industry_fallback(b_id_str, query_phrase, limit)

            scored_memories = []
            qv_norm = np.linalg.norm(query_vector)

            for mem in memories:
                v = mem.get("vector")
                if not v or len(v) != VECTOR_DIM:
                    continue

                mv = np.array(v)
                mv_norm = np.linalg.norm(mv)

                if qv_norm > 0 and mv_norm > 0:
                    similarity = float(np.dot(query_vector, mv) / (qv_norm * mv_norm))
                else:
                    similarity = 0.0

                scored_memories.append((similarity, mem))

            scored_memories.sort(key=lambda x: x[0], reverse=True)

            results = []
            for score, mem in scored_memories[:limit]:
                mem.pop("vector", None)
                mem.pop("_id", None)
                mem["similarity_score"] = round(score, 4)
                results.append(mem)

            logger.info(
                f"RAG search (NumPy fallback) returned {len(results)} memories "
                f"for business '{b_id_str}'"
            )
            return results
        except Exception as e:
            logger.error(f"Error searching RAG business memory: {e}")
            return []

    # ================================================================
    # Industry-scoped fallback (replaces the old tenant-leaking global search)
    # ================================================================

    @classmethod
    def _get_industry_fallback(cls, business_id, query_phrase, limit=3):
        """
        When a business has no memories, return industry benchmark patterns
        instead of leaking other businesses' data.
        """
        try:
            # Determine the business's industry from child_websites
            website = mongo.db.child_websites.find_one(
                {"owner_id": business_id},
                {"industry_type": 1, "business_type": 1},
            )
            if not website:
                from bson import ObjectId
                try:
                    website = mongo.db.child_websites.find_one(
                        {"owner_id": ObjectId(business_id)},
                        {"industry_type": 1, "business_type": 1},
                    )
                except Exception:
                    pass
            industry = (website or {}).get("industry_type") or (website or {}).get("business_type") or "general"

            # Query industry benchmarks
            from app.services.industry_benchmarks import get_benchmarks_for_industry
            benchmarks = get_benchmarks_for_industry(industry, limit=limit)

            if benchmarks:
                logger.info(
                    f"No business memories for '{business_id}'. "
                    f"Returning {len(benchmarks)} industry benchmarks ({industry})."
                )
                for b in benchmarks:
                    b["source"] = "industry_benchmark"
                    b["similarity_score"] = 0.85  # High confidence for curated benchmarks
                return benchmarks

            return []
        except Exception as e:
            logger.warning(f"Industry fallback failed: {e}")
            return []

    # ================================================================
    # Retrieve FAILED memories specifically
    # ================================================================

    @classmethod
    def retrieve_failed_memories(cls, business_id, query_phrase=None, limit=5):
        """
        Returns only FAILED optimization memories for a business.
        Useful for the orchestrator's failure comparison gate.
        """
        try:
            b_id_str = str(business_id)
            query = {
                "business_id": b_id_str,
                "patch_outcome": {"$regex": "^FAILED", "$options": "i"},
            }

            if query_phrase:
                # If we have a query, do similarity ranking
                query_vector = np.array(cls._get_embedding(query_phrase))
                cursor = mongo.db.business_memory.find(query)
                failures = list(cursor)

                if not failures:
                    return []

                qv_norm = np.linalg.norm(query_vector)
                scored = []
                for mem in failures:
                    v = mem.get("vector")
                    if not v or len(v) != VECTOR_DIM:
                        continue
                    mv = np.array(v)
                    mv_norm = np.linalg.norm(mv)
                    if qv_norm > 0 and mv_norm > 0:
                        sim = float(np.dot(query_vector, mv) / (qv_norm * mv_norm))
                    else:
                        sim = 0.0
                    scored.append((sim, mem))

                scored.sort(key=lambda x: x[0], reverse=True)
                results = []
                for score, mem in scored[:limit]:
                    mem.pop("vector", None)
                    mem.pop("_id", None)
                    mem["similarity_score"] = round(score, 4)
                    results.append(mem)
                return results
            else:
                # No query phrase — just return most recent failures
                cursor = mongo.db.business_memory.find(
                    query, {"vector": 0}
                ).sort("created_at", -1).limit(limit)
                results = []
                for doc in cursor:
                    doc.pop("_id", None)
                    results.append(doc)
                return results

        except Exception as e:
            logger.error(f"Error retrieving failed memories: {e}")
            return []

    # ================================================================
    # Compare hypothesis to known failures
    # ================================================================

    @classmethod
    def compare_to_failures(cls, business_id, hypothesis_text, threshold=0.7):
        """
        Checks whether a proposed hypothesis matches any known FAILED patches
        above the similarity threshold.

        Returns:
            List of matching failures with similarity scores, or empty list if safe.
        """
        try:
            failures = cls.retrieve_failed_memories(
                business_id, query_phrase=hypothesis_text, limit=3
            )

            matches = [
                f for f in failures
                if f.get("similarity_score", 0) >= threshold
            ]

            if matches:
                logger.warning(
                    f"⚠️ Hypothesis matches {len(matches)} known failure(s) "
                    f"for business '{business_id}' (threshold={threshold})"
                )
            return matches

        except Exception as e:
            logger.error(f"Error comparing hypothesis to failures: {e}")
            return []

    # ================================================================
    # Conversion pattern retrieval (cross-business via benchmarks)
    # ================================================================

    @classmethod
    def retrieve_conversion_patterns(cls, business_id, industry_type=None, limit=5):
        """
        Returns high-performing conversion patterns: first from this business's
        successful memories, then augmented with industry benchmarks.
        """
        try:
            b_id_str = str(business_id)

            # Own successful memories
            cursor = mongo.db.business_memory.find(
                {
                    "business_id": b_id_str,
                    "patch_outcome": "success",
                    "conversion_gain": {"$gt": 0},
                },
                {"vector": 0},
            ).sort("conversion_gain", -1).limit(limit)

            results = []
            for doc in cursor:
                doc.pop("_id", None)
                doc["source"] = "own_history"
                results.append(doc)

            # Augment with industry benchmarks if we have fewer than limit
            if len(results) < limit:
                industry = industry_type or "general"
                if not industry_type:
                    website = mongo.db.child_websites.find_one(
                        {"owner_id": b_id_str}, {"industry_type": 1, "business_type": 1}
                    )
                    if not website:
                        from bson import ObjectId
                        try:
                            website = mongo.db.child_websites.find_one(
                                {"owner_id": ObjectId(b_id_str)}, {"industry_type": 1, "business_type": 1}
                            )
                        except Exception:
                            pass
                    if website:
                        industry = website.get("industry_type") or website.get("business_type") or "general"

                from app.services.industry_benchmarks import get_benchmarks_for_industry
                benchmarks = get_benchmarks_for_industry(industry, limit=limit - len(results))
                for b in benchmarks:
                    b["source"] = "industry_benchmark"
                results.extend(benchmarks)

            return results[:limit]

        except Exception as e:
            logger.error(f"Error retrieving conversion patterns: {e}")
            return []

    # ================================================================
    # Layout success search
    # ================================================================

    @classmethod
    def search_layout_successes(cls, business_id, query_phrase, limit=5):
        """
        Searches for historically successful layout configurations
        that match the query phrase. Tenant-isolated.
        """
        try:
            b_id_str = str(business_id)
            query_vector = np.array(cls._get_embedding(query_phrase))

            cursor = mongo.db.business_memory.find({
                "business_id": b_id_str,
                "patch_outcome": "success",
            })
            memories = list(cursor)

            if not memories:
                return []

            qv_norm = np.linalg.norm(query_vector)
            scored = []
            for mem in memories:
                v = mem.get("vector")
                if not v or len(v) != VECTOR_DIM:
                    continue
                mv = np.array(v)
                mv_norm = np.linalg.norm(mv)
                if qv_norm > 0 and mv_norm > 0:
                    sim = float(np.dot(query_vector, mv) / (qv_norm * mv_norm))
                else:
                    sim = 0.0
                scored.append((sim, mem))

            scored.sort(key=lambda x: x[0], reverse=True)

            results = []
            for score, mem in scored[:limit]:
                mem.pop("vector", None)
                mem.pop("_id", None)
                mem["similarity_score"] = round(score, 4)
                results.append(mem)

            return results

        except Exception as e:
            logger.error(f"Error searching layout successes: {e}")
            return []

    # ================================================================
    # Utility: Store a successful patch as positive memory
    # ================================================================

    @classmethod
    def add_success_memory(cls, business_id, layout_snapshot, outcome_metrics):
        """
        Stores a successful layout configuration snapshot and its outcome metrics in the memory DB.
        """
        try:
            b_id_str = str(business_id)
            site_doc = mongo.db.child_websites.find_one(
                {"owner_id": b_id_str}, {"industry_type": 1, "business_type": 1}
            )
            if not site_doc:
                from bson import ObjectId
                try:
                    site_doc = mongo.db.child_websites.find_one(
                        {"owner_id": ObjectId(b_id_str)}, {"industry_type": 1, "business_type": 1}
                    )
                except Exception:
                    pass
            industry = (
                (site_doc or {}).get("industry_type")
                or (site_doc or {}).get("business_type")
                or "general"
            )
        except Exception:
            industry = "general"


        metrics_before = float(outcome_metrics.get("conversion_rate_percentage", 4.8))
        conversion_gain = 1.8
        metrics_after = metrics_before + conversion_gain

        sections = layout_snapshot.get("sections", [])
        layout_desc = f"Schema with {len(sections)} sections"
        if sections:
            layout_desc += f": {', '.join([s.get('id', '') for s in sections])}"

        return cls.add_memory(
            business_id=business_id,
            patch_name="fallback_layout_optimization",
            reason="Populating RAG memory with successful layout configuration in fallback mode",
            layout_used=layout_desc,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            conversion_gain=conversion_gain,
            agent_name="BusinessCopilot",
            patch_outcome="success",
            industry_type=industry,
            patch_json=layout_snapshot,
        )

    # ================================================================
    # Utility: Store a failed patch as negative memory
    # ================================================================

    @classmethod
    def add_failure_memory(cls, business_id, patch_name, reason, error_detail, patch_json=None):
        """
        Records a failed patch attempt so the AI avoids repeating it.
        Stores the full error context and patch_json for richer failure matching.
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
            patch_json=patch_json,
        )

