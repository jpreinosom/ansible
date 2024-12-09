import requests
import psycopg2

# Datos de conexión a la base de datos
db_conn = psycopg2.connect(
    host="192.168.100.58",
    database="grafana_db",
    user="grafana_user",
    password="grafana_password"
)
db_cursor = db_conn.cursor()

# Función para obtener las familias
def get_familias():
    query = "SELECT DISTINCT familia FROM inventario"
    db_cursor.execute(query)
    familias = db_cursor.fetchall()
    return [familia[0] for familia in familias]

# Función para obtener las distribuciones por familia
def get_distribuciones(familia):
    query = f"SELECT DISTINCT distribucion FROM inventario WHERE familia = '{familia}'"
    db_cursor.execute(query)
    distribuciones = db_cursor.fetchall()
    return [distribucion[0] for distribucion in distribuciones]

# Función para obtener las versiones por familia y distribución
def get_versiones(familia, distribucion):
    query = f"SELECT DISTINCT version FROM inventario WHERE familia = '{familia}' AND distribucion = '{distribucion}'"
    db_cursor.execute(query)
    versiones = db_cursor.fetchall()
    return [version[0] for version in versiones]

# Función para obtener los detalles de vulnerabilidades por distribución y versión
def get_vulnerabilidades(familia, distribucion, version):
    query = f"""
    SELECT 
        i.ip, 
        i.familia, 
        i.distribucion, 
        i.version,
        COUNT(CASE WHEN vul.categoria = 'high' THEN 1 END) AS high_count,
        COUNT(CASE WHEN vul.categoria = 'medium' THEN 1 END) AS medium_count,
        COUNT(CASE WHEN vul.categoria = 'low' THEN 1 END) AS low_count
    FROM 
        inventario i
    JOIN 
        vulnerabilidades vul ON vul.ip = i.ip
    WHERE 
        i.distribucion = '{distribucion}' 
        AND i.version = '{version}'
    GROUP BY 
        i.ip, i.familia, i.distribucion, i.version;
    """
    db_cursor.execute(query)
    return db_cursor.fetchall()

# Función para descargar el panel de Grafana
def download_panel_image(dashboard_uid, panel_id, familia, distribucion, version, output_filename):
    url = f"http://192.168.100.58:3000/render/d-solo/{dashboard_uid}/my-dashboard"
    params = {
        "orgId": 1,
        "panelId": panel_id,
        "width": 1200,  # Aumentar el ancho de la imagen
        "height": 600,
        "tz": "UTC",
        "var-familia": familia,
        "var-distribucion": distribucion,
        "var-version": version  # Filtro por versión
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"Imagen guardada como '{output_filename}'")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Función para descargar las 4 imágenes adicionales
def download_additional_images():
    additional_urls = [
        {"uid": "ea342cbc-58e6-45dc-b3cf-e12260ff0a87", "panel_id": 3, "name": "Panel_1"},
        {"uid": "ea342cbc-58e6-45dc-b3cf-e12260ff0a87", "panel_id": 4, "name": "Panel_2"},
        {"uid": "ea342cbc-58e6-45dc-b3cf-e12260ff0a87", "panel_id": 5, "name": "Panel_3"},
        {"uid": "ea342cbc-58e6-45dc-b3cf-e12260ff0a87", "panel_id": 6, "name": "Panel_4"}
    ]
    
    for i, panel in enumerate(additional_urls, start=1):
        output_filename = f"grafana_panel_additional_{panel['name']}.png"
        # Llamamos a la función de descarga, pasando los parámetros correspondientes
        download_panel_image(panel['uid'], panel['panel_id'], "", "", "", output_filename)

# Obtener todas las familias
familias = get_familias()

# Paneles que necesitan ser descargados
panels = [
    {"uid": "f866c5f4-9055-42fa-9e52-b5078a3369f2", "panel_id": 5, "name": "Procesadores_por_Familia"},
    {"uid": "f866c5f4-9055-42fa-9e52-b5078a3369f2", "panel_id": 4, "name": "Total_Vulnerabilidades_por_Familia"},
    {"uid": "f866c5f4-9055-42fa-9e52-b5078a3369f2", "panel_id": 3, "name": "Total_Disco_por_Distribucion"},
    {"uid": "f866c5f4-9055-42fa-9e52-b5078a3369f2", "panel_id": 6, "name": "RAM_por_Familia"},
    {"uid": "f866c5f4-9055-42fa-9e52-b5078a3369f2", "panel_id": 1, "name": "Cantidad_de_Maquinas_por_Familia"}
]

# Descargar el gráfico de cantidad de hosts por familia una sola vez
output_filename = "Cantidad_de_Hosts_por_Familia.png"
download_panel_image("ea342cbc-58e6-45dc-b3cf-e12260ff0a87", 2, "", "", "", output_filename)

# Descargar los paneles para cada familia
for familia in familias:
    # Paneles que son solo por familia (sin distribución ni versión)
    for panel in panels:
        output_filename = f"{panel['name']}_{familia}.png"
        download_panel_image(panel['uid'], panel['panel_id'], familia, "", "", output_filename)

    # Descargar los detalles de vulnerabilidades por cada distribución y versión
    distribuciones = get_distribuciones(familia)
    for distribucion in distribuciones:
        versiones = get_versiones(familia, distribucion)
        for version in versiones:
            # Obtener vulnerabilidades por familia, distribución y versión
            vulnerabilidades = get_vulnerabilidades(familia, distribucion, version)

            # Descargar los paneles que dependen de la distribución y versión
            output_filename = f"Detalle_Vulnerabilidades_{familia}_{distribucion}_{version}.png"
            download_panel_image("dcb90785-a2cc-433c-b417-30f9f3d43406", 1, familia, distribucion, version, output_filename)

# Descargar las 4 imágenes adicionales
download_additional_images()

# Cerrar la conexión a la base de datos
db_cursor.close()
db_conn.close()
