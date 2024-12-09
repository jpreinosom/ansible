import psycopg2
import json

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    host="192.168.100.58",
    database="grafana_db",
    user="grafana_user",
    password="grafana_password"
)
cursor = conn.cursor()

# Consulta SQL
query = '''
select  d.id_vulnerabilidad,
        d.explicacion,
        d.importancia, 
        d.impacto,
        d.riesgo,
        d.ejemplo , 
        vul.categoria,
        count(vul.ip) as cantidad
from vulnerabilidades vul, detalle_vulnerabilidades d
where vul.detalle = d.id_vulnerabilidad
group by  d.id_vulnerabilidad,
          d.explicacion,
          d.importancia, 
          d.impacto,
          d.riesgo,
          d.ejemplo ,
          vul.categoria;
'''

# Ejecutar consulta
cursor.execute(query)
result = cursor.fetchall()

# Organizar los resultados en un formato estructurado
vulnerabilities = []
for row in result:
    vulnerabilities.append({
        'id_vulnerabilidad': row[0],
        'explicacion': row[1],
        'importancia': row[2],
        'impacto': row[3],
        'riesgo': row[4],
        'ejemplo': row[5],
        'categoria': row[6],
        'cantidad': row[7]
    })

# Cerrar la conexión a la base de datos
conn.close()

# Función para generar el reporte en ASCII Doctor
def generate_ascii_report(vulnerabilities, category):
    report = f"= Vulnerabilidades {category.capitalize()} =\n\n"
    
    for vuln in vulnerabilities:
        # Explicaciones detalladas de la vulnerabilidad
        report += f"=== Vulnerabilidad ID {vuln['id_vulnerabilidad']}\n\n"
        
        # Generar explicaciones dinámicamente desde la base de datos
        report += f"1. **Explicación de la regla:**\n"
        report += f"{vuln['explicacion']}\n\n"
        
        report += f"2. **Por qué es importante no pasar por alto esta regla:**\n"
        report += f"{vuln['importancia']}\n\n"  # Toma la importancia de la base de datos
        
        report += f"3. **Impacto:**\n"
        report += f"{vuln['impacto']}\n\n"  # Toma el impacto de la base de datos
        
        report += f"4. **Riesgo al que estás expuesto:**\n"
        report += f"{vuln['riesgo']}\n\n"  # Toma el riesgo de la base de datos
        
        report += f"5. **Ejemplo real:**\n"
        report += f"{vuln['ejemplo']}\n\n"  # Toma el ejemplo real de la base de datos
    
    return report

# Clasificar vulnerabilidades por categoría
high_vulnerabilities = [v for v in vulnerabilities if v['categoria'] == 'high']
medium_vulnerabilities = [v for v in vulnerabilities if v['categoria'] == 'medium']
low_vulnerabilities = [v for v in vulnerabilities if v['categoria'] == 'low']

# Generar reportes para cada categoría
high_report = generate_ascii_report(high_vulnerabilities, 'high')
medium_report = generate_ascii_report(medium_vulnerabilities, 'medium')
low_report = generate_ascii_report(low_vulnerabilities, 'low')

# Guardar el reporte en archivos ASCII Doctor
with open('high_vulnerabilities.adoc', 'w') as f:
    f.write(high_report)

with open('medium_vulnerabilities.adoc', 'w') as f:
    f.write(medium_report)

with open('low_vulnerabilities.adoc', 'w') as f:
    f.write(low_report)

