# Building `DRAFT.tex`

## Portable preamble

`DRAFT.tex` uses `\IfFileExists{microtype.sty}{...}{}` so a missing `microtype` package does not stop the build (e.g. minimal TeX installs).

## TeX Live (Debian/Ubuntu)

Install a reasonable subset:

```bash
sudo apt-get install -y texlive-latex-base texlive-latex-recommended \
  texlive-fonts-recommended texlive-latex-extra
```

Optional typography: `sudo apt-get install -y texlive-microtype`.

## MiKTeX (Windows)

Install `microtype`, `lm`, `geometry`, `amsmath`, `booktabs`, `hyperref`, `listings`, `caption`, `subcaption`, `tabularx`, `longtable` via MiKTeX Console (Packages) or `mpm --install=<package>`.

## One-shot compile

From the repo root:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory papers/P3_Replay papers/P3_Replay/DRAFT.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory papers/P3_Replay papers/P3_Replay/DRAFT.tex
```

Figures under `papers/P3_Replay/figures/` must exist (see `scripts/export_p3_paper_figures.py`).

## CI

GitHub Actions job **`p3-paper-latex`** (see `.github/workflows/ci.yml`) compiles `papers/P3_Replay/DRAFT.tex` twice on Ubuntu with `texlive-latex-extra`. Local builds may produce `DRAFT.pdf`, `DRAFT.aux`, `DRAFT.log`, etc.; those artifacts are listed in `papers/P3_Replay/.gitignore` and should not be committed.

## Syncing numbers

After changing `summary.json`, regenerate tables and figures, then align **abstract and tables in `DRAFT.tex`** with `overhead_stats`, `baseline_overhead`, and `l1_twin_summary` from the summary file.
