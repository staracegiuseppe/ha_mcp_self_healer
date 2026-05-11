import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import Settings
from .models import HealingReport


class EmailNotifier:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_report(self, report: HealingReport) -> bool:
        if not self.settings.email_enabled:
            return False
        sender = self.settings.email_from or self.settings.smtp_user
        recipient = self.settings.email_to
        if not sender or not recipient:
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[HA Self Healer] {len(report.issues)} errore/i, {len(report.actions)} azione/i"
        msg["From"] = sender
        msg["To"] = recipient
        html = self._html(report)
        text = self._text(report)
        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        if self.settings.smtp_tls:
            smtp = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20)
            smtp.ehlo()
            smtp.starttls()
        else:
            smtp = smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port, timeout=20)
        try:
            smtp.login(self.settings.smtp_user, self.settings.smtp_password)
            smtp.sendmail(sender, [recipient], msg.as_string())
            return True
        finally:
            smtp.quit()

    def _text(self, report: HealingReport) -> str:
        lines = [report.summary, ""]
        for issue in report.issues:
            lines.append(f"- {issue.severity.upper()} {issue.source}: {issue.message}")
        lines.append("")
        for result in report.actions:
            lines.append(f"- {result.status.upper()} {result.action.title}: {result.detail or result.action.reason}")
        return "\n".join(lines)

    def _html(self, report: HealingReport) -> str:
        issues = "".join(
            f"<li><b>{issue.severity.upper()}</b> <code>{issue.source}</code><br>{_esc(issue.message)}</li>"
            for issue in report.issues
        )
        actions = "".join(
            f"<li><b>{result.status.upper()}</b> {result.action.title}<br><small>{_esc(result.detail or result.action.reason)}</small></li>"
            for result in report.actions
        )
        return f"""
        <html>
          <body style="font-family:Arial,sans-serif;color:#172033">
            <h2>Home Assistant MCP Self Healer</h2>
            <p>{_esc(report.summary)}</p>
            <h3>Errori rilevati</h3>
            <ul>{issues or "<li>Nessun errore nuovo.</li>"}</ul>
            <h3>Azioni</h3>
            <ul>{actions or "<li>Nessuna azione eseguita.</li>"}</ul>
          </body>
        </html>
        """


def _esc(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
