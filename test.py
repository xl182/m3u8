# 导入必要的库
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton

# 创建一个应用程序对象
app = QApplication([])

# 创建一个主窗口对象
window = QMainWindow()

# 创建一个列表部件对象
list_widget = QListWidget()

# 设置列表部件的视图模式为图标视图
list_widget.setViewMode(QListWidget.IconMode)

# 向列表部件中添加多个窗口
for i in range(10):
    # 创建一个按钮对象
    button = QPushButton(f"窗口{i}")

    # 将按钮添加到列表部件中
    list_widget.addItem(button)

# 将列表部件添加到主窗口中
window.setCentralWidget(list_widget)

# 显示主窗口
window.show()

# 启动应用程序
app.exec_()