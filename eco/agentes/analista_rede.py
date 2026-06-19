from typing import Any

import networkx as nx

from core.modelos import Amplificador


def analisar_rede(grafo: nx.DiGraph, metricas: dict, amplificadores: list[Amplificador]) -> dict[str, Any]:
    degrees = list(metricas["degree"].values()) if metricas["degree"] else [0]
    suspeitos_bot = sum(1 for a in amplificadores if a.suspeita_bot)
    contas_jovens = sum(1 for a in amplificadores if a.idade_conta_dias is not None and a.idade_conta_dias < 90)
    return {
        "num_contas": grafo.number_of_nodes(),
        "num_arestas": grafo.number_of_edges(),
        "max_degree": max(degrees),
        "degree_medio": sum(degrees) / len(degrees) if degrees else 0,
        "num_comunidades": len(metricas.get("comunidades", [])),
        "suspeitos_bot": suspeitos_bot,
        "contas_jovens": contas_jovens,
        "densidade": nx.density(grafo),
    }
