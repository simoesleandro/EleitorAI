CREATE TABLE IF NOT EXISTS candidatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    partido TEXT,
    cargo TEXT NOT NULL,
    alianca TEXT,
    eh_proprio INTEGER DEFAULT 0,
    monitorar_veritas INTEGER DEFAULT 1,
    monitorar_eco INTEGER DEFAULT 1,
    criado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS fontes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    identificador TEXT NOT NULL,
    nome TEXT,
    ativa INTEGER DEFAULT 1,
    coletor TEXT NOT NULL,
    config TEXT,
    ultimo_coleta TEXT,
    UNIQUE(tipo, identificador)
);

CREATE TABLE IF NOT EXISTS mencoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fonte_id INTEGER NOT NULL,
    candidato_id INTEGER,
    texto TEXT NOT NULL,
    autor TEXT,
    autor_id TEXT,
    timestamp TEXT NOT NULL,
    url TEXT,
    metricas TEXT,
    hash_conteudo TEXT NOT NULL UNIQUE,
    coletado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(fonte_id) REFERENCES fontes(id) ON DELETE CASCADE,
    FOREIGN KEY(candidato_id) REFERENCES candidatos(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_mencoes_candidato ON mencoes(candidato_id);
CREATE INDEX IF NOT EXISTS idx_mencoes_timestamp ON mencoes(timestamp);
CREATE INDEX IF NOT EXISTS idx_mencoes_fonte ON mencoes(fonte_id);

CREATE TABLE IF NOT EXISTS afirmacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mencao_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    sujeito TEXT,
    predicado TEXT,
    checavel INTEGER DEFAULT 1,
    confianca_extracao REAL,
    extraido_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(mencao_id) REFERENCES mencoes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    afirmacao_id INTEGER NOT NULL,
    veredito TEXT NOT NULL,
    evidencias TEXT NOT NULL,
    fontes_independentes INTEGER NOT NULL,
    confianca REAL NOT NULL,
    justificativa TEXT,
    contraposicao_sugerida TEXT,
    revisado_humano INTEGER DEFAULT 0,
    modelo TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(afirmacao_id) REFERENCES afirmacoes(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_checagens_veredito ON checagens(veredito);

CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(
    entidade_tipo TEXT,
    entidade_id INTEGER,
    conteudo TEXT,
    embedding FLOAT[768]
);

CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo TEXT NOT NULL,
    severidade TEXT NOT NULL,
    titulo TEXT NOT NULL,
    payload TEXT NOT NULL,
    enviado_telegram INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo TEXT NOT NULL,
    periodo TEXT NOT NULL,
    conteudo_md TEXT NOT NULL,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(modulo, periodo)
);

CREATE TABLE IF NOT EXISTS job_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    payload TEXT,
    status TEXT DEFAULT 'pending',
    resultado TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    iniciado_em TEXT,
    concluido_em TEXT
);
CREATE INDEX IF NOT EXISTS idx_job_queue_status ON job_queue(status);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nome TEXT,
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scheduler_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job TEXT NOT NULL,
    executado_em TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    resultado TEXT
);

CREATE TABLE IF NOT EXISTS narrativas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cluster_id TEXT NOT NULL,
    nome TEXT NOT NULL,
    descricao TEXT,
    volume INTEGER NOT NULL,
    velocidade_crescimento REAL,
    classificacao TEXT NOT NULL,
    confianca_classificacao REAL,
    justificativa_classificacao TEXT,
    primeiro_post_em TEXT,
    criado_em TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS amplificadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    narrativa_id INTEGER NOT NULL,
    identificador TEXT NOT NULL,
    tipo TEXT NOT NULL,
    centralidade REAL,
    suspeita_bot INTEGER DEFAULT 0,
    idade_conta_dias INTEGER,
    FOREIGN KEY(narrativa_id) REFERENCES narrativas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relacoes_amplificacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    narrativa_id INTEGER NOT NULL,
    de_identificador TEXT NOT NULL,
    para_identificador TEXT NOT NULL,
    peso REAL NOT NULL,
    janela_minutos INTEGER,
    tipo TEXT,
    FOREIGN KEY(narrativa_id) REFERENCES narrativas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS debates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    data TEXT NOT NULL,
    stream_url TEXT NOT NULL,
    candidatos_json TEXT NOT NULL,
    status TEXT DEFAULT 'agendado',
    iniciado_em TEXT,
    concluido_em TEXT
);

CREATE TABLE IF NOT EXISTS falas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    debate_id INTEGER NOT NULL,
    indice INTEGER NOT NULL,
    falante TEXT NOT NULL,
    texto TEXT NOT NULL,
    timestamp_inicio REAL,
    timestamp_fim REAL,
    FOREIGN KEY(debate_id) REFERENCES debates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS momentos_virais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fala_id INTEGER NOT NULL,
    afirmacao_id INTEGER,
    falacia TEXT,
    score_impacto REAL NOT NULL,
    score_viralidade REAL NOT NULL,
    score_total REAL NOT NULL,
    sugestao_contraposto TEXT,
    enviado_telegram INTEGER DEFAULT 0,
    criado_em TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(fala_id) REFERENCES falas(id) ON DELETE CASCADE,
    FOREIGN KEY(afirmacao_id) REFERENCES afirmacoes(id) ON DELETE SET NULL
);