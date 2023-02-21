# Jungbin Choi
# I pledge to the COMP 431 Honor Code


from socket import *
import socket
import sys
import os


# Globals
port_num: str = ''
string: str = ''
value: str = ''
index: int = 0
error: str = ''
forward: str = []
reverse: str = ''
data: str = []


# Constants
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
    global port_num, string, value, index, error, forward, reverse, data

    try:
        # Create socket from argv
        port_num = sys.argv[1]
        server = socket.socket(AF_INET, SOCK_STREAM)
        server.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)
        server.bind(('', int(port_num)))
        server.listen(1)
    except socket.error:
        print("Socket Creation Error")
        return

    while True:
        try:
            # Accept connection from client
            success_connect: bool = False
            try:
                connection, address = server.accept()
                success_connect = True
            except socket.error:
                print("Connection Error")

            send_220_success: bool = False
            if success_connect:
                # Send 220 message
                message_220: str = "220 " + socket.gethostname()
                try:
                    connection.send(message_220.encode())
                    send_220_success = True
                except socket.error:
                    print("220 Send Error")
                    if connection:
                        connection.close()

            hello_success: bool = False
            if send_220_success:
                # Recieve HELO message from client and respond with 250
                hello_from_client: str = connection.recv(2048).decode()
                client_name: str = ''
                if not check_hello_from_client(hello_from_client):
                    connection.send(error.encode())
                    if connection:
                        connection.close()
                else:
                    client_name = hello_from_client[4:].replace(' ', '').replace('\n', '')
                    Helo_250: str = "250 Hello " + client_name + " pleased to meet you"
                    connection.send(Helo_250.encode())
                    hello_success = True

            # SMTP Message Loop
            if hello_success:
                data_fail: bool = False
                error = ''
                index = 0
                string = connection.recv(2048).decode()
                value = string[index]

                data_fail = False

                reverse = ''
                forward.clear()
                data.clear()

                if mail_from_cmd():
                    connection.send(OK250.encode())

                    at_least_one: bool = False
                    while True:
                        index = 0
                        string = connection.recv(2048).decode()
                        value = string[index]

                        if rcpt_to_cmd():
                            at_least_one = True
                            connection.send(OK250.encode())
                        else:
                            index = 0
                            value = string[index]
                            error = ''
                            if mail_from_cmd() or error == ERROR501:
                                error = ERROR503
                                break
                            else:
                                index = 0
                                value = string[index]
                                error = ''

                                if at_least_one and data_cmd():
                                    connection.send(DATA354.encode())

                                    data_message: str = connection.recv(2048).decode()
                                        
                                    forward_domain: str = []
                                    for f_path in forward:
                                        at_index: int = 0
                                        char_index: int = 0
                                        for char in f_path:
                                            if char == '@':
                                                at_index = char_index
                                            char_index += 1
                                        if f_path[(at_index + 1):] not in forward_domain:
                                            forward_domain.append(f_path[(at_index + 1):])

                                    for path in forward_domain:
                                        full_path: str = "./forward/" + path
                                        if os.path.exists(full_path):
                                            with open(full_path, 'at') as message:
                                                message.write(data_message)
                                        else:
                                            with open(full_path, 'xt') as message:
                                                message.write(data_message)
                                        
                                    connection.send(OK250.encode())
                                    break
                                else:
                                    index = 0
                                    value = string[index]
                                    error = ''
                                    if ((not at_least_one) and data_cmd()) or error == ERROR501:
                                        error = ERROR503
                                        break
                                    else:
                                        index = 0
                                        value = string[index]
                                        error = ''
                                        rcpt_to_cmd()
                                        break

                    if error != '':
                        connection.send(error.encode())
                        if connection:
                            connection.close()
                else:
                    index = 0
                    value = string[index]
                    error = ''
                    if rcpt_to_cmd() or error == ERROR501:
                        error = ERROR503
                    else:
                        index = 0
                        value = string[index]
                        error = ''
                        if data_cmd() or error == ERROR501:
                            error = ERROR503
                        else:
                            index = 0
                            value = string[index]
                            error = ''
                            mail_from_cmd()

                    connection.send(error.encode())
                    if connection:
                        connection.close()
                    
            # QUIT Recieve/Answer
            quit_message: str = ''
            if connection:
                quit_message = connection.recv(2048).decode()
            if quit_message != "QUIT":
                print("QUIT Error")
            else:
                connection.send(("221 " + socket.gethostname().replace('\n', '') + " closing connection").encode())
                if connection:
                    connection.close()
        except (EOFError, IndexError):
            if data_fail:
                connection.send(ERROR501.encode())
            if connection:
                connection.close()
            

"""
    Checks the HELO command from the client

    * Generates 500/501 Error
"""
def check_hello_from_client(message: str):
    global string, value, index, error

    string = message
    index = 0
    value = string[index]

    for char in "HELO":
        if char != value:
            error = ERROR500
            return False
        index += 1
        value = string[index]

    if not whitespace():
        error = ERROR501
        return False

    return True


"""
    Checks the MAIL FROM Command

    * Generates 500/501 Error
"""
def mail_from_cmd():
    global value, string, index, error, reverse
    for char in "MAIL":
        if char != value:
            error = ERROR500
            return False
        index += 1
        value = string[index]

    if not whitespace():
        error = ERROR500
        return False

    for char in "FROM:":
        if char != value:
            error = ERROR500
            return False
        index += 1
        value = string[index]

    if not nullspace():
        return False

    if not reverse_path():
        return False
    index += 1
    value = string[index]

    if not nullspace():
        return False

    if not CRLF():
        return False

    # Saving reverse path
    begin_index: int = 0
    end_index: int = 0
    temp_index: int = 0
    for char in string:
        if char == '<':
            begin_index = temp_index + 1
        elif char == '>':
            end_index = temp_index
        temp_index += 1
    reverse = string[begin_index:end_index]

    return True


"""
    Checks the RCPT TO Command

    * Generates 500/501 Error
"""
def rcpt_to_cmd():
    global value, string, index, error, forward
    for char in "RCPT":
        if char != value:
            error = ERROR500
            return False
        index += 1
        value = string[index]

    if not whitespace():
        error = ERROR500
        return False

    for char in "TO:":
        if char != value:
            error = ERROR500
            return False
        index += 1
        value = string[index]

    if not nullspace():
        return False

    if not forward_path():
        return False
    index += 1
    value = string[index]

    if not nullspace():
        return False

    if not CRLF():
        return False

    begin_index: int = 0
    end_index: int = 0
    temp_index: int = 0
    for char in string:
        if char == '<':
            begin_index = temp_index + 1
        elif char == '>':
            end_index = temp_index
        temp_index += 1
    forward.append(string[begin_index:end_index])

    return True


"""
    Checks the DATA Command

    * Generates 500/501 Error
"""
def data_cmd():
    global value, string, index, error
    for char in "DATA":
        if char != value:
            error = ERROR500
            return False
        index += 1
        value = string[index]

    if not nullspace():
        return False

    if not CRLF():
        return False

    return True


"""
    Checks if the value is a whitespace or is a part of a whitespace

    * Generates 501 Error
"""
def whitespace():
    global value, error, index, string
    if not space():
        if error == '':
            error = ERROR501
        return False
    index += 1
    value = string[index]

    if not whitespace():
        error = ''

    return True


"""
    Checks if the character is a space or a tab
"""
def space():
    global value
    return ((value == ' ') or (value == '\t'))


"""
    Checks if the value is a null or is a whitespace
"""
def nullspace():
    global value, error
    if not whitespace():
        if not null():
            error = ''
            return True
        return False

    return True


"""
    Checks if the value is null
"""
def null():
    global value
    return value == ''


"""
    Checks if the reverse path is a valid path
"""
def reverse_path():
    return path()


"""
    Checks if the foward path is a valid path
"""
def forward_path():
    return path()


"""
    Checks the path

    * Generates 501 Error
"""
def path():
    global string, index, value, error
    if value != '<':
        if error == '':
            error = ERROR501
        return False
    index += 1
    value = string[index]

    if not mailbox():
        return False

    if value != '>':
        if error == '':
            error = ERROR501
        return False

    return True


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
    value = string[index]

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
    value = string[index]

    if not string_func():
        error = ''

    return True


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
    value = string[index]

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
    value = string[index]

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


"""
    Checks if the character is a newline

    * Generates 501 Error
"""
def CRLF():
    global value, error
    if value != '\n':
        if error == '':
            error = ERROR501
        return False

    return True


"""
    Checks if the character is a special character
"""
def special():
    global value
    spec_char: str = ['<', '>', '(', ')', '[', ']', '\\', '.', ',', ';', ':', '@', '\"']

    return value in spec_char


main()