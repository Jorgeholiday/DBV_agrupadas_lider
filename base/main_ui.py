# base/main_ui.py

import sys
import os
import subprocess
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QComboBox, QPushButton, QTextEdit, QTabWidget, QRadioButton
)
from PyQt6.QtCore import QThread, pyqtSignal, QObject

def kill_process_by_pid(pid, log_callback):
    """Tenta forçar a finalização de um processo pelo seu PID usando comandos do sistema."""
    log_callback(f"Último recurso: Tentando matar o processo com PID {pid} via comando do sistema.")
    try:
        if sys.platform == "win32":
            # /F para forçar, /T para matar processos filhos
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], check=True, capture_output=True)
        else:
            # -9 é o sinal SIGKILL, o mais forte
            subprocess.run(['kill', '-9', str(pid)], check=True, capture_output=True)
        log_callback(f"Comando de finalização forçada para o PID {pid} enviado com sucesso.")
    except Exception as e:
        log_callback(f"Falha ao tentar a finalização forçada via comando do sistema: {e}")

# --- Worker para rodar UM script externo ---
class ScriptRunnerWorker(QObject):
    progress_log = pyqtSignal(str)
    finished = pyqtSignal()
    process = None
    pid = None

    def __init__(self, command):
        super().__init__()
        self.command = command
        
    def run(self):
        try:
            self.progress_log.emit(f"--- Iniciando comando: {' '.join(self.command)} ---")
            # creationflags esconde a janela do console no Windows
            self.process = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', bufsize=1, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            self.pid = self.process.pid
            self.progress_log.emit(f"Processo iniciado com PID: {self.pid}")

            for line in iter(self.process.stdout.readline, ''):
                self.progress_log.emit(line.strip())
            
            self.process.stdout.close()
            self.process.wait()
        except Exception as e:
            self.progress_log.emit(f"ERRO INESPERADO: {e}")
        finally:
            self.progress_log.emit(f"--- Script finalizado (naturalmente ou por interrupção). ---")
            self.finished.emit()
            
    def stop(self):
        if self.process and self.pid:
            self.progress_log.emit(f"--- PARADA DE EMERGÊNCIA ACIONADA PARA O PID {self.pid} ---")
            try:
                # Ação 1: O método kill(), muito mais forte que terminate()
                self.progress_log.emit("Tentativa 1: Usando process.kill()")
                self.process.kill()
            except Exception as e:
                self.progress_log.emit(f"process.kill() falhou: {e}")
            
            # Ação 2: O método final, usando comandos do sistema
            kill_process_by_pid(self.pid, self.progress_log.emit)

# --- Worker para a automação MEGA GERAL ---
class MegaGeralWorker(QObject):
    progress_log = pyqtSignal(str)
    finished = pyqtSignal()
    is_running = True
    process = None
    pid = None

    def __init__(self, usuarios_comuns):
        super().__init__()
        self.usuarios = usuarios_comuns

    def run_single_command(self, command):
        if not self.is_running: return
        self.progress_log.emit(f"--- Executando: {' '.join(command)} ---")
        try:
            self.process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', bufsize=1, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            )
            self.pid = self.process.pid
            self.progress_log.emit(f"Processo iniciado com PID: {self.pid}")

            for line in iter(self.process.stdout.readline, ''):
                if not self.is_running: break
                self.progress_log.emit(line.strip())
            
            self.process.stdout.close()
            if self.is_running: # Só espera se não foi interrompido
                self.process.wait()
        except Exception as e:
            self.progress_log.emit(f"ERRO durante a execução: {e}")

    def run(self):
        total_users = len(self.usuarios)
        for i, user in enumerate(self.usuarios):
            if not self.is_running: break
            
            self.progress_log.emit("\n" + "="*70 + f"\nINICIANDO MEGA GERAL PARA: {user['nome'].upper()} ({i+1}/{total_users})\n" + "="*70)

            self.run_single_command([sys.executable, 'lider_automacao.py', str(user['lider_index']), '1'])
            if not self.is_running: break
            self.run_single_command([sys.executable, 'lider_automacao.py', str(user['lider_index']), '2'])
            if not self.is_running: break
            self.run_single_command([sys.executable, 'agrupadas_orquestrador.py', user['nome'], user['codigo'], user['email'], user['ano']])
            
        if not self.is_running:
            self.progress_log.emit("--- Automação Mega Geral INTERROMPIDA PELO USUÁRIO. ---")
        
        self.finished.emit()

    def stop(self):
        self.is_running = False # Interrompe o loop principal
        if self.process and self.pid:
            self.progress_log.emit(f"--- PARADA DE EMERGÊNCIA ACIONADA PARA O PID {self.pid} ---")
            try:
                self.progress_log.emit("Tentativa 1: Usando process.kill()")
                self.process.kill()
            except Exception as e:
                self.progress_log.emit(f"process.kill() falhou: {e}")

            kill_process_by_pid(self.pid, self.progress_log.emit)

# --- Janela Principal da Aplicação ---
class MainWindow(QWidget):
    # ... (o resto da classe MainWindow permanece o mesmo da resposta anterior)
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None
        self.init_ui()

    def carregar_usuarios_de_csv(self, nome_arquivo_csv):
        usuarios = []
        try:
            caminho_csv = os.path.join("db", nome_arquivo_csv)
            with open(caminho_csv, mode='r', encoding='utf-8', newline='') as f:
                leitor = csv.DictReader(f)
                for row in leitor:
                    usuarios.append(row)
            return usuarios
        except FileNotFoundError:
            self.update_log(f"AVISO: Arquivo de grupo '{nome_arquivo_csv}' não encontrado.")
            return []

    def init_ui(self):
        self.setWindowTitle("Orquestrador de Automação - Desbravadores")
        self.setGeometry(100, 100, 800, 600)
        
        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # --- Aba 1: Líder ---
        self.tab_lider = QWidget()
        lider_layout = QVBoxLayout()
        self.lider_combo_usuarios = QComboBox()
        usuarios_lider = self.carregar_usuarios_de_csv("grupo-lider.csv")
        for i, usuario in enumerate(usuarios_lider):
            self.lider_combo_usuarios.addItem(usuario['nome'], i + 1)
        self.lider_radio_texto = QRadioButton("Requisitos SEM anexo de PDF", self)
        self.lider_radio_pdf = QRadioButton("Requisitos COM anexo de PDF", self)
        self.lider_radio_texto.setChecked(True)
        self.btn_iniciar_lider = QPushButton("Iniciar Automação do Líder")
        self.btn_iniciar_lider.setStyleSheet("background-color: #007BFF; color: white; padding: 10px;")
        lider_layout.addWidget(QLabel("Selecione o Usuário do Grupo de Líder:"))
        lider_layout.addWidget(self.lider_combo_usuarios)
        lider_layout.addWidget(self.lider_radio_texto); lider_layout.addWidget(self.lider_radio_pdf)
        lider_layout.addWidget(self.btn_iniciar_lider)
        self.tab_lider.setLayout(lider_layout)

        # --- Aba 2: Agrupadas ---
        self.tab_agrupadas = QWidget()
        agrupadas_layout = QVBoxLayout()
        self.agrupadas_combo_usuarios = QComboBox()
        usuarios_agrupadas = self.carregar_usuarios_de_csv("grupo-agrupadas.csv")
        for usuario in usuarios_agrupadas:
            self.agrupadas_combo_usuarios.addItem(usuario['nome'], usuario) 
        self.btn_iniciar_agrupadas = QPushButton("Iniciar Automação para Usuário Selecionado")
        self.btn_iniciar_agrupadas.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        agrupadas_layout.addWidget(QLabel("Selecione o Usuário do Grupo de Classes Agrupadas:"))
        agrupadas_layout.addWidget(self.agrupadas_combo_usuarios)
        agrupadas_layout.addWidget(self.btn_iniciar_agrupadas)
        self.tab_agrupadas.setLayout(agrupadas_layout)

        # --- Aba 3: Mega Geral ---
        self.tab_mega = QWidget()
        mega_layout = QVBoxLayout()
        label_aviso_mega = QLabel("<b>Atenção:</b> Esta ação executará a automação <b>COMPLETA</b> (Líder e Agrupadas) para todos os usuários que estiverem presentes em <b>AMBOS</b> os arquivos CSV. O processo pode demorar bastante.")
        label_aviso_mega.setWordWrap(True)
        self.btn_iniciar_mega = QPushButton("!! INICIAR MEGA GERAL !!")
        self.btn_iniciar_mega.setStyleSheet("background-color: #dc3545; color: white; padding: 10px; font-size: 16px; font-weight: bold;")
        mega_layout.addWidget(label_aviso_mega)
        mega_layout.addWidget(self.btn_iniciar_mega)
        self.tab_mega.setLayout(mega_layout)

        # Adicionando as abas
        self.tabs.addTab(self.tab_lider, "Cartão de Líder")
        self.tabs.addTab(self.tab_agrupadas, "Classes Agrupadas")
        self.tabs.addTab(self.tab_mega, "⚡ Mega Geral ⚡")

        # Widgets Comuns
        self.log_area = QTextEdit(); self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #dcdcdc; font-family: 'Consolas';")
        self.btn_parar = QPushButton("PARAR AUTOMAÇÃO (EMERGÊNCIA)")
        self.btn_parar.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        self.btn_parar.setEnabled(False)

        main_layout.addWidget(self.tabs)
        main_layout.addWidget(QLabel("Log de Atividades:"))
        main_layout.addWidget(self.log_area)
        main_layout.addWidget(self.btn_parar)
        self.setLayout(main_layout)

        # Conectar sinais
        self.btn_iniciar_lider.clicked.connect(self.iniciar_automacao_lider)
        self.btn_iniciar_agrupadas.clicked.connect(self.iniciar_automacao_agrupadas)
        self.btn_iniciar_mega.clicked.connect(self.iniciar_mega_geral)
        self.btn_parar.clicked.connect(self.parar_automacao)

    def preparar_para_rodar(self):
        self.log_area.clear()
        self.set_buttons_enabled(False)
        self.btn_parar.setEnabled(True)
        self.btn_parar.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; font-weight: bold;")
        
    def set_buttons_enabled(self, enabled):
        self.btn_iniciar_lider.setEnabled(enabled)
        self.btn_iniciar_agrupadas.setEnabled(enabled)
        self.btn_iniciar_mega.setEnabled(enabled)
        self.tabs.setEnabled(enabled)

    def iniciar_automacao_lider(self):
        usuario_choice = str(self.lider_combo_usuarios.currentData())
        modo_choice = "2" if self.lider_radio_pdf.isChecked() else "1"
        command = [sys.executable, 'lider_automacao.py', usuario_choice, modo_choice]
        self.run_generic_script(command)

    def iniciar_automacao_agrupadas(self):
        usuario = self.agrupadas_combo_usuarios.currentData()
        if not usuario: return
        command = [sys.executable, 'agrupadas_orquestrador.py', usuario['nome'], usuario['codigo'], usuario['email'], usuario['ano']]
        self.run_generic_script(command)

    def iniciar_mega_geral(self):
        self.preparar_para_rodar()
        
        usuarios_lider = self.carregar_usuarios_de_csv("grupo-lider.csv")
        usuarios_agrupadas = self.carregar_usuarios_de_csv("grupo-agrupadas.csv")
        
        codigos_agrupadas = {u['codigo']: u for u in usuarios_agrupadas}
        usuarios_comuns = []
        for idx, user_lider in enumerate(usuarios_lider):
            if user_lider['codigo'] in codigos_agrupadas:
                user_lider['lider_index'] = idx + 1
                usuarios_comuns.append(user_lider)

        if not usuarios_comuns:
            self.update_log("Nenhum usuário em comum encontrado.")
            self.automacao_finalizada()
            return
            
        self.update_log(f"Encontrados {len(usuarios_comuns)} usuários em comum. Iniciando...")
        
        self.thread = QThread()
        self.worker = MegaGeralWorker(usuarios_comuns)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.automacao_finalizada_thread)
        self.worker.progress_log.connect(self.update_log)
        self.thread.start()

    def run_generic_script(self, command):
        self.preparar_para_rodar()
        self.thread = QThread()
        self.worker = ScriptRunnerWorker(command)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.automacao_finalizada_thread)
        self.worker.progress_log.connect(self.update_log)
        self.thread.start()

    def parar_automacao(self):
        self.btn_parar.setText("FORÇANDO PARADA...")
        self.btn_parar.setEnabled(False)
        if self.worker:
            self.worker.stop()

    def update_log(self, message):
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def automacao_finalizada_thread(self):
        if self.thread: self.thread.quit()
        if self.worker: self.worker.deleteLater()
        if self.thread: self.thread.deleteLater()
        self.worker = None
        self.thread = None
        self.automacao_finalizada()

    def automacao_finalizada(self):
        self.set_buttons_enabled(True)
        self.btn_parar.setEnabled(False)
        self.btn_parar.setText("PARAR AUTOMAÇÃO (EMERGÊNCIA)")
        self.btn_parar.setStyleSheet("background-color: #6c757d; color: white; padding: 8px;")
        if "INTERROMPIDA" not in self.log_area.toPlainText():
             self.log_area.append("\n--- PROCESSO FINALIZADO. PRONTO PARA A PRÓXIMA TAREFA. ---")
             
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())