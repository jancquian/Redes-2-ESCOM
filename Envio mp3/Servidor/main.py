
#    recording = AudioSegment.from_file(BytesIO(song_byte), format="mp3")
#    recording.export('new.mp3', format='mp3')  # for export
#    play(recording)  # for play

import socket
import selectors
from pydub import AudioSegment
from io import BytesIO


sel = selectors.DefaultSelector()
mp3_segments = []
mp3_dic = {}
iterator = 0


def joint_segments(segment_bytelist):

    songbyte = b""

    for byte_segment in segment_bytelist:
        songbyte = songbyte + byte_segment

    return songbyte


def accept(sock_a, mask_a):
    sock_conn, addr = sock_a.accept()  # Should be ready
    print('aceptado', sock_conn, ' de', addr)
    sock_conn.setblocking(False)
    sel.register(sock_conn, selectors.EVENT_READ | selectors.EVENT_WRITE, read_write)
    # sel.register(sock_conn,selectors.EVENT_WRITE, read_write)


def read_write(sock_c, mask_c):
    if mask & selectors.EVENT_READ:
        data = sock_c.recv(1024)  # Should be ready
        global mp3_dic
        # global mp3_segments
        global iterator

        if data:
            print('recibido', repr(data), 'a', sock_c)

            if str(sock_c.fileno()) in mp3_dic:
                mp3_dic[str(sock_c.fileno())].append(data)
            else:
                mp3_dic[str(sock_c.fileno())] = []
                mp3_dic[str(sock_c.fileno())].append(data)
            # print(sock_c.fileno())
            # mp3_segments.append(data)
            print('respondiendo', repr(data), 'a', sock_c)
            sock_c.sendall(data)  # Hope it won't block
        else:
            #newsong_byte = joint_segments(mp3_segments)
            newsong_byte = joint_segments(mp3_dic[str(sock_c.fileno())])

            newsong_name = "new_mp3_" + str(iterator) + ".mp3"

            newsong_mp3 = AudioSegment.from_file(BytesIO(newsong_byte), format="mp3")
            newsong_mp3.export(newsong_name, format='mp3')

            iterator = iterator + 1
            # mp3_segments = []

            print('cerrando', sock_c)
            sel.unregister(sock_c)
            sock_c.close()
    if mask & selectors.EVENT_WRITE:
        print("enviando datos")


with socket.socket() as sock_accept:
    sock_accept.bind(('localhost', 12345))
    sock_accept.listen(100)
    sock_accept.setblocking(False)
    sel.register(sock_accept, selectors.EVENT_READ, accept)
    while True:
        print("Esperando evento...")
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
