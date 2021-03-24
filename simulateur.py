import sqlite3
import pandas as pd
from classes import *
from fonctions import *
import numpy as np
from copy import deepcopy

con = sqlite3.connect('Simulations.con')

cur = con.cursor()

def insert_simul(f, A, duree, quantite, lamda, poids_moyen, pattern_arrivees, pattern_poids):

    #==================================Serveurs

    serveurs_id = [None, None, None]
    i = 0
    for s in f.serveurs:
        if s.__name__() == 'RR':
            q = s.quantum
            description_s = (s.__name__(), s.loi_temps.__doc__, q)
            cur.execute("SELECT rowid FROM Serveurs WHERE (discipline, loi_temps, quantum) = (?,?,?)", description_s)
        else:
            description_s = (s.__name__(), s.loi_temps.__doc__)
            cur.execute("SELECT rowid FROM Serveurs WHERE (discipline, loi_temps) = (?,?)", description_s)
        row = cur.fetchone()
        if row:
            serveurs_id[i] = row[0]
        else:
            cur.execute("INSERT INTO Serveurs (discipline, loi_temps, quantum) VALUES (?,?,?)", description_s)
            serveurs_id[i] = cur.lastrowid
    
    con.commit()

    #==================================File

    if serveurs_id[1] == None:
        description_f = (f.taille_buffer, serveurs_id[0])
        cur.execute("SELECT rowid FROM Files WHERE (buffer, serveur_id) = (?,?)", description_f)
        row = cur.fetchone()
    elif serveurs_id[2] == None:
        description_f = (f.taille_buffer, serveurs_id[0], serveurs_id[1])
        cur.execute("SELECT rowid FROM Files WHERE (buffer, serveur_id, serveur_2_id) = (?,?,?)", description_f)
        row = cur.fetchone()
    else:
        description_f = (f.taille_buffer, serveurs_id[0], serveurs_id[1], serveurs_id[2])
        cur.execute("SELECT rowid FROM Files WHERE (buffer, serveur_id, serveur_2_id, serveur_3_id) = (?,?,?,?)", description_f)
        row = cur.fetchone()

    if row == None:
        description_f = (f.taille_buffer, serveurs_id[0], serveurs_id[1], serveurs_id[2])
        cur.execute("INSERT INTO Files (buffer, serveur_id, serveur_2_id, serveur_3_id) VALUES (?,?,?,?)", description_f)
        file_id = cur.lastrowid
    else:
        file_id = row[0]

    #==================================Arrive

    description_a=(duree, quantite, lamda, poids_moyen, pattern_arrivees, pattern_poids)
    cur.execute("SELECT rowid FROM Arrivees WHERE (duree, quantite, lambda, poids_moyen, pattern_arrivees, pattern_poids) = (?,?,?,?,?,?)", description_a) 
    row = cur.fetchone()
    if row == None:
        cur.execute("INSERT INTO Arrivees (duree, quantite, lambda, poids_moyen, pattern_arrivees, pattern_poids) VALUES (?,?,?,?,?,?)", description_a)
        arrivee_id = cur.lastrowid
    else:
        arrivee_id = row[0]

    con.commit()

    #==================================Data

    N = f.simul_taille(A)
    row = [np.average(N), f.pertes, f.pertes_ponderees, np.average(f.temps_attente), np.average(f.temps_chez_serveurs), file_id, arrivee_id]

    cur.execute('''INSERT INTO Data(taille, pertes, pertes_ponderees, attente, attente_service, file_id, arrivees_id) VALUES (?,?,?,?,?,?,?)''', row)
    con.commit()

# for k in range(1,30):
#     liste = [File(k, [Serveur()]), File(k, [Serveur_Priorite(1)])]+[File(k, [Serveur_RR(i)]) for i in range(1,4)]
#     for _ in range(50):
#         A = poisson(10000, 1, poids_poisson(10))
#         for f in liste:
#             A_bis = deepcopy(A)
#             f.reset()
#             insert_simul(f, A_bis, 10000, 10000, 1, 10, 'poisson', 'poisson')

df = pd.read_sql('SELECT buffer, avg(pertes) FROM Data JOIN Files ON file_id = Files.id GROUP BY buffer;', con=con)

df.plot(x = 0, y=1)

            