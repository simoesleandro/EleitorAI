import pytest
from unittest.mock import patch
from core.coletores.youtube import coletar_transcricao, salvar_mencao, _hash_conteudo
from core.modelos import Mencao


@pytest.fixture
def fonte(db):
    from core.db import get_db
    conn = get_db(db_path=db)
    conn.execute(
        "INSERT INTO fontes (tipo, identificador, coletor) VALUES ('youtube', 'test-vid', 'core.coletores.youtube')"
    )
    conn.commit()
    row = conn.execute("SELECT id FROM fontes WHERE identificador='test-vid'").fetchone()
    fid = row["id"]
    conn.close()
    return fid


def test_hash_conteudo_dedup():
    h1 = _hash_conteudo("video123", "mesmo texto")
    h2 = _hash_conteudo("video123", "mesmo texto")
    h3 = _hash_conteudo("video456", "mesmo texto")
    assert h1 == h2
    assert h1 != h3


def test_salvar_mencao_retorna_id(db, fonte):
    m = Mencao(fonte_id=fonte, texto="teste", timestamp="2026-06-18T10:00:00", hash_conteudo="abc")
    mid = salvar_mencao(m)
    assert isinstance(mid, int)
    assert mid > 0


def test_salvar_mencao_dedup_mesmo_hash(db, fonte):
    m = Mencao(fonte_id=fonte, texto="dup", timestamp="2026-06-18T10:00:00", hash_conteudo="dup-hash")
    id1 = salvar_mencao(m)
    id2 = salvar_mencao(m)
    assert id1 == id2


def test_coletar_transcricao_usa_youtube_transcript_api(db):
    fake_transcript = [
        {"text": "zero crescimento populacional", "start": 0.0, "duration": 5.0},
        {"text": "vou melhorar a saude", "start": 5.0, "duration": 5.0},
    ]
    with patch("core.coletores.youtube.YouTubeTranscriptApi.get_transcript", return_value=fake_transcript):
        mencoes = coletar_transcricao("vid123", candidato_id=1)
    assert len(mencoes) == 2
    assert "zero crescimento" in mencoes[0].texto
