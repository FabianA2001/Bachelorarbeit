import sys
import tkinter as tk

import fitz  # PyMuPDF
from PIL import Image, ImageTk

OFFSET_X = 0.7
OFFSET_Y = 1


def get_pdf_page_image(pdf_path, page_number):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return img, pix.width, pix.height, page.rect


class PDFBoxSelector:
    def __init__(self, img, width, height, page_rect, scale=2.0):
        self.root = tk.Tk()
        self.root.title("PDF Box Selector")
        self.scale = scale
        self.orig_width = width
        self.orig_height = height
        self.width = int(width * scale)
        self.height = int(height * scale)
        self.page_rect = page_rect
        # Kompatibel mit neuen und alten Pillow-Versionen
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = getattr(Image, "LANCZOS", getattr(Image, "NEAREST", 0))
        self.img = img.resize((self.width, self.height), resample)
        self.tk_img = ImageTk.PhotoImage(self.img)
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def on_drag(self, event):
        self.end_x = event.x
        self.end_y = event.y
        if any(
            v is None
            for v in (self.rect, self.start_x, self.start_y, self.end_x, self.end_y)
        ):
            return
        self.canvas.coords(
            self.rect, self.start_x, self.start_y, self.end_x, self.end_y
        )

    def on_release(self, event):
        self.end_x = event.x
        self.end_y = event.y
        # Umrechnung in PDF-Koordinaten (unten links ist (0,0)), Skalierung beachten
        if any(v is None for v in (self.start_x, self.start_y, self.end_x, self.end_y)):
            return
        x0, y0 = self.start_x, self.start_y
        x1, y1 = self.end_x, self.end_y
        # Canvas (0,0) ist oben links, PDF (0,0) ist unten links
        # Rückskalieren auf Originalgröße
        x0_unscaled = x0 / self.scale
        y0_unscaled = y0 / self.scale
        x1_unscaled = x1 / self.scale
        y1_unscaled = y1 / self.scale
        pdf_x0 = x0_unscaled * self.page_rect.width / self.orig_width
        pdf_y0 = (
            (self.orig_height - y0_unscaled) * self.page_rect.height / self.orig_height
        )
        pdf_x1 = x1_unscaled * self.page_rect.width / self.orig_width
        pdf_y1 = (
            (self.orig_height - y1_unscaled) * self.page_rect.height / self.orig_height
        )
        pt_to_cm = 2.54 / 72
        print(
            f"Ecke 1: ({pdf_x0:.2f}, {pdf_y0:.2f}) Punkte | ({pdf_x0 * pt_to_cm:.2f}, {pdf_y0 * pt_to_cm:.2f}) cm"
        )
        print(
            f"Ecke 2: ({pdf_x1:.2f}, {pdf_y1:.2f}) Punkte | ({pdf_x1 * pt_to_cm:.2f}, {pdf_y1 * pt_to_cm:.2f}) cm"
        )
        print(
            f"({pdf_x0 * pt_to_cm - OFFSET_X:.2f}, {pdf_y0 * pt_to_cm - OFFSET_Y:.2f}) rectangle ({pdf_x1 * pt_to_cm - OFFSET_X:.2f}, {pdf_y1 * pt_to_cm - OFFSET_Y:.2f})"
        )

    def run(self):
        self.root.mainloop()


def main():
    if len(sys.argv) < 3:
        print("Usage: python test.py <pdf_path> <page_number> [scale]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    page_number = int(sys.argv[2])
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    img, width, height, page_rect = get_pdf_page_image(pdf_path, page_number)
    selector = PDFBoxSelector(img, width, height, page_rect, scale=scale)
    selector.run()


if __name__ == "__main__":
    main()
