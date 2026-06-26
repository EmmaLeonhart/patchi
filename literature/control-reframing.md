# Position — "Neural networks are information-flow controllers, not learners"

Pygmalion's notebook asserts that a neural network "seems more like a control
system regulating the flow of information than a learning machine" — "from each
neuron, which neuron should the network pay attention to, pay more attention to
than which" — and proposes splitting a **control unit** from a separate
**learning unit** with an API between them. This note argues the claim properly:
which part is grounded, and which part is the notebook's thesis rather than
established science. (Companion to `REVIEW.md` §3, item 6, which flagged it.)

## The grounded half: flow-control *is* a real and central mechanism

Modern architectures contain explicit machinery for *routing/gating information*,
not just fitting weights:

- **Attention as learned gain** — self-attention computes softmax-normalised
  weights over tokens and takes a weighted sum, i.e. it *routes* information by
  learned relevance rather than processing everything uniformly (Vaswani et al.,
  *Attention Is All You Need*, 2017, arXiv:1706.03762). This is the closest real
  mechanism to Pygmalion's "which neuron should pay attention to which."
- **Gating in recurrent nets** — LSTM input/forget/output gates and GRU
  update/reset gates *literally* regulate what information enters, persists, and
  leaves the state (Hochreiter & Schmidhuber, *Long Short-Term Memory*, 1997, DOI
  10.1162/neco.1997.9.8.1735; Cho et al., 2014, arXiv:1406.1078). Gating is
  control-of-flow by construction.
- **Conditional routing** — sparsely-gated Mixture-of-Experts uses a learned
  *router* to send each token to a subset of sub-networks (Shazeer et al., 2017,
  arXiv:1701.06538); highway/residual connections control how much signal passes
  a layer (Srivastava et al., *Highway Networks*, 2015, arXiv:1505.00387).

So the *control-of-information-flow* reading captures a genuine and increasingly
dominant aspect of how these systems work. As a **lens**, it is defensible and
even illuminating — much of the progress from 2017 on is about better routing.

## The overreaching half: "controllers, *not* learners" is a false dichotomy

The strong form of the claim does not hold, for a structural reason:

1. **The controllers are themselves learned.** Attention weights, gates, and
   routers are computed by parameters set by gradient descent. The network does
   not *come* with a controller; it *learns* one. "Not a learning machine"
   therefore contradicts how the control structures arise — control and learning
   are not alternatives, the network **learns the controller**.
2. **It displaces, not replaces, the dominant frame.** The established accounts —
   universal function approximation and representation learning — are not refuted
   by noting that some computation is routing. A useful additional lens is not a
   new fundamental ontology.
3. **The proposed control/learning *separation* is a design proposal, not a
   result.** A network that configures another (Pygmalion's "control unit" with an
   API to a "learning unit") resembles real ideas — hypernetworks, meta-learning,
   learned optimisers — but those *also* learn the controller, so they support the
   "routing matters" reading while undercutting "not learners."

## Verdict

**Partially supported as a lens; false in its strong form.** "Neural networks
regulate information flow" is true and important (attention, gating, routing are
real flow-control mechanisms). "Neural networks are controllers *and not*
learners" is a false dichotomy, because the controllers are learned — so it is
Pygmalion's framing to *argue for in specific mechanisms*, not a fact to assert.
For Patchi, the actionable form is narrow and defensible: **treat gating/attention
as the place where the control reading earns its keep**, and drop the "not
learners" claim. The block/category layer already leans this way — a `NeuralBlock`
is an explicit, inspectable transform you reason about structurally rather than a
pile of opaque learned weights — which is the control reading made concrete,
without denying that, in a fuller system, those transforms would be learned.
