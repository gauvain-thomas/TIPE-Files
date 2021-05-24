# %% Import

from files import *
from database import *
from statistics import mean
# from sklearn.linear_model import LinearRegression
import random as r
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3

# %% Connecteur SQLite3
# def sqlite_power(x,n):
#     return int(x)**n
#
con = sqlite3.connect('resultats.db')
# con.create_function("power", 2, sqlite_power)
# %% Fonctions de création de dictionnaires d'arrivées

def cree_arrivee(d, f, loi_nbr_clients, loi_poids):
    """
    Genere des arrivees de clients suivant des lois données.
    loi_nbr_clients : lambda, n -> Renvoie une liste de n nombres de clients (moyenne lambda)
    loi_poids : lambda -> Renvoie un poids (moyenne lambda)
    """
    arr_par_inst = loi_nbr_clients(f-d)
    A = dict()
    for i in range(f-d):
        if arr_par_inst[i] != 0:
            A[i+d] = []
            for j in range(arr_par_inst[i]):
                A[i+d].append(Client(poids=loi_poids()))
    return A

def poisson(n, lam, poids_moy):
    """Genere des arrivees de λ clients par unite de temps en moyenne, suivant une loi de poisson."""
    loi_arr = lambda n: np.random.poisson(lam, n)
    loi_p = lambda: np.random.poisson(poids_moy)
    return cree_arrivee(0, n, loi_arr, loi_p)

def echelon(d, f, p, n):
    """Crée un échellon, d : début, f : fin, p : poids, n : nombre de clients"""
    loi_arr = lambda i: [n for _ in range(i)]
    loi_p = lambda: p
    return cree_arrivee(d, f, loi_arr, loi_p)

def fusionne_arrivees(A, B):
    """Renvoie l'arrivée formée des deux dictionnaires d'arrivés fusionnés"""
    C = deepcopy(A)
    for b in B:
        if b in A:
            for client in B[b]:
                C[b].append(client)
        else:
            C[b] = B[b]
    return C

def fusionne_liste(liste):
    """Fusionne une liste de dictionnaire d'arrivées récursivement"""
    if len(liste) == 1:
        return liste[0]
    else:
        return fusionne_arrivees(liste.pop(0), fusionne_liste(liste))

# %% Différents serveurs

# Poids moyen enlevé par unité de temps
λ = 10
# n = 5
# np.random.binomial(n, λ/n, 10)
FIFO_d = Serveur_FIFO(lambda:λ, λ, 'FIFO_d')
FIFO_p = Serveur_FIFO(lambda: np.random.poisson(λ), λ, 'FIFO_p')
FIFO_p2 = Serveur_FIFO(lambda: np.random.poisson(λ), λ, 'FIFO_p2')
FIFO_p3 = Serveur_FIFO(lambda: np.random.poisson(λ), λ, 'FIFO_p3')
# FIFO_b = Serveur_FIFO(lambda: np.random.binomial(n, λ/n), λ, FIFO_b)
LIFO_p = Serveur_LIFO(lambda: np.random.poisson(λ), λ, 'LIFO_p')
LIFO_d = Serveur_LIFO(lambda:λ, λ, 'LIFO_d')
RR_d = Serveur_RR(lambda:λ, λ//10, λ, 'RR_d')
RR_p = Serveur_RR(lambda: np.random.poisson(λ), λ//10, λ, 'RR_p')
PRIO_d = Serveur_Prio(lambda:λ, λ, 'PRIO_d')
PRIO_p = Serveur_Prio(lambda: np.random.poisson(λ), λ, 'PRIO_p')
PRIO_p2 = Serveur_Prio(lambda: np.random.poisson(λ), λ, 'PRIO_p2')
PRIO_p3 = Serveur_Prio(lambda: np.random.poisson(λ), λ, 'PRIO_p3')
FP = Serveur_FP(lambda: np.random.poisson(λ), λ//3,λ, 'FP_p')
FPd = Serveur_FP(lambda:λ, λ//3,λ, 'FP_d')

# %% Différentes files d'exemple

F1 = File(K=200, serveurs=[FIFO_p], couleur='red')
F2 = File(K=200, serveurs=[PRIO_p], couleur='blue')
F1d = File(K=200, serveurs=[FIFO_d], couleur='red')
F2d = File(K=200, serveurs=[PRIO_d], couleur='blue')
F3 = File(K=200, serveurs=[FIFO_p, FIFO_p2, FIFO_p3], couleur='red')
F4 = File(K=200, serveurs=[FIFO_p, FIFO_p2, FIFO_p3], couleur='red')
F_FP = File(K=200, serveurs=[FP, FIFO_p, FIFO_p2], couleur='orange')
# F_FP = File(K=200, serveurs=[FP, FIFO_p, FIFO_p2], couleur='orange')

# %% Différentes arrivées
n = 10**4
A1 = poisson(n, 10, 1)
A2 = poisson(n, 5, 2)
A3 = poisson(n, 2, 5)
A4 = poisson(n, 1, 10)
A5 = echelon(100, 110, 2, 3)
A6 = poisson(n, 9, 1)
A7 = poisson(n,np.sqrt(10) ,np.sqrt(10))
A8 = poisson(n, 3, 3)
A9 = poisson(n, 9, 1)

# %%%% Affichages de différents Résultats
# %% Remplissage du buffer en fonction du temps
def plot_taille_buffer(F_liste, A, figname=None):
    """Prend une liste de files en entrée ainsi qu'une arrivée et simuleces files
    avec la même arrivée"""
    # Plot
    fig, axs = plt.subplots(2)
    ax1, ax2 = axs
    fig.set_size_inches(10, 5)
    ax2.grid(True)
    fig.tight_layout()

    for F in F_liste:
        tailles = []
        pertes = []
        nom = str(F.serveurs[0])[:4]

        F.reset()
        F.A = deepcopy(A)

        start = time.time()
        while not F.file_vide():
            tailles.append(F.nbr_clients())
            pertes.append(F.pertes_poids)
            F.iteration()

        # print("Simulation finie en : {} secondes".format(time.time()-start))

        T = [i for i in range(len(tailles))]
        # ax1.hlines(F.K, 0, n, color='grey', alpha = .5)

        # plt.subplot(211)
        ax1.plot(tailles, label='Buffer {}'.format(nom), color=F.couleur)
        ax1.set_title('Nombre de clients dans le buffer')
        ax1.legend(loc=2)
        # ax1.set_xlabel('t')

        # plt.subplot(212)
        ax2.plot(pertes, label='Pertes pondérées {}'.format(nom), color=F.couleur)
        ax2.set_title('Pertes')
        ax2.legend(loc=2)
        # ax2.set_xlabel('t')

plot_taille_buffer([F1, F2], A2)
plot_taille_buffer([F1, F2], A4)

# %% Caisse moins de dix articles
plot_taille_buffer([F3, F_FP], fusionne_liste([A9, A4, A2]))
print(np.average(F3.liste_attentes), np.average(F_FP.liste_attentes))
# for serveur in F_FP.serveurs:
#     print(serveur, serveur.inactivite//1000)
# plot_taille_buffer([F4, F_FP], fusionne_liste([A1, A6, A4]))
# plot_taille_buffer([F3, F_FP], fusionne_liste([A1, A6, A4]))

# %% Little
def verifie_Little():
    query ='SELECT attente_moyen as Attente_moyenne, nbr_clients_moyen*poids_moyen/10 as Nombre_sortie_normalisé FROM Simulation\
            JOIN Files ON Files.id = file_id\
            JOIN Arrivees ON Arrivees.id = id_arrivee'
    little_df = pd.read_sql(sql=query, con=con)
    plot = little_df.plot.scatter(x=0, y=1, color='blue', figsize=(10,6), s=5, title='Vérification de la loi de Little')
    # little_df.plot(x=0, y=1)
    fig = plot.get_figure()
    # fig.savefig("Verif_Little.png")
    x = little_df['Attente_moyenne'].to_numpy()
    y = little_df['Nombre_sortie_normalisé'].to_numpy()

verifie_Little()

# %% Pertes en fonction de la taille du buffer
def plot_pertes_buffer(lam=9, Kmax=50, ecart=10**-3):
    query ='SELECT taille_buffer as K, AVG(pertes_poids)/10000 as Pertes, nbr_arrivees_moyen*poids_moyen as Lambda, COUNT(*) as Nombre_simulés\
            FROM Simulation\
            JOIN Files ON Files.id = file_id\
            JOIN Arrivees ON Files.id_arrivee = Arrivees.id\
            JOIN Serveurs ON serveur_1_id = Serveurs.id\
            WHERE ABS(Lambda - {}) <= {} AND 0<K AND taille_buffer<{}\
            GROUP BY taille_buffer\
            HAVING pertes != 0\
            ORDER BY K'.format(lam, ecart, Kmax+1)
    df = pd.read_sql(sql=query, con=con)
    x = df['K'].to_numpy()
    y = df['Pertes'].to_numpy()
    def f(K):
        rho = lam/10
        return ((1-rho/10)/(1-rho**(K+1)))*rho**K
    # print(f(0), f(1), f(2), f(3), f(4))
    # a = y[0+4]/f(1+4)
    indice_repere = 5
    # print(len(y))
    a = y[0+indice_repere]/f(1+indice_repere)
    th = [f(K)*a for K in x]
    df['Théorique'] = th
    # print(df)
    # df.plot(x=0, y='Pertes', color='blue')
    df.plot(x='K', y=['Pertes','Théorique'], color=['blue', 'tab:cyan'], figsize=(10,6), title='Pertes en fonction de la taille du buffer')
    # return df.head()
    # return df

plot_pertes_buffer(9, 50, 0)

# %% Temps d'attente en fonction de la taille du buffer

def plot_attentes_buffer(lam=9, Kmax=5000):
    query ='SELECT taille_buffer as K, AVG(attente_moyen) as Attente_moyenne, nbr_arrivees_moyen*poids_moyen as Lambda, COUNT(*) as Nombre_simulés\
            FROM Simulation\
            JOIN Files ON Files.id = file_id\
            JOIN Arrivees ON Files.id_arrivee = Arrivees.id\
            JOIN Serveurs ON serveur_1_id = Serveurs.id\
            WHERE Lambda = {} AND 0<K AND taille_buffer<{}\
            GROUP BY taille_buffer\
            ORDER BY K'
    df = pd.read_sql(sql=query.format(lam, Kmax), con=con)
    df.plot.scatter(x=0, y=1, color='purple', label='λ = {}'.format(lam), figsize=(10,6))
    # df.plot(x='K', y=['Attente_moyenne'], color=['blue'])
    # print(df.head(1))
    # print(df.tail(1))

plot_attentes_buffer(9,100)

plot_attentes_buffer(10,100)
# %%
def plot_attentes_buffes_liste(lamliste, Kmax=5000):
    query ='SELECT taille_buffer as K, AVG(attente_moyen) as Attente_moyenne, nbr_arrivees_moyen*poids_moyen as Lambda, COUNT(*) as Nombre_simulés\
            FROM Simulation\
            JOIN Files ON Files.id = file_id\
            JOIN Arrivees ON Files.id_arrivee = Arrivees.id\
            JOIN Serveurs ON serveur_1_id = Serveurs.id\
            WHERE Lambda = {} AND 0<K AND taille_buffer<{}\
            GROUP BY taille_buffer\
            ORDER BY K'

    for i in lamliste:
        dfi = pd.read_sql(sql=query.format(i, Kmax), con=con)
        x = dfi['K'].to_numpy()
        y = dfi['Attente_moyenne'].to_numpy()
        plt.scatter(x, y, label='λ = {}'.format(i), s=15)
    plt.legend(loc=0)
    # print(df.tail(1))

plot_attentes_buffes_liste([7,8,9],100)

# %% Remplissage en fonction du taux d'arrivée

def plot_remplissage_lambda():
    query ='SELECT nbr_arrivees_moyen*poids_moyen as Lambda, nbr_clients_moyen as N, COUNT(*) as Nombre_simulés\
            FROM Simulation\
            JOIN Files ON Files.id = file_id\
            JOIN Arrivees ON Files.id_arrivee = Arrivees.id\
            JOIN Serveurs ON serveur_1_id = Serveurs.id\
            GROUP BY Lambda\
            HAVING Nombre_simulés > 50\
            ORDER BY Lambda'
    df = pd.read_sql(sql=query, con=con)
    df.plot.scatter(x=0, y=1, color='green', figsize=(10,6))
    # return df.tail()
    # df.plot(x='K', y=['Attente_moyenne'], color=['blue'])
    # print(df.head(1))
    # print(df.tail(1))

plot_remplissage_lambda()

# %%
# L =
# type(val[0])
#
# L = []
# for i in val:
#     L.append(i)
#
#
# val = np.arange(1,12,.1)
# L = [(i,j) for i in val for j in val if i*j<=12]
# L
#
# np.floor(1.5)
# i, j = np.floor(5*np.random.rand() + 1), np.floor(5*np.random.rand() + 1)
# print(i, j, i*j)
# np.random.choice(L)
