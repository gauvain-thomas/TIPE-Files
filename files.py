"""
Définit les classes relatives à la construction et la simultaion de files d'attente.
"""
from copy import deepcopy
import time
# from random import choose

class File:
    """
    Classe File :
    Définie par un buffer et une liste de serveurs

    K : Taille du buffer
    serveurs : Liste des serveurs

    buffer : Liste des clients
    liste_attentes : Le temps d'attente d'un client y est ajouté dès qu'il a été traité
    pertes : Nombre de pertes en terme de clients
    pertes_poids : Nombre de pertes en terme de clients
    t : Temps propre de la file
    A : Dictionnaire des arrivées à un certain temps, par exemple, A[3] renvoie une liste
        des clients arrivant à t=3
    couleur : Uniquement utilisé pour les représentations graphiques
    """

    def __init__(self, K, serveurs, couleur='red'):
        self.K = K
        self.serveurs = serveurs
        # self.nom = nom

        self.pertes = 0
        self.pertes_poids = 0
        self.buffer = []
        self.t = 0
        # self.A = deepcopy(A)
        # self.A_copy = deepcopy(A)
        self.liste_attentes = []
        self.couleur = couleur
        self.somme_clients = 0

    def reset(self):
        """Remise à zéro de la file, avec les mêmes valeurs initiales --- NON FONCTIONNEL"""
        for serveur in self.serveurs:
            serveur.reset()
        self.__init__(self.K, self.serveurs, self.couleur)

    def __str__(self):
        visuel = str(self.buffer) + '\n'
        for serveur in self.serveurs:
            visuel = visuel + str(serveur) + '\n'
        return visuel

    def iteration(self):
        """
        Appelle la foncton itération pour chacun des serveurs. Incrémente les
        temps d'attente des clients
        """
        arrivees = self.A.get(self.t)
        if arrivees != None:
            self.ajoute_liste_clients(arrivees)

        for serveur in self.serveurs:
            serveur.iteration(self)

        for client in self.buffer:
            client.inc_temps()

        self.t += 1
        self.somme_clients += self.nbr_clients()

    def simulation(self, affichage=False):
        """Itère la file jusqu'à que le buffer et les serveurs soient vides"""
        # print('Début de la simulation')
        # print(bool(self.file_vide()))
        # start = time.time()
        while not self.file_vide() or self.reste_clients():
            if affichage:
                print(self)
            self.iteration()
        # print("Simulation finie en : {} secondes".format(int(time.time()-start)))
        # print(self)
        # print('Fin de la simulation')

    def nbr_arrivees_moyen(self):
        """Renvoie le nombre de clients moyen dans le buffer depuis le début de la simulation"""
        return self.somme_clients/self.t

    def file_vide(self):
        """Renvoie True si le buffer est vide, ainsi que chacun des serveurs"""
        # i, n = 0, len(self.serveurs)
        est_vide = self.buffer_vide()
        # print(est_vide)
        if self.A:
            est_vide = est_vide and not self.reste_clients()
        for serveur in self.serveurs:
            if serveur.has_client:
                est_vide = False
                break
        return est_vide

    def reste_clients(self):
        return self.t < len(self.A)

    def nbr_clients(self):
        """Renvoie le nombre de clients dans le buffer"""
        return len(self.buffer)

    def sortir_client(self, t):
        self.liste_attentes.append(t)

    def buffer_vide(self):
        """Renvoie True si le buffer est vide"""
        return self.nbr_clients() == 0

    def buffer_plein(self):
        """Renvoie True si le buffer est complet"""
        return self.nbr_clients() == self.K

    def ajoute_client(self, client):
        """Ajoute un client au buffer"""
        if not self.buffer_plein():
            self.buffer.append(client)
        else:
            self.pertes += 1
            self.pertes_poids += client.poids

    def ajoute_liste_clients(self, lc):
        """Ajoute chacun des clients d'une liste au buffer"""
        for client in lc:
            self.ajoute_client(client)

    def pop_buff_min(self):
        index = 0
        poids_min = self.buffer[0].poids
        for i in range(len(self.buffer)):
            poids = self.buffer[i].poids
            if poids == 1:
                return self.buffer.pop(i)
            if poids < poids_min:
                index = i

        return self.buffer.pop(i)

    def pop_premier_petit(self, poids_max):
        n = self.nbr_clients()
        i = 0
        while i < n:
            if self.buffer[i].poids <= poids_max:
                return self.buffer.pop(i)
            i += 1
        return None

class Client:
    """Classe client : Contient un temps d'attente et un poids"""

    def __init__(self, poids=1):
        self.poids = poids
        self.temps_attente = 0

    def __repr__(self):
        """Représentation d'un client, entièrement défini par un temps et un poids"""
        return '<{} {}>'.format(self.temps_attente, self.poids)

    def inc_temps(self):
        """Incrémente le temps d'attente du client"""
        self.temps_attente += 1

    def retire_poids(self, p):
        self.poids -= p

    def poids_neg(self):
        return self.poids <= 0

# %% Serveurs
class Serveur:
    """
    Classe Serveur : Définie à partir d'une loi de sortie
    Contient un seul client à la fois
    """

    def __init__(self, S, nbr_sorties_moyen, loi):
        self.S = S
        self.has_client = False
        self.loi = loi
        self.nbr_sorties_moyen = nbr_sorties_moyen
        self.inactivite = 0

    def __str__(self):
        if self.has_client:
            return str(self.client_actuel)
        else:
            return 'Vide'

    def iteration(self, F):
        """
        Le poids à enlever est défini par la loi d'arrivée, et le serveur
        continue à récupérer des clients tant que il peut retirer du poids
        """
        self.poids_restant = self.S()
        while self.poids_restant > 0:
            if self.has_client:
                self.client_actuel.retire_poids(self.poids_restant)

                if self.client_actuel.poids_neg():
                    self.poids_restant = abs(self.client_actuel.poids)
                    F.sortir_client(self.client_actuel.temps_attente)
                    self.has_client = False
                else:
                    self.poids_restant = 0
            else:
                if not F.buffer_vide():
                    self.nouveau_client(F)
                else:
                    self.poids_restant = 0

        if self.has_client:
            self.client_actuel.inc_temps()
        else:
            self.inactivite += 1

    def reset(self):
        self.has_client = False

class Serveur_FIFO(Serveur):
    """Serveur First In First Out"""

    # def __init__(self, S):
    #     super().__init__(S)

    def __str__(self):
        return 'FIFO : ' + super().__str__()

    def iteration(self, F):
        if not (self.has_client or F.buffer_vide()):
            self.nouveau_client(F)

        super().iteration(F)


    def nouveau_client(self, F):
        self.client_actuel = F.buffer.pop(0)
        self.has_client = True

class Serveur_LIFO(Serveur):
    """Serveur Last In First Out"""

    # def __init__(self, S):
    #     super().__init__(S)

    def __str__(self):
        return 'LIFO : ' + super().__str__()

    def iteration(self, F):
        if not (self.has_client or F.buffer_vide()):
            self.nouveau_client(F)

        super().iteration(F)


    def nouveau_client(self, F):
        self.client_actuel = F.buffer.pop(-1)
        self.has_client = True

class Serveur_RR(Serveur):
    """
    Serveur Round Robin : Si un client est en traitement depuis plus de t_max,
    il est renvoyé dans le buffer et un autre client est récupéré.
    """

    def __init__(self, S, attente_max, nbr_sorties_moyen, loi):
        super().__init__(S, nbr_sorties_moyen, loi)
        self.attente_max = attente_max
        self.temps_attendu = 0

    def __str__(self):
        return 'RR : ' + super().__str__() + ' ' + str(self.temps_attendu)

    def iteration(self, F):
        super().iteration(F)
        if self.has_client:
            if self.temps_attendu >= self.attente_max:
                F.ajoute_client(self.client_actuel)
                self.has_client = False

        if not (self.has_client or F.buffer_vide()):
            self.nouveau_client(F)

        self.temps_attendu += 1

    def nouveau_client(self, F):
        self.client_actuel = F.buffer.pop(0)
        self.has_client = True
        self.temps_attendu = 0

class Serveur_Prio(Serveur):
    """Serveur Priorité : le serveur choisit un client dans le buffer dont le poids est minimal"""

    # def __init__(self, S):
    #     super().__init__(S)

    def __str__(self):
        return 'PRIO : ' + super().__str__()

    def iteration(self, F):
        if not (self.has_client or F.buffer_vide()):
            self.nouveau_client(F)

        super().iteration(F)

    def nouveau_client(self, F):
        self.client_actuel = F.pop_buff_min()
        self.has_client = True

class Serveur_FP(Serveur):
    """Serveur Priorité : le serveur choisit un client dans le buffer dont le poids est minimal"""

    def __init__(self, S, poids_max, nbr_sorties_moyen, loi):
        super().__init__(S, nbr_sorties_moyen, loi)
        self.poids_max = poids_max

    def __str__(self):
        return 'FP : ' + super().__str__()

    def iteration(self, F):
        if not (self.has_client or F.buffer_vide()):
            self.nouveau_client(F)

        super().iteration(F)

    def nouveau_client(self, F):
        self.client_actuel = F.pop_premier_petit(self.poids_max)
        if self.client_actuel:
            self.has_client = True
        else:
            self.poids_restant = 0
