import socket
import random


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


def generar_tablero(dificultad):

    tablero = []
    dimension, minas = generar_bombas(dificultad)

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


def main():

    host = "192.168.43.199"  # Direccion de la interfaz de loopback estándar (localhost)
    port = 65432  # Puerto que usa el cliente  (los puertos sin provilegios son > 1023)
    buffer_size = 1024

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
        TCPServerSocket.bind((host, port))
        TCPServerSocket.listen()
        print("El servidor está preparado para iniciar el juego...\n")

        client_conn, client_addr = TCPServerSocket.accept()
        with client_conn:
            print("Conexion establecida con:", client_addr, "...\n")
            while True:

                print("Esperando a recibir dificultad del juego... ")
                dificultad = int.from_bytes(client_conn.recv(buffer_size), 'little') - 48
                print("Dificultad establecida en: ", dificultad, "...\n")
                tablero = generar_tablero(str(dificultad))
                print("El tablero es...\n")
                dibujar(tablero)
                print("\nPartida en progreso, validando los datos...")

                # Criterio para saber que tamaño debe de alcanzar la lista de validas
                if dificultad == 0:
                    criterio = 71
                else:
                    criterio = 216

                condicion = True
                correctas = []
                while condicion:
                    print(len(correctas))

                    ax = client_conn.recv(buffer_size)
                    bx = client_conn.recv(buffer_size)
                    a = int(ax.decode())
                    b = int(bx.decode())
                    # print(len(tablero))
                    # print("a:", a)
                    # print("b:", b)
                    if tablero[a][b] == 'X':
                        client_conn.sendall(b"-1")
                        condicion = False
                    else:
                        if (a, b) not in correctas:
                            correctas.append((a, b))
                        if len(correctas) == criterio:
                            client_conn.sendall(b"0")
                            condicion = False
                        else:
                            client_conn.sendall(b"1")
                break
            TCPServerSocket.close()


if __name__ == "__main__":
    main()
