import tkinter as tk
from tkinter import ttk, messagebox
import pyaudio
import wave
import threading
import os 
import numpy as np
from queue import Queue
import time                 
from PIL import ImageGrab, Image # Importação corrigida: incluímos 'Image'
import ctypes 

# Importa a função "cérebro" do arquivo analise.py
from analise import analisar_audio

class AppAnalisadorDeVoz:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador de Tom de Voz")
        self.root.geometry("400x420") 
        
        # Estado da Aplicação
        self.app_state = "IDLE" 
        self.current_session_type = "Antes"
        self.countdown_job = None 
        
        self.nome_participante = tk.StringVar()
        
        # Configuração de Áudio
        self.mic_map = {} 
        self.selected_mic_name = tk.StringVar()
        self.mic_names = self.carregar_lista_mics() 

        self.is_recording = False
        self.frames = []
        self.audio_queue = Queue() # Fila para o VU Meter
        
        self.current_participant_folder = None 
        
        self.criar_menu_superior() 
        self.criar_widgets()
        
        # Pré-seleciona o primeiro microfone se disponível
        if self.mic_names:
            self.selected_mic_name.set(self.mic_names[0])

    def carregar_lista_mics(self):
        """Lista os microfones disponíveis no sistema."""
        print("Carregando dispositivos de áudio...")
        self.mic_map = {}
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        mic_names = []
        for i in range(0, num_devices):
            device = p.get_device_info_by_host_api_device_index(0, i)
            if (device.get('maxInputChannels')) > 0:
                device_name = device.get('name')
                mic_names.append(device_name)
                self.mic_map[device_name] = i 
                print(f"Encontrado Mic: {device_name} (Índice: {i})")
        p.terminate()
        return mic_names

    def criar_menu_superior(self):
        """Cria a barra de menus."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar) 
        menu_ajuda = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre as Métricas", command=self.mostrar_dialogo_metricas)
        menu_ajuda.add_separator() 
        menu_ajuda.add_command(label="Créditos", command=self.mostrar_dialogo_creditos)
    
    def mostrar_dialogo_creditos(self):
        messagebox.showinfo(
            "Créditos",
            "Analisador de Tom de Voz - Versão 1.0\n\n"
            "Desenvolvido para a disciplina de Computação Afetiva.\n"
            "Autores: Luís Henrique e Maria Antonia.\n"
            "Orientação: Prof. Raul Paradeda."
        )

    def mostrar_dialogo_metricas(self):
        texto = (
            "SIGNIFICADO DAS MÉTRICAS:\n\n"
            "• Pitch (Variação): A 'melodia' da fala. Variação alta = Engajamento. Variação baixa = Monotonia.\n\n"
            "• Jitter: Instabilidade na frequência. Valores altos indicam tremor ou nervosismo.\n\n"
            "• Shimmer: Instabilidade no volume. Indica rouquidão ou tensão vocal.\n\n"
            "• Ritmo: Sílabas por segundo. Muito rápido = Ansiedade. Muito lento = Hesitação."
        )
        messagebox.showinfo("Sobre as Métricas", texto)

    def criar_widgets(self):
        """Constrói a interface gráfica."""
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Nome do Participante:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.nome_participante, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="Microfone:").grid(row=1, column=0, sticky="w", pady=5)
        mic_dropdown = ttk.Combobox(frame, textvariable=self.selected_mic_name, values=self.mic_names, state="readonly", width=28)
        mic_dropdown.grid(row=1, column=1, pady=5)
        
        self.btn_principal = ttk.Button(frame, text="Iniciar Gravação (Sessão 'Antes')", command=self.controlar_sessao)
        self.btn_principal.grid(row=3, column=0, columnspan=2, pady=20, ipady=10) 
        
        self.btn_abortar = ttk.Button(frame, text="Abortar / Resetar", command=self.abortar_tudo, state="disabled")
        self.btn_abortar.grid(row=4, column=0, columnspan=2) 
        
        self.status_label = ttk.Label(frame, text="Pronto para iniciar.")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=10) 
        
        # VU Meter (Barra de volume)
        self.vu_meter = ttk.Progressbar(frame, mode='determinate', length=300)
        self.vu_meter.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5) 
        self.vu_meter.grid_remove() 
        
        # Barra de progresso de carregamento
        self.progress_bar = ttk.Progressbar(frame, mode='indeterminate')
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=10) 
        self.progress_bar.grid_remove()

    def controlar_sessao(self):
        if self.app_state == "IDLE":
            self.iniciar_countdown()
        elif self.app_state == "RECORDING":
            self.parar_gravacao()

    def iniciar_countdown(self):
        if not self.nome_participante.get().strip():
            messagebox.showwarning("Aviso", "Por favor, insira o nome do participante.")
            return
        if not self.selected_mic_name.get():
            messagebox.showwarning("Aviso", "Por favor, selecione um microfone.")
            return
            
        self.app_state = "COUNTDOWN"
        self.btn_principal.config(state="disabled")
        self.btn_abortar.config(state="normal")
        self.countdown_job = self.root.after(1000, self.update_countdown, 3)

    def update_countdown(self, count):
        if self.app_state != "COUNTDOWN": return 
        if count > 0:
            self.status_label.config(text=f"Iniciando em {count}...")
            self.countdown_job = self.root.after(1000, self.update_countdown, count - 1)
        else:
            self.iniciar_gravacao_real()

    def iniciar_gravacao_real(self):
        self.app_state = "RECORDING"
        self.is_recording = True
        self.frames = []
        
        self.status_label.config(text=f"Gravando (Sessão: {self.current_session_type})...")
        self.btn_principal.config(text="Parar Gravação", state="normal")
        self.btn_abortar.config(state="normal")
        
        self.vu_meter.grid()
        self.root.after(50, self.atualizar_vu_meter)
        
        selected_name = self.selected_mic_name.get()
        selected_index = self.mic_map.get(selected_name, None) 
        
        self.thread_gravacao = threading.Thread(target=self.thread_target_gravar, args=(selected_index,))
        self.thread_gravacao.start()
        
    def atualizar_vu_meter(self):
        if self.app_state != "RECORDING":
            self.vu_meter['value'] = 0
            self.vu_meter.grid_remove()
            return
        try:
            while not self.audio_queue.empty():
                rms_value = self.audio_queue.get_nowait()
            MAX_RMS = 5000 
            vu_percent = (rms_value / MAX_RMS) * 100
            self.vu_meter['value'] = min(vu_percent, 100)
        except Queue.Empty:
            pass
        self.root.after(50, self.atualizar_vu_meter) 

    def parar_gravacao(self):
        self.app_state = "ANALYZING"
        self.is_recording = False
        self.status_label.config(text="Finalizando gravação...")
        if hasattr(self, 'thread_gravacao'): 
            self.thread_gravacao.join() 
        
        nome_base = self.nome_participante.get().strip().replace(" ", "_")
        sessao = self.current_session_type
        
        # Criação de pastas
        self.current_participant_folder = os.path.join(os.getcwd(), nome_base)
        os.makedirs(self.current_participant_folder, exist_ok=True)
        
        nome_arquivo = f"{nome_base}_{sessao}.wav"
        full_audio_path = os.path.join(self.current_participant_folder, nome_arquivo)
        
        self.salvar_arquivo(full_audio_path) 

        self.status_label.config(text="Análise iniciada... Por favor, aguarde.")
        self.btn_principal.config(state="disabled")
        self.btn_abortar.config(state="disabled")
        self.progress_bar.grid()
        self.progress_bar.start()

        self.resultado_analise = None
        self.thread_analise = threading.Thread(
            target=self.thread_target_analisar_e_comparar, 
            args=(full_audio_path, sessao, nome_base, self.current_participant_folder)
        )
        self.thread_analise.start()
        self.root.after(100, self.verificar_analise_concluida)
        
    def verificar_analise_concluida(self):
        if self.thread_analise.is_alive():
            self.root.after(100, self.verificar_analise_concluida)
            return

        self.progress_bar.stop()
        self.progress_bar.grid_remove()

        if not (self.resultado_analise and self.resultado_analise['atual']):
            messagebox.showerror("Erro", "Não foi possível analisar o áudio.")
            self.abortar_tudo()
            return

        self.exibir_janela_resultados(
            self.resultado_analise['atual'],
            self.resultado_analise['antes'],
            self.current_participant_folder
        )
        self.status_label.config(text="Análise finalizada. Verifique o relatório.")
        
    def abortar_tudo(self):
        self.app_state = "ABORTING" 
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        if self.is_recording:
            self.is_recording = False
            if hasattr(self, 'thread_gravacao'):
                self.thread_gravacao.join()
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.vu_meter['value'] = 0
        self.vu_meter.grid_remove()
        self.status_label.config(text="Pronto para iniciar.")
        self.btn_principal.config(text="Iniciar Gravação (Sessão 'Antes')", state="normal")
        self.btn_abortar.config(state="disabled")
        self.nome_participante.set("")
        self.current_session_type = "Antes"
        self.app_state = "IDLE"
        self.current_participant_folder = None

    def thread_target_analisar_e_comparar(self, nome_arquivo_atual_path, sessao, nome_base, participant_folder):
        resultado_atual = analisar_audio(nome_arquivo_atual_path)
        resultado_antes = None
        if sessao == "Depois":
            nome_arquivo_antes = f"{nome_base}_Antes.wav"
            full_path_antes = os.path.join(participant_folder, nome_arquivo_antes)
            if os.path.exists(full_path_antes):
                resultado_antes = analisar_audio(full_path_antes)
            else:
                print(f"Aviso: Arquivo '{full_path_antes}' não encontrado.")
        
        self.resultado_analise = {'atual': resultado_atual, 'antes': resultado_antes}

    def _gerar_dicas_feedback(self, resultado):
        pontos_positivos = []
        pontos_melhoria = []
        LIMITE_MONOTONIA = 20
        LIMITE_JITTER = 1.5
        LIMITE_ESTABILIDADE_BOA = 0.8
        LIMITE_RITMO_RAPIDO = 5.5
        LIMITE_RITMO_LENTO = 3.0

        variacao_pitch = resultado.get('variacao_pitch', 0)
        if variacao_pitch >= LIMITE_MONOTONIA:
            pontos_positivos.append(f"• Ótimo Engajamento ({variacao_pitch:.2f} Hz): A sua entonação variou bem, tornando a fala dinâmica.")
        else:
            pontos_melhoria.append(f"• Variação de Pitch Baixa ({variacao_pitch:.2f} Hz): Voz monótona. Tente variar mais a entonação para prender a atenção.")

        jitter = resultado.get('jitter_percent', 0)
        if jitter > LIMITE_JITTER:
            pontos_melhoria.append(f"• Jitter Alto ({jitter:.2f}%): Instabilidade vocal detectada (tremor), possível sinal de nervosismo.")
        elif jitter <= LIMITE_ESTABILIDADE_BOA:
            pontos_positivos.append(f"• Excelente Estabilidade ({jitter:.2f}%): Voz firme e segura.")

        ritmo_sps = resultado.get('ritmo_sps', 0)
        if ritmo_sps > LIMITE_RITMO_RAPIDO:
            pontos_melhoria.append(f"• Ritmo Rápido ({ritmo_sps:.2f} sil/seg): Fala acelerada. Tente fazer pausas e respirar.")
        elif ritmo_sps < LIMITE_RITMO_LENTO and ritmo_sps > 0:
             pontos_melhoria.append(f"• Ritmo Lento ({ritmo_sps:.2f} sil/seg): Fala muito pausada, pode indicar hesitação.")
        elif ritmo_sps >= LIMITE_RITMO_LENTO and ritmo_sps <= LIMITE_RITMO_RAPIDO:
            pontos_positivos.append(f"• Ritmo Ideal ({ritmo_sps:.2f} sil/seg): Velocidade de fala adequada e clara.")

        if not pontos_positivos and not pontos_melhoria:
            pontos_positivos.append("• Ótimo trabalho! Métricas equilibradas.")
            
        return pontos_positivos, pontos_melhoria

    def exibir_janela_resultados(self, resultado_atual, resultado_antes=None, participant_folder=None):
        janela_resultado = tk.Toplevel(self.root)
        janela_resultado.title(f"Relatório de Análise")
        janela_resultado.transient(self.root)
        janela_resultado.grab_set()

        frame = ttk.Frame(janela_resultado, padding="15")
        frame.pack(fill="both", expand=True)
        
        # Frame rolável seria ideal, mas vamos manter simples por agora
        frame_conteudo = ttk.Frame(frame)
        frame_conteudo.pack(fill="both", expand=True)
        
        ttk.Label(frame_conteudo, text="Resultados da Apresentação", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        pontos_positivos, pontos_melhoria = self._gerar_dicas_feedback(resultado_atual)
        sessao_tipo = "Antes"
        
        if not resultado_antes:
            # Relatório Simples
            janela_resultado.geometry("500x650")
            sessao_tipo = "Antes"
            
            # Exibição dos dados numéricos
            labels = [
                (f"Arquivo: {os.path.basename(resultado_atual.get('nome_arquivo', 'N/A'))}", 0),
                (f"Volume Médio: {resultado_atual.get('volume_medio', 0):.4f}", 2),
                (f"Variação Pitch: {resultado_atual.get('variacao_pitch', 0):.2f} Hz", 3),
                (f"Jitter: {resultado_atual.get('jitter_percent', 0):.3f}%", 4),
                (f"Shimmer: {resultado_atual.get('shimmer_percent', 0):.3f}%", 5),
                (f"Ritmo: {resultado_atual.get('ritmo_sps', 0):.2f} sil/seg", 6)
            ]
            for text, row in labels:
                ttk.Label(frame_conteudo, text=text).grid(row=row, column=0, columnspan=4, sticky='w')

            # Barras
            pontuacao_engajamento = min(100, max(0, (resultado_atual.get('variacao_pitch', 0) - 10) / 50 * 100))
            ttk.Label(frame_conteudo, text="\nEngajamento (Variação Vocal):").grid(row=7, column=0, columnspan=4, sticky='w')
            ttk.Progressbar(frame_conteudo, length=400, value=pontuacao_engajamento).grid(row=8, column=0, columnspan=4)

            # Dicas
            ttk.Label(frame_conteudo, text="\nPontos Positivos:", font=("Helvetica", 10, "bold"), foreground="green").grid(row=9, column=0, sticky='w', pady=(10,0))
            curr_row = 10
            for d in pontos_positivos:
                ttk.Label(frame_conteudo, text=d, wraplength=450).grid(row=curr_row, column=0, sticky='w'); curr_row+=1
            
            ttk.Label(frame_conteudo, text="\nPontos de Melhoria:", font=("Helvetica", 10, "bold"), foreground="red").grid(row=curr_row, column=0, sticky='w', pady=(10,0)); curr_row+=1
            for d in pontos_melhoria:
                ttk.Label(frame_conteudo, text=d, wraplength=450).grid(row=curr_row, column=0, sticky='w'); curr_row+=1
            
            # Botões
            frame_botoes = ttk.Frame(frame)
            frame_botoes.pack(fill="x", pady=20)
            ttk.Button(frame_botoes, text="Resetar", command=lambda: self._resetar_e_fechar(janela_resultado)).pack(side="left", expand=True)
            ttk.Button(frame_botoes, text="Ir para Sessão 'Depois'", command=lambda: self._avancar_para_sessao_depois(janela_resultado)).pack(side="right", expand=True)
            
            # Salva automaticamente após 500ms
            self.root.after(500, lambda: self._salvar_relatorio_como_imagem(janela_resultado, participant_folder, sessao_tipo))
            return

        # Relatório Comparativo
        janela_resultado.geometry("550x600")
        sessao_tipo = "Depois"
        
        # Cabeçalho Tabela
        headers = ["Métrica", "Antes", "Depois", "Melhora"]
        for i, h in enumerate(headers):
            ttk.Label(frame_conteudo, text=h, font=("Helvetica", 10, "bold")).grid(row=1, column=i, padx=10)

        def calc_melhora(a, b, invert=False):
            if a == 0: return "N/A", "black"
            diff = ((b - a) / a) * 100
            good = diff > 0 if not invert else diff < 0
            color = "green" if good else "red"
            return f"{diff:+.1f}%", color

        metrics = [
            ("Volume", 'volume_medio', "{:.4f}", False),
            ("Pitch Var.", 'variacao_pitch', "{:.2f}", False),
            ("Jitter", 'jitter_percent', "{:.3f}", True),
            ("Shimmer", 'shimmer_percent', "{:.3f}", True),
            ("Ritmo", 'ritmo_sps', "{:.2f}", False)
        ]

        for i, (label, key, fmt, invert) in enumerate(metrics, start=2):
            val_a = resultado_antes.get(key, 0)
            val_b = resultado_atual.get(key, 0)
            txt_melhora, color = calc_melhora(val_a, val_b, invert)
            
            ttk.Label(frame_conteudo, text=label).grid(row=i, column=0, sticky='w', padx=10)
            ttk.Label(frame_conteudo, text=fmt.format(val_a)).grid(row=i, column=1, padx=10)
            ttk.Label(frame_conteudo, text=fmt.format(val_b)).grid(row=i, column=2, padx=10)
            ttk.Label(frame_conteudo, text=txt_melhora, foreground=color).grid(row=i, column=3, padx=10)

        # Dicas da sessão Depois
        curr_row = 8
        ttk.Label(frame_conteudo, text="\nFeedback Atual (Sessão 'Depois'):", font=("Helvetica", 10, "bold")).grid(row=curr_row, column=0, columnspan=4, sticky='w', pady=(15, 5)); curr_row+=1
        
        for d in pontos_positivos:
             ttk.Label(frame_conteudo, text=d, wraplength=500, foreground="green").grid(row=curr_row, column=0, columnspan=4, sticky='w'); curr_row+=1
        for d in pontos_melhoria:
             ttk.Label(frame_conteudo, text=d, wraplength=500, foreground="red").grid(row=curr_row, column=0, columnspan=4, sticky='w'); curr_row+=1

        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill="x", pady=20)
        ttk.Button(frame_botoes, text="Concluir e Novo Participante", command=lambda: self._resetar_e_fechar(janela_resultado)).pack(expand=True)

        self.root.after(500, lambda: self._salvar_relatorio_como_imagem(janela_resultado, participant_folder, sessao_tipo))

    def _avancar_para_sessao_depois(self, janela):
        janela.destroy()
        self.current_session_type = "Depois"
        self.status_label.config(text="Pronto para a sessão 'Depois'.")
        self.btn_principal.config(text="Iniciar Gravação (Sessão 'Depois')", state="normal")
        self.app_state = "IDLE"

    def _resetar_e_fechar(self, janela):
        janela.destroy()
        self.abortar_tudo()

    def thread_target_gravar(self, device_index):
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, 
                                input=True, frames_per_buffer=1024, 
                                input_device_index=device_index)
            while self.is_recording:
                data = stream.read(1024, exception_on_overflow=False)
                self.frames.append(data)
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                rms = np.sqrt(np.mean(audio_chunk.astype(float)**2))
                self.audio_queue.put(rms)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Erro na gravação: {e}")
        finally:
            audio.terminate()

    def salvar_arquivo(self, full_path):
        with wave.open(full_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(self.frames))

    def _salvar_relatorio_como_imagem(self, janela, folder, sessao_tipo):
        print(f"Salvando relatório automático para {sessao_tipo}...")
        try:
            # DPI Awareness fix para screenshots corretos
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
                scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            except:
                scale = 1.0

            janela.attributes('-topmost', 1) # Traz para frente
            janela.update()
            time.sleep(0.2)
            
            x = janela.winfo_rootx()
            y = janela.winfo_rooty()
            w = janela.winfo_width()
            h = janela.winfo_height()
            
            # Captura com ajuste de escala
            bbox = (x*scale, y*scale, (x+w)*scale, (y+h)*scale)
            img = ImageGrab.grab(bbox)
            
            # Redimensiona de volta se necessário (para manter qualidade visual 1:1)
            if scale != 1.0:
                img = img.resize((w, h), Image.Resampling.LANCZOS) # Aqui usamos o Image importado

            filename = f"Relatorio_{sessao_tipo}.png"
            img.save(os.path.join(folder, filename))
            print("Relatório salvo.")
            
            janela.attributes('-topmost', 0) # Libera
            
        except Exception as e:
            print(f"Erro ao salvar imagem: {e}")
            # Não mostra popup de erro para não interromper o fluxo visual, apenas loga
            try: janela.attributes('-topmost', 0)
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AppAnalisadorDeVoz(root)
    root.mainloop()