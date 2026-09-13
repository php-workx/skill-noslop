# No Slop

No Slop makes reader-facing prose simple, concise, direct, and understandable without prior project context. It improves both language and explanation while removing conspicuous AI-style rhetoric and em dashes.

The skill preserves supplied facts, numbers, links, citations, uncertainty, necessary context, protected content, and requested output formats. It does not diagnose whether a person used AI.

## Why

LLMs often produce polished writing that is harder to understand than it needs to be. Reports and analyses may use complicated language, hide the main point, or assume the reader knows the project and earlier discussion.

Editing can create a second problem: it may flatten the vocabulary, cadence, humor, uncertainty, and useful edge that make the writing sound like its author.

No Slop makes the language simpler while preserving meaning and voice. For technical reports, it also checks whether a mixed engineering audience has enough context to understand the concepts, relationships, and requested action.

## Quick install

Install No Slop globally with the Skills CLI:

```sh
npx skills add php-workx/skill-noslop --skill no-slop --global --yes
```

The CLI installs the skill in your user scope and links compatible detected agents to it. Restart the agent after installation.

To target one agent explicitly:

```sh
npx skills add php-workx/skill-noslop --skill no-slop --global --agent claude-code --yes
npx skills add php-workx/skill-noslop --skill no-slop --global --agent codex --yes
```

You can also ask a coding agent:

```text
Install the no-slop skill globally from https://github.com/php-workx/skill-noslop
```

## Use

Claude Code with the standalone skill:

```text
/no-slop Rewrite this incident report in plain language for engineers who do not know the project.
```

Codex:

```text
$no-slop Rewrite this analysis. Preserve the technical details, but explain the missing context.
```

Audit without rewriting:

```text
Use no-slop to audit this report for formulaic language and missing explanatory context.
```

Request an isolated fresh-reader check:

```text
Use no-slop to deep-review this design proposal for readers unfamiliar with the system.
```

## What it does

- Drafts reader-facing prose without formulaic filler, false drama, puffery, or generic conclusions.
- Rewrites prose with the minimum effective edit and returns only the requested output.
- Audits visible writing patterns by quoting the text, naming the pattern, and suggesting a repair.
- Makes technical reports understandable to engineers who know common software concepts but not the specific project, incident, or decision.
- Identifies missing definitions, prerequisites, relationships, significance, and requested actions before polishing the wording.
- Replaces em dashes in editable prose with punctuation or clearer sentence structure.
- Keeps code, commands, identifiers, literal quotations, legal or policy text, and marked protected spans unchanged.

For complex reports and analyses, No Slop runs a local comprehension reconstruction by default. A complex audit or an explicit request for a deep review, fresh-reader pass, or publication-ready verification uses one isolated reader when the runtime supports subagents. Say `quick` or `no second reader` to keep the local check. The intent map and review remain internal unless requested.

## Common patterns

No Slop checks these patterns in context rather than deleting them mechanically:

- Empty contrast such as “not X, but Y”
- Throat-clearing before the real point
- Fake insight or reveal language
- Unsupported importance claims and generic praise
- Vague authority such as “experts agree”
- Superficial analysis that names no mechanism or consequence
- Repetitive sentence shapes and dramatic fragments
- Synonym cycling that makes terminology less consistent
- Generic recap endings
- Missing actors, definitions, prerequisites, relationships, or significance

## Skill installation versus plugin installation

| | Standalone skill with `npx skills` | Native plugin |
| --- | --- | --- |
| Installs | `SKILL.md` and its reference files | A runtime-specific package that may contain skills, commands, agents, hooks, MCP servers, LSP servers, settings, or executables |
| Scope | Works across supported agents and can be installed globally or per project | Installed and managed by one agent runtime |
| Invocation | Uses the agent's normal skill name, such as `/no-slop` or `$no-slop` | Claude namespaces the skill, such as `/no-slop:no-slop` |
| Updates | `npx skills update --global` | The runtime's plugin manager and plugin version |
| Best use | Simple installation of portable instructions | Distribution of several runtime features as one versioned package |

No Slop currently ships one skill and no hooks, MCP servers, or background services. The standalone `npx` installation provides the same writing behavior and is the recommended option.

For Codex, use the standalone `npx` installation. This repository includes Codex package metadata for distribution tooling, but it does not publish a Codex marketplace installation.

## Claude Code: session-local plugin

The repository also contains a Claude plugin manifest for local testing and plugin-based distribution. Clone the repository and start Claude from the clone root:

```sh
claude --plugin-dir /absolute/path/to/clone/plugins/no-slop
```

Invoke the namespaced plugin skill:

```text
/no-slop:no-slop Rewrite this release note in plain language.
```

`--plugin-dir` loads the plugin for that session. It does not persist the installation.

## Manual standalone installation

The standalone skill directory is:

```text
/absolute/path/to/clone/plugins/no-slop/skills/no-slop
```

Copy it to the directory used by your agent:

```sh
cp -R /absolute/path/to/clone/plugins/no-slop/skills/no-slop ~/.agents/skills/no-slop
cp -R /absolute/path/to/clone/plugins/no-slop/skills/no-slop ~/.codex/skills/no-slop
cp -R /absolute/path/to/clone/plugins/no-slop/skills/no-slop ~/.claude/skills/no-slop
```

## Tested runtimes

| Runtime | Tested version | Recommended installation |
| --- | --- | --- |
| Codex CLI | `0.150.1` | Global standalone skill |
| Claude Code | `2.1.251` | Global standalone skill |

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
