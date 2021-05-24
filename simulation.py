from main import *

# def simul_poisson(nbr_iter, nbr_arr_moy, poids_moy, K, serveur):
#     n = 10**4
#     data = {
#     'file_id' : [],
#     'duree' : [],
#     'pertes_nombre' : [],
#     'pertes_poids' : [],
#     'attente_moyen' : [],
#     'nbr_clients_moyen' : []
#     }
#     start = time.time()
#     F = File(K=K, serveurs=[serveur], couleur='red')
#     for i in range(nbr_iter):
#         arr = nbr_arr_moy
#         pmoy = poids_moy
#         F.reset()
#         A = poisson(n=n, lam=arr, poids_moy=pmoy)
#         F.A = deepcopy(A)
#         F.simulation()
#         # t_moy = taille_moyenne(F)
#         t_moy = F.nbr_arrivees_moyen()
#
#
#         data['file_id'].append(index_file(F))
#         data['duree'].append(n)
#         data['pertes_nombre'].append(F.pertes)
#         data['pertes_poids'].append(F.pertes_poids)
#         data['attente_moyen'].append(mean(F.liste_attentes))
#         data['nbr_clients_moyen'].append(t_moy)
#
#         # data = {
#         # 'file_id' : index_file(F),
#         # 'duree' : n,
#         # 'pertes_nombre' : F.pertes,
#         # 'pertes_poids' : F.pertes_poids,
#         # 'attente_moyen' : mean(F.liste_attentes)
#         # }
#     index = [i for i in range(len(data['duree']))]
#     df_exp = pd.DataFrame(data, index=index)
#     # df_exp
#     df_exp.to_sql('Simulation', con, if_exists='append', index=False)
#     print("Simulation finie en : {} secondes".format(time.time()-start))
#     # print(df_exp.mean())



val = np.arange(1,12,.1)
L = [(i,j) for i in val for j in val if i*j<=12]

start = time.time()
tmax = 60*1
n = len(L)
serveurs = [FIFO_p, FIFO_d, PRIO_p, PRIO_d, RR_p]
ns = len(serveurs)

def simulation():
    i=0
    while time.time() - start < tmax:
        r = np.random.randint(n)
        l, p = L[r]
        i +=1
        A = poisson(n=10**4, lam=l, poids_moy=p)
        K = np.random.randint(1,100)
        print('{} : l={}, p={}, lp={}, K={} '.format(i, str(l)[:3], str(p)[:3], str(l*p)[:3], K))
        simul_poisson(nbr_iter=50, nbr_arr_moy=l, poids_moy=p, K=K, serveurs=[serveurs[np.random.randint(ns)]])

def simulationM10():
    i=0
    while time.time() - start < tmax:
        r = np.random.randint(n)
        l, p = L[r][0], L[r][1]
        K = np.random.randint(1,200)
        A = poisson(n=10**4, lam=l, poids_moy=p)
        i +=1
        print('{} : l={}, p={}, lp={}, K={} '.format(i, str(l)[:3], str(p)[:3], str(l*p)[:3], K))
        simul_poisson(nbr_iter=50, nbr_arr_moy=l, poids_moy=p, K=K, serveurs=[serveurs[np.random.randint(ns)]])

FIFO_ps = Serveur_FIFO(lambda: np.random.poisson(λ), λ, 'FIFO_p')
FIFO_p2s = Serveur_FIFO(lambda: np.random.poisson(λ), λ, 'FIFO_p2')
FPs = Serveur_FP(lambda: np.random.poisson(λ), λ//3,λ, 'FP_p')
# F_FPs = File(K=200, serveurs=[FPs, FIFO_ps], couleur='orange')
# F1s = File(K=200, serveurs=[FIFO_ps, FIFO_p2s], couleur='red')

# simul_poisson(50, 3, 3, 200, [FPs, FIFO_ps])
# simul_poisson(50, 3, 3, 200, [FIFO_ps, FIFO_p2s])


# simulation()
