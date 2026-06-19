import logging
from datetime import datetime
from typing import Optional

import networkx as nx

from core.modelos import Amplificador, RelacaoAmplificacao

logger = logging.getLogger(__name__)


def construir_grafo(mencoes: list[dict]) -> nx.DiGraph:
    grafo = nx.DiGraph()
    for m in mencoes:
        autor = str(m.get("autor_id") or m.get("autor") or "unknown")
        grafo.add_node(autor)
        forwarded_from = (m.get("metricas") or {}).get("forwarded_from")
        if forwarded_from:
            origem = str(forwarded_from)
            grafo.add_node(origem)
            grafo.add_edge(origem, autor, tipo="forward", timestamp=m.get("timestamp"))
    for i, m1 in enumerate(mencoes):
        for m2 in mencoes[i+1:]:
            if (m1.get("autor_id") and m2.get("autor_id") and
                m1.get("autor_id") != m2.get("autor_id") and
                m1.get("texto") == m2.get("texto") and
                m1.get("texto")):
                t1 = _parse_ts(m1.get("timestamp"))
                t2 = _parse_ts(m2.get("timestamp"))
                if t1 and t2:
                    delta = abs((t1 - t2).total_seconds()) / 60
                    if delta < 60:
                        grafo.add_edge(str(m1["autor_id"]), str(m2["autor_id"]),
                                       tipo="crosspost", janela_minutos=int(delta))
    return grafo


def calcular_metricas(grafo: nx.DiGraph) -> dict:
    return {
        "degree": dict(grafo.degree()),
        "in_degree": dict(grafo.in_degree()),
        "betweenness": nx.betweenness_centrality(grafo),
        "comunidades": list(nx.weakly_connected_components(grafo)),
    }


def extrair_amplificadores(grafo: nx.DiGraph, metricas: dict, tipo: str = "telegram_channel") -> list[Amplificador]:
    amplificadores = []
    max_degree = max(metricas["degree"].values()) if metricas["degree"] else 1
    for node, deg in metricas["degree"].items():
        if deg == 0:
            continue
        centralidade = deg / max_degree if max_degree > 0 else 0
        suspeita_bot = deg >= 5 and metricas["in_degree"].get(node, 0) == 0
        amplificadores.append(Amplificador(
            identificador=node,
            tipo=tipo,
            centralidade=centralidade,
            suspeita_bot=suspeita_bot,
        ))
    return sorted(amplificadores, key=lambda a: a.centralidade, reverse=True)


def extrair_relacoes(grafo: nx.DiGraph) -> list[RelacaoAmplificacao]:
    relacoes = []
    for u, v, data in grafo.edges(data=True):
        relacoes.append(RelacaoAmplificacao(
            de_identificador=u,
            para_identificador=v,
            peso=1.0,
            janela_minutos=data.get("janela_minutos", 0),
            tipo=data.get("tipo", "forward"),
        ))
    return relacoes


def _parse_ts(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None
