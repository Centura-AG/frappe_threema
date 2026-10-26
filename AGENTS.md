## Customer documentation

Customer docs live in `client_docs/` and follow `CONVENTIONS.md` in Centura-AG/centura_docs. `docs/` is for technical docs only.

- A change to a documented process updates its page in the same PR. The page's `covers` frontmatter lists what it describes; CI fails when a covered item changes and the page does not.
- A new important process gets a page in the same PR. Important means that customers use it regularly or that it changes how they work. Small features, settings and fixes need no page.
- State it in the PR description: "Docs: page added", "Docs: page updated" or "Docs: none needed, because …".
- Screenshots: add an entry to `client_docs/shots.yaml` and run the shots tool. Never take screenshots by hand.
- Write German first. Update `page.en.md` / `page.fr.md` only where they exist.
