"""Build the concise report from measured summaries; requires reportlab and pymupdf."""
import json
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

out = Path('outputs')
styles = getSampleStyleSheet()
styles['BodyText'].fontSize=10
styles['BodyText'].leading=14
story=[]
def p(text): story.append(Paragraph(text,styles['BodyText']));story.append(Spacer(1,8))
def h(text): story.append(Paragraph(text,styles['Heading2']))
story.append(Paragraph('Local LLM Structured Output Evaluation',styles['Title']))
p('NLP Project I | Technical report | 19 November 2026')
h('1. Task and data')
p('The task combines seven-class Turkish news classification (dunya, ekonomi, kultur, saglik, siyaset, spor, teknoloji) with PERSON, ORGANIZATION and LOCATION extraction. TTC-4900 provides category labels but no gold entity labels. A deterministic sample uses 15 articles per class (105 total), restricted to 300-2500 characters; a separate 35-document development set was used for design trials. Sampling seed: 20261109. This length restriction limits generalization to long articles; a character limit does not guarantee a token limit.')
p('I manually selected the entity names in all 105 articles using a local browser interface. I selected them myself, rather than correcting prefilled model suggestions. The final reviewed file contains 949 entity annotations. The validation code checks required fields, entity types and whether the selected text appears in the article. These checks do not prove that every label is correct. I was the only annotator, so there was no independent review.')
p('The hardest part of annotation was deciding where a name started and ended. I did not always know the full names of the people or organizations mentioned. Foreign names listed one after another were especially confusing. I sometimes searched Google to identify the people and understand which parts belonged to each name. I also found it difficult to recognize unfamiliar organizations and separate their names when several appeared together. These difficulties are a possible source of mistakes in my manual labels.')
p('Rules: annotate explicit person names, named organizations (including sports clubs), and geographic names. Exclude titles, products, dates, quantities and events. Preserve source spelling and underscores. Retain each distinct surface form once per document; short and full names are separate surface forms, not merged aliases. Use the longest relevant name rather than nested entities. Entity scoring requires type and normalized exact surface match: Unicode NFC, collapsed whitespace, and Turkish-aware casing (capital dotted I to i and capital dotless I to dotless i before lowercasing). No partial match is used.')
h('2. Reproducibility and controlled comparison')
m=json.loads((out/'main_reviewed/manifest.json').read_text(encoding='utf-8'))
p('Inference is local through Ollama 0.40.16. Model tag: qwen2.5:3b; observed local model ID: 357c53fb659c; parameter size: 3.1B; quantization: Q4_K_M. Hardware: NVIDIA RTX 3050 Laptop GPU, 4 GB VRAM. Python 3.13.17, ollama Python package 0.6.1, Pydantic 2.12.4. No cloud LLM API is called by the inference pipeline.')
p('Main run: temperature=0, seed=42, top_k=40, top_p=0.9, num_ctx=4096, num_predict=512, keep_alive=10m, stream=false. The secondary run changes only temperature to 1. Other unspecified runtime options retain Ollama defaults. Both settings use identical system/user messages, JSON schema text in the prompt, sample order and options. Prompt-only omits the format key entirely. Schema-constrained adds format=OUTPUT_JSON_SCHEMA. No few-shot examples are used. Each article is run prompt-only first, then constrained; latency is not an unbiased speed comparison because of loading/caching/order effects.')
p('The schema requires category plus entities.persons, entities.organizations and entities.locations as string arrays (maximum 20 per type); extra fields are forbidden. The typed-list representation replaced a repetitive array-of-objects design after development trials. The final prompt was selected on development data; the test labels were not used to optimize it. An initial exploratory test article was inspected before the final split was frozen, so the process is not a fully pristine blind evaluation.')
story.append(PageBreak())
h('3. Parsing, validation and metrics')
p('json.loads is first applied directly to raw model text. If parsing fails, the cleaner removes surrounding Markdown fences or extracts the first balanced JSON object while respecting quoted braces and escapes. It does not repair broken quotes or unfinished JSON. Exceptions are recorded rather than crashing the run. Parsed data is validated against the Pydantic schema. JSON parsing and schema validity are measured separately; syntactically valid JSON can still have missing fields or wrong types.')
p('All rates use all 105 articles, including failures. Classification accuracy is correct labels divided by 105. An invalid output counts as an incorrect class and an empty entity prediction. Entity counts are accumulated per document as typed multisets (duplicate predictions are penalized): precision=TP/(TP+FP), recall=TP/(TP+FN), F1=2TP/(2TP+FP+FN). These are end-to-end metrics, not scores conditional on successful parsing.')
h('4. Measured results')
data=[['Temp.','Setting','Raw JSON','Clean JSON','Schema','Accuracy','Entity F1']]
results={}
for temp,folder in [(0,'main_reviewed'),(1,'temperature1_reviewed')]:
    s=json.loads((out/folder/'summary.json').read_text())['settings'];results[temp]=s
    for setting,v in s.items():
        data.append([str(temp),'Prompt-only' if setting=='prompt_only' else 'Schema']+[f'{100*v[k]:.2f}%' for k in ['raw_json_success_rate','cleaned_json_success_rate','schema_validity_rate','classification_accuracy','entity_f1_micro']])
t=Table(data,colWidths=[35,85,65,65,60,60,65]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#163e4b')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),9),('GRID',(0,0),(-1,-1),.3,colors.lightgrey)]));story.append(t);story.append(Spacer(1,12))
for temp,s in results.items():
    for setting,v in s.items():
        p(f"T={temp}, {setting}: entity TP={v['entity_tp']}, FP={v['entity_fp']}, FN={v['entity_fn']}; precision={v['entity_precision_micro']:.3f}, recall={v['entity_recall_micro']:.3f}.")
story.append(PageBreak())
h('5. Interpretation and limitations')
p('At temperature 0, constrained decoding raises schema validity from 92.38% to 99.05% and end-to-end classification accuracy from 49.52% to 54.29% (52 to 57 correct). Entity F1 decreases from 30.05% to 29.63%. The constrained run finds more correct entities (257 vs 226) but also produces more false positives (529 vs 329). Thus structural correctness does not imply semantic correctness. Some accuracy improvement can come from converting invalid outputs into usable predictions rather than better class reasoning.')
for setting in ['prompt_only','schema_constrained']:
    a,b=results[0][setting],results[1][setting]
    p(f"Raising temperature for {setting} changes raw parsing by {100*(b['raw_json_success_rate']-a['raw_json_success_rate']):+.2f} percentage points, classification accuracy by {100*(b['classification_accuracy']-a['classification_accuracy']):+.2f}, and entity F1 by {100*(b['entity_f1_micro']-a['entity_f1_micro']):+.2f}. These are observations from one fixed seed, not universal temperature effects.")
p('At temperature 0 there were no transport errors; two prompt-only outputs and one constrained output hit the generation limit and remained incomplete. Cleaning did not rescue these truncated outputs. Other limitations include a small length-filtered sample, single human review, strict surface-form matching, the 20-entity output cap, low-capacity quantized inference and no repeated-seed confidence intervals. Long entity lists and category overlap can reduce performance. The 7.6B candidate was only tried on one cold call; that observation is not a reliable comparative speed benchmark.')
h('Qualitative examples')
p('In the e-prescription article (ttc4900-row-2847), both modes predicted ekonomi instead of the dataset label saglik. The output also included the common noun for pharmacies as an organization. This illustrates category overlap and over-extraction of non-named entities. In the Amy Winehouse article (ttc4900-row-2444), the model failed to recover the expected person names and confused the court mention with a location. The JSON structure alone could not prevent these semantic errors.')
h('References and artifacts')
p('TTC-4900: github.com/savasy/TurkishTextClassification. Ollama structured outputs: docs.ollama.com/capabilities/structured-outputs. Code: scripts/run_experiment.py. Frozen annotations: outputs/reviewed_annotations_20261119.jsonl. Raw outputs, summaries and manifests: outputs/main_reviewed and outputs/temperature1_reviewed. The final video must demonstrate live runs; saved rehearsal logs alone do not meet that requirement.')
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.drawRightString(550,25,str(doc.page))
SimpleDocTemplate(str(out/'technical_report.pdf'),pagesize=A4,rightMargin=40,leftMargin=40,topMargin=35,bottomMargin=40).build(story,onFirstPage=footer,onLaterPages=footer)
print(out/'technical_report.pdf')
