import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
from tkinter import font as tkfont

class EnhancedPoint:
    def __init__(self, x, y, id=None):
        self.x = x
        self.y = y
        self.id = id

    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __repr__(self):
        return f"({self.x:.1f}, {self.y:.1f})"

class EnhancedClosestPairVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Closest Pair Visualizer")
        self.root.geometry("1100x700")
        
        # Simple color scheme
        self.theme = {
            "bg": "#f0f0f0",
            "fg": "#000000",
            "accent": "#0066cc",
            "secondary": "#3399ff",
            "danger": "#cc0000",
            "success": "#009933",
            "warning": "#ff9900",
            "canvas_bg": "#ffffff",
            "grid": "#e0e0e0"
        }

        # Points storage
        self.points = []
        self.closest_pair = (None, None)
        self.min_distance = float('inf')
        self.point_counter = 0

        # Visualization control
        self.visualization_speed = 200
        self.is_visualizing = False
        self.is_paused = False
        self.visualization_steps = []
        self.current_step = 0

        # Animation states
        self.highlighted_points = []
        self.active_comparisons = []

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        title_label = ttk.Label(header_frame,
                               text="Closest Pair of Points Visualizer",
                               font=("Arial", 18, "bold"))
        title_label.pack()
        subtitle_label = ttk.Label(header_frame,
                                  text="Divide & Conquer Algorithm - O(n log n)",
                                  font=("Arial", 10))
        subtitle_label.pack()

        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2, padding="5")
        left_panel.grid(row=1, column=0, sticky=(tk.N, tk.S), padx=(0, 5))

        # Control sections
        self.create_point_controls(left_panel)
        self.create_visualization_controls(left_panel)
        self.create_algorithm_info(left_panel)

        # Canvas area
        canvas_container = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2, padding="5")
        canvas_container.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Canvas header
        canvas_header = ttk.Frame(canvas_container)
        canvas_header.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(canvas_header, text="Point Canvas",
                 font=("Arial", 12)).pack(side=tk.LEFT)
        self.canvas_status = ttk.Label(canvas_header, text="Ready")
        self.canvas_status.pack(side=tk.RIGHT)

        # Canvas
        self.canvas = tk.Canvas(canvas_container,
                               bg=self.theme["canvas_bg"],
                               relief=tk.FLAT,
                               borderwidth=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw initial grid
        self.draw_canvas_grid()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<B1-Motion>", self.add_point_drag)
        self.canvas.bind("<Motion>", self.show_mouse_position)

        # Right panel - Details
        right_panel = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2, padding="5", width=250)
        right_panel.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.E), padx=(5, 0))
        right_panel.grid_propagate(False)
        self.create_details_panel(right_panel)

        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.create_footer(footer_frame)

    def create_point_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Point Controls", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Add points buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add Point",
                  command=self.add_random_point).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Random Set",
                  command=self.add_random_points).pack(side=tk.LEFT)

        # Point count slider
        slider_frame = ttk.Frame(frame)
        slider_frame.pack(fill=tk.X, pady=10)
        ttk.Label(slider_frame, text="Points:").pack(side=tk.LEFT)
        self.point_count_var = tk.IntVar(value=15)
        ttk.Scale(slider_frame, from_=5, to=50,
                 orient=tk.HORIZONTAL,
                 variable=self.point_count_var).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Clear button
        ttk.Button(frame, text="Clear All",
                  command=self.clear_points).pack(fill=tk.X, pady=5)

        # Instructions
        instr_text = "Instructions:\n• Click to add points\n• Drag to add multiple\n• At least 2 points needed"
        ttk.Label(frame, text=instr_text,
                 justify=tk.LEFT).pack(fill=tk.X, pady=(10, 0))

    def create_visualization_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))

        # Control buttons
        control_grid = ttk.Frame(frame)
        control_grid.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(control_grid, text="Start",
                                   command=self.start_visualization)
        self.start_btn.grid(row=0, column=0, padx=2, pady=2, sticky=tk.EW)
        
        self.pause_btn = ttk.Button(control_grid, text="Pause",
                                   command=self.toggle_pause,
                                   state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=1, padx=2, pady=2, sticky=tk.EW)
        
        ttk.Button(control_grid, text="Step",
                  command=self.step_forward).grid(row=1, column=0, padx=2, pady=2, sticky=tk.EW)
        ttk.Button(control_grid, text="Back",
                  command=self.step_backward).grid(row=1, column=1, padx=2, pady=2, sticky=tk.EW)
        
        control_grid.columnconfigure(0, weight=1)
        control_grid.columnconfigure(1, weight=1)

        # Speed control
        speed_frame = ttk.Frame(frame)
        speed_frame.pack(fill=tk.X, pady=10)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=200)
        ttk.Scale(speed_frame, from_=50, to=1000,
                 orient=tk.HORIZONTAL,
                 variable=self.speed_var,
                 command=self.update_speed).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Instant solve button
        ttk.Button(frame, text="Solve Instantly",
                  command=self.find_closest_no_visual).pack(fill=tk.X, pady=(5, 0))

    def create_algorithm_info(self, parent):
        frame = ttk.LabelFrame(parent, text="Algorithm Info", padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        info_text = """Divide & Conquer Steps:
1. Sort points by x-coordinate
2. Recursively divide into halves
3. Find closest in each half
4. Check strip (7 points max)

Complexity:
• Brute Force: O(n²)
• D&C: O(n log n)"""
        
        ttk.Label(frame, text=info_text,
                 justify=tk.LEFT).pack(fill=tk.BOTH, expand=True)

    def create_details_panel(self, parent):
        # Current step info
        step_frame = ttk.LabelFrame(parent, text="Current Step", padding="10")
        step_frame.pack(fill=tk.X, pady=(0, 10))
        self.step_info = tk.StringVar(value="Ready")
        ttk.Label(step_frame, textvariable=self.step_info,
                 wraplength=230,
                 justify=tk.LEFT).pack(fill=tk.X)

        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        self.stats_text = tk.StringVar()
        self.stats_text.set("Points: 0\nClosest Distance: N/A")
        ttk.Label(stats_frame, textvariable=self.stats_text,
                 justify=tk.LEFT).pack(fill=tk.X)

        # Legend
        legend_frame = ttk.LabelFrame(parent, text="Legend", padding="10")
        legend_frame.pack(fill=tk.X)
        
        legend_items = [
            ("○", "Regular Point", self.theme["accent"]),
            ("●", "Closest Pair", self.theme["danger"]),
            ("──", "Division Line", self.theme["success"]),
            ("▆", "Strip Area", self.theme["warning"]),
            ("···", "Comparison", "#666666"),
        ]
        
        for symbol, text, color in legend_items:
            item_frame = ttk.Frame(legend_frame)
            item_frame.pack(fill=tk.X, pady=2)
            tk.Label(item_frame, text=symbol, fg=color,
                    bg=self.theme["bg"]).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(item_frame, text=text).pack(side=tk.LEFT)

    def create_footer(self, parent):
        # Progress bar
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=5)
        ttk.Label(progress_frame, text="Progress:").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Status message
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(parent, textvariable=self.status_var).pack(fill=tk.X, pady=(5, 0))

        # Performance info
        perf_frame = ttk.Frame(parent)
        perf_frame.pack(fill=tk.X, pady=(5, 0))
        self.perf_text = tk.StringVar(value="Comparisons: 0 | Time: 0ms")
        ttk.Label(perf_frame, textvariable=self.perf_text).pack(side=tk.RIGHT)

    def draw_canvas_grid(self):
        """Draw a simple grid on the canvas"""
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 500
        
        # Draw vertical lines
        for x in range(0, width, 50):
            self.canvas.create_line(x, 0, x, height,
                                   fill=self.theme["grid"],
                                   width=0.5, tags="grid")
        # Draw horizontal lines
        for y in range(0, height, 50):
            self.canvas.create_line(0, y, width, y,
                                   fill=self.theme["grid"],
                                   width=0.5, tags="grid")

    def add_point(self, event):
        if self.is_visualizing and not self.is_paused:
            return
            
        self.point_counter += 1
        point = EnhancedPoint(event.x, event.y, self.point_counter)
        self.points.append(point)
        
        # Simple point drawing
        self.draw_point(point, self.theme["accent"])
        self.update_stats()
        self.canvas_status.config(text=f"Point {self.point_counter} at ({event.x}, {event.y})")

    def add_point_drag(self, event):
        if self.is_visualizing:
            return
            
        # Add point with spacing
        if len(self.points) == 0 or (abs(event.x - self.points[-1].x) > 10 or abs(event.y - self.points[-1].y) > 10):
            self.add_point(event)

    def add_random_point(self):
        canvas_width = self.canvas.winfo_width() or 700
        canvas_height = self.canvas.winfo_height() or 500
        x = 50 + (canvas_width - 100) * (0.1 + 0.8 * (hash(str(time.time())) % 1000) / 1000)
        y = 50 + (canvas_height - 100) * (0.1 + 0.8 * (hash(str(time.time() + 1000)) % 1000) / 1000)
        
        self.point_counter += 1
        point = EnhancedPoint(x, y, self.point_counter)
        self.points.append(point)
        self.draw_point(point, self.theme["accent"])
        self.update_stats()
        self.canvas_status.config(text=f"Random point {self.point_counter} added")

    def add_random_points(self):
        count = self.point_count_var.get()
        
        if self.is_visualizing:
            return
            
        self.clear_points()
        canvas_width = self.canvas.winfo_width() or 700
        canvas_height = self.canvas.winfo_height() or 500
        
        for i in range(count):
            x = 50 + (canvas_width - 100) * (0.1 + 0.8 * (i / count))
            y = 50 + (canvas_height - 100) * (0.1 + 0.8 * ((hash(str(i)) % 1000) / 1000))
            
            self.point_counter += 1
            point = EnhancedPoint(x, y, self.point_counter)
            self.points.append(point)
            self.draw_point(point, self.theme["accent"])
        
        self.update_stats()

    def draw_point(self, point, color, size=6, tag="point"):
        x, y = point.x, point.y
        # Draw point
        self.canvas.create_oval(x - size, y - size,
                               x + size, y + size,
                               fill=color, outline="black",
                               width=1, tags=tag)
        
        # Draw point ID if not too many points
        if point.id and len(self.points) <= 30:
            self.canvas.create_text(x, y - size - 8,
                                   text=f"P{point.id}",
                                   fill=color,
                                   font=("Arial", 8),
                                   tags=tag)

    def clear_points(self):
        self.is_visualizing = False
        self.is_paused = False
        self.current_step = 0
        self.visualization_steps = []
        
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.pause_btn.config(text="Pause")
        self.progress_var.set(0)
        self.step_info.set("Ready")
        
        self.points = []
        self.closest_pair = (None, None)
        self.min_distance = float('inf')
        self.point_counter = 0
        
        # Clear canvas
        for item in self.canvas.find_all():
            if "grid" not in self.canvas.gettags(item):
                self.canvas.delete(item)
        self.draw_canvas_grid()
        self.update_stats()
        self.status_var.set("Ready")
        self.canvas_status.config(text="Canvas cleared")

    def update_speed(self, value):
        self.visualization_speed = int(float(value))

    def update_stats(self):
        if len(self.points) > 0:
            dist_text = f"{self.min_distance:.2f}" if self.min_distance != float('inf') else "N/A"
            self.stats_text.set(f"Points: {len(self.points)}\nClosest Distance: {dist_text}")
        else:
            self.stats_text.set("Points: 0\nClosest Distance: N/A")

    def show_mouse_position(self, event):
        self.canvas.delete("mouse_pos")
        self.canvas.create_text(10, 10,
                               text=f"({event.x}, {event.y})",
                               anchor=tk.NW,
                               fill="#666666",
                               font=("Arial", 9),
                               tags="mouse_pos")

    def start_visualization(self):
        if len(self.points) < 2:
            messagebox.showinfo("Not Enough Points", "Please add at least 2 points to start!")
            return
            
        if self.is_visualizing:
            return
            
        self.is_visualizing = True
        self.is_paused = False
        self.visualization_steps = []
        self.current_step = 0
        
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="Pause")
        
        # Clear previous visualization
        self.canvas.delete("line")
        self.canvas.delete("closest")
        self.canvas.delete("strip")
        self.canvas.delete("divider")
        self.canvas.delete("temp")
        
        # Sort points
        points_sorted = sorted(self.points, key=lambda p: p.x)
        
        self.status_var.set("Generating steps...")
        self.root.update()
        self.generate_visualization_steps(points_sorted)
        
        self.status_var.set("Visualization started")
        self.progress_var.set(0)
        self.root.after(100, self.run_visualization)

    def generate_visualization_steps(self, points):
        """Generate visualization steps"""
        def dc_with_steps(points_x, depth=0, side=""):
            if len(points_x) <= 3:
                step = {
                    "type": "base_case",
                    "points": points_x[:],
                    "depth": depth,
                    "side": side,
                    "message": f"Base case ({side}) - {len(points_x)} points\nUsing brute force"
                }
                self.visualization_steps.append(step)
                
                min_dist = float('inf')
                closest = (None, None)
                
                for i in range(len(points_x)):
                    for j in range(i+1, len(points_x)):
                        dist = points_x[i].distance_to(points_x[j])
                        step_compare = {
                            "type": "compare",
                            "points": [points_x[i], points_x[j]],
                            "distance": dist,
                            "depth": depth,
                            "side": side,
                            "message": f"Comparing {points_x[i]} ↔ {points_x[j]}\nDistance = {dist:.2f}"
                        }
                        self.visualization_steps.append(step_compare)
                        
                        if dist < min_dist:
                            min_dist = dist
                            closest = (points_x[i], points_x[j])
                
                step_result = {
                    "type": "result",
                    "min_distance": min_dist,
                    "closest_pair": closest,
                    "depth": depth,
                    "side": side,
                    "message": f"Result ({side})\nDistance = {min_dist:.2f}"
                }
                self.visualization_steps.append(step_result)
                return min_dist, closest

            # Divide step
            mid = len(points_x) // 2
            mid_x = points_x[mid].x
            
            step_divide = {
                "type": "divide",
                "mid_x": mid_x,
                "left_points": points_x[:mid],
                "right_points": points_x[mid:],
                "depth": depth,
                "side": side,
                "message": f"Divide (Depth {depth})\nAt x = {mid_x:.1f}\nLeft: {len(points_x[:mid])}, Right: {len(points_x[mid:])}"
            }
            self.visualization_steps.append(step_divide)

            # Recursive calls
            left_min, left_closest = dc_with_steps(points_x[:mid], depth + 1, "L")
            right_min, right_closest = dc_with_steps(points_x[mid:], depth + 1, "R")

            # Combine results
            min_dist = min(left_min, right_min)
            closest = left_closest if left_min < right_min else right_closest
            
            step_combine = {
                "type": "combine",
                "min_dist": min_dist,
                "closest": closest,
                "depth": depth,
                "side": side,
                "message": f"Combine (Depth {depth})\nCurrent min: {min_dist:.2f}"
            }
            self.visualization_steps.append(step_combine)

            # Check strip
            strip_points = [p for p in points_x if abs(p.x - mid_x) < min_dist]
            strip_points_sorted = sorted(strip_points, key=lambda p: p.y)
            
            step_strip = {
                "type": "strip",
                "mid_x": mid_x,
                "strip_width": 2 * min_dist,
                "strip_points": strip_points_sorted,
                "depth": depth,
                "side": side,
                "message": f"Checking strip\nPoints in strip: {len(strip_points_sorted)}"
            }
            self.visualization_steps.append(step_strip)

            # Check points in strip
            for i in range(len(strip_points_sorted)):
                for j in range(i+1, min(i+8, len(strip_points_sorted))):
                    if strip_points_sorted[j].y - strip_points_sorted[i].y >= min_dist:
                        break
                        
                    dist = strip_points_sorted[i].distance_to(strip_points_sorted[j])
                    step_compare_strip = {
                        "type": "compare_strip",
                        "points": [strip_points_sorted[i], strip_points_sorted[j]],
                        "distance": dist,
                        "depth": depth,
                        "side": side,
                        "message": f"Strip comparison\nDistance = {dist:.2f}"
                    }
                    self.visualization_steps.append(step_compare_strip)
                    
                    if dist < min_dist:
                        min_dist = dist
                        closest = (strip_points_sorted[i], strip_points_sorted[j])

            step_final = {
                "type": "final",
                "min_distance": min_dist,
                "closest_pair": closest,
                "depth": depth,
                "side": side,
                "message": f"Depth {depth} result\nDistance = {min_dist:.2f}"
            }
            self.visualization_steps.append(step_final)

            return min_dist, closest

        # Add initial step
        initial_step = {
            "type": "start",
            "points": points[:],
            "message": f"Starting algorithm\n{len(points)} points"
        }
        self.visualization_steps.append(initial_step)

        # Run the algorithm
        start_time = time.time()
        self.min_distance, self.closest_pair = dc_with_steps(points)
        elapsed_time = (time.time() - start_time) * 1000

        # Add final summary
        summary_step = {
            "type": "summary",
            "min_distance": self.min_distance,
            "closest_pair": self.closest_pair,
            "time_ms": elapsed_time,
            "total_steps": len(self.visualization_steps),
            "message": f"Algorithm complete\nDistance: {self.min_distance:.2f}\nTime: {elapsed_time:.1f}ms"
        }
        self.visualization_steps.append(summary_step)

    def run_visualization(self):
        if not self.is_visualizing or self.is_paused:
            return
            
        if self.current_step < len(self.visualization_steps):
            progress = (self.current_step / len(self.visualization_steps)) * 100
            self.progress_var.set(progress)
            self.visualize_step(self.current_step)
            self.current_step += 1
            self.root.after(self.visualization_speed, self.run_visualization)
        else:
            self.is_visualizing = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.status_var.set("Visualization complete")
            messagebox.showinfo("Complete", f"Algorithm finished!\nClosest distance: {self.min_distance:.2f}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="Resume")
            self.status_var.set("Paused")
        else:
            self.pause_btn.config(text="Pause")
            self.status_var.set("Resumed")
            self.run_visualization()

    def step_forward(self):
        if not self.is_visualizing:
            self.start_visualization()
            return
            
        if self.is_paused and self.current_step < len(self.visualization_steps):
            self.visualize_step(self.current_step)
            self.current_step += 1
            self.progress_var.set((self.current_step / len(self.visualization_steps)) * 100)

    def step_backward(self):
        if self.is_visualizing and self.current_step > 0 and self.is_paused:
            self.current_step -= 1
            self.redraw_to_step(self.current_step)

    def redraw_to_step(self, step_idx):
        # Clear and redraw up to step_idx
        self.canvas.delete("all")
        self.draw_canvas_grid()
        
        # Draw all points
        for point in self.points:
            self.draw_point(point, self.theme["accent"], 6)
        
        # Replay steps up to step_idx
        for i in range(step_idx):
            step = self.visualization_steps[i]
            
            if step["type"] == "divide":
                mid_x = step["mid_x"]
                canvas_height = self.canvas.winfo_height() or 500
                self.canvas.create_line(mid_x, 0, mid_x, canvas_height,
                                       fill=self.theme["success"], width=2, tags="divider", dash=(5, 2))
            elif step["type"] == "strip":
                mid_x = step["mid_x"]
                strip_width = step["strip_width"]
                canvas_height = self.canvas.winfo_height() or 500
                self.canvas.create_rectangle(
                    mid_x - strip_width/2, 0,
                    mid_x + strip_width/2, canvas_height,
                    fill=self.theme["warning"], stipple="gray50",
                    outline="", tags="strip"
                )
            elif step["type"] in ["compare", "compare_strip"]:
                p1, p2 = step["points"]
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                       fill="#666666", width=1,
                                       dash=(2, 2), tags="temp")
            elif step["type"] in ["result", "final", "summary"]:
                if step["closest_pair"][0] and step["closest_pair"][1]:
                    p1, p2 = step["closest_pair"]
                    self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                           fill=self.theme["danger"], width=2,
                                           tags="line")
                    self.draw_point(p1, self.theme["danger"], 8)
                    self.draw_point(p2, self.theme["danger"], 8)
        
        # Update step info
        if step_idx > 0:
            self.step_info.set(self.visualization_steps[step_idx - 1]["message"])
        else:
            self.step_info.set("Ready")

    def visualize_step(self, step_idx):
        step = self.visualization_steps[step_idx]
        
        # Clear temporary drawings
        self.canvas.delete("temp")
        self.canvas.delete("highlight")
        
        # Update step info
        self.step_info.set(step["message"])
        
        # Draw based on step type
        if step["type"] == "divide":
            mid_x = step["mid_x"]
            canvas_height = self.canvas.winfo_height() or 500
            self.canvas.create_line(mid_x, 0, mid_x, canvas_height,
                                   fill=self.theme["success"], width=2, tags="divider", dash=(5, 2))
            self.status_var.set(f"Dividing at x = {mid_x:.1f}")
            
        elif step["type"] == "strip":
            mid_x = step["mid_x"]
            strip_width = step["strip_width"]
            canvas_height = self.canvas.winfo_height() or 500
            self.canvas.create_rectangle(
                mid_x - strip_width/2, 0,
                mid_x + strip_width/2, canvas_height,
                fill=self.theme["warning"], stipple="gray50",
                outline="", tags="strip"
            )
            self.status_var.set(f"Strip with {len(step['strip_points'])} points")
            
        elif step["type"] in ["compare", "compare_strip"]:
            p1, p2 = step["points"]
            # Draw comparison line
            self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                   fill="#666666", width=1,
                                   dash=(2, 2), tags="temp")
            # Highlight points
            self.draw_point(p1, "#666666", 8, "highlight")
            self.draw_point(p2, "#666666", 8, "highlight")
            # Show distance
            mid_x = (p1.x + p2.x) / 2
            mid_y = (p1.y + p2.y) / 2
            self.canvas.create_text(mid_x, mid_y,
                                   text=f"{step['distance']:.2f}",
                                   fill="#666666", font=("Arial", 9),
                                   tags="temp")
            self.status_var.set(f"Distance = {step['distance']:.2f}")
            
        elif step["type"] in ["result", "final"]:
            if step["closest_pair"][0]:
                p1, p2 = step["closest_pair"]
                # Draw connection
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                       fill=self.theme["danger"], width=2,
                                       tags="line")
                # Highlight points
                self.draw_point(p1, self.theme["danger"], 8, "highlight")
                self.draw_point(p2, self.theme["danger"], 8, "highlight")
                # Show distance
                self.canvas.create_text((p1.x + p2.x)/2, (p1.y + p2.y)/2 - 15,
                                       text=f"{step['min_distance']:.2f}",
                                       fill=self.theme["danger"], font=("Arial", 10),
                                       tags="highlight")
            self.status_var.set(f"Found: {step['min_distance']:.2f}")
            
        elif step["type"] == "summary":
            if step["closest_pair"][0]:
                p1, p2 = step["closest_pair"]
                # Clear previous
                self.canvas.delete("line")
                self.canvas.delete("closest")
                
                # Draw all points normally
                for point in self.points:
                    if point != p1 and point != p2:
                        self.draw_point(point, self.theme["accent"], 6)
                
                # Draw final pair
                self.draw_point(p1, self.theme["danger"], 10, "closest")
                self.draw_point(p2, self.theme["danger"], 10, "closest")
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                       fill=self.theme["danger"], width=3,
                                       tags=("line", "closest"))
                # Show final distance
                self.canvas.create_text((p1.x + p2.x)/2, (p1.y + p2.y)/2,
                                       text=f"{step['min_distance']:.2f}",
                                       fill=self.theme["danger"], font=("Arial", 11, "bold"),
                                       tags="closest")
                
                # Update global values
                self.min_distance = step['min_distance']
                self.closest_pair = step['closest_pair']
                self.update_stats()
                self.perf_text.set(f"Steps: {len(self.visualization_steps)} | Time: {step['time_ms']:.1f}ms")

    def find_closest_no_visual(self):
        if len(self.points) < 2:
            messagebox.showinfo("Not Enough Points", "Please add at least 2 points!")
            return
            
        # Clear previous
        self.canvas.delete("line")
        self.canvas.delete("closest")
        
        # Sort and run
        points_sorted = sorted(self.points, key=lambda p: p.x)
        start_time = time.time()
        self.min_distance, self.closest_pair = self.closest_pair_dc(points_sorted)
        elapsed_time = (time.time() - start_time) * 1000
        
        # Draw result
        if self.closest_pair[0] and self.closest_pair[1]:
            # Draw all points
            for point in self.points:
                if point != self.closest_pair[0] and point != self.closest_pair[1]:
                    self.draw_point(point, self.theme["accent"], 6)
            # Highlight closest pair
            self.draw_point(self.closest_pair[0], self.theme["danger"], 10, "closest")
            self.draw_point(self.closest_pair[1], self.theme["danger"], 10, "closest")
            # Draw connection
            self.canvas.create_line(self.closest_pair[0].x, self.closest_pair[0].y,
                                   self.closest_pair[1].x, self.closest_pair[1].y,
                                   fill=self.theme["danger"], width=3, tags=("line", "closest"))
            # Show distance
            self.canvas.create_text((self.closest_pair[0].x + self.closest_pair[1].x)/2,
                                   (self.closest_pair[0].y + self.closest_pair[1].y)/2,
                                   text=f"{self.min_distance:.2f}",
                                   fill=self.theme["danger"], font=("Arial", 11),
                                   tags="closest")
        
        self.update_stats()
        self.status_var.set(f"Solved: {self.min_distance:.2f}")
        self.perf_text.set(f"Time: {elapsed_time:.1f}ms")

    def closest_pair_dc(self, points_x):
        """Divide and conquer algorithm without visualization"""
        def brute_force(points):
            min_dist = float('inf')
            closest = (None, None)
            for i in range(len(points)):
                for j in range(i+1, len(points)):
                    dist = points[i].distance_to(points[j])
                    if dist < min_dist:
                        min_dist = dist
                        closest = (points[i], points[j])
            return min_dist, closest

        def dc_recursive(points_x):
            n = len(points_x)
            if n <= 3:
                return brute_force(points_x)

            mid = n // 2
            mid_point = points_x[mid]

            left_min, left_closest = dc_recursive(points_x[:mid])
            right_min, right_closest = dc_recursive(points_x[mid:])

            min_dist = min(left_min, right_min)
            closest = left_closest if left_min < right_min else right_closest

            strip = [p for p in points_x if abs(p.x - mid_point.x) < min_dist]
            strip.sort(key=lambda p: p.y)

            for i in range(len(strip)):
                for j in range(i+1, min(i+8, len(strip))):
                    if strip[j].y - strip[i].y >= min_dist:
                        break
                    dist = strip[i].distance_to(strip[j])
                    if dist < min_dist:
                        min_dist = dist
                        closest = (strip[i], strip[j])

            return min_dist, closest

        return dc_recursive(points_x)

def main():
    root = tk.Tk()
    app = EnhancedClosestPairVisualizer(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()