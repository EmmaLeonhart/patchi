# Patchi: Formalizing and Stress-Testing Pygmalion's Relation-Based Theory of Cognition

**Theory:** Pygmalion. **Formalization, implementation, and experiments:** Emma Leonhart with an autonomous coding agent.

## Abstract

Pygmalion's notebook *artificial time* sketches an ambitious unified theory of
machine cognition: meaning is made of relations between words; words are
agreements on labels; context is the base relation from which all others draw
meaning; information is carried by *infons* in *situations*; memory is a
recursion indexed by an "artificial time"; words map bijectively to
reconfigurable "VHDL-style" neural blocks; and a topos-level layer reasons about
those blocks. We do two things with it. First, we read the sprawling notebook as
a single *layered stack* and ground each layer in established theory (situation
semantics, distributional and compositional vector semantics, vector-symbolic
architectures and conceptual spaces, neuro-symbolic AI and knowledge-graph
embeddings, and topos/modal/spatial/temporal logic), finding that the layers are
well-trodden and the *bridges between them* are where the originality and the
risk live. Second, we build a runnable reference implementation of the core and
empirically test two distinct claims it makes about similarity. (i) Its signature
*similarity-weighted blending* operator — reconstructing a word from its
neighbourhood in vector space — is sharply regime-dependent and, on clean data,
**negative**: blending denoises noisy vectors (up to +0.14 Spearman) but *hurts*
clean pretrained embeddings, a result that holds across GloVe-50/100 and
fastText-300 × WordSim-353 and SimLex-999 (blend beats raw in 0 of 6) and is not
rescued by residual or phrase-level variants. (ii) A *different* Pygmalion claim —
that similarity is **relational**, "the number of words two words have in common" —
is **positive**: a WordNet structural/taxonomic signal, which never looks at the
embedding, significantly *complements* distributional cosine on genuine-similarity
judgements (SimLex-999) across all three embeddings (cosine+path-similarity beats
cosine by +0.08 to +0.17 Spearman, every bootstrap 95% CI above zero, including the
strongest fastText embedding). Pygmalion's *specific* "shared-neighbour count" is a
weaker instantiation than the textbook WordNet measures it resembles (Wu-Palmer,
path), but the phenomenon he pointed at is real, sizable, and significant. The
two-sided finding: his framework **loses as geometry, wins as relational
structure** on genuine similarity. We report both directions in full, including the
negative result and the demotion of the specific operator.

## 1. Introduction

This paper formalizes and empirically stress-tests a theory of cognition due to
**Pygmalion**. The source material — a research notebook and an accompanying
report — proposes that cognition can be assembled bottom-up from relations
between words, with a stack of increasingly abstract structures built on top.
The notebook is idiosyncratic and wide-ranging; read charitably it is not a
grab-bag but a coherent architecture that recruits one established intellectual
tradition per layer.

Our contribution is twofold: (i) a literature-grounded reading of the framework
that separates what is already known from what is genuinely new, and (ii) a
working implementation of the core plus a measured empirical test of two distinct
claims it makes about similarity — a negative result for the signature blending
operator (similarity as vector reconstruction) and a positive one for the
relational claim (similarity as shared taxonomic structure).

## 2. The framework as a layered stack

The notebook's own closing hierarchy makes the stack explicit:

```
infons / infon-classes        → situation theory (Devlin)
WordClasses (poly+geom+axiom)  → conceptual spaces + VSA (Gärdenfors, Plate/Kanerva)
neural "VHDL" blocks           → distributional / compositional semantics (word2vec, DisCoCat)
spatial / temporal logic       → modal / spatial / temporal logic (Kripke, Aiello, Pnueli)
objects → thought → idea        → emergent (the project's own contribution)
collectives / topos            → categorical logic (Mac Lane–Moerdijk, Goldblatt)
```

Each arrow is a *bridge* Pygmalion asserts: "spatial logic is the gateway to
vector algebra"; "topos as VHDL category reasoning"; the bijective "translator:
WordClass → NeuralCircuitBlock". The layers are mature prior art; the bridges are
the research, and several are not known to be consistent.

## 3. Related work (what is already known)

- **Meaning from distribution.** A word's meaning is fixed by the company it
  keeps (Firth 1957; Harris 1954) and is representable geometrically, with
  relations as consistent vector offsets (Mikolov et al. 2013; Pennington et al.
  2014; Bordes et al. 2013). Pygmalion's "meaning as relations between words" and
  the "king − man + woman ≈ queen" example are this tradition.
- **Information as infons-in-situations.** The `⟨relation, args, polarity⟩` infon
  and the support relation `s ⊨ σ` are Devlin's situation theory (Barwise & Perry
  1983; Devlin 1991) verbatim; the symbolic account is complete, a graded/learned
  one is not.
- **Compositional vectors, categorically.** DisCoCat (Coecke, Sadrzadeh & Clark
  2010) already fuses grammar, category theory, and distributional vectors to
  compose sentence meaning — the closest existing realization of the vision.
- **Binding and regions.** VSA/HDC (Plate 1995; Kanerva 2009; Gayler 2003;
  Smolensky 1990) supplies binding/bundling; Gärdenfors' conceptual spaces (2000)
  supply concepts-as-regions — Pygmalion's "classes as perimeters."
- **Worlds, space, time, topoi.** Kripke (1963), the *Handbook of Spatial Logics*
  (Aiello et al. 2007), Pnueli (1977), and topos internal logic (Mac Lane &
  Moerdijk 1992; Goldblatt 1979) each exist in mature form.

The recurring shape of the gap: the components are known in isolation; the
bridges are not standard. The full literature review with ~26 cited sources is in
the repository (`literature/REVIEW.md`).

## 4. The implemented system

We built a runnable Python core (`patchi`) covering a vertical slice of the
stack, each component unit-tested:

- **WordClass lexicon** — words as vectors with a parameter bag and
  cosine nearest-neighbour lookup.
- **Signed relation graph** — synonym(+)/antonym(−) edges (the stimulator/
  inhibitor spectrum) with TransE-style relation offsets; held-out edges are
  recovered by offset arithmetic.
- **Similarity-weighted blending operator** — `blend(w) = Σ sim(w,sᵢ)^p·vec(sᵢ) /
  Σ sim(w,sᵢ)^p`, with uniform weighting recovering an additive baseline.
- **Infon/situation layer** — `⟨relation, args, polarity⟩` with a *graded*
  `support(s,σ) ∈ [0,1]` (Devlin's binary support made continuous and
  vector-backed), so context-conditioning measurably changes outputs.
- **Proof(walk) trace** — every output records the words/weights that produced
  it, with a single-source-of-truth discipline so the trace cannot diverge from
  the computed value.
- **Reduced cores for the harder bridges** — a registry-backed bijective
  translator (bijection over the lexicon, grown on demand), a category of
  invertible affine blocks with property checkers (the computable shadow of the
  topos layer), and "artificial time" as the discrete recursion index of a memory
  cell. These are deliberate reductions; the full versions are named as future work.

## 5. Methods

We run two families of experiment. The first tests the **blending operator** — the
framework's most distinctive composition primitive — against two baselines (raw
vectors; additive = unweighted neighbour mean), using the *same* operator code
throughout. The second tests the **relational similarity** claim against a
distributional-cosine baseline. All scores are Spearman correlations with human
judgements; embeddings are GloVe-50, GloVe-100, and fastText-300 (a different,
subword architecture); datasets are **WordSim-353** (relatedness) and
**SimLex-999** (genuine similarity, which deliberately penalises mere relatedness).

- **Synthetic denoising.** Clustered prototype vectors plus Gaussian noise; ground
  truth = cosine of the clean prototypes.
- **Real-embedding reconstruction.** Blend/additive/raw across all three embeddings
  × both datasets; plus a residual form `(1−α)·raw + α·blend` and a phrase-level
  variant.
- **Relational structure.** A WordNet graph in which each word's features are the
  synsets on its senses' hypernym paths (the concepts it *is a kind of*); structural
  similarity is the overlap of two words' feature sets, computed by
  `patchi.structural` (common-neighbour / Jaccard / Adamic-Adar) and never reading
  the embedding. We compare it to the textbook WordNet measures (Wu-Palmer, path),
  to GloVe cosine, and to a combined (rank-average) score; we put 95% confidence
  intervals on the gains with a paired bootstrap (B = 2000) and validate the learned
  combining weight with 5-fold cross-validation.

## 6. Results

**Real embeddings (the headline).** Raw GloVe-50 scores Spearman **0.5033** —
matching the known literature value, a check that the harness is correct. Every
reconstruction underperforms it:

| k | power | additive | blend | blend − raw |
|--:|------:|---------:|------:|------------:|
| 3 | 6 | 0.4420 | 0.4470 | −0.0564 |
| 5 | 2 | 0.4309 | 0.4336 | −0.0697 |
| 10 | 2 | 0.4318 | 0.4347 | −0.0686 |
| 25 | 2 | 0.4228 | 0.4256 | −0.0777 |

On clean pretrained vectors, reconstructing a word from its neighbourhood
**loses to doing nothing** (best blend 0.447 vs raw 0.503). The similarity
weighting reliably beats the unweighted average, but only by +0.001 to +0.009.

**Synthetic (the contrast).** When vectors are noisy, reconstruction *denoises*:

| noise | power | raw | additive | blend |
|------:|------:|----:|---------:|------:|
| 0.4 | 4.0 | 0.892 | 0.829 | **0.972** |
| 0.8 | 4.0 | 0.689 | 0.751 | 0.866 |
| 1.6 | 4.0 | 0.363 | 0.352 | 0.349 |

Here blend beats raw by up to +0.14, and the weighting beats additive by
+0.10–0.14 — until noise is high enough that the neighbourhood itself is
unreliable and the gain vanishes or goes slightly negative.

**Generality of the negative result.** The "reconstruction hurts on clean vectors"
finding holds across {GloVe-50, GloVe-100, fastText-300} × {WordSim-353,
SimLex-999} — **blend beats raw in 0 of 6 cells**, including the different fastText
architecture and a much stronger raw baseline (0.718). A residual form was also
swept: the best mixing weight is α = 0 (raw), so a little smoothing does not rescue
it. A phrase-composition variant tells the same story — plain additive composition
beats the similarity-weighted one at every noise level. The blending operator is a
noise-conditional smoother, not a free improvement over standard embeddings.

**The relational claim is positive.** Pygmalion's framework also asserts, separately,
that similarity is *relational* — "the number of words two words have in common." We
test this with WordNet structure that never looks at the embedding, and it carries
genuine, complementary signal on the genuine-similarity dataset (SimLex-999). With
the standard *path* similarity, combining the structural signal with GloVe cosine
(flat rank-average) beats cosine alone on every embedding, significantly:

| embedding | SimLex cosine | + structural (path) | bootstrap Δ (95% CI) |
|-----------|----:|----:|:--:|
| GloVe-50     | 0.263 | 0.431 | +0.168 [+0.133, +0.202] |
| GloVe-100    | 0.296 | 0.448 | +0.151 [+0.118, +0.184] |
| fastText-300 | 0.445 | 0.524 | +0.080 [+0.050, +0.111] |

Every confidence interval is strictly above zero, including fastText, the strongest
embedding. A learned mixing weight (tuned on a train split, scored under 5-fold
cross-validation) is ≥ cosine on every cell, and on relatedness (WordSim-353), where
cosine already dominates, it correctly collapses toward cosine rather than dragging
it down.

Two qualifications keep this accurate. First, the gain is **regime-specific**: it
appears on SimLex (similarity) and not on WordSim (relatedness), because WordNet's
taxonomy measures is-a-kind-of, which is exactly what SimLex rewards and distributional
cosine conflates with relatedness. Second, Pygmalion's *specific* operationalisation —
a shared-neighbour count (Adamic-Adar over shared ancestors) — is **weaker** than the
textbook WordNet measures it resembles: on SimLex (GloVe-100 set) it scores 0.298 against
Wu-Palmer's 0.438 and path's 0.476. His instinct (similarity is taxonomic/relational
structure complementary to vector geometry) is vindicated; his particular metric is not
the best tool for it.

## 7. Discussion

The two experiments separate two claims the framework runs together. As **geometry**
— reconstructing a word from its neighbourhood in vector space — Pygmalion's
operator is a denoiser whose value is entirely conditional on input noise: it wins
when averaging over trustworthy neighbours recovers signal (noisy vectors) and loses
when the base vectors are already clean, where averaging washes out discriminative
information; the similarity weighting is real but small, never the difference between
winning and losing. As **relational structure** — similarity as overlap of
taxonomic neighbourhoods — the same framework is right: that signal is independent of
the embedding and significantly complements it on genuine-similarity judgements,
across two architectures and the strongest available baseline. The synthesis is
two-sided and not what either experiment alone implies: **the framework loses as
geometry and wins as relational structure.** It is also self-correcting on the
specifics — the relational *direction* is vindicated while Pygmalion's particular
shared-neighbour metric is shown to be a weaker version of similarity measures the
field already has.

## 8. Limitations

The empirical scope is three embeddings (GloVe-50/100 + fastText-300, two
architectures) × two datasets (WordSim-353, SimLex-999) — broad, but still English
single-word similarity; phrase-level and cross-lingual tests are future work. The
relational result is grounded in WordNet only; a denser or genuinely *signed*
relation graph (e.g. ConceptNet) is needed to test the stimulator/inhibitor
*polarity* half of Pygmalion's spectrum claim, which WordNet's sparse antonyms left
at noise. The bootstrap resamples pairs, which slightly understates dependence
between pairs sharing a word. The harder bridges (full topos internal logic, richer
polynomial/geometric block internals, the control-system reframing of neural nets)
are implemented only as reduced cores or named as future work, not papered over.

## 9. Conclusion

Pygmalion's framework is a coherent stack whose layers are well-grounded and whose
bridges are the open contribution. Measured rather than asserted, it gives a
two-sided result: its signature blending operator is a noise-conditional smoother
that loses to raw vectors on clean embeddings (0 of 6 cells), while a *different*
claim it makes — that similarity is relational, carried by shared taxonomic
structure — significantly complements distributional cosine on genuine-similarity
judgements across all three embeddings (+0.08 to +0.17 Spearman, every CI above
zero). His specific shared-neighbour metric is bettered by the textbook WordNet
measures, but the phenomenon he pointed at is real, sizable, and significant. Loses
as geometry, wins as relational structure. The full implementation, literature
review, and reproducible benchmarks are public at
<https://github.com/EmmaLeonhart/patchi> (report: <https://emmaleonhart.github.io/patchi/>).

## References

Selected; full notes with verified identifiers in `literature/sources.md`.
Barwise & Perry, *Situations and Attitudes* (1983). Devlin, *Logic and
Information* (1991). Firth (1957); Harris (1954). Turney & Pantel (2010). Mikolov
et al. (2013); Pennington et al. (2014). Coecke, Sadrzadeh & Clark (2010). Plate
(1995); Kanerva (2009); Gayler (2003); Smolensky (1990). Gärdenfors (2000).
Bordes et al. (2013, TransE). Vaswani et al. (2017). Mac Lane & Moerdijk (1992);
Goldblatt (1979). Kripke (1963). Aiello, Pratt-Hartmann & van Benthem (2007).
Pnueli (1977). Miller (1995, WordNet); Wu & Palmer (1994, verb-semantics
similarity); Leacock & Chodorow (1998, path-based similarity); Hill, Reichart &
Korhonen (2015, SimLex-999).
