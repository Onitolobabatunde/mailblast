#!/usr/bin/env python3
"""
MailBlast Pro - Professional Email Sending Desktop Application
"""

import sys
import os
import json
import csv
import smtplib
import ssl
import time
import re
import platform
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from cryptography.fernet import Fernet

_MACOS = platform.system() == "Darwin"
_WINDOWS = platform.system() == "Windows"
_UI_FONT = "SF Pro Display" if _MACOS else "Segoe UI"
_MONO_FONT = "Menlo" if _MACOS else "Consolas"

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QCheckBox, QSpinBox, QComboBox, QFileDialog, QMessageBox,
    QSplitter, QFrame, QScrollArea, QProgressBar, QHeaderView, QDialog,
    QFormLayout, QDialogButtonBox, QGroupBox, QDoubleSpinBox, QStatusBar,
    QToolBar, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QObject, QByteArray
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QPixmap, QPainter, QLinearGradient,
    QBrush, QAction, QFontDatabase, QTextCursor
)

# ─── Constants ────────────────────────────────────────────────────────────────

APP_NAME = "MailBlast Pro"
APP_VERSION = "1.0.0"
if _MACOS:
    CONFIG_DIR = Path.home() / "Library" / "Application Support" / "MailBlast"
else:
    CONFIG_DIR = Path.home() / ".mailblast"
CONFIG_FILE = CONFIG_DIR / "config.json"
KEY_FILE = CONFIG_DIR / ".key"

PRESET_SMTP = {
    "Gmail": {"host": "smtp.gmail.com", "port": 587, "ssl": False, "tls": True},
    "Gmail SSL": {"host": "smtp.gmail.com", "port": 465, "ssl": True, "tls": False},
    "Yahoo": {"host": "smtp.mail.yahoo.com", "port": 587, "ssl": False, "tls": True},
    "Outlook/Hotmail": {"host": "smtp-mail.outlook.com", "port": 587, "ssl": False, "tls": True},
    "GoDaddy": {"host": "smtpout.secureserver.net", "port": 465, "ssl": True, "tls": False},
    "Truehost/Roundcube": {"host": "mail.truehost.com.ng", "port": 587, "ssl": False, "tls": True},
    "Zoho Mail": {"host": "smtp.zoho.com", "port": 587, "ssl": False, "tls": True},
    "Custom": {"host": "", "port": 587, "ssl": False, "tls": True},
}

DARK_STYLE = """
QMainWindow, QDialog {
    background-color: #0d0f14;
    color: #e8eaf0;
}
QWidget {
    background-color: #0d0f14;
    color: #e8eaf0;
    font-family: -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #1e2330;
    background-color: #111520;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #111520;
    color: #6b7280;
    padding: 10px 22px;
    border: none;
    font-weight: 500;
    font-size: 12px;
    letter-spacing: 0.3px;
}
QTabBar::tab:selected {
    background-color: #1a1f2e;
    color: #60a5fa;
    border-bottom: 2px solid #3b82f6;
}
QTabBar::tab:hover:!selected {
    color: #94a3b8;
    background-color: #141824;
}
QGroupBox {
    border: 1px solid #1e2330;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px;
    font-weight: 600;
    font-size: 11px;
    color: #4b5563;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #111520;
    border: 1px solid #1e2330;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e8eaf0;
    selection-background-color: #3b82f6;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #3b82f6;
    background-color: #141824;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #6b7280;
}
QComboBox QAbstractItemView {
    background-color: #111520;
    border: 1px solid #1e2330;
    selection-background-color: #1e3a5f;
    color: #e8eaf0;
    outline: none;
}
QPushButton {
    background-color: #1e2330;
    color: #94a3b8;
    border: 1px solid #2a3142;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: 500;
    min-height: 32px;
}
QPushButton:hover {
    background-color: #252d3d;
    color: #e8eaf0;
    border-color: #3b82f6;
}
QPushButton:pressed {
    background-color: #1a2235;
}
QPushButton#primary {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    font-weight: 600;
}
QPushButton#primary:hover {
    background-color: #3b82f6;
}
QPushButton#primary:pressed {
    background-color: #1d4ed8;
}
QPushButton#danger {
    background-color: #7f1d1d;
    color: #fca5a5;
    border: none;
}
QPushButton#danger:hover {
    background-color: #991b1b;
    color: #ffffff;
}
QPushButton#success {
    background-color: #14532d;
    color: #86efac;
    border: none;
    font-weight: 600;
}
QPushButton#success:hover {
    background-color: #166534;
    color: #ffffff;
}
QTableWidget {
    background-color: #0d0f14;
    border: 1px solid #1e2330;
    border-radius: 8px;
    gridline-color: #1a1f2e;
    color: #e8eaf0;
    selection-background-color: #1e3a5f;
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #111520;
}
QTableWidget::item:alternate {
    background-color: #0f1118;
}
QHeaderView::section {
    background-color: #111520;
    color: #4b5563;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #1e2330;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
QScrollBar:vertical {
    background: #0d0f14;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #1e2330;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #2a3347;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: #0d0f14;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #1e2330;
    border-radius: 4px;
}
QCheckBox {
    spacing: 8px;
    color: #94a3b8;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #2a3142;
    background-color: #111520;
}
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #3b82f6;
    image: none;
}
QProgressBar {
    border: none;
    border-radius: 4px;
    background-color: #111520;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2563eb, stop:1 #7c3aed);
    border-radius: 4px;
}
QStatusBar {
    background-color: #080a0f;
    color: #4b5563;
    border-top: 1px solid #1e2330;
    font-size: 11px;
}
QSplitter::handle {
    background-color: #1e2330;
    width: 1px;
}
QLabel#heading {
    font-size: 20px;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.3px;
}
QLabel#subheading {
    font-size: 12px;
    color: #4b5563;
    letter-spacing: 0.2px;
}
QLabel#stat_value {
    font-size: 28px;
    font-weight: 700;
    color: #f1f5f9;
}
QLabel#stat_label {
    font-size: 11px;
    color: #4b5563;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
"""

LIGHT_STYLE = DARK_STYLE.replace("#0d0f14", "#f7f8fb") \
    .replace("#080a0f", "#ffffff") \
    .replace("#111520", "#ffffff") \
    .replace("#141824", "#f2f4f8") \
    .replace("#1a1f2e", "#e5e7eb") \
    .replace("#1e2330", "#d8dee8") \
    .replace("#2a3142", "#c9d1dd") \
    .replace("#252d3d", "#eef2f7") \
    .replace("#e8eaf0", "#172033") \
    .replace("#f1f5f9", "#0f172a") \
    .replace("#94a3b8", "#475569") \
    .replace("#6b7280", "#64748b") \
    .replace("#4b5563", "#64748b") \
    .replace("#374151", "#64748b")

# ─── Security / Crypto ────────────────────────────────────────────────────────

def get_or_create_key():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    # Set file permissions securely if possible (ignore errors on Windows/macOS)
    try:
        KEY_FILE.chmod(0o600)
    except Exception:
        pass
    return key

def encrypt(text: str) -> str:
    f = Fernet(get_or_create_key())
    return f.encrypt(text.encode()).decode()

def decrypt(token: str) -> str:
    try:
        f = Fernet(get_or_create_key())
        return f.decrypt(token.encode()).decode()
    except Exception:
        return token

# ─── Config ───────────────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text())
            cfg.setdefault("smtp_accounts", [])
            cfg.setdefault("settings", {"delay": 2.0, "threads": 3, "retry": True})
            cfg.setdefault("ui", {"theme": "dark"})
            return cfg
        except Exception:
            pass
    return {"smtp_accounts": [], "settings": {"delay": 2.0, "threads": 3, "retry": True}, "ui": {"theme": "dark"}}

def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))

# ─── Email Validation ─────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(email.strip()))

# ─── SMTP Worker ──────────────────────────────────────────────────────────────

class EmailSendWorker(QObject):
    log_signal = pyqtSignal(str, str)   # message, level (info/success/error/warn)
    progress_signal = pyqtSignal(int, int)  # sent, total
    finished_signal = pyqtSignal(dict)      # summary
    status_signal = pyqtSignal(str)

    def __init__(self, recipients, smtp_accounts, subject, body_text,
                 is_html, delay, attachments=None, from_account=None, reply_to=None):
        super().__init__()
        self.recipients = recipients
        self.smtp_accounts = smtp_accounts
        self.subject = subject
        self.body_text = body_text
        self.is_html = is_html
        self.delay = delay
        self.attachments = attachments or []
        self.from_account = (from_account or "").strip()
        self.reply_to = (reply_to or "").strip()
        self._stop = False
        self._pause = False

    def stop(self):
        self._stop = True

    def pause(self):
        self._pause = not self._pause

    def run(self):
        sent = 0
        failed = 0
        total = len(self.recipients)
        smtp_idx = 0
        connection = None
        current_smtp = None

        self.log_signal.emit(f"Starting campaign: {total} recipients", "info")

        for i, recipient in enumerate(self.recipients):
            while self._pause:
                time.sleep(0.3)
            if self._stop:
                self.log_signal.emit("Campaign stopped by user.", "warn")
                break

            email = recipient.get("email", "").strip()
            if not is_valid_email(email):
                self.log_signal.emit(f"  ✗ Invalid email skipped: {email}", "error")
                failed += 1
                self.progress_signal.emit(sent, total)
                continue

            # Build message
            sender_name = recipient.get("sender_name", "")
            name = recipient.get("name", email.split("@")[0])
            smtp = self.smtp_accounts[smtp_idx % len(self.smtp_accounts)]
            from_addr = smtp["username"]

            # Use custom From Account header if provided; envelope sender stays as SMTP username
            from_header = self.from_account if self.from_account else from_addr
            from_display = f'"{sender_name}" <{from_header}>' if sender_name else from_header

            subject = self.subject.replace("{name}", name).replace(
                "{email}", email).replace("{sender_name}", sender_name)

            # Fill placeholders in body
            body = self.body_text
            for key, val in recipient.items():
                body = body.replace(f"{{{key}}}", val)

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_display
            msg["To"] = email
            if self.reply_to:
                msg["Reply-To"] = self.reply_to
            if self.is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))

            # Attachments
            for att_path in self.attachments:
                try:
                    with open(att_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(att_path)}")
                    msg.attach(part)
                except Exception as e:
                    self.log_signal.emit(f"  ⚠ Attachment error: {e}", "warn")

            # Send
            try:
                # Reuse or create SMTP connection
                smtp_key = f"{smtp['host']}:{smtp['port']}:{smtp['username']}"
                if current_smtp != smtp_key or connection is None:
                    if connection:
                        try:
                            connection.quit()
                        except Exception:
                            pass
                    connection = self._connect_smtp(smtp)
                    current_smtp = smtp_key
                    self.log_signal.emit(
                        f"  ⟳ Connected to SMTP: {smtp['host']} ({smtp['username']})", "info")

                connection.sendmail(from_addr, [email], msg.as_string())
                self.log_signal.emit(
                    f"  ✓ Sent → {email}  [{smtp['host']} | {smtp['username']}]", "success")
                sent += 1
                smtp_idx += 1  # rotate

            except smtplib.SMTPServerDisconnected:
                # Try reconnect once
                try:
                    connection = self._connect_smtp(smtp)
                    connection.sendmail(from_addr, [email], msg.as_string())
                    self.log_signal.emit(f"  ✓ Sent (retry) → {email}", "success")
                    sent += 1
                    smtp_idx += 1
                except Exception as e2:
                    self.log_signal.emit(
                        f"  ✗ Failed → {email}: [{type(e2).__name__}] {e2}", "error")
                    failed += 1
                    connection = None
            except Exception as e:
                self.log_signal.emit(
                    f"  ✗ Failed → {email}: [{type(e).__name__}] {e}", "error")
                failed += 1
                connection = None
                smtp_idx += 1  # try next smtp

            self.progress_signal.emit(sent, total)
            self.status_signal.emit(f"Sending... {i+1}/{total} | ✓ {sent} | ✗ {failed}")

            if i < total - 1 and not self._stop:
                time.sleep(self.delay)

        if connection:
            try:
                connection.quit()
            except Exception:
                pass

        summary = {"sent": sent, "failed": failed, "total": total}
        self.log_signal.emit(
            f"\n{'='*50}\n  Campaign Complete: {sent} sent, {failed} failed\n{'='*50}", "info")
        self.finished_signal.emit(summary)

    def _connect_smtp(self, smtp: dict):
        host = smtp["host"]
        port = int(smtp["port"])
        user = smtp["username"]
        password = decrypt(smtp.get("password_enc", smtp.get("password", "")))

        if smtp.get("ssl"):
            context = ssl.create_default_context()
            conn = smtplib.SMTP_SSL(host, port, context=context, timeout=20)
        else:
            conn = smtplib.SMTP(host, port, timeout=20)
            if smtp.get("tls", True):
                conn.starttls()

        conn.login(user, password)
        return conn


class SendThread(QThread):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker

    def run(self):
        self.worker.run()


class SmtpHealthWorker(QThread):
    result_signal = pyqtSignal(int, bool, str)  # row, success, message

    def __init__(self, accounts):
        super().__init__()
        self.accounts = accounts  # list of (row_index, account_dict)

    def run(self):
        for row, acc in self.accounts:
            try:
                host, port = acc["host"], int(acc["port"])
                pwd = decrypt(acc.get("password_enc", ""))
                if acc.get("ssl"):
                    ctx = ssl.create_default_context()
                    conn = smtplib.SMTP_SSL(host, port, context=ctx, timeout=10)
                else:
                    conn = smtplib.SMTP(host, port, timeout=10)
                    if acc.get("tls"):
                        conn.starttls()
                conn.login(acc["username"], pwd)
                conn.quit()
                self.result_signal.emit(row, True, "OK")
            except Exception as e:
                self.result_signal.emit(row, False, str(e)[:60])


# ─── SMTP Account Dialog ──────────────────────────────────────────────────────

class SMTPDialog(QDialog):
    def __init__(self, parent=None, account=None):
        super().__init__(parent)
        self.setWindowTitle("SMTP Account")
        self.setMinimumWidth(480)
        self.setStyleSheet(DARK_STYLE)
        self._build(account)

    def _build(self, account):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Configure SMTP Account")
        title.setObjectName("heading")
        title.setFont(QFont(_UI_FONT, 16, QFont.Weight.Bold))
        layout.addWidget(title)
        info = QLabel("You can use any SMTP server. Fill in your provider's details or choose a preset.")
        info.setStyleSheet("color: #60a5fa; font-size: 11px; background: transparent;")
        layout.addWidget(info)

        # Preset picker
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Quick Setup:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PRESET_SMTP.keys()))
        self.preset_combo.currentTextChanged.connect(self._apply_preset)
        preset_row.addWidget(self.preset_combo)
        layout.addLayout(preset_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1e2330; border: none; max-height: 1px;")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_edit = QLineEdit(account.get("name", "") if account else "")
        self.name_edit.setPlaceholderText("e.g. Gmail Main")
        form.addRow("Account Name:", self.name_edit)

        self.host_edit = QLineEdit(account.get("host", "") if account else "")
        self.host_edit.setPlaceholderText("smtp.gmail.com")
        form.addRow("SMTP Host:", self.host_edit)

        self.port_edit = QSpinBox()
        self.port_edit.setRange(1, 65535)
        self.port_edit.setValue(int(account.get("port", 587)) if account else 587)
        form.addRow("Port:", self.port_edit)

        self.user_edit = QLineEdit(account.get("username", "") if account else "")
        self.user_edit.setPlaceholderText("you@example.com")
        form.addRow("Username / Email:", self.user_edit)

        self.pass_edit = QLineEdit()
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setPlaceholderText("App password or SMTP password")
        if account:
            self.pass_edit.setText(decrypt(account.get("password_enc", "")))
        form.addRow("Password:", self.pass_edit)

        flags_layout = QHBoxLayout()
        self.ssl_check = QCheckBox("Use SSL")
        self.tls_check = QCheckBox("Use STARTTLS")
        if account:
            self.ssl_check.setChecked(account.get("ssl", False))
            self.tls_check.setChecked(account.get("tls", True))
        else:
            self.tls_check.setChecked(True)
        flags_layout.addWidget(self.ssl_check)
        flags_layout.addWidget(self.tls_check)
        flags_layout.addStretch()
        form.addRow("Encryption:", flags_layout)

        layout.addLayout(form)

        # Test button
        test_btn = QPushButton("⚡ Test Connection")
        test_btn.clicked.connect(self._test_connection)
        layout.addWidget(test_btn)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setObjectName("primary")
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(
            "background-color: #2563eb; color: white; font-weight: 600; border: none;")
        layout.addWidget(btns)

    def _apply_preset(self, name):
        p = PRESET_SMTP.get(name, {})
        if p.get("host"):
            self.host_edit.setText(p["host"])
            self.port_edit.setValue(p["port"])
            self.ssl_check.setChecked(p.get("ssl", False))
            self.tls_check.setChecked(p.get("tls", True))
            if not self.name_edit.text():
                self.name_edit.setText(name)

    def _test_connection(self):
        host = self.host_edit.text().strip()
        port = self.port_edit.value()
        user = self.user_edit.text().strip()
        pwd = self.pass_edit.text()
        use_ssl = self.ssl_check.isChecked()
        use_tls = self.tls_check.isChecked()

        if not all([host, user, pwd]):
            QMessageBox.warning(self, "Missing Fields", "Please fill in host, username, and password.")
            return

        try:
            if use_ssl:
                ctx = ssl.create_default_context()
                conn = smtplib.SMTP_SSL(host, port, context=ctx, timeout=10)
            else:
                conn = smtplib.SMTP(host, port, timeout=10)
                if use_tls:
                    conn.starttls()
            conn.login(user, pwd)
            conn.quit()
            QMessageBox.information(self, "Success", f"✓ Connection to {host}:{port} successful!")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", f"✗ {str(e)}")

    def get_account(self):
        return {
            "name": self.name_edit.text().strip() or self.host_edit.text().strip(),
            "host": self.host_edit.text().strip(),
            "port": self.port_edit.value(),
            "username": self.user_edit.text().strip(),
            "password_enc": encrypt(self.pass_edit.text()),
            "ssl": self.ssl_check.isChecked(),
            "tls": self.tls_check.isChecked(),
        }


# ─── Log Console Widget ───────────────────────────────────────────────────────

class LogConsole(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont(_MONO_FONT, 11))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #080a0f;
                color: #94a3b8;
                border: 1px solid #1e2330;
                border-radius: 8px;
                padding: 8px;
            }
        """)

    def append_log(self, msg: str, level: str = "info"):
        colors = {
            "info": "#94a3b8",
            "success": "#34d399",
            "error": "#f87171",
            "warn": "#fbbf24",
        }
        color = colors.get(level, "#94a3b8")
        ts = datetime.now().strftime("%H:%M:%S")
        html = f'<span style="color:#4b5563;">[{ts}]</span> <span style="color:{color};">{msg}</span>'
        self.append(html)
        self.moveCursor(QTextCursor.MoveOperation.End)


# ─── Stat Card ────────────────────────────────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, label, value="0", accent="#3b82f6"):
        super().__init__()
        self.accent = accent
        self.setMinimumHeight(72)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #111520;
                border: 1px solid #1e2330;
                border-left: 3px solid {accent};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(2)

        self.val_label = QLabel(value)
        self.val_label.setObjectName("stat_value")
        self.val_label.setFont(QFont(_UI_FONT, 26, QFont.Weight.Bold))
        self.val_label.setStyleSheet(f"color: {accent}; background: transparent; border: none;")

        self.lbl_label = QLabel(label.upper())
        self.lbl_label.setObjectName("stat_label")
        self.lbl_label.setFont(QFont(_UI_FONT, 10))
        self.lbl_label.setStyleSheet("color: #4b5563; background: transparent; border: none; letter-spacing: 1px;")

        lay.addWidget(self.val_label)
        lay.addWidget(self.lbl_label)

    def set_value(self, v):
        self.val_label.setText(str(v))


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.recipients = []
        self.attachments = []
        self.send_worker = None
        self.send_thread = None
        self._sending = False
        self._extra_columns = []
        self._health_worker = None
        self.sidebar = None
        self.sidebar_collapsed = False
        self.theme = self.config.get("ui", {}).get("theme", "dark")

        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(720, 520)
        self.resize(1100, 720)
        self._apply_theme()
        self._restore_window_state()
        self._build_ui()
        self._refresh_smtp_list()
        self._update_stats()

    def _apply_theme(self):
        self.setStyleSheet(DARK_STYLE if self.theme == "dark" else LIGHT_STYLE)

    def _restore_window_state(self):
        ui = self.config.get("ui", {})
        geometry_hex = ui.get("geometry")
        if geometry_hex:
            self.restoreGeometry(QByteArray.fromHex(geometry_hex.encode("ascii")))

    def _save_window_state(self):
        ui = self.config.setdefault("ui", {})
        ui["theme"] = self.theme
        ui["geometry"] = bytes(self.saveGeometry().toHex()).decode("ascii")
        save_config(self.config)

    def closeEvent(self, event):
        self._save_window_state()
        super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_responsive_shell()

    def _update_responsive_shell(self):
        if not self.sidebar:
            return
        compact = self.width() < 820
        if compact and not self.sidebar_collapsed:
            self.sidebar.setVisible(False)
            self.sidebar_collapsed = True
        elif not compact and self.sidebar_collapsed:
            self.sidebar.setVisible(True)
            self.sidebar_collapsed = False

    def _toggle_sidebar(self):
        if self.sidebar:
            self.sidebar_collapsed = self.sidebar.isVisible()
            self.sidebar.setVisible(not self.sidebar.isVisible())

    def _toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.config.setdefault("ui", {})["theme"] = self.theme
        save_config(self.config)
        self._apply_theme()
        self.theme_btn.setText("Dark" if self.theme == "light" else "Light")

    def _scrollable_tab(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(widget)
        return scroll

    def _toolbar_container(self, layout):
        wrap = QWidget()
        wrap.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumHeight(54)
        scroll.setMaximumHeight(68)
        scroll.setWidget(wrap)
        return scroll

    def _build_macos_menu(self):
        from PyQt6.QtGui import QKeySequence
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(True)

        app_menu = menu_bar.addMenu(APP_NAME)
        about_action = QAction(f"About {APP_NAME}", self)
        about_action.triggered.connect(self._show_about)
        app_menu.addAction(about_action)
        app_menu.addSeparator()
        quit_action = QAction(f"Quit {APP_NAME}", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(QApplication.instance().quit)
        app_menu.addAction(quit_action)

        file_menu = menu_bar.addMenu("File")
        import_action = QAction("Import Recipients…", self)
        import_action.setShortcut(QKeySequence("Ctrl+O"))
        import_action.triggered.connect(self._import_recipients)
        file_menu.addAction(import_action)
        export_action = QAction("Export Recipients…", self)
        export_action.setShortcut(QKeySequence("Ctrl+S"))
        export_action.triggered.connect(self._export_recipients)
        file_menu.addAction(export_action)

    def _show_about(self):
        QMessageBox.about(self, f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br><br>"
            "Professional email campaign tool.<br>"
            "Credentials are encrypted and stored locally.")

    def _build_ui(self):
        if _MACOS:
            self._build_macos_menu()
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = self._build_sidebar()
        root.addWidget(self.sidebar)

        # Main content
        content = QWidget()
        content.setStyleSheet("background-color: #0d0f14;")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        # Header
        header = self._build_header()
        content_lay.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        content_lay.addWidget(self.tabs)

        self._build_smtp_tab()
        self._build_compose_tab()
        self._build_recipients_tab()
        self._build_console_tab()

        root.addWidget(content, 1)
        self._update_responsive_shell()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"{APP_NAME} ready  ·  v{APP_VERSION}")

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setMinimumWidth(180)
        sidebar.setMaximumWidth(260)
        sidebar.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #080a0f;
                border-right: 1px solid #1e2330;
            }
        """)
        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo area
        logo_frame = QFrame()
        logo_frame.setMinimumHeight(64)
        logo_frame.setStyleSheet("background-color: #080a0f; border-bottom: 1px solid #1a1f2e;")
        logo_lay = QVBoxLayout(logo_frame)
        logo_lay.setContentsMargins(20, 12, 20, 12)

        app_name = QLabel("MailBlast")
        app_name.setFont(QFont(_UI_FONT, 16, QFont.Weight.Bold))
        app_name.setStyleSheet("color: #3b82f6; background: transparent; letter-spacing: -0.5px;")

        pro_badge = QLabel("PRO")
        pro_badge.setFont(QFont(_UI_FONT, 9, QFont.Weight.Bold))
        pro_badge.setStyleSheet("""
            color: #7c3aed;
            background: #1e1036;
            border-radius: 3px;
            padding: 1px 6px;
            letter-spacing: 1px;
        """)

        name_row = QHBoxLayout()
        name_row.addWidget(app_name)
        name_row.addWidget(pro_badge)
        name_row.addStretch()
        logo_lay.addLayout(name_row)
        lay.addWidget(logo_frame)

        # Stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background: transparent;")
        stats_lay = QVBoxLayout(stats_frame)
        stats_lay.setContentsMargins(16, 16, 16, 8)
        stats_lay.setSpacing(10)

        lbl = QLabel("CAMPAIGN STATS")
        lbl.setFont(QFont(_UI_FONT, 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #2a3347; background: transparent; letter-spacing: 1.5px;")
        stats_lay.addWidget(lbl)

        self.stat_total = StatCard("Recipients", "0", "#3b82f6")
        self.stat_sent = StatCard("Sent", "0", "#10b981")
        self.stat_failed = StatCard("Failed", "0", "#ef4444")
        self.stat_smtp = StatCard("SMTP Accounts", "0", "#8b5cf6")

        for s in [self.stat_total, self.stat_sent, self.stat_failed, self.stat_smtp]:
            stats_lay.addWidget(s)

        lay.addWidget(stats_frame)
        lay.addStretch()

        # Send control
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("background: transparent;")
        ctrl_lay = QVBoxLayout(ctrl_frame)
        ctrl_lay.setContentsMargins(16, 8, 16, 16)
        ctrl_lay.setSpacing(8)

        self.send_btn = QPushButton("▶  START CAMPAIGN")
        self.send_btn.setObjectName("success")
        self.send_btn.setMinimumHeight(42)
        self.send_btn.setFont(QFont(_UI_FONT, 11, QFont.Weight.Bold))
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #059669, stop:1 #0d9488);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #14b8a6);
            }
        """)
        self.send_btn.clicked.connect(self._start_campaign)

        self.stop_btn = QPushButton("■  STOP")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.setMinimumHeight(34)
        self.stop_btn.clicked.connect(self._stop_campaign)
        self.stop_btn.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(8)
        self.progress_bar.setValue(0)

        ctrl_lay.addWidget(self.send_btn)
        ctrl_lay.addWidget(self.stop_btn)
        ctrl_lay.addWidget(self.progress_bar)
        lay.addWidget(ctrl_frame)

        return sidebar

    def _build_header(self):
        header = QFrame()
        header.setMinimumHeight(56)
        header.setStyleSheet("""
            QFrame {
                background-color: #080a0f;
                border-bottom: 1px solid #1a1f2e;
            }
        """)
        lay = QHBoxLayout(header)
        lay.setContentsMargins(16, 8, 16, 8)

        menu_btn = QPushButton("Menu")
        menu_btn.setMaximumWidth(84)
        menu_btn.clicked.connect(self._toggle_sidebar)
        lay.addWidget(menu_btn)

        title = QLabel("Email Campaign Manager")
        title.setFont(QFont(_UI_FONT, 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e8eaf0; background: transparent;")

        subtitle = QLabel(datetime.now().strftime("%A, %B %d %Y"))
        subtitle.setFont(QFont(_UI_FONT, 11))
        subtitle.setStyleSheet("color: #374151; background: transparent;")

        self.theme_btn = QPushButton("Dark" if self.theme == "light" else "Light")
        self.theme_btn.setMaximumWidth(84)
        self.theme_btn.clicked.connect(self._toggle_theme)

        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(subtitle)
        lay.addWidget(self.theme_btn)
        return header

    # ── SMTP Tab ──

    def _build_smtp_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        # Toolbar
        toolbar = QHBoxLayout()
        add_btn = QPushButton("+ Add SMTP Account")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self._add_smtp)

        edit_btn = QPushButton("✎ Edit Selected")
        edit_btn.clicked.connect(self._edit_smtp)

        del_btn = QPushButton("✕ Remove")
        del_btn.setObjectName("danger")
        del_btn.clicked.connect(self._remove_smtp)

        test_btn = QPushButton("⚡ Test Selected")
        test_btn.clicked.connect(self._test_selected_smtp)

        health_btn = QPushButton("🔍 Check All Health")
        health_btn.clicked.connect(self._check_all_smtp)

        select_all_btn = QPushButton("☑️ Select All")
        select_all_btn.clicked.connect(self._select_all_smtp)

        deselect_all_btn = QPushButton("☐ Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all_smtp)

        toolbar.addWidget(add_btn)
        toolbar.addWidget(edit_btn)
        toolbar.addWidget(del_btn)
        toolbar.addWidget(test_btn)
        toolbar.addWidget(health_btn)
        toolbar.addWidget(select_all_btn)
        toolbar.addWidget(deselect_all_btn)
        toolbar.addStretch()

        info = QLabel("💡 Credentials are encrypted and stored locally. Use App Passwords for Gmail/Yahoo.")
        info.setStyleSheet("color: #374151; font-size: 11px; background: transparent;")
        toolbar.addWidget(info)
        lay.addWidget(self._toolbar_container(toolbar))

        # Table
        self.smtp_table = QTableWidget()
        self.smtp_table.setColumnCount(8)
        self.smtp_table.setHorizontalHeaderLabels(["Use", "Name", "Host", "Port", "Username", "SSL", "TLS", "Status"])
        self.smtp_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.smtp_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.smtp_table.setAlternatingRowColors(True)
        self.smtp_table.verticalHeader().setVisible(False)
        lay.addWidget(self.smtp_table)

        # Settings row
        settings_group = QGroupBox("Sending Settings")
        settings_lay = QHBoxLayout(settings_group)

        settings_lay.addWidget(QLabel("Send Interval:"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 3600.0)
        self.interval_spin.setValue(self.config.get("settings", {}).get("delay", 2.0))
        self.interval_spin.setSingleStep(1.0)
        self.interval_spin.setMinimumWidth(90)
        self.interval_unit_combo = QComboBox()
        self.interval_unit_combo.addItems(["seconds", "minutes"])
        self.interval_unit_combo.setMinimumWidth(90)
        interval_hint = QLabel("delay between each email sent")
        interval_hint.setStyleSheet("color: #4b5563; font-size: 11px; background: transparent;")
        settings_lay.addWidget(self.interval_spin)
        settings_lay.addWidget(self.interval_unit_combo)
        settings_lay.addWidget(interval_hint)

        settings_lay.addSpacing(20)

        self.retry_check = QCheckBox("Retry failed emails")
        self.retry_check.setChecked(self.config.get("settings", {}).get("retry", True))
        settings_lay.addWidget(self.retry_check)

        settings_lay.addSpacing(20)
        settings_lay.addWidget(QLabel("SMTP Rotation:"))
        self.rotation_combo = QComboBox()
        self.rotation_combo.addItems(["Round Robin", "Sequential"])
        self.rotation_combo.setMinimumWidth(130)
        settings_lay.addWidget(self.rotation_combo)

        settings_lay.addStretch()

        save_settings_btn = QPushButton("Save Settings")
        save_settings_btn.clicked.connect(self._save_settings)
        settings_lay.addWidget(save_settings_btn)
        lay.addWidget(settings_group)
        tab = self._scrollable_tab(tab)

        self.tabs.addTab(tab, "⚙  SMTP Accounts")

    # ── Compose Tab ──

    def _build_compose_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: fields
        left = QWidget()
        left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(10)

        # Redesigned Message Settings section for better clarity and alignment
        fields_group = QGroupBox("Message Settings")
        fields_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        fields_vbox = QVBoxLayout(fields_group)
        fields_vbox.setSpacing(16)
        fields_vbox.setContentsMargins(16, 16, 16, 16)

        # Subject
        subject_row = QHBoxLayout()
        subject_label = QLabel("Subject:")
        subject_label.setMinimumWidth(110)
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Subject — supports {name}, {email}, {sender_name}")
        self.subject_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        subject_row.addWidget(subject_label)
        subject_row.addWidget(self.subject_edit)
        fields_vbox.addLayout(subject_row)

        # From Account row
        from_row = QHBoxLayout()
        from_label = QLabel("From Account:")
        from_label.setMinimumWidth(110)
        self.from_account_edit = QLineEdit()
        self.from_account_edit.setPlaceholderText("override@yourdomain.com  (leave blank to use SMTP username)")
        self.from_account_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        from_row.addWidget(from_label)
        from_row.addWidget(self.from_account_edit)
        fields_vbox.addLayout(from_row)

        # Reply-To row
        replyto_row = QHBoxLayout()
        replyto_label = QLabel("Reply-To:")
        replyto_label.setMinimumWidth(110)
        self.reply_to_edit = QLineEdit()
        self.reply_to_edit.setPlaceholderText("reply@yourdomain.com")
        self.reply_to_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        replyto_row.addWidget(replyto_label)
        replyto_row.addWidget(self.reply_to_edit)
        fields_vbox.addLayout(replyto_row)

        left_lay.addWidget(fields_group)

        format_row = QHBoxLayout()
        self.html_check = QCheckBox("HTML Email")
        self.html_check.setChecked(True)
        format_row.addWidget(self.html_check)

        preview_btn = QPushButton("👁 Preview")
        preview_btn.clicked.connect(self._show_preview)
        format_row.addWidget(preview_btn)
        format_row.addStretch()

        hint = QLabel("Placeholders: {name}  {email}  {sender_name}  {company}")
        hint.setStyleSheet("color: #374151; font-size: 11px; background: transparent;")
        format_row.addWidget(hint)
        left_lay.addLayout(format_row)

        self.body_edit = QTextEdit()
        self.body_edit.setPlaceholderText(
            "Hello {name},\n\nYour email body here...\n\nBest regards,\n{sender_name}")
        self.body_edit.setMinimumHeight(250)
        self.body_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.body_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        left_lay.addWidget(self.body_edit)

        # Attachments
        att_group = QGroupBox("Attachments")
        att_lay = QHBoxLayout(att_group)
        add_att_btn = QPushButton("+ Add File")
        add_att_btn.clicked.connect(self._add_attachment)
        clear_att_btn = QPushButton("✕ Clear All")
        clear_att_btn.clicked.connect(self._clear_attachments)
        self.att_label = QLabel("No attachments")
        self.att_label.setStyleSheet("color: #4b5563; background: transparent;")
        att_lay.addWidget(add_att_btn)
        att_lay.addWidget(clear_att_btn)
        att_lay.addWidget(self.att_label)
        att_lay.addStretch()
        left_lay.addWidget(att_group)

        splitter.addWidget(left)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([760, 220])

        # Right: quick tips
        right = QWidget()
        right.setMinimumWidth(200)
        right.setMaximumWidth(240)
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(6)

        tips_group = QGroupBox("Tips & Placeholders")
        tips_lay = QVBoxLayout(tips_group)
        tips = QTextEdit()
        tips.setReadOnly(True)
        tips.setStyleSheet("""
            QTextEdit {
                background: #080a0f;
                border: 1px solid #1a1f2e;
                border-radius: 6px;
                color: #4b5563;
                font-size: 12px;
                padding: 8px;
            }
        """)
        tips.setHtml("""
        <style>body{color:#6b7280;font-family:-apple-system,'SF Pro Display','Segoe UI',sans-serif;font-size:12px;}</style>
        <p><b style="color:#3b82f6;">Built-in Placeholders</b></p>
        <p><code style="color:#a78bfa;">{name}</code> — Recipient name</p>
        <p><code style="color:#a78bfa;">{email}</code> — Recipient email</p>
        <p><code style="color:#a78bfa;">{sender_name}</code> — Sender display</p>
        <p><code style="color:#a78bfa;">{company}</code> — Company field</p>
        <br>
        <p><b style="color:#10b981;">Custom Fields</b></p>
        <p>Add extra columns to your CSV and use them as <code style="color:#a78bfa;">{column_name}</code> placeholders automatically.</p>
        <p>e.g. a <i>city</i> column → <code style="color:#a78bfa;">{city}</code></p>
        <br>
        <p><b style="color:#3b82f6;">Best Practices</b></p>
        <p>• Use App Passwords for Gmail</p>
        <p>• Set delay ≥ 2s to avoid rate limits</p>
        <p>• Test SMTP before bulk sending</p>
        <p>• Validate recipients first</p>
        <br>
        <p><b style="color:#3b82f6;">CSV Format</b></p>
        <p>email, name, sender_name, company, [custom...]</p>
        """)
        tips_lay.addWidget(tips)
        right_lay.addWidget(tips_group)

        splitter.addWidget(right)
        lay.addWidget(splitter)
        tab = self._scrollable_tab(tab)

        self.tabs.addTab(tab, "✉  Compose")

    # ── Recipients Tab ──

    def _build_recipients_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        toolbar = QHBoxLayout()
        import_btn = QPushButton("📂 Import CSV/TXT")
        import_btn.setObjectName("primary")
        import_btn.clicked.connect(self._import_recipients)

        validate_btn = QPushButton("✓ Validate Emails")
        validate_btn.clicked.connect(self._validate_recipients)

        export_btn = QPushButton("💾 Export List")
        export_btn.clicked.connect(self._export_recipients)

        clear_btn = QPushButton("✕ Clear All")
        clear_btn.setObjectName("danger")
        clear_btn.clicked.connect(self._clear_recipients)

        add_row_btn = QPushButton("+ Add Row")
        add_row_btn.clicked.connect(self._add_recipient_row)

        remove_row_btn = QPushButton("- Remove Row")
        remove_row_btn.clicked.connect(self._remove_selected_row)

        toolbar.addWidget(import_btn)
        toolbar.addWidget(validate_btn)
        toolbar.addWidget(add_row_btn)
        toolbar.addWidget(remove_row_btn)
        toolbar.addStretch()
        toolbar.addWidget(export_btn)
        toolbar.addWidget(clear_btn)
        lay.addWidget(self._toolbar_container(toolbar))

        self.recipient_count_label = QLabel("0 recipients loaded")
        self.recipient_count_label.setStyleSheet("color: #4b5563; font-size: 12px; background: transparent;")
        lay.addWidget(self.recipient_count_label)

        self.recip_table = QTableWidget()
        self.recip_table.setColumnCount(4)
        self.recip_table.setHorizontalHeaderLabels(["Email", "Name", "Sender Name", "Company"])
        self.recip_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recip_table.setAlternatingRowColors(True)
        self.recip_table.verticalHeader().setVisible(False)
        self.recip_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recip_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.recip_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        lay.addWidget(self.recip_table)

        sample_lbl = QLabel("CSV format: email, name, sender_name, company  (header row optional)")
        sample_lbl.setStyleSheet("color: #374151; font-size: 11px; background: transparent;")
        lay.addWidget(sample_lbl)
        tab = self._scrollable_tab(tab)

        self.tabs.addTab(tab, "👥  Recipients")

    # ── Console Tab ──

    def _build_console_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        toolbar = QHBoxLayout()
        clear_log_btn = QPushButton("🗑 Clear Log")
        clear_log_btn.clicked.connect(lambda: self.log_console.clear())
        export_log_btn = QPushButton("💾 Export Log")
        export_log_btn.clicked.connect(self._export_log)
        toolbar.addWidget(clear_log_btn)
        toolbar.addWidget(export_log_btn)
        toolbar.addStretch()
        lay.addWidget(self._toolbar_container(toolbar))

        self.log_console = LogConsole()
        lay.addWidget(self.log_console)
        tab = self._scrollable_tab(tab)

        self.tabs.addTab(tab, "📋  Send Console")

    # ── SMTP Methods ──

    def _refresh_smtp_list(self):
        accounts = self.config.get("smtp_accounts", [])
        self.smtp_table.setRowCount(len(accounts))

        for i, acc in enumerate(accounts):
            # Checkbox for selection - wrapped in a container widget for proper alignment
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            check = QCheckBox()
            check.setChecked(True)  # Default to selected
            layout.addWidget(check)
            self.smtp_table.setCellWidget(i, 0, container)
            
            self.smtp_table.setItem(i, 1, QTableWidgetItem(acc.get("name", "")))
            self.smtp_table.setItem(i, 2, QTableWidgetItem(acc.get("host", "")))
            self.smtp_table.setItem(i, 3, QTableWidgetItem(str(acc.get("port", ""))))
            self.smtp_table.setItem(i, 4, QTableWidgetItem(acc.get("username", "")))
            self.smtp_table.setItem(i, 5, QTableWidgetItem("Yes" if acc.get("ssl") else "No"))
            self.smtp_table.setItem(i, 6, QTableWidgetItem("Yes" if acc.get("tls") else "No"))
            status_item = QTableWidgetItem("○ Untested")
            status_item.setForeground(QColor("#4b5563"))
            self.smtp_table.setItem(i, 7, status_item)

        self.stat_smtp.set_value(len(accounts))

    def _add_smtp(self):
        dlg = SMTPDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            acc = dlg.get_account()
            self.config.setdefault("smtp_accounts", []).append(acc)
            save_config(self.config)
            self._refresh_smtp_list()

    def _edit_smtp(self):
        row = self.smtp_table.currentRow()
        if row < 0:
            return
        acc = self.config["smtp_accounts"][row]
        dlg = SMTPDialog(self, acc)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.config["smtp_accounts"][row] = dlg.get_account()
            save_config(self.config)
            self._refresh_smtp_list()

    def _remove_smtp(self):
        row = self.smtp_table.currentRow()
        if row < 0:
            return
        self.config["smtp_accounts"].pop(row)
        save_config(self.config)
        self._refresh_smtp_list()

    def _test_selected_smtp(self):
        row = self.smtp_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Account", "Please select an SMTP account to test.")
            return
        acc = self.config["smtp_accounts"][row]
        try:
            host, port = acc["host"], int(acc["port"])
            pwd = decrypt(acc.get("password_enc", ""))
            if acc.get("ssl"):
                ctx = ssl.create_default_context()
                conn = smtplib.SMTP_SSL(host, port, context=ctx, timeout=10)
            else:
                conn = smtplib.SMTP(host, port, timeout=10)
                if acc.get("tls"):
                    conn.starttls()
            conn.login(acc["username"], pwd)
            conn.quit()
            self._set_smtp_status(row, True, "OK")
            QMessageBox.information(self, "Test Passed",
                f"✓ Successfully connected to {host}:{port}")
        except Exception as e:
            self._set_smtp_status(row, False, str(e)[:50])
            QMessageBox.critical(self, "Test Failed", f"✗ {e}")

    def _set_smtp_status(self, row, success, message):
        if success:
            item = QTableWidgetItem("● OK")
            item.setForeground(QColor("#34d399"))
        else:
            item = QTableWidgetItem(f"✗ {message}")
            item.setForeground(QColor("#f87171"))
        self.smtp_table.setItem(row, 7, item)

    def _check_all_smtp(self):
        accounts = self.config.get("smtp_accounts", [])
        if not accounts:
            QMessageBox.information(self, "No Accounts", "No SMTP accounts to check.")
            return
        for i in range(self.smtp_table.rowCount()):
            item = QTableWidgetItem("⟳ Checking...")
            item.setForeground(QColor("#fbbf24"))
            self.smtp_table.setItem(i, 7, item)
        self._health_worker = SmtpHealthWorker(list(enumerate(accounts)))
        self._health_worker.result_signal.connect(self._on_health_result)
        self._health_worker.start()
        self.status_bar.showMessage("Running SMTP health check...")

    def _on_health_result(self, row, success, message):
        self._set_smtp_status(row, success, message)
        # Check if all rows are done
        all_done = all(
            self.smtp_table.item(i, 7) and
            not self.smtp_table.item(i, 7).text().startswith("⟳")
            for i in range(self.smtp_table.rowCount())
        )
        if all_done:
            self.status_bar.showMessage("SMTP health check complete.", 4000)

    def _select_all_smtp(self):
        for i in range(self.smtp_table.rowCount()):
            container = self.smtp_table.cellWidget(i, 0)
            if container:
                for child in container.children():
                    if isinstance(child, QCheckBox):
                        child.setChecked(True)
                        break

    def _deselect_all_smtp(self):
        for i in range(self.smtp_table.rowCount()):
            container = self.smtp_table.cellWidget(i, 0)
            if container:
                for child in container.children():
                    if isinstance(child, QCheckBox):
                        child.setChecked(False)
                        break

    def _save_settings(self):
        interval_secs = self.interval_spin.value()
        if self.interval_unit_combo.currentText() == "minutes":
            interval_secs *= 60
        self.config["settings"] = {
            "delay": interval_secs,
            "retry": self.retry_check.isChecked(),
        }
        save_config(self.config)
        self.status_bar.showMessage("Settings saved.", 3000)

    # ── Recipient Methods ──

    def _import_recipients(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Recipients", "", "CSV/TXT Files (*.csv *.txt);;All Files (*)")
        if not path:
            return
        self.recipients.clear()
        self._extra_columns = []
        base_cols = ["email", "name", "sender_name", "company"]
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = None
            for row in reader:
                if not row:
                    continue
                first = row[0].strip().lower()
                if headers is None:
                    if first in ("email", "e-mail"):
                        headers = [c.strip().lower().replace(" ", "_") for c in row]
                        self._extra_columns = [h for h in headers[4:] if h not in base_cols]
                        continue
                    else:
                        # No header row — use positional defaults
                        headers = base_cols[:]
                        if len(row) > 4:
                            extra = [f"field{i+1}" for i in range(len(row) - 4)]
                            headers += extra
                            self._extra_columns = extra
                recip = {headers[j]: row[j].strip() if j < len(row) else "" for j in range(len(headers))}
                # Ensure base keys exist
                for k in base_cols:
                    recip.setdefault(k, "")
                if not recip.get("email"):
                    continue
                self.recipients.append(recip)
        self._refresh_recip_table()
        self._update_stats()
        self.log_console.append_log(f"Imported {len(self.recipients)} recipients from {Path(path).name}", "info")
        if self._extra_columns:
            self.log_console.append_log(
                f"Custom fields: {', '.join('{' + c + '}' for c in self._extra_columns)}", "info")

    def _refresh_recip_table(self):
        base_cols = ["email", "name", "sender_name", "company"]
        all_cols = base_cols + self._extra_columns
        headers = ["Email", "Name", "Sender Name", "Company"] + [
            c.replace("_", " ").title() for c in self._extra_columns
        ]
        self.recip_table.setColumnCount(len(all_cols))
        self.recip_table.setHorizontalHeaderLabels(headers)
        self.recip_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.recip_table.setRowCount(len(self.recipients))
        for i, r in enumerate(self.recipients):
            for j, key in enumerate(all_cols):
                item = QTableWidgetItem(r.get(key, ""))
                if key == "email" and not is_valid_email(r.get("email", "")):
                    item.setForeground(QColor("#f87171"))
                self.recip_table.setItem(i, j, item)
        self.recipient_count_label.setText(f"{len(self.recipients)} recipients loaded")

    def _add_recipient_row(self):
        new_row = {"email": "", "name": "", "sender_name": "", "company": ""}
        for c in self._extra_columns:
            new_row[c] = ""
        self.recipients.append(new_row)
        self._refresh_recip_table()
        self.recip_table.scrollToBottom()
        self.recip_table.editItem(self.recip_table.item(len(self.recipients)-1, 0))

    def _remove_selected_row(self):
        row = self.recip_table.currentRow()
        if 0 <= row < len(self.recipients):
            self.recipients.pop(row)
            self._refresh_recip_table()
            self._update_stats()

    def _validate_recipients(self):
        invalid = 0
        for r in self.recipients:
            if not is_valid_email(r.get("email", "")):
                invalid += 1
        valid = len(self.recipients) - invalid
        msg = f"Validation: {valid} valid, {invalid} invalid email(s)"
        self.log_console.append_log(msg, "info" if invalid == 0 else "warn")
        self.status_bar.showMessage(msg, 5000)
        self._refresh_recip_table()

    def _clear_recipients(self):
        self.recipients.clear()
        self._refresh_recip_table()
        self._update_stats()

    def _export_recipients(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Recipients", "recipients.csv",
                                               "CSV Files (*.csv)")
        if not path:
            return
        all_cols = ["email", "name", "sender_name", "company"] + self._extra_columns
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self.recipients)
        self.status_bar.showMessage(f"Exported {len(self.recipients)} recipients.", 3000)

    # ── Compose Methods ──

    def _add_attachment(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Attachments")
        if paths:
            self.attachments.extend(paths)
            self.att_label.setText(f"{len(self.attachments)} file(s) attached")

    def _clear_attachments(self):
        self.attachments.clear()
        self.att_label.setText("No attachments")

    def _show_preview(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Email Preview")
        dlg.setMinimumSize(600, 500)
        dlg.setStyleSheet(DARK_STYLE)
        lay = QVBoxLayout(dlg)
        preview = QTextEdit()
        preview.setReadOnly(True)
        body = self.body_edit.toPlainText()
        sample_r = self.recipients[0] if self.recipients else {
            "name": "John Doe", "email": "john@example.com",
            "sender_name": "Support Team", "company": "Acme Corp"
        }
        for k, v in sample_r.items():
            body = body.replace(f"{{{k}}}", v)
        if self.html_check.isChecked():
            preview.setHtml(body)
        else:
            preview.setPlainText(body)
        lay.addWidget(QLabel(f"Subject: {self.subject_edit.text()}"))
        lay.addWidget(preview)
        dlg.exec()

    # ── Campaign ──

    def _start_campaign(self):
        if self._sending:
            return

        smtp_accounts = self.config.get("smtp_accounts", [])
        if not smtp_accounts:
            QMessageBox.warning(self, "No SMTP", "Please add at least one SMTP account first.")
            return

        # Get selected SMTP accounts
        selected_smtp = []
        for i in range(self.smtp_table.rowCount()):
            container = self.smtp_table.cellWidget(i, 0)
            if container:
                # Get checkbox from container
                for child in container.children():
                    if isinstance(child, QCheckBox) and child.isChecked():
                        selected_smtp.append(smtp_accounts[i])
                        break

        if not selected_smtp:
            QMessageBox.warning(self, "No SMTP Selected", "Please select at least one SMTP account to use.")
            return

        # Sync recipients from table (including any custom columns)
        all_cols = ["email", "name", "sender_name", "company"] + self._extra_columns
        for i in range(self.recip_table.rowCount()):
            if i < len(self.recipients):
                for j, key in enumerate(all_cols):
                    item = self.recip_table.item(i, j)
                    if item:
                        self.recipients[i][key] = item.text()

        valid_recips = [r for r in self.recipients if is_valid_email(r.get("email", ""))]
        if not valid_recips:
            QMessageBox.warning(self, "No Recipients",
                "No valid recipients found. Please import or add recipient emails.")
            return

        subject = self.subject_edit.text().strip()
        body = self.body_edit.toPlainText().strip()
        if not subject or not body:
            QMessageBox.warning(self, "Incomplete", "Please fill in Subject and Body.")
            return

        invalid = len(self.recipients) - len(valid_recips)
        if invalid > 0:
            resp = QMessageBox.question(self, "Invalid Emails",
                f"{invalid} invalid email(s) will be skipped. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp != QMessageBox.StandardButton.Yes:
                return

        self._start_campaign_now()

    def _start_campaign_now(self):
        # This is the original campaign start logic
        self._sending = True
        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        valid_recips = [r for r in self.recipients if is_valid_email(r.get("email", ""))]
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(valid_recips))
        self.stat_sent.set_value(0)
        self.stat_failed.set_value(0)

        smtp_accounts = self.config.get("smtp_accounts", [])
        selected_smtp = []
        for i in range(self.smtp_table.rowCount()):
            container = self.smtp_table.cellWidget(i, 0)
            if container:
                for child in container.children():
                    if isinstance(child, QCheckBox) and child.isChecked():
                        selected_smtp.append(smtp_accounts[i])
                        break

        interval_secs = self.interval_spin.value()
        if self.interval_unit_combo.currentText() == "minutes":
            interval_secs *= 60

        self.send_worker = EmailSendWorker(
            recipients=valid_recips,
            smtp_accounts=selected_smtp,
            subject=self.subject_edit.text().strip(),
            body_text=self.body_edit.toPlainText().strip(),
            is_html=self.html_check.isChecked(),
            delay=interval_secs,
            attachments=self.attachments,
            from_account=self.from_account_edit.text().strip(),
            reply_to=self.reply_to_edit.text().strip(),
        )
        self.send_worker.log_signal.connect(self.log_console.append_log)
        self.send_worker.progress_signal.connect(self._on_progress)
        self.send_worker.finished_signal.connect(self._on_finished)
        self.send_worker.status_signal.connect(self.status_bar.showMessage)

        self.send_thread = SendThread(self.send_worker)
        self.send_thread.start()

        self.tabs.setCurrentIndex(3)  # switch to console
        self.log_console.append_log(f"Campaign started: {len(valid_recips)} recipients using {len(selected_smtp)} SMTP account(s)", "info")

    def _stop_campaign(self):
        if self.send_worker:
            self.send_worker.stop()
        self.stop_btn.setEnabled(False)

    def _on_progress(self, sent, total):
        self.progress_bar.setValue(sent)
        self.stat_sent.set_value(sent)
        failed = total - sent - (total - self.progress_bar.maximum()) if total != self.progress_bar.maximum() else 0

    def _on_finished(self, summary):
        self._sending = False
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.stat_sent.set_value(summary["sent"])
        self.stat_failed.set_value(summary["failed"])
        self.progress_bar.setValue(summary["sent"])
        self.status_bar.showMessage(
            f"Campaign complete: {summary['sent']} sent, {summary['failed']} failed")
        QMessageBox.information(self, "Campaign Complete",
            f"✓ Sent: {summary['sent']}\n✗ Failed: {summary['failed']}\nTotal: {summary['total']}")

    def _update_stats(self):
        self.stat_total.set_value(len(self.recipients))
        self.stat_smtp.set_value(len(self.config.get("smtp_accounts", [])))

    # ── Template Methods ──

    def _export_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Log", "campaign_log.txt",
                                               "Text Files (*.txt)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.log_console.toPlainText())
        self.status_bar.showMessage(f"Log exported to {path}", 3000)


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    screen = app.primaryScreen()
    dpi = screen.logicalDotsPerInch() if screen else 96
    base_font_size = 13 if _MACOS else (10 if dpi < 140 else 11)
    app.setFont(QFont(_UI_FONT, base_font_size))

    # Apply palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d0f14"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e8eaf0"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#111520"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0f1118"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e8eaf0"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1e2330"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#94a3b8"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563eb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
