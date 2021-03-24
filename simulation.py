from main import *

c=0
for K in range(1,25):
    for l in range(1,10):
        for p in range(1,10):
            if l*p==9:
                c += 1

i=0
for K in range(50,75):
    for l in range(1,10):
        for p in range(1,10):
            if 7<=l*p<=10:
                i+=1
                A = poisson(n=10**4, lam=l, poids_moy=p)
                print('{}/{} : '.format(i, c))
                simul_poisson(nbr_iter=10, nbr_arr_moy=l, poids_moy=p, K=K)
