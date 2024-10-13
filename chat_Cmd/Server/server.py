import socket
import threading
import sys
import os
import pickle

class Servidor():

    def __init__(self, host="localhost", port=7000):
        self.files_dir = os.path.join(os.getcwd(), 'Files')

        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)

        self.clientes = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((str(host), int(port)))
        self.sock.listen(10)
        self.sock.setblocking(False)

        aceptar = threading.Thread(target=self.aceptarCon)
        procesar = threading.Thread(target=self.procesarCon)

        aceptar.daemon = True
        aceptar.start()

        procesar.daemon = True
        procesar.start()

        try:
            while True:
                msg = input('-> ')
                if msg == 'salir':
                    self.sock.close()
                    sys.exit()
        except:
            self.sock.close()
            sys.exit()

    def msg_to_all(self, msg, cliente):
        for c in self.clientes:
            try:
                if c != cliente:
                    c.send(msg)
            except:
                self.clientes.remove(c)

    def aceptarCon(self):
        print("Aceptando conexiones...")
        while True:
            try:
                conn, addr = self.sock.accept()
                conn.setblocking(False)
                self.clientes.append(conn)
            except:
                pass

    def procesarCon(self):
        print("Procesando conexiones...")
        while True:
            if len(self.clientes) > 0:
                for c in self.clientes:
                    try:
                        data = c.recv(4096)
                        if data:
                            data = pickle.loads(data)

                            if data.get("type") == "list_files":
                                self.send_file_list(c)

                            elif data.get("type") == "get_file":
                                filename = data["filename"]
                                self.send_file(c, filename)

                            else:
                                self.msg_to_all(pickle.dumps(data), c)
                    except:
                        pass

    def send_file_list(self, client):
        try:
            files = os.listdir(self.files_dir)
            client.send(pickle.dumps({"type": "file_list", "files": files}))
        except Exception as e:
            print(f"Error al enviar la lista de archivos: {e}")

    def send_file(self, client, filename):
        try:
            filepath = os.path.join(self.files_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    filedata = f.read()

                data = {
                    "type": "file",
                    "filename": filename,
                    "filedata": filedata
                }
                client.send(pickle.dumps(data))
                print(f"Archivo '{filename}' enviado al cliente.")
            else:
                client.send(pickle.dumps({"type": "error", "message": f"Archivo '{filename}' no encontrado."}))
        except Exception as e:
            print(f"Error al enviar el archivo '{filename}': {e}")

server = Servidor()
