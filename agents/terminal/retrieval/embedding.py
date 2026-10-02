# import asyncio
# from dataclasses import dataclass

# from sentence_transformers import SentenceTransformer


# class EmbeddingProviderError(RuntimeError):
#     """Raised when embedding generation violates the provider contract."""


# @dataclass(frozen=True)
# class Qwen3EmbeddingConfig:
#     """
#     Configuration for Qwen/Qwen3-Embedding-0.6B.
#     """

#     model_name: str = "Qwen/Qwen3-Embedding-0.6B"

#     dimension: int = 1024

#     batch_size: int = 16

#     device: str | None = None

#     normalize_embeddings: bool = True


# class Qwen3EmbeddingProvider:
#     """
#     Local embedding provider backed by Qwen3-Embedding-0.6B.

#     Query and document encoding remain separate because Qwen3 uses
#     a query-specific retrieval prompt while documents are encoded
#     without that query instruction.
#     """

#     def __init__(
#         self,
#         config: Qwen3EmbeddingConfig | None = None,
#         *,
#         model=None,
#     ) -> None:
#         self.config = config or Qwen3EmbeddingConfig()

#         self._validate_config()

#         self._model = model

#         if self._model is None:
#             self._model = SentenceTransformer(
#                 self.config.model_name,
#                 device=self.config.device,
#             )

#     @property
#     def dimension(self) -> int:
#         return self.config.dimension

#     @property
#     def model_name(self) -> str:
#         return self.config.model_name

#     async def embed_documents(
#         self,
#         texts: list[str],
#     ) -> list[list[float]]:
#         self._validate_text_batch(
#             texts,
#             name="documents",
#         )

#         if not texts:
#             return []

#         vectors = await asyncio.to_thread(
#             self._encode_documents,
#             texts,
#         )

#         return self._validate_vectors(
#             vectors,
#             expected_count=len(texts),
#         )

#     async def embed_queries(
#         self,
#         texts: list[str],
#     ) -> list[list[float]]:
#         self._validate_text_batch(
#             texts,
#             name="queries",
#         )

#         if not texts:
#             return []

#         vectors = await asyncio.to_thread(
#             self._encode_queries,
#             texts,
#         )

#         return self._validate_vectors(
#             vectors,
#             expected_count=len(texts),
#         )

#     def _encode_documents(
#         self,
#         texts: list[str],
#     ):
#         return self._model.encode_document(
#             texts,
#             batch_size=self.config.batch_size,
#             normalize_embeddings=(self.config.normalize_embeddings),
#             truncate_dim=self.config.dimension,
#             convert_to_numpy=True,
#             show_progress_bar=False,
#         )

#     def _encode_queries(
#         self,
#         texts: list[str],
#     ):
#         return self._model.encode_query(
#             texts,
#             batch_size=self.config.batch_size,
#             normalize_embeddings=(self.config.normalize_embeddings),
#             truncate_dim=self.config.dimension,
#             convert_to_numpy=True,
#             show_progress_bar=False,
#         )

#     def _validate_vectors(
#         self,
#         vectors,
#         *,
#         expected_count: int,
#     ) -> list[list[float]]:
#         if vectors is None:
#             raise EmbeddingProviderError(
#                 "Embedding provider returned no vectors.",
#             )

#         vector_list = [
#             vector.tolist() if hasattr(vector, "tolist") else list(vector)
#             for vector in vectors
#         ]

#         if len(vector_list) != expected_count:
#             raise EmbeddingProviderError(
#                 "Embedding count mismatch: "
#                 f"expected {expected_count}, "
#                 f"received {len(vector_list)}.",
#             )

#         for index, vector in enumerate(
#             vector_list,
#         ):
#             if len(vector) != self.config.dimension:
#                 raise EmbeddingProviderError(
#                     "Embedding dimension mismatch at index "
#                     f"{index}: expected "
#                     f"{self.config.dimension}, received "
#                     f"{len(vector)}.",
#                 )

#         return [[float(value) for value in vector] for vector in vector_list]

#     @staticmethod
#     def _validate_text_batch(
#         texts: list[str],
#         *,
#         name: str,
#     ) -> None:
        
#         if not isinstance(
#             texts,
#             list,
#         ):
#             raise TypeError(
#                 f"{name} must be a list of strings.",
#             )

#         for index, text in enumerate(
#             texts,
#         ):
#             if not isinstance(
#                 text,
#                 str,
#             ):
#                 raise TypeError(
#                     f"{name}[{index}] must be a string.",
#                 )

#             if not text.strip():
#                 raise ValueError(
#                     f"{name}[{index}] cannot be empty.",
#                 )

#     def _validate_config(self) -> None:
#         if self.config.dimension < 1:
#             raise ValueError(
#                 "dimension must be at least 1.",
#             )

#         if self.config.batch_size < 1:
#             raise ValueError(
#                 "batch_size must be at least 1.",
#             )

from dataclasses import dataclass

from ollama import AsyncClient, ResponseError


class EmbeddingProviderError(RuntimeError):
    """Raised when embedding generation violates the provider contract."""


@dataclass(frozen=True)
class Qwen3EmbeddingConfig:
    """
    Configuration for the local Qwen3 embedding model served by Ollama.
    """

    # model_name: str = "qwen3-embedding:4b"
    model_name: str = "qwen3-embedding:0.6b"

    dimension: int = 1024

    batch_size: int = 16

    host: str = "http://127.0.0.1:11434"

    normalize_embeddings: bool = True

    query_instruction: str = (
        "Given the Terminal Agent information need, "
        "retrieve retained evidence that is relevant to answering "
        "the query."
    )


class Qwen3EmbeddingProvider:
    """
    Local Qwen3-Embedding provider backed by Ollama.

    Documents are embedded as plain searchable text.

    Queries receive the Qwen retrieval instruction before being sent
    to Ollama, matching Qwen's query/document asymmetry.
    """

    def __init__(
        self,
        config: Qwen3EmbeddingConfig | None = None,
        *,
        client: AsyncClient | None = None,
    ) -> None:
        self.config = (
            config
            or Qwen3EmbeddingConfig()
        )

        self._validate_config()

        self._client = (
            client
            or AsyncClient(
                host=self.config.host,
            )
        )

    @property
    def dimension(self) -> int:
        return self.config.dimension

    @property
    def model_name(self) -> str:
        return self.config.model_name

    async def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self._validate_text_batch(
            texts,
            name="documents",
        )

        if not texts:
            return []

        return await self._embed(
            texts=texts,
        )

    async def embed_queries(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self._validate_text_batch(
            texts,
            name="queries",
        )

        if not texts:
            return []

        instructed_queries = [
            self._format_query(
                query,
            )
            for query in texts
        ]

        return await self._embed(
            texts=instructed_queries,
        )

    def _format_query(
        self,
        query: str,
    ) -> str:
        return (
            f"Instruct: "
            f"{self.config.query_instruction}\n"
            f"Query:{query}"
        )

    async def _embed(
        self,
        *,
        texts: list[str],
    ) -> list[list[float]]:
        try:
            response = await self._client.embed(
                model=self.config.model_name,
                input=texts,
                dimensions=self.config.dimension,
            )
        except ResponseError as exc:
            raise EmbeddingProviderError(
                "Ollama embedding request failed: "
                f"{exc}",
            ) from exc
        except Exception as exc:
            raise EmbeddingProviderError(
                "Unexpected embedding-provider failure: "
                f"{exc}",
            ) from exc

        embeddings = response.embeddings

        if embeddings is None:
            raise EmbeddingProviderError(
                "Ollama returned no embeddings.",
            )

        vector_list = [
            list(vector)
            for vector in embeddings
        ]

        self._validate_vectors(
            vector_list,
            expected_count=len(texts),
        )

        return [
            [
                float(value)
                for value in vector
            ]
            for vector in vector_list
        ]

    def _validate_vectors(
        self,
        vectors: list[list[float]],
        *,
        expected_count: int,
    ) -> None:
        if len(vectors) != expected_count:
            raise EmbeddingProviderError(
                "Embedding count mismatch: "
                f"expected {expected_count}, "
                f"received {len(vectors)}.",
            )

        for index, vector in enumerate(
            vectors,
        ):
            if len(vector) != self.config.dimension:
                raise EmbeddingProviderError(
                    "Embedding dimension mismatch at index "
                    f"{index}: expected "
                    f"{self.config.dimension}, received "
                    f"{len(vector)}.",
                )

        if not self.config.normalize_embeddings:
            return

        for index, vector in enumerate(vectors):
            norm = sum(
                value * value
                for value in vector
            ) ** 0.5

            if norm == 0:
                raise EmbeddingProviderError(
                    "Embedding vector at index "
                    f"{index} has zero magnitude.",
                )

    @staticmethod
    def _validate_text_batch(
        texts: list[str],
        *,
        name: str,
    ) -> None:
        if not isinstance(
            texts,
            list,
        ):
            raise TypeError(
                f"{name} must be a list of strings.",
            )

        for index, text in enumerate(
            texts,
        ):
            if not isinstance(
                text,
                str,
            ):
                raise TypeError(
                    f"{name}[{index}] must be a string.",
                )

            if not text.strip():
                raise ValueError(
                    f"{name}[{index}] cannot be empty.",
                )

    def _validate_config(self) -> None:
        if self.config.dimension < 1:
            raise ValueError(
                "dimension must be at least 1.",
            )

        if self.config.batch_size < 1:
            raise ValueError(
                "batch_size must be at least 1.",
            )

        if not self.config.model_name.strip():
            raise ValueError(
                "model_name cannot be empty.",
            )

        if not self.config.host.strip():
            raise ValueError(
                "host cannot be empty.",
            )

        if not self.config.query_instruction.strip():
            raise ValueError(
                "query_instruction cannot be empty.",
            )