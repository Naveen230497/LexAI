"""Retrieval-Augmented Generation engine for per-session legal document Q&A."""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncGenerator

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.prompts.qa_system import build_qa_prompt

if TYPE_CHECKING:
    from app.core.gemini_client import GeminiClient


class RAGEngine:
    """Retrieval-Augmented Generation engine for legal document Q&A.

    Uses ChromaDB as the vector store and LangChain to orchestrate the
    retrieval chain. Each session gets its own ChromaDB collection so
    documents are isolated between users.

    Attributes:
        _session_id: Unique session identifier used as the ChromaDB collection name.
        _chroma_dir: Filesystem path where ChromaDB persists its data.
        _gemini_client: Configured :class:`GeminiClient` instance for generation.
        _embedding_model: Gemini embedding model identifier string.
        _vectorstore: ChromaDB-backed LangChain vector store (set after indexing).
    """

    def __init__(
        self,
        session_id: str,
        chroma_dir: str,
        gemini_client: "GeminiClient",
        embedding_model: str,
    ) -> None:
        """Initialize the RAG engine for a specific session.

        Args:
            session_id: Unique session ID; used as the ChromaDB collection name.
            chroma_dir: Filesystem path for ChromaDB persistence.
            gemini_client: Configured Gemini client used for answer generation.
            embedding_model: Gemini embedding model identifier.
        """
        self._session_id = session_id
        self._chroma_dir = chroma_dir
        self._gemini_client = gemini_client
        self._embedding_model = embedding_model
        self._vectorstore: Chroma | None = None

        # Build the LangChain embeddings wrapper once; it is stateless.
        from app.config import get_settings

        settings = get_settings()
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=settings.GEMINI_API_KEY,
        )

    def index_document(self, chunks: list[str]) -> None:
        """Embed document chunks and store them in ChromaDB.

        Creates or replaces the ChromaDB collection for this session. Calling
        this method a second time on the same session will overwrite the
        previous index.

        Args:
            chunks: List of text chunks produced by
                :func:`app.core.document_processor.chunk_document`.
        """
        # Security: Collection name is scoped to session_id (a UUID) so one
        # user's data never bleeds into another session's collection.
        collection_name = f"session_{self._session_id.replace('-', '_')}"

        self._vectorstore = Chroma.from_texts(
            texts=chunks,
            embedding=self._embeddings,
            collection_name=collection_name,
            persist_directory=self._chroma_dir,
        )

    async def stream_answer(
        self,
        question: str,
        history: list[dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        """Stream answer tokens for a question about the indexed document.

        Retrieves the top-5 most relevant chunks using MMR (Maximum Marginal
        Relevance) search, then builds a grounded prompt and streams the
        Gemini response token by token.

        Args:
            question: Sanitized user question about the document.
            history: Previous conversation turns as a list of
                ``{"role": str, "content": str}`` dicts.

        Yields:
            Individual text tokens from the Gemini streaming response.

        Raises:
            RuntimeError: If :meth:`index_document` has not been called first.
        """
        if self._vectorstore is None:
            raise RuntimeError(
                "RAGEngine.index_document() must be called before stream_answer()."
            )

        # MMR retrieval reduces redundancy among retrieved chunks, ensuring
        # the top-5 chunks cover diverse sections of the document.
        retriever = self._vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20},
        )
        relevant_docs = retriever.invoke(question)
        context_chunks = [doc.page_content for doc in relevant_docs]

        prompt = self._build_retrieval_prompt(question, context_chunks, history)

        async for token in self._gemini_client.stream_generate(prompt):
            yield token

    def _build_retrieval_prompt(
        self,
        question: str,
        context_chunks: list[str],
        history: list[dict[str, str]],
    ) -> str:
        """Build the full grounded prompt combining context, history, and question.

        Args:
            question: The user's question.
            context_chunks: Retrieved document chunks from ChromaDB.
            history: Prior conversation turns.

        Returns:
            Complete prompt string ready for Gemini.
        """
        context = "\n\n---\n\n".join(context_chunks)
        return build_qa_prompt(context=context, question=question, history=history)
