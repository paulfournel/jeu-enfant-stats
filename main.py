import random
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Algorithm:
    def __init__(self):
        self.name = 'some'

    def shouldContinuePick(self, currently_picked, points):
        choice = input("Voulez-vous piocher une autre carte ? (o/n) ")
        return choice.lower() == 'o'

    def ouPlacerRouge(self, points):
        choix = input("Où voulez-vous placer le rouge (jaune/bleue/verte) ? ")
        while choix not in ['jaune', 'bleue', 'verte']:
            logger.debug("Choix invalide. Veuillez choisir entre jaune, bleue ou verte.")
            choix = input("Où voulez-vous placer le rouge (jaune/bleue/verte) ? ")
        return choix


class AlgorithmEnfant:
    def __init__(self):
        self.name = 'some'

    def shouldContinuePick(self, currently_picked, points, stats):

        return len(currently_picked) < random.randint(1, 5)

    def ouPlacerRouge(self, points):
        sorted_colors = sorted(points.items(), key=lambda x: x[1], reverse=True)
        filtered_colors = [color for color, score in sorted_colors if score < 9]
        if len(filtered_colors) == 0:
            return sorted_colors[0][0]
        return random.choice(filtered_colors)

class AlgorithmFixe:
    def __init__(self):
        self.name = 'some'

    def shouldContinuePick(self, currently_picked, points, stats):
        sorted_colors = sorted(points.items(), key=lambda x: x[1], reverse=True)
        filtered_colors = [color for color, score in sorted_colors if score < 9]
        filtered_out_colors = [color for color, score in sorted_colors if score >= 9]

        if points[filtered_colors[0]] + sum([c.numero for c in currently_picked if c.couleur == filtered_colors[0] or c.couleur == 'red']) > 8:
            return False

        if stats['noires'] == 0:
            return True

        interesting_card_picked = len([c for c in currently_picked if c.couleur not in filtered_out_colors])
        return interesting_card_picked < (np.floor(stats['cartes']/stats['noires']))-1

    def ouPlacerRouge(self, points):
        sorted_colors = sorted(points.items(), key=lambda x: x[1], reverse=True)
        filtered_colors = [color for color, score in sorted_colors if score < 9]
        if len(filtered_colors) == 0:
            return sorted_colors[0][0]
        return filtered_colors[0]

class AlgorithmFixeAjuste:
    def __init__(self):
        self.name = 'some'

    def shouldContinuePick(self, currently_picked, points, stats):
        sorted_colors = sorted(points.items(), key=lambda x: x[1], reverse=True)
        filtered_colors = [color for color, score in sorted_colors if score < 9]
        filtered_out_colors = [color for color, score in sorted_colors if score >= 9]

        if points[filtered_colors[0]] + sum([c.numero for c in currently_picked if c.couleur == filtered_colors[0] or c.couleur == 'red']) > 8:
            return False

        if stats['noires'] == 0:
            logger.info(f"You can pick all! {stats}")
            return True

        interesting_card_picked = len([c for c in currently_picked if c.couleur not in filtered_out_colors])
        if (np.floor(stats['cartes']/stats['noires'])) < 1:
            logger.info(f"Many blacks! {stats}")
        return interesting_card_picked < (np.floor(stats['cartes']/stats['noires']))-1

    def ouPlacerRouge(self, points):
        sorted_colors = sorted(points.items(), key=lambda x: x[1], reverse=True)
        filtered_colors = [color for color, score in sorted_colors if score < 9]
        filtered_out_colors = [color for color, score in sorted_colors if score >= 9]

        if 'verte' not in filtered_out_colors:
            return 'verte'

        if len(filtered_colors) == 0:
            return sorted_colors[0][0]
        return filtered_colors[0]

class Carte:
    def __init__(self, couleur, numero):
        self.couleur = couleur
        self.numero = numero


class JeuCartes:
    def __init__(self):
        self.cartes = []
        self.defausse = []
        couleurs = ['jaune', 'bleue', 'verte', 'noire', 'rouge']
        numeros_jbv = [1, 1, 1, 1, 1, 1, 1, 2]

        for couleur in couleurs:
            if couleur == 'rouge':
                self.cartes.extend([Carte(couleur, 1) for _ in range(3)])
            elif couleur == 'noire':
                self.cartes.extend([Carte(couleur, None) for _ in range(9)])
            #elif couleur == 'bleue':
            #    self.cartes.extend([Carte(couleur, num) for num in numeros_jbv[0:7]])
            else:
                self.cartes.extend([Carte(couleur, num) for num in numeros_jbv])

        random.shuffle(self.cartes)

    def pioche(self):
        if len(self.cartes) == 0:
            self.cartes = self.defausse
            self.defausse = []

            random.shuffle(self.cartes)

        return self.cartes.pop()

    def stats(self):
        return {'cartes': len(self.cartes),
                'noires': len([c for c in self.cartes if c.couleur == 'noire'])}


class Jeu:
    def __init__(self, algo):
        self.jeu_cartes = JeuCartes()

        self.points = {'jaune': 0, 'bleue': 0, 'verte': 0}
        self.compteur = 0
        self.algo = algo
        self.des = 3

    def displayGameState(self):
        logger.debug("État actuel du jeu:")
        logger.debug(f"Points: {self.points}")
        logger.debug(f"Compteur: {self.compteur}")
        logger.debug("----")

    def jouer(self):
        self.displayGameState()
        currently_picked = []
        while True:
            while True:
                carte_piochee = self.jeu_cartes.pioche()
                logger.debug(f"Carte piochée : {carte_piochee.couleur} {carte_piochee.numero}")

                currently_picked.append(carte_piochee)

                if carte_piochee.couleur == 'noire':
                    logger.debug("Carte noire ! Vous perdez les cartes piochées.")
                    self.jeu_cartes.defausse.extend(currently_picked)
                    currently_picked = []
                    break
                else:
                    if not self.algo.shouldContinuePick(currently_picked, self.points, self.jeu_cartes.stats()):
                        break

            for carte in currently_picked:
                if carte.couleur in ['jaune', 'bleue', 'verte']:
                    self.points[carte.couleur] += carte.numero

                if carte.couleur == 'rouge':
                    choix = self.algo.ouPlacerRouge(self.points)
                    self.points[choix] += 1

            self.lancer_des()

            if self.compteur > 37:
                logger.debug("Le compteur a dépassé 37. Vous avez perdu!")
                return False

            for couleur, points in self.points.items():
                if points == 9:
                    self.points[couleur] = 10
                    logger.debug(f"La couleur {couleur} a atteint 9 points. Un dé est retiré.")
                    self.des -= 1

            if all(value >= 9 for value in self.points.values()):
                logger.debug(f"Gagné!")
                return True

            self.displayGameState()

    def lancer_des(self):
        dice = [0, 0, 0, 1, 1, 2]  # Dice with 3 zeros, 2 ones, and 1 two
        res = [random.choice(dice) for _ in range(self.des)]
        somme_des = sum(res)
        logger.debug(f"Vous avez lancé les dés : res. Total : {somme_des}")

        self.compteur += somme_des


# Lancement du jeu
results = []
for i in range(10000):
    jeu = Jeu(AlgorithmFixe())
    results.append(jeu.jouer())

percentage_true = np.mean(results) * 100
logger.info(f"Algo adulte {percentage_true}")


results = []
for i in range(10000):
    jeu = Jeu(AlgorithmFixeAjuste())
    results.append(jeu.jouer())

percentage_true = np.mean(results) * 100
logger.info(f"Algo adulte ajuste {percentage_true}")

results = []
for i in range(10000):
    jeu = Jeu(AlgorithmEnfant())
    results.append(jeu.jouer())

percentage_true = np.mean(results) * 100
logger.info(f"Algo enfant {percentage_true}")
