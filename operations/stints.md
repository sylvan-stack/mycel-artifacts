---
role: authored
---
# Guide: Stints

A stint is a named set of stop criteria for one run of a long-running
process: how much work the run is asked to do and how much it may spend.
Naming a stint in a request replaces spelling out the limits each time.

This guide is authoritative for the list of stints, how one is written down,
and how to use, add and change them. What each measure counts and what each
kind of limit does is defined by the process that runs the stint. One process
honours stints today: the
[deep pull-request review](pr-deep-review.md#stop-criteria), whose measures
and kinds are in its
[reference](pr-deep-review-reference.md#stop-criteria).

A stint is not a model setting. Which model does the work and how hard it
thinks is a separate choice.

## Using a stint

Name it in the request: “continue the review, `<name>` stint”.

A run takes its stint from the first of these that exists:

1. the stint named in the request;
2. the default stint of the work in hand — for a review, `default_stint` in
   its `state.json`;
3. the default stint named in this guide;
4. none: the run continues until the process says the work is complete.

Then:

- **Limits stated in the request go on top of the stint.** A stated limit
  replaces the stint's limit on the same measure in the same direction —
  maximum or minimum, soft or hard — and every other limit of the stint
  stays. “`<name>` stint, but at most 30 minutes” changes only the soft time
  maximum. A stated limit the stint does not have is added.
- **“No stint”** in a request runs without criteria, whatever the defaults.
- **An unknown name is never guessed.** List the defined stints and ask.
- **A contradiction is reported, not repaired.** If the result has a soft
  maximum above its hard maximum, or a minimum above a maximum of the same
  measure, say so when the run starts; the process's precedence rules decide.
- **The run records what it used.** It states the stint's name and the
  resolved limits in its opening line and stores both with the run, so a
  later change to the stint does not alter what past runs report.

## Defined stints

Default stint: none.

None defined yet.

## Adding or changing a stint

A stint is agreed in conversation before it is written. Numbers chosen
without evidence are worse than no stint, so the agent's part is to
recommend and explain, not to record what it is told. When the user asks for
a new stint or a change to one:

1. **Ask what it is for** when the request does not say: whether the run is
   attended, how long the user will be away, and what must not happen —
   stopping too early, spending too much.
2. **Use only the limits the purpose needs.** Each limit answers one stated
   concern. Add none for completeness.
3. **Recommend a value for each limit and give its basis:** what earlier runs
   recorded as spent (`runs` in the state files), the plan usage the harness
   reports when it reports one, and what the limit would have meant for
   those runs. Say when the basis is one measurement or an estimate.
4. **Say how the limits will behave together:** which one will end a run
   first, any limit that cannot take effect, any two that cannot both hold,
   and anything the purpose depends on that a stint cannot control.
5. **Write it once the user has agreed the table.**
   - Name it in lowercase kebab-case. The name must be new and must not be a
     command word of a process that honours stints, such as `next` or
     `verify`.
   - Turn the agreed wording into kinds with the
     [wording table](pr-deep-review-reference.md#from-the-users-words-to-a-kind).
     A limit given without “soft” or “hard” is soft.
   - Check that every measure is one a process that honours stints defines,
     that no soft maximum is above its hard maximum, and that no minimum is
     above a maximum of the same measure.
   - Add it under *Defined stints* in the form below.
6. **Review it after its first runs.** Compare what those runs spent with the
   stint's limits and propose corrections.

```markdown
### <name>

<When to use it.> Basis: <where the numbers come from>, <date>.

| Measure | Kind | Value |
|---|---|---|
| <measure> | <soft or hard> <minimum or maximum> | <value and unit> |
```

To change a stint, agree the change the same way and edit its table in
place. Runs already recorded keep the limits they ran with. To remove one,
delete its section; a default that still names it is treated as absent, and
the run says so.

To set a default, change the *Default stint* line above for every process, or
`default_stint` in a review's `state.json` for that review only.

Managing stints needs no skill of its own. The request reaches this guide
through the process the stint is for.
