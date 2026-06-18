import pytest
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
