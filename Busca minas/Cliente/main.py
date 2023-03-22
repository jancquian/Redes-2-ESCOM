import socket


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
        print(' ')


def main():

    print("Ingresa los datos del servidor para iniciar el juego...\n")
    host = str(input("HOST: "))  # loop back 127.0.0.1
    port = int(input("PORT: "))  # 65432 mayor a 1024
    buffer_size = 1024  # limitar el tamaño de los mensajes

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((host, port))
        print("\nConexion establecida con exito...\n")

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
        tablero = []

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

        condicion = True
        while condicion:
            dibujar(tablero)
            a = int(input("Ingresa a(fila)   : "))
            b = int(input("Ingresa b(columna): "))
            print(len(tablero))
            if -1 < a < len(tablero) and -1 < b < len(tablero):
                TCPClientSocket.sendall(bytes(str(a), 'utf-8'))
                TCPClientSocket.sendall(bytes(str(b), 'utf-8'))
                respuesta = TCPClientSocket.recv(buffer_size)
                if respuesta == b"-1":
                    print("Has perdido el juego, bomba en: ", (a, b))
                    break
                elif respuesta == b"0":
                    print("Has ganado el juego y una chapata, felicidades :)")
                    break
                elif respuesta == b"1":
                    tablero[a][b] = 'S'

        TCPClientSocket.close()


if __name__ == "__main__":
    main()
