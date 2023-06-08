import sys
from socket import *
import threading
import shutil

WIDTH = shutil.get_terminal_size().columns


class Cliente:  # Classe que representa un client qualsevol del xat multicanal.
    nom_usuari = ""

    def __init__(self, serverName, serverPort):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        print("\033[0m\033[1mConnexió Exitosa Amb El Xat Multicanal.\033[0m\033[0m")

        self.nom_usuari = input("\033[92m\033[1m▶ Ingresa nom d'usuari:\033[0m\033[0m ")
        clientSocket.send(self.nom_usuari.encode())

        Aux = threading.Thread(
            target=self.envia_missatge, args=(clientSocket, ))
        Aux.daemon = True
        Aux.start()
        # Procés auxiliar que ens permet dur a terme un bucle infinit que estigui continuament rebent
        # missatges de la resta de clients mentre que tenim un altre bucle infinit que envia els seus
        # missatges al servidor.
        self.guia_comandas(self.nom_usuari)
        # self.menu_comandas()
        while True:
            modifiedSentence = clientSocket.recv(1024)
            print(modifiedSentence.decode())

    def guia_comandas(self, nom_usuari):
        print("\n\033[92m\033[1mBon Dia \033[0m\033[1m" + nom_usuari +
              "\033[92m\033[1m. Benvingut A \033[0m\033[1m DISCARD\033[92m\033[1m, El Nostre Xat Multicanal.\033[92m\033[1m\nEsperem Que Disfrutis La Teva Estancia Aqui.\033[0m\033[0m")
        print()
        print("██████╗ ██╗███████╗ ██████╗ █████╗ ██████╗ ██████╗ ".center(WIDTH))
        print("██╔══██╗██║██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗".center(WIDTH))
        print("██║  ██║██║███████╗██║     ███████║██████╔╝██║  ██║".center(WIDTH))
        print("██║  ██║██║╚════██║██║     ██╔══██║██╔══██╗██║  ██║".center(WIDTH))
        print("██████╔╝██║███████║╚██████╗██║  ██║██║  ██║██████╔╝".center(WIDTH))
        print("╚═════╝ ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ".center(WIDTH))

        print("═══════════════════════════════════════════════════".center(WIDTH))

    # Mètode per enviar missatges al servidor. El server els gestiona i els envia a tots els clients connectats.
    def envia_missatge(self, clientSocket):
        while True:
            sentence = input('')
            clientSocket.send(sentence.encode())


if __name__ == '__main__':

    serverPort = 5000
    # Posar la ip del dispositiu on s'ha iniciat el servidor. Per defecte tenim 'localhost' i port 5000.
    serverName = '192.168.61.243'

    while True:
        # Bucle que intenta crear un client si el servidor està actiu, si no és el cas,
        # mostra un missatge d'error indicant-ho.
        print("\033[0m\033[1mIntentando Conectar al Xat Multicanal....\033[0m\033[0m")
        try:
            cliente = Cliente(serverName, serverPort)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("\033[0m\033[1mAun no hay un Chat Multicanal activo.\033[0m\033[0m ")
