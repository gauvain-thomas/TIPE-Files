#----------Constantes----------

au_travail = "tab:green"
au_repos = "tab:orange"


#----------Fonctions----------

def indice_min(l): # Sert a trouver le prochain evenement
    '''Renvoie l'indice du minimum d'une liste.'''
    out = -2
    m = float('inf')
    for i in range(len(l)):
        if l[i] <= m:
            m = l[i]
            out = i
    return out

def pop_min(buffer): # Appelle le plus petit client
    #assert buffer
    indice_min = 0
    minimum = buffer[0][1]
    for i in range(1, len(buffer)):
        x = buffer[i][1]
        if x < minimum:
            indice_min = i
            minimum = x
    return buffer.pop(indice_min)

def nommer(f, doc): #Confère une docstring à une fonction
    f.__doc__ = doc
    return f

#----------Classes----------

class File:
    '''Classe représentant une file complete :
    Prend pour parametres
        - une taille maximale K, qui peut etre infinie (float('inf'))
        - une liste de Serveurs
    '''
    def __init__(self, K, serveurs, type_de_file = 'File'):
        self.type = type_de_file
        self.taille_buffer = K
        self.serveurs = serveurs
        self.buffer = []
        self.occupation = 0
        self.horloge = 0
        self.pertes = 0
        self.pertes_ponderees = 0
        self.fin_service = 0
        self.temps_attente = []
        self.temps_chez_serveurs = []
        self.temps_travail = [[[0 for _ in self.serveurs], au_repos]]

    def __name__(self):
        return self.type

    def reset(self):
        for serveur in self.serveurs:
            serveur.reset()
        self.__init__(self.taille_buffer, self.serveurs)

    def simul(self,A):

        nb_serveurs = len(self.serveurs)

        while self.fin_service != nb_serveurs:
            
            liste = [serv.temps_service for serv in self.serveurs]
            i = indice_min(liste)

            if A and (A[0][0] <= liste[i]):
                t,p = A.pop(0)
                self.horloge = t
                if self.occupation <= self.taille_buffer :
                    self.buffer.append([t,p])
                    self.occupation += 1
                else:
                    self.pertes += 1
                    self.pertes_ponderees += p

            else:
                self.serveurs[i].service(self, A)
                self.occupation += self.serveurs[i].action_buffer

    def simul_taille(self,A):

        N = []

        nb_serveurs = len(self.serveurs)

        while self.fin_service != nb_serveurs:
            
            liste = [serv.temps_service for serv in self.serveurs]
            i = indice_min(liste)

            if A and (A[0][0] <= liste[i]):
                t,p = A.pop(0)
                self.horloge = t
                if self.occupation <= self.taille_buffer :
                    self.buffer.append([t,p])
                    self.occupation += 1
                else:
                    self.pertes += 1
                    self.pertes_ponderees += p
                N.append((self.horloge, self.occupation))

            else:
                self.serveurs[i].service(self, A)
                self.occupation += self.serveurs[i].action_buffer
                N.append((self.horloge, self.occupation))
                
        N.append((self.horloge, self.occupation))

        return N
        
    def simul_taille_pertes(self,A):

        N = []
        P = []

        nb_serveurs = len(self.serveurs)

        while self.fin_service != nb_serveurs:
            
            liste = [serv.temps_service for serv in self.serveurs]
            i = indice_min(liste)

            if A and (A[0][0] <= liste[i]):
                t,p = A.pop(0)
                self.horloge = t
                if self.occupation <= self.taille_buffer :
                    self.buffer.append([t,p])
                    self.occupation += 1
                else:
                    self.pertes += 1
                    self.pertes_ponderees += p
                N.append((self.horloge, self.occupation))
                P.append((self.horloge, self.pertes_ponderees))

            else:
                self.serveurs[i].service(self, A)
                self.occupation += self.serveurs[i].action_buffer
                N.append((self.horloge, self.occupation))
                P.append((self.horloge, self.pertes_ponderees))
                
        N.append((self.horloge, self.occupation))
        P.append((self.horloge, self.pertes_ponderees))

        return N,P

class Serveur:
    '''Classe représentant un serveur.'''
    def __init__(self, loi_temps = nommer((lambda poids :poids/10), 'p/10')):
        self.loi_temps = loi_temps
        self.client_actuel = None
        self.temps_service = 0 # Instant au quel le serveur aura fini de servir le cilent actuel
        self.action_buffer = 0 # Décrit la variation de file.occupation (utilisé dans la classe file)
        self.etat = au_repos

    def __name__(self):
        return 'FIFO'
    
    def reset(self):
        self.__init__(loi_temps = self.loi_temps)
    
    def service(self, file, A):
        file.horloge = self.temps_service
        self.action_buffer = 0
        if file.buffer:
            self.etat = au_travail
            self.client_actuel = file.buffer.pop(0)
            self.action_buffer -= 1
            self.temps_service = self.loi_temps(self.client_actuel[1]) + file.horloge
            file.temps_attente.append(self.temps_service - self.client_actuel[0])
            file.temps_chez_serveurs.append(self.temps_service - file.horloge)
        elif A:
            self.etat = au_repos
            ts = self.temps_service
            self.temps_service = A[0][0]
        else:
            self.etat = au_repos
            file.fin_service += 1
        file.temps_travail.append([[s.temps_service for s in file.serveurs], self.etat])
        
class Serveur_RR(Serveur):
    '''
    Hérite de la classe serveur:

    Les serveurs Round Robin servent un client pendant une durée max (quantum) avant de le réinsrer dans la file.
    '''
    
    def __init__(self, quantum, loi_temps = nommer((lambda poids :poids/10), 'p/10')):
        super().__init__(loi_temps)
        self.quantum = quantum

    def __name__(self):
        return 'RR'

    def reset(self):
        self.__init__(self.quantum, loi_temps = self.loi_temps)

    def service(self, file, A):
        file.horloge = self.temps_service
        self.action_buffer = 0
        if self.client_actuel:
            file.buffer.append(self.client_actuel)
            self.action_buffer += 1
            self.client_actuel = None
        if file.buffer:
            self.etat = au_travail
            self.client_actuel = file.buffer.pop(0)
            self.action_buffer -= 1
            t,p = self.client_actuel
            temps_de_service = self.loi_temps(p)
            if temps_de_service > self.quantum:
                self.temps_service = self.quantum + file.horloge
                p -= int(self.quantum//(temps_de_service/p))
                self.client_actuel = (t,p)
            else:
                self.temps_service = temps_de_service + file.horloge
                file.temps_attente.append(self.temps_service - self.client_actuel[0])
                self.client_actuel = None
        elif A:
            self.etat = au_repos
            self.temps_service = A[0][0]
        else:
            self.etat = au_repos
            file.fin_service += 1
        file.temps_travail.append([[s.temps_service for s in file.serveurs], self.etat])

class Serveur_Priorite(Serveur):
    '''
    Hérite de la classe serveur:

    Les serveurs Priorite appellent systematiquement le client de plus petit poids dans la file.
    '''
    
    def __init__(self, loi_temps = nommer((lambda poids :poids/10), 'p/10')):
        super().__init__()

    def __name__(self):
        return 'PRIO'

    def service(self, file, A):
        file.horloge = self.temps_service
        self.action_buffer = 0
        if file.buffer:
            self.etat = au_travail
            self.client_actuel = pop_min(file.buffer)
            self.action_buffer -= 1
            self.temps_service = self.loi_temps(self.client_actuel[1]) + file.horloge
            file.temps_attente.append(self.temps_service - self.client_actuel[0])
            file.temps_chez_serveurs.append(self.temps_service - file.horloge)
        elif A:
            self.etat = au_repos
            self.temps_service = A[0][0]
        else:
            self.etat = au_repos
            file.fin_service += 1
        file.temps_travail.append([[s.temps_service for s in file.serveurs], self.etat])