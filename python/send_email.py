# send_email.py
import sys
import smtplib
from email.mime.text import MIMEText
import os
import psycopg2
from psycopg2 import sql

def send_email(sender, receiver, smtp_server, smtp_port, smtp_user, smtp_password, host, days_left):
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

def fetch_certificates(db_host, db_port, db_name, db_user, db_password):
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        query = sql.SQL("SELECT host, days_left FROM certificado")
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        sys.exit(1)

def main():
    # Obtener credenciales SMTP desde variables de entorno
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_user or not smtp_password:
        print("Error: Las variables de entorno SMTP_USER y SMTP_PASSWORD deben estar definidas.")
        sys.exit(1)

    sender = 'juanpablo@betel-tech.cl'
    receiver = 'jpreinosom@gmail.com'
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Obtener credenciales de la base de datos desde variables de entorno
    db_host = os.getenv('DB_HOST', '192.168.100.58')  # Host de la base de datos
    db_port = os.getenv('DB_PORT', '5432')       # Puerto de la base de datos
    db_name = os.getenv('DB_NAME', 'grafana_db') # Nombre de la base de datos
    db_user = os.getenv('DB_USER', 'grafana_user')     # Usuario de la base de datos
    db_password = os.getenv('DB_PASSWORD', 'grafana_password') # Contraseña de la base de datos

    # Fetch certificates from the database
    certificates = fetch_certificates(db_host, db_port, db_name, db_user, db_password)

    if not certificates:
        print("No se encontraron certificados en la base de datos.")
        sys.exit(0)

    for record in certificates:
        host, days_left = record
        try:
            days_left = int(days_left)
        except ValueError:
            print(f"Error: 'days_left' para el host {host} no es un número válido.")
            continue

        send_email(sender, receiver, smtp_server, smtp_port, smtp_user, smtp_password, host, days_left)

if __name__ == "__main__":
    main()
