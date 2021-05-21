from main import *

i=0
val = np.arange(1,12,.1)
L = [(i,j) for i in val for j in val if i*j<=12]

start = time.time()
tmax = 60*1
n = len(L)
serveurs = [FIFO_p, FIFO_d, PRIO_p, PRIO_d, RR_p]
ns = len(serveurs)

while time.time() - start < tmax:
    r = np.random.randint(n)
    l, p = L[r][0], L[r][1]
    i +=1
    A = poisson(n=10**4, lam=l, poids_moy=p)
    K = np.random.randint(1,100)
    print('{} : l={}, p={}, lp={}, K={} '.format(i, str(l)[:3], str(p)[:3], str(l*p)[:3], K))
    simul_poisson(nbr_iter=50, nbr_arr_moy=l, poids_moy=p, K=K, serveur=serveurs[np.random.randint(ns)])
