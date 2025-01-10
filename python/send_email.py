# send_email.py
import sys
import smtplib
from email.mime.text import MIMEText

def send_email(host, days_left):
    sender = 'tu_email@example.com'
    receiver = 'destinatario@example.com'
    subject = f"Alerta: Certificado SSL próximo a expirar en {host}"
    body = f"El certificado SSL del host {host} vence en {days_left} días."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:
        with smtplib.SMTP('smtp.example.com') as server:
            server.login('usuario', 'contraseña')
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
