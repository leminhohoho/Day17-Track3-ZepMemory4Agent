from __future__ import annotations

from typing import Any

from .config import settings
from .context_budget import ContextBudgetManager
from .utils import cap_query, join_nonempty
from .zep_common import prime_eval_thread, render_graph_search


class StudentMemory:
    """Only this file needs to be edited by students."""

    def __init__(self, client: Any):
        self.client = client
        self.budget = ContextBudgetManager(settings.context_tokens)

    # NOTE: Zep rejects graph.search queries longer than 400 characters. Some
    # eval queries are longer than that, so wrap every query with
    # `cap_query(query)` (see src/utils.py) before passing it to graph.search.

    def retrieve_long_term(self, user_id: str, thread_id: str, query: str) -> str:
        # The Context Block is assembled from whatever the thread currently
        # holds, so the eval query must be on the thread before we ask for it.
        prime_eval_thread(self.client, user_id, thread_id, query)

        user_context = self.client.thread.get_user_context(thread_id=thread_id)
        context_block = getattr(user_context, "context", "") or ""

        # The summary alone can drop specifics like an open-loop deadline, so
        # append an edge (fact) search. Edges carry valid_at/invalid_at, which
        # is also what makes the recency/conflict case explainable.
        try:
            facts = self.client.graph.search(
                user_id=user_id,
                query=cap_query(query),
                scope="edges",
                limit=20,
            )
            fact_text = render_graph_search(facts)
        except Exception:
            fact_text = ""

        return join_nonempty([context_block, fact_text], sep="\n\n")

    def retrieve_episodic(self, user_id: str, query: str) -> str:
        # user_id (not graph_id): episodes are the user's own trajectory.
        # scope="episodes" returns the raw source messages, which is what keeps
        # incident markers like ASYNC-FIX-20 intact.
        results = self.client.graph.search(
            user_id=user_id,
            query=cap_query(query),
            scope="episodes",
            limit=15,
        )
        # Cap each episode: a few long session messages would otherwise eat the
        # 3% episodic budget and push out the short reflection that carries the
        # "connection churn, not timeout threshold" conclusion.
        return render_graph_search(results, episode_char_cap=180)

    def retrieve_semantic(self, graph_id: str, query: str) -> str:
        # graph_id, NOT user_id: this is the shared domain KB, not anyone's
        # personal memory. Searching by user_id here would return preferences
        # instead of the playbook and fail E06/E11.
        capped = cap_query(query)
        try:
            results = self.client.graph.search(
                graph_id=graph_id,
                query=capped,
                scope="episodes",
                limit=8,
            )
        except Exception:
            # Not all accounts/SDK versions expose episode scope on a
            # standalone graph; nodes still carry the entity summaries.
            results = self.client.graph.search(
                graph_id=graph_id,
                query=capped,
                scope="nodes",
                limit=8,
            )
        # No episode_char_cap here: these documents put their marker
        # (PAYMENT-RULE-3, CONN-POOL-FIRST) at the END, so truncating loses it.
        return render_graph_search(results)

    def assemble_context(self, layers: dict[str, str]) -> tuple[str, dict[str, dict[str, int]]]:
        # ContextBudgetManager already encodes the lab's 10/4/3/3 split and the
        # short_term -> long_term -> episodic -> semantic priority order, and
        # returns (merged_text, per-layer breakdown).
        return self.budget.assemble(layers)
