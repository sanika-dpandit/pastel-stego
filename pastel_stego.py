import sys  # System-specific parameters and functions
import os   # OS interaction, e.g., file paths
from PyQt5.QtWidgets import (  # Importing PyQt5 GUI widgets
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QTextEdit,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont  # For image display and font settings
from PyQt5.QtCore import Qt  # For alignment and other Qt core features
from PIL import Image  # PIL (Pillow) library to handle image loading/saving
import stepic  # Stepic library to encode/decode messages in images (LSB steganography)
from random import randint  # To generate random numbers (for noise image)
import colorsys  # For color conversions (HSV to RGB) in gradient images


class StegooQt(QWidget):
    def __init__(self):
        super().__init__()  # Initialize the parent QWidget

        # Set window title shown in the OS window bar
        self.setWindowTitle("Steganography Tool (Stepic Only) - PyQt5")

        # Set window size and initial position (x=100,y=100,width=700,height=650)
        self.setGeometry(100, 100, 700, 650)

        # Enable accepting drag & drop events in this widget
        self.setAcceptDrops(True)

        # Set window background to a vertical linear gradient from light blue shades
        self.setStyleSheet("""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #a1c4fd,
                stop:1 #c2e9fb
            );
        """)

        self.image_path = ""  # Store the currently loaded/generated image path
        self.logo_path = "logo.png"  # Path to app logo image file (optional)

        # QStackedWidget lets us stack multiple "pages" (screens) and switch between them
        self.stacked = QStackedWidget()

        # Main layout of the main window is vertical, holding the stacked widget
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked)

        # Initialize all the different pages/screens of the app and add to stacked widget
        self.init_initial_screen()
        self.init_use_existing_image()
        self.init_generate_options()
        self.init_blank_color_choices()
        self.init_gradient_choices()
        self.init_encode_decode()

        # Show the first page initially (index 0)
        self.stacked.setCurrentIndex(0)

    # Called when dragging something over the window - we check if it contains valid image file urls
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # Loop over all URLs in dragged data
            for url in event.mimeData().urls():
                # If any file ends with .png or .bmp (case-insensitive), accept the drag event
                if url.toLocalFile().lower().endswith(('.png', '.bmp')):
                    event.acceptProposedAction()
                    return
        # Otherwise ignore the drag event
        event.ignore()

    # Called when the dragged files are dropped onto the window
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            # Loop all dropped files
            for url in event.mimeData().urls():
                path = url.toLocalFile()  # Get full local file path from URL
                # Only accept PNG or BMP image files
                if path.lower().endswith(('.png', '.bmp')):
                    self.image_path = path  # Save selected image path
                    # Show preview scaled to 200x200 in the UI
                    self.image_preview.setPixmap(QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio))
                    self.continue_btn.setEnabled(True)  # Enable "Continue" button to proceed
                    # Update label to show loaded image filename
                    self.drop_label.setText(f"Loaded: {os.path.basename(path)}")
                    break  # Only load first valid image
            event.acceptProposedAction()
        else:
            event.ignore()

    # Helper to create a QLabel for the logo image, or text if logo file not found
    def get_logo(self):
        label = QLabel()
        if os.path.exists(self.logo_path):  # Check if logo image file exists
            # Load logo image, scale it nicely, and set it in label
            pixmap = QPixmap(self.logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Load logo image and scale to 100x100 pixels preserving ratio, with smooth scaling
            label.setPixmap(pixmap)#Set pixmap to the label
            label.setAlignment(Qt.AlignCenter)#Center align the label contents
        else:
            label.setText("[Logo not found]")  # Fallback text if logo missing
            label.setAlignment(Qt.AlignCenter)
        return label#Return QLabel widget (with image or text)

    # Helper method to apply consistent styles to QPushButton widgets
    # Apply a CSS stylesheet to a QPushButton to make buttons consistent in color, font, and shape
    def style_button(self, button):
        button.setStyleSheet("""
            QPushButton {
                background-color: #BEE3F8;
                color: #003366;
                font-weight: bold;
                font-family: 'Segoe UI';
                padding: 8px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #A3CFF0;
            }
        """)

    # Initialize first (home) screen page: Logo, title, and image option buttons
    def init_initial_screen(self):
        page = QWidget()# # Create a QWidget page to hold widgets
        layout = QVBoxLayout()## Vertical layout for arranging widgets

        layout.addWidget(self.get_logo())  # Add logo to top

        title = QLabel("Steganography Tool")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))  # Large bold font
        title.setAlignment(Qt.AlignCenter)## Center horizontally
        layout.addWidget(title)# # Add title label

        label = QLabel("Choose Image Option")# Instruction label
        label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Button to use an existing image (browse or drag-drop)
        btn1 = QPushButton("Use Existing Image (Browse or Drag & Drop)")
        btn1.clicked.connect(lambda: self.stacked.setCurrentIndex(1))  # Switch to page 1
        self.style_button(btn1)
        layout.addWidget(btn1)

        # Button to generate a new image (blank, noise, gradient)
        btn2 = QPushButton("Generate New Image")
        btn2.clicked.connect(lambda: self.stacked.setCurrentIndex(2))  # Switch to page 2
        self.style_button(btn2)
        layout.addWidget(btn2)

        page.setLayout(layout)
        self.stacked.addWidget(page)  # Add this page to stacked widget

    # Page for using existing image: drag & drop or browse button, preview, and continue button
    def init_use_existing_image(self):
        page = QWidget()
        layout = QVBoxLayout()

        instr = QLabel("Drag and drop PNG/BMP image below or click Browse")
        instr.setFont(QFont("Segoe UI", 12))
        instr.setAlignment(Qt.AlignCenter)
        layout.addWidget(instr)

        self.drop_label = QLabel("Drop Image Here")
        self.drop_label.setFixedHeight(100)  # Fixed height for drop area label
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed #003366; background-color: #BEE3F8;")  # Visual styling
        ## Dashed border to indicate drop zone
        layout.addWidget(self.drop_label)

        browse_btn = QPushButton("Browse Image")
        browse_btn.clicked.connect(self.browse_image)  # Open file dialog
        self.style_button(browse_btn)
        layout.addWidget(browse_btn)

        self.continue_btn = QPushButton("Continue")
        self.continue_btn.setEnabled(False)  # Disabled until image selected
        self.continue_btn.clicked.connect(lambda: self.switch_to_encode_decode())  # Proceed to encode/decode page
        self.style_button(self.continue_btn)
        layout.addWidget(self.continue_btn)

        self.image_preview = QLabel()  # Label to preview loaded image
        self.image_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_preview)

        page.setLayout(layout)
        self.stacked.addWidget(page)

    # Page for choosing image generation options (blank, noise, gradient)
    def init_generate_options(self):
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Select Image Type to Generate")
        label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn_blank = QPushButton("Blank Image")
        self.style_button(btn_blank)
        btn_blank.clicked.connect(lambda: self.stacked.setCurrentIndex(3))  # Go to blank color choices page
        layout.addWidget(btn_blank)

        btn_noise = QPushButton("Noise Image")
        self.style_button(btn_noise)
        btn_noise.clicked.connect(self.generate_noise_image)  # Generate noise image immediately
        layout.addWidget(btn_noise)

        btn_gradient = QPushButton("Gradient Image")
        self.style_button(btn_gradient)
        btn_gradient.clicked.connect(lambda: self.stacked.setCurrentIndex(4))  # Go to gradient choices page
        layout.addWidget(btn_gradient)

        back_btn = QPushButton("Back")
        self.style_button(back_btn)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))  # Back to home page
        layout.addWidget(back_btn)

        page.setLayout(layout)
        self.stacked.addWidget(page)

    # Page to choose blank image color for generation
    def init_blank_color_choices(self):
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Select Color for Blank Image")
        label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Dictionary of color names and their RGB tuples
        colors = {
            "Light Blue": (173, 216, 230),
            "Sky Blue": (135, 206, 235),
            "Powder Blue": (176, 224, 230),
            "Alice Blue": (240, 248, 255),
            "Deep Sky Blue": (0, 191, 255)
        }

        # Create button for each color option
        for name, color in colors.items():
            btn = QPushButton(name)
            self.style_button(btn)
            # Use lambda to pass color as argument when button clicked
            btn.clicked.connect(lambda checked, c=color: self.generate_blank_image(c))
            layout.addWidget(btn)

        back_btn = QPushButton("Back")
        self.style_button(back_btn)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(2))  # Back to generate options page
        layout.addWidget(back_btn)

        page.setLayout(layout)
        self.stacked.addWidget(page)

    # Page to choose gradient type for generation
    def init_gradient_choices(self):
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Select Gradient Type")
        label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Gradient presets with start and end RGB colors or None for special gradient
        gradients = {
            "Sky Blue → Deep Sky Blue": ((135, 206, 250), (0, 191, 255)),
            "Powder → Alice": ((176, 224, 230), (240, 248, 255)),
            "Ocean": None
        }

        # Create buttons for each gradient choice
        for name, gradient in gradients.items():
            btn = QPushButton(name)
            self.style_button(btn)
            if gradient:
                # Pass gradient tuple to generator function
                btn.clicked.connect(lambda checked, g=gradient: self.generate_gradient_image(g))
            else:
                # Ocean uses special function
                btn.clicked.connect(self.generate_ocean_gradient)
            layout.addWidget(btn)

        back_btn = QPushButton("Back")
        self.style_button(back_btn)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(2))  # Back to generate options
        layout.addWidget(back_btn)

        page.setLayout(layout)
        self.stacked.addWidget(page)

    # Generate blank image with a single RGB color and save it
    def generate_blank_image(self, color):
        img = Image.new("RGB", (300, 300), color)  # Create new image 300x300 pixels
        self.save_generated_image(img)## Save image with dialog and update UI

    # Generate noise image by setting random RGB values for each pixel
    def generate_noise_image(self):
        img = Image.new("RGB", (300, 300))  # Blank image
        pixels = img.load()  # Load pixel access object
        for x in range(300):
            for y in range(300):
                # Assign random RGB tuple to each pixel
                pixels[x, y] = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.save_generated_image(img)

    # Generate a linear gradient image between two RGB colors horizontally
    def generate_gradient_image(self, colors):
        start, end = colors
        img = Image.new("RGB", (300, 300))## Create blank image
        for x in range(300):
            t = x / 299  # Normalize x to 0..1 for interpolation
            # Linear interpolate each RGB channel between start and end color
            r = int(start[0] + (end[0] - start[0]) * t)#Interpolate red channel linearly
            g = int(start[1] + (end[1] - start[1]) * t)#Interpolate green channel
            b = int(start[2] + (end[2] - start[2]) * t)# Interpolate blue channel
            for y in range(300):
                img.putpixel((x, y), (r, g, b))  # Set color pixel at (x,y)
        self.save_generated_image(img)#Save image and update UI

    # Generate an "Ocean" gradient using HSV to RGB color conversion horizontally
    def generate_ocean_gradient(self):
        img = Image.new("RGB", (300, 300))
        for x in range(300):
            h = x / 300  # Hue value from 0 to 1 across width
            r, g, b = colorsys.hsv_to_rgb(0.55 + h * 0.1, 0.6, 1)  # Convert HSV to RGB tuple
            rgb = (int(r * 255), int(g * 255), int(b * 255))  # Scale RGB floats to 0-255 ints
            for y in range(300):
                img.putpixel((x, y), rgb)# # Set pixel color
        self.save_generated_image(img)# # Save image and update UI

    # Show a file dialog to save the generated image and update UI accordingly
    def save_generated_image(self, img):
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
        #Open save file dialog with PNG filter
        if path:
            img.save(path)  # Save PIL Image to selected path
            self.image_path = path  # Update current image path
            QMessageBox.information(self, "Saved", f"Image saved to: {path}")  # Inform user
            self.switch_to_encode_decode()  # Go to encode/decode screen

    # Open file dialog to browse and select an existing image
    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.bmp)")
        # Open file open dialog filtering PNG and BMP images
        if path:
            self.image_path = path
            # Update preview with selected image scaled to 200x200
            self.image_preview.setPixmap(QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio))
            ## Preview selected image scaled to 200x200
            self.continue_btn.setEnabled(True)  # Enable continue button after image selected

    # Switch UI to encode/decode page and reset inputs/results
    def switch_to_encode_decode(self):
        self.stacked.setCurrentIndex(5)  # Page index 5 is encode/decode screen
        self.message_input.clear()  # Clear previous message input
        if self.image_path:
            # Show loaded/generated image preview on encode/decode page
            self.image_display.setPixmap(QPixmap(self.image_path).scaled(200, 200, Qt.KeepAspectRatio))
            self.result_label.setText("")  # Clear previous decode results

    # Initialize the encode/decode message page
    def init_encode_decode(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Encode / Decode Message")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.image_display = QLabel()  # Show current image here
        self.image_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_display)

        self.message_input = QTextEdit()  # Text box for user to enter secret message to encode
        self.message_input.setPlaceholderText("Type your secret message here...")
        self.message_input.setFixedHeight(100)
        layout.addWidget(self.message_input)

        encode_btn = QPushButton("Encode Message")
        encode_btn.clicked.connect(self.encode_message)  # Hook up encode function
        self.style_button(encode_btn)
        layout.addWidget(encode_btn)

        decode_btn = QPushButton("Decode Message")
        decode_btn.clicked.connect(self.decode_message)  # Hook up decode function
        self.style_button(decode_btn)
        layout.addWidget(decode_btn)

        self.result_label = QLabel("")  # Label to show decoded message or errors
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #003366; font-size: 14px;")
        layout.addWidget(self.result_label)

        back_btn = QPushButton("Back to Home")
        self.style_button(back_btn)
        back_btn.clicked.connect(lambda: self.stacked.setCurrentIndex(0))  # Back to home page
        layout.addWidget(back_btn)

        page.setLayout(layout)
        self.stacked.addWidget(page)

    # Called when user clicks "Encode Message"
    def encode_message(self):
        message = self.message_input.toPlainText().strip()  # Get message text from textbox
        # Check if message and image loaded
        if not message or not self.image_path:
            QMessageBox.warning(self, "Error", "Please load an image and enter a message.")
            return
        # Ask user where to save encoded image
        path, _ = QFileDialog.getSaveFileName(self, "Save Encoded Image", "", "PNG Files (*.png)")
        if path:
            img = Image.open(self.image_path).convert("RGB")  # Load current image as RGB
            encoded = stepic.encode(img, message.encode())  # Encode message bytes into image
            encoded.save(path)  # Save encoded image to user path
            self.image_path = path  # Update image path to newly saved file
            # Update preview with new encoded image
            self.image_display.setPixmap(QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio))
            QMessageBox.information(self, "Success", "Message encoded and image saved.")

    # Called when user clicks "Decode Message"
    def decode_message(self):
        # Check if image loaded
        if not self.image_path:
            QMessageBox.warning(self, "Error", "Please load an image.")
            return
        try:
            img = Image.open(self.image_path)  # Open current image
            decoded = stepic.decode(img)  # Extract hidden message bytes
            # Convert bytes to string, ignoring errors
            msg = decoded.decode(errors='ignore') if isinstance(decoded, bytes) else decoded
            self.result_label.setText(f"Decoded Message: {msg}")  # Show decoded message in label
        except Exception as e:
            # Show error popup if decoding failed
            QMessageBox.critical(self, "Decoding Failed", str(e))


# Standard Python boilerplate to run the app only if this script is run directly
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create Qt application object
    window = StegooQt()  # Create instance of our main window class
    window.show()  # Show window on screen
    sys.exit(app.exec_())  # Run the Qt event loop until app exits
