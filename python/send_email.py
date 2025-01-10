import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuración de correo
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "juanpablo@betel-tech.cl"
smtp_password = "cohjocamjhnymopm"

to_email = "jpreinosom@gmail.com"
from_email = "juanpablo@betel-tech.cl"
subject = "¡Atención! El certificado SSL de SERVER está a punto de expirar"
body = f"""
El certificado SSL en el servidor SERVER expira en X días (Expira el: ExpirationDate).
Por favor, solicite un nuevo certificado lo antes posible.
"""

# Crear el mensaje
message = MIMEMultipart()
message['From'] = from_email
message['To'] = to_email
message['Subject'] = subject
message.attach(MIMEText(body, 'plain'))

# Enviar el correo
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(from_email, to_email, message.as_string())
    server.quit()
    print("Correo enviado con éxito")
except Exception as e:
    print(f"Error al enviar el correo: {e}")
