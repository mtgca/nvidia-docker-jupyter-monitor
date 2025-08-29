import docker
from dotenv import load_dotenv
import os
from NotionAutoUpdateBot import create_page, token_update, delete_page, search_page, port_update
from model import Container_info
import regex
from time import sleep

load_dotenv(".env")
host = os.getenv("Host")
if host == None:
    raise EnvironmentError('Enviroment variable "Host" does not exists')

Client = docker.from_env()

# Caché para contenedores que pasen por 'die'
containers_cache = {}

def recovery_double_token(container_name):
    print(f"🔧 Iniciando sistema de recuperación para {container_name}")
    try:
        container = Client.containers.get(container_name)
        container.exec_run("bash -c 'cd ~/.local/share/jupyter && rm -rf runtime'")
        container.restart()
        sleep(5)
        container_restarted = Client.containers.get(container_name)
        result = container_restarted.exec_run("jupyter notebook list")
        res = regex.split("=", result.output.decode())
        if len(res) > 2:
            print(f"⚠️ Aún hay problema de doble token después de la recuperación")
            return ""
        else:
            print(f"✅ Recuperación exitosa para {container_name}")
            return res[1][:-5]
    except Exception as e:
        print(f"❌ Error durante la recuperación en {container_name}: {e}")
        return ""

def get_jtoken(container_name):
    try:
        container = Client.containers.get(container_name)
        sleep(3)
        result = container.exec_run("jupyter notebook list")
        res = regex.split("=", result.output.decode())
        if len(res) > 2:
            print(f"⚠️ Detectado problema de doble token en {container_name}")
            return "RECOVERY_NEEDED"
        return res[1][:-5]
    except Exception as e:
        print(f"⚠️ Error ejecutando en {container_name}: {e}")
        return ""

print("Escuchando eventos de Docker...")

def main_loop():
    for event in Client.events(decode=True):
        if event.get("Type") != "container":
            continue

        action = event.get("Action")
        container_id = event["id"]

        # Verificar si el contenedor empieza con "colab"
        try:
            container = Client.containers.get(container_id)
            container_name = container.name
            if not container_name.startswith("colab"):
                continue  # Ignorar contenedores que no empiecen con "colab"
        except docker.errors.NotFound:
            # Para eventos como destroy, el contenedor puede no existir
            # Verificar en caché si tenemos info previa
            if container_id in containers_cache:
                cached_name = containers_cache[container_id]["Name"].lstrip("/")
                if not cached_name.startswith("colab"):
                    continue
                print(f"📋 Procesando contenedor colab desde caché: {cached_name}")
            else:
                continue

        # Manejo de create/start para guardar en caché
        if action in ["create", "start"]:
            try:
                container = Client.containers.get(container_id)
                containers_cache[container_id] = container.attrs
            except docker.errors.NotFound:
                print(f"⚠️ Contenedor {container_id[:12]} no encontrado al crear/iniciar.")
                continue

        # Guardar info desde el caché si existe
        info = containers_cache.get(container_id)
        if not info:
            if action == "destroy":
                print(f"⚠️ Contenedor {container_id[:12]} destruido sin info previa")
            continue

        # Obtener contenedor actual si existe
        container = None
        if action in ["create", "start", "restart"]:
            try:
                container = Client.containers.get(container_id)
            except docker.errors.NotFound:
                print(f"⚠️ Contenedor {container_id[:12]} no existe al intentar acceder")
        
        # Extraer puerto
        port = 0
        if container:
            # Para create, esperar un poco y recargar attrs
            if action == "create":
                sleep(3)
                container.reload()
            ports = container.attrs["NetworkSettings"]["Ports"]
            if "8080/tcp" in ports and ports["8080/tcp"]:
                port = int(ports["8080/tcp"][0]["HostPort"])

        # Obtener token
        jtoken = ""
        if container and action in ["create", "start", "restart"]:
            jtoken = get_jtoken(container.name)
            if jtoken == "RECOVERY_NEEDED":
                jtoken = recovery_double_token(container.name)

        c_info = Container_info(
            page_id="",
            Container_ID=container_id[:12],
            Name_Container=info["Name"].lstrip("/"),
            Port=port,
            Token_J=jtoken,
            Host=host
        )

        try:
            if action == "create":
                print("Created")
                create_page(c_info)

            elif action == "restart":
                print("Restarted")
                c_info.page_id = search_page(c_info.Name_Container, host)
                try:
                    token_update(jtoken, c_info.page_id)
                    port_update(c_info.Port, c_info.page_id)
                except:
                    create_page(c_info)

            elif action == "die":
                print("Container died, info guardada en caché.")

            elif action == "destroy":
                print("Destroyed")
                c_info.page_id = search_page(c_info.Name_Container, host)
                delete_page(c_info.page_id)
                containers_cache.pop(container_id, None)

        except Exception as e:
            print(f"⚠️ Error en acción {action}: {e}")
            raise RuntimeError(f"Error enviando a Notion: {e}")
            continue

def main():
    main_loop()

if __name__ == "__main__":
    main()
