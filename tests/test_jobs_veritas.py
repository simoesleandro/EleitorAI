from unittest.mock import patch
from worker.jobs_veritas import job_veritas_check


def test_job_veritas_check_salva_e_envia_alerta_se_falso(tmp_path, monkeypatch):
    from core.config import get_settings
    get_settings.cache_clear()
    monkeypatch.setenv("DB_PATH", str(tmp_path / "t.db"))
    from core.db import init_db
    init_db(str(tmp_path / "t.db"))

    fake_state = {
        "status": "concluido",
        "dossie_md": "# dossie",
        "checagens": [],
    }
    with patch("worker.jobs_veritas.rodar_veritas", return_value=fake_state), \
         patch("worker.jobs_veritas.enviar_alerta") as mock_alerta, \
         patch("worker.jobs_veritas._salvar_checagens") as mock_salvar:
        result = job_veritas_check({"conteudo": "x", "mencao_id": 1})
    assert result["status"] == "concluido"
    mock_salvar.assert_called_once()


def test_job_veritas_check_sem_mencao_id_cria_ad_hoc(tmp_path, monkeypatch):
    from core.config import get_settings
    from core.db import get_db, init_db
    from core.modelos import ClaimExtraida, Evidencia, ResultadoVerificacao
    from worker.jobs_veritas import AD_HOC_MENCAO_TEXTO

    get_settings.cache_clear()
    db_path = str(tmp_path / "t.db")
    monkeypatch.setenv("DB_PATH", db_path)
    init_db(db_path)

    conn = get_db(db_path)
    conn.execute(
        "INSERT INTO fontes (tipo, identificador, nome, coletor) VALUES (?, ?, ?, ?)",
        ("rss", "ad-hoc-src", "ad-hoc", "manual"),
    )
    conn.execute(
        "INSERT INTO candidatos (nome, partido, cargo) VALUES (?, ?, ?)",
        ("Candidato Ad-hoc", "PART", "governador"),
    )
    conn.commit()
    conn.close()

    claim = ClaimExtraida(texto="afirmacao teste", checavel=True, confianca=0.9)
    rv = ResultadoVerificacao(
        veredito="verdadeiro",
        evidencias=[Evidencia(fonte="IBGE", trecho="ok", url="u")],
        fontes_independentes=1,
        confianca=0.9,
        justificativa="ok",
        contraposicao_sugerida="",
    )
    fake_state = {
        "status": "concluido",
        "dossie_md": "# d",
        "checagens": [(claim, rv)],
    }

    with patch("worker.jobs_veritas.rodar_veritas", return_value=fake_state), \
         patch("worker.jobs_veritas.enviar_alerta"):
        result = job_veritas_check({"conteudo": "x"})

    assert result["status"] == "concluido"

    conn = get_db(db_path)
    row = conn.execute(
        "SELECT id FROM mencoes WHERE texto=?",
        (AD_HOC_MENCAO_TEXTO,),
    ).fetchone()
    assert row is not None
    ad_hoc_id = row["id"]
    af = conn.execute(
        "SELECT mencao_id FROM afirmacoes WHERE texto=?",
        ("afirmacao teste",),
    ).fetchone()
    assert af is not None
    assert af["mencao_id"] == ad_hoc_id
    ch = conn.execute(
        "SELECT c.veredito FROM checagens c JOIN afirmacoes a ON c.afirmacao_id=a.id WHERE a.texto=?",
        ("afirmacao teste",),
    ).fetchone()
    assert ch is not None
    assert ch["veredito"] == "verdadeiro"
    conn.close()
