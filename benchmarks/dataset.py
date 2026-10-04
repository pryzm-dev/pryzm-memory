"""Génération DÉTERMINISTE du jeu de données du banc mémoire (v1).

Profil fictif : Léa Moreau, développeuse freelance à Nantes et cofondatrice de
« Carnetto » (SaaS fictif de carnets de commandes pour artisans). Toutes les
personnes, entreprises clientes et chiffres sont INVENTÉS ; aucune donnée réelle
d'utilisateur. Les noms d'outils grand public (Figma, Stripe…) servent de décor.

Contenu :
  - 45 faits simples, chacun interrogé 3 fois (paraphrase FR, question en
    anglais = interlinguistique, question indirecte à faible recouvrement lexical) ;
    quelques faits portent un identifiant exact (facture, ticket, code d'erreur) ;
  - 12 paires « multi-sauts » (la réponse demande DEUX souvenirs), 2 questions chacune ;
  - 12 paires « mise à jour » (ancien fait périmé + nouveau fait), 2 questions
    chacune : le souvenir attendu est le NOUVEAU, l'ancien est marqué `stale` ;
  - 40 questions SANS réponse dans la base (sujets jamais évoqués) ;
  - des souvenirs « distracteurs » générés par gabarits (graine fixe) pour faire
    varier la taille de la base de 100 à 2000 souvenirs. Les distracteurs ne
    répondent à aucune question (vérifié par test) mais partagent volontairement
    du vocabulaire (TJM d'autres personnes, hébergement d'autres projets…).

Usage :
    python -m bench.dataset            # écrit bench/data/dataset_v1.json
"""
from __future__ import annotations

import json
import os
import random

SEED = 20261002
VERSION = "v1"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATASET_PATH = os.path.join(DATA_DIR, f"dataset_{VERSION}.json")
MAX_DISTRACTORS = 2000

# ── Faits simples : (texte, langue, type, [(question, langue, style), ×3]) ────
SIMPLE = [
    ("Je préfère qu'on me tutoie et qu'on aille droit au but dans les réponses, sans formules de politesse.", "fr", "preference",
     [("comment Léa veut qu'on lui parle", "fr", "paraphrase"), ("preferred tone when answering her", "en", "crosslingue"), ("faut-il vouvoyer l'utilisatrice ?", "fr", "indirecte")]),
    ("Ma stack par défaut pour les nouveaux projets clients : Next.js côté front, FastAPI côté back, PostgreSQL pour la base.", "fr", "technical_decision",
     [("technologies utilisées par défaut sur un projet client", "fr", "paraphrase"), ("default backend framework for client projects", "en", "crosslingue"), ("avec quoi je code l'API d'habitude ?", "fr", "indirecte")]),
    ("Je suis allergique aux arachides : à signaler pour tout restaurant réservé pour moi.", "fr", "user",
     [("allergie alimentaire de Léa", "fr", "paraphrase"), ("does she have any food allergy", "en", "crosslingue"), ("puis-je lui commander un plat avec une sauce aux cacahuètes ?", "fr", "indirecte")]),
    ("Mon expert-comptable est le cabinet Roussel & Associés à Nantes ; ma référente s'appelle Nadia Roussel.", "fr", "context",
     [("qui s'occupe de ma comptabilité", "fr", "paraphrase"), ("who is my accountant", "en", "crosslingue"), ("à qui envoyer mes justificatifs de dépenses ?", "fr", "indirecte")]),
    ("Carnetto est hébergé chez Scaleway, région Paris (fr-par), sur une instance DEV1-M.", "fr", "architecture",
     [("hébergeur de Carnetto", "fr", "paraphrase"), ("Carnetto hosting provider and region", "en", "crosslingue"), ("dans quel datacenter tournent les serveurs de mon SaaS ?", "fr", "indirecte")]),
    ("Nordhaus Logistics pays invoices at 45 days end of month, never earlier.", "en", "context",
     [("délai de paiement des factures Nordhaus", "fr", "crosslingue"), ("when does Nordhaus settle its invoices", "en", "paraphrase"), ("combien de temps attendre avant de relancer Nordhaus pour un impayé ?", "fr", "indirecte")]),
    ("Je ne travaille jamais le mercredi après-midi : c'est réservé à mes enfants.", "fr", "preference",
     [("disponibilité le mercredi après-midi", "fr", "paraphrase"), ("is she available on Wednesday afternoons", "en", "crosslingue"), ("peut-on caler un rendez-vous client mercredi à 15 h ?", "fr", "indirecte")]),
    ("Facture F-2026-0412 envoyée à Studio Kélia le 3 avril pour 2 400 € HT, refonte du site vitrine.", "fr", "note",
     [("facture F-2026-0412", "fr", "identifiant"), ("amount of invoice F-2026-0412", "en", "crosslingue"), ("combien j'ai facturé Studio Kélia pour la refonte de leur site ?", "fr", "indirecte")]),
    ("Bug Carnetto : l'export PDF plante avec ERR_FONT_SUBSET quand une commande contient des emojis ; contournement : retirer les emojis avant la génération.", "fr", "bug",
     [("erreur ERR_FONT_SUBSET", "fr", "identifiant"), ("PDF export crash workaround", "en", "crosslingue"), ("pourquoi certaines commandes refusent de s'imprimer ?", "fr", "indirecte")]),
    ("Mon objectif 2026 : atteindre 3 000 € de revenu mensuel récurrent sur Carnetto d'ici décembre.", "fr", "intention",
     [("objectif de revenu récurrent de Carnetto", "fr", "paraphrase"), ("revenue goal for this year", "en", "crosslingue"), ("combien je veux que mon SaaS rapporte chaque mois ?", "fr", "indirecte")]),
    ("I write all commit messages in English, using the Conventional Commits format.", "en", "preference",
     [("langue des messages de commit", "fr", "crosslingue"), ("commit message convention", "en", "paraphrase"), ("en quelle langue rédiger l'historique git ?", "fr", "indirecte")]),
    ("Mes mails pro passent par Fastmail avec mon domaine lea-moreau.dev.", "fr", "context",
     [("fournisseur de messagerie professionnelle", "fr", "paraphrase"), ("which email provider do I use for work", "en", "crosslingue"), ("où configurer les enregistrements MX de mon domaine ?", "fr", "indirecte")]),
    ("Mon associé Hugo Lambert gère le commercial et les démos de Carnetto ; moi, le produit et le code.", "fr", "context",
     [("rôle de Hugo Lambert dans Carnetto", "fr", "paraphrase"), ("who handles sales at Carnetto", "en", "crosslingue"), ("qui s'occupe de vendre l'appli aux artisans ?", "fr", "indirecte")]),
    ("Pour les maquettes, je travaille sur Figma avec une grille de 8 px et la police Inter.", "fr", "preference",
     [("outil de maquette et grille utilisée", "fr", "paraphrase"), ("design grid size and font", "en", "crosslingue"), ("quel espacement de base pour mes composants d'interface ?", "fr", "indirecte")]),
    ("Le contrat avec Brasserie Lumen inclut 6 heures de maintenance par mois ; au-delà, c'est facturé 90 € l'heure.", "fr", "context",
     [("heures de maintenance incluses pour Brasserie Lumen", "fr", "paraphrase"), ("Lumen maintenance hours included in the contract", "en", "crosslingue"), ("si la brasserie demande 10 h de corrections ce mois-ci, combien facturer ?", "fr", "indirecte")]),
    ("Je fais du trail : prochaine course prévue, l'Ultra Trail de la Côte de Granit en mai.", "fr", "user",
     [("prochaine course de trail", "fr", "paraphrase"), ("upcoming running race", "en", "crosslingue"), ("pourquoi je bloque un week-end de mai en Bretagne ?", "fr", "indirecte")]),
    ("Je suis végétarienne depuis 2019.", "fr", "user",
     [("est-ce que Léa mange de la viande", "fr", "paraphrase"), ("is she vegetarian", "en", "crosslingue"), ("puis-je l'inviter dans un restaurant de grillades ?", "fr", "indirecte")]),
    ("Le nom de domaine carnetto.fr expire le 14 février ; il est chez OVH, avec un renouvellement manuel.", "fr", "todo",
     [("date d'expiration du domaine carnetto.fr", "fr", "paraphrase"), ("domain renewal date for Carnetto", "en", "crosslingue"), ("qu'est-ce qui risque de tomber en panne mi-février ?", "fr", "indirecte")]),
    ("Je veux tester un programme de parrainage Carnetto : un mois offert au parrain et au filleul.", "fr", "intention",
     [("idée de programme de parrainage", "fr", "paraphrase"), ("referral program idea", "en", "crosslingue"), ("comment récompenser les clients qui recommandent l'appli ?", "fr", "indirecte")]),
    ("Tom Becker, CTO at Nordhaus Logistics, insists on a weekly status report every Friday before noon.", "en", "context",
     [("rapport hebdomadaire demandé par Nordhaus", "fr", "crosslingue"), ("Tom Becker reporting expectations", "en", "paraphrase"), ("qu'est-ce que je dois envoyer avant vendredi midi ?", "fr", "indirecte")]),
    ("Décision : on abandonne Stripe Checkout au profit de Stripe Billing pour gérer les abonnements Carnetto (proratas, essais gratuits).", "fr", "technical_decision",
     [("choix de Stripe pour les abonnements", "fr", "paraphrase"), ("subscription billing decision", "en", "crosslingue"), ("pourquoi ne plus utiliser la page de paiement hébergée ?", "fr", "indirecte")]),
    ("Mon bureau est en coworking à La Cantine, quai de la Fosse à Nantes ; mon badge ouvre de 7 h à 22 h.", "fr", "context",
     [("où se trouve mon bureau", "fr", "paraphrase"), ("coworking space location", "en", "crosslingue"), ("jusqu'à quelle heure je peux rester travailler au bureau ?", "fr", "indirecte")]),
    ("Je déteste les réunions de plus de 30 minutes : proposer par défaut des créneaux de 25 minutes.", "fr", "preference",
     [("durée préférée des réunions", "fr", "paraphrase"), ("default meeting length", "en", "crosslingue"), ("combien de temps bloquer pour un point avec un prospect ?", "fr", "indirecte")]),
    ("Sauvegardes Carnetto : dump PostgreSQL chaque nuit à 3 h vers un bucket Backblaze B2, rétention 30 jours.", "fr", "architecture",
     [("politique de sauvegarde de Carnetto", "fr", "paraphrase"), ("backup retention period", "en", "crosslingue"), ("un client a supprimé ses données il y a 3 semaines, peut-on les récupérer ?", "fr", "indirecte")]),
    ("Numéro SIRET de mon entreprise individuelle : 852 147 963 00027.", "fr", "context",
     [("SIRET 852 147 963", "fr", "identifiant"), ("company registration number", "en", "crosslingue"), ("quel identifiant légal mettre sur un devis ?", "fr", "indirecte")]),
    ("Studio Kélia veut une palette sobre : noir, blanc cassé et un seul accent terracotta.", "fr", "preference",
     [("palette de couleurs de Studio Kélia", "fr", "paraphrase"), ("Kelia brand colours", "en", "crosslingue"), ("quelle teinte pour les boutons du site de Kélia ?", "fr", "indirecte")]),
    ("Je lis le soir ; en ce moment, « Le Mythe de Sisyphe » de Camus.", "fr", "user",
     [("livre que je lis en ce moment", "fr", "paraphrase"), ("current book she is reading", "en", "crosslingue"), ("qu'est-ce que j'ai sur ma table de chevet ?", "fr", "indirecte")]),
    ("Sur Carnetto, le plan Artisan coûte 19 € par mois et le plan Atelier 49 € par mois.", "fr", "context",
     [("prix des formules Carnetto", "fr", "paraphrase"), ("Carnetto pricing tiers", "en", "crosslingue"), ("combien paie un boulanger qui prend l'offre de base ?", "fr", "indirecte")]),
    ("My git repositories live on a self-hosted Forgejo instance; GitHub is only used for open-source mirrors.", "en", "technical_decision",
     [("où sont hébergés mes dépôts git", "fr", "crosslingue"), ("git hosting choice", "en", "paraphrase"), ("où pousser le code d'un nouveau projet client ?", "fr", "indirecte")]),
    ("Ma banque pro est Qonto ; les virements clients arrivent sur le compte se terminant par 4471.", "fr", "context",
     [("banque professionnelle", "fr", "paraphrase"), ("business bank account", "en", "crosslingue"), ("où arrivent les paiements de mes clients ?", "fr", "indirecte")]),
    ("Je parle couramment anglais et allemand, et j'ai un niveau B1 en italien.", "fr", "user",
     [("langues que je parle", "fr", "paraphrase"), ("languages she speaks", "en", "crosslingue"), ("puis-je faire la démo en allemand chez un client de Hambourg ?", "fr", "indirecte")]),
    ("Bug résolu : les notifications push iOS ne partaient plus car le certificat APNs avait expiré ; renouvelé le 12 mars, rappel annuel à prévoir.", "fr", "bug",
     [("notifications iOS qui ne partaient plus", "fr", "paraphrase"), ("APNs certificate expiry", "en", "crosslingue"), ("pourquoi les clients sur iPhone ne recevaient plus d'alertes ?", "fr", "indirecte")]),
    ("Mon assurance RC Pro est chez Hiscox, plafond 500 000 €, contrat renouvelé chaque septembre.", "fr", "context",
     [("assurance responsabilité civile professionnelle", "fr", "paraphrase"), ("professional liability insurance", "en", "crosslingue"), ("un client exige une attestation d'assurance, à qui la demander ?", "fr", "indirecte")]),
    ("Règle : jamais de mise en production le vendredi après 16 h.", "fr", "preference",
     [("règle de déploiement le vendredi", "fr", "paraphrase"), ("deployment freeze rule", "en", "crosslingue"), ("puis-je livrer la nouvelle version vendredi à 17 h ?", "fr", "indirecte")]),
    ("Le logo de Carnetto a été dessiné par Inès Faure, illustratrice freelance à Rennes.", "fr", "context",
     [("qui a dessiné le logo de Carnetto", "fr", "paraphrase"), ("Carnetto logo designer", "en", "crosslingue"), ("à qui demander une variante de l'icône de l'appli ?", "fr", "indirecte")]),
    ("Je vais chez l'ostéopathe tous les deux mois à cause d'un mal de dos chronique.", "fr", "user",
     [("problème de dos et suivi ostéopathe", "fr", "paraphrase"), ("chronic back pain", "en", "crosslingue"), ("pourquoi j'ai un rendez-vous médical régulier tous les deux mois ?", "fr", "indirecte")]),
    ("Analytics on Carnetto use a self-hosted Plausible instance, cookieless, so no consent banner is needed.", "en", "technical_decision",
     [("outil de mesure d'audience de Carnetto", "fr", "crosslingue"), ("web analytics tool", "en", "paraphrase"), ("faut-il un bandeau cookies sur le site ?", "fr", "indirecte")]),
    ("Atelier Verrier Duval paie toujours par chèque ; les relances se font par téléphone, jamais par mail.", "fr", "context",
     [("moyen de paiement de l'Atelier Verrier Duval", "fr", "paraphrase"), ("how does Duval pay", "en", "crosslingue"), ("comment relancer le verrier pour une facture en retard ?", "fr", "indirecte")]),
    ("Ma fille Zoé a cours de piano le samedi matin à 10 h.", "fr", "user",
     [("cours de piano de Zoé", "fr", "paraphrase"), ("daughter's piano lesson time", "en", "crosslingue"), ("suis-je libre samedi vers 10 h ?", "fr", "indirecte")]),
    ("TVA : je suis au régime réel, avec une TVA à 20 % sur toutes mes prestations.", "fr", "context",
     [("taux de TVA appliqué", "fr", "paraphrase"), ("VAT rate on my services", "en", "crosslingue"), ("combien ajouter au montant HT sur une facture ?", "fr", "indirecte")]),
    ("Idée : ajouter à Carnetto un mode hors ligne pour les artisans sur les marchés sans réseau.", "fr", "intention",
     [("idée de mode hors ligne", "fr", "paraphrase"), ("offline mode idea", "en", "crosslingue"), ("comment prendre des commandes quand il n'y a pas de 4G ?", "fr", "indirecte")]),
    ("Pour les tests de bout en bout, on utilise Playwright, lancé dans la CI à chaque merge request.", "fr", "technical_decision",
     [("outil de tests de bout en bout", "fr", "paraphrase"), ("end-to-end testing framework", "en", "crosslingue"), ("comment vérifier que le parcours de commande marche avant de fusionner ?", "fr", "indirecte")]),
    ("Je bois mon café sans sucre, et plus aucun café après 14 h.", "fr", "preference",
     [("habitudes de café", "fr", "paraphrase"), ("coffee habits", "en", "crosslingue"), ("lui proposer un expresso à 16 h ?", "fr", "indirecte")]),
    ("Le prospect Boulangerie Fournil des Halles attend une démo de Carnetto le 18 du mois.", "fr", "todo",
     [("date de la démo pour le Fournil des Halles", "fr", "paraphrase"), ("bakery prospect demo date", "en", "crosslingue"), ("quand dois-je présenter l'appli au boulanger des Halles ?", "fr", "indirecte")]),
    ("Ticket SUP-1187 : un client signale des commandes en double après synchronisation ; cause trouvée : double clic sur Valider.", "fr", "bug",
     [("ticket SUP-1187", "fr", "identifiant"), ("cause of duplicate orders issue", "en", "crosslingue"), ("pourquoi certaines commandes apparaissent deux fois ?", "fr", "indirecte")]),
]

# ── Multi-sauts : (souvenir A, souvenir B, [questions]) ───────────────────────
MULTIHOP = [
    ("Chez Brasserie Lumen, mon interlocutrice principale est Julie Marchand.",
     "Julie Marchand ne lit pas ses mails : la joindre uniquement par Signal.",
     [("comment joindre mon contact chez Brasserie Lumen ?", "fr"), ("best channel to reach my contact at Brasserie Lumen", "en")]),
    ("Le serveur de staging de Carnetto s'appelle « orque ».",
     "La machine orque a été réinstallée sous Debian 12 en janvier.",
     [("quel système d'exploitation tourne sur le staging de Carnetto ?", "fr"), ("which OS runs on Carnetto's staging server", "en")]),
    ("Mon mentor au réseau Initiative Nantes est Bernard Lefèvre.",
     "Bernard Lefèvre a dirigé une imprimerie pendant 25 ans avant de prendre sa retraite.",
     [("dans quel secteur mon mentor a-t-il travaillé ?", "fr"), ("my mentor's professional background", "en")]),
    ("The Nordhaus project codename is Kranich.",
     "Kranich doit être livré avant le 30 novembre, avec des pénalités de retard prévues au contrat.",
     [("date limite de livraison du projet Nordhaus", "fr"), ("deadline for the Nordhaus project", "en")]),
    ("Ma sœur Claire habite à Lyon.",
     "Je dois aller à Lyon pour le salon Artisanat Pro le 9 octobre.",
     [("chez qui puis-je dormir pendant le salon Artisanat Pro ?", "fr"), ("who could host me during the Artisanat Pro trade show", "en")]),
    ("Le fournisseur d'envoi de SMS de Carnetto est Textilo.",
     "Textilo facture 0,045 € par SMS envoyé en France.",
     [("combien coûte un SMS de rappel envoyé par Carnetto ?", "fr"), ("cost per reminder text message sent by Carnetto", "en")]),
    ("Le développeur freelance qui m'aide en renfort s'appelle Karim Haddad.",
     "Karim Haddad est indisponible tout le mois d'août.",
     [("mon développeur en renfort est-il disponible en août ?", "fr"), ("is my backup developer available in August", "en")]),
    ("La réunion d'associés de Carnetto a lieu le premier lundi de chaque mois.",
     "Le premier lundi d'octobre, je serai en déplacement à Bordeaux toute la journée.",
     [("faut-il déplacer la réunion d'associés d'octobre ?", "fr"), ("conflict with the October partners meeting", "en")]),
    ("Our biggest customer by revenue is the bakery chain Maison Garnier.",
     "Maison Garnier utilise Carnetto dans 14 boutiques.",
     [("combien de boutiques a notre plus gros client ?", "fr"), ("number of shops of our largest customer", "en")]),
    ("Le site de Studio Kélia est déployé sur Netlify.",
     "Le compte Netlify est au nom de Hugo, pas au mien.",
     [("qui possède le compte d'hébergement du site de Studio Kélia ?", "fr"), ("who owns the hosting account for the Studio Kélia website", "en")]),
    ("La Librairie La Grande Ourse m'a commandé un atelier « coder son site » pour adolescents.",
     "Les ateliers pour adolescents sont facturés 350 € la demi-journée.",
     [("combien facturer l'atelier de La Grande Ourse ?", "fr"), ("price for the workshop ordered by La Grande Ourse", "en")]),
    ("Le dépôt du site de Brasserie Lumen s'appelle lumen-vitrine.",
     "Le dépôt lumen-vitrine utilise Astro 4 et Tailwind.",
     [("avec quel framework est fait le site de Brasserie Lumen ?", "fr"), ("which framework powers the Brasserie Lumen website", "en")]),
]

# ── Mises à jour : (ancien, nouveau, [questions]) ─────────────────────────────
UPDATES = [
    ("Mon TJM est de 450 € HT.", "J'ai augmenté mon TJM : 520 € HT à partir de cette année.",
     [("quel est mon tarif journalier actuel ?", "fr"), ("my current day rate", "en")]),
    ("J'habite rue Paul Bellamy à Nantes.", "J'ai déménagé : j'habite maintenant à Rezé, 4 allée des Tilleuls.",
     [("où est-ce que j'habite ?", "fr"), ("my home address", "en")]),
    ("Mon numéro pro est le 06 12 34 56 78.", "Nouveau numéro pro depuis mon changement d'opérateur : 07 98 76 54 32.",
     [("quel est mon numéro de téléphone professionnel ?", "fr"), ("my work phone number", "en")]),
    ("Le front de Carnetto est en Vue 2.", "Migration terminée : le front de Carnetto est maintenant en SvelteKit.",
     [("framework front-end de Carnetto", "fr"), ("Carnetto frontend framework", "en")]),
    ("Hugo travaille à mi-temps sur Carnetto.", "Hugo est passé à temps plein sur Carnetto depuis le 1er septembre.",
     [("Hugo est-il à temps plein sur Carnetto ?", "fr"), ("how much time Hugo spends on Carnetto", "en")]),
    ("Carnetto compte 12 clients payants.", "Carnetto compte désormais 47 clients payants.",
     [("combien de clients payants a Carnetto ?", "fr"), ("number of paying customers", "en")]),
    ("My preferred code editor is VS Code.", "Switched editors: I now use Zed full-time.",
     [("quel éditeur de code j'utilise ?", "fr"), ("which code editor do I use", "en")]),
    ("La réunion hebdo avec Brasserie Lumen est le mardi à 9 h.", "La réunion hebdo avec Brasserie Lumen passe au jeudi à 14 h.",
     [("quand a lieu le point hebdomadaire avec Lumen ?", "fr"), ("weekly meeting slot with Lumen", "en")]),
    ("Objectif sport : courir 3 fois par semaine.", "Nouvel objectif sport, revu à la baisse : 2 sorties par semaine à cause du dos.",
     [("combien de fois par semaine je veux courir ?", "fr"), ("weekly running target", "en")]),
    ("J'utilise Notion pour prendre mes notes.", "J'ai quitté Notion : toutes mes notes sont maintenant dans Obsidian.",
     [("quel outil j'utilise pour mes notes ?", "fr"), ("note-taking app I use", "en")]),
    ("Mon contact chez Studio Kélia est Marc.", "Marc a quitté Studio Kélia ; mon nouveau contact là-bas est Sofia Benali.",
     [("qui est mon contact chez Studio Kélia ?", "fr"), ("my contact person at Studio Kélia", "en")]),
    ("Carnetto support hours are 9am to 6pm, Monday to Friday.", "Support hours changed: Carnetto support now runs 8am to 8pm, Monday to Saturday.",
     [("horaires du support Carnetto", "fr"), ("Carnetto support opening hours", "en")]),
]

# ── Sans réponse : sujets JAMAIS évoqués dans la base (ni cœur ni distracteurs) ──
UNANSWERABLE = [
    ("comment s'appelle mon chien ?", "fr"), ("what is my cat's name", "en"),
    ("quelle voiture je conduis ?", "fr"), ("what car do I drive", "en"),
    ("quel est mon film préféré ?", "fr"), ("my favourite movie", "en"),
    ("quel est mon groupe sanguin ?", "fr"), ("my blood type", "en"),
    ("quelle est ma pointure ?", "fr"), ("my shoe size", "en"),
    ("date de mon anniversaire de mariage", "fr"), ("wedding anniversary date", "en"),
    ("quel est mon signe astrologique ?", "fr"), ("my zodiac sign", "en"),
    ("mot de passe du wifi de la maison", "fr"), ("home wifi password", "en"),
    ("numéro de mon passeport", "fr"), ("my passport number", "en"),
    ("comment s'appelle mon dentiste ?", "fr"), ("my dentist's name", "en"),
    ("quelle équipe de foot je supporte ?", "fr"), ("which football team do I support", "en"),
    ("est-ce que je joue d'un instrument de musique ?", "fr"), ("do I play a musical instrument myself", "en"),
    ("quelle est ma couleur préférée ?", "fr"), ("my favourite colour", "en"),
    ("où suis-je partie en vacances l'été dernier ?", "fr"), ("where did I go on holiday last summer", "en"),
    ("quel est le prénom de mon fils ?", "fr"), ("what is my son's first name", "en"),
    ("quelle est ma série télé préférée ?", "fr"), ("favourite TV series", "en"),
    ("ai-je un crédit immobilier en cours ?", "fr"), ("do I have a mortgage", "en"),
    ("quel est mon plat préféré ?", "fr"), ("my favourite dish", "en"),
    ("à quel âge ai-je eu mon bac ?", "fr"), ("which university did I attend", "en"),
    ("quelle marque de smartphone j'utilise ?", "fr"), ("what phone model do I own", "en"),
]

# ── Distracteurs (gabarits + réservoirs disjoints des entités du cœur) ────────
_PEOPLE = ["Paul Girard", "Sophie Lemaire", "Antoine Rey", "Mélanie Petit", "Yann Le Goff", "Chloé Bertin",
           "Nicolas Faure", "Laura Chevalier", "Thomas Roux", "Emma Guérin", "Lucas Blanc", "Manon Perrin",
           "Julien Morel", "Camille Robin", "Maxime Colin", "Pauline Garnier", "Hélène Brun", "Victor Lucas",
           "Anna Schmidt", "James Carter", "Olivia Brooks", "Pedro Alves", "Sara Lindqvist", "Ethan Walsh"]
_CLIENTS = ["Fromagerie Belcour", "Cave des Trois Ponts", "Menuiserie Arvor", "Fleuriste Pétale d'Or",
            "Garage Solidaire Erdre", "Épicerie Le Panier Vert", "Atelier Céramique Kaolin", "Savonnerie Lune Douce",
            "Chocolaterie Maison Prével", "Cordonnerie du Marché", "Torréfaction Grain Noir", "Imprimerie Sillage",
            "Brightline Retail", "Harbor & Pine", "Kestrel Analytics", "Oakfield Studio"]
_PROJECTS = ["Hélios", "Mistral", "Ardoise", "Boréal", "Canopée", "Écume", "Granit", "Pollen", "Sextant", "Volute"]
_TECH = ["Django", "Laravel", "Ruby on Rails", "Express", "Spring Boot", "Flask", "NestJS", "Phoenix",
         "Nuxt", "Remix", "Angular", "SolidJS", "Gatsby", "Eleventy", "Hugo"]
_HOSTS = ["Hetzner", "Clever Cloud", "Render", "Fly.io", "Vercel", "DigitalOcean", "Infomaniak", "Railway"]
_TOOLS = ["Linear", "Trello", "Jira", "Slack", "Mattermost", "Loom", "Miro", "Excalidraw", "Sentry", "Grafana",
          "Metabase", "n8n", "Zapier", "Airtable", "Penpot", "Tally"]
_CITIES = ["Rennes", "Angers", "Bordeaux", "Lille", "Tours", "Brest", "Vannes", "Saint-Nazaire", "Poitiers", "Caen"]
_BOOKS = ["« Atomic Habits »", "« Shape Up »", "« The Mom Test »", "« Refactoring »", "« Deep Work »",
          "« Clean Architecture »", "« Zero to One »", "« Inspired »", "« Designing Data-Intensive Applications »"]
_TOPICS = ["l'accessibilité des formulaires", "le cache HTTP", "les index PostgreSQL partiels", "le rendu côté serveur",
           "les web components", "la gestion des fuseaux horaires", "les migrations de schéma sans coupure",
           "la pagination par curseur", "les files de tâches", "l'internationalisation des dates",
           "le chiffrement des sauvegardes", "la limitation de débit d'API", "les tests de charge"]
_DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
_MONTHS = ["janvier", "février", "mars", "avril", "juin", "juillet", "septembre", "novembre"]

_TEMPLATES_FR = [
    "Réunion avec {client} : ils veulent revoir la page d'accueil et ajouter un formulaire de contact.",
    "Le TJM de {person} pour la mission {project} est de {rate} € HT.",
    "{person} préfère être relancé·e par téléphone plutôt que par mail.",
    "Le projet {project} pour {client} utilise {tech} et sera hébergé chez {host}.",
    "Note de lecture {book} : retenir l'idée de réduire le périmètre plutôt que décaler la date.",
    "À creuser : {topic}, pour un futur article de blog.",
    "{client} a payé la facture de {month} avec {delay} jours de retard.",
    "Atelier découverte de {tool} prévu avec {person} un {day} matin.",
    "{person} habite à {city} et peut passer au bureau une fois par mois.",
    "Pour {client}, livrer les maquettes avant la fin du mois de {month}.",
    "Le serveur de {project} a redémarré deux fois cette semaine ; vérifier la mémoire disponible.",
    "{client} demande un devis pour une boutique en ligne d'environ {n} produits.",
    "Idée d'article : comparer {tech} et {tech2} pour un petit site vitrine.",
    "L'équipe de {client} utilise {tool} pour suivre ses tâches.",
    "Le bug d'affichage du menu sur {project} venait d'un conflit de z-index.",
    "{person} cherche un ou une freelance {tech} à {city} pour trois mois.",
    "Webinaire sur {topic} le {day} {nday} {month} à 18 h.",
    "Mission {project} terminée : {n} heures passées au total, client satisfait.",
    "{client} souhaite former deux salariés à {tool}.",
    "Le site de {client} charge en {sec} secondes sur mobile, à optimiser.",
    "Penser à envoyer le récapitulatif de la réunion à {person} avant {day}.",
    "{person} recommande {book} pour mieux mener les entretiens clients.",
    "{client} est à {city} ; prévoir un déplacement au lancement du site.",
    "Le contrat de {client} se termine fin {month} ; proposer un renouvellement.",
]
_TEMPLATES_EN = [
    "Call with {client}: they want a booking module before the summer season.",
    "{person} charges {rate} € per day for {tech} work.",
    "{person} prefers async updates over meetings.",
    "{project} staging runs on {host} with a nightly deploy.",
    "Reading note on {book}: ship the smallest useful thing first.",
    "Look into {tool} for {client}'s internal dashboard.",
    "{client} asked for a quote to migrate their site to {tech}.",
    "{person} will review the {project} pull requests on {dayen}s.",
    "{client} reported a slow checkout page on mobile.",
    "Idea: write a short guide about {tech} deployments on {host}.",
    "{person} moved to {city} and now works remotely.",
    "The {project} invoice for {client} totals {n}0 € excluding VAT.",
]
_DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


def _distractors(rng: random.Random, n: int, spec: dict | None = None) -> list[tuple[str, str]]:
    spec = spec or _V1_POOLS
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    guard = 0
    while len(out) < n and guard < n * 50:
        guard += 1
        if rng.random() < spec["p_fr"]:
            tpl, lang = rng.choice(spec["templates_fr"]), "fr"
        else:
            tpl, lang = rng.choice(spec["templates_en"]), "en"
        txt = tpl.format(**spec["fill"](rng))
        if txt not in seen:
            seen.add(txt)
            out.append((txt, lang))
    if len(out) < n:
        raise RuntimeError(f"Gabarits insuffisants : {len(out)}/{n} distracteurs uniques")
    return out


def _v1_fill(rng: random.Random) -> dict:
    tech, tech2 = rng.sample(_TECH, 2)
    return dict(
        person=rng.choice(_PEOPLE), client=rng.choice(_CLIENTS), project=rng.choice(_PROJECTS),
        tech=tech, tech2=tech2, host=rng.choice(_HOSTS), tool=rng.choice(_TOOLS), city=rng.choice(_CITIES),
        book=rng.choice(_BOOKS), topic=rng.choice(_TOPICS), day=rng.choice(_DAYS), dayen=rng.choice(_DAYS_EN),
        month=rng.choice(_MONTHS), rate=rng.randrange(300, 800, 10), delay=rng.randrange(5, 60),
        n=rng.randrange(12, 400), nday=rng.randrange(1, 29), sec=rng.randrange(3, 12),
    )


_V1_POOLS = {"p_fr": 0.72, "templates_fr": _TEMPLATES_FR, "templates_en": _TEMPLATES_EN, "fill": _v1_fill}


def _lang_v1(text: str, kind: str) -> str:
    if kind == "multihop_a":
        return "en" if text.startswith(("The ", "Our ")) else "fr"
    if kind == "update":
        return "en" if text.startswith(("My ", "Carnetto support")) else "fr"
    return "fr"


def build_from(spec: dict, seed: int, version: str) -> dict:
    """Constructeur générique : `spec` porte le contenu (faits, multi-sauts, mises à
    jour, sans-réponse, gabarits de distracteurs). Ordre des tirages aléatoires figé."""
    rng = random.Random(seed)
    memories: list[dict] = []
    queries: list[dict] = []
    lang_of = spec["lang_of"]

    def mem(text, lang, mtype, role, age_days, importance):
        mid = f"m{len(memories):04d}"
        memories.append({"id": mid, "text": text, "lang": lang, "type": mtype, "role": role,
                         "age_days": age_days, "importance": importance})
        return mid

    def query(text, lang, kind, relevant, style=None, stale=None):
        queries.append({"id": f"q{len(queries):04d}", "text": text, "lang": lang, "kind": kind,
                        "style": style or kind, "relevant": relevant, "stale": stale or []})

    for text, lang, mtype, qs in spec["simple"]:
        mid = mem(text, lang, mtype, "core", rng.randrange(5, 300), rng.randrange(5, 8))
        for qt, ql, style in qs:
            query(qt, ql, "simple", [mid], style=style)
    for a, b, qs in spec["multihop"]:
        ia = mem(a, lang_of(a, "multihop_a"), "context", "core", rng.randrange(30, 300), 6)
        ib = mem(b, lang_of(b, "multihop_b"), "context", "core", rng.randrange(5, 200), 6)
        for qt, ql in qs:
            query(qt, ql, "multihop", [ia, ib])
    for old, new, qs in spec["updates"]:
        lang = lang_of(old, "update")
        io = mem(old, lang, "context", "core", rng.randrange(330, 480), 6)
        inew = mem(new, lang, "context", "core", rng.randrange(3, 40), 6)
        for qt, ql in qs:
            query(qt, ql, "temporal", [inew], stale=[io])
    for qt, ql in spec["unanswerable"]:
        query(qt, ql, "unanswerable", [])

    n_core = len(memories)
    for txt, lang in _distractors(rng, MAX_DISTRACTORS - n_core, spec["pools"]):
        mem(txt, lang, "note", "distractor", rng.randrange(1, 500), rng.randrange(3, 8))

    return {
        "version": version, "seed": seed, "persona": spec["persona"],
        "n_core": n_core, "memories": memories, "queries": queries,
        "scales": [100, 250, 500, 1000, 2000],
    }


V1_SPEC = {
    "persona": "Léa Moreau (fictive), freelance + cofondatrice de Carnetto (fictif)",
    "simple": SIMPLE, "multihop": MULTIHOP, "updates": UPDATES, "unanswerable": UNANSWERABLE,
    "pools": _V1_POOLS, "lang_of": _lang_v1,
}


def build(seed: int = SEED) -> dict:
    return build_from(V1_SPEC, seed, VERSION)


def corpus_for_scale(ds: dict, size: int) -> list[dict]:
    """Tous les souvenirs du cœur + les premiers distracteurs jusqu'à `size`."""
    core = [m for m in ds["memories"] if m["role"] == "core"]
    dis = [m for m in ds["memories"] if m["role"] == "distractor"]
    if size < len(core):
        raise ValueError(f"taille {size} < cœur ({len(core)})")
    return core + dis[: size - len(core)]


def dataset_path(version: str = VERSION) -> str:
    return os.path.join(DATA_DIR, f"dataset_{version}.json")


def load(path: str = DATASET_PATH) -> dict:
    """`path` : chemin du JSON, ou simplement « v1 » / « v2 »."""
    if path in ("v1", "v2"):
        path = dataset_path(path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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
