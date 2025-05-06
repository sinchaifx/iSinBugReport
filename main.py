import sys
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
                              QPushButton, QMessageBox)
from PySide6.QtCore import Qt

# โหลด API Key จากไฟล์ .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    QMessageBox.critical(None, "ข้อผิดพลาด", "ไม่พบ GOOGLE_API_KEY ในไฟล์ .env หรือ Environment Variable กรุณาตั้งค่าก่อนใช้งาน")
    sys.exit()

# กำหนดค่า Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

class BugReportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bug Report Generator with AI Summary")
        self.setMinimumSize(1200, 800)
        
        # ตัวแปรสำหรับเก็บลิงค์วิดีโอ
        self.video_links = []
        
        # สร้าง UI
        self.setup_ui()
        
    def setup_ui(self):
        # สร้าง widget หลัก
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout หลัก
        main_layout = QHBoxLayout(main_widget)
        
        # สร้างส่วนซ้าย (Input)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # หัวข้อปัญหา
        title_layout = QHBoxLayout()
        title_label = QLabel("หัวข้อปัญหา:")
        self.title_input = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        left_layout.addLayout(title_layout)
        
        # รายละเอียดปัญหา
        details_label = QLabel("รายละเอียดปัญหา:")
        self.details_input = QTextEdit()
        left_layout.addWidget(details_label)
        left_layout.addWidget(self.details_input)
        
        # ลิงค์วิดีโอ
        video_layout = QHBoxLayout()
        video_label = QLabel("ลิงค์วิดีโอ:")
        self.video_input = QLineEdit()
        self.video_input.setPlaceholderText("ใส่ลิงค์วิดีโอ (เช่น YouTube, Vimeo)")
        video_layout.addWidget(video_label)
        video_layout.addWidget(self.video_input)
        left_layout.addLayout(video_layout)
        
        # วิธี Reproduce
        reproduce_label = QLabel("วิธี Reproduce:")
        self.reproduce_input = QTextEdit()
        left_layout.addWidget(reproduce_label)
        left_layout.addWidget(self.reproduce_input)
        
        # ผลลัพธ์ที่คาดหวัง
        expected_layout = QHBoxLayout()
        expected_label = QLabel("ผลลัพธ์ที่คาดหวัง:")
        self.expected_input = QLineEdit()
        expected_layout.addWidget(expected_label)
        expected_layout.addWidget(self.expected_input)
        left_layout.addLayout(expected_layout)
        
        # ผลลัพธ์จริง
        actual_layout = QHBoxLayout()
        actual_label = QLabel("ผลลัพธ์จริง:")
        self.actual_input = QLineEdit()
        actual_layout.addWidget(actual_label)
        actual_layout.addWidget(self.actual_input)
        left_layout.addLayout(actual_layout)
        
        # ปุ่มสร้างรายงาน
        generate_button = QPushButton("สร้างรายงาน Bug")
        generate_button.clicked.connect(self.generate_report)
        left_layout.addWidget(generate_button)
        
        # สร้างส่วนขวา (Output)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        output_label = QLabel("รายงาน Bug (Markdown):")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        # ปุ่มคัดลอก
        copy_button = QPushButton("คัดลอก Markdown")
        copy_button.clicked.connect(self.copy_to_clipboard)
        
        right_layout.addWidget(output_label)
        right_layout.addWidget(self.output_text)
        right_layout.addWidget(copy_button)
        
        # เพิ่มส่วนซ้ายและขวาเข้าไปใน layout หลัก
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)
        
    def generate_report(self):
        issue_title = self.title_input.text().strip()
        issue_details = self.details_input.toPlainText().strip()
        reproduce_steps = self.reproduce_input.toPlainText().strip()
        expected_result = self.expected_input.text().strip()
        actual_result = self.actual_input.text().strip()
        video_link = self.video_input.text().strip()
        
        if not all([issue_title, issue_details, reproduce_steps, expected_result, actual_result]):
            QMessageBox.warning(self, "ข้อมูลไม่ครบถ้วน", "กรุณากรอกข้อมูลทุกช่องยกเว้นลิงค์วิดีโอ")
            return
            
        prompt_text = f"""
โปรดสรุป Bug Report นี้เป็นภาษาไทยในย่อหน้าเดียว โดยเน้นที่ปัญหาหลัก วิธีทำให้เกิดซ้ำ และผลลัพธ์ที่แตกต่างกัน:

หัวข้อปัญหา: {issue_title}
รายละเอียดปัญหา: {issue_details}
วิธี Reproduce ปัญหา: {reproduce_steps}
ผลลัพธ์ที่คาดหวัง: {expected_result}
ผลลัพธ์จริง: {actual_result}
ลิงค์วิดีโอ: {video_link if video_link else 'ไม่มี'}

สรุป:
"""
        
        gemini_summary = "ไม่สามารถสร้างสรุปจาก Gemini ได้"
        try:
            response = model.generate_content(prompt_text)
            gemini_summary = response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            QMessageBox.critical(self, "API Error", f"เกิดข้อผิดพลาดในการเรียก Gemini API: {e}\n\nแสดงรายงานแบบไม่มีสรุปจาก AI แทน")
            
        markdown_report = f"""# Bug Report: {issue_title}

**สรุป (โดย AI):**
{gemini_summary}

---

## รายละเอียดปัญหา
{issue_details}

---

## วิธี Reproduce ปัญหา
{reproduce_steps}

---

## ผลลัพธ์ที่คาดหวัง
{expected_result}

---

## ผลลัพธ์จริง
{actual_result}

---

## ลิงค์วิดีโอ
{video_link if video_link else 'ไม่มี'}

---
"""
        
        self.output_text.setPlainText(markdown_report)
        
    def copy_to_clipboard(self):
        markdown_text = self.output_text.toPlainText().strip()
        if markdown_text:
            QApplication.clipboard().setText(markdown_text)
            QMessageBox.information(self, "สำเร็จ", "คัดลอก Markdown ไปยัง Clipboard แล้ว")
        else:
            QMessageBox.warning(self, "ไม่มีข้อมูล", "ไม่มีข้อความ Markdown ที่จะคัดลอก")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BugReportWindow()
    window.show()
    sys.exit(app.exec())