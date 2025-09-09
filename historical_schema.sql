-- ESQUEMA OTIMIZADO PARA DADOS HISTÓRICOS

-- Tabela de clubes
CREATE TABLE IF NOT EXISTS clubes (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    abreviacao VARCHAR(10)
);

-- Tabela de jogadores (otimizada para dados históricos)
CREATE TABLE IF NOT EXISTS jogadores (
    id SERIAL PRIMARY KEY,
    atleta_id INTEGER,
    rodada_id INTEGER,
    temporada INTEGER,
    clube_id INTEGER REFERENCES clubes(id),
    posicao VARCHAR(50),
    status VARCHAR(50),
    pontos_num DECIMAL(10,2),
    preco_num DECIMAL(10,2),
    variacao_num DECIMAL(10,2),
    media_num DECIMAL(10,2),
    jogos_num INTEGER,
    apelido VARCHAR(100),
    nome VARCHAR(255)
);

-- Índices otimizados
CREATE INDEX IF NOT EXISTS idx_jogadores_clube ON jogadores(clube_id);
CREATE INDEX IF NOT EXISTS idx_jogadores_posicao ON jogadores(posicao);
CREATE INDEX IF NOT EXISTS idx_jogadores_status ON jogadores(status);
CREATE INDEX IF NOT EXISTS idx_jogadores_atleta_id ON jogadores(atleta_id);
CREATE INDEX IF NOT EXISTS idx_jogadores_rodada_id ON jogadores(rodada_id);
CREATE INDEX IF NOT EXISTS idx_jogadores_temporada ON jogadores(temporada);
