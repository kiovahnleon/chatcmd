import socket
import threading
import sys
import pickle
import os

class Cliente():

    def __init__(self, host="localhost", port=7000):

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((str(host), int(port)))

            msg_recv = threading.Thread(target=self.msg_recv)
            msg_recv.daemon = True
            msg_recv.start()

            while True:
                msg = input('-> ')

                if msg == 'lsFiles':
                    self.request_file_list()

                elif msg.startswith("get"):
                    filename = msg.split(" ", 1)[1]
                    self.request_file(filename)

                elif msg != 'salir':
                    self.send_msg(msg)

                else:
                    self.sock.close()
                    sys.exit()

        except:
            print("Error al conectar el socket")

    def msg_recv(self):
        while True:
            try:
                data = self.sock.recv(4096)
                if data:
                    data = pickle.loads(data)

                    if data.get("type") == "file_list":
                        print("Archivos en el servidor: \nget <nombreArchivo> para bajar el archivo deseado")
                        for f in data["files"]:
                            print(f)

                    elif data.get("type") == "file":
                        self.save_file(data["filename"], data["filedata"])

                    elif data.get("type") == "error":
                        print(data["message"])

                    else:
                        print(data)
            except:
                pass

    def send_msg(self, msg):
        try:
            self.sock.send(pickle.dumps({"type": "message", "data": msg}))
        except:
            print('Error al enviar el mensaje')

    def request_file_list(self):
        try:
            self.sock.send(pickle.dumps({"type": "list_files"}))
        except:
            print("Error al solicitar la lista de archivos")

    def request_file(self, filename):
        try:
            self.sock.send(pickle.dumps({"type": "get_file", "filename": filename}))
        except:
            print(f"Error al solicitar el archivo '{filename}'")

    def save_file(self, filename, filedata):
        try:
            filepath = os.path.join('downloads', filename)
            with open(filepath, "wb") as f:
                f.write(filedata)
            print(f"Archivo '{filename}' guardado en la carpeta 'downloads'.")
        except:
            print('Error al guardar el archivo.')

cliente = Cliente()
