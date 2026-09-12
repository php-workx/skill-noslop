# No Slop

No Slop makes reader-facing prose simple, concise, direct, and understandable without prior project context. It improves both language and explanation while removing conspicuous AI-style rhetoric and em dashes.

The skill preserves supplied facts, numbers, links, citations, uncertainty, necessary context, protected content, and requested output formats. It does not diagnose whether a person used AI.

## What it does

- Drafts reader-facing prose without formulaic filler, false drama, puffery, or generic conclusions.
- Rewrites prose with the minimum effective edit and returns only the requested output.
- Audits visible writing patterns by quoting the text, naming the pattern, and suggesting a repair.
- Makes technical reports understandable to engineers who know common software concepts but not the specific project, incident, or decision.
- Identifies missing definitions, prerequisites, relationships, significance, and requested actions before polishing the wording.
- Replaces em dashes in editable prose with punctuation or clearer sentence structure.
- Keeps code, commands, identifiers, literal quotations, legal or policy text, and marked protected spans unchanged.

For complex reports and analyses, No Slop uses one fresh-reader reconstruction when the runtime supports isolated subagents. The reader sees only the draft and audience definition, then reports what it understood and which context is missing. When subagents are unavailable, the skill applies the same reconstruction checklist locally. The intent map and review remain internal unless requested.

## Tested runtimes

| Runtime | Tested version | Installation |
| --- | --- | --- |
| Codex CLI | `0.150.1` | Standalone skill |
| Claude Code | `2.1.251` | Session-local plugin or standalone skill |

## Claude Code: session-local plugin

Claude loads this plugin for the current session only. From the clone root, start Claude with:

```sh
claude --plugin-dir /absolute/path/to/clone/plugins/no-slop
```

In that fresh session, invoke:

```text
/no-slop:no-slop Rewrite this release note in plain language.
```

`--plugin-dir` does not persist the plugin installation. Use the standalone installation below when you want the skill available across sessions.

## Standalone installation

The canonical standalone source is:

```text
/absolute/path/to/clone/plugins/no-slop/skills/no-slop
```

Copy that directory to one target for the agent you use:

```sh
cp -R /absolute/path/to/clone/plugins/no-slop/skills/no-slop ~/.agents/skills/no-slop
cp -R /absolute/path/to/clone/plugins/no-slop/skills/no-slop ~/.codex/skills/no-slop
cp -R /absolute/path/to/clone/plugins/no-slop/skills/no-slop ~/.claude/skills/no-slop
```

Restart the agent after installation.

In a new Codex thread, invoke `$no-slop`. In Claude Code, invoke `/no-slop:no-slop`.

## Modes

| Mode | Use | Result |
| --- | --- | --- |
| Draft | Ask for reader-facing prose. | Applies the language, context, and explanation rules while drafting. |
| Rewrite | Ask to simplify, clarify, or remove AI-style language. | Returns understandable revised content in the requested format. |
| Audit | Ask to audit, scan, or flag a draft. | Quotes style and comprehension findings without rewriting or accusing the author of using AI. |

Use explicit invocation when the guarantee matters. Implicit activation is best effort and intentionally does not apply to code-only tasks or terse factual answers.

## Local-only package

No Slop is locally installable. It has no runtime service dependency, API key, telemetry, remote marketplace, hook, or automated user-file rewrite.

## License

[MIT](LICENSE)
