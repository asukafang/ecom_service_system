"""向量化封装：调用 OpenAI Embeddings 接口。

- 支持批量编码（list[str] → list[list[float]]）。
- 可配置 model 与 base_url（与 chat 模型共用一套 OpenAI 客户端配置）。
- 返回原始 list[float]，由调用方决定如何持久化（这里用 json，不引入 numpy 依赖）。
"""

"""本地 Embedding 封装。"""

from typing import Iterable

from sentence_transformers import SentenceTransformer


class Embedder:
    """使用本地 Sentence Transformers 模型生成向量。"""

    def __init__(
        self,
        api_key: str = "",
        base_url: str = "",
        model: str = "BAAI/bge-small-zh-v1.5",
        batch_size: int = 32,
    ):
        self._model = model
        self._batch_size = batch_size
        self._client = SentenceTransformer(model)

    @property
    def model(self) -> str:
        return self._model

    def encode(self, texts: Iterable[str]) -> list[list[float]]:
        texts = list(texts)
        if not texts:
            return []

        vectors = self._client.encode(
            texts,
            batch_size=self._batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return vectors.tolist()

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0]