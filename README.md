# Third party model risk scanner

Most organisations will consume AI rather than build it. This scanner walks a code base and finds the AI that was bought or borrowed: imports of vendor SDKs (OpenAI, Anthropic, Cohere, Vertex, Bedrock through boto3, LangChain), model identifiers passed as strings (gpt-4o, a Hugging Face repo id, a torch hub path), and serialised model files sitting in the tree (.pkl, .pt, .onnx, .safetensors). It builds an inventory, looks each item up in a small table of known models and licenses, and scores it against a seven item checklist drawn from OSFI Guideline E-23, OSFI B-10 and the NIST AI RMF third party guidance. The output is a csv inventory, a markdown risk report and a bar chart of checklist coverage.

## Connection to the research

"The Governance Lag: Why Slow AI Adoption Is the Larger Risk" (Rehman, 2026) argues that governance frameworks were written with the in house model in mind, while the adoption that is actually happening runs through APIs and open weights that nobody in the organisation trained. The gap between the two is where the risk accumulates: a model that is not in the inventory is not validated, not monitored and not documented, and the organisation does not know it. The first governance task is therefore discovery, and discovery can be automated. This repo is that argument as a tool.

## Why this matters in financial services

OSFI E-23 brings vendor and open source models into scope of model risk management and keeps the institution accountable for validating and monitoring them. OSFI B-10 covers the third party relationship itself. The EU AI Act puts duties on deployers that use general purpose models, and ISO 42001 Annex A.10 asks for allocated responsibility with suppliers. An inventory is the precondition for all of it. Running this scanner against each repository in an institution's estate, then merging the csv outputs, gives a first draft of the enterprise AI dependency inventory and a list of open questions per dependency.

## How to run

```
pip install -r requirements.txt
python scanner.py
python scanner.py /path/to/your/repo
pytest
```

With no argument it scans `sample_project/`, which contains four small fake service files, a requirements file and two fake model artifacts. The sample is built so that it exercises every detection rule.

## What the scores mean

Each dependency gets a weighted score between 0 and 1 across seven checks: documented provenance, license known and compatible, model card available, version pinned, data residency confirmed, independent evaluation, and vendor incident and deprecation process. The first three come from `data/known_models.json`. Version pinning is read from the requirements file for packages, from a date or version suffix for model ids, and from a version tag in the filename for model files. The last three can only be answered by the organisation, so they default to false and the report says so. Scores at or above 0.8 are low risk, 0.5 to 0.8 medium, below 0.5 high.

In the sample run the pickled fraud model and the churn weights score poorly because there is nothing in the tree that says where they came from. The yolov5 dependency drops to high risk because its AGPL license is flagged as restrictive for commercial use. The hosted APIs land in the middle: vendor documentation exists, but data residency and incident process are unconfirmed.

## Data

`data/checklist.json` holds the checks, weights, source references and band thresholds. `data/known_models.json` holds a handful of well known models and APIs with vendor, license and documentation status, written from public vendor pages as of late 2026. Add your own models there, and set data_residency_confirmed, evaluated_internally and incident_process to true once they have been confirmed, then rerun.

## Limitations

Detection is regex based and will miss model ids built from variables, config files, or environment variables. It only reads Python. The known models table is small and the license and documentation facts in it should be rechecked before relying on them. A scanner finds what is in the code; it does not find what is in a vendor contract or a SaaS tool used outside the code base.

Saif Rehman, MMAI, Smith School of Business, Queen's University
