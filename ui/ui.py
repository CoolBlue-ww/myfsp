import os ,sys
from lxml import html
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                             QLabel, QFileDialog, QSplitter, QListWidget)


class XPathValidator(QMainWindow):
    def __init__(self):
        """
        def on_click():
    messagebox.showinfo('Message', 'Hello World')
    root = tk.Tk()
    root.title('Hello World')
    root.geometry('300x300')
    btn = tk.Button(root, text='Click Me', command=on_click)
    btn.pack(expand=True, fill='x')
    root.mainloop()
        """
        super().__init__()
        self.setWindowTitle("XPath 验证工具")
        self.setGeometry(100, 100, 1000, 700)

        # 中央部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 创建分割器，使界面可以调整大小
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧面板 - HTML 内容
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # HTML 文件加载按钮
        load_btn = QPushButton("加载 HTML 文件")
        load_btn.clicked.connect(self.load_html_file)
        left_layout.addWidget(load_btn)

        # HTML 内容显示
        self.html_display = QTextEdit()
        self.html_display.setPlaceholderText("HTML 内容将显示在这里...")
        left_layout.addWidget(QLabel("HTML 内容:"))
        left_layout.addWidget(self.html_display)

        # 右侧面板 - XPath 输入和结果
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # XPath 输入
        right_layout.addWidget(QLabel("XPath 表达式:"))
        self.xpath_input = QLineEdit()
        self.xpath_input.setPlaceholderText("输入 XPath 表达式...")
        self.xpath_input.textChanged.connect(self.evaluate_xpath)
        right_layout.addWidget(self.xpath_input)

        # 结果显示
        right_layout.addWidget(QLabel("匹配结果:"))
        self.result_list = QListWidget()
        right_layout.addWidget(self.result_list)

        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])  # 初始大小比例

        main_layout.addWidget(splitter)

        # 存储 HTML 文档对象
        self.html_doc = None

    def load_html_file(self):
        """加载 HTML 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 HTML 文件", "", "HTML 文件 (*.atc_html *.htm)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                    self.html_display.setPlainText(html_content)
                    # 解析 HTML
                    self.html_doc = html.fromstring(html_content)
                    # 清空之前的 XPath 结果
                    self.result_list.clear()
            except Exception as e:
                self.html_display.setPlainText(f"错误: {str(e)}")
                self.html_doc = None

    def evaluate_xpath(self):
        """评估 XPath 表达式并显示结果"""
        if not self.html_doc:
            return

        xpath_expr = self.xpath_input.text()
        if not xpath_expr:
            self.result_list.clear()
            return

        try:
            # 执行 XPath 查询
            results = self.html_doc.xpath(xpath_expr)

            # 清空之前的结果
            self.result_list.clear()

            # 显示结果
            for i, result in enumerate(results):
                if isinstance(result, str):
                    self.result_list.addItem(f"{i + 1}: {result}")
                else:
                    # 对于元素节点，显示标签和文本内容
                    text_content = result.text_content().strip()[:100] + "..." if len(
                        result.text_content().strip()) > 100 else result.text_content().strip()
                    self.result_list.addItem(f"{i + 1}: <{result.tag}> - {text_content}")

        except Exception as e:
            self.result_list.clear()
            self.result_list.addItem(f"XPath 错误: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XPathValidator()
    window.show()
    sys.exit(app.exec())