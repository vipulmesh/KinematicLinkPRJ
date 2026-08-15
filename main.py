import sys
import os
from PySide6.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QFrame, 
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QIcon, QPixmap, QFont, QColor
from PySide6.QtCore import Qt

from gui.gui import MainWindow


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class SplashScreen(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(600, 400)
        
        # Container frame for styling
        container = QFrame(self)
        container.setGeometry(10, 10, 580, 380)
        container.setStyleSheet('''
            QFrame {
                background-color: #1e1e2e;
                border: 2px solid #313244;
                border-radius: 12px;
            }
            QLabel {
                color: #cdd6f4;
                border: none;
                background: transparent;
            }
        ''')
        
        # Drop shadow for professional look
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Application Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        splash_image_path = resource_path(os.path.join("assets", "splash.png"))
        
        if os.path.exists(splash_image_path):
            pixmap = QPixmap(splash_image_path)
            # Scale if too large, maintain aspect ratio
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            # Fallback icon or text if splash.png is missing
            icon_path = resource_path(os.path.join("assets", "app_icon.ico"))
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(pixmap)
            else:
                logo_label.setText("[Application Logo]")
                logo_label.setStyleSheet("color: #a6adc8; font-size: 16px; font-style: italic;")
                
        layout.addWidget(logo_label)
        
        # Title
        title = QLabel("FOUR-BAR\nKINEMATIC CHAIN SIMULATOR")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 22, QFont.Bold)
        title_font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        title.setFont(title_font)
        title.setStyleSheet("color: #89b4fa;")
        
        # Version
        version = QLabel("Version 2.0")
        version.setAlignment(Qt.AlignCenter)
        version_font = QFont("Segoe UI", 12)
        version.setFont(version_font)
        version.setStyleSheet("color: #a6adc8;")
        
        # Loading
        loading = QLabel("Loading...")
        loading.setAlignment(Qt.AlignCenter)
        loading_font = QFont("Segoe UI", 10)
        loading_font.setItalic(True)
        loading.setFont(loading_font)
        loading.setStyleSheet("color: #74c7ec; margin-top: 30px;")
        
        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(loading)


def main():
    app = QApplication(sys.argv)
    
    # Set taskbar icon for Windows to ensure it shows up correctly
    if os.name == 'nt':
        import ctypes
        try:
            myappid = 'vipul.fourbar.simulator.2.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Load icon
    icon_path = resource_path(os.path.join("assets", "app_icon.ico"))
    app_icon = None
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

    # Show Splash Screen
    splash = SplashScreen()
    splash.show()
    
    # Process events so splash screen paints immediately
    app.processEvents()

    # Initialize Main Window
    window = MainWindow()
    if app_icon:
        window.setWindowIcon(app_icon)
        
    # Close splash and show main window
    splash.close()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()    