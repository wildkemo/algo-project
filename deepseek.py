import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
from tkinter import font as tkfont
from tkinter import colorchooser

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
        self.root.title("✨ Closest Pair of Points - Interactive Visualizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2b2b2b")

        # Custom colors
        self.theme = {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "accent": "#4ecdc4",
            "secondary": "#45b7d1",
            "danger": "#ff6b6b",
            "success": "#98c379",
            "warning": "#e5c07b",
            "info": "#61afef",
            "canvas_bg": "#1e1e1e",
            "grid": "#3c3c3c"
        }

        # Points storage
        self.points = []
        self.closest_pair = (None, None)
        self.min_distance = float('inf')
        self.point_counter = 0

        # Visualization control
        self.visualization_speed = 300  # ms between steps
        self.is_visualizing = False
        self.is_paused = False
        self.visualization_steps = []
        self.current_step = 0

        # Animation states
        self.highlighted_points = []
        self.active_comparisons = []

        self.setup_ui()

    def setup_ui(self):
        # Configure custom styles
        self.setup_styles()

        # Main container
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_frame, style="Header.TFrame")
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        title_label = ttk.Label(header_frame,
                               text="🎯 Closest Pair of Points Visualizer",
                               font=("Arial", 24, "bold"),
                               style="Header.TLabel")
        title_label.pack(pady=10)
        subtitle_label = ttk.Label(header_frame,
                                  text="Divide & Conquer Algorithm - O(n log n) Complexity",
                                  font=("Arial", 12),
                                  style="Subtitle.TLabel")
        subtitle_label.pack()

        # Left panel - Controls
        left_panel = ttk.Frame(main_frame, style="Panel.TFrame")
        left_panel.grid(row=1, column=0, sticky=(tk.N, tk.S), padx=(0, 15))

        # Control sections
        self.create_point_controls(left_panel)
        self.create_visualization_controls(left_panel)
        self.create_algorithm_info(left_panel)

        # Canvas area
        canvas_container = ttk.Frame(main_frame, style="Panel.TFrame")
        canvas_container.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Canvas header
        canvas_header = ttk.Frame(canvas_container, style="CanvasHeader.TFrame")
        canvas_header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(canvas_header, text="📐 Point Canvas",
                 font=("Arial", 14, "bold"),
                 style="CanvasHeader.TLabel").pack(side=tk.LEFT)
        self.canvas_status = ttk.Label(canvas_header,
                                      text="Ready to draw points",
                                      style="CanvasStatus.TLabel")
        self.canvas_status.pack(side=tk.RIGHT)

        # Canvas with grid
        self.canvas = tk.Canvas(canvas_container,
                               bg=self.theme["canvas_bg"],
                               relief=tk.FLAT,
                               borderwidth=0,
                               highlightthickness=2,
                               highlightbackground=self.theme["accent"])
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Draw grid on canvas
        self.draw_canvas_grid()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.add_point)
        self.canvas.bind("<B1-Motion>", self.add_point_drag)
        self.canvas.bind("<Motion>", self.show_mouse_position)

        # Right panel - Details
        right_panel = ttk.Frame(main_frame, style="Panel.TFrame", width=300)
        right_panel.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.E), padx=(15, 0))
        right_panel.grid_propagate(False)
        self.create_details_panel(right_panel)

        # Footer - Progress and stats
        footer_frame = ttk.Frame(main_frame, style="Footer.TFrame")
        footer_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))
        self.create_footer(footer_frame)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure("Header.TFrame", background=self.theme["bg"])
        style.configure("Header.TLabel", background=self.theme["bg"], foreground=self.theme["accent"])
        style.configure("Subtitle.TLabel", background=self.theme["bg"], foreground=self.theme["info"])
        style.configure("Panel.TFrame", background="#3c3c3c", relief=tk.RAISED, borderwidth=1)
        style.configure("CanvasHeader.TFrame", background="#2d2d2d")
        style.configure("CanvasHeader.TLabel", background="#2d2d2d", foreground=self.theme["fg"])
        style.configure("CanvasStatus.TLabel", background="#2d2d2d", foreground=self.theme["success"])
        style.configure("Footer.TFrame", background="#252526")
        style.configure("Footer.TLabel", background="#252526", foreground=self.theme["fg"])

        # Button styles
        style.configure("Accent.TButton",
                       background=self.theme["accent"],
                       foreground="black",
                       borderwidth=0,
                       focusthickness=3,
                       focuscolor=self.theme["accent"])
        style.map("Accent.TButton",
                 background=[('active', self.theme["secondary"])])
        style.configure("Success.TButton",
                       background=self.theme["success"],
                       foreground="black")
        style.map("Success.TButton",
                 background=[('active', "#7ca85e")])
        style.configure("Warning.TButton",
                       background=self.theme["warning"],
                       foreground="black")
        style.configure("Danger.TButton",
                       background=self.theme["danger"],
                       foreground="white")

        # LabelFrame styles
        style.configure("Custom.TLabelframe",
                       background="#3c3c3c",
                       foreground=self.theme["accent"])
        style.configure("Custom.TLabelframe.Label",
                       background="#3c3c3c",
                       foreground=self.theme["accent"],
                       font=("Arial", 11, "bold"))

        # --- Custom Progress Bar Style ---
        style.configure("custom.Horizontal.TProgressbar",
                       troughcolor=self.theme["grid"],
                       background=self.theme["accent"],
                       lightcolor=self.theme["secondary"],
                       darkcolor=self.theme["accent"],
                       bordercolor="#252526", # Match footer
                       thickness=15) # Adjust thickness as needed
        # --- End Custom Progress Bar Style ---

    def create_point_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="🎮 Point Controls",
                              style="Custom.TLabelframe", padding="10")
        frame.pack(fill=tk.X, pady=(0, 15))

        # Add points buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="➕ Add Point",
                  command=self.add_random_point, # Renamed for single click
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🎲 Random Set",
                  command=self.add_random_points_with_tooltip, # New function for tooltip
                  style="Accent.TButton").pack(side=tk.LEFT)

        # Point count slider
        slider_frame = ttk.Frame(frame)
        slider_frame.pack(fill=tk.X, pady=10)
        ttk.Label(slider_frame, text="Random Points:").pack(side=tk.LEFT)
        self.point_count_var = tk.IntVar(value=15)
        point_slider = ttk.Scale(slider_frame, from_=5, to=50,
                                orient=tk.HORIZONTAL,
                                variable=self.point_count_var)
        point_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Clear button
        ttk.Button(frame, text="🗑️ Clear All",
                  command=self.clear_points,
                  style="Danger.TButton").pack(fill=tk.X, pady=5)

        # Instructions
        instr_text = """💡 Instructions:
• Click on canvas to add points
• Drag mouse to add multiple points
• Right-click on point to remove it""" # Note: Right-click remove not implemented in original code
        instr_label = ttk.Label(frame, text=instr_text,
                               justify=tk.LEFT,
                               background="#3c3c3c",
                               foreground=self.theme["info"])
        instr_label.pack(fill=tk.X, pady=(10, 0))

    def create_visualization_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="🎬 Visualization",
                              style="Custom.TLabelframe", padding="10")
        frame.pack(fill=tk.X, pady=(0, 15))

        # Main control buttons
        control_grid = ttk.Frame(frame)
        control_grid.pack(fill=tk.X, pady=5)
        self.start_btn = ttk.Button(control_grid, text="▶️ Start",
                                   command=self.start_visualization,
                                   style="Success.TButton")
        self.start_btn.grid(row=0, column=0, padx=2, pady=2, sticky=tk.EW)
        self.pause_btn = ttk.Button(control_grid, text="⏸️ Pause",
                                   command=self.toggle_pause,
                                   state=tk.DISABLED,
                                   style="Warning.TButton")
        self.pause_btn.grid(row=0, column=1, padx=2, pady=2, sticky=tk.EW)
        ttk.Button(control_grid, text="⏩ Step", # Renamed for clarity
                  command=self.step_forward,
                  style="Accent.TButton").grid(row=1, column=0, padx=2, pady=2, sticky=tk.EW)
        ttk.Button(control_grid, text="⏪ Step Back", # Renamed for clarity
                  command=self.step_backward,
                  style="Accent.TButton").grid(row=1, column=1, padx=2, pady=2, sticky=tk.EW)
        control_grid.columnconfigure(0, weight=1)
        control_grid.columnconfigure(1, weight=1)

        # Speed control
        speed_frame = ttk.Frame(frame)
        speed_frame.pack(fill=tk.X, pady=10)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.IntVar(value=300)
        speed_slider = ttk.Scale(speed_frame, from_=50, to=2000,
                                orient=tk.HORIZONTAL,
                                variable=self.speed_var,
                                command=self.update_speed)
        speed_slider.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Instant solve button
        ttk.Button(frame, text="⚡ Solve Instantly",
                  command=self.find_closest_no_visual,
                  style="Accent.TButton").pack(fill=tk.X, pady=(5, 0))

    def create_algorithm_info(self, parent):
        frame = ttk.LabelFrame(parent, text="📊 Algorithm Info",
                              style="Custom.TLabelframe", padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        info_text = """🎯 Divide & Conquer Steps:
1. ✅ Sort points by x-coordinate
2. 📐 Recursively divide into halves
3. 🔍 Find closest in each half
4. 📏 Check strip (7 points max)
⚡ Complexity:
• Brute Force: O(n²)
• D&C: O(n log n)
✨ Visualization Legend:
• 🔵 Regular points
• 🔴 Current closest pair
• 🟢 Division line
• 🟡 Strip area
• ⚫ Compared points
• 🟣 Final result"""
        info_label = ttk.Label(frame, text=info_text,
                              justify=tk.LEFT,
                              background="#3c3c3c",
                              foreground=self.theme["fg"],
                              font=("Consolas", 9))
        info_label.pack(fill=tk.BOTH, expand=True)

    def create_details_panel(self, parent):
        # Current step info
        step_frame = ttk.LabelFrame(parent, text="📝 Current Step",
                                   style="Custom.TLabelframe", padding="10")
        step_frame.pack(fill=tk.X, pady=(0, 15))
        self.step_info = tk.StringVar(value="Waiting for visualization...")
        step_label = ttk.Label(step_frame, textvariable=self.step_info,
                              wraplength=250,
                              justify=tk.LEFT,
                              background="#3c3c3c",
                              foreground=self.theme["success"],
                              font=("Arial", 10))
        step_label.pack(fill=tk.X)

        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="📈 Statistics",
                                    style="Custom.TLabelframe", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        self.stats_text = tk.StringVar()
        self.stats_text.set("Points: 0\nComparisons: 0\nClosest Distance: N/A")
        stats_label = ttk.Label(stats_frame, textvariable=self.stats_text,
                               justify=tk.LEFT,
                               background="#3c3c3c",
                               foreground=self.theme["info"],
                               font=("Arial", 10))
        stats_label.pack(fill=tk.X)

        # Legend
        legend_frame = ttk.LabelFrame(parent, text="🌈 Legend",
                                     style="Custom.TLabelframe", padding="10")
        legend_frame.pack(fill=tk.X)
        legend_items = [
            ("🔵", "Regular Point", "#4ecdc4"),
            ("🔴", "Closest Pair", "#ff6b6b"),
            ("🟢", "Division Line", "#98c379"),
            ("🟡", "Strip Area", "#e5c07b"),
            ("⚫", "Comparison", "#61afef"),
            ("🟣", "Final Result", "#c678dd")
        ]
        for icon, text, color in legend_items:
            item_frame = ttk.Frame(legend_frame)
            item_frame.pack(fill=tk.X, pady=2)
            color_label = tk.Label(item_frame, text="●", fg=color,
                                  bg="#3c3c3c", font=("Arial", 14))
            color_label.pack(side=tk.LEFT, padx=(0, 10))
            ttk.Label(item_frame, text=text,
                     background="#3c3c3c",
                     foreground=self.theme["fg"]).pack(side=tk.LEFT)

    def create_footer(self, parent):
        # Progress bar
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=5)
        ttk.Label(progress_frame, text="Progress:",
                 style="Footer.TLabel").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        # Use the custom style here
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           style="custom.Horizontal.TProgressbar")
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # Status messages
        self.status_var = tk.StringVar(value="🎯 Ready to find the closest pair!")
        status_label = ttk.Label(parent, textvariable=self.status_var,
                                style="Footer.TLabel",
                                font=("Arial", 10))
        status_label.pack(fill=tk.X, pady=(5, 0))

        # Performance info
        perf_frame = ttk.Frame(parent)
        perf_frame.pack(fill=tk.X, pady=(5, 0))
        self.perf_text = tk.StringVar(value="Comparisons: 0 | Time: 0ms")
        perf_label = ttk.Label(perf_frame, textvariable=self.perf_text,
                              style="Footer.TLabel",
                              font=("Arial", 9))
        perf_label.pack(side=tk.RIGHT)

    def draw_canvas_grid(self):
        """Draw a grid on the canvas for better visualization"""
        width = self.canvas.winfo_width() or 800
        height = self.canvas.winfo_height() or 500
        # Draw vertical lines
        for x in range(0, width, 50):
            self.canvas.create_line(x, 0, x, height,
                                   fill=self.theme["grid"],
                                   width=1, tags="grid")
        # Draw horizontal lines
        for y in range(0, height, 50):
            self.canvas.create_line(0, y, width, y,
                                   fill=self.theme["grid"],
                                   width=1, tags="grid")
        # Draw coordinate indicators
        for x in range(100, width, 100):
            self.canvas.create_text(x, 10, text=str(x),
                                   fill=self.theme["grid"],
                                   font=("Arial", 8), tags="grid")
        for y in range(100, height, 100):
            self.canvas.create_text(10, y, text=str(y),
                                   fill=self.theme["grid"],
                                   font=("Arial", 8), tags="grid")

    def add_point(self, event):
        # Allow adding points only when not visualizing or paused during manual stepping
        if self.is_visualizing and not self.is_paused:
             # Prevent adding points during active visualization
             # You could add a status message here if desired
             return
        self.point_counter += 1
        point = EnhancedPoint(event.x, event.y, self.point_counter)
        self.points.append(point)
        # Draw point with animation
        self.animate_point_creation(point)
        self.update_stats()
        self.canvas_status.config(text=f"Point {self.point_counter} added at ({event.x}, {event.y})")
        # Tooltip removed from single click

    def add_point_drag(self, event):
        # Allow adding points via drag only when not visualizing
        if self.is_visualizing:
            return
        # Add point with debouncing
        if len(self.points) == 0 or (abs(event.x - self.points[-1].x) > 10 or abs(event.y - self.points[-1].y) > 10):
            self.add_point(event)

    def add_random_point(self):
        # Renamed function for single click button
        canvas_width = self.canvas.winfo_width() or 700
        canvas_height = self.canvas.winfo_height() or 500
        x = 50 + (canvas_width - 100) * (0.1 + 0.8 * (hash(str(time.time())) % 1000) / 1000)
        y = 50 + (canvas_height - 100) * (0.1 + 0.8 * (hash(str(time.time() + 1000)) % 1000) / 1000)
        self.point_counter += 1
        point = EnhancedPoint(x, y, self.point_counter)
        self.points.append(point)
        self.animate_point_creation(point)
        self.update_stats()
        self.canvas_status.config(text=f"Random point {self.point_counter} added")

    def add_random_points_with_tooltip(self):
        # New function to call original add_random_points and show tooltip
        self.add_random_points()
        self.show_info_popup("Random Points Generated",
                            f"Successfully generated {self.point_count_var.get()} random points.\nClick 'Start' to begin visualization!")

    def add_random_points(self, count=None):
        if count is None:
            count = self.point_count_var.get()
        # Allow adding points only when not visualizing
        if self.is_visualizing:
            return
        self.clear_points() # Clear existing points first
        canvas_width = self.canvas.winfo_width() or 700
        canvas_height = self.canvas.winfo_height() or 500
        for i in range(count):
            x = 50 + (canvas_width - 100) * (0.1 + 0.8 * (i / count))
            y = 50 + (canvas_height - 100) * (0.1 + 0.8 * ((hash(str(i)) % 1000) / 1000))
            self.point_counter += 1
            point = EnhancedPoint(x, y, self.point_counter)
            self.points.append(point)
            # Draw immediately for better performance
            self.draw_point(point, self.theme["accent"])
        self.update_stats()
        # Tooltip removed from here, handled in calling function

    def animate_point_creation(self, point):
        """Animate point appearance with ripple effect"""
        size = 6
        for i in range(5, 0, -1):
            radius = size + i * 2
            color = self.theme["accent"] if i % 2 else self.theme["secondary"]
            self.canvas.create_oval(point.x - radius, point.y - radius,
                                   point.x + radius, point.y + radius,
                                   outline=color, width=1, tags="temp_anim")
            self.canvas.update()
            time.sleep(0.02)
        self.canvas.delete("temp_anim")
        self.draw_point(point, self.theme["accent"])

    def draw_point(self, point, color, size=8, tag="point"):
        x, y = point.x, point.y
        # Draw outer ring
        self.canvas.create_oval(x - size - 2, y - size - 2,
                               x + size + 2, y + size + 2,
                               fill="white", outline="white", tags=tag)
        # Draw main point
        self.canvas.create_oval(x - size, y - size,
                               x + size, y + size,
                               fill=color, outline="white",
                               width=2, tags=tag)
        # Draw point ID
        if point.id and len(self.points) <= 30:
            self.canvas.create_text(x, y - size - 10,
                                   text=f"P{point.id}",
                                   fill=color,
                                   font=("Arial", 8, "bold"),
                                   tags=tag)

    def clear_points(self):
        # Ensure visualization is stopped before clearing
        self.is_visualizing = False
        self.is_paused = False
        self.current_step = 0
        self.visualization_steps = []
        # Update UI elements that might be active
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.pause_btn.config(text="⏸️ Pause") # Reset pause button text
        self.progress_var.set(0) # Reset progress bar
        self.step_info.set("Waiting for visualization...") # Reset step info

        # Clear internal lists
        self.points = []
        self.closest_pair = (None, None)
        self.min_distance = float('inf')
        self.point_counter = 0

        # Clear canvas
        for item in self.canvas.find_all():
            if "grid" not in self.canvas.gettags(item):
                self.canvas.delete(item)
        self.draw_canvas_grid() # Redraw grid
        self.update_stats()
        self.status_var.set("🎯 Ready to find the closest pair!")
        self.canvas_status.config(text="Canvas cleared. Click to add points.")

    def update_speed(self, value):
        self.visualization_speed = int(float(value))

    def update_stats(self):
        if len(self.points) > 0:
            self.stats_text.set(f"Points: {len(self.points)}\n"
                               f"Point IDs: 1-{self.point_counter}\n"
                               f"Closest Distance: {self.min_distance if self.min_distance != float('inf') else 'N/A'}")
        else:
            self.stats_text.set("Points: 0\nPoint IDs: N/A\nClosest Distance: N/A")

    def show_tooltip(self, x, y, text):
        """Show a temporary tooltip near the mouse"""
        # This function is kept but not used for single point clicks anymore
        tooltip = tk.Toplevel(self.root)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x + 20}+{y + 20}")
        label = ttk.Label(tooltip, text=text,
                         background="yellow", # Color changed for clarity
                         foreground="black",
                         padding=5,
                         relief=tk.SOLID,
                         borderwidth=1)
        label.pack()
        # Auto-destroy after 1.5 seconds
        tooltip.after(1500, tooltip.destroy)

    def show_info_popup(self, title, message):
        """Show a styled information popup"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=self.theme["bg"])
        popup.geometry("400x200")
        popup.resizable(False, False)
        # Center the popup
        popup.transient(self.root)
        popup.grab_set()
        # Title
        title_label = ttk.Label(popup, text=title,
                               font=("Arial", 14, "bold"),
                               background=self.theme["bg"],
                               foreground=self.theme["accent"])
        title_label.pack(pady=20)
        # Message
        message_label = ttk.Label(popup, text=message,
                                 wraplength=350,
                                 justify=tk.CENTER,
                                 background=self.theme["bg"],
                                 foreground=self.theme["fg"])
        message_label.pack(pady=10)
        # OK button
        ok_button = ttk.Button(popup, text="OK",
                              command=popup.destroy,
                              style="Accent.TButton")
        ok_button.pack(pady=20)
        # Auto-close after 3 seconds
        popup.after(3000, popup.destroy)

    def show_mouse_position(self, event):
        """Show mouse position on canvas"""
        self.canvas.delete("mouse_pos")
        self.canvas.create_text(10, 10,
                               text=f"({event.x}, {event.y})",
                               anchor=tk.NW,
                               fill=self.theme["info"],
                               font=("Arial", 9),
                               tags="mouse_pos")

    def start_visualization(self):
        if len(self.points) < 2:
            self.show_info_popup("Not Enough Points",
                                "Please add at least 2 points to start visualization!")
            return
        if self.is_visualizing:
            return
        # Reset visualization state
        self.is_visualizing = True
        self.is_paused = False
        self.visualization_steps = []
        self.current_step = 0
        self.highlighted_points = []
        self.active_comparisons = []
        # Update UI
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL, text="⏸️ Pause")
        # Clear previous visualization elements
        self.canvas.delete("line")
        self.canvas.delete("closest")
        self.canvas.delete("strip")
        self.canvas.delete("divider")
        self.canvas.delete("temp")
        self.canvas.delete("step_info")
        # Sort points by x-coordinate
        points_sorted = sorted(self.points, key=lambda p: p.x)
        # Generate visualization steps
        self.status_var.set("🔄 Generating visualization steps...")
        self.root.update()
        self.generate_visualization_steps(points_sorted)
        # Start visualization
        self.status_var.set("🎬 Visualization started! Follow each step below.")
        self.progress_var.set(0)
        self.root.after(100, self.run_visualization)

    def generate_visualization_steps(self, points):
        """Generate enhanced visualization steps"""
        def dc_with_steps(points_x, depth=0, side=""):
            if len(points_x) <= 3:
                # Base case: brute force
                step = {
                    "type": "base_case",
                    "points": points_x[:],
                    "depth": depth,
                    "side": side,
                    "message": f"🔍 BASE CASE ({side}) - {len(points_x)} points\nUsing brute force to find closest pair"
                }
                self.visualization_steps.append(step)
                min_dist = float('inf')
                closest = (None, None)
                comparisons = []
                for i in range(len(points_x)):
                    for j in range(i+1, len(points_x)):
                        dist = points_x[i].distance_to(points_x[j])
                        comparisons.append((points_x[i], points_x[j], dist))
                        step_compare = {
                            "type": "compare",
                            "points": [points_x[i], points_x[j]],
                            "distance": dist,
                            "depth": depth,
                            "side": side,
                            "message": f"⚡ COMPARING\n{points_x[i]} ↔ {points_x[j]}\nDistance = {dist:.2f}"
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
                    "comparisons": comparisons,
                    "message": f"✅ BASE RESULT ({side})\nClosest pair: {closest[0]} ↔ {closest[1]}\nDistance = {min_dist:.2f}"
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
                "message": f"📐 DIVIDE (Depth {depth})\nDividing at x = {mid_x:.1f}\nLeft: {len(points_x[:mid])} points, Right: {len(points_x[mid:])} points"
            }
            self.visualization_steps.append(step_divide)

            # Recursive calls
            left_min, left_closest = dc_with_steps(points_x[:mid], depth + 1, "LEFT")
            right_min, right_closest = dc_with_steps(points_x[mid:], depth + 1, "RIGHT")

            # Combine results
            min_dist = min(left_min, right_min)
            closest = left_closest if left_min < right_min else right_closest
            step_combine = {
                "type": "combine",
                "min_dist": min_dist,
                "closest": closest,
                "left_min": left_min,
                "right_min": right_min,
                "depth": depth,
                "side": side,
                "message": f"🔄 COMBINE (Depth {depth})\nLeft min: {left_min:.2f}, Right min: {right_min:.2f}\nCurrent min: {min_dist:.2f}"
            }
            self.visualization_steps.append(step_combine)

            # Check points in the strip
            strip_points = [p for p in points_x if abs(p.x - mid_x) < min_dist]
            strip_points_sorted = sorted(strip_points, key=lambda p: p.y)
            step_strip = {
                "type": "strip",
                "mid_x": mid_x,
                "strip_width": 2 * min_dist,
                "strip_points": strip_points_sorted,
                "depth": depth,
                "side": side,
                "message": f"📏 CHECKING STRIP\nWidth: {2*min_dist:.2f} around x = {mid_x:.1f}\nPoints in strip: {len(strip_points_sorted)}"
            }
            self.visualization_steps.append(step_strip)

            # Check points in strip (only need to check 7 points ahead)
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
                        "message": f"⚡ STRIP COMPARISON\n{strip_points_sorted[i]} ↔ {strip_points_sorted[j]}\nDistance = {dist:.2f}"
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
                "message": f"🎯 DEPTH {depth} RESULT\nClosest pair: {closest[0]} ↔ {closest[1]}\nDistance = {min_dist:.2f}"
            }
            self.visualization_steps.append(step_final)

            return min_dist, closest

        # Add initial step
        initial_step = {
            "type": "start",
            "points": points[:],
            "message": f"🚀 STARTING ALGORITHM\n{len(points)} points sorted by x-coordinate\nDivide & Conquer begins!"
        }
        self.visualization_steps.append(initial_step)

        # Run the algorithm
        start_time = time.time()
        self.min_distance, self.closest_pair = dc_with_steps(points)
        elapsed_time = (time.time() - start_time) * 1000

        # Add final summary step
        summary_step = {
            "type": "summary",
            "min_distance": self.min_distance,
            "closest_pair": self.closest_pair,
            "time_ms": elapsed_time,
            "total_steps": len(self.visualization_steps),
            "message": f"🏁 ALGORITHM COMPLETE!\nClosest Pair Found:\n{self.closest_pair[0]} ↔ {self.closest_pair[1]}\nDistance: {self.min_distance:.2f}\nTime: {elapsed_time:.1f}ms\nTotal Steps: {len(self.visualization_steps)}"
        }
        self.visualization_steps.append(summary_step)

    def run_visualization(self):
        if not self.is_visualizing or self.is_paused:
            return
        if self.current_step < len(self.visualization_steps):
            # Update progress
            progress = (self.current_step / len(self.visualization_steps)) * 100
            self.progress_var.set(progress)
            # Visualize current step
            self.visualize_step(self.current_step)
            self.current_step += 1
            # Schedule next step
            self.root.after(self.visualization_speed, self.run_visualization)
        else:
            # Visualization complete
            self.is_visualizing = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.status_var.set("✅ Visualization complete! Closest pair found.")
            self.show_info_popup("Visualization Complete",
                                f"Algorithm finished successfully!\nClosest distance: {self.min_distance:.2f}\nTotal steps: {self.current_step}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="▶️ Resume")
            self.status_var.set("⏸️ Visualization paused")
        else:
            self.pause_btn.config(text="⏸️ Pause")
            self.status_var.set("▶️ Visualization resumed")
            self.run_visualization()

    def step_forward(self):
        if not self.is_visualizing:
            # Start visualization if not already running
            self.start_visualization()
            # After starting, the first step is run automatically after 100ms
            # So we don't run another step here immediately
            return
        # If paused, proceed with manual step
        if self.is_paused:
            if self.current_step < len(self.visualization_steps):
                self.visualize_step(self.current_step)
                self.current_step += 1
                self.progress_var.set((self.current_step / len(self.visualization_steps)) * 100)

    def step_backward(self):
        if self.is_visualizing and self.current_step > 0:
             # Only allow backward stepping if paused
             if not self.is_paused:
                 return
             self.current_step -= 1
             # Clear and redraw from beginning up to the new current step
             self.canvas.delete("all")
             self.draw_canvas_grid()
             # Redraw all points
             for point in self.points:
                 self.draw_point(point, "#4ecdc4", 8)
             # Replay steps up to current_step (exclusive)
             for i in range(self.current_step):
                 step = self.visualization_steps[i]
                 # Redraw elements based on the type of step, similar to visualize_step
                 # but only draw *final* states for that step, not animations
                 if step["type"] == "divide":
                     # Draw divider line
                     mid_x = step["mid_x"]
                     canvas_height = self.canvas.winfo_height() or 500
                     self.canvas.create_line(mid_x, 0, mid_x, canvas_height,
                                            fill=self.theme["success"], width=3, tags="divider")
                 elif step["type"] == "strip":
                     # Draw strip area
                     mid_x = step["mid_x"]
                     strip_width = step["strip_width"]
                     canvas_height = self.canvas.winfo_height() or 500
                     fill_color = "#e5c07b"
                     outline_color = "#d4b16a"
                     self.canvas.create_rectangle(
                         mid_x - strip_width/2, 0,
                         mid_x + strip_width/2, canvas_height,
                         fill=fill_color, stipple="gray50",
                         outline=outline_color,
                         width=2, tags="strip"
                     )
                 elif step["type"] in ["compare", "compare_strip"]:
                     # Draw comparison line
                     p1, p2 = step["points"]
                     self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                            fill="#61afef", width=2,
                                            arrow=tk.BOTH, tags="temp")
                 elif step["type"] in ["result", "final", "summary"]:
                     # Draw closest pair line if available
                     if step["closest_pair"][0] and step["closest_pair"][1]:
                         p1, p2 = step["closest_pair"]
                         # Draw line
                         self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                                fill="#ff6b6b", width=3,
                                                tags=("line", "closest"))
                         # Draw points (they might be redrawn later, but that's okay)
                         self.draw_point(p1, "#ff6b6b", 10, "closest")
                         self.draw_point(p2, "#ff6b6b", 10, "closest")

             # Update step info text to reflect the previous step's message
             if self.current_step > 0:
                 self.step_info.set(self.visualization_steps[self.current_step - 1]["message"])
             else:
                 self.step_info.set("Waiting for visualization...")

    def visualize_step(self, step_idx):
        step = self.visualization_steps[step_idx]
        # Clear temporary drawings
        self.canvas.delete("temp")
        self.canvas.delete("step_info")
        self.canvas.delete("highlight")
        # Update step info
        self.step_info.set(step["message"])
        # Draw based on step type
        if step["type"] == "start":
            self.status_var.set("🎬 Starting algorithm...")
        elif step["type"] == "divide":
            # Draw dividing line with animation
            mid_x = step["mid_x"]
            canvas_height = self.canvas.winfo_height() or 500
            for i in range(0, canvas_height, 20):
                self.canvas.create_line(mid_x, i, mid_x, min(i+10, canvas_height),
                                       fill=self.theme["success"], width=3, tags="divider")
                self.canvas.update()
                time.sleep(0.005)
            # Highlight left and right halves
            for point in step["left_points"]:
                self.draw_point(point, "#45b7d1", 10, "highlight")
            for point in step["right_points"]:
                self.draw_point(point, "#c678dd", 10, "highlight")
            self.status_var.set(f"📐 Dividing at x = {mid_x:.1f}")
        elif step["type"] == "strip":
            # Draw strip area with gradient
            mid_x = step["mid_x"]
            strip_width = step["strip_width"]
            canvas_height = self.canvas.winfo_height() or 500
            # Animate strip appearance
            for alpha in range(0, 60, 5):
                color = f"#{alpha:02x}{alpha:02x}00"
                self.canvas.create_rectangle(
                    mid_x - strip_width/2, 0,
                    mid_x + strip_width/2, canvas_height,
                    fill=color, stipple="gray50",
                    outline="", tags=("strip", "temp")
                )
                self.canvas.update()
                time.sleep(0.01)
            self.canvas.delete("temp")
            # Final strip
            fill_color = "#e5c07b"
            outline_color = "#d4b16a"
            self.canvas.create_rectangle(
                mid_x - strip_width/2, 0,
                mid_x + strip_width/2, canvas_height,
                fill=fill_color, stipple="gray50",
                outline=outline_color,
                width=2, tags="strip"
            )
            # Highlight points in strip
            for point in step["strip_points"]:
                self.draw_point(point, "#e5c07b", 12, "highlight")
            self.status_var.set(f"📏 Checking strip with {len(step['strip_points'])} points")
        elif step["type"] in ["compare", "compare_strip"]:
            # Animate comparison with pulsing line
            p1, p2 = step["points"]
            for width in [1, 3, 5, 3, 1]:
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                       fill="#61afef", width=width,
                                       arrow=tk.BOTH, tags="temp")
                self.canvas.update()
                time.sleep(0.05)
                self.canvas.delete("temp")
            # Draw final line
            line = self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                          fill="#61afef", width=2,
                                          arrow=tk.BOTH, tags="temp")
            # Animate points
            for point in [p1, p2]:
                for size in [8, 12, 15, 12, 8]:
                    self.draw_point(point, "#61afef", size, "highlight")
                    self.canvas.update()
                    time.sleep(0.03)
            # Show distance label
            mid_x = (p1.x + p2.x) / 2
            mid_y = (p1.y + p2.y) / 2
            self.canvas.create_text(mid_x, mid_y,
                                   text=f"d = {step['distance']:.2f}",
                                   fill="#61afef", font=("Arial", 10, "bold"),
                                   tags="temp")
            self.status_var.set(f"⚡ Comparing points: distance = {step['distance']:.2f}")
        elif step["type"] in ["result", "final"]:
            # Highlight the closest pair found in this step
            if step["closest_pair"][0]:
                p1, p2 = step["closest_pair"]
                # Flash the points
                for _ in range(3):
                    self.draw_point(p1, "#ff6b6b", 15, "highlight")
                    self.draw_point(p2, "#ff6b6b", 15, "highlight")
                    self.canvas.update()
                    time.sleep(0.1)
                    self.draw_point(p1, "#4ecdc4", 8, "highlight")
                    self.draw_point(p2, "#4ecdc4", 8, "highlight")
                    self.canvas.update()
                    time.sleep(0.1)
                # Draw connection line
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                       fill="#ff6b6b", width=3,
                                       tags=("line", "highlight"))
                # Show distance
                self.canvas.create_text((p1.x + p2.x)/2, (p1.y + p2.y)/2 - 20,
                                       text=f"d = {step['min_distance']:.2f}",
                                       fill="#ff6b6b", font=("Arial", 11, "bold"),
                                       tags="highlight")
            self.status_var.set(f"✅ Found closest pair: distance = {step['min_distance']:.2f}")
        elif step["type"] == "summary":
            # Final result display
            if step["closest_pair"][0]:
                p1, p2 = step["closest_pair"]
                # Clear previous highlights
                self.canvas.delete("highlight")
                self.canvas.delete("line")
                self.canvas.delete("closest")
                # Draw all points normally
                for point in self.points:
                    if point != p1 and point != p2:
                        self.draw_point(point, "#4ecdc4", 8)
                # Draw final closest pair with special effect
                for size in [10, 15, 20, 15, 10]:
                    self.draw_point(p1, "#ff6b6b", size, "closest")
                    self.draw_point(p2, "#ff6b6b", size, "closest")
                    self.canvas.update()
                    time.sleep(0.05)
                # Draw final line with animation
                for width in [1, 2, 3, 4, 3, 2]:
                    self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                           fill="#ff6b6b", width=width,
                                           tags=("line", "closest"))
                    self.canvas.update()
                    time.sleep(0.03)
                # Final thicker line
                self.canvas.create_line(p1.x, p1.y, p2.x, p2.y,
                                       fill="#ff6b6b", width=4,
                                       tags=("line", "closest"))
                # Show final distance
                self.canvas.create_text((p1.x + p2.x)/2, (p1.y + p2.y)/2,
                                       text=f"✨ d = {step['min_distance']:.2f} ✨",
                                       fill="#ff6b6b", font=("Arial", 12, "bold"),
                                       tags="closest")
                # Update global values
                self.min_distance = step['min_distance']
                self.closest_pair = step['closest_pair']
                self.update_stats()
                # Update performance info
                self.perf_text.set(f"Comparisons: {len(self.visualization_steps)} | "
                                  f"Time: {step['time_ms']:.1f}ms")

    def find_closest_no_visual(self):
        if len(self.points) < 2:
            self.show_info_popup("Not Enough Points", "Please add at least 2 points!")
            return
        # Clear previous visualization elements
        self.canvas.delete("line")
        self.canvas.delete("closest")
        self.canvas.delete("strip")
        self.canvas.delete("divider")
        self.canvas.delete("temp")
        # Sort points
        points_sorted = sorted(self.points, key=lambda p: p.x)
        # Run algorithm
        start_time = time.time()
        self.min_distance, self.closest_pair = self.closest_pair_dc(points_sorted)
        elapsed_time = (time.time() - start_time) * 1000
        # Draw result
        if self.closest_pair[0] and self.closest_pair[1]:
            # Draw all points
            for point in self.points:
                if point != self.closest_pair[0] and point != self.closest_pair[1]:
                    self.draw_point(point, "#4ecdc4", 8)
            # Highlight closest pair
            self.draw_point(self.closest_pair[0], "#ff6b6b", 15, "closest")
            self.draw_point(self.closest_pair[1], "#ff6b6b", 15, "closest")
            # Draw connection
            self.canvas.create_line(self.closest_pair[0].x, self.closest_pair[0].y,
                                   self.closest_pair[1].x, self.closest_pair[1].y,
                                   fill="#ff6b6b", width=4, tags=("line", "closest"))
            # Show distance
            self.canvas.create_text((self.closest_pair[0].x + self.closest_pair[1].x)/2,
                                   (self.closest_pair[0].y + self.closest_pair[1].y)/2,
                                   text=f"d = {self.min_distance:.2f}",
                                   fill="#ff6b6b", font=("Arial", 12, "bold"),
                                   tags="closest")
        self.update_stats()
        self.status_var.set(f"⚡ Instant solve complete! Distance: {self.min_distance:.2f}")
        self.perf_text.set(f"Time: {elapsed_time:.1f}ms")
        self.show_info_popup("Solution Found",
                            f"Closest pair found instantly!\n"
                            f"Distance: {self.min_distance:.2f}\n"
                            f"Time: {elapsed_time:.1f}ms")

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

        # points_sorted_by_y = sorted(points_x, key=lambda p: p.y) # Not used here, kept for reference from original
        return dc_recursive(points_x)

def main():
    root = tk.Tk()
    # Set window icon and title
    root.title("Closest Pair Visualizer")
    # Make window responsive
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    app = EnhancedClosestPairVisualizer(root)
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.mainloop()

if __name__ == "__main__":
    main()
