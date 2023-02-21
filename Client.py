# Jungbin Choi
# I pledge to the COMP 431 Honor Code


from socket import *
import socket
import sys


# Globals
port_num: str = ''
server_name: str = ''


# Constants
CLIENTNAME = socket.gethostname()
ERROR500 = "500"
ERROR501 = "501"
ERROR503 = "503"
DATA354 = "354"
OK250 = "250"


def main():
    global port_num, server_name

    # Ask for headers
    sys.stdout.write("From:\n")
    from_line: str = sys.stdin.readline().replace('\n', '')
    sys.stdout.write("To:\n")
    to_line: str = sys.stdin.readline()
    to_line_split: str = to_line.split(',')
    for line in to_line_split:
        line = line.replace(' ', '')
    sys.stdout.write("Subject:\n")
    subject_line: str = sys.stdin.readline()
    sys.stdout.write("Message:\n")
    message_lines: str = []
    while True:
        message: str = sys.stdin.readline()
        if message != ".\n":
            message_lines.append(message)
        else:
            break

    try:
        # Create socket from argv
        server_name = sys.argv[1]
        port_num = sys.argv[2]
        connection = socket.socket(AF_INET, SOCK_STREAM)
        connection.connect((server_name, int(port_num)))
    except socket.error:
        print("Socket Creation/Connection Error")
        return

    # Recieve 220 Message
    recv_220_message: str = connection.recv(1024).decode()
    if recv_220_message != ("220 " + server_name):
        return

    # Send HELO Message
    helo_message: str = "HELO " + CLIENTNAME + '\n'
    connection.send(helo_message.encode())

    # Recieve 250 Response
    recv_250_message: str = connection.recv(1024).decode()

    # MAIL FROM Send
    mail_from: str = "MAIL FROM: <" + from_line + ">\n"
    connection.send(mail_from.encode())

    # MAIL FROM Recieve/Error Check
    mail_from_answer: str = connection.recv(1024).decode()
    if mail_from_answer != OK250:
        print("MAIL FROM Error - " + mail_from_answer)
        return

    # RCPT TO Send/Recieve/Error Check
    for line in to_line_split:
        connection.send(("RCPT TO: <" + line.replace('\n', '') + ">\n").encode())
        rcpt_to_answer: str = connection.recv(1024).decode()
        if rcpt_to_answer != OK250:
            print("RCPT TO Error - " + rcpt_to_answer)
            return

    # Send DATA
    data_send: str = "DATA\n"
    connection.send(data_send.encode())
    data_answer: str = connection.recv(1024).decode()
    if data_answer != DATA354:
        print("DATA Error - " + data_answer)
        return
    
    from_line_portion: str = "From: <" + from_line + ">\n"
    line_index: int = 0
    max_line_index: int = len(to_line_split) - 1
    to_line_portion: str = "To: "
    for line in to_line_split:
        line = "<" + line.replace('\n', '') + ">"
        if line_index != max_line_index:
            line = line + ", "
        to_line_portion += line
        line_index += 1
    subject_line_portion: str = "\nSubject: " + subject_line + '\n'
    message_line_portion: str = ''
    for line in message_lines:
        message_line_portion += line

    data_line: str = from_line_portion + to_line_portion + subject_line_portion + message_line_portion

    connection.send(data_line.encode())

    # DATA Recieve/Error Checking
    data_success: str = connection.recv(1024).decode()
    if data_success != OK250:
        print("DATA Message Error - " + data_success)
        return

    # QUIT Send
    connection.send("QUIT".encode())

    # QUIT Recieve
    quit_answer: str = connection.recv(1024).decode()
    if quit_answer != ("221 " + server_name + " closing connection"):
        print("QUIT Error")
    return


main()