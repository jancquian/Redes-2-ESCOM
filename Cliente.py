import threading
import time
import socket
import logging

host = "127.0.0.1"
port = 65432
buffer_size = 1024
num_players = 2
players_list = []
flag = 0
tablero = []
condicion = True
victoria = False

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


def dibujar(tab):

    # Se pone una X inicial solo de referencia
    print('XX', end=" ")
    for indice in range(0, len(tab)):
        if indice < 10:
            print('0' + str(indice), end=" ")
        else:
            print(indice, end=" ")
    print(' ')

    # Se imprimen las filas caracter por caracter
    for fila in range(0, len(tablero)):
        if fila < 10:
            print('0' + str(fila), end=" ")
        else:
            print(fila, end=" ")

        for columna in range(0, len(tablero)):
            print(' ' + tablero[fila][columna], end=" ")
        print(' ')


def nxt_trn(fg):

    global players_list

    if len(players_list) == 0:
        return -1

    if players_list.index(fg) == len(players_list) - 1:
        print("----------AHORA_SE_EJECUTA_HILO_" + str(players_list[0]) + "----------")
        return players_list[0]
    else:
        idx = players_list.index(fg)
        print("----------AHORA_SE_EJECUTA_HILO_" + str(players_list[idx + 1]) + "----------")
        return players_list[idx + 1]


def player(num):
    """hilo de cada jugador"""
    global flag
    global tablero
    global condicion
    global victoria

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:

        TCPClientSocket.connect((host, port))

        while flag != num:
            pass

        print("\nConexion establecida con exito (Jugador " + str(num) + ")...\n")

        flag = nxt_trn(num)

        while flag != num:
            pass

        if num == 0:

            print("Selecciona la dificultad del juego...")
            print("     0. PRINCIPIANTE.")
            print("     1. AVANZADA.")

            while True:
                dificultad = str(input("Opción: "))
                if dificultad == '0' or dificultad == '1':
                    dificultad = bytes(dificultad, 'utf-8')
                    break
                else:
                    print("Volver a introducir", end=" ")

            TCPClientSocket.sendall(dificultad)

            # Se genera el tablero vacio
            # tablero = []

            if (int.from_bytes(dificultad, 'little') - 48) == 0:

                for fila in range(0, 9):
                    sub_lista = []
                    for columna in range(0, 9):
                        sub_lista.append('U')
                    tablero.append(sub_lista)

            else:

                for fila in range(0, 16):
                    sub_lista = []
                    for columna in range(0, 16):
                        sub_lista.append('U')
                    tablero.append(sub_lista)

            print("\nEl tablero de juego es...\n")

        while condicion:
            dibujar(tablero)
            a = int(input("Ingresa a(fila)   : "))
            b = int(input("Ingresa b(columna): "))
            # print(len(tablero))
            if -1 < a < len(tablero) and -1 < b < len(tablero):
                TCPClientSocket.sendall(bytes(str(a), 'utf-8'))
                time.sleep(1)
                TCPClientSocket.sendall(bytes(str(b), 'utf-8'))
                respuesta = TCPClientSocket.recv(buffer_size)
                if respuesta == b"-1":
                    print("Has perdido el juego, bomba en: ", (a, b))
                    condicion = False
                    break
                elif respuesta == b"0":
                    print("Has ganado el juego y una chapata, felicidades :)")
                    condicion = False
                    victoria = True
                    break
                elif respuesta == b"1":
                    tablero[a][b] = 'S'

                    flag = nxt_trn(num)
                    while flag != num:
                        pass

        if victoria:
            print("Han ganado...")
        else:
            print("Volaron en mil pedazos")

        TCPClientSocket.close()
        global players_list
        flag = nxt_trn(num)
        players_list.pop(players_list.index(num))

    # logging.debug("Función worker")
    return


threads = []
for i in range(num_players):
    players_list.append(i)
    t = threading.Thread(target=player, args=(i,))
    threads.append(t)
    t.start()
