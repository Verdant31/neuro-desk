"""
Build script para compilar arquivos AutoHotkey e empacotar o projeto Python.

Este script:
1. Compila arquivos .ahk em executáveis
2. Copia bibliotecas e prompts para o destino
3. Converte main.py para executável
4. Move arquivos de configuração e assets
"""

import os
import shutil
import subprocess
import sys
from glob import glob


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Caminhos do AutoHotkey
A2EXE_PATH = 'C:/Programming/AutoHotkey/Compiler/Ahk2Exe.exe'
BASE_FILE = r'C:\\Programming\\AutoHotkey\\v2\\AutoHotkey64.exe'

# Diretórios do projeto e build
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
BUILD_DIR = os.path.join(PROJECT_ROOT, 'build')
OBFUSCATED_DIR = os.path.join(BUILD_DIR, 'obf')

# Diretórios de origem
SOURCE_DIRS = {
    'modules': './modules',
    'lib': './lib',
    'prompts': './prompts',
    'assets': './assets'
}

# Diretórios de destino
DEST_DIRS = {
    'modules': '../app/src-tauri/resources/binaries',
    'lib': '../app/src-tauri/resources/lib',
    'prompts': '../app/src-tauri/resources/prompts',
    'main_exe': '../app/src-tauri/resources/',
    'assets': '../app/src-tauri/resources/assets'
}

# Configurações do executável principal
MAIN_PY = 'main.py'
MAIN_EXE_NAME = 'main-x86_64-pc-windows-msvc.exe'


# Arquivos para copiar
FILES_TO_COPY = [
    ('settings.json', 'settings.json'),
    ('.auth_cache', '.auth_cache')
]


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def create_directories():
    """Cria todos os diretórios de destino necessários."""
    for dest_dir in DEST_DIRS.values():
        os.makedirs(dest_dir, exist_ok=True)
        print(f'Diretório criado/verificado: {dest_dir}')


def compile_ahk_files():
    """Compila todos os arquivos .ahk em executáveis."""
    print('\n=== COMPILANDO ARQUIVOS AUTOHOTKEY ===')

    ahk_files = glob(os.path.join(SOURCE_DIRS['modules'], '*.ahk'))

    for ahk_file in ahk_files:
        exe_name = os.path.splitext(os.path.basename(ahk_file))[0] + '.exe'

        # Destinos para o executável
        tauri_exe_path = os.path.join(DEST_DIRS['modules'], exe_name)
        binaries_exe_path = os.path.join('./binaries', exe_name)

        print(f'Compilando {os.path.basename(ahk_file)}...')

        try:
            # Compila para o diretório do Tauri
            _compile_single_ahk(ahk_file, tauri_exe_path)

            # Compila para o diretório binaries
            _compile_single_ahk(ahk_file, binaries_exe_path)

            print(f'✓ Compilação concluída: {exe_name}')

        except subprocess.CalledProcessError as e:
            print(
                f'✗ Falha na compilação de {os.path.basename(ahk_file)}: {e}')
        except Exception as e:
            print(
                f'✗ Erro inesperado ao compilar {os.path.basename(ahk_file)}: {e}')


def _compile_single_ahk(ahk_file, output_path):
    """Compila um único arquivo .ahk para o caminho especificado."""
    subprocess.run([
        A2EXE_PATH,
        '/in', ahk_file,
        '/out', output_path,
        '/base', BASE_FILE
    ], check=True)


# -----------------------------
# Ofuscação de código Python
# -----------------------------

def _list_root_python_files():
    """Lista arquivos .py no diretório raiz do projeto que devem ser ofuscados."""
    root_files = []
    for name in os.listdir(PROJECT_ROOT):
        path = os.path.join(PROJECT_ROOT, name)
        if os.path.isfile(path) and name.endswith('.py') and name not in {'build.py'}:
            root_files.append(path)
    return root_files


def obfuscate_python_sources():
    """Ofusca os arquivos Python do projeto preservando a estrutura de pastas.

    Gera uma árvore ofuscada em BUILD_DIR/obf e mantém os pacotes (ex.: helpers) intactos
    para evitar que imports quebrem. Usa o Python atual (venv) para executar o PyArmor.
    """
    print('\n=== OFUSCANDO CÓDIGO PYTHON (PYARMOR) ===')

    # Preparar diretório de saída
    if os.path.exists(OBFUSCATED_DIR):
        shutil.rmtree(OBFUSCATED_DIR)
        print(f'Removido diretório existente: {OBFUSCATED_DIR}')
    os.makedirs(OBFUSCATED_DIR, exist_ok=True)

    # Alvos para ofuscar: arquivos .py na raiz + pacotes relevantes (helpers)
    targets = _list_root_python_files()
    helpers_dir = os.path.join(PROJECT_ROOT, 'helpers')
    if os.path.isdir(helpers_dir):
        targets.append(helpers_dir)

    if not targets:
        print('⚠ Nenhum arquivo/diretório Python encontrado para ofuscação.')
        return False

    # Comando do PyArmor: gerar saída preservando estrutura
    # Nota: usamos sys.executable para garantir o venv correto
    cmd = [
        sys.executable, '-m', 'pyarmor.cli', '--silent', 'gen',
        '-O', OBFUSCATED_DIR,
        '-r',
        *targets
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f'✓ Código ofuscado em: {OBFUSCATED_DIR}')
        return True
    except FileNotFoundError:
        print('✗ PyArmor não encontrado. Instale com: pip install pyarmor')
        raise
    except subprocess.CalledProcessError as e:
        print(f'✗ Falha ao ofuscar com PyArmor: {e}')
        raise


def copy_directory_tree(src_key, dst_key, description):
    """Copia uma árvore de diretórios, removendo o destino se existir."""
    src_dir = SOURCE_DIRS[src_key]
    dst_dir = DEST_DIRS[dst_key]

    print(f'\n=== COPIANDO {description.upper()} ===')

    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
        print(f'Removido diretório existente: {dst_dir}')

    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dst_dir)
        print(f'✓ Copiado {src_dir} -> {dst_dir}')
    else:
        print(f'⚠ Diretório não encontrado: {src_dir}')


def build_python_executable():
    """Converte main.py em executável usando PyInstaller após ofuscação."""
    print('\n=== CONVERTENDO PYTHON PARA EXECUTÁVEL ===')

    # Empacotar com PyInstaller a partir do código ofuscado
    main_obf = os.path.join(OBFUSCATED_DIR, 'main.py')
    if not os.path.exists(main_obf):
        # fallback para o main original caso a ofuscação não tenha gerado main.py
        main_obf = os.path.join(PROJECT_ROOT, 'main.py')
        print('⚠ main.py ofuscado não encontrado. Usando main.py original.')

    dist_abs = os.path.join(PROJECT_ROOT, 'dist')
    os.makedirs(dist_abs, exist_ok=True)

    # Incluir runtime do PyArmor como dados, se existir
    runtime_glob = glob(os.path.join(OBFUSCATED_DIR, 'pyarmor_runtime_*'))
    runtime_add_data = []
    if runtime_glob:
        runtime_dir = runtime_glob[0]
        # Formato do PyInstaller no Windows: SRC;DEST
        runtime_add_data = ['--add-data', f"{runtime_dir};."]

    # Incluir módulos ofuscados como hidden-import (PyInstaller pode não detectar via análise estática)
    hidden_imports = []
    try:
        for fname in os.listdir(OBFUSCATED_DIR):
            if fname.endswith('.py') and fname != 'main.py':
                mod = os.path.splitext(fname)[0]
                hidden_imports += ['--hidden-import', mod]
    except FileNotFoundError:
        pass

    # Hidden imports adicionais (dependências de runtime comuns)
    third_party_mods = [
        'speech_recognition', 'pyaudio', 'tqdm',
        'langchain', 'langchain_core', 'langchain_openai', 'langchain_ollama',
        'langgraph', 'langsmith', 'tiktoken', 'openai',
        'playsound'
    ]
    for mod in third_party_mods:
        hidden_imports += ['--hidden-import', mod]

    # Garantir inclusão completa dos pacotes (dados, submódulos)
    collect_helpers = ['--collect-all', 'helpers']
    collect_third_party = []
    for mod in third_party_mods:
        collect_third_party += ['--collect-all', mod]

    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--name', 'main',
            '--distpath', dist_abs,
            '--log-level', 'ERROR',
            '--paths', OBFUSCATED_DIR,
            *hidden_imports,
            *collect_helpers,
            *collect_third_party,
            *runtime_add_data,
            main_obf
        ]
        subprocess.run(cmd, check=True)

        print('✓ PyInstaller executado com sucesso')

    except subprocess.CalledProcessError as e:
        print(f'✗ Falha no PyInstaller: {e}')
        raise


def move_main_executable():
    """Move o executável principal para o destino correto."""
    print('\n=== MOVENDO EXECUTÁVEL PRINCIPAL ===')

    main_exe_src = os.path.join(PROJECT_ROOT, 'dist', 'main.exe')
    main_exe_dst = os.path.join(DEST_DIRS['main_exe'], MAIN_EXE_NAME)

    if os.path.exists(main_exe_src):
        shutil.move(main_exe_src, main_exe_dst)
        print(f'✓ Movido {main_exe_src} -> {main_exe_dst}')
    else:
        print('✗ main.exe não encontrado em dist/. Build pode ter falhado.')


def copy_configuration_files():
    """Copia arquivos de configuração para o destino."""
    print('\n=== COPIANDO ARQUIVOS DE CONFIGURAÇÃO ===')

    for src_file, dst_file in FILES_TO_COPY:
        src_path = src_file
        dst_path = os.path.join(DEST_DIRS['main_exe'], dst_file)

        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f'✓ Copiado {src_path} -> {dst_path}')
        else:
            print(f'⚠ Arquivo não encontrado: {src_path}. Pulando...')


def copy_assets():
    """Copia assets para o destino, removendo destino existente se necessário."""
    print('\n=== COPIANDO ASSETS ===')

    src_dir = SOURCE_DIRS['assets']
    dst_dir = DEST_DIRS['assets']

    # Remove destino se existir
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
        print(f'Removido diretório existente: {dst_dir}')

    # Copia se origem existir
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dst_dir)
        print(f'✓ Copiado {src_dir} -> {dst_dir}')
    else:
        print(f'⚠ Diretório não encontrado: {src_dir}')


def cleanup_temp_artifacts():
    """Remove diretórios/arquivos temporários: dist, build e main.spec."""
    print('\n=== LIMPANDO ARTEFATOS TEMPORÁRIOS ===')

    targets = [
        os.path.join(PROJECT_ROOT, 'dist'),
        os.path.join(PROJECT_ROOT, 'build'),
        os.path.join(PROJECT_ROOT, 'main.spec'),
    ]

    for path in targets:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f'✓ Removido diretório: {path}')
            elif os.path.isfile(path):
                os.remove(path)
                print(f'✓ Removido arquivo: {path}')
            else:
                print(f'• Não encontrado: {path}')
        except Exception as e:
            print(f'⚠ Falha ao remover {path}: {e}')


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Executa todo o processo de build."""
    print('🚀 INICIANDO PROCESSO DE BUILD')
    print('=' * 50)

    try:
        # 1. Criar diretórios necessários
        create_directories()

        # 2. Compilar arquivos AutoHotkey
        compile_ahk_files()

        # 3. Copiar bibliotecas
        copy_directory_tree('lib', 'lib', 'bibliotecas')

        # 4. Copiar prompts
        copy_directory_tree('prompts', 'prompts', 'prompts')

        # Ofuscar código Python
        obfuscate_python_sources()

        # 5. Construir executável Python
        build_python_executable()

        # 6. Mover executável principal
        move_main_executable()

        # 7. Copiar arquivos de configuração
        copy_configuration_files()

        # 8. Copiar assets
        copy_assets()

        print('\n' + '=' * 50)
        print('✅ BUILD CONCLUÍDO COM SUCESSO!')

    except Exception as e:
        print('\n' + '=' * 50)
        print(f'❌ BUILD FALHOU: {e}')
        raise
    finally:
        cleanup_temp_artifacts()


if __name__ == '__main__':
    main()
