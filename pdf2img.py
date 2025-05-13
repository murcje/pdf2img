# Python script with a GUI to convert a multi-page PDF into a single long vertical image.
#
# Required libraries:
# 1. PyMuPDF (fitz): For reading PDF files and rendering pages as images.
#    Installation: pip install PyMuPDF
# 2. Pillow (PIL): For image manipulation (creating a new image, pasting pages).
#    Installation: pip install Pillow
# 3. Tkinter: For the GUI (usually comes with Python standard library).
#
# How to use:
# 1. Make sure you have Python installed.
# 2. Install the required libraries (PyMuPDF, Pillow) if you haven't already:
#    pip install PyMuPDF Pillow
# 3. Save this script as a Python file (e.g., pdf_to_image_gui.py).
# 4. Run the script from your terminal: python pdf_to_image_gui.py
# 5. A window will appear. Use the buttons to select your PDF, choose an output
#    location, set DPI, optionally check "Only include pages with images",
#    and then click "Convert".

import fitz  # PyMuPDF
from PIL import Image # ImageTk is not strictly needed for this version
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk # ttk for themed widgets

class PDFConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF to Vertical Image Converter")
        master.geometry("550x450") # Increased height for new option

        # Style configuration
        style = ttk.Style()
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TCheckbutton", padding=5, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))

        # --- UI Elements ---

        # Header
        self.header_label = ttk.Label(master, text="PDF to Single Vertical Image", style="Header.TLabel")
        self.header_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="ew")

        # Input PDF
        self.pdf_label = ttk.Label(master, text="Input PDF:")
        self.pdf_label.grid(row=1, column=0, sticky="w", padx=10, pady=(5,0)) # Added pady
        self.pdf_path_var = tk.StringVar()
        self.pdf_entry = ttk.Entry(master, textvariable=self.pdf_path_var, width=50, state="readonly")
        self.pdf_entry.grid(row=1, column=1, padx=5, pady=(5,0), sticky="ew")
        self.pdf_browse_button = ttk.Button(master, text="Browse...", command=self.browse_pdf)
        self.pdf_browse_button.grid(row=1, column=2, padx=10, pady=(5,0), sticky="ew")

        # Output Image
        self.output_label = ttk.Label(master, text="Output Image:")
        self.output_label.grid(row=2, column=0, sticky="w", padx=10, pady=(5,0))
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(master, textvariable=self.output_path_var, width=50, state="readonly")
        self.output_entry.grid(row=2, column=1, padx=5, pady=(5,0), sticky="ew")
        self.output_browse_button = ttk.Button(master, text="Save As...", command=self.browse_output)
        self.output_browse_button.grid(row=2, column=2, padx=10, pady=(5,0), sticky="ew")

        # DPI
        self.dpi_label = ttk.Label(master, text="DPI (e.g., 150):")
        self.dpi_label.grid(row=3, column=0, sticky="w", padx=10, pady=(5,0))
        self.dpi_var = tk.StringVar(value="150") # Default DPI
        self.dpi_entry = ttk.Entry(master, textvariable=self.dpi_var, width=10)
        self.dpi_entry.grid(row=3, column=1, sticky="w", padx=5, pady=(5,0))

        # **** NEW: Checkbox for filtering pages with images ****
        self.only_images_var = tk.BooleanVar(value=False) # Default to False
        self.only_images_check = ttk.Checkbutton(
            master,
            text="Only include pages with images",
            variable=self.only_images_var
        )
        self.only_images_check.grid(row=4, column=0, columnspan=3, sticky="w", padx=10, pady=(10,0))


        # Convert Button
        self.convert_button = ttk.Button(master, text="Convert to Image", command=self.start_conversion)
        # Adjusted row for convert button due to new checkbox
        self.convert_button.grid(row=5, column=0, columnspan=3, pady=20, sticky="ew", padx=100)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(master, variable=self.progress_var, maximum=100)
        # Adjusted row for progress bar
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,5))

        # Status Label
        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        # Adjusted row for status label
        self.status_label.grid(row=7, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Configure grid column weights to make entry fields expand
        master.grid_columnconfigure(1, weight=1)


    def browse_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if file_path:
            self.pdf_path_var.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            suggested_output = os.path.join(os.path.dirname(file_path), base_name + "_combined.png")
            self.output_path_var.set(suggested_output)
            self.update_status(f"Selected PDF: {os.path.basename(file_path)}")

    def browse_output(self):
        initial_file = ""
        if self.pdf_path_var.get():
            base_name = os.path.splitext(os.path.basename(self.pdf_path_var.get()))[0]
            initial_file = base_name + "_combined.png"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Combined Image As",
            defaultextension=".png",
            initialfile=initial_file,
            filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*"))
        )
        if file_path:
            self.output_path_var.set(file_path)
            self.update_status(f"Output will be saved to: {os.path.basename(file_path)}")

    def update_status(self, message):
        self.status_var.set(f"Status: {message}")
        self.master.update_idletasks()

    def start_conversion(self):
        pdf_path = self.pdf_path_var.get()
        output_path = self.output_path_var.get()
        dpi_str = self.dpi_var.get()
        only_with_images = self.only_images_var.get() # Get state of the new checkbox

        if not pdf_path:
            messagebox.showerror("Error", "Please select an input PDF file.")
            return
        if not output_path:
            messagebox.showerror("Error", "Please specify an output image file path.")
            return

        try:
            dpi = int(dpi_str)
            if dpi <= 0:
                raise ValueError("DPI must be positive.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid DPI value: {e}. Please enter a positive number.")
            return

        self.update_status("Processing... Please wait.")
        self.convert_button.config(state=tk.DISABLED)
        self.progress_var.set(0)

        try:
            # Pass the new option to the processing function
            self.pdf_to_vertical_image_with_gui_updates(pdf_path, output_path, dpi, only_with_images)
            messagebox.showinfo("Success", f"Image successfully created at:\n{output_path}")
            self.update_status("Conversion complete!")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"An error occurred: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.convert_button.config(state=tk.NORMAL)
            self.progress_var.set(0)

    def pdf_to_vertical_image_with_gui_updates(self, pdf_path, output_image_path, dpi=150, only_pages_with_images=False):
        """
        Converts a PDF file into a single long vertical image, with GUI updates and image filter.
        """
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise Exception(f"Error opening PDF file '{pdf_path}': {e}")

        if doc.page_count == 0:
            doc.close()
            raise Exception(f"The PDF file '{pdf_path}' has no pages.")

        self.update_status(f"Scanning '{os.path.basename(pdf_path)}' ({doc.page_count} pages)...")
        
        pages_to_process = []
        if only_pages_with_images:
            self.update_status("Filtering pages: Checking for images...")
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                if page.get_images(full=True): # Check if page has images
                    pages_to_process.append(page_num)
                # Update progress during scanning (optional, can be slow for many pages)
                # self.progress_var.set(((page_num + 1) / doc.page_count) * 20) # Dedicate 20% of progress to scanning
                # self.master.update_idletasks()
            if not pages_to_process:
                doc.close()
                raise Exception("No pages containing images were found in the PDF.")
            self.update_status(f"Found {len(pages_to_process)} pages with images.")
        else:
            pages_to_process = list(range(doc.page_count))

        num_pages_to_render = len(pages_to_process)
        if num_pages_to_render == 0: # Should be caught by the check above if only_images is true
             doc.close()
             raise Exception("No pages selected for processing.")


        self.update_status(f"Processing {num_pages_to_render} pages...")

        page_images = []
        total_height = 0
        max_width = 0
        rendered_page_count = 0

        for page_num in pages_to_process: # Iterate through the filtered list of page numbers
            try:
                page = doc.load_page(page_num) # Load the specific page
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                page_images.append(img)

                total_height += img.height
                if img.width > max_width:
                    max_width = img.width
                
                rendered_page_count += 1
                progress_percentage = (rendered_page_count / num_pages_to_render) * 100 * 0.9 # Use 90% for rendering
                if only_pages_with_images:
                    progress_percentage = progress_percentage # Keep as is, scanning was separate
                
                self.progress_var.set(progress_percentage)
                self.update_status(f"Rendered page {rendered_page_count}/{num_pages_to_render} (Original page {page_num + 1})")

            except Exception as e:
                print(f"Error processing page {page_num + 1}: {e}")
                # Optionally inform user via status or skip
                self.update_status(f"Error on page {page_num + 1}, skipping.")
                continue

        doc.close()

        if not page_images:
            raise Exception("No pages were successfully rendered.") # Should ideally not happen if pages_to_process was not empty

        self.update_status(f"Creating output image ({max_width}x{total_height})...")
        self.progress_var.set(95) # Indicate final image creation step

        final_image = Image.new("RGB", (max_width, total_height), (255, 255, 255)) # White background

        current_y = 0
        for img in page_images:
            x_offset = (max_width - img.width) // 2
            final_image.paste(img, (x_offset, current_y))
            current_y += img.height
        
        self.update_status("Saving image...")
        try:
            final_image.save(output_image_path)
            self.progress_var.set(100)
        except Exception as e:
            raise Exception(f"Error saving the final image: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()
