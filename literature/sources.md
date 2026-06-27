# Patchi — literature sources

Source notes for the literature review, organized by the cluster of Pygmalion's
framework each body of work grounds. Identifiers (DOI / arXiv / ISBN / URL) are
given only where verified; "no verified identifier" marks where we have the
work but not a confirmed identifier (never invented). The synthesis that draws
these together is in [`REVIEW.md`](REVIEW.md).

Pygmalion's original framework lives in [`../data_lake/artificialtime2.txt`](../data_lake/artificialtime2.txt)
and the companion report; it is his intellectual work. The notes below map his
constructs onto established theory — what they descend from, and where Patchi
must do new work.

---

## Primary sources (Pygmalion's notebooks)

The evidentiary base of the project is Pygmalion's own writing. There are two
overlapping notebook dumps; they are the *same intellectual work*, captured at
two stages of organization.

- **[`../data_lake/artificialtime2.txt`](../data_lake/artificialtime2.txt)** (800 lines) —
  the raw notebook. Free-flowing, unsorted; the constructs (infons, WordClasses,
  the bijective translator, spatial/temporal logic, topos meta-reasoning, the
  control reframing) appear in the order they were thought. Also carries a handful
  of still-open "(no answer yet)" prompts that the later pass dropped — *BIG DATA +
  CONNECTIVITY + AI*, *a COMPILER FOR THE AI*, bridging ML/knowledge-experts
  (clusters, decision trees, causal inference) into the linguistic engine, the
  neural-net-as-learning-engine on a separate server.
- **[`../data_lake/proto.txt`](../data_lake/proto.txt)** (848 lines) — a **later,
  reorganized pass** of the same material. Line-for-line it is ~99% identical to
  `artificialtime2.txt` (a sorted-line diff leaves only ~13 lines unique to it,
  most of them section banners); it adds **no new construct**. What it adds is
  *structure*: the dump is partitioned into seven labeled phases that expose
  Pygmalion's own intended pipeline ordering —
  1. **commentaries** — the motivating intuitions (rules-as-LP, classifiers,
     VSMs, the infon→WordClass→block→spatial/temporal→object→thought→idea→topos
     abstraction ladder);
  2. **representation** — the representation layer proper (the
     polynomial+geometric+axiomatic WordClass, spatial-logic-as-gateway-to-vector-
     algebra, topos-as-VHDL-category, classes-as-perimeters, verbs-as-functions,
     "a model is a subset of the atoms");
  3. **entropy_destilation** — distillation into ordered forms: the
     syntax → semantics → pragmatics → world-knowledge cascade, NN constituent
     detection, geometric meaning from linear-algebra constraints;
  4. **synthesis** — the binding ideas: context-as-base-relation,
     words-as-agreements, memory-as-recursion, words-as-function-sets,
     thought = ⟨perception, memory⟩, ideas-as-persistent-thoughts;
  5. **storing** — the persistence layer: the similarity database schema, the
     node/edge/function-mapping graph structures, the `<temporal, spatial>` memory
     tuple;
  6. **source** — lexical bootstrapping from encyclopedias + dictionaries
     (WordNet/Wiktionary/DBpedia) into the reasoning engine;
  7. **control** — the control view: `MESSAGE_SWITCHER`, the Kripke `M=⟨W,R,V⟩`
     spatial logic, error-based feedback, parameters-as-polynomials, and the
     "neural nets are information-flow controllers" reframing.

  This phase partition is itself useful evidence: it is the author confirming,
  in his own hand, that the notebook is a single layered stack rather than a
  grab-bag — and the phase order (represent → distill → synthesize → store →
  source → control) lines up with the layered reading in
  [`REVIEW.md`](REVIEW.md) §1. Because `proto.txt` adds no new theory, it changes
  none of the citations below; it is archived as the cleaner entry point into the
  same corpus.

---

## Situation semantics & information

Grounds: **infons**, **situations**, **context-as-base-relation**, **words-as-agreements**.

- **Jon Barwise & John Perry, *Situations and Attitudes* (1983), MIT Press; reissued CSLI 1999** — ISBN 9781575861937 (CSLI ed.). Founded *situation semantics* as a realist, partial alternative to possible-worlds semantics: meaning arises from structured, *partial* situations (real bits of the world), and is the *relation* between an utterance-situation and a described situation. → Grounds Pygmalion's **situations** as partial, real context-bases that carry information.
- **Keith Devlin, *Logic and Information*, Vol. 1: *Situation Theory* (1991), Cambridge University Press** — ISBN 9780521499712 (pbk). Formalizes the *infon* ⟨R, a₁…aₙ, i⟩ (relation, arguments, polarity i∈{0,1}, often a spatio-temporal location) and the *supports* relation `s ⊨ σ` ("situation s supports infon σ"); truth is the holding of an infon *relative to a situation*. → This is **verbatim Pygmalion's infon**, and `s ⊨ σ` makes the situation the base against which every relation acquires meaning. (Pygmalion cites "the book logic and information by Delvin".)
- **Keith Devlin, *InfoSense: Turning Information into Knowledge* (1999), W. H. Freeman** — ISBN 9780716734840. Non-technical situation theory: same infons read against different situations yield different information. → Context-as-base-relation, intuitively.
- **Jon Barwise & Jerry Seligman, *Information Flow: The Logic of Distributed Systems* (1997), Cambridge University Press** — ISBN 9780521583862. *Channel theory*: information flows along channels of *classifications* linked by *infomorphisms*, with *local logics* for fallibility. → A compositional account of how information moves *between* situations — relevant if Patchi wires contexts together rather than supporting them individually.
- **David Lewis, *Convention: A Philosophical Study* (1969), Harvard University Press; Blackwell 2002** — ISBN 9780631232568 (Blackwell). Meaning as an *arbitrary, self-perpetuating solution to a recurring coordination problem*: a sound–meaning pairing is conventional, settled by mutual expectation. (Upstream: Saussure, *Course in General Linguistics* (1916), arbitrariness of the sign.) → Grounds Pygmalion's **"words are agreements on labels"** with a precise mechanism.

### Gap / what Patchi adds
These theories are symbolic and set-theoretic; none give a *computational, learnable, sub-symbolic* realization. There is no native account of graded support, similarity between situations, or how the "base relation" of context could be *learned*. Patchi's contribution: infons as embeddings, `s ⊨ σ` as a continuous support score, context as a learned conditioning signal.

---

## Distributional & compositional semantics

Grounds: **words-as-coordinates**, **relations-as-offsets**, **similarity-weighted composition**, **geometric meaning**.

- **J.R. Firth, "A Synopsis of Linguistic Theory 1930–1955" (1957), in *Studies in Linguistic Analysis* (Blackwell); Z.S. Harris, "Distributional Structure" (1954), *Word* 10(2–3):146–162** — DOI 10.1080/00437956.1954.11659520. The distributional hypothesis: a word's meaning is characterized by the contexts it occurs in. → The foundational premise behind "meaning as relations between sets of words."
- **P.D. Turney & P. Pantel, "From Frequency to Meaning: Vector Space Models of Semantics" (2010), *JAIR* 37:141–188** — DOI 10.1613/jair.2934; arXiv:1003.1141. Organizes VSMs by matrix structure; cosine similarity, PPMI/tf-idf weighting, dimensionality reduction. → Names the **VSM** Pygmalion invokes; the word–context matrix is "words as coordinates."
- **T. Mikolov, K. Chen, G. Corrado, J. Dean, "Efficient Estimation of Word Representations in Vector Space" (2013)** — arXiv:1301.3781 (skip-gram/CBOW); the analogy result is in **Mikolov, Yih & Zweig, "Linguistic Regularities in Continuous Space Word Representations" (2013), NAACL-HLT 746–751** (ACL N13-1090). Relations appear as approximately consistent vector offsets, solvable by arithmetic. → Pygmalion's exact **"king − man + woman ≈ queen"** offset.
- **J. Pennington, R. Socher, C.D. Manning, "GloVe: Global Vectors for Word Representation" (2014), *EMNLP* 1532–1543** — DOI 10.3115/v1/D14-1162. Embeddings from global co-occurrence ratios; vector differences capture meaning ratios. → Reinforces relation-as-offset from a count-based route.
- **B. Coecke, M. Sadrzadeh, S. Clark, "Mathematical Foundations for a Compositional Distributional Model of Meaning" (2010), *Linguistic Analysis* 36** — arXiv:1003.4394 (**DisCoCat**). Unifies Lambek pregroup grammar with distributional vector spaces in a compact closed category, so grammatical reductions become linear maps composing word vectors into sentence vectors. → **The closest analogue to Pygmalion's vision**: grammar + category theory + distributional vectors fused to compute phrase meaning geometrically.

### Gap / what Patchi adds
The field gives words-as-coordinates, relations-as-offsets, and a grammar-driven (bilinear/tensorial) composition operator. None treats phrase meaning as Pygmalion's **similarity-weighted polynomial blending** over the lexicon. Patchi formalizes that specific blending operator and ties it to the offset/geometry tradition.

---

## Vector-symbolic architectures & conceptual spaces

Grounds: **word→block bijection**, **binding/blending composition**, **classes-as-regions**, **geometric similarity**.

- **Tony A. Plate, "Holographic Reduced Representations" (1995), *IEEE TNN* 6(3):623–641** — DOI 10.1109/72.377968. Compositional structure in fixed-width vectors: role–filler binding via **circular convolution**, superposition for blending, approximate inverse to unbind. → Pygmalion's **binding/blending** composition, directly.
- **Pentti Kanerva, "Hyperdimensional Computing…" (2009), *Cognitive Computation* 1:139–159** — DOI 10.1007/s12559-009-9009-8. ~10,000-D random vectors with **binding** (multiply/XOR), **bundling** (add), **permutation** (sequencing); similarity as overlap; noise-tolerant via near-orthogonality. → word→atomic-hypervector and geometric similarity as overlap.
- **Ross W. Gayler, "Vector Symbolic Architectures answer Jackendoff's challenges…" (2003), Proc. ICCS/ASCS 133–138** — arXiv:cs/0412059. Coins **VSA**; binding+superposition+clean-up memory address variable binding and rapid construction of structured representations. → The formal account of words-as-reconfigurable-blocks composed dynamically.
- **Peter Gärdenfors, *Conceptual Spaces: The Geometry of Thought* (2000), MIT Press** — ISBN 9780262071994 (also *The Geometry of Meaning*, 2014, ISBN 9780262026789). Concepts as **convex regions** in spaces of quality dimensions; similarity as distance; prototypes as centroids. → Maps almost exactly onto Pygmalion's **"classes as perimeters/regions delimited by parameters in Cartesian space."**
- **Paul Smolensky, "Tensor product variable binding…" (1990), *Artificial Intelligence* 46(1–2):159–216** — DOI 10.1016/0004-3702(90)90007-M. Binds role/filler via the **tensor product** + superposition; the dimensionality growth HRR/HDC later compress. → The ancestor of binding-via-vector-product.

### Gap / what Patchi adds
VSA/HDC supplies binding/blending but atomic vectors are opaque, with no class *boundary*; Conceptual Spaces supplies class-as-region geometry but no binding algebra over regions. Patchi's move: a *bijective* word→block mapping whose blocks are simultaneously bindable VSA vectors **and** parameter-delimited regions — so set theory over class perimeters and vector composition act on the same objects. Whether binding stays closed under region membership is the open formal question.

---

## Neuro-symbolic AI, knowledge-graph embeddings & the control view

Grounds: **graph-of-deductions**, **Prolog⇄neural bridge**, **relations-as-offsets**, **attention-as-gain**, **signed (stimulator/inhibitor) graph**, **control view of NNs**.

- **A. d'Avila Garcez & L. C. Lamb, "Neurosymbolic AI: The 3rd Wave" (2020; *AI Review* 2023)** — arXiv:2012.05876. Integrating robust neural learning with symbolic reasoning/explainability. → Pygmalion's Prolog⇄neural bridge is exactly this program.
- **T. R. Besold et al., "Neural-Symbolic Learning and Reasoning: A Survey and Interpretation" (2017)** — arXiv:1711.03902. Scope, realizations, open challenges of neural-symbolic computation. → Background for bridging logic programs and neural substrates.
- **A. Bordes et al., "Translating Embeddings for Modeling Multi-relational Data" (TransE, NeurIPS 2013)** — papers.nips.cc/paper/5071. A relation is a translation: head + relation ≈ tail. → The anchor for **"relations as vector offsets"**: deduction-edges as geometric translations.
- **Q. Wang, Z. Mao, B. Wang & L. Guo, "Knowledge Graph Embedding: A Survey…" (2017), *IEEE TKDE*** — DOI 10.1109/TKDE.2017.2754499. Translational/bilinear/neural KGE families preserving graph structure. → Situates relations-as-offsets and signed-edge variants.
- **A. Vaswani et al., "Attention Is All You Need" (2017)** — arXiv:1706.03762. Self-attention = softmax-normalized weighted sums over tokens; routes information by learned relevance. → Grounds **"attention as gain + normalization"** and the routing/control reading. *(No verified source endorses the strong "NNs are control systems, not learners" claim — that is Pygmalion's framing to defend, not consensus.)*
- **M. Richardson & P. Domingos, "Markov Logic Networks" (2006), *Machine Learning*** — DOI 10.1007/s10994-006-5833-1. Weighted first-order formulae define a Markov network over groundings. → A precedent for weighted/signed logic-as-graph (stimulator/inhibitor edges).

### Gap / what Patchi adds
The pieces exist separately (relations-as-offsets, the logic⇄neural bridge, attention-as-gain, weighted logic-graphs). None unify them where nodes are *word sets*, edges are *logical deductions*, the graph is *signed* (synonyms-stimulate / antonyms-inhibit), and the net is reframed as an information-flow *controller*. That synthesis + the control reframing is Patchi's claim to defend.

---

## Topos/categorical logic & modal/spatial/temporal logic

Grounds: **topos meta-reasoning over blocks**, **sheaf/local-to-global for situations**, **Kripke worlds as experiential states**, **spatial-logic↔vector-algebra**, **temporal logic for memory**.

- **Saunders Mac Lane & Ieke Moerdijk, *Sheaves in Geometry and Logic* (1992), Springer** — ISBN 9780387977102; DOI 10.1007/978-1-4612-0927-0. Topos as a category generalizing sheaves and set-models; the **subobject classifier Ω** (predicates as morphisms into a truth object), **internal intuitionistic higher-order logic**, **sheaf semantics** (Grothendieck topologies, local-to-global gluing). → Topos as the ambient category for neural blocks: Ω-"properties," an internal logic for property-preservation, and gluing as "local-to-global gluing of situations."
- **Robert Goldblatt, *Topoi: The Categorial Analysis of Logic* (1979; rev. 1984), North-Holland** — ISBN 9780444852076 (no single verified DOI for the original printing). The logician's route into topoi: arrows/objects as primitives, internal Heyting-valued logic from Ω. → The companion for **"topos as VHDL category reasoning"** — meta-reasoning over block composition/equivalence as arrow-algebra.
- **Brendan Fong & David I. Spivak, *Seven Sketches in Compositionality* (2019)** — arXiv:1803.05316 (MIT Press ed. ISBN 9781108711821). Compositional modeling via orders, monoidal categories, functors, databases, (co)limits. → Grounds "neural blocks as objects/morphisms" and reasoning about composition in a verified applied-CT text. *(A specific "category theory of consciousness/cognition" reference was flagged uncertain and is NOT cited pending verification.)*
- **Saul Kripke, "Semantical Considerations on Modal Logic" (1963), *Acta Philosophica Fennica* 16:83–94** (no verified DOI; widely reprinted). Relational semantics **M = ⟨W, R, V⟩**; ◻ quantifies over R-accessible worlds; frame conditions on R ↔ modal axioms. → **Verbatim Pygmalion's M=⟨W,R,V⟩** with worlds as experiential-knowledge states, R as reachability between them.
- **M. Aiello, I. Pratt-Hartmann & J. van Benthem (eds.), *Handbook of Spatial Logics* (2007), Springer** — ISBN 9781402055867; DOI 10.1007/978-1-4020-5587-4. Logics whose models are spaces (S4 over topological spaces, mereotopology, region calculi). → Underwrites **"Spatial Logic"**; the topological-modal link bridges qualitative space toward vector representations. (Region Connection Calculus — Randell, Cui & Cohn, *KR'92* 165–176, no verified DOI — is the canonical region calculus.)
- **Amir Pnueli, "The Temporal Logic of Programs" (1977), *18th IEEE FOCS* 46–57** — DOI 10.1109/SFCS.1977.32. Founds linear temporal logic (◻/◇/until over execution sequences). → The reference for the **TemporalLogic** half of Pygmalion's memory tuple.

### Gap / what Patchi adds
Each ingredient exists in isolation; none is articulated as a substrate for *neural blocks*, and there is no standard `<TemporalLogic, SpatialLogic>` memory tuple. Patchi's move: composable blocks as objects/morphisms in one topos so "this composition preserves bijectivity" is an internal-logic theorem, with modal/temporal/spatial logic bound into one memory model where "spatial logic is the gateway to vector algebra." That joint identification is the contribution to formalize and defend.
