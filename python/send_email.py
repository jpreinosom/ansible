# send_email.py
import sys
import smtplib
from email.mime.text import MIMEText
import os

def send_email(host, days_left):
    sender = 'juanpablo@betel-tech.cl'
    receiver = 'jpreinosom@gmail.com'
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = os.getenv('SMTP_USER')          # Obtén desde variable de entorno
    smtp_password = os.getenv('SMTP_PASSWORD')  # Obtén desde variable de entorno

    subject = f"Alerta: Certificado SSL próximo a expirar en {host}"
    body = f"El certificado SSL del host {host} vence en {days_left} días."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()            # Identificarse con el servidor
            server.starttls()        # Iniciar TLS
            server.ehlo()            # Reidentificarse después de iniciar TLS
            server.login(smtp_user, smtp_password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"Correo enviado para {host}")
    except Exception as e:
        print(f"Error al enviar correo para {host}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: send_email.py <host> <days_left>")
        sys.exit(1)
    host = sys.argv[1]
    days_left = sys.argv[2]
    send_email(host, days_left)

