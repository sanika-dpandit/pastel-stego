# pastel-stego
# 🌸 Pastel Stego - PyQt5 Steganography Tool

A pastel-themed desktop application for securely hiding and extracting messages from images using LSB steganography (via Stepic). Developed with PyQt5, the tool provides an aesthetic, drag-and-drop interface and supports image generation, preview, and message encoding/decoding.
 
 # Features

| Feature           | Description                                                              |
|-------------------|--------------------------------------------------------------------------|
|  Pastel UI        | Soft gradient blue UI with styled buttons for a smooth user experience   |
|  Drag & Drop      | Easily drop `.png` or `.bmp` files into the interface                    |
|  Browse & Preview | Browse image files and preview selected images                           |
|  Image Generation | Generate blank, random noise, or custom gradient images for testing      |
|  Encode Message   | Hide text securely using LSB technique (Stepic)                          |
|  Decode Message   | Extract hidden message from images                                       |
|  Save Support     | Save generated or encoded images in PNG format                           |
|  Informative UI   | Popups for success/error and real-time image/message display             |

## How to Use
1. Launch the tool.
2. Choose to use an existing image via drag-and-drop or browsing, or generate a new one (blank, noise, gradient).
3. Navigate to the Encode/Decode page.
4. Enter your secret message and click **Encode Message** to hide the message.
5. Click Decode Message to extract the hidden message from an image.

## Technologies Used
- Python 3
- PyQt5 – GUI framework
- Pillow (PIL) – Image processing
- Stepic – LSB-based steganography
- colorsys, random – For image generation

## Future Enhancements
- Add optional encryption (e.g., Caesar cipher or AES encryption)
- Support for multi-image batch encoding/decoding
- File hiding (beyond text messages)
- Additional UI themes (e.g., dark mode)

## Author
Sanika Pandit 
