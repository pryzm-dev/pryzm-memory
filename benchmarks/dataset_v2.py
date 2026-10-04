"""Jeu HOLDOUT v2 du banc mémoire : réservé à la VALIDATION FINALE.

Règle anti-surapprentissage : aucun hyperparamètre du moteur n'est choisi en
regardant ce jeu. Les réglages se font sur v1 ; v2 ne sert qu'à vérifier que le
gain tient sur un autre personnage, d'autres formulations, une autre graine et
d'autres gabarits de distracteurs.

Profil fictif : Malik Benhamou, kinésithérapeute associé d'un cabinet à Lille,
président bénévole d'un club de course (« Les Foulées de la Deûle ») et auteur
d'un guide de prévention en cours d'écriture. Plus d'anglais que v1 (collègues
et éditeur anglophones). Tout est INVENTÉ ; aucune donnée réelle.

Usage :
    python -m bench.dataset_v2         # écrit bench/data/dataset_v2.json
"""
from __future__ import annotations

import json
import os
import random

from bench.dataset import DATA_DIR, build_from

SEED = 77310519
VERSION = "v2"
DATASET_PATH = os.path.join(DATA_DIR, f"dataset_{VERSION}.json")

SIMPLE = [
    ("Je commence mes consultations à 7 h 30 et je ne prends plus personne après 18 h.", "fr", "preference",
     [("horaires de consultation de Malik", "fr", "paraphrase"), ("what time does Malik stop seeing patients", "en", "crosslingue"), ("puis-je lui proposer un rendez-vous à 19 h ?", "fr", "indirecte")]),
    ("Le cabinet utilise le logiciel de gestion Doctolib pour l'agenda et Vega pour la facturation.", "fr", "technical_decision",
     [("logiciel de facturation du cabinet", "fr", "paraphrase"), ("which billing software does the practice use", "en", "crosslingue"), ("avec quoi j'édite les feuilles de soins ?", "fr", "indirecte")]),
    ("I am lactose intolerant, so no dairy at team lunches.", "en", "user",
     [("intolérance alimentaire de Malik", "fr", "crosslingue"), ("does Malik have a food intolerance", "en", "paraphrase"), ("peut-on prévoir un plateau de fromages pour son pot de départ ?", "fr", "indirecte")]),
    ("Notre banque professionnelle est le Crédit Mutuel de Lille-Vauban ; le conseiller s'appelle Damien Lecocq.", "fr", "context",
     [("qui est notre conseiller bancaire ?", "fr", "paraphrase"), ("name of our business bank advisor", "en", "crosslingue"), ("à qui demander une hausse du découvert autorisé ?", "fr", "indirecte")]),
    ("Le cabinet loue 120 m² au 18 rue de Wazemmes, bail commercial de 9 ans signé en 2022.", "fr", "context",
     [("surface des locaux du cabinet", "fr", "paraphrase"), ("how big is the clinic space we rent", "en", "crosslingue"), ("jusqu'à quand sommes-nous engagés pour les murs ?", "fr", "indirecte")]),
    ("My editor at Tidewater Press is Fiona McAllister; the manuscript is due on 15 March.", "en", "context",
     [("date de remise du manuscrit", "fr", "crosslingue"), ("who is my editor at the publisher", "en", "paraphrase"), ("pour quand dois-je avoir fini d'écrire le livre ?", "fr", "indirecte")]),
    ("Le club Les Foulées de la Deûle compte 86 adhérents cette saison.", "fr", "note",
     [("nombre d'adhérents du club", "fr", "paraphrase"), ("how many members does the running club have", "en", "crosslingue"), ("combien de dossards commander pour que chaque membre en ait un ?", "fr", "indirecte")]),
    ("Devis D-7731 envoyé au comité d'entreprise Valtrans : 12 séances de prévention du mal de dos pour 1 680 € TTC.", "fr", "note",
     [("devis D-7731", "fr", "identifiant"), ("price quoted to Valtrans works council", "en", "crosslingue"), ("combien j'ai proposé pour les ateliers dos chez le transporteur ?", "fr", "indirecte")]),
    ("Panne de la table de traction TX-400 : code erreur E17 ; le technicien Medimat passe sous 48 h si on appelle avant midi.", "fr", "bug",
     [("code erreur E17 sur la table", "fr", "identifiant"), ("what to do when the traction table fails", "en", "crosslingue"), ("l'appareil d'élongation est bloqué, qui contacter ?", "fr", "indirecte")]),
    ("Objectif de l'année : ouvrir un deuxième créneau de rééducation post-opératoire du genou le samedi matin.", "fr", "intention",
     [("objectif du cabinet pour l'année", "fr", "paraphrase"), ("new weekend service planned at the clinic", "en", "crosslingue"), ("que veut-on lancer le samedi matin ?", "fr", "indirecte")]),
    ("I keep my patient notes in French but write the book drafts in English.", "en", "preference",
     [("langue de rédaction du livre", "fr", "crosslingue"), ("which language for the book drafts", "en", "paraphrase"), ("en quelle langue envoyer les chapitres à l'éditeur ?", "fr", "indirecte")]),
    ("Les associés du cabinet sont Inès Carpentier et Romain Delattre ; chacun détient un tiers des parts.", "fr", "context",
     [("qui sont mes associés ?", "fr", "paraphrase"), ("who are my business partners at the clinic", "en", "crosslingue"), ("avec qui dois-je voter pour une grosse dépense ?", "fr", "indirecte")]),
    ("Le site du club est hébergé sur o2switch, avec un WordPress mis à jour par Bastien.", "fr", "architecture",
     [("hébergeur du site du club", "fr", "paraphrase"), ("where is the running club website hosted", "en", "crosslingue"), ("qui s'occupe des mises à jour du site de l'association ?", "fr", "indirecte")]),
    ("Order BC-2290: two new massage tables from Kinémat, delivery expected the week of 12 May.", "en", "note",
     [("bon de commande BC-2290", "fr", "identifiant"), ("when will the new massage tables arrive", "en", "paraphrase"), ("quand le matériel neuf doit-il être livré au cabinet ?", "fr", "indirecte")]),
    ("Je fais du vélo-taf tous les jours, 9 km par trajet, même sous la pluie.", "fr", "user",
     [("comment Malik vient au travail", "fr", "paraphrase"), ("how does he commute", "en", "crosslingue"), ("faut-il lui réserver une place de parking ?", "fr", "indirecte")]),
    ("La cotisation annuelle au club est de 45 € par adulte et 25 € pour les moins de 18 ans.", "fr", "context",
     [("prix de l'adhésion au club", "fr", "paraphrase"), ("membership fee for teenagers", "en", "crosslingue"), ("combien doit payer un lycéen pour s'inscrire ?", "fr", "indirecte")]),
    ("I never take calls during sessions; patients and suppliers should text me instead.", "en", "preference",
     [("comment me joindre pendant les séances", "fr", "crosslingue"), ("can people call him while he is treating patients", "en", "paraphrase"), ("le fournisseur peut-il me téléphoner à 10 h ?", "fr", "indirecte")]),
    ("Le cabinet est fermé les trois premières semaines d'août.", "fr", "context",
     [("fermeture estivale du cabinet", "fr", "paraphrase"), ("summer closing dates of the clinic", "en", "crosslingue"), ("un patient peut-il venir le 10 août ?", "fr", "indirecte")]),
    ("Notre assurance responsabilité civile professionnelle est chez la MACSF, contrat RCP-55821.", "fr", "context",
     [("contrat RCP-55821", "fr", "identifiant"), ("professional liability insurer", "en", "crosslingue"), ("qui prévenir si un patient porte plainte ?", "fr", "indirecte")]),
    ("Le trail de la Deûle, organisé par le club, aura lieu le 21 juin au départ du parc de la Citadelle.", "fr", "note",
     [("date du trail organisé par le club", "fr", "paraphrase"), ("where does the club trail race start", "en", "crosslingue"), ("quel jour faut-il réserver les barrières de la Citadelle ?", "fr", "indirecte")]),
    ("Working title of my book: « Move Early, Heal Better ».", "en", "note",
     [("titre provisoire du livre", "fr", "crosslingue"), ("working title of Malik's book", "en", "paraphrase"), ("quel nom mettre sur la couverture de la maquette ?", "fr", "indirecte")]),
    ("La secrétaire du cabinet, Nadège, travaille les lundis, mardis et jeudis.", "fr", "context",
     [("jours de présence de la secrétaire", "fr", "paraphrase"), ("which days does the receptionist work", "en", "crosslingue"), ("qui répond au téléphone le mercredi ?", "fr", "indirecte")]),
    ("J'ai suivi la formation en thérapie manuelle du Concept Maitland en 2021.", "fr", "user",
     [("formations suivies par Malik", "fr", "paraphrase"), ("manual therapy certification", "en", "crosslingue"), ("quelle méthode manuelle j'ai apprise ?", "fr", "indirecte")]),
    ("The club's bank account is with La Banque Postale, managed by the treasurer Agnès Vandamme.", "en", "context",
     [("qui gère les comptes du club ?", "fr", "crosslingue"), ("who is the running club treasurer", "en", "paraphrase"), ("à qui transmettre le chèque de la mairie pour l'association ?", "fr", "indirecte")]),
    ("Le Wi-Fi des patients est séparé du réseau du cabinet ; la box est une Livebox Pro.", "fr", "architecture",
     [("configuration du réseau du cabinet", "fr", "paraphrase"), ("is the guest network separated", "en", "crosslingue"), ("un patient connecté peut-il voir nos ordinateurs ?", "fr", "indirecte")]),
    ("Je déteste les réunions de plus de 30 minutes ; au-delà, je demande un ordre du jour écrit.", "fr", "preference",
     [("durée maximale des réunions pour Malik", "fr", "paraphrase"), ("how long can a meeting with him last", "en", "crosslingue"), ("puis-je lui caler une réunion d'une heure sans préparation ?", "fr", "indirecte")]),
    ("Ticket INC-5521 chez Vega : les feuilles de soins électroniques sont rejetées avec le motif 412 depuis la mise à jour de mars.", "fr", "bug",
     [("ticket INC-5521", "fr", "identifiant"), ("electronic claim rejection issue", "en", "crosslingue"), ("pourquoi la sécu refuse mes télétransmissions ?", "fr", "indirecte")]),
    ("We pay 340 € a month for the shared cleaning company, Net'Nord.", "en", "context",
     [("coût du ménage du cabinet", "fr", "crosslingue"), ("monthly cleaning company cost", "en", "paraphrase"), ("combien économiserait-on en faisant le ménage nous-mêmes ?", "fr", "indirecte")]),
    ("Mon expert-comptable est Philippe Ducrocq, cabinet Ducrocq Conseil à Roubaix.", "fr", "context",
     [("nom de mon comptable", "fr", "paraphrase"), ("who does my accounting", "en", "crosslingue"), ("à qui envoyer la liasse fiscale ?", "fr", "indirecte")]),
    ("La salle de renforcement musculaire du cabinet a un rameur Concept2 et deux vélos Wattbike.", "fr", "note",
     [("équipement de la salle de renfo", "fr", "paraphrase"), ("what cardio machines does the clinic have", "en", "crosslingue"), ("un patient peut-il faire du rameur chez nous ?", "fr", "indirecte")]),
    ("Code promo partenaire FOULEES25 : -25 % chez Running Conseil Lille pour les adhérents.", "fr", "note",
     [("code FOULEES25", "fr", "identifiant"), ("discount for club members at the running shop", "en", "crosslingue"), ("comment un adhérent paie moins cher ses chaussures ?", "fr", "indirecte")]),
    ("I want to run the Berlin marathon under 3 h 15 next September.", "en", "intention",
     [("objectif de Malik au marathon", "fr", "crosslingue"), ("target time for the Berlin marathon", "en", "paraphrase"), ("quel chrono je vise à l'automne ?", "fr", "indirecte")]),
    ("Les séances de groupe « dos » ont lieu le mardi à 18 h dans la grande salle, 8 personnes maximum.", "fr", "context",
     [("créneau des séances collectives pour le dos", "fr", "paraphrase"), ("group back class capacity", "en", "crosslingue"), ("peut-on inscrire un dixième participant mardi ?", "fr", "indirecte")]),
    ("Ma sauvegarde des documents du cabinet se fait chaque nuit sur un NAS Synology, copié chaque semaine chez Infomaniak.", "fr", "architecture",
     [("sauvegarde des fichiers du cabinet", "fr", "paraphrase"), ("clinic backup strategy", "en", "crosslingue"), ("si l'ordinateur grille, perd-on les dossiers ?", "fr", "indirecte")]),
    ("Le club s'entraîne le jeudi à 19 h au stade Pierre-de-Coubertin, piste en tartan.", "fr", "context",
     [("lieu de l'entraînement du jeudi", "fr", "paraphrase"), ("where does the club train on Thursdays", "en", "crosslingue"), ("où retrouver le groupe pour le fractionné de la semaine ?", "fr", "indirecte")]),
    ("Facture FA-0938 de la plateforme de visio Tessera : 29 € par mois, prélèvement le 5.", "fr", "note",
     [("facture FA-0938", "fr", "identifiant"), ("cost of the video consultation platform", "en", "crosslingue"), ("combien coûte l'outil de téléconsultation ?", "fr", "indirecte")]),
]

MULTIHOP = [
    ("Mon interlocuteur à la mairie pour le trail est Grégory Lemaire.",
     "Grégory Lemaire n'est joignable que le matin, au service des sports.",
     [("quand appeler mon contact mairie pour le trail ?", "fr"), ("best time to call my town hall contact for the race", "en")]),
    ("The clinic's shockwave device is a Storz Masterpuls.",
     "Le Masterpuls doit être révisé tous les 18 mois ; dernière révision en janvier dernier.",
     [("quand réviser l'appareil d'ondes de choc ?", "fr"), ("next service due for the shockwave machine", "en")]),
    ("Mon parrain dans le réseau de kinés du sport est Alain Verbeke.",
     "Alain Verbeke a été kiné de l'équipe de France de handball pendant dix ans.",
     [("quelle expérience a mon parrain ?", "fr"), ("my sponsor's background in sports physio", "en")]),
    ("Le livre est découpé en 12 chapitres ; le chapitre 7 porte sur la course à pied.",
     "Le chapitre sur la course à pied doit être relu par la coach Mélodie Ramez.",
     [("qui relit le chapitre 7 ?", "fr"), ("who reviews chapter seven of the book", "en")]),
    ("Mon frère Yanis vit à Bruxelles.",
     "Le congrès de kinésithérapie du sport se tient à Bruxelles du 4 au 6 avril.",
     [("où dormir pendant le congrès de kiné du sport ?", "fr"), ("who could host me during the sports physio congress", "en")]),
    ("Les tenues du club sont fabriquées par Kiprun Team.",
     "Kiprun Team demande un minimum de 30 pièces par commande.",
     [("combien de maillots au minimum pour la commande du club ?", "fr"), ("minimum order for the club kits", "en")]),
    ("L'étudiant stagiaire de cette année s'appelle Hugo Masset.",
     "Hugo Masset passe ses partiels toute la deuxième quinzaine de janvier.",
     [("le stagiaire est-il là fin janvier ?", "fr"), ("is the intern available in late January", "en")]),
    ("L'assemblée générale du club a lieu le dernier vendredi de novembre.",
     "Le dernier vendredi de novembre, je suis de garde au centre de rééducation.",
     [("faut-il déplacer l'AG du club ?", "fr"), ("conflict with the club's general meeting", "en")]),
    ("Our largest corporate client is the logistics firm Valtrans.",
     "Valtrans a 340 salariés sur son site de Lesquin.",
     [("combien de salariés a notre plus gros client entreprise ?", "fr"), ("headcount of our largest corporate client", "en")]),
    ("Le site du cabinet a été fait par l'agence Pixelweb.",
     "Pixelweb a été rachetée et ne fait plus de maintenance.",
     [("qui maintient le site du cabinet ?", "fr"), ("who maintains the clinic website", "en")]),
    ("La salle polyvalente de Wazemmes nous prête sa grande salle pour les ateliers seniors.",
     "La salle polyvalente de Wazemmes ferme pour travaux en février.",
     [("les ateliers seniors peuvent-ils avoir lieu en février ?", "fr"), ("can the seniors workshops run in February", "en")]),
    ("Le podcast du club s'appelle « Dans les foulées ».",
     "« Dans les foulées » est monté avec Audacity par Clémence.",
     [("qui fait le montage du podcast du club ?", "fr"), ("who edits the running club podcast", "en")]),
]

UPDATES = [
    ("Le tarif de la séance hors convention est de 45 €.", "Nouveau tarif hors convention depuis janvier : 52 € la séance.",
     [("combien coûte une séance hors convention ?", "fr"), ("current price of a non-reimbursed session", "en")]),
    ("Le cabinet est au 3 rue Gambetta.", "Le cabinet a déménagé : nous sommes désormais au 18 rue de Wazemmes.",
     [("adresse du cabinet", "fr"), ("clinic address", "en")]),
    ("Mon numéro de portable pro est le 06 41 22 18 90.", "Changement de numéro pro : 07 61 03 44 25.",
     [("numéro de portable professionnel de Malik", "fr"), ("Malik's work mobile number", "en")]),
    ("Le club s'entraîne le samedi à 9 h au parc de la Citadelle.", "La sortie longue du club passe au dimanche à 8 h 30 au parc de la Citadelle.",
     [("quand a lieu la sortie longue du club ?", "fr"), ("weekend long run time", "en")]),
    ("Inès travaille à 80 % au cabinet.", "Inès est repassée à temps plein au cabinet depuis la rentrée.",
     [("temps de travail d'Inès", "fr"), ("is Inès full time at the clinic", "en")]),
    ("Le club a 15 bénévoles actifs.", "Le club compte maintenant 24 bénévoles actifs.",
     [("combien de bénévoles a le club ?", "fr"), ("number of active volunteers", "en")]),
    ("My running watch is a Garmin Forerunner 245.", "New watch: I switched to a Coros Pace 3.",
     [("quelle montre de course j'utilise ?", "fr"), ("which running watch do I use", "en")]),
    ("Le point d'équipe du cabinet a lieu le lundi à 13 h.", "Le point d'équipe du cabinet est déplacé au vendredi à 12 h 30.",
     [("quand a lieu la réunion d'équipe du cabinet ?", "fr"), ("weekly team meeting slot", "en")]),
    ("Objectif d'écriture : 1 000 mots par jour.", "Objectif d'écriture revu : 500 mots par jour, mais sans exception.",
     [("combien de mots j'écris par jour ?", "fr"), ("daily writing target", "en")]),
    ("Les comptes du club sont tenus sur un tableur Excel.", "Les comptes du club sont désormais tenus sur l'application Assoconnect.",
     [("outil de comptabilité du club", "fr"), ("what tool tracks the club accounts", "en")]),
    ("Mon contact chez Kinémat est Laurent.", "Laurent a quitté Kinémat ; je passe maintenant par Sabrina Ouali.",
     [("qui est mon contact chez Kinémat ?", "fr"), ("my sales contact at Kinémat", "en")]),
    ("My publisher wants 60,000 words.", "The publisher cut the target length: the book must now be 45,000 words.",
     [("longueur demandée pour le livre", "fr"), ("required word count for the book", "en")]),
]

UNANSWERABLE = [
    ("quel est le nom de mon perroquet ?", "fr"), ("what is my horse called", "en"),
    ("quelle moto j'ai ?", "fr"), ("which motorbike do I ride", "en"),
    ("quel est mon livre de chevet ?", "fr"), ("my favourite novel", "en"),
    ("quelle est ma taille de chemise ?", "fr"), ("my shirt size", "en"),
    ("date de mon divorce", "fr"), ("when did I get divorced", "en"),
    ("quel est mon ascendant ?", "fr"), ("my rising sign", "en"),
    ("code de l'alarme de la maison", "fr"), ("home alarm code", "en"),
    ("numéro de ma carte vitale", "fr"), ("my social security number", "en"),
    ("comment s'appelle mon ophtalmo ?", "fr"), ("my eye doctor's name", "en"),
    ("quelle équipe de rugby je supporte ?", "fr"), ("which basketball team do I follow", "en"),
    ("est-ce que je parle allemand ?", "fr"), ("do I speak Japanese", "en"),
    ("quel est mon parfum préféré ?", "fr"), ("my favourite perfume", "en"),
    ("où suis-je allé en voyage de noces ?", "fr"), ("where was my honeymoon", "en"),
    ("comment s'appelle ma fille ?", "fr"), ("what is my daughter's name", "en"),
    ("quel jeu vidéo je préfère ?", "fr"), ("favourite video game", "en"),
    ("ai-je une résidence secondaire ?", "fr"), ("do I own a holiday home", "en"),
    ("quel est mon dessert préféré ?", "fr"), ("my favourite dessert", "en"),
    ("dans quel lycée suis-je allé ?", "fr"), ("which high school did I go to", "en"),
    ("quel ordinateur portable j'ai à la maison ?", "fr"), ("what laptop do I own", "en"),
    ("ai-je déjà sauté en parachute ?", "fr"), ("have I ever been skydiving", "en"),
]

# ── Distracteurs : vocabulaire voisin (autres kinés, autres clubs, autres salles…) ──
_PEOPLE = ["Bruno Lefebvre", "Céline Dupuis", "Kevin Mercier", "Sandrine Hoste", "Jérémy Wattez", "Aurore Delmotte",
           "Fabien Leroy", "Gaëlle Hennion", "Mathieu Caron", "Elise Debruyne", "Rachid Amrani", "Lucie Vermeersch",
           "Olivier Ponchel", "Marion Dewailly", "Tom Becquart", "Nora Bensalem", "Peter Hughes", "Hannah Mills",
           "Daniel Okafor", "Sofie Janssens", "Mark Turner", "Grace Liu"]
_ORGS = ["Cabinet Kiné Fives", "Centre Médical Vauban", "Club Athlétique Roubaix", "Les Gazelles de Tourcoing",
         "Maison de Santé Hellemmes", "Fit & Form Villeneuve", "Association Sport Seniors Lomme", "Pharmacie du Beffroi",
         "Clinique des Sports Marcq", "Running Team Armentières", "Northwind Fitness", "Brookside Physio"]
_EQUIP = ["une table électrique", "un appareil de pressothérapie", "un tapis de course", "des haltères réglables",
          "un plateau de Freeman", "une presse à cuisses", "un appareil d'électrothérapie", "des élastiques de rééducation"]
_EQUIP_EN = ["a treadmill", "a balance board", "a leg press", "a TENS unit", "foam rollers", "resistance bands"]
_RACES = ["les 10 km de Villeneuve", "le semi de Lille", "la route du Louvre", "le cross de Lambersart",
          "les Boucles de la Marque", "le trail des Weppes", "les 20 km de Bruxelles"]
_TOPICS = ["la tendinopathie d'Achille", "l'entorse de cheville", "la lombalgie chronique", "le syndrome rotulien",
           "la rééducation de l'épaule", "les étirements avant course", "la prévention des chutes", "la posture au bureau",
           "le renforcement du gainage", "la récupération après marathon"]
_TOPICS_EN = ["hamstring injuries", "load management", "running economy", "ankle sprains", "core stability"]
_CITIES = ["Douai", "Arras", "Valenciennes", "Dunkerque", "Béthune", "Lens", "Cambrai", "Calais", "Tournai"]
_MONTHS = ["janvier", "février", "mars", "mai", "juin", "juillet", "octobre", "décembre"]
_DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"]
_DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

_TEMPLATES_FR = [
    "{person} cherche un remplaçant kiné à {city} pour {n} semaines cet été.",
    "{org} veut acheter {equip} et demande mon avis.",
    "Le tarif de {person} pour une séance à domicile est de {rate} €.",
    "{person} préfère qu'on lui écrive par mail plutôt que par SMS.",
    "Formation sur {topic} proposée par {org} le {day} {nday} {month}.",
    "{org} organise {race} ; ils cherchent des bénévoles au ravitaillement.",
    "Article à lire sur {topic}, conseillé par {person}.",
    "{person} habite à {city} et vient en covoiturage aux réunions régionales.",
    "{org} a réglé sa cotisation de {month} avec {delay} jours de retard.",
    "Idée de chapitre : {topic}, avec un exemple tiré de {race}.",
    "{person} a couru {race} en {h} h {mm}.",
    "{org} ouvre un créneau de {topic} le {day} soir.",
    "Le local de {org} est à {city}, à côté de la gare.",
    "{person} a recommandé {org} pour la location de {equip}.",
    "Penser à renvoyer la convention de stage à {org} avant {day}.",
    "{org} a {n} adhérents et un budget annuel d'environ {k} 000 €.",
    "Le parking de {org} est payant après {hh} h.",
    "{person} propose un atelier sur {topic} pour {org}.",
    "Réunion régionale des kinés à {city} le {day} {nday} {month}.",
    "{org} a changé de logiciel d'agenda en {month}.",
]
_TEMPLATES_EN = [
    "{person} is looking for a locum physio in {city} for {n} weeks.",
    "{org} asked whether {equip_en} is worth buying.",
    "Webinar on {topic_en} hosted by {org} on {dayen}.",
    "{person} ran {race} in {h}:{mm}.",
    "{person} prefers phone calls to emails.",
    "{org} needs volunteers for {race}.",
    "Reading note: a review paper on {topic_en}, shared by {person}.",
    "{org} charges {rate} € per session for {topic_en} rehab.",
    "{person} moved to {city} and opened a small practice.",
    "{org} reported {n} new members this quarter.",
]


def _fill(rng: random.Random) -> dict:
    return dict(
        person=rng.choice(_PEOPLE), org=rng.choice(_ORGS), equip=rng.choice(_EQUIP), equip_en=rng.choice(_EQUIP_EN),
        race=rng.choice(_RACES), topic=rng.choice(_TOPICS), topic_en=rng.choice(_TOPICS_EN), city=rng.choice(_CITIES),
        month=rng.choice(_MONTHS), day=rng.choice(_DAYS), dayen=rng.choice(_DAYS_EN), nday=rng.randrange(1, 29),
        rate=rng.randrange(30, 90), delay=rng.randrange(5, 60), n=rng.randrange(2, 400), h=rng.randrange(0, 3),
        mm=f"{rng.randrange(0, 60):02d}", k=rng.randrange(3, 90), hh=rng.randrange(8, 20),
    )


def _lang(text: str, kind: str) -> str:
    if text.startswith(("The ", "Our ", "My ", "I ", "We ")):
        return "en"
    return "fr"


SPEC = {
    "persona": "Malik Benhamou (fictif), kinésithérapeute associé à Lille + président d'un club de course (fictif)",
    "simple": SIMPLE, "multihop": MULTIHOP, "updates": UPDATES, "unanswerable": UNANSWERABLE,
    "pools": {"p_fr": 0.6, "templates_fr": _TEMPLATES_FR, "templates_en": _TEMPLATES_EN, "fill": _fill},
    "lang_of": _lang,
}


def build(seed: int = SEED) -> dict:
    return build_from(SPEC, seed, VERSION)


def main() -> None:
    ds = build()
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(ds, f, ensure_ascii=False, indent=1)
    kinds: dict[str, int] = {}
    for q in ds["queries"]:
        kinds[q["kind"]] = kinds.get(q["kind"], 0) + 1
    print(f"{DATASET_PATH} : {len(ds['memories'])} souvenirs (cœur {ds['n_core']}), "
          f"{len(ds['queries'])} questions {kinds}")


if __name__ == "__main__":
    main()
