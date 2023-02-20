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
    from_line: str = sys.stdin.readline().remove('\n')
    sys.stdout.write("To:\n")
    to_line: str = sys.stdin.readline()
    to_line_split: str = to_line.split(',')
    for line in to_line_split:
        line.remove('').remove('\n')
    sys.stdout.write("Subject:\n")
    subject_line: str = sys.stdin.readline()
    sys.stdout.write("Message:\n")
    message_lines: str = []
    while True:
        message: str = sys.stdin.readline()
        if message != ".\n":
            message_lines.append(message)
        else:
            message_lines.append(message)
            break

    try:
        # Create socket from argv
        server_name = sys.argv[1]
        port_num = sys.argv[2]
        connection = socket(AF_INET, SOCK_STREAM)
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
        connection.send("RCPT TO: <" + line + ">\n")
        rcpt_to_answer: str = connection.recv(1024).decode()
        if rcpt_to_answer != OK250:
            print("RPCT TO Error - " + rcpt_to_answer)
            return

    # Send DATA/Headers
    connection.send("DATA\n".encode())
    data_answer: str = connection.recv(1024).decode()
    if data_answer != DATA354:
        print("DATA Error - " + data_answer)
        return

    connection.send(('From: <' + from_line + '>\n').encode())

    line_index: int = 0
    max_line_index: int = len(to_line_split) - 1
    single_line: str = ''
    for line in to_line_split:
        line = "<" + line + ">"
        if line_index != max_line_index:
            line = line + ", "
        single_line += line
        line_index += 1
    connection.send(("To: " + single_line + '\n').encode())
    
    connection.send(("Subject: " + subject_line + '\n').encode())

    for line in message_lines:
        connection.send(line.encode())
    
    # DATA Recieve/Error Checking
    data_success_answer: connection.recv(1024).decode()
    if data_success_answer != OK250:
        print("DATA Error - " + data_success_answer)
        return

    # QUIT Send
    connection.send("QUIT".encode())

    # QUIT Recieve
    quit_answer: str = connection.recv(1024).decode()
    if quit_answer != ("221 " + server_name + " closing connection"):
        print("QUIT Error")
    return


main()