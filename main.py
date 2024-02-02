import os.path
import sys
from pathlib import Path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QWidget, QDialog

from ui import ui_download_config
from utils.prepare import prepare
from ui.ui_downloader import Ui_Downloader
from ui.ui_state_widget import Ui_stateWidget
from utils.downloader import DownloadThread, get_store_path


class Main(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.download_config_widget = None
        self.scroll_area_layout = None
        self.ui = Ui_Downloader()
        self.w, self.h = self.width(), self.height()
        self.state_widgets = []
        self.thread_list = []
        self.ui.setupUi(self)

        self.setup()

    def paste_url(self):
        clipboard = QApplication.clipboard()
        url = clipboard.text()
        self.ui.urlEdit.setText(url)

    def setup(self):
        self.ui.pasteButton.clicked.connect(self.paste_url)
        self.ui.downloadButton.clicked.connect(self.show_config_dialog)

    def show_config_dialog(self):
        url = self.ui.urlEdit.text()
        store_path = get_store_path()
        self.download_config_widget = QDialog()
        self.download_config_widget.ui = ui_download_config.Ui_Dialog()
        self.download_config_widget.ui.setupUi(self.download_config_widget)
        self.download_config_widget.ui.urlEdit.setText(url)
        self.download_config_widget.ui.pathEdit.setText(store_path)
        self.download_config_widget.show()
        self.download_config_widget.ui.buttonBox.accepted.connect(lambda: self.download(url, store_path))

    def download(self, url, store_path):
        self.ui.urlEdit.clear()
        if "http" not in url:
            return

        self.w, self.h = self.width(), self.height()
        state_widget = QWidget()
        state_widget.ui = Ui_stateWidget()
        state_widget.ui.setupUi(state_widget)
        state_widget.ui.pathLabel.setText(store_path)

        def add_state_widget():
            item = QListWidgetItem()
            item.setSizeHint(QSize(self.width() - 50, int(self.height() / 10)))
            self.ui.infoWidget.addItem(item)
            self.ui.infoWidget.setItemWidget(item, state_widget)
            state_widget.ui.progressBar.setValue(0)

        add_state_widget()

        download_mode = self.download_config_widget.ui.modeBox.currentIndex() + 1
        download_thread = DownloadThread(url, download_mode, store_path)
        self.thread_list.append(download_thread)
        download_thread.start()

        def update_show(str_goal, string):
            if str_goal == "value":
                state_widget.ui.progressBar.setValue(int(string))

        download_thread.signal.connect(update_show)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = Main()
    downloader.show()
    sys.exit(app.exec_())
