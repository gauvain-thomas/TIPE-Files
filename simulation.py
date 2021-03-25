from main import *

i=0
for K in range(1,50):
    for l in range(1,10):
        for p in range(1,10):
            if 7<=l*p<=10:
                i+=1
                A = poisson(n=10**4, lam=l, poids_moy=p)
                print('{}/{} : '.format(i, 539))
                simul_poisson(nbr_iter=20, nbr_arr_moy=l, poids_moy=p, K=K)
