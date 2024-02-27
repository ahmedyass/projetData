import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

data = pd.read_csv("termCandidates.ttg", sep="\t", header=None, names=["term", "pos", "lemma"])

# Filtrer les termes pertinents
relevant_data = data[data["pos"].isin(["NN", "NNS", "JJ", "NP"]) & (data["term"] != ".")]

# Compter la fréquence d'apparition des paires de termes
term_pair_counts = relevant_data.groupby(["term", "lemma"]).size().reset_index(name="Frequency")

# Transformer les données en format adapté à l'algorithme Apriori
term_pair_counts = term_pair_counts[term_pair_counts["Frequency"] > 1]
term_pair_counts["Frequency"] = 1

# Préparer les données pour l'analyse des règles d'association
term_pair_counts = term_pair_counts.pivot_table(index="term", columns="lemma", values="Frequency", aggfunc='sum', fill_value=0)

frequent_itemsets = apriori(term_pair_counts, min_support=0.05, use_colnames=True)

rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

print(rules)
