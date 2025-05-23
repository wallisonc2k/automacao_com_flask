import os
import sys
import socket

DEBUG = False  # Desabilitar em produção

def get_database_path():
    """Retorna o caminho do banco de dados no diretório do executável"""
    if getattr(sys, 'frozen', False):
        # Se está rodando como executável
        exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, 'database.db')
    else:
        # Se está rodando em desenvolvimento
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(BASE_DIR, 'database.db')

# Usar a função para definir o caminho do banco
SQLALCHEMY_DATABASE_URI = f"sqlite:///{get_database_path()}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

def get_local_ip():
    """Obter IP local da máquina"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip