from unittest.mock import patch
from worker.jobs_eco import job_eco_analyze, job_eco_coleta


def test_job_eco_analyze_retorna_resumo(db):
    fake_state = {
        "status": "concluido",
        "narrativas": [],
        "_grafos": {},
        "_amplificadores": {},
    }
    with patch("worker.jobs_eco.rodar_eco", return_value=fake_state):
        result = job_eco_analyze({"janela_horas": 6})
    assert result["status"] == "concluido"
    assert result["narrativas_processadas"] == 0
    assert result["janela_horas"] == 6


def test_job_eco_coleta_sem_handle_retorna_ok(db):
    result = job_eco_coleta({})
    assert result["coletado"] is True
    assert "telegram" in result
    assert "instagram" in result


def test_job_eco_coleta_com_handle_chama_instagram(db):
    with patch("core.coletores.instagram.coletar_posts", return_value=[]) as mock:
        result = job_eco_coleta({"instagram_handle": "test", "limite": 5})
    assert result["coletado"] is True
    assert result["instagram"] == 0
    mock.assert_called_once_with("test", limite=5)


def test_job_eco_coleta_handle_com_arroia_vira_telegram(db):
    """Handles starting with @ go to Telegram, not Instagram."""
    with patch("worker.jobs_eco._coletar_telegram", return_value=5) as mock_tg, \
         patch("core.coletores.instagram.coletar_posts") as mock_ig:
        result = job_eco_coleta({"instagram_handle": "@canal_telegram", "limite": 50})
    assert result["telegram"] == 5
    assert result["instagram"] == 0
    mock_tg.assert_called_once_with("@canal_telegram", 50)
    mock_ig.assert_not_called()


def test_job_eco_coleta_sem_handle_itera_fontes_telegram_ativas(db):
    """Without specific handle, iterate all active Telegram fontes."""
    conn = __import__("sqlite3").connect(db)
    conn.execute("DELETE FROM fontes")
    for canal in ("@a", "@b", "@c"):
        conn.execute(
            "INSERT INTO fontes (tipo, identificador, ativa, coletor) VALUES ('telegram', ?, 1, ?)",
            (canal, "core.coletores.telegram"),
        )
    conn.commit()
    conn.close()
    with patch("worker.jobs_eco._coletar_telegram", return_value=3) as mock:
        result = job_eco_coleta({"limite": 50})
    assert result["telegram"] == 9
    assert mock.call_count == 3
    canais_chamados = [c.args[0] for c in mock.call_args_list]
    assert canais_chamados == ["@a", "@b", "@c"]


def test_job_eco_coleta_canais_explicitos(db):
    with patch("worker.jobs_eco._coletar_telegram", return_value=2) as mock:
        result = job_eco_coleta({"telegram_channels": ["@x", "@y", "@z"]})
    assert result["telegram"] == 6
    assert mock.call_count == 3


def test_job_eco_coleta_ignora_fontes_inativas(db):
    conn = __import__("sqlite3").connect(db)
    conn.execute("DELETE FROM fontes")
    conn.execute(
        "INSERT INTO fontes (tipo, identificador, ativa, coletor) VALUES ('telegram', '@ativo', 1, ?)",
        ("core.coletores.telegram",),
    )
    conn.execute(
        "INSERT INTO fontes (tipo, identificador, ativa, coletor) VALUES ('telegram', '@inativo', 0, ?)",
        ("core.coletores.telegram",),
    )
    conn.commit()
    conn.close()
    with patch("worker.jobs_eco._coletar_telegram", return_value=1) as mock:
        result = job_eco_coleta({})
    canais_chamados = [c.args[0] for c in mock.call_args_list]
    assert "@ativo" in canais_chamados
    assert "@inativo" not in canais_chamados
