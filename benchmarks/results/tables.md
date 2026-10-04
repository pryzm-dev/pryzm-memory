
### Questions avec réponse (n=183) (base de 2000 souvenirs)

| Système | Recall@1 | Recall@5 | MRR | nDCG@10 |
|---|---|---|---|---|
| pryzm_actuel | 0.533 [0.465–0.601] | 0.697 [0.634–0.757] | 0.653 [0.589–0.715] | 0.643 [0.583–0.701] |
| pryzm_hybride | 0.533 [0.465–0.601] | 0.697 [0.634–0.757] | 0.653 [0.589–0.715] | 0.643 [0.583–0.701] |
| pryzm_passage | 0.516 [0.448–0.587] | 0.639 [0.574–0.708] | 0.616 [0.551–0.683] | 0.600 [0.539–0.665] |
| pryzm_sans_rerank | 0.104 [0.065–0.147] | 0.393 [0.322–0.462] | 0.227 [0.184–0.272] | 0.288 [0.242–0.337] |
| dense_e5 | 0.494 [0.429–0.566] | 0.708 [0.645–0.768] | 0.631 [0.571–0.694] | 0.638 [0.583–0.695] |
| bm25 | 0.377 [0.314–0.440] | 0.511 [0.443–0.579] | 0.488 [0.420–0.552] | 0.478 [0.415–0.540] |

### Par type de question (base de 2000 souvenirs)

| Système | Simples MRR (n=135) | Multi-sauts complet@5 (n=24) | Mises à jour à jour@5 (n=24) | Périmé en tête (n=24) | Sans réponse : abstention (n=40) |
|---|---|---|---|---|---|
| pryzm_actuel | 0.643 [0.563–0.716] | 0.083 [0.000–0.208] | 0.292 [0.125–0.458] | 0.708 [0.542–0.875] | 0.000 [0.000–0.000] |
| pryzm_hybride | 0.643 [0.563–0.716] | 0.083 [0.000–0.208] | 0.292 [0.125–0.458] | 0.708 [0.542–0.875] | 0.000 [0.000–0.000] |
| pryzm_passage | 0.610 [0.530–0.691] | 0.083 [0.000–0.208] | 0.292 [0.125–0.458] | 0.667 [0.458–0.833] | 0.000 [0.000–0.000] |
| pryzm_sans_rerank | 0.235 [0.182–0.290] | 0.000 [0.000–0.000] | 0.750 [0.583–0.917] | 0.000 [0.000–0.000] | 0.000 [0.000–0.000] |
| dense_e5 | 0.622 [0.547–0.696] | 0.083 [0.000–0.208] | 0.333 [0.167–0.542] | 0.667 [0.458–0.833] | 0.000 [0.000–0.000] |
| bm25 | 0.456 [0.376–0.536] | 0.125 [0.000–0.250] | 0.083 [0.000–0.208] | 0.625 [0.417–0.792] | 0.575 [0.425–0.725] |

### Par style (faits simples, Recall@5, paraphrase n=41, autre langue et indirecte n=45) (base de 2000 souvenirs)

| Système | Paraphrase FR | Interlinguistique | Indirecte | Identifiant exact (n=4) |
|---|---|---|---|---|
| pryzm_actuel | 0.878 [0.780–0.976] | 0.756 [0.622–0.867] | 0.422 [0.289–0.578] | 1.000 [1.000–1.000] |
| pryzm_hybride | 0.878 [0.780–0.976] | 0.756 [0.622–0.867] | 0.422 [0.289–0.578] | 1.000 [1.000–1.000] |
| pryzm_passage | 0.829 [0.707–0.927] | 0.689 [0.533–0.822] | 0.400 [0.267–0.556] | 0.750 [0.250–1.000] |
| pryzm_sans_rerank | 0.537 [0.390–0.707] | 0.378 [0.244–0.511] | 0.311 [0.178–0.444] | 0.000 [0.000–0.000] |
| dense_e5 | 0.902 [0.805–0.976] | 0.778 [0.644–0.889] | 0.422 [0.289–0.578] | 1.000 [1.000–1.000] |
| bm25 | 0.780 [0.658–0.902] | 0.422 [0.289–0.578] | 0.289 [0.156–0.422] | 1.000 [1.000–1.000] |

### Passage à l'échelle : MRR (questions avec réponse)

| Système | 100 | 250 | 500 | 1000 | 2000 |
|---|---|---|---|---|---|
| pryzm_actuel | 0.760 [0.707–0.809] | 0.739 [0.683–0.791] | 0.714 [0.657–0.770] | 0.698 [0.638–0.758] | 0.653 [0.589–0.715] |
| pryzm_hybride | 0.760 [0.707–0.809] | 0.739 [0.683–0.791] | 0.714 [0.657–0.770] | 0.698 [0.638–0.758] | 0.653 [0.589–0.715] |
| pryzm_passage | 0.749 [0.695–0.799] | 0.735 [0.679–0.787] | 0.718 [0.659–0.772] | 0.678 [0.616–0.740] | 0.616 [0.551–0.683] |
| pryzm_sans_rerank | 0.212 [0.172–0.253] | 0.231 [0.190–0.273] | 0.245 [0.202–0.288] | 0.262 [0.214–0.309] | 0.227 [0.184–0.272] |
| dense_e5 | 0.742 [0.692–0.792] | 0.690 [0.634–0.743] | 0.660 [0.602–0.718] | 0.647 [0.588–0.708] | 0.631 [0.571–0.694] |
| bm25 | 0.514 [0.446–0.580] | 0.491 [0.425–0.555] | 0.491 [0.424–0.554] | 0.492 [0.425–0.557] | 0.488 [0.420–0.552] |

### Approximation « mémoire en texte injectée dans le contexte » : part des questions dont TOUS les souvenirs utiles tiennent dans le texte injecté

| Budget (caractères) | 100 | 250 | 500 | 1000 | 2000 |
|---|---|---|---|---|---|
| 2000 | 0.279 [0.219–0.344] | 0.142 [0.093–0.197] | 0.060 [0.027–0.098] | 0.033 [0.011–0.060] | 0.000 [0.000–0.000] |
| 6000 | 0.858 [0.803–0.907] | 0.432 [0.361–0.503] | 0.295 [0.230–0.361] | 0.197 [0.142–0.257] | 0.060 [0.027–0.098] |
| 20000 | 1.000 [1.000–1.000] | 1.000 [1.000–1.000] | 0.831 [0.770–0.885] | 0.481 [0.410–0.552] | 0.262 [0.202–0.328] |

### Latence de recherche (ms, machine de test)

| Système | 100 p50 / p95 | 250 p50 / p95 | 500 p50 / p95 | 1000 p50 / p95 | 2000 p50 / p95 |
|---|---|---|---|---|---|
| pryzm_actuel | 406 / 485 | 398 / 485 | 391 / 469 | 381 / 457 | 426 / 523 |
| pryzm_hybride | 406 / 488 | 403 / 482 | 400 / 471 | 383 / 462 | 381 / 460 |
| pryzm_passage | 400 / 487 | 395 / 488 | 388 / 470 | 378 / 456 | 376 / 451 |
| pryzm_sans_rerank | 48 / 56 | 51 / 60 | 54 / 64 | 54 / 63 | 57 / 68 |
| dense_e5 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 4 |
| bm25 | 0 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 1 / 2 |

### Comparaisons appariées (base 2000, différence a − b, IC 95 %, p bootstrap)

| a | b | groupe | métrique | diff | IC 95 % | p |
|---|---|---|---|---|---|---|
| pryzm_actuel | bm25 | toutes_avec_reponse | mrr | +0.165 | [+0.089 ; +0.237] | 0.000 |
| pryzm_actuel | dense_e5 | toutes_avec_reponse | mrr | +0.022 | [-0.035 ; +0.075] | 0.419 |
| pryzm_hybride | pryzm_actuel | toutes_avec_reponse | mrr | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | toutes_avec_reponse | mrr | +0.165 | [+0.089 ; +0.237] | 0.000 |
| pryzm_hybride | dense_e5 | toutes_avec_reponse | mrr | +0.022 | [-0.035 ; +0.075] | 0.419 |
| pryzm_actuel | bm25 | toutes_avec_reponse | r@5 | +0.186 | [+0.107 ; +0.262] | 0.000 |
| pryzm_actuel | dense_e5 | toutes_avec_reponse | r@5 | -0.011 | [-0.057 ; +0.038] | 0.747 |
| pryzm_hybride | pryzm_actuel | toutes_avec_reponse | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | toutes_avec_reponse | r@5 | +0.186 | [+0.107 ; +0.262] | 0.000 |
| pryzm_hybride | dense_e5 | toutes_avec_reponse | r@5 | -0.011 | [-0.057 ; +0.038] | 0.747 |
| pryzm_actuel | bm25 | toutes_avec_reponse | r@1 | +0.156 | [+0.079 ; +0.232] | 0.000 |
| pryzm_actuel | dense_e5 | toutes_avec_reponse | r@1 | +0.038 | [-0.035 ; +0.109] | 0.329 |
| pryzm_hybride | pryzm_actuel | toutes_avec_reponse | r@1 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | toutes_avec_reponse | r@1 | +0.156 | [+0.079 ; +0.232] | 0.000 |
| pryzm_hybride | dense_e5 | toutes_avec_reponse | r@1 | +0.038 | [-0.035 ; +0.109] | 0.329 |
| pryzm_actuel | bm25 | simple | mrr | +0.188 | [+0.101 ; +0.272] | 0.000 |
| pryzm_actuel | dense_e5 | simple | mrr | +0.022 | [-0.045 ; +0.086] | 0.495 |
| pryzm_hybride | pryzm_actuel | simple | mrr | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | simple | mrr | +0.188 | [+0.101 ; +0.272] | 0.000 |
| pryzm_hybride | dense_e5 | simple | mrr | +0.022 | [-0.045 ; +0.086] | 0.495 |
| pryzm_actuel | bm25 | multihop | complet@5 | -0.042 | [-0.167 ; +0.083] | 0.769 |
| pryzm_actuel | dense_e5 | multihop | complet@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | pryzm_actuel | multihop | complet@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | multihop | complet@5 | -0.042 | [-0.167 ; +0.083] | 0.769 |
| pryzm_hybride | dense_e5 | multihop | complet@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_actuel | bm25 | temporal | a_jour@5 | +0.208 | [+0.042 ; +0.375] | 0.002 |
| pryzm_actuel | dense_e5 | temporal | a_jour@5 | -0.042 | [-0.333 ; +0.250] | 0.906 |
| pryzm_hybride | pryzm_actuel | temporal | a_jour@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | temporal | a_jour@5 | +0.208 | [+0.042 ; +0.375] | 0.002 |
| pryzm_hybride | dense_e5 | temporal | a_jour@5 | -0.042 | [-0.333 ; +0.250] | 0.906 |
| pryzm_actuel | bm25 | style_indirecte | r@5 | +0.133 | [-0.022 ; +0.289] | 0.122 |
| pryzm_actuel | dense_e5 | style_indirecte | r@5 | +0.000 | [-0.133 ; +0.133] | 1.000 |
| pryzm_hybride | pryzm_actuel | style_indirecte | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | style_indirecte | r@5 | +0.133 | [-0.022 ; +0.289] | 0.122 |
| pryzm_hybride | dense_e5 | style_indirecte | r@5 | +0.000 | [-0.133 ; +0.133] | 1.000 |
| pryzm_actuel | bm25 | style_crosslingue | r@5 | +0.333 | [+0.156 ; +0.511] | 0.000 |
| pryzm_actuel | dense_e5 | style_crosslingue | r@5 | -0.022 | [-0.133 ; +0.089] | 0.870 |
| pryzm_hybride | pryzm_actuel | style_crosslingue | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | style_crosslingue | r@5 | +0.333 | [+0.156 ; +0.511] | 0.000 |
| pryzm_hybride | dense_e5 | style_crosslingue | r@5 | -0.022 | [-0.133 ; +0.089] | 0.870 |
| pryzm_actuel | bm25 | style_identifiant | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_actuel | dense_e5 | style_identifiant | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | pryzm_actuel | style_identifiant | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | style_identifiant | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | dense_e5 | style_identifiant | r@5 | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_actuel | bm25 | sans_reponse | abstention_ok | -0.575 | [-0.725 ; -0.425] | 0.000 |
| pryzm_actuel | dense_e5 | sans_reponse | abstention_ok | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | pryzm_actuel | sans_reponse | abstention_ok | +0.000 | [+0.000 ; +0.000] | 1.000 |
| pryzm_hybride | bm25 | sans_reponse | abstention_ok | -0.575 | [-0.725 ; -0.425] | 0.000 |
| pryzm_hybride | dense_e5 | sans_reponse | abstention_ok | +0.000 | [+0.000 ; +0.000] | 1.000 |

### Seuil hypothétique sur le score du reranker (pryzm_actuel, base 2000)

| Seuil | Sans réponse : abstention correcte | Avec réponse : abstention à tort | Avec réponse : Recall@1 conservé |
|---|---|---|---|
| -4 | 0.20 | 0.18 | 0.56 |
| -2 | 0.75 | 0.37 | 0.47 |
| -1 | 0.93 | 0.43 | 0.45 |
| 0 | 1.00 | 0.54 | 0.37 |
| 1 | 1.00 | 0.62 | 0.30 |
| 2 | 1.00 | 0.68 | 0.26 |
| 3 | 1.00 | 0.73 | 0.22 |
| 4 | 1.00 | 0.76 | 0.19 |
