import os
import uuid
import logging
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction,
)


class ChromaStore:
    """
    ChromaDB utility for Grace automation data.

    Collections managed:
    - strategy_evals: per-user, per-strategy evaluation snapshots
    - backtests: per-user, per-strategy backtest runs
    - trade_rationales: free-form explanations tied to trades/evals

    Persisted at data/chromadb/ by default to align with repo structure.
    """

    DEFAULT_COLLECTIONS = {
        "strategy_evals": "grace_strategy_evals",
        "backtests": "grace_backtests",
        "trade_rationales": "grace_trade_rationales",
    }

    def __init__(
        self,
        persist_dir: str = "data/chromadb",
        collections: Optional[Dict[str, str]] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        os.makedirs(persist_dir, exist_ok=True)
        self.logger = logging.getLogger("ChromaStore")
        self.client = chromadb.PersistentClient(path=persist_dir)
        # Use sentence-transformers to match repo requirements and enable similarity search
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        self.collections_cfg = collections or self.DEFAULT_COLLECTIONS

        # Warm up and ensure collections exist
        self._collections: Dict[str, Collection] = {}
        for key, name in self.collections_cfg.items():
            self._collections[key] = self.client.get_or_create_collection(
                name=name, embedding_function=self.embedding_function
            )
        self.logger.info(
            f"Initialized ChromaStore at {persist_dir} with collections: {self.collections_cfg}"
        )

    # Internal helpers
    def _col(self, key: str) -> Collection:
        if key not in self._collections:
            raise KeyError(f"Unknown collection key: {key}")
        return self._collections[key]

    def _gen_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid.uuid4().hex}"

    # Public: Strategy Evaluations
    def add_strategy_eval(
        self,
        user_id: str,
        strategy_id: str,
        document: str,
        score: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a strategy evaluation snapshot (free text) with optional score and metadata.
        Returns record id.
        """
        col = self._col("strategy_evals")
        rid = self._gen_id("eval")
        meta = {
            "user_id": user_id,
            "strategy_id": strategy_id,
            "kind": "strategy_eval",
        }
        if score is not None:
            meta["score"] = float(score)
        if metadata:
            meta.update(metadata)
        col.add(ids=[rid], documents=[document], metadatas=[meta])
        return rid

    def query_strategy_evals(
        self,
        user_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 10,
    ) -> Dict[str, Any]:
        col = self._col("strategy_evals")
        _where = dict(where or {})
        if user_id:
            _where["user_id"] = user_id
        if strategy_id:
            _where["strategy_id"] = strategy_id
        return col.query(where=_where, query_texts=query_texts or ["*"], n_results=n_results)

    # Public: Backtests
    def add_backtest(
        self,
        user_id: str,
        strategy_id: str,
        document: str,
        params: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a backtest run summary (free text) with parameters and metrics.
        Returns record id.
        """
        col = self._col("backtests")
        rid = self._gen_id("backtest")
        meta = {
            "user_id": user_id,
            "strategy_id": strategy_id,
            "kind": "backtest",
        }
        if params:
            meta["params"] = params
        if metrics:
            meta["metrics"] = metrics
        if metadata:
            meta.update(metadata)
        col.add(ids=[rid], documents=[document], metadatas=[meta])
        return rid

    def query_backtests(
        self,
        user_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 10,
    ) -> Dict[str, Any]:
        col = self._col("backtests")
        _where = dict(where or {})
        if user_id:
            _where["user_id"] = user_id
        if strategy_id:
            _where["strategy_id"] = strategy_id
        return col.query(where=_where, query_texts=query_texts or ["*"], n_results=n_results)

    # Public: Trade Rationales
    def add_trade_rationale(
        self,
        user_id: str,
        strategy_id: str,
        text: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a free-form rationale/explanation tied to a strategy or trade.
        Returns record id.
        """
        col = self._col("trade_rationales")
        rid = self._gen_id("rationale")
        meta = {
            "user_id": user_id,
            "strategy_id": strategy_id,
            "kind": "trade_rationale",
        }
        if tags:
            meta["tags"] = tags
        if metadata:
            meta.update(metadata)
        col.add(ids=[rid], documents=[text], metadatas=[meta])
        return rid

    def query_trade_rationales(
        self,
        user_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        where: Optional[Dict[str, Any]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 10,
    ) -> Dict[str, Any]:
        col = self._col("trade_rationales")
        _where = dict(where or {})
        if user_id:
            _where["user_id"] = user_id
        if strategy_id:
            _where["strategy_id"] = strategy_id
        return col.query(where=_where, query_texts=query_texts or ["*"], n_results=n_results)

    # Utility
    def delete_by_ids(self, collection_key: str, ids: List[str]) -> None:
        col = self._col(collection_key)
        col.delete(ids=ids)

    def reset_collection(self, collection_key: str) -> None:
        name = self.collections_cfg[collection_key]
        try:
            self.client.delete_collection(name)
        except Exception:
            pass
        self._collections[collection_key] = self.client.get_or_create_collection(
            name=name, embedding_function=self.embedding_function
        )
