# Security notes — Day 361

## This lab is defensive, and deliberately so

Every check here **describes a configuration and reports a weakness so it can be fixed**. There is no exploit code, nothing probes a running system, and the subject of the review is a fictional `Posture` dataclass rather than any real service.

That framing is the point rather than a disclaimer. A security review is an inspection, not an attack, and the skill being taught is finding your own weaknesses before someone else does.

## What this lab does and does not touch

- **No network.** The subject is a description, not a running system. No test opens a socket.
- **No credentials.** `secrets_in_environment` and friends are booleans on a dataclass. There is no secret anywhere in this lab.
- **No writes outside this directory.** Only `__pycache__/`, `.pytest_cache/` and, if you create it, `.venv/`.
- **No `sudo`, no global installs.**

## Prompt injection: what the checks can and cannot do

`check_untrusted_content_boundary` is the most important check here and also the most limited, and it is worth being precise about why.

A language model receives instructions and data through **one channel**. There is no mechanism in the architecture that distinguishes "this is your instruction" from "this is a document I retrieved". Marking untrusted content with delimiters helps, and it is not a guarantee — a sufficiently persuasive document can still influence behaviour.

Which is why the remediation names the permission model rather than the prompt. The realistic posture is:

- **Assume the model may be persuaded.** Design so that a persuaded model achieves little.
- **Grant the narrowest authority.** An agent that cannot delete cannot be talked into deleting.
- **Require confirmation for consequential actions.** A human in the loop for anything that writes, deletes or spends.
- **Never execute model output.** Sandbox it, or have a person approve it.

Anyone claiming a filter that solves prompt injection is describing a mitigation, not a fix.

## If a secret has been committed

The remediation on `check_secret_handling` says **rotate first**, and the ordering matters. Deleting the file removes it from the working tree and not from history — anyone with the repository, including anyone who cloned or forked it, still has the credential. Rewriting history helps only if you can guarantee every copy is rewritten, which for a public repository you cannot.

So: rotate the credential, then clean up. `gitleaks` and `trufflehog` scan history rather than the current tree, which is the right thing to check.

## What a passing review does and does not mean

Seven checks catch seven classes of failure. A clean report means those seven are addressed. It does not mean the system is secure, and treating it that way is how a review becomes theatre.

The `WEAK` posture exists to make the passing result meaningful. Without evidence that the review **can** fail, a clean report and a review that checks nothing are indistinguishable from outside.

## Reversing everything this lab did

```bash
rm -rf __pycache__ .pytest_cache .venv
```

Nothing else was created, and nothing outside this directory was modified.
