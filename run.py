#!/usr/bin/env python3
import os
import sys

# Adicionar o diretório do projeto ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import app

if __name__ == '__main__':
    # Verificar se está rodando como executável
    if getattr(sys, 'frozen', False):
        print("Executando como executável standalone")
        print(f"Diretório do executável: {os.path.dirname(sys.executable)}")
    else:
        print("Executando em modo desenvolvimento")
    
    # Executar aplicação
    app.run(host='0.0.0.0', port=5000, debug=True)