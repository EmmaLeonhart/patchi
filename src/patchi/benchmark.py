"""MVC-3 benchmark — does similarity-weighted blending recover structure better?

This measures the blending operator (`blend.py`) against two baselines on a
**controlled synthetic denoising task** with a known ground truth:

  * build ``n_clusters`` clean prototype vectors; each word is a prototype plus
    Gaussian noise. Ground-truth similarity of two words = cosine of their *clean*
    prototypes (what the noise is hiding).
  * three working representations per word:
      - ``raw``      — the noisy vector itself (no reconstruction)
      - ``additive`` — unweighted mean of the word's k nearest neighbours
      - ``blend``    — similarity-weighted mean of the k nearest neighbours
  * score = Spearman rank correlation between each method's pairwise cosine and
    the ground-truth pairwise cosine. Higher = recovers the hidden structure
    better.

**Scope, named plainly:** this is synthetic data, not real embeddings. It tests
the *operator's denoising behaviour* under controlled noise; it is NOT a claim
about WordSim-353 / real corpora. The real-embeddings run is the queued next
step (it needs a downloaded embedding table + dataset, unavailable offline).

Spearman is implemented in numpy so the package depends only on numpy.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple

import numpy as np

from .blend import blend_word
from .wordclass import Lexicon, cosine


def _rankdata(a: np.ndarray) -> np.ndarray:
    """Average-rank of each element (ties share the mean rank). numpy-only."""
    a = np.asarray(a, dtype=float)
    order = a.argsort()
    ranks = np.empty(len(a), dtype=float)
    ranks[order] = np.arange(1, len(a) + 1, dtype=float)
    # average ties
    _, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts))
    np.add.at(sums, inv, ranks)
    return (sums / counts)[inv]


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation (Pearson on ranks); 0.0 if either is constant."""
    rx, ry = _rankdata(x), _rankdata(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = float(np.sqrt((rx * rx).sum() * (ry * ry).sum()))
    if denom == 0.0:
        return 0.0
    return float((rx * ry).sum() / denom)


@dataclass
class SyntheticData:
    lexicon: Lexicon
    clean: Dict[str, np.ndarray]  # word -> clean prototype vector


def make_synthetic(
    n_clusters: int = 8,
    per_cluster: int = 6,
    dim: int = 24,
    noise: float = 0.6,
    seed: int = 0,
) -> SyntheticData:
    """Build a noisy lexicon with a known clean prototype behind each word."""
    rng = np.random.default_rng(seed)
    prototypes = rng.normal(size=(n_clusters, dim))
    embeddings: Dict[str, List[float]] = {}
    clean: Dict[str, np.ndarray] = {}
    for c in range(n_clusters):
        for j in range(per_cluster):
            w = f"c{c}_w{j}"
            clean_vec = prototypes[c]
            noisy = clean_vec + noise * rng.normal(size=dim)
            embeddings[w] = noisy.tolist()
            clean[w] = clean_vec.copy()
    return SyntheticData(Lexicon.from_embeddings(embeddings), clean)


def _ground_truth_pairs(data: SyntheticData) -> Tuple[List[Tuple[str, str]], np.ndarray]:
    words = data.lexicon.words()
    pairs = list(combinations(words, 2))
    gt = np.array([cosine(data.clean[a], data.clean[b]) for a, b in pairs])
    return pairs, gt


def evaluate(data: SyntheticData, *, k: int = 5, power: float = 2.0) -> Dict[str, float]:
    """Spearman(method pairwise cosine, ground-truth cosine) for each method."""
    pairs, gt = _ground_truth_pairs(data)
    lex = data.lexicon

    raw = {w: lex[w].vector for w in lex.words()}
    additive = {w: blend_word(lex, w, k=k, weighting="uniform") for w in lex.words()}
    blended = {w: blend_word(lex, w, k=k, weighting="similarity", power=power)
               for w in lex.words()}

    def score(rep: Dict[str, np.ndarray]) -> float:
        method = np.array([cosine(rep[a], rep[b]) for a, b in pairs])
        return spearman(method, gt)

    return {"raw": score(raw), "additive": score(additive), "blend": score(blended)}


def run_benchmark(seed: int = 0, **kwargs) -> Dict[str, object]:
    """End-to-end: build data, evaluate, return a JSON-serialisable result dict."""
    params = {"n_clusters": 8, "per_cluster": 6, "dim": 24, "noise": 0.6,
              "k": 5, "power": 2.0, "seed": seed}
    params.update(kwargs)
    data = make_synthetic(
        n_clusters=params["n_clusters"], per_cluster=params["per_cluster"],
        dim=params["dim"], noise=params["noise"], seed=params["seed"],
    )
    scores = evaluate(data, k=params["k"], power=params["power"])
    return {
        "task": "synthetic-denoising (controlled; not real embeddings)",
        "params": params,
        "metric": "spearman(method pairwise cosine, ground-truth clean cosine)",
        "scores": scores,
        "delta_blend_minus_additive": scores["blend"] - scores["additive"],
        "delta_blend_minus_raw": scores["blend"] - scores["raw"],
    }


def run_phrase_benchmark(
    n_clusters: int = 12,
    per_cluster: int = 6,
    dim: int = 24,
    noise: float = 0.6,
    n_phrases: int = 40,
    phrase_len: int = 3,
    power: float = 2.0,
    seed: int = 0,
) -> Dict[str, float]:
    """Which phrase-composition method best recovers ground-truth phrase meaning?

    Mirrors the MVC-3 denoising design at the *phrase* level. Words are noisy
    samples of concept prototypes. A phrase is ``phrase_len`` words drawn from
    distinct concepts; its **clean meaning** is the mean of those concepts'
    prototypes. Ground-truth phrase similarity = cosine of clean meanings. Each
    method composes the phrase from the *noisy* word vectors (reusing
    ``compose.compose_phrase``); score = Spearman(method pairwise cosine, GT).
    """
    from .compose import compose_phrase  # local import avoids a cycle at import time

    data = make_synthetic(n_clusters=n_clusters, per_cluster=per_cluster,
                          dim=dim, noise=noise, seed=seed)
    lex, clean = data.lexicon, data.clean
    rng = np.random.default_rng(seed + 1)

    phrases, clean_means = [], []
    for _ in range(n_phrases):
        clusters = rng.choice(n_clusters, size=phrase_len, replace=False)
        words = [f"c{c}_w{int(rng.integers(per_cluster))}" for c in clusters]
        phrases.append(words)
        clean_means.append(np.mean([clean[w] for w in words], axis=0))

    pairs = list(combinations(range(n_phrases), 2))
    gt = np.array([cosine(clean_means[i], clean_means[j]) for i, j in pairs])

    def score(method: str) -> float:
        comp = [compose_phrase(lex, p, method, power=power) for p in phrases]
        m = np.array([cosine(comp[i], comp[j]) for i, j in pairs])
        return round(spearman(m, gt), 4)

    return {"additive": score("additive"),
            "multiplicative": score("multiplicative"),
            "weighted": score("weighted")}


def run_sweep(
    noises=(0.4, 0.8, 1.2, 1.6, 2.0),
    powers=(1.0, 4.0),
    k: int = 8,
    seed: int = 0,
) -> List[Dict[str, float]]:
    """Sweep noise x power to characterise *when* similarity weighting helps.

    Returns one compact row per (noise, power), so the committed artifact shows
    the whole picture rather than a single flattering configuration.
    """
    rows: List[Dict[str, float]] = []
    for noise in noises:
        data = make_synthetic(noise=noise, seed=seed)  # same data across powers
        for power in powers:
            scores = evaluate(data, k=k, power=power)
            rows.append({
                "noise": noise, "power": power, "k": k,
                "raw": round(scores["raw"], 4),
                "additive": round(scores["additive"], 4),
                "blend": round(scores["blend"], 4),
                "blend_minus_additive": round(scores["blend"] - scores["additive"], 4),
            })
    return rows
