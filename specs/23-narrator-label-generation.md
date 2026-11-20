---
role: authored
---
# Mycel · 23 Narrator Label Generation

The owner approved the Label Generation design and asked to proceed on 18 November 2026. The default hosted model and reasoning effort follow [MYC-D99](22-narrator-summary-quality.md#decisions).

Narrator generates one short label from a single supplied text. Callers can use the label as a Chat Session title or a codename for a block or message. The caller supplies the text and a positive maximum word count. The label names the central subject, action or outcome. Additional words should make that focus more precise. A label may be a single word or a fragment. It may reuse source wording or use wording that the text supports. The input text is the complete evidence for selecting the label.

## Requirements

| ID | Narrator shall | From v1 | Verified by |
|---|---|---|---|
| MYC-23.1 <!-- ec72bd17-445f-4c1b-af2a-5302847a6c4d --> | Accept one UTF-8 text and a caller-supplied positive word limit. Use the text as evidence and generate one label that names its main subject, action or outcome. Permit fragments and shorter labels. | New | selected check |
| MYC-23.2 <!-- 12e4fe57-e2fd-4d23-9c2c-27595976d0cb --> | Validate one nonempty label against the word limit before writing it to stdout. Reject invalid input or a reply that fails validation after one format retry, with empty stdout and a short diagnostic. | New | selected check |
| MYC-23.3 <!-- ba7a123a-7e7f-4a4b-8ba0-709931845379 --> | Count label words using the same fixed English function-word exclusions in the model instructions and validation. Require at least one counted word. Preserve excluded words in the returned label. | New | selected check |
| MYC-23.4 | Accept Bash command text in a standalone `bash-label` mode and produce a short action label from static shell tokens. Use a generic shell label for unsupported commands. Leave the source unchanged | Owner direction | Narrator CLI and saved/live Elma shell disclosures |

## Interface

Run `narrator.py label --max-words N --model-command <JSON argv>` and send the text on stdin. The command accepts up to 192,000 input bytes, the existing Narrator input transport limit, and requires nonblank UTF-8 text without NUL. It accepts a raw text block without MYC-8 rendering. Keep the existing Narrator model-command transport and deadline. The adapter receives the label instructions followed by a JSON object containing `text` and `max_words`. Its reply is a JSON object with only `label`, using the existing plain or metered adapter response form.

Normalize whitespace to single spaces. For counting, split on whitespace and ignore surrounding punctuation and case. A token without letters or numbers uses no budget. The excluded English words are `a`, `an`, `and`, `and/or`, `as`, `at`, `but`, `by`, `for`, `from`, `in`, `nor`, `of`, `on`, `or`, `so`, `the`, `to`, `with`, and `yet`. Count a hyphenated term such as `single-checkout` as one word. On success, return a single line with the label and a terminating newline, with exit status zero. Model work for this feature uses the current authenticated Codex subscription when invoked against a hosted model. The model command is explicitly configured by the caller.

## Bash command labels

`narrator.py bash-label` accepts one UTF-8 shell command of up to 8,192 characters on stdin and writes one short action label. The labeler interprets static tokens without launching a shell or model. The same packaged function serves Elma’s collapsed shell calls.
