import socket
import threading
import tablegui
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client

global connection
global connection_accepted
global connection_thread
global server

HOST_IP = "0.0.0.0"

global CLIENT_IP
MY_PORT = 8000
CLIENT_PORT = 8000

def get_my_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP


def handle_send_start_game():
    print(CLIENT_IP, CLIENT_PORT)
    with xmlrpc.client.ServerProxy(f"http://{CLIENT_IP}:{CLIENT_PORT}/") as proxy:
        proxy.handle_start_game(get_my_ip(), MY_PORT)
        gui.hide_waiting_screen()
        gui.start_game(handle_send_message, handle_send_move, handle_send_give_up, 2)


def handle_send_message(message):
    if not message:
        return False
    with xmlrpc.client.ServerProxy(f"http://{CLIENT_IP}:{CLIENT_PORT}/") as proxy:
        proxy.handle_message(message)
    return True


def handle_send_move(x, y, z):
    gui.make_move(x, y, z)
    with xmlrpc.client.ServerProxy(f"http://{CLIENT_IP}:{CLIENT_PORT}/") as proxy:
        proxy.handle_move(f"{x}x{y}x{z}")


def handle_send_give_up():
    with xmlrpc.client.ServerProxy(f"http://{CLIENT_IP}:{CLIENT_PORT}/") as proxy:
        proxy.handle_give_up()
        gui.hide_game_screen()
        gui.show_disconnected_screen()
        connection_thread.join()


def handle_start_game(ip, port):
    global CLIENT_IP
    global CLIENT_PORT
    if CLIENT_IP:
        return False
    CLIENT_IP = ip
    CLIENT_PORT = port
    gui.hide_waiting_screen()
    gui.start_game(handle_send_message, handle_send_move, handle_send_give_up, 1)


def handle_connection_as_host(ip, port):
    global MY_PORT
    global CLIENT_IP
    global CLIENT_PORT

    CLIENT_IP = ip
    CLIENT_PORT = port

    MY_IP = get_my_ip()
    try:
        server = SimpleXMLRPCServer((MY_IP, MY_PORT), allow_none=True)
    except:
        MY_PORT += 1
        server = SimpleXMLRPCServer((MY_IP, MY_PORT), allow_none=True)
    print(f"Listening on port {MY_PORT}...")
    server.register_function(handle_start_game, "handle_start_game")
    server.register_instance(gui)
    gui.hide_connection_screen()
    gui.show_waiting_screen(MY_IP, MY_PORT, ip)
    if ip:
        handle_send_start_game()
    server.serve_forever()



def handle_start_connection(ip, port):
    global connection_thread
    if ip:
        connection_thread = threading.Thread(target=handle_connection_as_host, args=(ip, port))
    else:
        connection_thread = threading.Thread(target=handle_connection_as_host, args=('', ''))
    connection_thread.start()


gui = tablegui.TableGUI(handle_start_connection)


def main():
    gui.mainloop()


if __name__ == "__main__":
    main()
