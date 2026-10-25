"""
Busqueda_Heuristica_GUI.py

Interfaz gráfica para visualizar algoritmos de búsqueda Dijkstra y A*
con animación del recorrido de nodos.

author = "Sergio Alejandro Vera Martínez"
contact = "sergiovera3b@gmail.com"
date = "2025/10/31"
status = "Develop"
version = "1.0.0"
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import heapq
from collections import deque

class GraphVisualization:
    def __init__(self):
        # Grafo definido en la práctica
        self.graph = {
            'A': [('B', 4), ('C', 2)],
            'B': [('A', 4), ('E', 3), ('D', 5)],
            'C': [('A', 2), ('F', 6), ('D', 8)],
            'D': [('B', 5), ('C', 8), ('G', 1)],
            'E': [('B', 3), ('G', 9)],
            'F': [('C', 6), ('H', 2)],
            'G': [('D', 1), ('E', 9), ('H', 7)],
            'H': [('F', 2), ('G', 7)]
        }
        
        # Coordenadas para visualización
        self.coordinates = {
            'A': (100, 200),
            'B': (250, 150),
            'C': (150, 300),
            'D': (350, 250),
            'E': (400, 100),
            'F': (200, 400),
            'G': (450, 300),
            'H': (300, 450)
        }
        
        # Colores para diferentes estados
        self.colors = {
            'default': 'lightblue',
            'current': 'red',
            'visited': 'yellow',
            'path': 'green',
            'frontier': 'orange'
        }
        
        self.setup_gui()
    
    def setup_gui(self):
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Visualización de Algoritmos de Búsqueda - ASU")
        self.root.geometry("800x600")
        
        # Frame de controles
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # Selección de algoritmo
        ttk.Label(control_frame, text="Algoritmo:").grid(row=0, column=0, padx=5)
        self.algorithm_var = tk.StringVar(value="Dijkstra")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var,
                                      values=["Dijkstra", "A* Manhattan"])
        algorithm_combo.grid(row=0, column=1, padx=5)
        
        # Nodo inicio y objetivo
        ttk.Label(control_frame, text="Inicio:").grid(row=0, column=2, padx=5)
        self.start_var = tk.StringVar(value="A")
        start_combo = ttk.Combobox(control_frame, textvariable=self.start_var,
                                  values=list(self.graph.keys()))
        start_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(control_frame, text="Objetivo:").grid(row=0, column=4, padx=5)
        self.goal_var = tk.StringVar(value="H")
        goal_combo = ttk.Combobox(control_frame, textvariable=self.goal_var,
                                 values=list(self.graph.keys()))
        goal_combo.grid(row=0, column=5, padx=5)
        
        # Botones de control
        ttk.Button(control_frame, text="Ejecutar", 
                  command=self.run_algorithm).grid(row=0, column=6, padx=5)
        ttk.Button(control_frame, text="Paso a Paso", 
                  command=self.step_by_step).grid(row=0, column=7, padx=5)
        ttk.Button(control_frame, text="Reiniciar", 
                  command=self.reset).grid(row=0, column=8, padx=5)
        
        # Control de velocidad
        ttk.Label(control_frame, text="Velocidad:").grid(row=1, column=0, padx=5)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(control_frame, from_=0.1, to=2.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.grid(row=1, column=1, columnspan=2, padx=5, sticky=tk.EW)
        
        # Canvas para dibujar el grafo
        self.canvas = tk.Canvas(self.root, width=800, height=500, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para información
        self.text_area = tk.Text(self.root, height=10, width=80)
        self.text_area.pack(fill=tk.BOTH, padx=10, pady=5)
        
        # Estado de la animación
        self.animation_state = None
        self.step_index = 0
        self.steps = []
        
        # Dibujar grafo inicial
        self.draw_graph()
    
    def draw_graph(self):
        self.canvas.delete("all")
        
        # Dibujar aristas
        for node, neighbors in self.graph.items():
            x1, y1 = self.coordinates[node]
            for neighbor, weight in neighbors:
                x2, y2 = self.coordinates[neighbor]
                self.canvas.create_line(x1, y1, x2, y2, width=2, fill='gray')
                # Dibujar peso
                mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
                self.canvas.create_text(mid_x, mid_y, text=str(weight), 
                                      fill='black', font=('Arial', 10, 'bold'))
        
        # Dibujar nodos
        for node, (x, y) in self.coordinates.items():
            color = self.colors['default']
            if hasattr(self, 'node_colors') and node in self.node_colors:
                color = self.node_colors[node]
            
            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=color, outline='black')
            self.canvas.create_text(x, y, text=node, font=('Arial', 12, 'bold'))
    
    def update_node_color(self, node, color_type):
        if not hasattr(self, 'node_colors'):
            self.node_colors = {node: self.colors['default'] for node in self.graph}
        
        self.node_colors[node] = self.colors[color_type]
        self.draw_graph()
        self.root.update()
        time.sleep(1.0 / self.speed_var.get())
    
    def log_message(self, message):
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.root.update()
    
    def manhattan_distance(self, node1, node2):
        x1, y1 = self.coordinates[node1]
        x2, y2 = self.coordinates[node2]
        return abs(x1 - x2) + abs(y1 - y2)
    
    def dijkstra(self, start, goal):
        self.log_message(f"=== INICIANDO DIJKSTRA de {start} a {goal} ===")
        
        distances = {node: math.inf for node in self.graph}
        distances[start] = 0
        parents = {node: None for node in self.graph}
        visited = set()
        priority_queue = [(0, start)]
        
        step_count = 0
        self.steps = []
        
        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            step_count += 1
            
            if current_node in visited:
                continue
            
            # Registrar paso
            self.steps.append({
                'current': current_node,
                'visited': visited.copy(),
                'frontier': [node for _, node in priority_queue],
                'message': f"Paso {step_count}: Expandir {current_node} (costo: {current_distance})"
            })
            
            visited.add(current_node)
            
            if current_node == goal:
                self.log_message(f"¡OBJETIVO {goal} ALCANZADO!")
                break
            
            for neighbor, weight in self.graph[current_node]:
                if neighbor not in visited:
                    new_distance = current_distance + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        parents[neighbor] = current_node
                        heapq.heappush(priority_queue, (new_distance, neighbor))
        
        # Reconstruir camino
        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = parents[node]
        path.reverse()
        
        return path, distances[goal], step_count
    
    def a_star(self, start, goal):
        self.log_message(f"=== INICIANDO A* CON HEURÍSTICA MANHATTAN de {start} a {goal} ===")
        
        g_score = {node: math.inf for node in self.graph}
        g_score[start] = 0
        f_score = {node: math.inf for node in self.graph}
        f_score[start] = self.manhattan_distance(start, goal)
        parents = {node: None for node in self.graph}
        
        priority_queue = [(f_score[start], start)]
        visited = set()
        step_count = 0
        self.steps = []
        
        while priority_queue:
            current_f, current_node = heapq.heappop(priority_queue)
            step_count += 1
            
            if current_node in visited:
                continue
            
            # Registrar paso
            self.steps.append({
                'current': current_node,
                'visited': visited.copy(),
                'frontier': [node for _, node in priority_queue],
                'message': f"Paso {step_count}: Expandir {current_node} (f={current_f:.2f})"
            })
            
            visited.add(current_node)
            
            if current_node == goal:
                self.log_message(f"¡OBJETIVO {goal} ALCANZADO!")
                break
            
            for neighbor, weight in self.graph[current_node]:
                if neighbor not in visited:
                    tentative_g = g_score[current_node] + weight
                    if tentative_g < g_score[neighbor]:
                        parents[neighbor] = current_node
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self.manhattan_distance(neighbor, goal)
                        heapq.heappush(priority_queue, (f_score[neighbor], neighbor))
        
        # Reconstruir camino
        path = []
        node = goal
        while node is not None:
            path.append(node)
            node = parents[node]
        path.reverse()
        
        return path, g_score[goal], step_count
    
    def run_algorithm(self):
        self.reset()
        start = self.start_var.get()
        goal = self.goal_var.get()
        algorithm = self.algorithm_var.get()
        
        if start == goal:
            messagebox.showerror("Error", "El nodo inicio y objetivo deben ser diferentes")
            return
        
        # Ejecutar algoritmo seleccionado
        if algorithm == "Dijkstra":
            path, cost, steps = self.dijkstra(start, goal)
        else:
            path, cost, steps = self.a_star(start, goal)
        
        # Mostrar resultados
        self.log_message(f"\n=== RESULTADOS ===")
        self.log_message(f"Algoritmo: {algorithm}")
        self.log_message(f"Camino encontrado: {' -> '.join(path)}")
        self.log_message(f"Costo total: {cost}")
        self.log_message(f"Nodos expandidos: {steps}")
        
        # Animación automática
        self.animate_steps(path)
    
    def step_by_step(self):
        start = self.start_var.get()
        goal = self.goal_var.get()
        algorithm = self.algorithm_var.get()
        
        if start == goal:
            messagebox.showerror("Error", "El nodo inicio y objetivo deben ser diferentes")
            return
        
        # Ejecutar algoritmo para obtener pasos
        if algorithm == "Dijkstra":
            path, cost, steps = self.dijkstra(start, goal)
        else:
            path, cost, steps = self.a_star(start, goal)
        
        self.step_index = 0
        self.animation_state = 'stepping'
        self.show_next_step()
    
    def show_next_step(self):
        if self.step_index < len(self.steps):
            step = self.steps[self.step_index]
            self.log_message(step['message'])
            
            # Actualizar colores
            for node in self.graph:
                if node == step['current']:
                    self.update_node_color(node, 'current')
                elif node in step['visited']:
                    self.update_node_color(node, 'visited')
                elif node in step['frontier']:
                    self.update_node_color(node, 'frontier')
                else:
                    self.update_node_color(node, 'default')
            
            self.step_index += 1
            
            if self.animation_state == 'stepping':
                # Esperar botón para siguiente paso
                self.root.after(100, self.wait_for_next_step)
        else:
            # Mostrar camino final
            start = self.start_var.get()
            goal = self.goal_var.get()
            algorithm = self.algorithm_var.get()
            
            if algorithm == "Dijkstra":
                path, cost, steps = self.dijkstra(start, goal)
            else:
                path, cost, steps = self.a_star(start, goal)
            
            self.animate_path(path)
    
    def wait_for_next_step(self):
        # Este método permite pausar entre pasos
        # En una implementación completa, se agregaría un botón "Siguiente"
        self.root.after(int(1000 / self.speed_var.get()), self.show_next_step)
    
    def animate_steps(self, path):
        self.step_index = 0
        self.animation_state = 'auto'
        self.auto_animate()
    
    def auto_animate(self):
        if self.step_index < len(self.steps):
            step = self.steps[self.step_index]
            self.log_message(step['message'])
            
            # Actualizar colores
            for node in self.graph:
                if node == step['current']:
                    self.update_node_color(node, 'current')
                elif node in step['visited']:
                    self.update_node_color(node, 'visited')
                elif node in step['frontier']:
                    self.update_node_color(node, 'frontier')
                else:
                    self.update_node_color(node, 'default')
            
            self.step_index += 1
            self.root.after(int(1000 / self.speed_var.get()), self.auto_animate)
        else:
            self.animate_path(path)
    
    def animate_path(self, path):
        self.log_message("\n=== MOSTRANDO CAMINO ÓPTIMO ===")
        
        # Resaltar camino óptimo
        for i, node in enumerate(path):
            self.update_node_color(node, 'path')
            if i < len(path) - 1:
                # Resaltar arista del camino
                x1, y1 = self.coordinates[node]
                x2, y2 = self.coordinates[path[i+1]]
                self.canvas.create_line(x1, y1, x2, y2, width=4, fill='green', arrow=tk.LAST)
        
        self.log_message(f"Camino óptimo: {' -> '.join(path)}")
    
    def reset(self):
        """Reiniciar la visualización"""
        self.step_index = 0
        self.steps = []
        self.animation_state = None
        self.text_area.delete(1.0, tk.END)
        
        # Restablecer colores de nodos
        if hasattr(self, 'node_colors'):
            for node in self.node_colors:
                self.node_colors[node] = self.colors['default']
        
        self.draw_graph()
        self.log_message("Sistema reiniciado. Seleccione algoritmo y haga clic en Ejecutar.")
    
    def run(self):
        self.root.mainloop()

# Ejecutar la aplicación
if __name__ == "__main__":
    app = GraphVisualization()
    app.run()