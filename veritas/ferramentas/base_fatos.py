from core.rag.retriever import buscar


def buscar_factcheck(claim: str, k: int = 5) -> list[dict]:
    return buscar(claim, entidade_tipo="factcheck", k=k)
