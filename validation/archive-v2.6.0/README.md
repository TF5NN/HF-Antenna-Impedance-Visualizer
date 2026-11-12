# Archived: v2.6.0 validation reports

These reports describe **v2.6.0** (March 2026) and are kept for the record only.
Do not rely on them for the current tool:

- The antenna model was replaced in v3.0.0, so the end-fed, dipole and
  counterpoise reports describe a model that no longer exists.
- The tuner solver had a sign error that the tuner-matching report did not catch.

The current evidence is [`../nec_comparison_v3.md`](../nec_comparison_v3.md), and
[`../check_v3.mjs`](../check_v3.mjs) re-runs that comparison before every publish.
[`../qgate_validation.md`](../qgate_validation.md) stays in the main folder because
its Q-gate analysis still applies and the source refers to it.
