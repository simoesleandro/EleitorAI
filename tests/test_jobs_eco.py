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


def test_job_eco_coleta_com_handle_chama_instagram(db):
    with patch("core.coletores.instagram.coletar_posts", return_value=[]) as mock:
        result = job_eco_coleta({"instagram_handle": "@test", "limite": 5})
    assert result["coletado"] is True
    mock.assert_called_once_with("@test", limite=5)
