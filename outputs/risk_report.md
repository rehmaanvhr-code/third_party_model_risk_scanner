# Third party AI model risk report

Scanned: /home/claude/govrepos/third_party_model_risk_scanner/sample_project. 17 dependencies found across 6 files.

Risk bands: high 8, medium 9, low 0.

## Checklist

Documented provenance (weight 2). Is it clear who built the model, from what, and under what process? Source: OSFI E-23 section 3 (model development and vendor models); NIST AI RMF Map 4.1.

License known and compatible (weight 2). Is the license identified and does it allow commercial use in a regulated setting? Source: ISO/IEC 42001 A.10; NIST AI RMF Govern 6.1.

Model card or system card available (weight 2). Has the vendor published intended use, limitations and evaluation results? Source: NIST AI RMF Map 3.4; EU AI Act Art. 53 for general purpose models.

Version pinned in code or requirements (weight 2). Is the exact version fixed so behaviour does not change silently? Source: OSFI E-23 section 4 (model inventory and change control); NIST AI RMF Manage 2.4.

Data residency and retention understood (weight 2). Does data leave the organisation, and if so where is it processed and how long is it kept? Source: OSFI Guideline B-10 third party risk; ISO/IEC 42001 A.7.

Independent evaluation evidence (weight 1). Has the organisation tested the model on its own data rather than relying on vendor claims? Source: OSFI E-23 section 3 (validation); NIST AI RMF Measure 2.5.

Vendor incident and deprecation process (weight 1). Will the vendor tell you when the model changes, fails or is retired, and is there a fallback? Source: NIST AI RMF Govern 6.2; EU AI Act Art. 73.

## Findings

### High risk

sentence_transformers (package) in services/embeddings.py. Score 0.33. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

transformers (package) in services/embeddings.py. Score 0.33. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

langchain (package) in services/legacy_rag.py. Score 0.33. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

langchain_community (package) in services/legacy_rag.py. Score 0.33. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

torch (package) in services/legacy_rag.py. Score 0.33. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

ultralytics/yolov5 (model_id) in services/legacy_rag.py. Score 0.33. Vendor: Ultralytics. License: AGPL 3.0 (commercial license sold separately).
Open items: License known and compatible; Model card or system card available; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

anthropic (package) in services/chat_service.py. Score 0.33. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

churn_lstm.pt (model_file) in models/churn_lstm.pt. Score 0.33. Vendor: unknown. License: unknown.
Open items: Documented provenance; Model card or system card available; Version pinned in code or requirements; Independent evaluation evidence; Vendor incident and deprecation process.

### Medium risk

distilbert-base-uncased-finetuned-sst-2-english (model_id) in services/embeddings.py. Score 0.50. Vendor: Hugging Face. License: Apache 2.0.
Open items: Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

boto3 bedrock (package) in services/fraud_rules.py. Score 0.50. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

openai (package) in services/chat_service.py. Score 0.50. Vendor: unknown. License: unknown.
Open items: Model card or system card available; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

command-r (model_id) in services/legacy_rag.py. Score 0.50. Vendor: Cohere. License: proprietary; open weights under CC BY NC for research.
Open items: Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

claude-sonnet-4-5 (model_id) in services/chat_service.py. Score 0.50. Vendor: Anthropic. License: proprietary, commercial terms.
Open items: Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

gpt-4o (model_id) in services/chat_service.py. Score 0.50. Vendor: OpenAI. License: proprietary, API terms of use.
Open items: Version pinned in code or requirements; Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

fraud_gbm_v3.pkl (model_file) in models/fraud_gbm_v3.pkl. Score 0.50. Vendor: unknown. License: unknown.
Open items: Documented provenance; Model card or system card available; Independent evaluation evidence; Vendor incident and deprecation process.

anthropic.claude-3-haiku-20240307-v1:0 (model_id) in services/fraud_rules.py. Score 0.67. Vendor: Anthropic via AWS Bedrock. License: proprietary, AWS Marketplace terms.
Open items: Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

sentence-transformers/all-MiniLM-L6-v2 (model_id) in services/embeddings.py. Score 0.67. Vendor: Hugging Face community (sentence transformers). License: Apache 2.0.
Open items: Data residency and retention understood; Independent evaluation evidence; Vendor incident and deprecation process.

## What to do with this

Items marked data residency, evaluation and incident process cannot be inferred from code. Set them to true in data/known_models.json once the organisation has confirmed them with the vendor, then rerun. A pickled model file with no documentation nearby is a sign the model is not in the inventory at all.