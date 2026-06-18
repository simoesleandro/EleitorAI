from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Veredito = Literal["verdadeiro", "falso", "enganoso", "impreciso", "sem_contexto"]
Severidade = Literal["info", "medio", "alto", "critico"]
JobStatus = Literal["pending", "running", "done", "failed"]
TipoFonte = Literal["telegram", "youtube", "instagram", "portal"]
Modulo = Literal["veritas", "eco", "tribuno"]


class Evidencia(BaseModel):
    fonte: str
    trecho: str
    url: Optional[str] = None


class Mencao(BaseModel):
    fonte_id: int
    texto: str
    timestamp: str
    hash_conteudo: str
    candidato_id: Optional[int] = None
    autor: Optional[str] = None
    autor_id: Optional[str] = None
    url: Optional[str] = None
    metricas: dict[str, Any] = Field(default_factory=dict)
    id: Optional[int] = None


class Afirmacao(BaseModel):
    mencao_id: int
    texto: str
    sujeito: Optional[str] = None
    predicado: Optional[str] = None
    checavel: bool = True
    confianca_extracao: Optional[float] = None
    id: Optional[int] = None


class Checagem(BaseModel):
    afirmacao_id: int
    veredito: Veredito
    evidencias: list[Evidencia]
    fontes_independentes: int
    confianca: float
    justificativa: Optional[str] = None
    contraposicao_sugerida: Optional[str] = None
    modelo: Optional[str] = None
    id: Optional[int] = None


class Alerta(BaseModel):
    modulo: Modulo
    severidade: Severidade
    titulo: str
    payload: dict[str, Any]
    enviado_telegram: bool = False
    criado_em: Optional[str] = None
    id: Optional[int] = None


class Job(BaseModel):
    modulo: Modulo
    tipo: str
    payload: dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = "pending"
    resultado: Optional[dict[str, Any]] = None
    criado_em: Optional[str] = None
    iniciado_em: Optional[str] = None
    concluido_em: Optional[str] = None
    id: Optional[int] = None


class Candidato(BaseModel):
    nome: str
    cargo: str
    partido: Optional[str] = None
    alianca: Optional[str] = None
    eh_proprio: bool = False
    monitorar_veritas: bool = True
    monitorar_eco: bool = True
    id: Optional[int] = None


class Fonte(BaseModel):
    tipo: TipoFonte
    identificador: str
    coletor: str
    nome: Optional[str] = None
    ativa: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    ultimo_coleta: Optional[str] = None
    id: Optional[int] = None
