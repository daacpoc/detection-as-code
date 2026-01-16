# Sigma rules

Put your Sigma YAML rules here.

## Generating with Poe (Claude Opus 4.5)

If you keep your detection prompt in `prompt.md`, you can generate Sigma rules into this folder with:

```bash
export POE_API_KEY='...'
python tools/poe_generate_sigma.py --prompt prompt.md --out-dir rules/sigma
```

The Poe API provides an OpenAI-compatible endpoint at `https://api.poe.com/v1/chat/completions`. citeturn2search5

## Converting Sigma -> Sumo queries

This repo converts Sigma rules to Sumo query files in CI using a **local** `sigconverter.io` container.
The upstream project supports running locally via Docker (`docker build -t sigconverter.io .` and `docker run -p 8000:8000 sigconverter.io`). citeturn1view0

To run conversion locally:

```bash
# Start sigconverter.io (local)
git clone https://github.com/magicsword-io/sigconverter.io
cd sigconverter.io
docker build -t sigconverter.io .
docker run -d --rm --name sigconverter -p 8000:8000 sigconverter.io

# Convert
cd ..
export SIGCONVERTER_URL='http://localhost:8000/api/v1/convert'
python tools/convert_sigma_to_sumo.py --sigma-dir rules/sigma --out-dir build/sumo_queries
```
