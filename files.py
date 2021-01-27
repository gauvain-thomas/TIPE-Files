class File:
    """
    Classe File :
    Définie par un buffer et une liste de serveurs

    K : Taille du buffer
    serveurs : Liste des serveurs

    buffer : Liste des clients
    liste_attentes : Le temps d'attente d'un client y est ajouté dès qu'il a été traité
    pertes : nombre de pertes
    """

    def __init__(self, K, serveurs):
        self.K = K
        self.serveurs = serveurs

        self.pertes = 0
        self.buffer = []

        self.liste_attentes = []

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
        for serveur in self.serveurs:
            serveur.iteration(self)

        for client in self.buffer:
            client.inc_temps()

    def simulation(self, affichage=False):
        """Itère la file jusqu'à que le buffer et les serveurs soient vides"""
        # print('Début de la simulation')
        while not self.file_vide():
            if affichage:
                print(self)
            self.iteration()
        # print(self)
        # print('Fin de la simulation')

    def file_vide(self):
        """Renvoie True si le buffer est vide, ainsi que chacun des serveurs"""
        # i, n = 0, len(self.serveurs)
        est_vide = self.buffer_vide()
        for serveur in self.serveurs:
            if serveur.has_client:
                est_vide = False
                break
        return est_vide

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

    def ajoute_liste_clients(self, lc):
        """Ajoute chacun des clients d'une liste au buffer"""
        for client in lc:
            self.ajoute_client(client)

    def affiche_etat(self):
        pass

class Serveur:
    """
    Classe Serveur : Définie à partir d'une loi de sortie
    Contient un seul client à la fois
    """
    def __init__(self, S):
        self.S = S
        self.has_client = False

    def __str__(self):
        if self.has_client:
            return str(self.client_actuel)
        else:
            return 'Vide'

    def iteration(self, F):
        if self.has_client:
            self.client_actuel.inc_temps()
            self.client_actuel.retire_poids(self.S())

            if self.client_actuel.poids_neg():
                F.sortir_client(self.client_actuel.temps_attente)
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

    def __init__(self, S, attente_max):
        super().__init__(S)
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
