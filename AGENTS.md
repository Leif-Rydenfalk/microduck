# Preserve reviewable versions

Leif requested explicit version separation on 2026-09-08 because the work will
be reviewed by his boss. This supplements the workshop rules and TRIAD.

- Preserve superseded part and connection iterations through TRIAD. Never edit
  their design files in place after superseding them; new evidence may still
  be appended under the established evidence rules.
- Before changing a published drawing, report or handoff, preserve its complete
  reviewable version and source commit. Work on the next version separately.
  Git commits preserve source history; numbered frozen packages preserve what
  a reviewer actually received. Neither proves every intermediate rerender was
  retained before this instruction.
- `reviews/vNNNN/` and `reviews/Microduck-review-vNNNN.zip` are immutable review
  releases. Never overwrite, regenerate or amend an issued version. Correct
  mistakes in the next numbered version, recording the preceding version.
- Build review packages from explicit committed revisions using
  `tools/freeze_review.py`; include a file hash manifest and verification scope.
  Keep experiments, synthetic data and unverified candidates labeled. Do not
  describe an engineering review as manufacturing approval or verified 1:1.
- Preserve unrelated sessions' files. Do not include private communications,
  credentials or runtime payloads in a review package. Sending a package to a
  new person requires the user's authorization; preparing one does not.
