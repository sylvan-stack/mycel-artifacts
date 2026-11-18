---
role: authored
---
# Mycel · 23 Narrator Label Generation

The owner approved the Label Generation design and asked to proceed on 18 November 2026.

Narrator generates one short label from a single supplied text. Callers can use the label as a Chat Session title or a codename for a block or message. The caller supplies the text and a positive maximum word count. The label names the central subject, action or outcome. Additional words should make that focus more precise. A label may be a single word or a fragment. It may reuse source wording or use wording that the text supports. The input text is the complete evidence for selecting the label.

## Requirements

| ID | Narrator shall | From v1 | Verified by |
|---|---|---|---|
| MYC-23.1 <!-- ec72bd17-445f-4c1b-af2a-5302847a6c4d --> | Accept one UTF-8 text and a caller-supplied positive word limit. Use the text as evidence and generate one label that names its main subject, action or outcome. Permit fragments and shorter labels. | New | selected check |
| MYC-23.2 <!-- 12e4fe57-e2fd-4d23-9c2c-27595976d0cb --> | Validate one nonempty label against the word limit before writing it to stdout. Reject invalid input or a reply that fails validation after one format retry, with empty stdout and a short diagnostic. | New | selected check |

## Interface

Run `narrator.py label --max-words N --model-command <JSON argv>` and send the text on stdin. The command accepts up to 192,000 input bytes, the existing Narrator input transport limit, and requires nonblank UTF-8 text without NUL. It accepts a raw text block without MYC-8 rendering. Keep the existing Narrator model-command transport and deadline. The adapter receives the label instructions followed by a JSON object containing `text` and `max_words`. Its reply is a JSON object with only `label`, using the existing plain or metered adapter response form.

Count whitespace-delimited words and normalize whitespace to single spaces. On success, return a single line with the label and a terminating newline, with exit status zero. Model work for this feature uses the current authenticated Codex subscription when invoked against a hosted model. The model command is explicitly configured by the caller.
