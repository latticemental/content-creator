"""This library has been created using DeepSeek"""
import requests
import os
import yaml
from datetime import datetime
import time
import logging

class VideoDownloader:
    def __init__(self, debug=False):
        # Ruta del archivo de configuración
        self.CONFIG_FILE = "conf.yaml"

        # Cargar configuración desde el archivo YAML
        self.config = self._cargar_configuracion()

        # Configuración de la API de Pexels
        self.PEXELS_API_KEY = "DUNrGJqWjM9I8wB96TUuptinnPijrINcyTcg98SxXUr30LNow5X1Mbmh"  # Reemplaza con tu API Key

        # Obtener la carpeta principal de videos desde la configuración
        self.CARPETA_PRINCIPAL = self.config.get("VideoDownloader", {}).get("carpeta_videos", "local_videos")

        # Obtener la carpeta de logs desde la configuración
        self.CARPETA_LOGS = self.config.get("VideoDownloader", {}).get("carpeta_logs", "logs")

        # Crear la carpeta de logs si no existe
        if not os.path.exists(self.CARPETA_LOGS):
            os.makedirs(self.CARPETA_LOGS)

        # Configurar logging
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Crear un formateador para los mensajes de log
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Crear un manejador para guardar los logs en un archivo
        log_filename = f"{datetime.now().strftime('%Y%m%d')}_VideoDownloader.log"
        log_ruta_completa = os.path.join(self.CARPETA_LOGS, log_filename)  # Ruta completa del archivo de log
        file_handler = logging.FileHandler(log_ruta_completa)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

        # Si debug=True, mostrar los logs DEBUG en la consola
        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(console_handler)

        # Crear la carpeta principal si no existe
        if not os.path.exists(self.CARPETA_PRINCIPAL):
            os.makedirs(self.CARPETA_PRINCIPAL)

        # Inicializar el archivo de metadatos si no existe
        self.METADATA_FILE = os.path.join(self.CARPETA_PRINCIPAL, "metadatos.yaml")
        if not os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "w") as f:
                yaml.dump([], f)

    def _cargar_configuracion(self):
        """Carga la configuración desde el archivo conf.yaml."""
        if not os.path.exists(self.CONFIG_FILE):
            self.logger.warning(f"⚠️ El archivo de configuración '{self.CONFIG_FILE}' no existe. Usando valores por defecto.")
            return {}

        with open(self.CONFIG_FILE, "r") as f:
            try:
                config = yaml.safe_load(f)
                if not config:
                    self.logger.warning("⚠️ El archivo de configuración está vacío. Usando valores por defecto.")
                    return {}

                # Convertir la lista de configuraciones en un diccionario
                config_dict = {}
                for item in config:
                    if isinstance(item, dict):
                        config_dict.update(item)
                return config_dict

            except yaml.YAMLError as e:
                self.logger.error(f"❌ Error al leer el archivo de configuración: {e}")
                return {}

    def query(self, name, count):
        """Busca y descarga videos basados en la query y el número de videos especificado."""
        start_time = time.time()  # Iniciar el temporizador

        self.QUERY = name
        self.NUM_VIDEOS = count

        # Lista para almacenar las rutas completas de los videos descargados
        rutas_videos = []

        # Contador de videos descargados
        videos_descargados = 0

        # Cargar metadatos existentes
        with open(self.METADATA_FILE, "r") as f:
            metadatos = yaml.safe_load(f) or []

        # Página inicial para la búsqueda en la API
        pagina_actual = 1
        intentos_fallidos = 0

        # Continuar buscando hasta alcanzar el número de videos solicitados o hasta 5 intentos fallidos
        while videos_descargados < count and intentos_fallidos < 5:
            try:
                # Buscar videos en la página actual
                videos = self._buscar_videos(pagina=pagina_actual)
                if not videos:
                    self.logger.warning(f"⚠️ No se encontraron más videos en la página {pagina_actual}.")
                    intentos_fallidos += 1
                    pagina_actual += 1
                    continue  # Pasar a la siguiente página

                # Procesar cada video
                for video in videos:
                    if videos_descargados >= count:
                        break  # Salir si ya se alcanzó el número de videos solicitados

                    video_id = video["id"]

                    # Verificar si el video ya existe en los metadatos
                    video_existente = next((v for v in metadatos if v["id"] == video_id), None)
                    if video_existente:
                        # Si el video ya existe, devolver su ruta absoluta
                        ruta_carpeta = self._crear_carpeta(self.QUERY)
                        ruta_video = os.path.join(ruta_carpeta, video_existente["nombre_archivo"])
                        if os.path.exists(ruta_video):
                            rutas_videos.append(os.path.abspath(ruta_video))
                            videos_descargados += 1
                            self.logger.debug(f"✅ Video reutilizado: {ruta_video}")
                            continue  # Saltar este video

                    # Si el video no existe, descargarlo y procesarlo
                    ruta_video = self._procesar_video(video)
                    if ruta_video:
                        rutas_videos.append(ruta_video)
                        videos_descargados += 1
                        intentos_fallidos = 0  # Reiniciar el contador de intentos fallidos

                # Pasar a la siguiente página
                pagina_actual += 1

                # Esperar 1 segundo entre solicitudes para evitar el error 429
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ Error en la solicitud a la API: {e}")
                intentos_fallidos += 1
                time.sleep(5)  # Esperar 5 segundos antes de reintentar

        # Calcular y mostrar el tiempo total tomado
        end_time = time.time()
        tiempo_total = end_time - start_time
        self.logger.info(f"⏱️ Tiempo total para completar la función: {tiempo_total:.2f} segundos")

        # Devolver la lista de rutas de videos descargados
        return rutas_videos

    def _crear_carpeta(self, query):
        """Crea una carpeta para la query si no existe."""
        ruta_carpeta = os.path.join(self.CARPETA_PRINCIPAL, query)
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)
            self.logger.debug(f"📁 Carpeta creada: {ruta_carpeta}")
        return ruta_carpeta

    def _buscar_videos(self, pagina=1):
        """Busca videos en Pexels basados en la query y la página especificada."""
        url = f"https://api.pexels.com/videos/search?query={self.QUERY}&per_page={self.NUM_VIDEOS}&page={pagina}"
        headers = {"Authorization": self.PEXELS_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get("videos", [])
        else:
            self.logger.error(f"Error al obtener videos: {response.text}")
            return []

    def _descargar_video(self, url, query, nombre_archivo):
        """Descarga un video y lo guarda en la carpeta correspondiente."""
        ruta_carpeta = self._crear_carpeta(query)
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
        
        # Verificar si el video ya existe en la carpeta
        if os.path.exists(ruta_completa):
            self.logger.debug(f"✅ El video '{nombre_archivo}' ya existe en la carpeta '{ruta_carpeta}'. No se descargará nuevamente.")
            return os.path.abspath(ruta_completa)  # Devuelve la ruta absoluta del video existente
        
        # Descargar el video si no existe
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(ruta_completa, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            self.logger.info(f"✅ Video guardado: {ruta_completa}")
            return os.path.abspath(ruta_completa)  # Devuelve la ruta absoluta del video descargado
        else:
            self.logger.error(f"❌ Error al descargar: {url}")
            return None  # Indica que hubo un error

    def _generar_nombre_archivo(self, video_id, query, video_url):
        """Genera el nombre del archivo en el formato especificado."""
        # Obtener la fecha y hora actual en el formato YYYYMMDD_HHMMSS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Reemplazar espacios en la query por guiones bajos
        query_formateada = query.replace(" ", "_")
        
        # Obtener la extensión del archivo desde la URL del video
        extension = video_url.split(".")[-1].split("?")[0]  # Ejemplo: "mp4"
        
        # Crear el nombre del archivo
        nombre_archivo = f"{timestamp}_{video_id}_{query_formateada}.{extension}"
        return nombre_archivo

    def _guardar_metadatos(self, video_info):
        """Guarda los metadatos del video en el archivo YAML."""
        with open(self.METADATA_FILE, "r") as f:
            metadatos = yaml.safe_load(f) or []

        # Agregar los nuevos metadatos
        metadatos.append(video_info)

        # Guardar los metadatos actualizados en YAML
        with open(self.METADATA_FILE, "w") as f:
            yaml.dump(metadatos, f, default_flow_style=False)
        self.logger.info(f"✅ Metadatos actualizados en: {self.METADATA_FILE}")

    def _procesar_video(self, video):
        """Procesa un video: descarga, verifica duplicados y guarda metadatos."""
        video_id = video["id"]
        video_url = video["video_files"][0]["link"]  # Calidad más baja para rapidez
        
        # Generar el nombre del archivo
        nombre_archivo = self._generar_nombre_archivo(video_id, self.QUERY, video_url)
        
        # Descargar el video
        ruta_video = self._descargar_video(video_url, self.QUERY, nombre_archivo)
        if ruta_video:
            # Guardar metadatos del video
            video_info = {
                "id": video_id,
                "query_name": self.QUERY,  # Agregar el campo query_name
                "nombre_archivo": nombre_archivo,
                "url": video_url,
                "fecha_descarga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Fecha actual
            }
            self._guardar_metadatos(video_info)
            return ruta_video  # Devuelve la ruta absoluta del video descargado
        
        return None  # Si no se descargó el video, devuelve None

# Ejemplo de uso
if __name__ == "__main__":
    video_downloader = VideoDownloader(debug=True)
    queries = ["space", "stars", "food", "healthy", "safety"]
    for query in queries:
        rutas_videos = video_downloader.query(name=query, count=5)
        print(f"📂 Videos relacionados con '{query}': {rutas_videos}")