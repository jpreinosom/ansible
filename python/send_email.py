# send_email.py
import sys
import smtplib
from email.mime.text import MIMEText
import os
import psycopg2
from psycopg2 import sql
import logging
import time

# Configuración básica del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("send_email.log"),
        logging.StreamHandler()
    ]
)

def send_email(sender, receiver, server, host, days_left):
    subject = f"Alerta: Certificado SSL próximo a expirar en {host}"
    body = f"El certificado SSL del host {host} vence en {days_left} días."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    try:
        server.sendmail(sender, receiver, msg.as_string())
        logging.info(f"Correo enviado para {host}")
    except Exception as e:
        logging.error(f"Error al enviar correo para {host}: {e}")

def fetch_certificates(db_host, db_port, db_name, db_user, db_password):
    try:
        with psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        ) as conn:
            with conn.cursor() as cursor:
                query = sql.SQL("SELECT host, restantes FROM certificado")
                cursor.execute(query)
                records = cursor.fetchall()
        return records
    except Exception as e:
        logging.error(f"Error al conectar o consultar la base de datos: {e}")
        sys.exit(1)

def main():
    # Obtener credenciales SMTP desde variables de entorno
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not smtp_user or not smtp_password:
        logging.error("Las variables de entorno SMTP_USER y SMTP_PASSWORD deben estar definidas.")
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
        logging.info("No se encontraron certificados en la base de datos.")
        sys.exit(0)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.set_debuglevel(0)  # Cambiar a 1 para depuración
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            for record in certificates:
                host, restantes = record
                try:
                    restantes = int(restantes)
                except ValueError:
                    logging.error(f"'restantes' para el host {host} no es un número válido.")
                    continue

                send_email(sender, receiver, server, host, restantes)
                time.sleep(1)  # Evita enviar correos demasiado rápido
    except Exception as e:
        logging.error(f"Error al conectar o autenticar con el servidor SMTP: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
