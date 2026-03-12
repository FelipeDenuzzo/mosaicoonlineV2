"""
Interface gráfica para criação de mosaicos de imagens.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import time
import signal
from mosaico import criar_mosaico, calcular_tamanho_final


class InterfaceMosaico:
    """Interface gráfica para criar mosaicos."""
    
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Criador de Mosaicos")
        self.janela.geometry("700x800")
        self.janela.resizable(False, False)
        
        self.imagem_base = None
        self.pasta_pixels = None
        self.processando = False
        
        # Impedir que o App entre em sleep
        signal.signal(signal.SIGCONT, self._manter_vivo)
        
        # Thread para manter o processo vivo
        self.thread_keep_alive = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread_keep_alive.start()
        
        # Atualizar janela continuamente
        self._atualizar_janela()
        
        self._criar_interface()
    
    def _manter_vivo(self, signum, frame):
        """Signal handler para manter vivo"""
        pass
    
    def _keep_alive_loop(self):
        """Loop que mantém o processo ativo em background"""
        while True:
            try:
                time.sleep(0.5)
                # Simula atividade
                _ = os.getpid()
            except:
                pass
    
    def _atualizar_janela(self):
        """Atualiza a janela continuamente para evitar freeze"""
        try:
            self.janela.update_idletasks()
        except:
            pass
        # Agendar próxima atualização
        self.janela.after(100, self._atualizar_janela)
    
    def _criar_interface(self):
        """Cria todos os elementos da interface."""
        
        # ===== IMAGEM BASE =====
        frame1 = tk.LabelFrame(self.janela, text="1. Imagem Base", padx=10, pady=10)
        frame1.pack(fill="x", padx=10, pady=5)
        
        self.label_base = tk.Label(frame1, text="Nenhuma imagem selecionada", fg="gray")
        self.label_base.pack(anchor="w")
        tk.Button(frame1, text="Selecionar Imagem Base", command=self._selecionar_base).pack(fill="x", pady=5)
        
        # ===== PASTA PIXELS =====
        frame2 = tk.LabelFrame(self.janela, text="2. Pasta com Imagens de Pixel", padx=10, pady=10)
        frame2.pack(fill="x", padx=10, pady=5)
        
        self.label_pixels = tk.Label(frame2, text="Nenhuma pasta selecionada", fg="gray")
        self.label_pixels.pack(anchor="w")
        tk.Button(frame2, text="Selecionar Pasta", command=self._selecionar_pasta).pack(fill="x", pady=5)
        
        # ===== REDIMENSIONAMENTO =====
        frame3 = tk.LabelFrame(self.janela, text="3. Tamanho dos Pixels", padx=10, pady=10)
        frame3.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame3, text="Redimensionar pixels?").pack(anchor="w")
        self.var_redimensionar = tk.BooleanVar(value=False)
        tk.Radiobutton(frame3, text="Não - manter tamanho original", variable=self.var_redimensionar, value=False).pack(anchor="w")
        tk.Radiobutton(frame3, text="Sim - redimensionar para:", variable=self.var_redimensionar, value=True).pack(anchor="w")
        
        frame_tamanho = tk.Frame(frame3)
        frame_tamanho.pack(anchor="w", padx=20)
        tk.Label(frame_tamanho, text="Tamanho em pixels:").pack(side="left")
        self.entry_tamanho = tk.Spinbox(frame_tamanho, from_=10, to=500, width=10)
        self.entry_tamanho.insert(0, "100")
        self.entry_tamanho.pack(side="left", padx=5)
        
        # ===== VARIAÇÃO DE COR =====
        frame4 = tk.LabelFrame(self.janela, text="4. Variação de Cor (0-100)", padx=10, pady=10)
        frame4.pack(fill="x", padx=10, pady=5)
        
        self.var_variacao = tk.IntVar(value=30)
        frame_slider = tk.Frame(frame4)
        frame_slider.pack(fill="x")
        tk.Scale(frame_slider, from_=0, to=100, orient="horizontal", variable=self.var_variacao).pack(side="left", fill="x", expand=True)
        self.label_variacao = tk.Label(frame_slider, text="30", width=3)
        self.label_variacao.pack(side="left")
        self.var_variacao.trace("w", lambda *args: self.label_variacao.config(text=str(self.var_variacao.get())))
        
        tk.Label(frame4, text="0 = cores muito similares | 100 = maior variação", fg="gray", font=("Arial", 8)).pack(anchor="w")
        
        # ===== REPETIÇÕES =====
        frame5 = tk.LabelFrame(self.janela, text="5. Repetições de Pixels", padx=10, pady=10)
        frame5.pack(fill="x", padx=10, pady=5)
        
        self.var_repeticoes = tk.IntVar(value=0)
        tk.Radiobutton(frame5, text="0 - Cada pixel usado apenas 1 vez", variable=self.var_repeticoes, value=0).pack(anchor="w")
        tk.Radiobutton(frame5, text="2 - Cada pixel pode repetir até 2 vezes", variable=self.var_repeticoes, value=2).pack(anchor="w")
        tk.Radiobutton(frame5, text="4 - Cada pixel pode repetir até 4 vezes", variable=self.var_repeticoes, value=4).pack(anchor="w")
        
        # ===== TAMANHO FINAL E NOME =====
        frame6 = tk.LabelFrame(self.janela, text="6. Visualização e Nome do Arquivo", padx=10, pady=10)
        frame6.pack(fill="x", padx=10, pady=5)
        
        self.label_tamanho = tk.Label(frame6, text="Tamanho final: (selecione imagem e pasta)", fg="gray")
        self.label_tamanho.pack(anchor="w", pady=5)
        
        tk.Button(frame6, text="Calcular Tamanho Final", command=self._calcular_tamanho).pack(fill="x", pady=5)
        
        tk.Label(frame6, text="Nome do arquivo (sem extensão):").pack(anchor="w", pady=(10, 0))
        self.entry_nome = tk.Entry(frame6)
        self.entry_nome.insert(0, "mosaico")
        self.entry_nome.pack(fill="x", pady=5)
        
        # ===== ONDE SALVAR =====
        frame7 = tk.LabelFrame(self.janela, text="7. Onde Salvar", padx=10, pady=10)
        frame7.pack(fill="x", padx=10, pady=5)
        
        self.label_saida = tk.Label(frame7, text="Pasta: Documentos", fg="gray")
        self.label_saida.pack(anchor="w")
        tk.Button(frame7, text="Escolher Pasta de Saída", command=self._selecionar_saida).pack(fill="x", pady=5)
        
        self.pasta_saida = os.path.expanduser("~/Documentos")
        
        # ===== BOTÃO RODAR E PROGRESSO =====
        frame8 = tk.Frame(self.janela)
        frame8.pack(fill="x", padx=10, pady=10)
        
        self.botao_rodar = tk.Button(frame8, text="RODAR", command=self._rodar_mosaico, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"), height=2)
        self.botao_rodar.pack(fill="x", pady=5)
        
        self.label_progresso = tk.Label(frame8, text="", fg="blue")
        self.label_progresso.pack(anchor="w")
        
        self.barra_progresso = ttk.Progressbar(frame8, mode="determinate", length=400)
        self.barra_progresso.pack(fill="x", pady=5)
    
    def _selecionar_base(self):
        """Abre diálogo para selecionar imagem base."""
        caminho = filedialog.askopenfilename(
            title="Selecione a imagem base",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp"), ("Todas", "*.*")]
        )
        if caminho:
            self.imagem_base = caminho
            nome = os.path.basename(caminho)
            self.label_base.config(text=f"✓ {nome}", fg="black")
            self._atualizar_nome_arquivo()
    
    def _selecionar_pasta(self):
        """Abre diálogo para selecionar pasta de pixels."""
        pasta = filedialog.askdirectory(title="Selecione a pasta com imagens de pixel")
        if pasta:
            self.pasta_pixels = pasta
            nome = os.path.basename(pasta)
            self.label_pixels.config(text=f"✓ {nome}", fg="black")
            self._atualizar_nome_arquivo()
    
    def _selecionar_saida(self):
        """Abre diálogo para selecionar pasta de saída."""
        pasta = filedialog.askdirectory(title="Onde salvar o arquivo?")
        if pasta:
            self.pasta_saida = pasta
            nome = os.path.basename(pasta) or pasta
            self.label_saida.config(text=f"Pasta: {nome}", fg="black")
    
    def _atualizar_nome_arquivo(self):
        """Atualiza o nome do arquivo com base nas configurações."""
        if self.imagem_base:
            nome_base = os.path.splitext(os.path.basename(self.imagem_base))[0]
            tamanho = self.entry_tamanho.get()
            variacao = self.var_variacao.get()
            repeticoes = self.var_repeticoes.get()
            
            nome_sugerido = f"{nome_base}_{tamanho}_{variacao}_{repeticoes}"
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, nome_sugerido)
    
    def _calcular_tamanho(self):
        """Calcula e exibe o tamanho final."""
        if not self.imagem_base or not self.pasta_pixels:
            messagebox.showwarning("Aviso", "Selecione a imagem base e a pasta de pixels!")
            return
        
        try:
            tamanho = int(self.entry_tamanho.get())
            redimensionar = self.var_redimensionar.get()
            
            largura, altura, descricao = calcular_tamanho_final(
                self.imagem_base,
                self.pasta_pixels,
                tamanho,
                redimensionar
            )
            
            self.label_tamanho.config(text=f"Tamanho final: {descricao}", fg="black")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular tamanho: {e}")
    
    def _rodar_mosaico(self):
        """Inicia a criação do mosaico em thread separada."""
        if not self.imagem_base or not self.pasta_pixels:
            messagebox.showwarning("Aviso", "Selecione a imagem base e a pasta de pixels!")
            return
        
        if self.processando:
            messagebox.showwarning("Aviso", "Já há um processamento em andamento!")
            return
        
        self.botao_rodar.config(state="disabled")
        self.processando = True
        thread = threading.Thread(target=self._thread_criar_mosaico, daemon=False)
        thread.start()
    
    def _thread_criar_mosaico(self):
        """Thread que cria o mosaico."""
        try:
            tamanho = int(self.entry_tamanho.get())
            redimensionar = self.var_redimensionar.get()
            repeticoes = self.var_repeticoes.get()
            variacao = self.var_variacao.get()
            nome_arquivo = self.entry_nome.get().strip() or "mosaico"
            
            # Garantir que o nome não tenha extensão
            if nome_arquivo.endswith(".jpg"):
                nome_arquivo = nome_arquivo[:-4]
            
            caminho_saida = os.path.join(self.pasta_saida, f"{nome_arquivo}.jpg")
            
            # Callback para progresso
            def atualizar_progresso(atual, total):
                porcentagem = (atual / total) * 100
                self.label_progresso.config(text=f"Progresso: {atual}/{total}")
                self.barra_progresso.config(value=porcentagem)
                self.janela.update()
            
            self.label_progresso.config(text="Iniciando...", fg="blue")
            self.janela.update()
            
            largura, altura = criar_mosaico(
                self.imagem_base,
                self.pasta_pixels,
                tamanho,
                redimensionar,
                repeticoes,
                variacao,
                caminho_saida,
                callback_progresso=atualizar_progresso
            )
            
            self.label_progresso.config(text="✓ Concluído!", fg="green")
            self.barra_progresso.config(value=100)
            messagebox.showinfo(
                "Sucesso",
                f"Mosaico criado com sucesso!\n\n"
                f"Arquivo: {caminho_saida}\n"
                f"Tamanho: {largura}×{altura} pixels"
            )
        except Exception as e:
            self.label_progresso.config(text="✗ Erro!", fg="red")
            messagebox.showerror("Erro", f"Erro ao criar mosaico:\n{e}")
        finally:
            self.botao_rodar.config(state="normal")


if __name__ == "__main__":
    janela = tk.Tk()
    app = InterfaceMosaico(janela)
    janela.mainloop()
