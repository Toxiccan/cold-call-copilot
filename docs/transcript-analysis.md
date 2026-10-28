# Transcript analysis notes

These notes summarize the supplied 100-call bundle for product and prompt decisions. The transcript files remain local and are excluded from Git. This document contains aggregate metadata and paraphrased observations only; it does not include transcript quotes, names, or company details.

## Source outcome labels

The index contains 100 calls. These are the labels recorded by the caller, not verified intent classifications:

| Recorded outcome | Count |
|---|---:|
| `agreed_to_receive_report` | 14 |
| `call_again` | 4 |
| `do_not_call` | 10 |
| `follow_up` | 14 |
| `interested` | 7 |
| `moved_company` | 5 |
| `next_step_agreed` | 11 |
| `not_interested` | 14 |
| `not_logged` | 13 |
| `wrong_person` | 8 |

Recorded durations range from 30 to 687 seconds; the median is 93.5 seconds. That supports keeping live-call guidance concise while allowing for occasional longer conversations.

## Calls recorded as `not_logged`

There are 13 `not_logged` calls. The supplied inference file separately assigns these possible outcomes:

| Inferred outcome | Count |
|---|---:|
| `agreed_to_receive_report` | 7 |
| `follow_up` | 3 |
| `next_step_agreed` | 1 |
| `unknown` | 1 |
| `wrong_person` | 1 |

That file marks 12 inferences high confidence and 1 medium confidence. These remain inferences; the original source label stays `not_logged`. In particular, a missing outcome must not be treated as `not_interested`.

## Prompt decisions

The local review of all 100 call endings surfaced recurring situations: prospects ask for the call's purpose, request written details before deciding, defer because they are busy, route the caller to another contact, describe existing providers or business constraints, or agree to a specific callback or meeting. These observations are qualitative and overlap; they are not frequency estimates.

- Separate a request to receive information from an agreed meeting or scheduled call.
- Separate general interest from explicit agreement to a next step.
- Treat explicit do-not-call requests as a stop signal and honor them.
- Handle busy prospects, callback requests, wrong contacts, referrals, language mismatch, and connection trouble without assuming a sale.
- Use the prospect's own stated need; do not manufacture a problem or business fact.
- Keep intent classification uncertain when the words do not support a clear label.
- Interpret recorded outcome labels separately from what the prospect appears to mean in the conversation.

The backend prompt uses paraphrased patterns and a 12-case synthetic evaluation set informed by these decisions. The evaluation cases are not transcript excerpts. A validated stage-by-stage annotation of all 100 calls and a live Gemini evaluation remain to be completed.
