Azure Storage incident handoff
=============================

Review whether the preserved partner export path in storage account `prodpartnerblob`
still leaves a reusable SAS exposure under container `handoff-audits`.

Produce `/workdir/blob_sas_review.json` for ticket `BLOB-3814`.

The review must keep the preserved queue assignment and the canonical packaging mode from the
handoff profile.
