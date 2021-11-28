import os
import sys
import glob
import time
import socket
import math
import pickle
import numpy as np
import pandas as pd
from numpy import save
from numpy import load
from numpy import linalg as LA
from io import StringIO
from matplotlib import colors
from matplotlib import pyplot as plt
from matplotlib import image as mpimg
from _thread import *
import threading

# Server Const
# Input
path_matriz_modelo_npy = "C:\\Users\\joaop\\Desktop\\trabaio\\Server\\input\\H-1.npy"
path_matriz_modelo_csv = "C:\\Users\\joaop\\Desktop\\trabaio\\Server\\input\\H-1.csv"

# Output
path_image_output = "C:\\Users\\joaop\\Desktop\\trabaio\\Server\\output\\"

# Address
server_address = ('localhost', 10000)
byte_threshold = 500

# Thread
print_lock = threading.Lock()

def threaded(connection, matriz_modelo):
    
    last_signal = 0
    operation = ''
    data = []
    while True:
        packet = connection.recv(4096)
        if packet:
            data.append(packet)
            if sys.getsizeof(packet) < last_signal or sys.getsizeof(packet) < byte_threshold:
                print_lock.release()
                break
            last_signal = sys.getsizeof(packet)
        else:
            print_lock.release()
            break

    user, operation, algorithm, vetor_sinal = handle_request(data)

    if operation == '1':
        print("Operação Selecionada Enviar Mensagens")
        image_array, count = get_user_images(user)
        enviar_imagens(image_array, count, connection)
    elif operation == '2':
        if algorithm == '1':
            print("Reconstrução FISTA")
            image = fista(matriz_modelo, vetor_sinal)
        elif algorithm == '2':
            print("Reconstrução CGNE")
            image = cgne(matriz_modelo, vetor_sinal)
        else:
            print("Operação Invalida")
        handle_image(image, path_image_output, user)
    elif operation == '-1':
        print("Terminando sessão")
    else:
        print("Operação Invalida")
        
        
def get_next_file_name_index(user):
    file_name_array = glob.glob(path_image_output + user + "-*")
    highest_index = 0
    for x in file_name_array:
        file_name = x.split("\\")
        index = file_name[len(file_name) - 1].split(".")[0].split("-")[1]
        if int(index) > int(highest_index):
            highest_index = index
    
    return int(highest_index) + 1

def get_user_images(user):
    file_name_array = glob.glob(path_image_output + user + "-*")
    
    count = 0
    image_array = []
    for file_name in file_name_array:
        data = mpimg.imread(file_name)
        image_array = np.append(image_array, data)
        count = count + 1
        
    return image_array, count

def handle_request(data):
    outuput_message = pickle.loads(b"".join(data))
    
    user = outuput_message[len(outuput_message) - 1]
    operation = outuput_message[len(outuput_message) - 2]
    
    if operation == '2':
        algorithm = outuput_message[len(outuput_message) - 3]
        vetor_sinal = np.delete(outuput_message, [len(outuput_message) - 1, len(outuput_message) - 2, len(outuput_message) - 3])
        vetor_sinal = vetor_sinal.astype(np.float64)
    else:
        algorithm = ''
        vetor_sinal = []
    
    return user, operation, algorithm, vetor_sinal

def enviar_imagens(image_array, count, connection):
    if count > 0:
        image_array = np.append(image_array, count)
    else:
        image_array = np.append(image_array, '-1')
        
    data_string = pickle.dumps(image_array)
    send_message(connection, data_string)

# Server
def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def start_server(sock):
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(5)
    
def send_message(connection, msg):
    totalsent = 0
    while totalsent < sys.getsizeof(msg):
        sent = connection.send(msg[totalsent:])
        if sent == 0:
            break
        totalsent = totalsent + sent

def receive_message(connection, client_address):
    print('connection from', client_address)
    data = []
    while True:
        packet = connection.recv(4096)
        if packet:
            data.append(packet)
        else:
            print('no more data from ', client_address)
            break
    return data

# File Handling
def load_matriz_modelo():
    value = ""
    
    while value != "1" and value != "2":
    
        value = input("Choose an option:\n1 - Read from CSV \n2 - Load from NPY \n3 - Exit \n")
        
        if value == "1":
            start_time = time.time()
            print("Carregando Matriz Modelo csv\n")
            matriz_modelo = np.loadtxt(path_matriz_modelo_csv, delimiter=",", dtype=np.float64)
            print(matriz_modelo.shape)
            print("Matriz Modelo Carregada (t = %s segundos)" % (time.time() - start_time))
        elif value == "2":
            start_time = time.time()
            print("Carregando Matriz Modelo npy\n")
            matriz_modelo = np.load(path_matriz_modelo_npy).reshape((50816, 3600))
            print(matriz_modelo.shape)
            print("Matriz Modelo Carregada (t = %s segundos)" % (time.time() - start_time))
        elif value == "3":
            matriz_modelo = []
        else:
            print("Invalid Option\n\n")
    
    return matriz_modelo

def handle_image(image, directory, user):
    print("Processando Imagem")
    image = np.absolute(image)
    image = image.transpose()
    plt.imshow(image, cmap='gray', norm=plt.Normalize(image.min(), image.max()))
    path = directory + user + "-" + str(get_next_file_name_index(user)) + ".png"
    plt.savefig(path)
    print("Imagem salva em: ", path)

# CGNE
def cgne(h, g):
    print("Iniciando CGNE\n")

    f = np.zeros(3600)
    r = g - (h @ f)
    p = h.transpose() @ r
    erro = 1000
    i = 1
    
    start_time = time.time()
    print("Variaveis Incializadas")
    print("Inciando Primeira Iteração")
    
    menor_erro = 1e+20
    
    while erro > 1e-4:
        iteration_start_time = time.time()
        a = (r.transpose() @ r) / (p.transpose() @ p)
        
        f1 = f + (a * p)
        r1 = r - (a * (h @ p))
        
        b = (r1.transpose() @ r1) / (r.transpose() @ r)
        
        p1 = h.transpose() @ r1 + b * p
        
        erro = np.abs(LA.norm(r1, 2) - LA.norm(r, 2))
        if erro < menor_erro:
            menor_erro = erro
        
        print("Iteração: ", i)
        print("Erro: ", erro)
        print("Tempo Iteração: %s segundos" % (time.time() - iteration_start_time))
        print("Tempo Total: %s segundos\n" % (time.time() - start_time))
        
        i = i + 1
        r = r1
        f = f1
        p = p1
        
#         image = f.reshape(60,60)
#         image = np.absolute(image)
#         image = image.transpose()
#         plt.imshow(image, cmap='gray', norm=plt.Normalize(image.min(), image.max()))
#         path = path_image_output + "CGNE_" + "c_ganho_sinal" + "iter_" + str(i) + ".png"
#         plt.savefig(path)
        
        if i == 25:
            break
    
    print("Menor Erro: ", menor_erro)
    return f.reshape(60,60)

def calc_erro(r, r1):
    return np.absolute(LA.norm(r1, 2) - LA.norm(r, 2))

# FISTA
def fista(h, g):
    f = np.zeros(3600)
    y = f
    a = 1
    
    c = calc_fator_reducao(h)
    l = calc_coef_regularizacao(h, g)
    
    fator = l/c
    
    start_time = time.time()
    
    for i in range(25):
        iteration_start_time = time.time()
        vetor = y + (1/c) * h.transpose() @ (g - (h @ y))
        f1 = calc_s(fator, vetor)
        a1 = (1 + math.sqrt(1 + (4 * (a**2)))) / 2  
        y1 = f1 + (((a - 1) / a1) * (f1 - f)) 
        
        f = f1
        a = a1
        y = y1
        
#         image = f.reshape(60,60)
#         image = np.absolute(image)
#         image = image.transpose()
#         plt.imshow(image, cmap='gray')
#         path = path_image_output + "Fista_" + "c_ganho_sinal" + "iter_" + str(i) + ".png"
#         plt.savefig(path)
        
        print("Iteração: %s" % i)
        print("Tempo Iteração: %s segundos" % (time.time() - iteration_start_time))
        print("Tempo Total: %s segundos\n" % (time.time() - start_time))
    
    return f.reshape(60,60)

def calc_s(fator, vetor):
    return np.sign(vetor) * np.maximum(np.abs(vetor) - fator, 0.)
#     resultado = vetor
#     for i in range(vetor.size):
#         if(vetor[i] >= 0):
#             if(vetor[i] - fator <= 0):
#                 resultado[i] = 0
#             else:
#                 resultado[i] = vetor[i] - fator
#         elif(vetor[i] <  0):
#             if(vetor[i] + fator > 0):
#                 resultado[i] = 0
#             else:
#                 resultado[i] = vetor[i] + fator
#     return resultado

                  
def calc_fator_reducao(h):
    return LA.norm(h.transpose() @ h)

def calc_coef_regularizacao(h, g):
    return np.max(np.absolute(h.transpose() @ g)) * 0.10

def main():
    
    matriz_modelo = load_matriz_modelo()
    sock = create_socket()
    start_server(sock)
    
    while True:
        print('Esperando Conexao')
        connection, client_address = sock.accept()

        print_lock.acquire()
        print('Conectado em', client_address)
  
        # Start a new thredata:
        start_new_thread(threaded, (connection, matriz_modelo))

        
    connection.close()
            
if __name__ == "__main__":
    main()