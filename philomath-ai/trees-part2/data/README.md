# Trees Part 2 — Datasets

> **Part of [Trees Part 2](../README.md)**

This directory contains pairwise distance matrices used in the UPGMA
phylogenetics exercises.  Each CSV file has taxon names as both row and column
headers.  The diagonal is always 0 and the matrix is symmetric.

---

## `great_apes.csv` — Great Ape Cytochrome b Divergence

| Taxon | Notes |
|-------|-------|
| human | *Homo sapiens* |
| chimp | *Pan troglodytes* |
| bonobo | *Pan paniscus* |
| gorilla | *Gorilla gorilla* |
| orangutan | *Pongo pygmaeus* |

**Metric**: Nucleotide divergence (fraction of sites differing) in
cytochrome b, a mitochondrial protein-coding gene widely used for
primate phylogenetics.

**Expected topology**: `((human,(chimp,bonobo)),gorilla),orangutan`  
UPGMA should correctly recover the human–chimp–bonobo clade and place
the orangutan as the most divergent outgroup.

---

## `hemoglobin.csv` — Haemoglobin Alpha Chain Divergence

| Taxon | Notes |
|-------|-------|
| human | *Homo sapiens* — mammal |
| mouse | *Mus musculus* — mammal |
| zebrafish | *Danio rerio* — teleost fish |
| frog | *Xenopus laevis* — amphibian |
| shark | *Scyliorhinus canicula* — cartilaginous fish |
| lamprey | *Petromyzon marinus* — jawless fish (agnathan) |

**Metric**: Amino-acid divergence in the haemoglobin alpha chain.

**Expected topology**: lamprey is the most basal (diverged before the
jawed-vertebrate common ancestor).  Mammals (human, mouse) cluster together.

---

## `hiv_subtypes.csv` — HIV-1 Group M Subtype Divergence

| Taxon | Notes |
|-------|-------|
| A1 | Subtype A1 — common in East Africa |
| B  | Subtype B  — predominant in Western countries |
| C  | Subtype C  — most prevalent globally |
| D  | Subtype D  — common in East Africa |
| AE | CRF01_AE circulating recombinant form — common in Southeast Asia |
| G  | Subtype G  — common in West Africa |

**Metric**: Nucleotide divergence in the *env* gene.

**Note**: HIV-1 group M has a complex evolutionary history with extensive
recombination between subtypes.  UPGMA may not recover the true evolutionary
history because (a) the molecular clock assumption is violated and (b)
recombination violates the tree model entirely.

---

## `sars_cov2.csv` — SARS-CoV-2 Variants of Concern

| Taxon | Notes |
|-------|-------|
| original | Wuhan reference genome (Jan 2020) |
| alpha | B.1.1.7 — first detected UK, late 2020 |
| delta | B.1.617.2 — first detected India, 2021 |
| omicron_ba1 | BA.1 — first detected South Africa, Nov 2021 |
| omicron_ba2 | BA.2 — subvariant of Omicron, 2022 |

**Metric**: Approximate nucleotide divergence across the whole genome.

**Observation**: Omicron BA.1 and BA.2 are closely related to each other
and highly divergent from all earlier variants (Alpha, Delta, Original).

---

## `mtdna_haplogroups.csv` — Human Mitochondrial DNA Haplogroups

| Taxon | Notes |
|-------|-------|
| L0 | Oldest lineage — San people of southern Africa |
| L1 | Second oldest — central/west Africa |
| M  | Out-of-Africa founder lineage (eastern route) |
| N  | Out-of-Africa founder lineage (northern route) |
| R  | Subclade of N — European/Asian diversification |
| H  | Most common European haplogroup (subclade of R) |
| J  | Common European/Near Eastern haplogroup (subclade of R) |

**Metric**: Nucleotide divergence in the hypervariable region of
mitochondrial DNA.

**Observation**: L0 and L1 are the most basal haplogroups, consistent with
an African origin of modern humans.  M and N are the two primary
non-African founding lineages.  H and J are closely related (both in clade R).

---

## Sources & Caveats

These distance matrices are simplified/rounded educational approximations
based on published literature values.  For rigorous phylogenetic analysis,
use actual aligned sequence data with appropriate substitution models (e.g.,
GTR+Γ in IQ-TREE or RAxML).

Key references:
- Goodman et al. (1989) cytochrome b primate phylogenetics
- Hardison (1996) haemoglobin evolution
- Los Alamos HIV Sequence Database — https://www.hiv.lanl.gov
- Nextstrain SARS-CoV-2 phylogenetics — https://nextstrain.org/ncov
- Phylotree.org human mtDNA haplogroup tree — https://www.phylotree.org
