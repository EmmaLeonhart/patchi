"""GD-2 — does Pygmalion's "shared-neighbour distance" predict human similarity?

The notebook claims word similarity is *relational*: "distance between words =
the number of words they have in common" / "two words are similar if their
neighbourhood structures overlap" (data_lake/proto.txt L229-235, L308-316). Every
Patchi result so far measures the *geometric* signal (vector reconstruction:
blend <= raw, 0 of 6). This is the first test of the *structural* signal, from an
**independent** relation source — WordNet — that never looks at the embedding.

Construction. For each word we take its WordNet **shared-ancestor features**: the
set of all synsets on the hypernym paths of its senses (the concepts it *is a
kind of*). Two words "have in common" every ancestor concept they share — cat and
dog share carnivore / mammal / vertebrate / animal / entity. We build a symmetric
word<->feature adjacency and apply `patchi.structural`:

* common_neighbors / jaccard  — raw and size-normalised shared-ancestor overlap.
* adamic_adar                  — shared ancestors weighted by 1/log(degree), so a
                                 specific shared concept (carnivore) counts more
                                 than a generic one (entity). This is, in effect,
                                 a taxonomic (Resnik/Lin-flavoured) similarity that
                                 falls straight out of Pygmalion's "shared words"
                                 idea + the inverse-log-degree weighting.
* signed_overlap               — sign-aware variant (antonym features as -1).

We Spearman-correlate each against WordSim-353 and SimLex-999, compare to the
GloVe-cosine baseline on the *same* covered pairs, and test a **combined** score
(rank-average of cosine + adamic-adar) — the real question being whether the
relational signal adds what reconstruction could not.

Run: python scripts/run_structural.py   (needs nltk WordNet downloaded and the
cached GloVe in results/_cache/; see run_generality.py for the cache.)
"""

import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from patchi.structural import adamic_adar, common_neighbors, jaccard, signed_overlap  # noqa: E402
from patchi.benchmark import spearman  # noqa: E402

CACHE = ROOT / "results" / "_cache"
GLOVE = ("GloVe-100", CACHE / "glove100.gz")
POOL = 200_000  # cover the dataset vocab generously


# -- datasets (same loaders as run_generality) -------------------------------

def load_wordsim(path):
    pairs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        a, b, s = line.split("\t")[:3]
        pairs.append((a.lower(), b.lower(), float(s)))
    return pairs


def load_simlex(path):
    pairs, lines = [], path.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        c = line.split("\t")
        pairs.append((c[0].lower(), c[1].lower(), float(c[3])))
    return pairs


def load_glove(path, limit):
    words, vecs = [], []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        first = f.readline().split()
        if len(first) != 2:
            words.append(first[0]); vecs.append([float(x) for x in first[1:]])
        for line in f:
            if len(words) >= limit:
                break
            p = line.rstrip().split(" ")
            words.append(p[0]); vecs.append([float(x) for x in p[1:]])
    return words, np.asarray(vecs, dtype=float)


# -- WordNet shared-ancestor graph -------------------------------------------

def build_wordnet_graph(vocab):
    """Symmetric word<->feature adjacency over the hypernym-path ancestors.

    Returns (adj, signed_adj, covered) where ``covered`` is the set of vocab
    words that had at least one WordNet sense.
    """
    from nltk.corpus import wordnet as wn

    adj = defaultdict(set)
    signed = defaultdict(dict)
    covered = set()
    for w in vocab:
        synsets = wn.synsets(w)
        if not synsets:
            continue
        covered.add(w)
        feats = set()
        for syn in synsets:
            for path in syn.hypernym_paths():
                for anc in path:
                    feats.add(anc.name())
            # antonyms -> negative features (the inhibitor pole)
            for lemma in syn.lemmas():
                for ant in lemma.antonyms():
                    af = "ANT::" + ant.synset().name()
                    adj[w].add(af); adj[af].add(w)
                    signed[w][af] = -1; signed[af][w] = -1
        for f in feats:
            adj[w].add(f); adj[f].add(w)
            signed[w][f] = 1; signed[f][w] = 1
    return adj, signed, covered


def cos(u, v):
    return float(u @ v / ((np.linalg.norm(u) * np.linalg.norm(v)) + 1e-12))


def ranks(x):
    """Fractional ranks of a 1-D array (average ties), for rank-averaging."""
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x), float)
    r[order] = np.arange(len(x), dtype=float)
    # average ties
    _, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts)); np.add.at(sums, inv, r)
    return (sums / counts)[inv]


def evaluate(pairs, adj, signed, gM, gidx):
    # head-to-head needs both words in WordNet AND in GloVe
    usable = [(a, b, s) for a, b, s in pairs
              if a in adj and b in adj and a in gidx and b in gidx]
    in_wn = [(a, b, s) for a, b, s in pairs if a in adj and b in adj]
    human = np.array([s for _, _, s in usable])

    cn = np.array([common_neighbors(adj, a, b) for a, b, _ in usable], float)
    jac = np.array([jaccard(adj, a, b) for a, b, _ in usable])
    aa = np.array([adamic_adar(adj, a, b) for a, b, _ in usable])
    so = np.array([signed_overlap(signed, a, b) for a, b, _ in usable])
    cosv = np.array([cos(gM[gidx[a]], gM[gidx[b]]) for a, b, _ in usable])
    combined = ranks(cosv) + ranks(aa)  # rank-average of cosine + adamic-adar

    return {
        "pairs_total": len(pairs),
        "pairs_in_wordnet": len(in_wn),
        "pairs_usable_head2head": len(usable),
        "spearman": {
            "common_neighbors": round(spearman(cn, human), 4),
            "jaccard": round(spearman(jac, human), 4),
            "adamic_adar": round(spearman(aa, human), 4),
            "signed_overlap": round(spearman(so, human), 4),
            "cosine_baseline": round(spearman(cosv, human), 4),
            "combined_cos+aa": round(spearman(combined, human), 4),
        },
    }


def main() -> int:
    datasets = [("WordSim-353", load_wordsim(CACHE / "wordsim353.tsv")),
                ("SimLex-999", load_simlex(CACHE / "SimLex-999" / "SimLex-999.txt"))]
    vocab = sorted({w for _, ps in datasets for a, b, _ in ps for w in (a, b)})

    print(f"building WordNet shared-ancestor graph over {len(vocab)} words...")
    adj, signed, covered = build_wordnet_graph(vocab)
    print(f"  {len(covered)}/{len(vocab)} words had a WordNet sense; "
          f"{len(adj)} graph nodes total")

    words, gM = load_glove(GLOVE[1], POOL)
    gidx = {w: i for i, w in enumerate(words)}

    rows = []
    for name, pairs in datasets:
        res = evaluate(pairs, adj, signed, gM, gidx)
        res["dataset"] = name
        sp = res["spearman"]
        res["combined_beats_cosine"] = sp["combined_cos+aa"] > sp["cosine_baseline"]
        res["structural_best"] = max(sp["common_neighbors"], sp["jaccard"],
                                     sp["adamic_adar"])
        rows.append(res)

    result = {
        "task": "structural (WordNet shared-ancestor) similarity vs human, "
                "+ cosine baseline + combined",
        "embedding": GLOVE[0],
        "rows": rows,
        "combined_beats_cosine_anywhere": any(r["combined_beats_cosine"] for r in rows),
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "structural_benchmark.json").write_text(json.dumps(result, indent=2))

    print(f"\n{result['task']} [{GLOVE[0]}]")
    hdr = ("dataset      cover(wn/h2h)   c.nbr  jacc   adamic  signed  cosine  comb"
           "   comb>cos")
    print(hdr)
    for r in rows:
        sp = r["spearman"]
        print(f"{r['dataset']:<12} "
              f"{r['pairs_in_wordnet']:>4}/{r['pairs_usable_head2head']:<4}     "
              f"{sp['common_neighbors']:+.3f} {sp['jaccard']:+.3f} "
              f"{sp['adamic_adar']:+.3f} {sp['signed_overlap']:+.3f} "
              f"{sp['cosine_baseline']:+.3f} {sp['combined_cos+aa']:+.3f}  "
              f"{r['combined_beats_cosine']}")
    print(f"\ncombined beats cosine anywhere? {result['combined_beats_cosine_anywhere']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
