# Banc mémoire Pryzm v1 : rapport

*Course du 2 octobre 2026 (commit `56437d0`, jeu `dataset_v1.json`, graine 20261002).
Résultats bruts : `backend/bench/results/` (`runs.json` = une ligne par système × taille × question ;
`summary.csv`, `paired.csv`, `tables.md`).*

## En bref

- Sur notre jeu synthétique de 2000 souvenirs, la recherche Pryzm trouve le bon souvenir **en
  première position dans 53 % des cas** (IC 95 % : 47–60 %) et **dans les 5 premiers dans 70 %
  des cas** (63–76 %).
- Elle fait **nettement mieux que la recherche par mots-clés seule** (BM25) : +0,165 de MRR
  (IC [+0,089 ; +0,237]), surtout quand la question est posée dans une autre langue que le souvenir.
- Elle **ne fait pas mieux, de façon mesurable, que la recherche sémantique seule** avec le même
  modèle (e5-small) : +0,022 de MRR, IC [−0,035 ; +0,075]. La différence n'est **pas** significative.
- Face à une **mémoire injectée en texte dans le contexte** (approximation, voir § 3), à 2000
  souvenirs : Pryzm met tous les souvenirs utiles dans ses 5 résultats pour **64 %** des questions ;
  un texte de 20 000 caractères des souvenirs les plus récents ne les contient que pour **26 %**.
- Pryzm **perd** sur : les faits mis à jour (l'ancienne version sort en tête 71 % du temps),
  les questions qui demandent deux souvenirs (8 % complets dans le top 5), et les questions sans
  réponse (il ne dit **jamais** « rien trouvé », 0 sur 40).
- Deux défauts du moteur ont été trouvés (§ 6) : le bras « mots-clés » de la recherche hybride ne
  sert presque jamais, et la pondération importance × fraîcheur dégrade le classement quand le
  reranker est coupé.

## 1. Ce qui est mesuré

Une question arrive ; le moteur renvoie une liste classée de souvenirs. On mesure si les souvenirs
utiles sont dans la liste et à quel rang. **On ne mesure pas la réponse finale d'un assistant**
(aucun LLM n'intervient). C'est la brique « retrouver », pas « répondre ».

### Jeu de données (`backend/bench/dataset.py`, déterministe, versionné)
Personnage fictif (freelance + cofondatrice d'un SaaS fictif), aucune donnée réelle.
- 93 souvenirs « cœur » : 45 faits simples, 12 paires multi-sauts, 12 paires ancien/nouveau fait ;
- 1907 distracteurs générés par gabarits (FR 72 %, EN 28 %), qui partagent volontairement du
  vocabulaire (TJM d'autres personnes, hébergement d'autres projets…) sans répondre aux questions
  (vérifié par test) ;
- 223 questions : 135 simples (41 paraphrases FR, 45 interlinguistiques, 45 indirectes à faible
  recouvrement de mots, 4 identifiants exacts), 24 multi-sauts, 24 mises à jour, 40 sans réponse.
- Tailles de base : 100, 250, 500, 1000, 2000 souvenirs (cœur + premiers distracteurs).

### Métriques
Recall@1 et @5 (part des souvenirs utiles dans les k premiers), MRR (inverse du rang du premier
souvenir utile), nDCG@10, complet@5 (tous les souvenirs utiles dans le top 5), à-jour@5 (le
nouveau fait est dans le top 5 et devant l'ancien), périmé-en-tête (l'ancien sort avant le
nouveau), abstention (liste vide sur une question sans réponse), latence p50/p95.
IC 95 % : bootstrap percentile, 2000 tirages sur les questions. Comparaisons : bootstrap
**apparié** (mêmes questions) ; p bilatéral approché.

### Systèmes
| Nom | Description |
|---|---|
| `pryzm_actuel` | Le vrai `memory_search` du dépôt, sur PostgreSQL + pgvector (HNSW), avec les réglages de prod connus : e5-small multilingue, reranker `mmarco-mMiniLMv2-L12-H384-v1`, seuil 0,78, RRF k=60, importance × fraîcheur. Graphe désactivé. |
| `pryzm_hybride` | Idem, bras mots-clés PostgreSQL forcé actif (voir § 6.1). |
| `pryzm_passage` | Idem, souvenirs encodés avec le préfixe e5 `passage:` au lieu de `query:` (ablation). |
| `pryzm_sans_rerank` | Idem sans reranker (ablation). |
| `dense_e5` | Référence : sémantique seule, même modèle, cosinus exact, sans seuil. |
| `bm25` | Référence : mots-clés seuls (BM25, sans racinisation, accents retirés). |
| `contexte_N` | **Approximation** d'une mémoire résumée injectée dans le contexte : les souvenirs les plus récents concaténés jusqu'à N caractères (2000, 6000, 20 000). « Trouvé » = tous les souvenirs utiles sont dans le texte. Borne **haute** : on suppose un modèle qui lit parfaitement. Ce **n'est pas** ChatGPT, Claude ni Gemini. |

## 2. Résultats (2000 souvenirs, questions avec réponse, n = 183)

| Système | Recall@1 | Recall@5 | MRR | nDCG@10 |
|---|---|---|---|---|
| pryzm_actuel | 0,533 [0,465–0,601] | 0,697 [0,634–0,757] | 0,653 [0,589–0,715] | 0,643 [0,583–0,701] |
| pryzm_passage | 0,516 [0,448–0,587] | 0,639 [0,574–0,708] | 0,616 [0,551–0,683] | 0,600 [0,539–0,665] |
| pryzm_sans_rerank | 0,104 [0,065–0,147] | 0,393 [0,322–0,462] | 0,227 [0,184–0,272] | 0,288 [0,242–0,337] |
| dense_e5 | 0,494 [0,429–0,566] | 0,708 [0,645–0,768] | 0,631 [0,571–0,694] | 0,638 [0,583–0,695] |
| bm25 | 0,377 [0,314–0,440] | 0,511 [0,443–0,579] | 0,488 [0,420–0,552] | 0,478 [0,415–0,540] |

(`pryzm_hybride` donne exactement les mêmes chiffres que `pryzm_actuel` ; voir § 6.1.)

### Par type de question (2000 souvenirs)
| Système | Simples MRR (135) | Multi-sauts complet@5 (24) | Mises à jour à-jour@5 (24) | Périmé en tête (24) | Sans réponse : abstention (40) |
|---|---|---|---|---|---|
| pryzm_actuel | 0,643 [0,563–0,716] | 0,083 [0,000–0,208] | 0,292 [0,125–0,458] | 0,708 [0,542–0,875] | 0,000 |
| pryzm_sans_rerank | 0,235 | 0,000 | 0,750 [0,583–0,917] | 0,000 | 0,000 |
| dense_e5 | 0,622 [0,547–0,696] | 0,083 | 0,333 [0,167–0,542] | 0,667 | 0,000 |
| bm25 | 0,456 [0,376–0,536] | 0,125 | 0,083 | 0,625 | 0,575 [0,425–0,725] |

### Par style de question (faits simples, Recall@5)
| Système | Paraphrase FR (41) | Autre langue (45) | Indirecte (45) | Identifiant exact (4) |
|---|---|---|---|---|
| pryzm_actuel | 0,878 | 0,756 | 0,422 | 1,000 |
| dense_e5 | 0,902 | 0,778 | 0,422 | 1,000 |
| bm25 | 0,780 | 0,422 | 0,289 | 1,000 |

### Comparaisons appariées (2000 souvenirs)
| Comparaison | Métrique | Différence | IC 95 % | p |
|---|---|---|---|---|
| Pryzm − BM25 | MRR | +0,165 | [+0,089 ; +0,237] | < 0,001 |
| Pryzm − BM25 | Recall@5 | +0,186 | [+0,107 ; +0,262] | < 0,001 |
| Pryzm − BM25 | Recall@5, question dans une autre langue | +0,333 | [+0,156 ; +0,511] | < 0,001 |
| Pryzm − BM25 | à-jour@5 | +0,208 | [+0,042 ; +0,375] | 0,002 |
| Pryzm − BM25 | abstention | −0,575 | [−0,725 ; −0,425] | < 0,001 |
| Pryzm − sémantique seule | MRR | +0,022 | [−0,035 ; +0,075] | 0,42 (non significatif) |
| Pryzm − sémantique seule | Recall@1 | +0,038 | [−0,035 ; +0,109] | 0,33 (non significatif) |

Tableau complet : `backend/bench/results/tables.md` et `paired.csv`.

## 3. Mémoire injectée dans le contexte (approximation)

Part des questions dont **tous** les souvenirs utiles sont présents :

| | 100 | 250 | 500 | 1000 | 2000 souvenirs |
|---|---|---|---|---|---|
| Texte de 2000 caractères | 0,28 | 0,14 | 0,06 | 0,03 | 0,00 |
| Texte de 6000 caractères | 0,86 | 0,43 | 0,30 | 0,20 | 0,06 |
| Texte de 20 000 caractères | 1,00 | 1,00 | 0,83 | 0,48 | 0,26 [0,20–0,33] |
| **Pryzm, 5 premiers résultats** (complet@5) | 0,78 [0,72–0,84] | 0,75 | 0,71 | 0,69 | 0,64 [0,58–0,71] |
Lecture : tant que tout tient dans le texte, injecter tout le texte est imbattable (1,00 à 100 ou
250 souvenirs avec 20 000 caractères, contre 0,78 pour Pryzm). Quand la mémoire grossit,
la part utile qui tient dans un budget fixe s'effondre ; la recherche de Pryzm baisse beaucoup
moins (0,78 → 0,64) tout en n'envoyant que 5 souvenirs.

## 4. Passage à l'échelle (MRR, questions avec réponse)

| Système | 100 | 250 | 500 | 1000 | 2000 |
|---|---|---|---|---|---|
| pryzm_actuel | 0,760 | 0,739 | 0,714 | 0,698 | 0,653 |
| dense_e5 | 0,742 | 0,690 | 0,660 | 0,647 | 0,631 |
| bm25 | 0,514 | 0,491 | 0,491 | 0,492 | 0,488 |

## 5. Latence

`memory_search` complet : **p50 ≈ 380–430 ms, p95 ≈ 450–520 ms**, stable de 100 à 2000 souvenirs ;
≈ 50–60 ms sans reranker. Le reranker coûte donc ~350 ms par recherche.
Mesuré dans le processus (sans réseau ni HTTP), 2 threads torch, priorité basse, **sur le VPS qui
héberge aussi la production** : chiffres indicatifs, non publiables comme performance garantie.

## 6. Défauts trouvés dans le moteur (à corriger avant toute communication)

1. **Le bras mots-clés de la recherche hybride est inopérant.**
   a) `PgCollection._has_tsv()` interroge `information_schema.columns` en tant que `pryzm_app` ; les
   rôles tenant lui sont accordés **sans héritage** (`inherit_option = false`), donc la colonne
   `tsv` est invisible et la recherche hybride est **silencieusement désactivée**. Constaté sur
   l'instance de test (réputée fidèle à la prod) ; **à vérifier en prod** (requête lecture seule :
   `SELECT count(*) FROM information_schema.columns WHERE column_name='tsv'` en `pryzm_app`).
   b) Même forcé, il ne sert à rien : `websearch_to_tsquery` exige **tous** les mots ; seules
   7 questions sur 223 trouvent au moins un résultat lexical, et ces souvenirs étaient déjà trouvés
   par la sémantique. Piste : requête en OU (`plainto_tsquery` + `|`), ou BM25 sur les termes rares.
   c) Le `tsv` est indexé sans `unaccent` alors que la requête est passée dans `unaccent` :
   un mot accentué de la requête peut ne plus correspondre (non mesuré séparément).
2. **La pondération importance × fraîcheur abîme le classement** : sans reranker, le MRR tombe à
   0,23 contre 0,63 pour la sémantique seule. En prod, le reranker réordonne tout et efface cet effet…
   mais efface aussi l'avantage voulu de la fraîcheur : l'ancien fait sort avant le nouveau dans
   71 % des mises à jour (contre 0 % sans reranker). Piste : combiner score du reranker et fraîcheur.
3. **Le seuil de similarité ne fait jamais dire « rien trouvé »** (0/40), à cause de la règle
   « garder au moins 1 résultat si ≥ 0,15 » et des similarités e5 toujours hautes. Un seuil sur le
   score du reranker serait plus utile mais coûteux : à −1, 93 % d'abstentions justes mais 43 %
   d'abstentions à tort (tableau dans `tables.md`).
4. Les souvenirs sont encodés avec le préfixe e5 `query:` ; passer à `passage:` (recommandation e5)
   **n'aide pas** ici (MRR 0,616 contre 0,653) : ne pas changer sans autre preuve.

## 7. Limites

- Jeu **synthétique**, écrit par nous, un seul profil, FR/EN : il peut favoriser ou défavoriser
  certains systèmes. 4 questions « identifiant » seulement : rien de publiable sur ce style.
- Les distracteurs sont générés par gabarits : plus répétitifs qu'une vraie mémoire.
- Pas d'assistant dans la boucle : pas de mesure de la réponse finale ni des hallucinations.
- `contexte_N` est une **approximation** d'une mémoire résumée, pas le fonctionnement réel de
  ChatGPT, Claude ou Gemini, dont l'implémentation n'est pas publique.
- Pas d'autre serveur MCP de mémoire open source testé : leur installation demandait de télécharger
  des paquets et modèles depuis Internet sur la machine de production ; écarté par prudence.
- Réglages « prod » repris de nos notes internes (fichier de configuration de prod volontairement
  non lu) ; le graphe d'entités (v1.1) n'est pas évalué.
- Une seule course : la variance d'une course à l'autre n'est due qu'à la latence (le reste est
  déterministe à graine fixe, mais l'âge des souvenirs est relatif à la date de la course).

## 8. Reproduire

```bash
git -C ~/projets/pryzm/pryzm-memory checkout feat/benchmark-memoire && cd backend
set -a; . ~/sauvegardes/pryzm-test-local.env; set +a     # base de TEST uniquement
venv/bin/python -m bench.dataset    # régénère le jeu (identique, vérifié par test)
venv/bin/python -m bench.run        # ~25 min sur 4 vCPU ; refuse toute base « saas »
venv/bin/python -m bench.analyze && venv/bin/python -m bench.tables
venv/bin/python -m pytest -q tests/test_bench.py
```

## 9. Ce qu'on PEUT dire publiquement (mot pour mot)

Chaque phrase doit renvoyer vers ce rapport et le code du banc.

1. « Sur un banc public et reproductible de 2000 souvenirs et 183 questions (jeu synthétique,
   octobre 2026), la recherche de Pryzm place le bon souvenir dans ses 5 premiers résultats dans
   70 % des cas (IC 95 % : 63–76 %). »
2. « Sur ce même banc, Pryzm retrouve mieux les souvenirs qu'une recherche par mots-clés seule
   (MRR 0,65 contre 0,49), en particulier quand la question n'est pas dans la langue du souvenir
   (76 % contre 42 % dans les 5 premiers résultats). »
3. « Quand une mémoire passe de 100 à 2000 souvenirs, la part des questions dont tous les souvenirs
   utiles sont retrouvés par Pryzm passe de 78 % à 64 % ; avec un texte fixe de 20 000 caractères
   contenant les souvenirs les plus récents, elle passe de 100 % à 26 %. »
   (Toujours préciser : « texte fixe = approximation d'une mémoire résumée, pas un produit précis ».)
4. « Pryzm ne fait pas encore mieux qu'une recherche sémantique simple avec le même modèle ; il fait
   moins bien sur les faits mis à jour et ne sait pas encore répondre “rien trouvé”. » (À dire :
   c'est la contrepartie d'honnêteté exigée.)

## 10. Ce qu'on NE PEUT PAS dire

- Toute comparaison nommée avec ChatGPT, Claude, Gemini ou un concurrent (« meilleur que la mémoire
  de ChatGPT », « X fois plus précis que… ») : **aucun de ces produits n'a été testé**. Il faut d'abord
  le protocole manuel (`protocole-manuel-ia.md`, bras A contre bras C).
- « Recherche hybride » comme argument de qualité : le bras mots-clés n'apporte rien de mesurable.
- « Pryzm comprend quand les infos changent » / « garde toujours la version à jour » : faux ici (29 %).
- « Pryzm ne vous invente rien / dit quand il ne sait pas » : 0 abstention sur 40.
- « +139 % de MRR » (chiffre interne de juin) : mesuré sur des données réelles non publiables, non
  reproductible par un tiers.
- Toute latence comme garantie de service.
- Tout chiffre sans son intervalle de confiance et sans lien vers la méthode.

## 11. Moteur v3 (branche `feat/moteur-recherche-v3`, NON déployé)

Mesuré sur le banc v1 (réglage) puis sur le **holdout v2** (questions jamais vues pendant le réglage).
Détails, IC et décisions : `journal-ameliorations.md`. 2000 souvenirs, IC 95 % bootstrap apparié.

| Mesure | v1 avant → après | v2 holdout avant → après |
|---|---|---|
| R@1 | 0,533 → 0,609 (+0,077 [+0,02 ; +0,14]) | 0,465 → 0,529 (+0,064 [+0,01 ; +0,12]) |
| R@5 | 0,697 → 0,768 (+0,071 [+0,03 ; +0,12]) | 0,571 → 0,651 (+0,080 [+0,03 ; +0,13]) |
| MRR | 0,653 → 0,716 | 0,553 → 0,618 |
| À-jour@5 | 0,292 → 0,792 | 0,417 → 0,708 |
| Multi-sauts complet@5 | 0,083 → 0,667 | 0,208 → 0,417 (p = 0,06) |
| Abstention juste / fausses alertes | 0 → 0,85 / 0,14 | 0 → 0,775 / **0,28** |
| vs. sémantique seule (MRR) | +0,085 [+0,03 ; +0,14] | +0,162 [+0,10 ; +0,22] |

### Phrases publiables UNE FOIS la v3 déployée (et la course refaite sur le code déployé)

1. « Sur un banc public et reproductible (2000 souvenirs, questions jamais vues pendant le
   réglage), la recherche de Pryzm place le bon souvenir dans ses 5 premiers résultats dans 65 % des
   cas (IC 95 % : 58–72 %), contre 57 % pour la version précédente. »
2. « Quand un fait a été mis à jour, Pryzm remonte la version à jour dans ses 5 premiers résultats
   dans 71 % des cas sur ce banc (contre 42 % auparavant). »
3. « Sur ce banc, Pryzm fait mieux qu'une recherche sémantique simple avec le même modèle (MRR
   0,62 contre 0,46). »

### Toujours interdit

- « Pryzm sait quand il ne sait pas » : 28 % de fausses alertes sur le holdout ; signal à laisser coupé.
- Tout gain en langue croisée : non confirmé sur v2.
- Toute latence : l'objectif ≈ 600 ms au p95 n'est pas atteint (671–835 ms mesurés).
