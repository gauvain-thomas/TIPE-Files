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
        if loi in ['RR_p', 'RR_d']:
            attente_max = S.attente_max
            q_ajout = 'INSERT INTO Serveurs (loi_sortie, sortie_moyen, quantum) VALUES(\'{}\', {}), {}'.format(loi, s_moy, attente_max)
        elif loi in ['FP_p', 'FP_d']:
            pmax = S.poids_max
            q_ajout = 'INSERT INTO Serveurs (loi_sortie, sortie_moyen, M10_pmax) VALUES(\'{}\', {}), {}'.format(loi, s_moy, pmax)
        else:
            q_ajout = 'INSERT INTO Serveurs (loi_sortie, sortie_moyen) VALUES(\'{}\', {})'.format(loi, s_moy)
        con.execute(q_ajout)
        l = con.execute(query).fetchone()
    con.commit()
    return l[0]

def index_arrivee(loi_arrivees, nbr_clients_moyen, loi_poids, poids_moyen):
    """Renvoie l'index de l'arrivée de la BDD, la créant si elle n'existe pas"""
    query = 'SELECT id FROM Arrivees WHERE loi_arrivees=\'{}\' AND nbr_arrivees_moyen={} AND loi_poids=\'{}\' AND poids_moyen={}'.format(loi_arrivees, nbr_clients_moyen, loi_poids, poids_moyen)
    l = con.execute(query).fetchone()
    if l == None:
        q_ajout = 'INSERT INTO Arrivees (loi_arrivees, nbr_arrivees_moyen, loi_poids, poids_moyen) VALUES(\'{}\', {}, \'{}\', {})'.format(loi_arrivees, nbr_clients_moyen, loi_poids, poids_moyen)
        con.execute(q_ajout)
        l = con.execute(query).fetchone()
    con.commit()
    return l[0]

def index_file(F):
    indices_serveurs = []
    for S in F.serveurs:
         indices_serveurs.append(index_serveur(S))
    K = F.K
    # arrivee = F.nom
    id_arrivee = index_arrivee(F.A['loi_arrivees'], F.A['nbr_clients_moyen'], F.A['loi_poids'], F.A['poids_moyen'])
    nbr_serv = len(indices_serveurs)
    serv1 = indices_serveurs[0]
    if len(indices_serveurs) > 1:
        serv2 = indices_serveurs[1]
        query = 'SELECT id FROM Files WHERE taille_buffer={} AND id_arrivee=\'{}\' AND nombre_serveurs={} AND serveur_1_id={} AND serveur_2_id={}'.format(K, id_arrivee, nbr_serv, serv1, serv2)
    else:
        query = 'SELECT id FROM Files WHERE taille_buffer={} AND id_arrivee=\'{}\' AND nombre_serveurs={} AND serveur_1_id={} AND serveur_2_id is NULL'.format(K, id_arrivee, nbr_serv, serv1)

    l = con.execute(query).fetchone()
    if l == None:
        if len(indices_serveurs) > 1:
            q_ajout = 'INSERT INTO Files (taille_buffer, id_arrivee, nombre_serveurs, serveur_1_id, serveur_2_id) VALUES({}, \'{}\', {}, {}, {})'.format(K, id_arrivee, nbr_serv, serv1, serv2)
        else:
            q_ajout = 'INSERT INTO Files (taille_buffer, id_arrivee, nombre_serveurs, serveur_1_id) VALUES({}, \'{}\', {}, {})'.format(K, id_arrivee, nbr_serv, serv1)
        con.execute(q_ajout)
        l = con.execute(query).fetchone()
    con.commit()
    return l[0]
