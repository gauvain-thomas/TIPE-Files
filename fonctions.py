import numpy as np
import copy as cp
import matplotlib.pyplot as plt

#----------Arrivees----------

def echelon(t1, t2, n=1, distribution_poids = lambda :1):
    '''Génère un échelon de clients entre t1 et t2, de n clients de poids p par unité de temps.'''
    echelon = []
    for i in range(t1, t2+1):
        echelon += [(i, distribution_poids())]*n
    return echelon

def dirac(t, n, distribution_poids = lambda :1):
    '''Genère un dirac de n clients de poids p à l'instant t.'''
    return [(t,distribution_poids())]*n

def poisson(n, lam, distribution_poids):
    '''Genere des arrivees de λ clients par unite de temps en moyenne, suivant une loi de poisson.'''
    arr_par_inst = np.random.poisson(lam, (n+1))
    A = []
    for i in range(n+1):
        for j in range(arr_par_inst[i]):
            A.append((i, distribution_poids()))
    return A

def somme_arrivees(A1, A2):
    '''Somme deux paterns d'arrivees.'''
    A = cp.deepcopy(A1)
    for a in A2:
        insertion(A,a)
    return A

def fusion_arrivees(liste_arrivees):
    '''Fusionne une liste de paterns d'arrivees.'''
    A = liste_arrivees.pop(0)
    if liste_arrivees:
        return somme_arrivees(A, fusion_arrivees(liste_arrivees))
    else:
        return A
#----------Distributions de poids----------

def poids_deterministe(n):
    return lambda :n

def poids_poisson(mu):
    return lambda :np.random.poisson(mu)

#----------Lois de temps----------

def service_pile_ou_face(p):
    x = np.random.randint(2)
    if x:
        return np.random.poisson(p)
    else:
        return np.random.poisson(2*p)

#----------Lecture d'evenements----------

def lire_evenements_creux(evenements, t_max, cumule=0):
    '''Convertit une liste d'evenements en une liste d'instants distincts.'''
    out = [0]*int(np.ceil((t_max+1)))
    for ev in evenements:
        instant, valeur = ev
        if cumule:
            out[instant] += valeur
        else:
            out[instant] = valeur
    return out

def lire_evenements(evenements):
    '''Convertit une liste d'evenements en une liste d'instants et une liste des valeurs'''
    valeurs = []
    temps = []
    for ev in evenements:
        t, v = ev
        temps.append(t)
        valeurs.append(v)
    return temps, valeurs

#----------Tracés----------

def distribution(l):
    out = [0]*(max(l)-min(l)+2)
    for el in l:
        out[el] += 1
    print(np.average(out))
    plt.plot(out)
    plt.show()

def trace_taille_pertes(fs, A):

    colors = ['blue', 'orange', 'green', 'red']
    
    fig, axs = plt.subplots(2)

    axs[0].title.set_text('taille de la file')
    axs[0].set_xlabel('temps')

    axs[1].title.set_text('pertes')
    axs[1].set_xlabel('temps')

    for (i, f) in enumerate(fs):
        A_bis = cp.deepcopy(A)
        N, P = f.simul_taille_pertes(A_bis)
        (tn, N), (tp, P) = lire_evenements(N), lire_evenements(P)
        axs[0].plot(tn, N, color=colors[i], label=f.type)
        axs[1].plot(tp, P, color=colors[i])

    axs[0].tick_params(axis='y')
    axs[0].legend()
    axs[1].tick_params(axis='y')

    fig.tight_layout()

    plt.show()

def trace_taille_arrivees(f1, f2, A, title=''):

    A2 = cp.deepcopy(A)
    A3 = cp.deepcopy(A)
    N1= f1.simul_taille(A)
    N2= f2.simul_taille(A2)

    tn1, N1 = lire_evenements(N1)
    tn2, N2 = lire_evenements(N2)
    arrivees1, arrivees2 = lire_evenements_creux(A3, max(tn1), cumule = 1), lire_evenements_creux(A3, max(tn2), cumule=1)

    fig, ax = plt.subplots()

    ax.title.set_text(title)
    ax.set_ylabel('taille')
    ax.set_xlabel('temps')
    ax.plot(tn1, N1, color='tab:blue', label=f1.type)
    ax.tick_params(axis='y')
    ax.plot(tn2, N2, color='tab:orange', label=f2.type)
    ax.legend()

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'black'
    ax2.set_ylabel('arrivees', color=color)
    ax2.plot(arrivees1, color=color, alpha=0.2)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()

    plt.show()

    print((f1.type+':'), f1.pertes, 'pertes (pondérées)')
    print(f2.type+':', f2.pertes, 'pertes (pondérées)')

def trace_taille(f1, f2, A):
    A2 = cp.deepcopy(A)
    N1= f1.simul_taille(A)
    N2= f2.simul_taille(A2)
    tn1, N1 = lire_evenements(N1)
    tn2, N2 = lire_evenements(N2)

    fig, ax = plt.subplots()

    ax.title.set_text('taille de la file')
    ax.set_xlabel('temps')
    ax.plot(tn1, N1, color='blue', label=f1.type)
    ax.tick_params(axis='y')
    ax.plot(tn2, N2, color='orange', label=f2.type)
    ax.legend()

    fig.tight_layout()

    plt.show()

    print((f1.type+':'), f1.pertes, 'pertes (pondérées)')
    print((f2.type+':'), f2.pertes, 'pertes (pondérées)')

def trace(f, A):
    N = f.simul_taille(A)
    t,N = lire_evenements(N)
    plt.step(t,N)
    plt.show()

#----------Fonctions usuelles----------

def insertion(A,a):
    for i in range(len(A)):
            if A[i][0] >= a[0]:
                A.insert(i, a)
                return A
    A.append(a)
    return A
