import sys
import math
import time
import pickle
import socket
import numpy as np
from matplotlib import pyplot as plt

# Path Const
path_vetor_sinal_1 = "C:\\Users\\joaop\Desktop\\trabaio\\Client 1\\input\\g-1.txt"
path_vetor_sinal_2 = "C:\\Users\\joaop\Desktop\\trabaio\\Client 1\\input\\g-2.txt"
path_vetor_sinal_3 = "C:\\Users\\joaop\Desktop\\trabaio\\Client 1\\input\\a-1.txt"

path_image_output = "C:\\Users\\joaop\Desktop\\trabaio\\Client 1\\output\\"

# Client
server_address = ('localhost', 10000)

# Server
def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_server(sock):
    sock.connect(server_address)
    
def send_message(sock, msg):
    totalsent = 0
    while totalsent < sys.getsizeof(msg):
        sent = sock.send(msg[totalsent:])
        if sent == 0:
            break
        totalsent = totalsent + sent

def receive_message(sock):
    data = []
    last_signal = 0
    while True:
        packet = sock.recv(4096)
        if packet:
            data.append(packet)
            if sys.getsizeof(packet) < last_signal:
                print("Imagens Recebidas")
                break
            last_signal = sys.getsizeof(packet)
        else:
            break
    return data

# Signal Handler
def open_vetor_sinal(path_vetor_sinal):
    vetor_sinal = np.genfromtxt(path_vetor_sinal,dtype=str,delimiter='\n')
    vetor_sinal = np.char.replace(vetor_sinal, ',', '.')
    vetor_sinal = vetor_sinal.astype(np.float64)
    return vetor_sinal

def ganho_sinal(vetor_sinal):
#     sinal = vetor_sinal.reshape(64, 794)
#     nrows, ncols = sinal.shape
#     for i in range(nrows):
#         for j in range(ncols):
#             y = 100 + (1/20)*(j+1)*np.sqrt(j+1)
#             sinal[i][j] = sinal[i][j] * y

#     sinal = sinal.reshape(nrows * ncols)
    sinal = vetor_sinal
    for i in range(len(sinal)):
        y = 100 + (1/20)*(i+1)*np.sqrt(i+1)
        sinal[i] = sinal[i] * y
    
    return sinal

def mandar_vetor_sinal(sock, path, algorithm, user):
    print("Enviando Vetor Sinal")
    vetor_sinal = open_vetor_sinal(path)
    vetor_sinal = ganho_sinal(vetor_sinal)
    
    vetor_sinal = np.append(vetor_sinal, algorithm)
    vetor_sinal = np.append(vetor_sinal, '2')
    vetor_sinal = np.append(vetor_sinal, user)
    
    data_string = pickle.dumps(vetor_sinal)
    send_message(sock, data_string)
    
def requisitar_imagem_usuario(sock, user):
    print("Requisitando Imagem Usuario")
    msg = ['1', user]
    data_string = pickle.dumps(msg)
    send_message(sock, data_string)
    data = receive_message(sock)
    vetor_imagens, count = handle_response(data)
    handle_image_output(vetor_imagens, count, user)
    
def encerrar_sessao(sock, user):
    msg = ['-1', user]
    data_string = pickle.dumps(msg)
    send_message(sock, data_string)

# Response Handler
def handle_response(data):
    outuput_message = pickle.loads(b"".join(data))
    
    count = outuput_message[len(outuput_message) - 1]
    
    if int(count) > 0:
        outuput_message = np.delete(outuput_message, [len(outuput_message) - 1])
        outuput_message = outuput_message.astype(np.float64)
        vetor_imagens = np.split(outuput_message, count)      
    else:
        vetor_imagens = []
    
    return vetor_imagens, count

def handle_image_output(vetor_imagens, count, user):
    i = 1
    print("Processando Imagens")
    for i in range(len(vetor_imagens)):
        vetor_imagens[i] = vetor_imagens[i].reshape(288, 432, 4)
        plt.imshow(vetor_imagens[i])
        plt.show()
        print("Imagem ", str(i))
        i = i + 1
    
    imagem_selecao = '-1'
    while imagem_selecao != '':
        imagem_selecao = input("Escolha uma ou mais imagens para salvar localmente (digite os numeros separados por ';' em caso de mais de uma)")
        imagem_index = imagem_selecao.split(";")
        for x in imagem_index:
            if int(x) > int(count) or int(x) < 0:
                imagem_selecao = '-1'
                break
        if imagem_selecao == '-1':
            print("Um ou mais numeros selecionados fora do range")
        else:
            for x in imagem_index:
                image = vetor_imagens[int(x) - 1]
                plt.imshow(image)
                path = path_image_output + user + "-" + str(x) + ".png"
                plt.savefig(path)
                print("Imagem " + x + " salva em: ", path)
            imagem_selecao = ''

def main():
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    
    user = input("Input User Name: \n")
    
    operation = ''
    while operation != '1' and operation != '2':
        operation = input("Escolha uma opção:\n1 - Recuperar Imagens do Usuario \n2 - Reconstruir Sinal \n")
        
        if operation == '1':
            requisitar_imagem_usuario(sock, user)
            
        elif operation == '2':
            
            vetor_option = ''
            while vetor_option != '1' and vetor_option != '2' and vetor_option != '3':
                
                vetor_option = input("Escolha uma opção:\n1 - Vetor Sinal 1 \n2 - Vetor Sinal 2 \n3 - Vetor Sinal 3 \n")
                
                if vetor_option == '1' or vetor_option == '2' or vetor_option == '3':
                    alg_option = ''
                    while alg_option != '1' and alg_option != '2':
                        alg_option = input("Escolha uma opção:\n1 - Fista \n2 - CGNE \n")
                        if(alg_option != '1' and alg_option != '2'):
                            print("Opção Invalida")
                
                if vetor_option == '1':
                    mandar_vetor_sinal(sock, path_vetor_sinal_1, alg_option, user)
                elif vetor_option == '2':
                    mandar_vetor_sinal(sock, path_vetor_sinal_2, alg_option, user)
                elif vetor_option == '3':
                    mandar_vetor_sinal(sock, path_vetor_sinal_3, alg_option, user)
                elif vetor_option == '4':
                    print("Encerrando Operação")
                    break
                else:
                    print("Opção Invalida!")
        else:
            print("Opção Invalida!")
        
    print("Encerrando Cliente")
    encerrar_sessao(sock, user)
    sock.close()
    
if __name__ == "__main__":
    main()