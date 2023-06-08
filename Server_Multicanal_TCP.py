import sys
from socket import *
import threading
import random
import shutil

WIDTH = shutil.get_terminal_size().columns


class USER:
    nom = ""
    ip = ""
    socket = ""
    canalActual = ""
    connSock = ""

    def __init__(self, nom, ip, socket, canalActual, connSock):
        self.nom = nom
        self.ip = ip
        self.socket = socket
        # El canal al que un usuari s'uniex per defecte es el canal Main.
        self.canalActual = canalActual
        self.connSock = connSock

    def setNomCanal(self, nomNou):
        self.canalActual = nomNou

    def getNomCanal(self):
        return self.canalActual


class CANAL:
    nom = ""
    socketCanal = ""
    # Finalment es un set d'usuaris, no de strings nom nomes.
    usuarisCanalVec = []

    def __init__(self, nom, socketCanal, usuarisCanalVec):
        self.nom = nom
        self.socketCanal = socketCanal
        self.usuarisCanalVec = usuarisCanalVec


class Servidor:  # Classe que representa el servidior del xat multicanal en TCP.

    sockets = []
    # Array on es guardaràn les connexions fetes (els seus sockets creats).
    # Cada socket es únic per execució. Es necessari per a fer l'enviament dels missatges.
    canales = set()
    usuaris = set()
    forasters = set()
    # Set amb tots els usuaris del servidor.

    def __init__(self, serverPort):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(1)
        print("\033[1mEl Chat Multicanal esta en " +
              "\033[92m\033[1mlínea\033[0m\033[0m")

        while True:

            # Bucle que rep les connexions de tots els clients.
            connectionSocket, addr = serverSocket.accept()
            self.sockets.append(connectionSocket)

            nom_usuari = connectionSocket.recv(1024).decode()
            usuari = USER(nom_usuari, addr[0],
                          addr[1], "Main", connectionSocket)
            self.usuaris.add(usuari)
            self.forasters.add(usuari)
            print("\033[92m\033[1m\n▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                  str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + "\033[92m\033[1m Se ha unido▬▬▶\033[0m\033[0m")

            procAux = threading.Thread(
                target=self.aux, args=(addr, connectionSocket))
            procAux.daemon = True
            procAux.start()
            # Procés auxiliar que ens permet dur a terme un bucle infinit que estigui continuament esperant
            # noves connexions mentre que alhora tenim un altre bucle infinit que ens permet reenviar els
            # missatges de cada client a tota la resta de clients.

    def aux(self, addr, connecSocket):
        while True:
            feedback = " "
            # Bucle que rep i reenvia els missatges que envien tots els clients.
            sentence = connecSocket.recv(1024).decode()
            mis = sentence.split(' ', 1)

            for x in self.usuaris:
                if x.ip == addr[0] and x.socket == addr[1]:
                    nom_usuari = x.nom
                    break

            if (mis[0] == "CREA"):
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0\033[0")
                trobat = False
                for i in self.canales:
                    if i.nom == mis[1]:
                        trobat = True
                        break

                if trobat:
                    feedback = "   \033[0;31m\033[1m↳\033[0m ❌ \033[0;31m\033[1mEl canal ja existeix. " + \
                        "\033[0m\033[1m" + nom_usuari + "\033[0;31m\033[1m " + \
                        "no ha pogut crear el canal \033[0m\033[0m" + \
                        mis[1] + "\033[0m\033[0m"
                else:
                    self.crear_canal(mis[1])
                    feedback = (
                        "   \033[92m\033[1m↳\033[0m\033[1m ✅ " + nom_usuari + "\033[92m\033[1m ha creat el canal \033[0m\033[1m " + mis[1] + "\033[92m\033[1m correctament\033[0m\033[0m")

                print(feedback)

            elif mis[0] == "ELIMINA":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0m\033[0m")
                trobat2 = False
                for canal in self.canales:
                    if canal.nom == mis[1]:
                        trobat2 = True
                        break

                if trobat2:
                    self.eliminar_canal(mis[1])
                    feedback = (
                        "   \033[92m\033[1m↳\033[0m ✅ \033[1m" + nom_usuari + "\033[92m\033[1m ha eliminat el canal \033[0m\033[1m" + mis[1] + "\033[92m\033[1m correctament\033[0m\033[0m")
                else:
                    feedback = ("   \033[0;31m\033[1m↳\033[0m\033[1m ❌ \033[0;31m\033[1mEl canal no existeix. \033[0m\033[1m" +
                                nom_usuari + " \033[0;31m\033[1mno ha pogut eliminar el canal \033[0m\033[1m" + mis[1] + "\033[0m\033[0m")

                print(feedback)

            elif mis[0] == "CANVIA":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0m\033[0m")
                # Metode per canviar el nom del canal()
                if mis[1] != "Main":
                    existeix = False
                    for canal in self.canales:
                        # Comprovar que existeix el canal al que et vols canviar.
                        if canal.nom == mis[1]:
                            existeix = True
                            break
                else:
                    existeix = True

                if existeix:
                    for i in self.usuaris:
                        if i.connSock == connecSocket:
                            if i.canalActual == mis[1]:
                                feedback = ("   \033[0;31m\033[1m↳\033[0m ❌ \033[0m\033[1m " + nom_usuari + "\033[0;31m\033[1m Ja es al canal \033[0m\033[1m" +
                                            mis[1] + "\033[0;31m\033[1m. No ha pogut canviar de canal\033[0m\033[0m")
                            else:
                                self.canviar_canal(mis[1], i.nom)
                                feedback = "   \033[92m\033[1m↳\033[0m\033[1m ✅ \033[0m\033[1m " + nom_usuari + "\033[92m\033[1m ha canviat al canal \033[0m\033[0m" + \
                                    mis[1] + " \033[92m\033[1m correctament\033[0m\033[0m"
                            break

                else:
                    feedback = "   \033[0;31m\033[1m↳\033[0m\033[1m ❌ \033[0;31m El canal no existeix. \033[0m\033[0m" + \
                        nom_usuari + \
                        "\033[0;31m\033[1m No ha pogut canviar de canal\033[0m\033[0m"

                print(feedback)

            elif mis[0] == "PRIVAT":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m" + sentence + "\033[0m\033[0m")			
                tr = False
                s = mis[1].split(' ', 1)
                for u in self.usuaris:
                    if u.nom == s[0]:
                        sock = u.connSock
                        tr = True

                if tr:
                    mensaje = "\033[92m\033[1m ▶ " + \
                        str(nom_usuari) + "[PRIVAT]: \033[0m\033[1m" + s[1] + "\033[0m\033[0m"
                    self.envia_privat(sock, mensaje)
                    feedback = (
                        "   \033[92m\033[1m↳\033[0m ✅ \033[1m" + nom_usuari + "\033[92m\033[1m ha enviat el missatge \033[0m\033[1m" + s[1] + "\033[92m\033[1m a l'usuari \033[0m\033[1m" + s[0] + "\033[92m\033[1m correctament.\033[0m\033[0m")
                else:
                    feedback = (
                        "   \033[0;31m\033[1m↳\033[0m\033[1m ❌ \033[0;31m\033[1m No s'ha trobat l'usuari \033[0m\033[1m" + s[0] + "\033[0m\033[0m")

                print(feedback)

            elif mis[0] == "MOSTRA_CANALS":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0m\033[0m")
                self.imprimir_canals(connecSocket)

            elif mis[0] == "MOSTRA_USUARIS":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0m\033[0m")
                self.imprimir_usuaris_canal_actual(connecSocket)

            elif mis[0] == "MOSTRA_TOTS":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0m\033[0m")
                self.imprimir_tots_users(connecSocket)
            
            elif mis[0] == "HELP":
                print("\n\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mComanda escollida: \033[0m\033[1m" + sentence + "\033[0m\033[0m")
                self.menu_comandas(connecSocket)

            else:  # Parla al servidor, canal actual.
                for i in self.usuaris:
                    if i.connSock == connecSocket:
                        can = i.canalActual
                        break

                for c in self.canales:
                    if c.nom == can:
                        break

                if can == "Main":
                    for usu in self.forasters:
                        if usu.connSock != connecSocket:
                            mensaje = "\033[92m\033[1m ▶ " + \
                                str(nom_usuari) + ": \033[0m\033[1m" + sentence + "\033[0m\033[0m"
                            usu.connSock.send(mensaje.encode())
                else:
                    for u in c.usuarisCanalVec:
                        if u.connSock != connecSocket:
                            mensaje = "\033[92m\033[1m ▶ " + \
                                str(nom_usuari) + ": \033[0m\033[1m" + sentence + "\033[0m\033[0m"
                            u.connSock.send(mensaje.encode())

                print("\033[92m\033[1m▬▬\033[0m\033[1m" + str(addr[0]) + ":" +
                      str(addr[1]) + "\033[92m\033[1m▬▬ 👤 \033[0m\033[1m" + str(nom_usuari) + " \033[92m\033[1mEn el Canal \033[0m\033[1m" + str(can) + " \033[92m\033[1mHa dit:\033[0m\033[1m 💬 " + sentence + "\033[0m\033[0m")

            # Enviament de feedback a l'usuari que ha escrit la comanda.
            connecSocket.send(feedback.encode())

    def imprimir_canals(self, connecSocket):
        res = ""
        print("\033[92m\033[1m[CANALS ACTUALS]: \033[0m\033[0m")
        res += "\033[92m\033[1m\n[CANALS ACTUALS]:\n\033[0m\033[0m"
        print("\n\033[92m\033[1m  ➤ \033[0m\033[1mMain\033[0m\033[0m" + '\n', end='')
        res += "\n\033[92m\033[1m  ➤ \033[0m\033[1mMain\033[0m\033[0m" + '\n'
        for canal in self.canales:
            print("\n\033[92m\033[1m  ➤ \033[0m\033[1m" + canal.nom + "\033[0m\033[0m" +'\n', end='')
            res += "\n\033[92m\033[1m  ➤ \033[0m\033[1m" + canal.nom + "\033[0m\033[0m" + '\n'
        connecSocket.send(res.encode())

    def imprimir_usuaris_canal_actual(self, connecSocket):
        for u in self.usuaris:
            if u.connSock == connecSocket:
                canal_actual = u.canalActual
                break

        a = []
        for c in self.canales:
            if c.nom == canal_actual:
                a = c.usuarisCanalVec
                break

        res = ""
        print("\033[92m\033[1m[USUARIS \033[0m\033[1m" + canal_actual + "\033[92m\033[1m]: \033[0m\033[0m")
        res += "\033[92m\033[1m\n[USUARIS \033[0m\033[1m" + canal_actual + "\033[92m\033[1m]:\n\033[0m\033[0m" 
        if canal_actual == "Main":
            for usu in self.forasters:
                print("\n\033[92m\033[1m  ➤ \033[0m\033[1m" + usu.nom + "\033[0m\033[0m" + '\n', end='')
                res += "\n\033[92m\033[1m  ➤ \033[0m\033[1m" + usu.nom + "\033[0m\033[0m" + '\n'
        else:
            for usu in a:
                print("\n\033[92m\033[1m  ➤ \033[0m\033[1m" + usu.nom + "\033[0m\033[0m" + '\n', end='')
                res += "\n\033[92m\033[1m  ➤ \033[0m\033[1m" + usu.nom + "\033[0m\033[0m" + '\n'
        connecSocket.send(res.encode())

    def imprimir_tots_users(self, connecSocket):
        res = ""
        print("\033[92m\033[1m[USUARIS CONNECTATS]: \033[0m\033[0m" )
        res += "\033[92m\033[1m\n[USUARIS CONNECTATS]:\n\033[0m\033[0m" 
        for u in self.usuaris:
            print("\n\033[92m\033[1m  ➤\033[0m\033[1m "  + str(u.nom) + " | " + str(u.ip) +
                  " | " + str(u.socket) + " | " + str(u.canalActual) + " | " + str(u.connSock) + '\n' + "\033[0m\033[0m" , end='')
            res += "\n\033[92m\033[1m  ➤ \033[0m\033[1m" + str(u.nom) + "\033[92m\033[1m está en \033[0m\033[1m" + \
                str(u.canalActual) + '\n' + "\033[0m\033[0m" 
        connecSocket.send(res.encode())

    def crear_canal(self, nom_canal):
        nouCanalSocket = socket(AF_INET, SOCK_STREAM)
        canalNouUsuaris = set()

        nouCanalSocket = socket(AF_INET, SOCK_STREAM)
        # 1024 through 49151 Non well-known ports
        nouCanalSocket.bind(('', random.randint(6000, 40000)))

        canalNou = CANAL(nom_canal, nouCanalSocket, canalNouUsuaris)
        self.canales.add(canalNou)

    def eliminar_canal(self, nom_canal):
        trobat2 = False
        for c in self.canales:
            if c.nom == nom_canal:
                trobat2 = True
                break

        if trobat2:
            for i in c.usuarisCanalVec.copy():
                self.canviar_canal("Main", i.nom)
            c.socketCanal.close()
            self.canales.discard(c)

    def canviar_canal(self, nom_canal, nom_usuari):
        canalAnterior = ""
        for u in self.usuaris:
            if u.nom == nom_usuari:
                canalAnterior = u.canalActual
                u.canalActual = nom_canal
                break

        if canalAnterior == "Main":
            self.forasters.discard(u)
        else:
            for c in self.canales:
                if c.nom == canalAnterior:
                    c.usuarisCanalVec.discard(u)
                    break

        if nom_canal == "Main":
            self.forasters.add(u)
        else:
            for c in self.canales:
                if c.nom == nom_canal:
                    c.usuarisCanalVec.add(u)
                    break

    def envia_privat(self, sock, mensaje):
        sock.send(mensaje.encode())

    def menu_comandas(self, connecSocket):
        res = ""
        res += ("\n\033[92m\033[1m[MENU OPCIONS]:\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ CREAR CANAL\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m CREA [nom_canal]\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ ELIMINAR CANAL\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m ELIMINA [nom_canal]\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ CANVIAR DE CANAL\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m CANVIA [nom_canal]\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ MISSATGE PRIVAT A UN USUARI\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m PRIVAT [nom_usuari] [missatge]\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ MOSTRAR TOTS ELS CANALS QUE ESTAN ACTIUS\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m MOSTRA_CANALS\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ MOSTRAR ELS USUARIS DEL CANAL ACTUAL\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m MOSTRA_USUARIS\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ MOSTRAR TOTS ELS USUARIS CONNECTATS A AQUEST SERVIDOR\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m MOSTRA_TOTS\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ ENVIAR UN MISSATGE GENERAL\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m [missatge]\n\033[0m\033[0m")
        res += ("\n\033[92m\033[1m  ➤ AJUDA AMB LES COMANDES DISPONIBLES\033[0m\033[0m")
        res += ("\n\033[92m\033[1m         Sintaxis:\033[0m HELP\n\033[0m\033[0m")
        connecSocket.send(res.encode())


if __name__ == '__main__':

    # Per defecte tenim el port 5000.
    serverPort = 5000

    while True:
        # Bucle que intenta inicialitzar el servidor. Una vegada el servidor es troba iniciat, pot
        # rebre clients en forma local o mitjançant connexió TCP.
        print("Intentando Inicializar el Chat Multicanal...")
        try:
            servidor = Servidor(serverPort)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            print("No se ha podido iniciar el Chat Multicanal. Direccion en uso...")

    # Hemos escogido TCP por encima de UDP porque cada vez que el cliente envia un mensaje/una comanda, le envia al servidor su ip y un socket;
    # mientras que en TCP, el Cliente solo se lo envia una vez en la fase de conexion.
    # Asi evitamos llenar nuestro array con sockets que se vuelven inservibles.
