import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Frame Principal
frame_principal = tk.Frame(root)
frame_principal.pack(fill="both", expand=True)

# Canvas
canvas = tk.Canvas(frame_principal)
scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Frame Geral
frame_geral = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame_geral, anchor="nw")

# Layout
canvas.grid(row=0, column=0,pady=5, padx=10, sticky="ew")
scrollbar.grid(row=0, column=1,pady=5, padx=10, sticky="ns")

# Função para adicionar itens
def adicionar_item(texto, i):
    frame_item = tk.Frame(frame_geral, borderwidth=2, relief="groove")
    frame_item.grid(row=i, column=0,pady=5, padx=10, sticky="ew")
    tk.Label(frame_item, text=texto).grid(row=0, column=0,pady=5, padx=10, sticky="ew")
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

# Adicionar itens de exemplo
for i in range(20):
    adicionar_item(f"Item {i}", i)

root.mainloop()