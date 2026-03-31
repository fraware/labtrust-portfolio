# P1 Table Package

## Trace-family summary table

| Family | Type | Traces | Controllers | Shared keyed resources | Natural handover |
| --- | --- | ---: | --- | --- | --- |
| `lab_orchestration_partner_like` | quasi-real partner-like logs | 30 | controller_a, controller_b | yes | yes |
| `simulator_documented_semantics` | simulator-generated | 30 | planner_1, planner_2 | yes | yes |
| `incident_reconstructed` | reconstructed incident traces | 30 | robot_r1, robot_r2 | yes | yes |
| **Total** | mixed | **90** | multi-writer | yes | yes |

## Main benchmark + real-trace table

| Corpus | Sequence exact-match | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Benchmark (`contracts_eval`) | 100.0% | 37 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| Lab quasi-real (`contracts_eval_real`) | 0.0% | 30 | 0 | 30 | 1.0000 | 0.5000 | 0.6667 |
| Simulator quasi-real (`contracts_eval_real_sim`) | 100.0% | 45 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| Incident reconstructed (`contracts_eval_real_incident`) | 76.7% | 53 | 0 | 7 | 1.0000 | 0.8833 | 0.9381 |

## Strong baseline comparison table (benchmark corpus)

| Baseline | Exact-match | TP | FP | FN | False denials on valid traces | Runtime mean us |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B1 versioned OCC | 0.7593 | 18 | 2 | 19 | 2 | 1.4072 |
| B2 lease expiry/renewal | 0.5556 | 12 | 3 | 25 | 3 | 1.6156 |
| B3 lock lifecycle | 0.5370 | 13 | 3 | 24 | 3 | 1.5138 |
| B4 state-machine-only | 0.7037 | 27 | 9 | 10 | 9 | 1.8689 |
| B5 practical heuristic | 0.9815 | 37 | 2 | 0 | 2 | 2.9599 |

## Per-class breakdown table (benchmark, violations missed)

| Failure class | Full contract | B1 OCC | B2 Lease | B3 Lock | B4 SM-only | B5 Practical |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| split_brain | 0 | 17 | 9 | 8 | 0 | 0 |
| stale_write | 0 | 0 | 7 | 7 | -2 | 0 |
| reorder | 0 | 0 | 8 | 8 | 8 | 0 |
| unknown_key | 0 | 0 | 0 | 0 | 0 | 0 |

## Overhead table

| Corpus | p99 latency us | Normalization mean us | Validation mean us | State update mean us | Events/sec |
| --- | ---: | ---: | ---: | ---: | ---: |
| Benchmark | 6.9 | 0.7341 | 2.5575 | 11.0608 | 5531.58 |
| Lab quasi-real | 19.4 | 1.0589 | 3.7344 | 24.7667 | 3870.44 |
| Simulator quasi-real | 9.4 | 0.8311 | 2.7656 | 24.9422 | 5743.42 |
| Incident reconstructed | 23.1 | 0.9133 | 3.3022 | 32.0324 | 4188.87 |

## Case-study comparison table

| Mode | Split-brain handover invalidity | Timing-sensitive invalidity | Reason-coded replay diagnosis |
| --- | --- | --- | --- |
| Delivery correctness only | missed | missed | no |
| Strong baseline (B5 practical) | denied | partially missed | limited |
| Full contract | denied | denied | yes (`split_brain`, `stale_write`, `reorder_violation`) |
