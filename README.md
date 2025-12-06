# 📸 GeoSnap

[![CI](https://github.com/meinKommandant/GeoSnap/actions/workflows/ci.yml/badge.svg)](https://github.com/meinKommandant/GeoSnap/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey.svg)
![Version](https://img.shields.io/badge/version-2.2.0-green.svg)

**GeoSnap** is a powerful desktop tool that transforms your geotagged photos into professional KMZ reports for Google Earth and detailed Excel spreadsheets.

> **Turn your field photos into actionable geographic data in seconds.**

---

## ✨ Key Features

*   **🗺️ Portable KMZ Generation**: Creates `.kmz` files with embedded thumbnails. Share your reports easily via email without worrying about broken image links.
*   **📊 Excel Reporting**: Automatically generates formatted Excel (`.xlsx`) reports with GPS coordinates, timestamps, and altitude data.
*   **📄 Word Reports**: Generate professional Word (`.docx`) photo reports in reverse mode with landscape layout and 4 photos per page.
*   **🔄 Reverse Mode**: Import data from Excel to regenerate KMZ and Word reports.
*   **⚡ High Performance**: Multi-threaded processing ensures fast extraction of metadata from hundreds of images.
*   **🔄 Smart Orientation**: Automatically corrects image rotation based on EXIF data.
*   **🖥️ User-Friendly GUI**: Simple, intuitive interface for selecting folders and generating reports.

## 🚀 Installation

### Prerequisites
*   Python 3.8 or higher
*   pip (Python package installer)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/meinKommandant/GeoSnap.git
    cd GeoSnap
    ```

2.  **Create a virtual environment (Recommended):**
    *   Windows:
        ```bash
        py -m venv venv
        .\venv\Scripts\activate
        ```
    *   macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## 📖 Usage

1.  **Launch the application:**
    ```bash
    py geosnap_app.py
    ```

2.  **Select Input Folder:** Choose the directory containing your geotagged photos (JPG, HEIC, PNG).
3.  **Select Output Folder:** Choose where you want the report files to be saved.
4.  **Generate:** Click "Procesar" to generate your KMZ and Excel files.

## 🤝 Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.