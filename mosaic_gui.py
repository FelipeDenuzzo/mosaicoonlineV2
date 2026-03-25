import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
from PIL import Image
import threading

# Funções utilitárias

def mm_to_pixels(mm, dpi=240):
    inches = mm / 25.4
    return round(inches * dpi)

def pixels_to_cm(pixels, dpi=240):
    inches = pixels / dpi
    return inches * 2.54

def calculate_final_size(reference_path, tile_size_mm, tiles_folder=None, dpi=240):
    with Image.open(reference_path) as reference:
        ref_width = reference.width
        ref_height = reference.height
    tile_analysis_px = mm_to_pixels(tile_size_mm, dpi)
    tiles_x = max(1, ref_width // tile_analysis_px)
    tiles_y = max(1, ref_height // tile_analysis_px)
    # tamanho nativo do tile
    sample_size = 100
    if tiles_folder:
        try:
            supported = (".png", ".jpg", ".jpeg")
            for name in os.listdir(tiles_folder):
                if name.lower().endswith(supported):
                    with Image.open(os.path.join(tiles_folder, name)) as sample:
                        sample_size = sample.width
                        break
        except Exception:
            pass
    final_width_px = tiles_x * sample_size
    final_height_px = tiles_y * sample_size
    final_width_cm = pixels_to_cm(final_width_px, dpi)
    final_height_cm = pixels_to_cm(final_height_px, dpi)
    return final_width_px, final_height_px, final_width_cm, final_height_cm, tiles_x, tiles_y

# GUI principal
class MosaicGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mosaic Creator")
        self.geometry("650x850")
        self.minsize(650, 850)
        self.resizable(True, True)
        self.reference_path = None
        self.tiles_folder = None
        self.pixel_size_mm = tk.IntVar(value=25)
        self.max_uses = tk.IntVar(value=0)
        self.quality = tk.IntVar(value=85)
        self.similarity = tk.DoubleVar(value=0.0)
        self.size_label = None
        self._stop_event = threading.Event()
        self._thread = None
        self.create_widgets()

    def create_widgets(self):
        # Seleção de imagem base
        tk.Label(self, text="Imagem base:").pack(pady=(20,0))
        self.ref_entry = tk.Entry(self, width=40)
        self.ref_entry.pack(padx=10)
        tk.Button(self, text="Selecionar imagem", command=self.select_reference).pack(pady=5)

        # Seleção de pasta de pixels
        tk.Label(self, text="Pasta dos pixels:").pack(pady=(20,0))
        self.tiles_entry = tk.Entry(self, width=40)
        self.tiles_entry.pack(padx=10)
        tk.Button(self, text="Selecionar pasta", command=self.select_tiles_folder).pack(pady=5)

        # Régua para tamanho do pixel
        tk.Label(self, text="Tamanho do pixel (mm):").pack(pady=(20,0))
        self.pixel_slider = tk.Scale(
            self,
            from_=25,
            to=50,
            orient="horizontal",
            resolution=25,
            variable=self.pixel_size_mm,
            showvalue=True,
            length=350,
            command=self.on_pixel_change,
        )
        self.pixel_slider.pack(padx=20, fill="x")
        tk.Label(self, text="25mm (mais definição) ... 50mm (menos definição)").pack()

        # Régua para repetições
        tk.Label(self, text="Repetições máximas por pixel:").pack(pady=(20,0))
        self.uses_slider = tk.Scale(
            self,
            from_=0,
            to=4,
            orient="horizontal",
            resolution=2,
            variable=self.max_uses,
            showvalue=True,
            length=350,
            command=self.on_uses_change,
        )
        self.uses_slider.pack(padx=20, fill="x")
        tk.Label(self, text="0 = sem repetição, 2 ou 4 = pode repetir").pack()

        # Qualidade JPEG
        tk.Label(self, text="Qualidade JPEG:").pack(pady=(20,0))
        self.quality_slider = tk.Scale(
            self,
            from_=50,
            to=100,
            orient="horizontal",
            resolution=1,
            variable=self.quality,
            showvalue=True,
            length=350,
            command=self.on_quality_change,
        )
        self.quality_slider.pack(padx=20, fill="x")

        # Similaridade
        tk.Label(self, text="Similaridade de cor (0-1):").pack(pady=(20,0))
        self.similarity_slider = tk.Scale(
            self,
            from_=0,
            to=1,
            orient="horizontal",
            resolution=0.05,
            variable=self.similarity,
            showvalue=True,
            length=350,
            command=self.on_similarity_change,
        )
        self.similarity_slider.pack(padx=20, fill="x")

        # Tamanho final
        self.size_label = tk.Label(self, text="Tamanho final: ---")
        self.size_label.pack(pady=(20,0))
        tk.Label(self, text="* Somente o tamanho do pixel altera a dimensão do mosaico.", fg="gray").pack()

        # Campo para nome do arquivo final
        tk.Label(self, text="Nome do arquivo final:").pack(pady=(20,0))
        self.output_entry = tk.Entry(self, width=30)
        self.output_entry.insert(0, "mosaico_final.jpg")
        self.output_entry.pack(padx=10)

        # Botão para calcular tamanho
        tk.Button(self, text="Calcular tamanho", command=self.show_final_size).pack(pady=10)

        # Frame fixo na parte inferior para o botão
        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom", fill="x", pady=30)
        self.run_button = tk.Button(bottom_frame, text="CRIAR MOSAICO", command=self.run_mosaic_thread, bg="#4CAF50", fg="white", font=("Arial", 16, "bold"), height=2, width=22)
        self.run_button.pack(side="left", padx=10)
        self.stop_button = tk.Button(bottom_frame, text="PARAR", command=self.stop_mosaic, bg="#f44336", fg="white", font=("Arial", 16, "bold"), height=2, width=10, state="disabled")
        self.stop_button.pack(side="right", padx=10)

    # Atualizadores de sliders
    def on_pixel_change(self, val):
        self.pixel_size_mm.set(int(float(val)))
        self.update_size_label()

    def on_uses_change(self, val):
        self.max_uses.set(int(float(val)))

    def on_quality_change(self, val):
        self.quality.set(int(float(val)))

    def on_similarity_change(self, val):
        self.similarity.set(round(float(val), 2))

    def select_reference(self):
        path = filedialog.askopenfilename(title="Selecione a imagem base", filetypes=[("Imagens", "*.jpg *.jpeg *.png")])
        if path:
            self.reference_path = path
            self.ref_entry.delete(0, tk.END)
            self.ref_entry.insert(0, path)
            self.update_size_label()

    def select_tiles_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de pixels")
        if folder:
            self.tiles_folder = folder
            self.tiles_entry.delete(0, tk.END)
            self.tiles_entry.insert(0, folder)

    def update_size_label(self, *args):
        if self.reference_path:
            try:
                width_px, height_px, width_cm, height_cm, tiles_x, tiles_y = calculate_final_size(
                    self.reference_path, self.pixel_size_mm.get(), self.tiles_folder)
                self.size_label.config(text=f"Tamanho final: {width_px}x{height_px} px | {width_cm:.1f}x{height_cm:.1f} cm | Grid: {tiles_x}x{tiles_y}")
            except Exception:
                self.size_label.config(text="Tamanho final: ---")
        else:
            self.size_label.config(text="Tamanho final: ---")

    def show_final_size(self):
        self.update_size_label()

    def run_mosaic_thread(self):
        if self._thread and self._thread.is_alive():
            messagebox.showinfo("Processando", "Já existe um processamento em andamento.")
            return
        self._stop_event.clear()
        self.stop_button.config(state="normal")
        self.run_button.config(state="disabled")
        self._thread = threading.Thread(target=self.run_mosaic)
        self._thread.start()

    def run_mosaic(self):
        # Importa funções do script principal
        try:
            from mosaic_creator import build_mosaic
        except ImportError:
            self._reset_buttons()
            messagebox.showerror("Erro", "Não foi possível importar build_mosaic do mosaic_creator.py")
            return
        if not self.reference_path or not self.tiles_folder:
            self._reset_buttons()
            messagebox.showerror("Erro", "Selecione a imagem base e a pasta dos pixels.")
            return
        output_name = self.output_entry.get().strip()
        if not output_name:
            output_name = "mosaico_final.jpg"
        try:
            build_mosaic(
                reference_path=self.reference_path,
                tiles_folder=self.tiles_folder,
                tile_size_mm=int(self.pixel_size_mm.get()),
                max_uses=int(self.max_uses.get()),
                output_path=output_name,
                similarity=float(self.similarity.get()),
                quality=int(self.quality.get()),
                stop_event=self._stop_event
            )
            if self._stop_event.is_set():
                messagebox.showinfo("Parado", "Processamento interrompido pelo usuário.")
            else:
                messagebox.showinfo("Sucesso", f"Mosaico criado com sucesso! Salvo como {output_name}")
        except Exception as e:
            messagebox.showerror("Erro ao criar mosaico", str(e))
        self._reset_buttons()

    def stop_mosaic(self):
        self._stop_event.set()
        self.stop_button.config(state="disabled")

    def _reset_buttons(self):
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")

if __name__ == "__main__":
    try:
        print("Iniciando interface gráfica...")
        app = MosaicGUI()
        print("Interface aberta. Aguardando entrada do usuário...")
        app.mainloop()
    except Exception as e:
        print(f"❌ Erro ao iniciar interface: {e}")
        import traceback
        traceback.print_exc()
