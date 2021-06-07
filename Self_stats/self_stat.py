"""Création et analyse des résultats obtenus par mesure expérimentales sur une
file réelle : le self"""

import matplotlib.pyplot as plt
import numpy as np
import time
import pandas as pd
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from files import *
from fonctions import plot_taille_buffer


# %% Lecture fichiers

with open('entrees.txt', 'r') as f:
    entrees = f.readlines()

with open('milieu.txt', 'r') as f:
    milieu = f.readlines()

with open('sorties.txt', 'r') as f:
    sorties = f.readlines()

conv_time = lambda t:time.asctime(time.localtime(t))

# Début 'Tue May 25 18:21:40 2021'
debut = 1621959700
# Fin : 'Tue May 25 19:56:11 2021'
fin = 1621965371
# conv_time(1621965371)

entrees = [(int(i) - debut)/60 for i in entrees]
milieu = [(int(i) - debut)/60 for i in milieu]
sorties = [(int(i) - debut)/60 for i in sorties]

# df = pd.DataFrame(entrees)

# %% Attentes

attentes = [milieu[i] - entrees[i] for i in range(len(entrees))]
attentes2 = [sorties[i] - milieu[i] for i in range(len(entrees))]
attentes3 = [sorties[i] - entrees[i] for i in range(len(entrees))]

plt.plot(attentes)
plt.plot(attentes2)
plt.plot(attentes3)

print(np.average(attentes), np.median(attentes))
print(np.average(attentes2), np.median(attentes2))
print(np.average(attentes3), np.median(attentes3))


# %% Histogrammes

fig, axs = plt.subplots(3, 1, tight_layout=False, figsize=(10,6), sharex=True, sharey=True)

fig.suptitle('Histogrammes des arrivées / services de plateaux / fins de repas', fontsize=14)
pas = 1/6
bins = np.linspace(0, 90, 90/pas)
# axs[0].set_title('Entrées au self')
# axs[1].set_title('Services des plateaux')
# axs[2].set_title('Fins de repas')

axs[0].set(xlim=(0, 90), ylim=(0, 10))

hist_e = axs[0].hist(entrees, bins=bins, color='red', label='Entrée')
hist_m = axs[1].hist(milieu, bins=bins, color='green', label='Service plateau')
hist_s = axs[2].hist(sorties, bins=bins, color='blue', label='Sortie')

axs[0].legend(loc=1)
axs[1].legend(loc=1)
axs[2].legend(loc=1)

axs[2].set_xlabel('Temps écoulé (minutes)')
axs[1].set_ylabel('Nombre d\'arrivées')
plt.savefig('hist_arr.png', dpi=800)


# %% Lois de probabilités

fig, axs = plt.subplots(3, 1, tight_layout=False, figsize=(10,6), sharex=True, sharey=True)
axs[0].set(xlim=(0, 15))
b = range(15)
plt.xticks(range(15))

proba_e = axs[0].hist(hist_e[0], bins=b, color='red', density=True, rwidth=.75, label='Entrée')
proba_m = axs[1].hist(hist_m[0], bins=b, color='green', density=True, rwidth=.75, label='Service plateau')
proba_s = axs[2].hist(hist_s[0], bins=b, color='blue', density=True, rwidth=.75, label='Sortie')

axs[2].set_xlabel('Nombre d\'arrivées')
axs[1].set_ylabel('Probabilité')

axs[0].legend(loc=1)
axs[1].legend(loc=1)
axs[2].legend(loc=1)

moy_e = np.average(proba_e[1][:-1], weights=proba_e[0])
moy_m = np.average(proba_m[1][:-1], weights=proba_m[0])
moy_s = np.average(proba_s[1][:-1], weights=proba_s[0])

# plt.savefig('lois_sorties', dpi=800)
print(moy_e, moy_m, moy_s)

# %% Éliminer les zéros pour l'histogramme (arrivées vides)

fig, axs = plt.subplots(3, 1, tight_layout=False, figsize=(10,6), sharex=True, sharey=True)
axs[0].set(xlim=(1, 15))
plt.xticks(range(1,15))

proba_ez = axs[0].hist(hist_e[0][hist_e[0] > 0], bins=b, color='red', density=True, rwidth=.75, label='Entrée')
proba_mz = axs[1].hist(hist_m[0][hist_m[0] > 0], bins=b, color='green', density=True, rwidth=.75, label='Service plateau')
proba_sz = axs[2].hist(hist_s[0][hist_s[0] > 0], bins=b, color='blue', density=True, rwidth=.75, label='Sortie')

axs[2].set_xlabel('Nombre d\'arrivées')
axs[1].set_ylabel('Probabilité')

axs[0].legend(loc=1)
axs[1].legend(loc=1)
axs[2].legend(loc=1)

moy_ez = np.average(proba_ez[1][:-1], weights=proba_ez[0])
moy_mz = np.average(proba_mz[1][:-1], weights=proba_mz[0])
moy_sz = np.average(proba_sz[1][:-1], weights=proba_sz[0])

# plt.savefig('lois_sorties_zeroless', dpi=800)

print(moy_ez, moy_mz, moy_sz)


# %% Nombre de personnes dans la queue et dans le self

taille_f1 = [hist_e[0][:i+1].sum() - hist_m[0][:i+1].sum() for i in range(len(hist_e[0]))]
taille_f2 = [hist_m[0][:i+1].sum() - hist_s[0][:i+1].sum() for i in range(len(hist_e[0]))]
# taille_tot = [hist_e[0][:i+1].sum() - hist_s[0][:i+1].sum() for i in range(len(hist_e[0]))]
taille_tot = [i+j for i,j in zip(taille_f1, taille_f2)]

fig = plt.gcf()
fig.set_size_inches(10, 6)


# Plot

plt.plot(bins[:-1], taille_f1, label='Queue', color='red')
plt.plot(bins[:-1], taille_f2, label='Self', color = 'blue')
plt.plot(bins[:-1], taille_tot, label='Total', color='green')

plt.legend(loc=1)
# plt.savefig('self1.png', dpi=800)

# Convert data to csv
# df = pd.DataFrame(zip(bins[:-1], taille_f1, taille_f2), columns=['time', 'queue', 'self'])
# df.to_csv('data_self_30sec.csv')


# %% Simulation (Première modélisation non réaliste)

def loi_entree():
    return np.random.choice(proba_e[1][:-1], p=proba_e[0])

def loi_milieu():
    return np.random.choice(proba_m[1][:-1], p=proba_m[0])

def loi_sortie():
    return np.random.choice(proba_s[1][:-1], p=proba_s[0])

class Prefile(File):
    """Utilisé pour accoler des files en séries. Adjonction de dictionnaires
    utilisée par la suite préférable"""

    def __init__(self, K, serveurs, couleur, postFile):
        self.postFile = postFile
        self.postA = dict()
        super(Prefile, self).__init__(K, serveurs, couleur='red')

    def reset(self):
        """Remise à zéro de la file, avec les mêmes valeurs initiales --- NON FONCTIONNEL"""
        for serveur in self.serveurs:
            serveur.reset()
        self.__init__(self.K, self.serveurs, self.couleur, self.postFile)

    def sortir_client(self, t):
        c = Client()
        c.temps_attente = t
        # self.postFile.ajoute_client(c)
        if self.t not in self.postA:
            self.postA[self.t] = [c]
        else:
            self.postA[self.t].append(c)

        super().sortir_client(t)

class Serveur_self(Serveur_FIFO):
    """Utilisé pour que le service commence seulement après t_debut unités de temps"""

    def __init__(self, S, nbr_sorties_moyen, loi, t_debut):
        super(Serveur_self, self).__init__(S, nbr_sorties_moyen, loi)
        self.t_debut = t_debut

    def iteration(self, F):
        if not F.t < self.t_debut:
            super().iteration(F)

t_debut = np.where(hist_s[0] != 0)[0][0]

S1 = Serveur_FIFO(loi_milieu, moy_m, 'Queue')
S2 = Serveur_self(loi_sortie, moy_s, 'Self', t_debut=t_debut)

F2 = File(K=300, serveurs=[S2], couleur='blue')
F1 = Prefile(K=300, serveurs=[S1], couleur='green', postFile=F2)

entrees_int = [int(i) for i in entrees]

temp = hist_e[0]
A = dict()

for i, n in enumerate(temp):
    A[i] = [Client(1) for _ in range(int(n))]

# for  t, n in temp.items():
#     # print(t, n)
#     A[t] = [Client(1) for _ in range(n)]

fig, ax = plt.subplots(1)
fig.set_size_inches(10, 5)
fig.tight_layout()

#Première file

tailles = []
nom = F1.serveurs[0].loi

F1.A = A

while not F1.file_vide():
    tailles.append(F1.nbr_clients())
    F1.iteration()

ax.plot(tailles, label=nom, color=F1.couleur)
ax.set_title('Nombre de clients dans le buffer')
ax.legend(loc=2)


# % Deuxième file

tailles = []
nom = F2.serveurs[0].loi

F2.A = F1.postA

while not F2.file_vide():
    tailles.append(F2.nbr_clients())
    F2.iteration()

ax.plot(tailles, label=nom, color=F2.couleur)
ax.set_title('Nombre de clients dans le buffer')
ax.legend(loc=2)

# plot_taille_buffer([F2], F1.postA)
# plt.savefig('Simul_self4.png', dpi=800)
