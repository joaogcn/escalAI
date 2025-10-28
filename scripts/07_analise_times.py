import requests
import json
import os
import sys
from collections import defaultdict

# Adiciona o diretório raiz ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config import CARTOLA_BASE_URL, VISUALIZATION_DATA_PATH

def run():
    """Gera uma análise de desempenho dos times nas últimas 5 rodadas."""
    print('--- INICIANDO: Análise de Desempenho de Times ---')

    try:
        # 1. Obter o status do mercado para saber a rodada atual e o status
        status_response = requests.get(f"{CARTOLA_BASE_URL}/mercado/status")
        status_data = status_response.json()
        rodada_atual = status_data.get('rodada_atual')
        status_mercado = status_data.get('status_mercado')

        if not rodada_atual:
            print("ERRO: Não foi possível obter a rodada atual.")
            return False

        # Define o range de rodadas para análise (últimas 5 finalizadas)
        # Se o mercado está aberto, a rodada atual ainda não terminou.
        rodada_final = rodada_atual if status_mercado == 2 else rodada_atual - 1
        rodada_inicial = max(1, rodada_final - 4)
        rodadas_para_analisar = range(rodada_inicial, rodada_final + 1)
        print(f"  - Analisando o desempenho dos times entre as rodadas: {rodada_inicial} e {rodada_final}")

        # 2. Coletar dados das partidas e clubes
        all_partidas = []
        clubes = {}
        for rodada in rodadas_para_analisar:
            partidas_response = requests.get(f"{CARTOLA_BASE_URL}/partidas/{rodada}")
            partidas_data = partidas_response.json()
            all_partidas.extend(partidas_data.get('partidas', []))
            clubes.update(partidas_data.get('clubes', {}))
        
        if not all_partidas:
            print("ERRO: Não foi possível obter dados de partidas para as rodadas analisadas.")
            return False

        # 3. Calcular o Índice de Desempenho para cada time
        team_performance = defaultdict(lambda: {'pontos': 0, 'vitorias': 0, 'empates': 0, 'derrotas': 0, 'gols_pro': 0, 'gols_contra': 0, 'jogos': 0})

        for partida in all_partidas:
            if partida.get('placar_oficial_mandante') is None: continue # Ignora partidas não finalizadas

            id_casa = partida['clube_casa_id']
            id_visitante = partida['clube_visitante_id']
            gols_casa = partida['placar_oficial_mandante']
            gols_visitante = partida['placar_oficial_visitante']

            # Atualiza estatísticas básicas
            team_performance[id_casa]['gols_pro'] += gols_casa
            team_performance[id_casa]['gols_contra'] += gols_visitante
            team_performance[id_casa]['jogos'] += 1
            team_performance[id_visitante]['gols_pro'] += gols_visitante
            team_performance[id_visitante]['gols_contra'] += gols_casa
            team_performance[id_visitante]['jogos'] += 1

            # Lógica de pontos por resultado
            if gols_casa > gols_visitante:
                team_performance[id_casa]['pontos'] += 3
                team_performance[id_casa]['vitorias'] += 1
                team_performance[id_visitante]['derrotas'] += 1
            elif gols_visitante > gols_casa:
                team_performance[id_visitante]['pontos'] += 3
                team_performance[id_visitante]['vitorias'] += 1
                team_performance[id_casa]['derrotas'] += 1
            else:
                team_performance[id_casa]['pontos'] += 1
                team_performance[id_casa]['empates'] += 1
                team_performance[id_visitante]['pontos'] += 1

            # Bônus de clean sheet
            if gols_visitante == 0:
                team_performance[id_casa]['pontos'] += 2
            if gols_casa == 0:
                team_performance[id_visitante]['pontos'] += 2

        # 4. Formatar a saída
        output_list = []
        for team_id, stats in team_performance.items():
            output_list.append({
                'nome': clubes[str(team_id)]['nome'],
                'id': team_id,
                'indice_desempenho': stats['pontos'],
                'jogos': stats['jogos'],
                'vitorias': stats['vitorias'],
                'empates': stats['empates'],
                'derrotas': stats['derrotas'],
                'gols_pro': stats['gols_pro'],
                'gols_contra': stats['gols_contra']
            })

        # Ordena pelo índice
        output_list_sorted = sorted(output_list, key=lambda x: x['indice_desempenho'], reverse=True)

        # 5. Salvar o JSON
        output_path = os.path.join(VISUALIZATION_DATA_PATH, 'times_para_ficar_de_olho.json')
        os.makedirs(VISUALIZATION_DATA_PATH, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_list_sorted, f, ensure_ascii=False, indent=4)
        
        print(f"  - Análise de times salva em: {output_path}")
        print("--- SUCESSO: Análise de Desempenho de Times Concluída ---")
        return True

    except requests.exceptions.RequestException as e:
        print(f"ERRO: Falha na comunicação com a API do Cartola. {e}")
        return False
    except Exception as e:
        print(f"ERRO: Ocorreu um erro inesperado. {e}")
        return False

if __name__ == "__main__":
    run()
