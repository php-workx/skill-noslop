# Comprehension pass

Use this pass for multi-paragraph technical reports, analyses, design explanations, incident reviews, and other documents whose meaning depends on project context. Skip it for short messages, simple rewrites, and reference material that is already self-contained.

## Reader baseline

Unless the user identifies a narrower audience, write for a mixed technical audience. The reader understands common software engineering concepts but does not know this project, incident, decision, or earlier discussion.

Do not explain standard concepts merely to sound thorough. Explain project-local terms, acronyms, components, constraints, and decisions that the reader needs to follow the document.

## Build an intent map

Before drafting or rewriting, record a compact private checklist:

- the document's purpose;
- what the reader must understand;
- the main conclusion;
- required concepts and components;
- required causal or logical relationships;
- important constraints and assumptions;
- the expected decision or action, or `none` for an informational document.

This is an intent map, not hidden chain of thought. Do not expose it unless the user asks.

## Default to local reconstruction

After the first complete draft, perform one separate reconstruction using only the finished draft. Ask:

- Can an engineer unfamiliar with this work identify the problem, conclusion, and any requested action?
- Are project-local terms and acronyms explained at first use?
- Are components introduced before their interactions?
- Does the document state causal and logical relationships, or does it expect the reader to infer them?
- Does each important technical detail explain why it matters?
- Can the reader distinguish observed facts, interpretations, assumptions, and recommendations?
- Did shortening remove an explanation needed to understand the result?

This local pass is less independent than a fresh reader. Treat inferred clarity cautiously.

## Use a fresh reader for deep verification

Use one isolated fresh-reader reconstruction instead of the local pass when either condition applies:

- The user requests a deep review, fresh-reader pass, publication-ready verification, or equivalent independent check.
- The user requests an audit of a context-heavy, multi-paragraph document.

An explicit request for a quick pass or no second reader wins and uses the local reconstruction. Do not pause to ask permission. Do not run an isolated reader merely because the runtime supports subagents.

Give the fresh reader only the draft and the audience definition. Do not give it the intent map, prior conversation, intended conclusion, repository access, tools, or external references. The review must reveal what the document communicates by itself.

Ask the reader to return:

1. The main point in one sentence.
2. The problem the document addresses.
3. Important concepts and what they mean.
4. Components or actors and their roles.
5. The sequence of events or causal and logical relationships.
6. Important constraints and assumptions.
7. The requested decision or action, or that none is stated.
8. Missing context, ambiguous references, and unanswered questions that may affect understanding.

For each reconstructed item, require:

- a short quote or location from the draft;
- `high`, `medium`, or `low` confidence;
- `explicit` or `inferred` as the basis.

The reader reports observable understanding. It does not rewrite the document, score its quality, assign severity, demand exhaustive background, or provide hidden reasoning.

## Compare and repair

Compare the reconstruction with the private intent map. The writer, not the reader, classifies each mismatch:

- `blocking`: the reader cannot identify a conclusion, mechanism, or required action that the document intends to communicate;
- `material`: a missing definition, prerequisite, or relationship could cause misunderstanding;
- `optional`: the context might be interesting but is not needed for this document's purpose.

An informational document does not need a requested action. An omitted implementation detail is not a gap unless the intended reader needs it to understand or act.

Repair blocking gaps. Repair material gaps when the supplied material supports the explanation. Usually omit optional context.

Do not invent missing facts or explanations. Ask one precise question when a blocking gap requires information only the author can provide.

Run one repair cycle. A second isolated pass is justified only when the first fresh reader misunderstood the main conclusion, mechanism, or requested action.

## Deliver only the requested document

The intent map and reader reconstruction are internal checks. Return only the requested report or analysis unless the user asks to see the audit.