# Phase 1 historical reference

The immutable Phase 1 reference is Git commit `60405f7701b898aad6e753e5f441b73195d04cfa`. Its [frozen run manifest](../outputs/manifests/final_run.json), [dataset summary](../outputs/manifests/dataset_summary.json), [results](../docs/RESULTS_INTERPRETATION.md) and [limitations](../docs/LIMITATIONS.md) remain in their original locations. Phase 1 contained 31 passages, 6 dev queries and 12 test queries; its source-conditioned labels were agent-generated and not independently human reviewed.

Its selected development weights were (0, 0), so the selected method matched RRF. Its nonzero setting was exploratory; the previously inspected test must not be used to choose Phase 2 settings or presented as new independent evidence. Reproduction status and exact current hashes are recorded separately in `outputs/phase2/manifests/stage_13.json` and `outputs/phase2/logs/`.
