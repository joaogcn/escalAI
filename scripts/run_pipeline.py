import importlib
import time
import sys
import os

sys.path.append(os.path.dirname(__file__))

PIPELINE_SCRIPTS = [
    '01_limpeza',
    '02_verificacao',
    '03_analise_descritiva',
    '04_exploracao',
    '05_agregacao'
]

def main():
    """
    Orquestrador principal do pipeline de dados.
    Executa cada script do pipeline em sequência e para se algum falhar.
    """
    print("==================================================")
    print("INICIANDO PIPELINE DE DADOS COMPLETO...")
    print("==================================================")
    start_time = time.time()

    for script_name in PIPELINE_SCRIPTS:
        try:
            script_module = importlib.import_module(script_name)
            
            success = script_module.run()
            
            if not success:
                print(f"\nERRO FATAL: O script '{script_name}' falhou. Abortando o pipeline.")
                return
        except ImportError as e:
            print(f"\nERRO FATAL: Não foi possível importar o script '{script_name}'. Detalhe: {e}")
            return
        except Exception as e:
            print(f"\nERRO FATAL: Ocorreu um erro inesperado ao executar '{script_name}'. Detalhe: {e}")
            return

    end_time = time.time()
    total_time = end_time - start_time
    print("\n==================================================")
    print(f"PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f"Tempo total de execução: {total_time:.2f} segundos.")
    print("==================================================")

if __name__ == "__main__":
    main()
