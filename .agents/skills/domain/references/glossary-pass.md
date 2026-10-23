# The extraction pass

The active discipline applied to a conversation in one go, rather than term by term.

## Process

1. **Scan the conversation** for domain-relevant nouns, verbs and concepts.
2. **Identify problems**:
   - The same word used for different concepts (ambiguity)
   - Different words used for the same concept (synonyms)
   - Vague or overloaded terms
3. **Propose a canonical glossary** with opinionated term choices.
4. **Write to `GLOSSARY.md`** in the working directory, using the format in `glossary-format.md`.
5. **Output a summary** inline in the conversation.

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others as aliases to avoid.
- **Flag conflicts explicitly.** If a term is used ambiguously in the conversation, call it out in a "Flagged ambiguities" section with a clear recommendation.
- **Only include terms relevant for domain experts.** Skip the names of modules or classes unless they have meaning in the domain language.
- **Keep definitions tight.** One sentence max. Define what it IS, not what it does.
- **Show relationships.** Use bold term names and express cardinality where obvious.
- **Only include domain terms.** Skip generic programming concepts (array, function, endpoint) unless they have domain-specific meaning.
- **Group terms into multiple tables** when natural clusters emerge (for example by subdomain, lifecycle or actor). Each group gets its own heading and table. If all terms belong to a single cohesive domain, one table is fine: don't force groupings.
- **Write an example dialogue.** A short conversation (3-5 exchanges) between a developer and a domain expert that demonstrates how the terms interact naturally. The dialogue should clarify boundaries between related concepts and show terms being used precisely.

## Relationships

- An **Invoice** belongs to exactly one **Customer**
- An **Order** produces one or more **Invoices**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
>
> **Domain expert:** "No: an **Invoice** is only generated once a **Fulfilment** is confirmed. A single **Order** can produce multiple **Invoices** if items ship in separate **Shipments**."
>
> **Dev:** "So if a **Shipment** is cancelled before dispatch, no **Invoice** exists for it?"
>
> **Domain expert:** "Exactly. The **Invoice** lifecycle is tied to the **Fulfilment**, not the **Order**."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User**. These are distinct concepts: a **Customer** places orders, while a **User** is an authentication identity that may or may not represent a **Customer**.

## Re-running

When the pass runs again on the same conversation or a later one:

1. Read the existing `GLOSSARY.md`.
2. Incorporate any new terms from the subsequent discussion.
3. Update definitions where understanding has evolved.
4. Re-flag any new ambiguities.
5. Rewrite the example dialogue to include the new terms.
