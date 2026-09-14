# SignUpFlow delegated build task

Work only on the explicit versioned item below. Current user scope and the
selected versioned roadmap lane override historical priority text. Run tests
first for implementation changes and keep all review and validation local.
No CI checks or hosted reviewers are used. Ollama is an application voice model
only and must not be used for code review.

Planning and reviewer modes may not commit, push, create or merge a PR.
Reviewer agents never merge. A builder may touch and stage only its declared
owned paths. Completion text is only a hint: the runner also checks the command
exit, guarded calls, owned diff, current local evidence, and GitHub mergeability.

This checked-in excerpt illustrates the policy prefix emitted by `--dry-run`.
The live rendered prompt then includes the complete versioned work-item JSON and
the selected task prompt; paths and acceptance criteria vary by package.
