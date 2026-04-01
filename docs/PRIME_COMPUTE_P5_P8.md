# Prime Intellect compute for P5 and P8

This runbook describes using **persistent disks** and **Prime instances (pods)** so large P5 and P8 evaluations survive instance termination and can use machines with more vCPU/RAM than a laptop. Commands align with the current [Prime Intellect CLI documentation](https://docs.primeintellect.ai/cli-reference/introduction.md).

**Scope:** P5 multi-scenario generation and held-out scaling eval; P8 meta collapse sweep and meta eval. P6 Prime Inference is documented under P6 in [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md).

## Prerequisites

- [Prime CLI](https://docs.primeintellect.ai/cli-reference/introduction.md) configured (`prime login`).
- API key with **Disks** and **Instances** read/write where required ([API keys](https://docs.primeintellect.ai/api-reference/api-keys.md)).
- Disk and instance must be in the **same provider and datacenter** ([use persistent storage with instances](https://docs.primeintellect.ai/tutorials-storage/use-persistent-storage-with-instances.md)).

## 1. Persistent disk

List storage offerings:

```bash
prime availability disks
prime availability disks --regions united_states
```

Create a disk (use a short **id** from the table; size in GB). Disks bill hourly until terminated ([Managing Disks](https://docs.primeintellect.ai/cli-reference/managing-disks.md)).

```bash
prime disks create --id <short_id> --size 500 --name labtrust-p5-p8-runs
```

Wait until status is **ACTIVE** (`prime disks list` or `prime disks get <disk-id>`). Status values are documented in [Managing Disks](https://docs.primeintellect.ai/cli-reference/managing-disks.md).

Alternatively, create a disk from the dashboard: **Storage** then **Create Disk** ([create persistent storage](https://docs.primeintellect.ai/tutorials-storage/create-persistent-storage.md)).

## 2. Instance (pod) with disk attached

List GPU/compute availability:

```bash
prime availability list
```

Create an instance and attach the disk ([Provision Instance](https://docs.primeintellect.ai/cli-reference/provision-gpu.md)):

```bash
prime pods create --id <availability_short_id> --disks <your-disk-uuid>
```

Use the dashboard **Filter by your existing disks** so only compatible locations appear ([use persistent storage with instances](https://docs.primeintellect.ai/tutorials-storage/use-persistent-storage-with-instances.md)).

After the instance is running, open **instance details** to find the **mount path** for the attached volume (same disk can attach to multiple instances when the provider supports it).

Manage the instance:

```bash
prime pods status <pod-id>
prime pods ssh <pod-id>
prime pods terminate <pod-id>
```

Configure SSH key per [Provision Instance](https://docs.primeintellect.ai/cli-reference/provision-gpu.md).

**CPU-heavy note:** Prime’s provisioning flow is oriented to GPU SKUs. For Python-only thin-slice sims, choose an offering with enough **vCPUs and RAM**; if only GPU-backed SKUs exist, you still pay for the GPU while running CPU-bound jobs.

## 3. On the instance

1. Mount path: use the path shown in instance details (shared filesystem).
2. Clone the repo under the mount, or symlink `datasets/runs` to a directory on the mount so artifacts persist after `prime pods terminate`.
3. Install Python 3 and dependencies (`pip install -e impl/` or install from project root as you do locally).
4. Environment:

```bash
export LABTRUST_KERNEL_DIR=/path/to/labtrust-portfolio/kernel
export PYTHONPATH=/path/to/labtrust-portfolio/impl/src
```

## 4. P5 pipeline on Prime

**Generate runs** (writes under `--out`, default `datasets/runs/multiscenario_runs`). Default `--profile all` includes every scenario YAML under `bench/maestro/scenarios/` (seven ids as of this doc, including `regime_stress_v1` and `rep_cps_scheduling_v0`). Use `--profile real_world` to omit `toy_lab_v0`.

```bash
cd /path/to/labtrust-portfolio
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/generate_multiscenario_runs.py --out datasets/runs/multiscenario_runs --seeds 20 --fault-mix
```

**Shard across multiple instances** (same `--out` on a shared disk). Examples:

```bash
# Worker A: two scenarios, seeds 1–10
python scripts/generate_multiscenario_runs.py --out datasets/runs/multiscenario_runs \
  --scenarios toy_lab_v0,lab_profile_v0 --fault-mix --seed-min 1 --seed-max 10
# Worker B: same scenarios, seeds 11–20
python scripts/generate_multiscenario_runs.py --out datasets/runs/multiscenario_runs \
  --scenarios toy_lab_v0,lab_profile_v0 --fault-mix --seed-min 11 --seed-max 20
# Worker C: other scenarios, seeds 1–20
python scripts/generate_multiscenario_runs.py --out datasets/runs/multiscenario_runs \
  --scenarios warehouse_v0,traffic_v0,regime_stress_v0,regime_stress_v1,rep_cps_scheduling_v0 --fault-mix --seeds 20
```

When all shards finish, run held-out eval **once** (and optionally a second pass for leave-one-family-out):

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/scaling_heldout_eval.py \
  --runs-dir datasets/runs/multiscenario_runs \
  --out datasets/runs/scaling_eval
# Optional stricter OOS by taxonomy family (lab / warehouse / traffic):
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/scaling_heldout_eval.py \
  --runs-dir datasets/runs/multiscenario_runs \
  --out datasets/runs/scaling_eval_family \
  --holdout-mode family --no-secondary
python scripts/export_scaling_tables.py --results datasets/runs/scaling_eval/heldout_results.json
python scripts/plot_scaling_mae.py --results datasets/runs/scaling_eval/heldout_results.json
```

## 5. P8 pipeline on Prime

Publishable P8 runs **two scenarios** (`regime_stress_v0` and `regime_stress_v1`) via [run_paper_experiments.py](../scripts/run_paper_experiments.py) `p8()` (not quick). On one instance with the disk attached:

```bash
cd /path/to/labtrust-portfolio
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/run_paper_experiments.py --paper P8
```

Writes `datasets/runs/meta_eval/comparison.json`, `datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json`, and per-dir `collapse_sweep.json`. Then export and verify:

```bash
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/comparison.json
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/export_meta_tables.py --comparison datasets/runs/meta_eval/scenario_regime_stress_v1/comparison.json
PYTHONPATH=impl/src LABTRUST_KERNEL_DIR=kernel \
  python scripts/verify_p8_meta_artifacts.py --comparison datasets/runs/meta_eval/comparison.json \
    --sweep datasets/runs/meta_eval/collapse_sweep.json --strict-publishable
python scripts/plot_meta_collapse.py --sweep datasets/runs/meta_eval/collapse_sweep.json
```

See [EVALS_RUNBOOK.md](EVALS_RUNBOOK.md) (P8). Persist `datasets/runs/meta_eval` on the attached disk so you can terminate the pod and later attach the disk to export tables again.

## 6. Teardown and cost

- **Instance:** `prime pods terminate <pod-id>` when jobs finish.
- **Disk:** Keeps data; attach to a new instance to resume. **Terminate disk** only when data is backed up: `prime disks terminate <disk-id>` ([Managing Disks](https://docs.primeintellect.ai/cli-reference/managing-disks.md)) — irreversible.

Disks incur hourly charges from creation until termination; larger disks cost more ([Managing Disks](https://docs.primeintellect.ai/cli-reference/managing-disks.md)).

## References

| Topic | URL |
|-------|-----|
| CLI overview | https://docs.primeintellect.ai/cli-reference/introduction.md |
| Managing disks | https://docs.primeintellect.ai/cli-reference/managing-disks.md |
| Provision instance + attach disks | https://docs.primeintellect.ai/cli-reference/provision-gpu.md |
| Attach disk / mount path | https://docs.primeintellect.ai/tutorials-storage/use-persistent-storage-with-instances.md |
| Create disk (UI) | https://docs.primeintellect.ai/tutorials-storage/create-persistent-storage.md |
