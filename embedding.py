from __future__ import annotations
import logging
from typing import List
from dotenv import load_dotenv, find_dotenv
import yaml
from google import genai
CONFIG_FILE = 'config.yaml'

with open(CONFIG_FILE, 'r') as config_file:
    config = yaml.load(config_file,Loader=yaml.FullLoader)

logger = logging.getLogger(__name__)
_ = load_dotenv(find_dotenv())

class GeminiAIEmbeddings():
    """`GeminiAI Embeddings` embedding models."""
    model_name = "text-embedding-004"
    client = genai.Client(api_key=config['gemini']['api_key'])
    """`GeminiAI.GeminiAI"""

    def embed_query(self, text: str) -> List[float]:
        """
        生成输入文本的 embedding.

        Args:
            texts (str): 要生成 embedding 的文本.

        Return:
            embeddings (List[float]): 输入文本的 embedding, 一个浮点数值列表.
        """
        embeddings = self.client.models.embed_content(
            model=self.model_name,
            contents=text
        )
        return embeddings.embeddings[0].values

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        生成输入文本列表的 embedding.
        Args:
            texts (List[str]): 要生成 embedding 的文本列表.

        Returns:
            List[List[float]]: 输入列表中每个文档的 embedding 列表。每个 embedding 都表示为一个浮点值列表。
        """
        return [self.embed_query(text) for text in texts]
