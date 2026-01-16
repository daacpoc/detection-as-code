[![sumo-tf-deploy](https://github.com/dc401/cwx-demo-sumo/actions/workflows/sumo-tf-deploy.yml/badge.svg)](https://github.com/dc401/cwx-demo-sumo/actions/workflows/sumo-tf-deploy.yml)
# cybwerwox-demo-sumo
This repo is for the Detection as Code CI/CD pipeline demo in the Cyberwox series by Day Johnson and Dennis Chow for Sumo Logic demonstration using synthetic AI testing.

## Do you want to learn more?
Please consider supporting the work for future contributions.

### Automating Security Detection Engineering

<a href="https://www.packtpub.com/product/automating-security-detection-engineering/9781837636419?utm_source=github&utm_medium=repository&utm_campaign=9781837636419"><img src="https://content.packt.com/_/image/original/B22006/cover_image_large.jpg" alt="Automating Security Detection Engineering" height="256px" align="right"></a>

This is the code repository for [Automating Security Detection Engineering](https://www.packtpub.com/product/automating-security-detection-engineering/9781837636419?utm_source=github&utm_medium=repository&utm_campaign=9781837636419), published by Packt.

**A hands-on guide to implementing Detection as Code**

## What is this book about?
This book focuses entirely on the automation of detection engineering with practice labs, and technical guidance that optimizes and scales detection focused programs. Using this book as a bootstrap, practitioners can mature their program and free up valuable engineering time.

This book covers the following exciting features:
* Understand the architecture of Detection as Code implementations
* Develop custom test functions using Python and Terraform
* Leverage common tools like GitHub and Python 3.x to create detection-focused CI/CD pipelines
* Integrate cutting-edge technology and operational patterns to further refine program efficacy
* Apply monitoring techniques to continuously assess use case health
* Create, structure, and commit detections to a code repository

If you feel this book is for you, get your [copy](https://www.amazon.com/dp/1837636419) today!

<a href="https://www.packtpub.com/?utm_source=github&utm_medium=banner&utm_campaign=GitHubBanner"><img src="https://raw.githubusercontent.com/PacktPublishing/GitHub/master/GitHub.png" 
alt="https://www.packtpub.com/" border="5" /></a>

---

## Pipeline behavior in this repo

This repository deploys **Sumo Logic Log Monitors** using Terraform.

### Branching behavior

* **Pull Requests** to `main`: runs `terraform fmt -check`, `terraform init`, `terraform validate`, and `terraform plan`.
* **Pushes to `main`**: runs the same checks and then `terraform apply`.

### Required GitHub Actions secrets

Terraform deploy:

* `TF_VAR_SUMOLOGIC_ACCESS_ID`
* `TF_VAR_SUMOLOGIC_ACCESS_KEY`

Optional (enables smoke tests):

* `SUMO_API_BASE_URL` – your deployment API base including `/api` (example: `https://api.us1.sumologic.com/api`). Sumo documents that the correct endpoint depends on your deployment region/pod. citeturn3search0turn3search2
* `SUMO_HTTP_SOURCE_URL` – the unique URL for a Hosted Collector **HTTP Logs & Metrics Source** used by CI to ingest test logs. citeturn3search7turn3search14

Optional (enables Sigma generation):

* `POE_API_KEY` – your Poe API key (OpenAI-compatible endpoint). citeturn2search5turn2search1

### Sigma build artifacts (conversion)

If you add Sigma rules under `rules/sigma/`, CI will:

1. Start a **local** `sigconverter.io` container (Docker build + run). citeturn1view0
2. Convert Sigma rules into Sumo queries and upload them as a workflow artifact.

### Smoke tests (ingest + query)

If `SUMO_API_BASE_URL` and `SUMO_HTTP_SOURCE_URL` are set, CI will:

1. Upload `tests/*.log` samples to your HTTP Source.
2. Execute searches defined in `tests/smoke-tests.yml` using the Search Job API (`POST /v1/search/jobs`) and fail the build if expectations are not met. citeturn3search0

---

## Generating Sigma rules with Poe (Claude Opus 4.5)

This repo includes `tools/poe_generate_sigma.py` which sends `prompt.md` (or any prompt file) to Poe's OpenAI-compatible API and writes Sigma YAML files under `rules/sigma/`. citeturn2search5turn2search1

Example:

```bash
export POE_API_KEY='...'
python tools/poe_generate_sigma.py --prompt prompt.md --out-dir rules/sigma
```

---

## Running sigconverter.io locally on your Terraform box

If the box you provision with Terraform is where you want conversion to run, use `tools/install_sigconverter.sh` to build + run sigconverter.io via Docker (listens on port 8000 by default). The upstream project supports this Docker flow. citeturn1view0
