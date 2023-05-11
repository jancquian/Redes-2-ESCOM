# !/usr/bin/env python3

# import sys
import socket
import selectors
import types
# from pydub import AudioSegment
# from pydub.playback import play
# from io import BytesIO

# COSAS DE PYDUB
#    recording = AudioSegment.from_file(BytesIO(song_byte), format="mp3")
#   recording.export('new.mp3', format='mp3')  # for export
#    play(recording)  # for play
# FIN DE PYDUB

# Esto va a ser una funcion para recuperar los bytes del .mp3 a partir de la lista de segmentos(bytes) en la cual
# se fragmento el archivo:

# message_from_list = b""
# for byte_segment in mp3bytelist:
#    message_from_list = message_from_list + byte_segment
# recording = AudioSegment.from_file(BytesIO(message_from_list), format="mp3")
# recording.export('new_song.mp3', format='mp3')

# Fin de la funcion


def fragment_mp3(bytes_mp3, buffer_size):

    start = 0
    end = buffer_size
    size = buffer_size

    mp3bytelist = []

    while True:

        segment = bytes_mp3[start:end]
        mp3bytelist.append(segment)

        start = start + size
        end = start + size

        if end >= len(bytes_mp3):
            f_segment = bytes_mp3[start:len(bytes_mp3)]
            mp3bytelist.append(f_segment)
            break

    return mp3bytelist


def select_message_list(identifier):

    if identifier == 1:
        song_mp3 = open("input/audio.mp3", 'rb')
    elif identifier == 2:
        song_mp3 = open("input/audio2.mp3", 'rb')
    elif identifier == 3:
        song_mp3 = open("input/audio3.mp3", 'rb')
    else:
        song_mp3 = open("input/default.mp3", 'rb')

    byte_mp3 = song_mp3.read()
    mp3_segments = fragment_mp3(byte_mp3, 1024)

    return mp3_segments


def start_connections(host, port, num_conns):
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print("Iniciando conexión", connid, "con", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        messages = select_message_list(connid)
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=list(messages),
            outb=b"",
        )
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("recibido", repr(recv_data), "de conexión", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print("cerrando conexión", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


sel = selectors.DefaultSelector()

host = "127.0.0.1"
port = 12345
num_conns = 4

start_connections(host, int(port), int(num_conns))


try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
