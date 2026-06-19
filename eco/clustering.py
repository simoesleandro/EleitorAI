import logging

import hdbscan
import numpy as np

from core.llm import gerar_embedding
from core.modelos import Cluster

logger = logging.getLogger(__name__)


def clusterizar_mencoes(mencoes: list[dict], min_cluster_size: int = 5) -> list[Cluster]:
    if len(mencoes) < min_cluster_size:
        return []
    embeddings = []
    for m in mencoes:
        try:
            emb = gerar_embedding(m["texto"])
            embeddings.append(emb)
        except Exception as e:
            logger.warning(f"embedding falhou p/ mencao {m.get('id')}: {e}")
            embeddings.append([0.0] * 768)
    if not embeddings:
        return []
    matrix = np.array(embeddings)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, min_samples=3)
    labels = clusterer.fit_predict(matrix)
    clusters = []
    for label in set(labels):
        if label == -1:
            continue
        indices = [i for i, label_val in enumerate(labels) if label_val == label]
        if len(indices) < min_cluster_size:
            continue
        mencao_ids = [mencoes[i]["id"] for i in indices]
        centroide = _gerar_centroide_texto(mencoes, indices)
        clusters.append(Cluster(
            id=f"cluster_{label}",
            mencao_ids=mencao_ids,
            centroide_texto=centroide,
            volume=len(mencao_ids),
        ))
    return clusters


def _gerar_centroide_texto(mencoes: list[dict], indices: list[int]) -> str:
    textos = [mencoes[i]["texto"] for i in indices[:5]]
    return " | ".join(textos[:3])[:200]
