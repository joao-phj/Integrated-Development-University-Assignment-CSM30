import numpy as np
from numpy import linalg as LA
from matplotlib import pyplot as plt

DEBUG_MODE = True

def GanhoDeSinal (G):
  sinal = G.reshape(64,794)
  nrows, ncols = sinal.shape
  for i in range(nrows):
    for j in range(ncols):
      y = 100 + (1/20)*(i+1)*np.sqrt(i+1)
      sinal[i][j] = sinal[i][j] * y
  tamanho = nrows * ncols
  out = sinal.reshape(tamanho)
  return out

"""
O G é quadrado, tem 64 colunas, cada coluna é um sensor, com 794 amostras por sensor

"""
def CoeficienteDeRegularizacao (H, G):
  l = np.absolute(H.transpose() @ G)
  l = l.max()
  l = l * 0.10
  print(f'Coeficiente de Regularização: {l}')
  return l

def FatorDeReducao(H):
  c = H.transpose() @ H
  c = LA.norm(c)
  print(f'Fator de Redução: {c}')
  return c


def CGNE (H, G):
  print("Inicio CGNE")
  f = np.zeros(3600)
  r = G - (H @ f)
  p = H.transpose() @ r

  erro = 1
  while(erro > 0.0001):
  #for i in range(10):
    a = (r.transpose() @ r) / (p.transpose() @ p)
    f = f + (a * p)
    rplus = r - (a * H @ p)
    B = (rplus.transpose() @ rplus) / (r.transpose() @ r)
    p = (H.transpose() @ rplus) + (B * p)
    # Calculo do erro < 0,0001
    erro = np.absolute(LA.norm(rplus) - LA.norm(r))
    if(DEBUG_MODE):
      image = f.reshape(60,60)
      image = np.absolute(image)
      image = image.transpose()
      plt.imshow(image)
      plt.show()
    print(f'Erro CGNE: {erro}')
    r = rplus

  # transformando o array numa matrix 60x60 e aplicando valores absolutos
  image = f.reshape(60,60)
  image = np.absolute(image)
  image = image.transpose()
  print("Fim CGNE")
  return image

def S(fator, vetor):
  # TODO veriricar o que falta aqui
  resultado = vetor
  for i in range(vetor.size):
    if np.absolute(vetor[i]) <= fator:
      resultado[i] = 0
    elif vetor[i] > 0:
      resultado[i] = vetor[i] - fator
    else:
      resultado[i] = vetor[i] + fator
  return resultado

def FISTA (H, G): # l = lambda,
  print("Inicio FISTA")
  f = np.zeros(3600)
  y = f 
  a = 1 # Qual o tamanho do vetor
  l = CoeficienteDeRegularizacao(H, G)
  c = FatorDeReducao(H)
  #calculando labda/c. Estou chamando de fator
  fator = l/c
  vetor = f
  #calculando o vetor
  for i in range(5):
    print(f'Iteração FISTA: {i}')
    vetor = y + ((1/c) * H.transpose()) @ (G - H @ y)
    f_plus = S(fator, vetor)
    a_plus = (1 + np.sqrt(1 + 4*a**2))/2
    y_plus = f_plus + ((a - 1)/a_plus)*(f_plus - f)
    f = f_plus
    a = a_plus
    y = y_plus
    # TODO Como calcular o erro?
  
  image = f.reshape(60,60)
  image = np.absolute(image)
  image = image.transpose()
  print("Fim FISTA")
  return image

def main ():

  print("Começou")

  print("Loading G como string")
  G = np.genfromtxt(r'C:\Users\renat\OneDrive\Área de Trabalho\dis-csm30\g-3.txt',dtype=np.str,delimiter='\t')

  print("Tratando G")
  G = np.char.replace(G, ',', '.')
  G = G.astype('float64')
  G = GanhoDeSinal(G)

  print("Loading H")
  H = np.genfromtxt(r'C:\Users\renat\OneDrive\Área de Trabalho\dis-csm30\H-1.txt',delimiter=',')

  image = CGNE(H, G)
  plt.imshow(image)
  plt.show()

  image_fista = FISTA(H, G)
  plt.imshow(image_fista)
  plt.show()

  print("Acabou")


if __name__ == '__main__':
    main ()