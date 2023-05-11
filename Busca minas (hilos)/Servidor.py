import socket
import sys
import random
import threading

host = "127.0.0.1"
port = 65432
buffer_size = 1024
flag = 0
numConn = 2
tablero_g = []
dificultad = 0
correctas = []
condicion = True
criterio = 0


def nxt_trn(fg):

    global numConn

    if fg >= numConn - 1:
        print("----------AHORA_SE_EJECUTA_HILO_0----------")
        return 0
    else:
        print("----------AHORA_SE_EJECUTA_HILO_" + str(fg + 1) + "----------")
        return fg + 1


def generar_bombas(opcion):

    dimension = 0
    minas = []

    # DIFICULTAD PRINCIPIANTE
    if opcion == '0':

        dimension = 9
        continuar = True

        while continuar:
            bomba = (random.randint(0, 8), random.randint(0, 8))
            if bomba not in minas:
                minas.append(bomba)
            if len(minas) == 10:
                continuar = False

    # DIFICULTAD AVANZADA
    elif opcion == '1':

        dimension = 16
        continuar = True

        while continuar:
            bomba = (random.randint(0, 15), random.randint(0, 15))
            if bomba not in minas:
                minas.append(bomba)
            if len(minas) == 40:
                continuar = False

    else:
        return dimension, []

    return dimension, minas


def generar_tablero(dif):

    tablero = []
    dimension, minas = generar_bombas(dif)

    if dimension != 0:
        for fila in range(0, dimension):
            aux = []
            for columna in range(0, dimension):
                if (fila, columna) in minas:
                    aux.append('X')
                else:
                    aux.append('O')
            tablero.append(aux)
        return tablero

    else:
        return []


def dibujar(tablero):

    # Se pone una X inicial solo de referencia
    print('XX', end=" ")
    for indice in range(0, len(tablero)):
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
        print('')


def servirPorSiempre(socketTcp, listaconexiones):

    for num in range(numConn):
        client_conn, client_addr = socketTcp.accept()
        listaconexiones.append(client_conn)
        thread_read = threading.Thread(target=recibir_datos, args=[client_conn, client_addr, num])
        thread_read.start()

    while True:
        gestion_conexiones(listaconexiones)



def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    if len(listaconexiones) == 0:
        sys.exit(0)
    # print(len(listaconexiones))
    # print("hilos activos:", threading.active_count())
    # print("enum", threading.enumerate())
    # print("conexiones: ", len(listaconexiones))
    # print(listaconexiones)


def recibir_datos(client_conn, client_addr, num):

    global tablero_g
    global correctas
    global flag
    global dificultad
    global criterio
    global condicion

    while flag != num:
        pass

    print("Conexion establecida con:", client_addr, "...\n")

    flag = nxt_trn(flag)
    while flag != num:
        pass

    if flag == 0:
        print("Esperando a recibir dificultad del juego... ")
        dificultad = int.from_bytes(client_conn.recv(buffer_size), 'little') - 48
        print("Dificultad establecida en: ", dificultad, "...\n")
        tablero_g = generar_tablero(str(dificultad))
        print("El tablero es...\n")
        dibujar(tablero_g)
        print("\nPartida en progreso, validando los datos...")
        # Criterio para saber que tamaño debe de alcanzar la lista de validas
        if dificultad == 0:
            criterio = 71
        else:
            criterio = 216

    flag = nxt_trn(flag)
    while flag != num:
        pass

    while condicion:
        ax = client_conn.recv(buffer_size)
        bx = client_conn.recv(buffer_size)
        a = int(ax.decode())
        b = int(bx.decode())
        if tablero_g[a][b] == 'X':
            respuesta = b"-1"
            condicion = False
        else:
            if (a, b) not in correctas:
                correctas.append((a, b))
            if len(correctas) == criterio:
                respuesta = b"0"
                condicion = False
            else:
                respuesta = b"1"

        client_conn.sendall(respuesta)

        flag = nxt_trn(flag)
        while flag != num:
            pass

    # global listaConexiones
    # listaConexiones.remove(client_conn)
    print("Desconectando a: ", num)
    client_conn.close()
    print("Se desconecto: ", num)
    flag = nxt_trn(flag)



listaConexiones = []

serveraddr = (host, int(port))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    print("El servidor TCP está disponible y en espera de solicitudes")

    servirPorSiempre(TCPServerSocket, listaConexiones)
