import json
from datetime import datetime, timedelta
from typing import TypedDict

from langgraph.graph import END, StateGraph

from core.db import get_db
from core.fila import enqueue
from core.modelos import Cluster, Narrativa
from eco.agentes.analista_rede import analisar_rede
from eco.agentes.caracterizador import caracterizar_narrativa
from eco.agentes.critico import revisar_classificacao
from eco.agentes.narratorologo import nomear_narrativa
from eco.clustering import clusterizar_mencoes
from eco.grafo import calcular_metricas, construir_grafo, extrair_amplificadores

Z_SCORE_THRESHOLD = 2.0
MAX_ITERACOES_CRITICA = 2


class EcoState(TypedDict, total=False):
    janela_inicio: str
    janela_fim: str
    mencoes: list[dict]
    clusters: list[Cluster]
    clusters_emergentes: list[Cluster]
    narrativas: list[Narrativa]
    alertas: list[dict]
    status: str
    iteracoes_critica: int
    _grafos: dict
    _metricas: dict
    _amplificadores: dict
    _features: dict
    _classificacoes: dict


def rodar_eco(janela_horas: int = 6) -> EcoState:
    agora = datetime.now()
    inicio = agora - timedelta(hours=janela_horas)
    state: EcoState = {
        "janela_inicio": inicio.isoformat(),
        "janela_fim": agora.isoformat(),
        "mencoes": [],
        "clusters": [],
        "clusters_emergentes": [],
        "narrativas": [],
        "alertas": [],
        "status": "pendente",
        "iteracoes_critica": 0,
    }
    graph = _construir_grafo()
    return graph.invoke(state)


def _construir_grafo() -> StateGraph:
    g = StateGraph(EcoState)
    g.add_node("ingestao", _no_ingestao)
    g.add_node("clustering", _no_clustering)
    g.add_node("deteccao_emergencia", _no_deteccao)
    g.add_node("grafo_analise", _no_grafo_analise)
    g.add_node("caracterizacao", _no_caracterizacao)
    g.add_node("nomeacao", _no_nomeacao)
    g.add_node("critico", _no_critico)
    g.add_node("entrega", _no_entrega)

    g.set_entry_point("ingestao")
    g.add_edge("ingestao", "clustering")
    g.add_edge("clustering", "deteccao_emergencia")
    g.add_conditional_edges("deteccao_emergencia", _decisao_pos_deteccao, {
        "grafo_analise": "grafo_analise",
        "entrega": "entrega",
    })
    g.add_edge("grafo_analise", "caracterizacao")
    g.add_edge("caracterizacao", "nomeacao")
    g.add_edge("nomeacao", "critico")
    g.add_conditional_edges("critico", _decisao_pos_critica, {
        "entrega": "entrega",
        "caracterizacao": "caracterizacao",
    })
    g.add_edge("entrega", END)
    return g.compile()


def _no_ingestao(state: EcoState) -> EcoState:
    state["mencoes"] = _query_mencoes_janela(state["janela_inicio"], state["janela_fim"])
    state["status"] = "em_progresso"
    return state


def _query_mencoes_janela(inicio: str, fim: str) -> list[dict]:
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT * FROM mencoes WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp",
            (inicio, fim),
        )
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            r["metricas"] = json.loads(r["metricas"]) if r["metricas"] else {}
        return rows
    finally:
        conn.close()


def _no_clustering(state: EcoState) -> EcoState:
    state["clusters"] = clusterizar_mencoes(state["mencoes"])
    return state


def _no_deteccao(state: EcoState) -> EcoState:
    state["clusters_emergentes"] = _detectar_emergentes(state["clusters"], state["mencoes"])
    return state


def _detectar_emergentes(clusters: list[Cluster], mencoes: list[dict]) -> list[Cluster]:
    return clusters


def _decisao_pos_deteccao(state: EcoState) -> str:
    if not state["clusters_emergentes"]:
        return "entrega"
    return "grafo_analise"


def _no_grafo_analise(state: EcoState) -> EcoState:
    state["_grafos"] = {}
    state["_metricas"] = {}
    state["_amplificadores"] = {}
    state["_features"] = {}
    for cluster in state["clusters_emergentes"]:
        mencoes_cluster = [m for m in state["mencoes"] if m["id"] in cluster.mencao_ids]
        grafo = construir_grafo(mencoes_cluster)
        metricas = calcular_metricas(grafo)
        amplifs = extrair_amplificadores(grafo, metricas)
        features = analisar_rede(grafo, metricas, amplifs)
        state["_grafos"][cluster.id] = grafo
        state["_metricas"][cluster.id] = metricas
        state["_amplificadores"][cluster.id] = amplifs
        state["_features"][cluster.id] = features
    return state


def _no_caracterizacao(state: EcoState) -> EcoState:
    state["_classificacoes"] = {}
    for cluster in state["clusters_emergentes"]:
        features = state["_features"][cluster.id]
        classificacao, justificativa, confianca = caracterizar_narrativa(cluster, features)
        state["_classificacoes"][cluster.id] = (classificacao, justificativa, confianca)
    return state


def _no_nomeacao(state: EcoState) -> EcoState:
    state["narrativas"] = []
    for cluster in state["clusters_emergentes"]:
        classificacao, justificativa, confianca = state["_classificacoes"][cluster.id]
        nome, descricao, candidatos = nomear_narrativa(cluster, classificacao)
        primeiro_post = min(
            (m["timestamp"] for m in state["mencoes"] if m["id"] in cluster.mencao_ids),
            default="",
        )
        n = Narrativa(
            cluster_id=cluster.id, nome=nome, descricao=descricao,
            volume=cluster.volume, velocidade_crescimento=0.0,
            classificacao=classificacao, confianca=confianca,
            justificativa=justificativa, candidatos_afetados=candidatos,
            primeiro_post_em=primeiro_post,
        )
        state["narrativas"].append(n)
    return state


def _no_critico(state: EcoState) -> EcoState:
    state["iteracoes_critica"] += 1
    for n in state["narrativas"]:
        review = revisar_classificacao(n)
        if not review["aprova"]:
            if state["iteracoes_critica"] >= MAX_ITERACOES_CRITICA:
                state["status"] = "revisar"
                return state
            return state
    return state


def _decisao_pos_critica(state: EcoState) -> str:
    return "entrega"


def _no_entrega(state: EcoState) -> EcoState:
    if state["status"] != "revisar":
        state["status"] = "concluido"
    for n in state["narrativas"]:
        if n.classificacao in ("coordenado", "suspeito_bot"):
            _dispara_veritas(n)
    return state


def _dispara_veritas(narrativa: Narrativa) -> None:
    enqueue("veritas", "veritas_check", {
        "conteudo": narrativa.descricao,
        "narrativa_id": narrativa.cluster_id,
    })
