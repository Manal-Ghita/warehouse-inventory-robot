# Données

## Source

Entrepôt réel d'un fabricant de chaussures (Sherbrooke, Québec), extrait de son logiciel de gestion d'entrepôt puis anonymisé par les auteurs.

- Article : R. Furlan de Assis, W. de Paula Ferreira, M. Ouhimmou, *Order picking dataset from a warehouse of a footwear manufacturing company*, Data in Brief 61 (2025), 111837. https://doi.org/10.1016/j.dib.2025.111837
- Données : Mendeley Data, v1. https://doi.org/10.17632/pf2w725pw3.1

## Licence

Données sous licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Les fichiers de `processed/` sont dérivés de ces données et modifiés comme décrit ci-dessous.

## Récupérer les données brutes

Les données brutes ne sont pas versionnées. Télécharger l'archive depuis Mendeley Data et la décompresser dans `data/raw/footwear_warehouse/`.

## Fichiers produits

Générés par `notebooks/01_exploration_dataset.ipynb` :

- `processed/emplacements.csv` : les 2 292 emplacements et leurs coordonnées schématiques.
- `processed/base_stock.csv` : 20 097 couples (emplacement, produit), base de stock du robot.

## Modifications apportées

- Stock passé du format large (18 colonnes) à une ligne par couple (emplacement, produit).
- Doublons d'un même produit dans un même emplacement supprimés.
- Quantités ignorées : elles sont recopiées artificiellement dans les 18 colonnes.

## Remarques sur la documentation d'origine

- `z` est un numéro de niveau (1 à 4), pas une hauteur en mètres.
- `x` et `y` ne sont pas en mètres : coordonnées schématiques, avec des échelles différentes selon l'axe. Les dimensions réelles viennent du plan `Full layout.dwg`.
- 2 292 emplacements dans les fichiers, contre 2 293 annoncés dans l'article.