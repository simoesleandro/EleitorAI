"""Seed sample data for EleitorAI demo."""
from core.db import init_db, get_db

DB = r"C:\Meus_projetos\vox-plataforma\eleitorai\data\demo.db"
init_db(DB)
conn = get_db()

# Fontes
conn.execute(
    "INSERT OR IGNORE INTO fontes (tipo, identificador, nome, ativa, coletor) "
    "VALUES ('portal', 'g1.globo.com', 'G1', 1, 'core.coletores.youtube')"
)
conn.execute(
    "INSERT OR IGNORE INTO fontes (tipo, identificador, nome, ativa, coletor) "
    "VALUES ('telegram', '@exemplo', 'Canal Exemplo', 1, 'core.coletores.telegram')"
)
conn.execute(
    "INSERT OR IGNORE INTO fontes (tipo, identificador, nome, ativa, coletor) "
    "VALUES ('portal', 'uol.com.br', 'UOL', 1, 'core.coletores.youtube')"
)
conn.execute(
    "INSERT OR IGNORE INTO candidatos (nome, partido, cargo, eh_proprio) "
    "VALUES ('Candidato A', 'PARTIDO X', 'presidente', 1)"
)
conn.execute(
    "INSERT OR IGNORE INTO candidatos (nome, partido, cargo, eh_proprio) "
    "VALUES ('Opositor B', 'PARTIDO Y', 'presidente', 0)"
)

fonte_id = conn.execute("SELECT id FROM fontes ORDER BY id LIMIT 1").fetchone()["id"]
cand_id = conn.execute("SELECT id FROM candidatos WHERE eh_proprio = 1 LIMIT 1").fetchone()["id"]
oponente_id = conn.execute("SELECT id FROM candidatos WHERE eh_proprio = 0 LIMIT 1").fetchone()["id"]

# Menção ad-hoc
mencao = conn.execute(
    "INSERT INTO mencoes (fonte_id, candidato_id, texto, autor, autor_id, timestamp, url, metricas, hash_conteudo) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (fonte_id, cand_id, "[ad-hoc] coletiva de imprensa 18/06",
     "jornalista", "j1", "2026-06-18T14:00:00",
     "https://exemplo.com/noticia", "{}", "demo-adhoc-1"),
)
mencao_id = mencao.lastrowid

# Menções adicionais
extras = [
    ("Post 1: critica sem fundamento", "user1", "u1", 100),
    ("Post 2: dados favoraveis sobre economia", "user2", "u2", 250),
    ("Post 3: fake news sobre saude publica", "user3", "u3", 80),
    ("Post 4: video descontextualizado de 2019", "user4", "u4", 500),
    ("Post 5: verdade mas dado de 2018", "user5", "u5", 60),
]
for i, (txt, autor, autor_id, likes) in enumerate(extras):
    conn.execute(
        "INSERT INTO mencoes (fonte_id, candidato_id, texto, autor, autor_id, timestamp, url, metricas, hash_conteudo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (fonte_id, oponente_id, txt, autor, autor_id,
         f"2026-06-{18-i:02d}T1{i}:00:00", f"https://exemplo.com/p{i}",
         f'{{"likes": {likes}}}', f"demo-m{i}"),
    )

# Checagens - dados como lista de tuplas para clareza
checagens_data = [
    {
        "texto": "O pais teve crescimento economico de 8% no ultimo ano",
        "sujeito": "pais", "predicado": "teve crescimento de 8%",
        "veredito": "falso", "confianca": 0.92, "fontes": 2,
        "justificativa": "IBGE aponta crescimento de 4.1% no periodo, nao 8%. Divergencia de quase 2x entre o claim e os dados oficiais.",
        "contra": "Crescimento real do PIB foi 4.1% no periodo, nao 8%. Segundo IBGE."
    },
    {
        "texto": "A inflacao acumulada e de 12% segundo o IBGE",
        "sujeito": "inflacao", "predicado": "e 12%",
        "veredito": "verdadeiro", "confianca": 0.85, "fontes": 2,
        "justificativa": "IBGE confirma IPCA acumulado de 12.3% no periodo. Dados corroboram o claim.",
        "contra": "Confirmado: IPCA 12.3% no acumulado. Dados do IBGE corroboram."
    },
    {
        "texto": "O desemprego caiu pela metade desde 2022",
        "sujeito": "desemprego", "predicado": "caiu pela metade",
        "veredito": "enganoso", "confianca": 0.78, "fontes": 2,
        "justificativa": "Taxa de desemprego caiu 18%, nao 50%. Claim exagera o efeito da politica economica.",
        "contra": "Desemprego caiu 18%, nao metade. Cuidado com exageros em declaracoes economicas."
    },
    {
        "texto": "Vamos aumentar o salario minimo em 20%",
        "sujeito": "salario minimo", "predicado": "aumentar 20%",
        "veredito": "sem_contexto", "confianca": 0.65, "fontes": 1,
        "justificativa": "Claim sobre intencao futura, nao fato verificavel. Aguardar proposta formal.",
        "contra": "Aguardar proposta concreta antes de checar viabilidade do aumento."
    },
    {
        "texto": "O IDH do Brasil e o maior da historia",
        "sujeito": "IDH", "predicado": "maior da historia",
        "veredito": "impreciso", "confianca": 0.72, "fontes": 2,
        "justificativa": "IDH de 2022 e 0.760, similar a 2019. Claim e simplista - houve oscilacoes.",
        "contra": "IDH variou entre 0.754 e 0.760 - nao houve melhora sem precedentes como sugere o claim."
    },
    {
        "texto": "Investimento em educacao triplicou no meu mandato",
        "sujeito": "educacao", "predicado": "triplicou",
        "veredito": "falso", "confianca": 0.88, "fontes": 2,
        "justificativa": "Investimento em educacao subiu 47% em valores nominais, nao triplicou. Sem correcao monetaria, ainda menos.",
        "contra": "Investimento em educacao subiu 47% (nominal), nao triplicou. Pedir fontes para o claim."
    },
    {
        "texto": "A violencia caiu 40% nas grandes cidades",
        "sujeito": "violencia", "predicado": "caiu 40%",
        "veredito": "enganoso", "confianca": 0.81, "fontes": 2,
        "justificativa": "Atlas da Violencia mostra reducao de 12% em medias nas grandes cidades, nao 40%. Claim exagera.",
        "contra": "Reducao real foi 12%, nao 40%. Atlas da Violencia 2024 tem os dados oficiais."
    },
]

for ch in checagens_data:
    af = conn.execute(
        "INSERT INTO afirmacoes (mencao_id, texto, sujeito, predicado, checavel, confianca_extracao) "
        "VALUES (?, ?, ?, ?, 1, 0.9)",
        (mencao_id, ch["texto"], ch["sujeito"], ch["predicado"]),
    )
    af_id = af.lastrowid
    if ch["fontes"] >= 2:
        ev = '[{"fonte": "IBGE", "trecho": "Dados oficiais do IBGE 2024 confirmam outro valor", "url": "https://ibge.gov.br/censo"}, {"fonte": "FGV", "trecho": "Estudo independente corrobora o dado do IBGE", "url": "https://fgv.br/estudo"}]'
    else:
        ev = '[{"fonte": "Midia X", "trecho": "Reportagem sem dados primarios verificaveis", "url": null}]'
    conn.execute(
        "INSERT INTO checagens (afirmacao_id, veredito, evidencias, fontes_independentes, confianca, justificativa, contraposicao_sugerida, modelo) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, 'gemini')",
        (af_id, ch["veredito"], ev, ch["fontes"], ch["confianca"], ch["justificativa"], ch["contra"]),
    )

# Alertas
alerts = [
    ("alto", "Claim falso detectado: crescimento de 8%"),
    ("alto", "Claim falso detectado: educacao triplicou"),
    ("medio", "Claim enganoso: violencia caiu 40%"),
    ("alto", "Claim falso: IDH maior da historia"),
    ("medio", "Claim impreciso: inflacao 12%"),
]
for sev, titulo in alerts:
    conn.execute(
        "INSERT INTO alertas (modulo, severidade, titulo, payload, enviado_telegram, criado_em) "
        "VALUES ('veritas', ?, ?, '{\"id\": 1}', 1, datetime('now', ?))",
        (sev, titulo, "-2 hours"),
    )

# Scheduler log
for i, job in enumerate(["veritas_check", "veritas_seed", "recover_stuck_jobs", "veritas_check"]):
    conn.execute(
        "INSERT INTO scheduler_log (job, executado_em) VALUES (?, datetime('now', ?))",
        (job, f"-{i*3} hours"),
    )

# Briefing
conn.execute(
    "INSERT INTO briefings (modulo, periodo, conteudo_md) "
    "VALUES ('veritas', '2026-06-18', "
    "'# Briefing diario 18/06/2026\\n\\n"
    "**7 checagens processadas.**\\n\\n"
    "- 3 claims falsos\\n- 2 enganosos\\n- 1 impreciso\\n- 1 verdadeiro\\n\\n"
    "**Alertas enviados:** 5 via Telegram\\n\\n"
    "**Topico do dia:** crescimento economico inflado em declaracoes publicas.')"
)

conn.commit()
conn.close()

conn = get_db()
print("Checagens:", conn.execute("SELECT COUNT(*) c FROM checagens").fetchone()["c"])
print("Alertas:", conn.execute("SELECT COUNT(*) c FROM alertas").fetchone()["c"])
print("Mencoes:", conn.execute("SELECT COUNT(*) c FROM mencoes").fetchone()["c"])
print("Briefings:", conn.execute("SELECT COUNT(*) c FROM briefings").fetchone()["c"])
print("Sample data seeded")
