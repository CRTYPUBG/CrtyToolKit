"""
Crty ToolKit
© 2025 Crty. Tüm hakları saklıdır.
"""

import sys
import os
import shutil
import winreg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Kayıt defteri anahtarı yolu
REG_PATH = r"Software\Tencent\MobileGamePC"

# Yedek dosya yolu
BACKUP_FILE = "registry_backup.reg"

# Kayıt defteri yedekleme fonksiyonu
def backup_registry():
    try:
        os.system(f'reg export "HKCU\\{REG_PATH}" {BACKUP_FILE} /y')
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

# Kayıt defterinden anahtarları okuma fonksiyonu
def read_registry_keys():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
            i = 0
            data = {}
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    data[name] = value
                    i += 1
                except OSError:
                    break
            return data
    except Exception as e:
        print(f"Hata: {e}")
        return {}

# Kayıt defterine değer yazma fonksiyonu
def write_registry_value(name, value):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
            # Veri tipine göre ayarla
            if isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            elif isinstance(value, str):
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            else:
                return False
        return True
    except Exception as e:
        print(f"Hata: {e}")
        return False

@app.route("/")
def index():
    # Registry değerlerini gönder
    data = read_registry_keys()
    return render_template("index.html", registry=data)

@app.route("/backup", methods=["POST"])
def backup():
    success = backup_registry()
    return jsonify({"success": success})

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    results = {}
    for key, val in data.items():
        # Burada val tipini uygun hale getirebilirsin (string veya int)
        try:
            if val.isdigit():
                val = int(val)
        except:
            pass
        results[key] = write_registry_value(key, val)
    return jsonify(results)

def run_flask():
    app.run(port=5000, debug=False)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crty ToolKit")
        self.setGeometry(100, 100, 900, 600)
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)
        self.browser.load(QUrl("http://127.0.0.1:5000"))

if __name__ == "__main__":
    from threading import Thread
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    app_qt = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app_qt.exec_())
