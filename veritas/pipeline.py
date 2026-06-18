from typing import Optional, TypedDict

from langgraph.graph import StateGraph, END

from core.modelos import ClaimExtraida, ResultadoVerificacao
from veritas.agentes.extrator import extrair_claims
from veritas.agentes.pesquisador import pesquisar_evidencias
from veritas.agentes.verificador import verificar_claim, validar_guard_fontes
from veritas.agentes.redator import gerar_dossie_md
from veritas.agentes.critico import revisar_checagem

MAX_ITERACOES_CRITICA = 3
MAX_ITERACOES_GUARD = 2


class VeritasState(TypedDict, total=False):
    conteudo: str
    mencao_id: Optional[int]
    afirmacoes: list[ClaimExtraida]
    checagens: list[tuple[ClaimExtraida, ResultadoVerificacao]]
    dossie_md: Optional[str]
    status: str
    iteracoes_critica: int
    erros: list[str]


def rodar_veritas(conteudo: str, mencao_id: Optional[int] = None) -> VeritasState:
    state: VeritasState = {
        "conteudo": conteudo,
        "mencao_id": mencao_id,
        "afirmacoes": [],
        "checagens": [],
        "dossie_md": None,
        "status": "pendente",
        "iteracoes_critica": 0,
        "erros": [],
    }
    graph = _construir_grafo()
    final = graph.invoke(state)
    return final


def _construir_grafo() -> StateGraph:
    g = StateGraph(VeritasState)
    g.add_node("extrair", _no_extrair)
    g.add_node("pesquisar", _no_pesquisar)
    g.add_node("verificar", _no_verificar)
    g.add_node("redator", _no_redator)
    g.add_node("critico", _no_critico)
    g.add_node("entrega", _no_entrega)

    g.set_entry_point("extrair")
    g.add_edge("extrair", "pesquisar")
    g.add_edge("pesquisar", "verificar")
    g.add_conditional_edges("verificar", _decisao_pos_verificacao, {
        "redator": "redator",
        "pesquisar": "pesquisar",
    })
    g.add_edge("redator", "critico")
    g.add_conditional_edges("critico", _decisao_pos_critica, {
        "entrega": "entrega",
        "pesquisar": "pesquisar",
    })
    g.add_edge("entrega", END)
    return g.compile()


def _no_extrair(state: VeritasState) -> VeritasState:
    claims = extrair_claims(state["conteudo"], apenas_checaveis=True)
    state["afirmacoes"] = claims
    state["status"] = "em_progresso"
    return state


def _no_pesquisar(state: VeritasState) -> VeritasState:
    state["checagens"] = []
    for claim in state["afirmacoes"]:
        evidencias = pesquisar_evidencias(claim)
        state["checagens"].append((claim, evidencias))
    return state


def _no_verificar(state: VeritasState) -> VeritasState:
    novas_checagens = []
    for claim, evidencias_ou_rv in state["checagens"]:
        if isinstance(evidencias_ou_rv, ResultadoVerificacao):
            novas_checagens.append((claim, evidencias_ou_rv))
            continue
        rv = verificar_claim(claim, evidencias_ou_rv)
        novas_checagens.append((claim, rv))
    state["checagens"] = novas_checagens
    return state


def _decisao_pos_verificacao(state: VeritasState) -> str:
    for claim, rv in state["checagens"]:
        guard = validar_guard_fontes(rv)
        if not guard["passou"]:
            state["erros"].append(f"guard falhou p/ '{claim.texto}': {guard['motivo']}")
            return "pesquisar"
    return "redator"


def _no_redator(state: VeritasState) -> VeritasState:
    state["dossie_md"] = gerar_dossie_md(state["conteudo"], state["checagens"])
    return state


def _no_critico(state: VeritasState) -> VeritasState:
    state["iteracoes_critica"] += 1
    for claim, rv in state["checagens"]:
        review = revisar_checagem(rv, claim)
        if not review["aprova"]:
            if state["iteracoes_critica"] >= MAX_ITERACOES_CRITICA:
                state["status"] = "revisar"
            else:
                state["status"] = "em_revisao"
            return state
    return state


def _decisao_pos_critica(state: VeritasState) -> str:
    if state.get("status") == "revisar":
        return "entrega"
    if state.get("status") == "em_revisao":
        return "pesquisar"
    return "entrega"


def _no_entrega(state: VeritasState) -> VeritasState:
    if state["status"] != "revisar":
        state["status"] = "concluido"
    return state
