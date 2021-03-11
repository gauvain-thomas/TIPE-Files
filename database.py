"""Gère toutes les fonctions relatives à la base de donnée"""

import sqlite3

con = sqlite3.connect('resultats.db')


def index_serveur(S):
    """Renvoie l'index du serveur de la BDD, le créant s'il n'existe pas"""
    s_moy = S.nbr_sorties_moyen
    loi = S.loi
    query = 'SELECT id FROM Serveurs WHERE loi_sortie=\'{}\' AND sortie_moyen={}'.format(loi, s_moy)
    l = con.execute(query).fetchone()
    if l == None:
        q_ajout = 'INSERT INTO Serveurs (loi_sortie, sortie_moyen) VALUES(\'{}\', {})'.format(loi, s_moy)
        con.execute(q_ajout)
        l = con.execute(query).fetchone()
    con.commit()
    return l[0]

def index_file(F):
    indices_serveurs = []
    for S in F.serveurs:
         indices_serveurs.append(index_serveur(S))
    K = F.K
    arrivee = F.nom
    nbr_serv = len(indices_serveurs)
    serv1 = indices_serveurs[0]
    if len(indices_serveurs) > 1:
        serv2 = indices_serveurs[1]
        query = 'SELECT id FROM Files WHERE taille_buffer={} AND arrivee=\'{}\' AND nombre_serveurs={} AND serveur_1_id={} AND serveur_2_id={}'.format(K, arrivee, nbr_serv, serv1, serv2)
    else:
        query = 'SELECT id FROM Files WHERE taille_buffer={} AND arrivee=\'{}\' AND nombre_serveurs={} AND serveur_1_id={} AND serveur_2_id is NULL'.format(K, arrivee, nbr_serv, serv1)

    l = con.execute(query).fetchone()
    if l == None:
        if len(indices_serveurs) > 1:
            q_ajout = 'INSERT INTO Files (taille_buffer, arrivee, nombre_serveurs, serveur_1_id, serveur_2_id) VALUES({}, \'{}\', {}, {}, {})'.format(K, arrivee, nbr_serv, serv1, serv2)
        else:
            q_ajout = 'INSERT INTO Files (taille_buffer, arrivee, nombre_serveurs, serveur_1_id) VALUES({}, \'{}\', {}, {})'.format(K, arrivee, nbr_serv, serv1)
        con.execute(q_ajout)
        l = con.execute(query).fetchone()
    con.commit()
    return l[0]
