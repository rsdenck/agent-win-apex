import os
import re
import subprocess

class LicenseFileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def file_exists(self):
        """Verifica se o arquivo existe no caminho especificado."""
        return os.path.exists(self.file_path)

    def read_file_lines(self):
        """Lê todas as linhas do arquivo com a codificação correta e retorna uma lista de strings."""
        try:
            with open(self.file_path, 'r', encoding='latin1') as license_file:
                return license_file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Erro: O arquivo '{self.file_path}' não foi encontrado.")
        except Exception as error:
            raise Exception(f"Ocorreu um erro inesperado ao ler o arquivo: {str(error)}")


class LicenseUsageAnalyzer:
    def __init__(self, file_lines):
        self.file_lines = file_lines

    def count_licenses(self):
        """Conta o número de licenças disponíveis e em uso a partir das linhas do arquivo."""
        licenses_available = 0
        licenses_in_use = 0
        counting_licenses = False
        unique_sessions = set()  # Conjunto para armazenar combinações únicas (nome, servidor, data/hora)

        for line in self.file_lines:
            line = line.strip()  # Remove espaços extras no início e fim

            # Utilizando regex para capturar o número de licenças disponíveis
            match = re.search(r"Total of (\d+) licenses available", line)
            if match:
                licenses_available = int(match.group(1))

            # Quando encontrar a linha que indica o início das licenças em uso
            if "nodelocked license locked to NOTHING" in line:
                counting_licenses = True
                continue

            # Quando começar a contar as licenças em uso, verificar linhas que começam com "start"
            if counting_licenses and "start" in line:
                # Usar uma expressão regular para capturar o nome, servidor e data/hora
                session_match = re.search(r"(\w+)\s+.+\((.+)\), start (.+)", line)
                if session_match:
                    nome = session_match.group(1)
                    servidor = session_match.group(2)
                    data_hora = session_match.group(3)

                    # Criar uma combinação única (nome, servidor, data/hora)
                    session_id = f"{nome}-{servidor}-{data_hora}"

                    if session_id not in unique_sessions:
                        unique_sessions.add(session_id)
                        licenses_in_use += 1

        return licenses_available, licenses_in_use


def main(metric):
    file_path = r'C:\Zabbix\scripts\appLic.txt'

    # Executar lmutil para gerar o arquivo appLic.txt
    if os.path.exists(file_path):
        os.remove(file_path)

    subprocess.run([r'C:\Zabbix\scripts\lmutil.exe', 'lmstat', '-a', '>', file_path], shell=True)

    # Ler o arquivo gerado
    license_reader = LicenseFileReader(file_path)

    if not license_reader.file_exists():
        raise FileNotFoundError(f"Erro: O arquivo '{file_path}' não foi criado corretamente.")

    file_lines = license_reader.read_file_lines()

    # Analisar o uso de licenças
    license_analyzer = LicenseUsageAnalyzer(file_lines)
    available, in_use = license_analyzer.count_licenses()

    if metric == "available":
        print(available)
    elif metric == "in_use":
        print(in_use)
    else:
        print("Métrica inválida.")


if __name__ == "__main__": 
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])  # Receber 'available' ou 'in_use' como argumento
    else:
        print("Por favor, forneça uma métrica (available ou in_use).")
