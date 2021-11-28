import time
import numpy as np
import pandas as pd
from io import StringIO

path_matriz_modelo = "C:\\Users\\joaop\\Desktop\\trabaio\\input\\H-1.csv"
path_vetor_sinal = "C:\\Users\\joaop\Desktop\\trabaio\\input\\g-1.txt"

def convert_to_csv():
    print("Read File Start - %s" % (time.time() - start_time))
    read_file = pd.read_csv(path_matriz_modelo)
    print("Read File End - %s" % (time.time() - start_time))

    print("Convert File Start -  %s" % (time.time() - start_time))
    read_file.to_csv("C:\\Users\\joaop\\Desktop\\trabaio\\output\\H-1.csv", index=None)
    print("Convert File End -  %s" % (time.time() - start_time))
    
    print("Execution End = %s" % (time.time() - start_time))

# CGNE
def calc_fator_reducao(matriz_modelo):
    return linalg.norm(np.matmul(matriz_modelo.transpose(), matriz_modelo))

def calc_coef_regularizacao(matriz_modelo):
    return True

def calc_erro():
    return True

def calc_ganho_sinal():
    return True

def main():
    start_time = time.time()

    matriz_modelo = np.loadtxt(path_matriz_modelo, dtype=np.float32, delimiter=",")
    # vetor_sinal = np.genfromtxt(path_vetor_sinal)

    print("Execution End = %s" % (time.time() - start_time))

    return

if __name__ == "__main__":
    main()