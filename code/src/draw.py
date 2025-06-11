import tkinter as tk

GRID_SIZE = 40  # Abstand zwischen den Rasterpunkten
POINT_RADIUS = 6


class PointEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Punkte-Editor (ganzzahliges Raster)")
        self.canvas = tk.Canvas(master, width=800, height=600, bg="white")
        self.canvas.pack()
        self.points = []
        self.point_items = {}  # (x, y) -> Canvas-Objekt-ID
        self.selected_point = None
        self.canvas.bind("<Button-1>", self.select_or_add_point)
        self.draw_grid()
        self.button_print = tk.Button(
            master, text="Positionen ausgeben", command=self.print_points
        )
        self.button_print.pack()
        self.button_delete = tk.Button(
            master,
            text="Ausgewählten Punkt löschen",
            command=self.delete_selected_point,
        )
        self.button_delete.pack()

    def draw_grid(self):
        for x in range(0, 800, GRID_SIZE):
            self.canvas.create_line(x, 0, x, 600, fill="#eee")
        for y in range(0, 600, GRID_SIZE):
            self.canvas.create_line(0, y, 800, y, fill="#eee")

    def select_or_add_point(self, event):
        x = round(event.x / GRID_SIZE)
        y = round(event.y / GRID_SIZE)
        if (x, y) in self.points:
            self.select_point((x, y))
        else:
            self.add_point((x, y))

    def add_point(self, point):
        x, y = point
        if (x, y) not in self.points:
            self.points.append((x, y))
            cx, cy = x * GRID_SIZE, y * GRID_SIZE
            item = self.canvas.create_oval(
                cx - POINT_RADIUS,
                cy - POINT_RADIUS,
                cx + POINT_RADIUS,
                cy + POINT_RADIUS,
                fill="red",
            )
            self.point_items[(x, y)] = item

    def select_point(self, point):
        # Deselect previous
        if self.selected_point and self.selected_point in self.point_items:
            item = self.point_items[self.selected_point]
            self.canvas.itemconfig(item, outline="", width=1)
        # Select new
        self.selected_point = point
        item = self.point_items[point]
        self.canvas.itemconfig(item, outline="blue", width=3)

    def delete_selected_point(self):
        if self.selected_point and self.selected_point in self.points:
            self.points.remove(self.selected_point)
            item = self.point_items.pop(self.selected_point, None)
            if item is not None:
                self.canvas.delete(item)
            self.selected_point = None

    def print_points(self):
        print("Gesetzte Punkte (Rasterkoordinaten):")
        print(f" nodes=[{', '.join(f'Node(({x}, {y}))' for (x, y) in self.points)}]")


if __name__ == "__main__":
    root = tk.Tk()
    editor = PointEditor(root)
    root.lift()
    root.attributes("-topmost", True)
    root.after(100, lambda: root.attributes("-topmost", False))
    root.mainloop()
