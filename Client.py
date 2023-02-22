# Jungbin Choi
# I pledge to the COMP 431 Honor Code


from socket import *
import socket
import sys


# Globals
port_num: str = ''
server_name: str = ''
string: str = ''
value: str = ''
index: int = 0
error: str = ''


# Constants
CLIENTNAME = socket.gethostname()
ERROR500 = "500"
ERROR501 = "501"
ERROR503 = "503"
DATA354 = "354"
OK250 = "250"
ZERO_ASCII = 48
NINE_ASCII = 57
UPPER_A_ASCII = 65
UPPER_Z_ASCII = 90
LOWER_A_ASCII = 97
LOWER_Z_ASCII = 122


def main():
    global port_num, server_name, string, value, index, error

    # Ask for From:
    sys.stdout.write("From:\n")
    from_line: str = sys.stdin.readline().replace('\n', '')
    string = from_line
    value = string[index]
    while not mailbox():
        print("Wrong Format - From:")
        from_line = sys.stdin.readline().replace('\n', '')
        string = from_line
        index = 0
        value = string[index]

    # Ask for To:
    sys.stdout.write("To:\n")
    to_line: str = sys.stdin.readline()
    to_line_rm_nl: str = to_line.replace('\n', '')
    to_line_rm_sp: str = to_line_rm_nl.replace(" ", '')
    to_line_split: str = to_line_rm_sp.split(',')
    to_line_index: int = 0
    to_line_max: int = len(to_line_split)
    string = to_line_split[to_line_index]
    index = 0
    value = string[index]
    while True:
        string = to_line_split[to_line_index]
        index = 0
        value = string[index]
        if not mailbox():
            print("Wrong Format - To:")
            to_line = sys.stdin.readline()
            to_line_rm_nl = to_line.replace('\n', '')
            to_line_rm_sp = to_line_rm_nl.replace(" ", '')
            to_line_split = to_line_rm_sp.split(',')
            to_line_index = -1
            to_line_max = len(to_line_split)
            string = to_line_split[to_line_index]
            index = 0
            value = string[index]
        to_line_index += 1
        if to_line_index == to_line_max:
            break

    # Ask for Subject: & Message:
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
    recv_220_message: str = connection.recv(2048).decode()
    if recv_220_message != ("220 " + server_name):
        print("220 Error")
        # QUIT Send
        connection.send("QUIT".encode())
        # QUIT Recieve
        quit_answer: str = connection.recv(2048).decode()
        if quit_answer != ("221 " + server_name + " closing connection"):
            print("QUIT Error")
        return

    # Send HELO Message
    helo_message: str = "HELO " + CLIENTNAME + '\n'
    connection.send(helo_message.encode())

    # Recieve 250 Response
    recv_250_message: str = connection.recv(2048).decode()
    if recv_250_message != "250 Hello " + CLIENTNAME + " pleased to meet you":
        print("250 Error")
        # QUIT Send
        connection.send("QUIT".encode())
        # QUIT Recieve
        quit_answer: str = connection.recv(2048).decode()
        if quit_answer != ("221 " + server_name + " closing connection"):
            print("QUIT Error")
        return

    # MAIL FROM Send
    mail_from: str = "MAIL FROM: <" + from_line + ">\n"
    connection.send(mail_from.encode())

    # MAIL FROM Recieve/Error Check
    mail_from_answer: str = connection.recv(2048).decode()
    if mail_from_answer != OK250:
        print("MAIL FROM Error - " + mail_from_answer)
        # QUIT Send
        connection.send("QUIT".encode())
        # QUIT Recieve
        quit_answer: str = connection.recv(2048).decode()
        if quit_answer != ("221 " + server_name + " closing connection"):
            print("QUIT Error")
        return

    # RCPT TO Send/Recieve/Error Check
    for line in to_line_split:
        connection.send(("RCPT TO: <" + line + ">\n").encode())
        rcpt_to_answer: str = connection.recv(2048).decode()
        if rcpt_to_answer != OK250:
            print("RCPT TO Error - " + rcpt_to_answer)
            # QUIT Send
            connection.send("QUIT".encode())
            # QUIT Recieve
            quit_answer: str = connection.recv(2048).decode()
            if quit_answer != ("221 " + server_name + " closing connection"):
                print("QUIT Error")
            return

    # Send DATA
    data_send: str = "DATA\n"
    connection.send(data_send.encode())
    data_answer: str = connection.recv(2048).decode()
    if data_answer != DATA354:
        print("DATA Error - " + data_answer)
        # QUIT Send
        connection.send("QUIT".encode())
        # QUIT Recieve
        quit_answer: str = connection.recv(2048).decode()
        if quit_answer != ("221 " + server_name + " closing connection"):
            print("QUIT Error")
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
    data_success: str = connection.recv(2048).decode()
    if data_success != OK250:
        print("DATA Message Error - " + data_success)
        # QUIT Send
        connection.send("QUIT".encode())
        # QUIT Recieve
        quit_answer: str = connection.recv(2048).decode()
        if quit_answer != ("221 " + server_name + " closing connection"):
            print("QUIT Error")
        return

    # QUIT Send
    connection.send("QUIT".encode())

    # QUIT Recieve
    quit_answer: str = connection.recv(2048).decode()
    if quit_answer != ("221 " + server_name + " closing connection"):
        print("QUIT Error")
    return


"""
    Checks the mailbox

    * Generates 501 Error
"""
def mailbox():
    global string, index, value, error
    if not local_part():
        if error == '':
            error = ERROR501
        return False

    if value != '@':
        if error == '':
            error = ERROR501
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return False

    if not domain():
        if error == '':
            error = ERROR501
        return False

    return True


"""
    Checks if the local part is a string
"""
def local_part():
    return string_func()


"""
    Checks if it's a string

    * Generates 501 Error
"""
def string_func():
    global value, string, index, error
    if not char():
        if error == '':
            error = ERROR501
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return False

    if not string_func():
        error = ''

    return True


"""
    Checks if the character is a space or a tab
"""
def space():
    global value
    return ((value == ' ') or (value == '\t'))


"""
    Checks if the character is a special character
"""
def special():
    global value
    spec_char: str = ['<', '>', '(', ')', '[', ']', '\\', '.', ',', ';', ':', '@', '\"']

    return value in spec_char


"""
    Checks if the current value is a regular character i.e. not a spaceial char or space/tab
"""
def char():
    return not (space() or special())


"""
    Checks for the domain name
"""
def domain():
    global string, index, value
    if not element():
        return False

    if value == '.':
        index += 1
        value = string[index]
        return domain()

    return True


"""
    Checks if the element is a single character of is a name

    * Generates 501 Error
"""
def element():
    global value, string, index, error
    if not name():
        if error == '':
            error = ERROR501
        return False

    return True


"""
    Checks if the name is a series of letters
"""
def name():
    global value, string, index
    if not letter():
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return False

    let_dig_str()

    return True


"""
    Checks if the character is a letter using the character's ASCII
"""
def letter():
    global value
    ascii_value = ord(value)

    return (((ascii_value >= UPPER_A_ASCII) and (ascii_value <= UPPER_Z_ASCII)) or ((ascii_value >= LOWER_A_ASCII) and (ascii_value <= LOWER_Z_ASCII)))


"""
    Checks if the given string is a letter, digit or a string
"""
def let_dig_str():
    global value, string, index
    if not let_dig():
        return False
    index += 1
    try:
        value = string[index]
    except IndexError:
        return False

    let_dig_str()

    return True


"""
    Checks if the character is a letter or a digit
"""
def let_dig():
    return (letter() or digit())


"""
    Checks if the character is decimal digit
"""
def digit():
    global value
    ascii_value = ord(value)

    return ((ascii_value >= ZERO_ASCII) and (ascii_value <= NINE_ASCII))


main()