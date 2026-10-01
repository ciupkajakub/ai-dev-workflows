# Proposal readiness regression case

## Fixed evaluation criteria

Recorded on 2026-10-01 before editing the preparation instructions. Apply the same
criteria to the retained proposal and any candidate. Use `pass`, `fail`, or
`unknown` with a requirement and code/document reference. No average score:
a material failure or unknown prevents a ready verdict. Planned tests are design
evidence, not executed proof.

| ID | Criterion | Evidence needed for pass |
| --- | --- | --- |
| R1 | Requirement fidelity | Every promised behavior has a source; requested outcomes, necessary technical decisions, and agent assumptions are distinguishable. No silent scope expansion or exception to a requirement. |
| R2 | Executable flow | For each affected entry point, follow input → validator and actual rule → result producer → consumer action. Identify when side effects occur. A handler for an error with no producer fails. |
| R3 | Path coverage | Checks set up the condition that causes the real validator to accept/reject and observe the consumer and side effects. Distinct implementations need distinct scenarios; shared check IDs alone do not suffice. |
| R4 | Component and interface changes | Named owners, before/after behavior, added/changed/removed inputs and outputs, their origin and callers. Worker-private helpers need no design. |
| R5 | Presentation consistency | The short approval package covers material R4 changes, matches the plan and scope, and uses clear language. Every optional graph edge agrees with the entry point and side-effect boundary. |

## Reproduction inputs and procedure

The [retained proposal](fixtures/b119-proposal.txt) contains the original request,
FEATURE revision 2, IMPLEMENTATION revision 3, PROGRESS, and final presentation.
The batch snapshots include SHA256 identities. The source transcript is
`/Users/ciupek/.codex/attachments/225dc75d-2430-4ac9-925c-0d20f19f9b2c/Wklejony tekst.txt`.
Application code is read-only at
`/Users/ciupek/Desktop/programowanie/prywatne/smashnego/smashnego-rails`,
HEAD `10a5226206851e98a5360d68efba21188be1be7f`.
Workflow baseline is `2d15588c154573b886378c923cc1883a1cee25fd`, revision 4.1.0,
schema 4. Do not update the application, delete the batch, or run delivery.

For a bounded native reviewer trial, supply only the retained input, application
code access, applicable instructions, candidate preparation procedure, and R1–R5.
Do not supply expected findings or the author's verdict. Ask for evidence per
criterion, including unknowns. Compare the returned findings with the diagnostic
expectations below only after the review. Retain the run identity and outcome.
This tests proposal review on one case, not a fresh Cursor preparation or delivery.

## Diagnosis and expected findings

The installed package was compared read-only with source commit `2d15588c` using
`skills/check_package.py` before the edit: integrity verified, matching local
source HEAD. The source checkout was clean. Application code below was also
compared with its recorded HEAD; local workflow changes are not implementation
of this feature. Locations in this section are relative to the application.

| Evidence | Conclusion | Criterion |
| --- | --- | --- |
| FEATURE AC6 and IMPLEMENTATION T002 promise delivery recovery before SMS. `app/services/orders/checkout.rb:108–117` only selects pickup in `read_only_call`; `app/controllers/public/checkout_phone_proofs_controller.rb:9–14` sends SMS after successful preflight. | Confirmed missing error producer: adding delivery recovery cannot make preflight reject an unavailable delivery window. The proposal is incomplete if it retains that promise. | R2 fail |
| Original request, six behavior items; `app/javascript/controllers/cart/checkout_dom.js:145–153`, `checkout.js:55–61`; `app/services/orders/checkout/delivery_selection.rb:30–40`. | The original request does not demand a new delivery-before-SMS path. Public delivery requires online payment; guest pickup payment uses SMS. Separate these paths before choosing whether to remove an unsupported promise or seek approval for extra behavior. Reusing checkout selection at click time also requires resolving payment/consent rules. | R1 requires reconciliation; R2 incomplete |
| Final Mermaid edge `Zamawiam albo prośba o SMS → Obecny hold przy zapisie → Zamówienie zapisane`. Same controller and checkout code. | Confirmed false edge: a successful SMS request sends a challenge, without a capacity hold or order creation. | R5 fail |
| IMPLEMENTATION T001 adds `cart_recovery[intent]`, `anchor_at`, response `replacement`, and omission semantics. T002 adds `delivery_window_starts_at` to checkout/SMS parameters and changes recovery inputs. Final summary mentions intents and a comparison time but omits the two time parameter names and owning controller/service interfaces. | Confirmed incomplete interface overview. Naming holds and the offer verifier does not cover the material producer/consumer changes already in the plan. The detailed plan does contain useful contract work; it is not merely a file list. | R4 partial; R5 fail |
| V002 names request specs and desired recovery, but no delivery preflight validator or triggering scenario; V004 uses generic delivery/SMS wording. `DeliveryPromises#valid_request?` and `OwnFleet::DeliveryOffer#available?` require nonempty lines, `app/services/delivery_promises.rb:114–116` and `app/services/own_fleet/delivery_offer.rb:91–95`. | Confirmed gap: check labels cannot close the missing SMS chain or prove empty-cart delivery behavior. The pickup empty-cart repair does not establish delivery coverage. Which empty-cart delivery behavior is intended needs resolution without inventing kitchen load or reservation rules. | R3 fail; R1/R2 unresolved for empty delivery cart |
| Final text: “żywość”, “maluje”, “Całe lane ... nie zamykają”. | Replace these with availability validation, list rendering, and the specific checks required to close the batch. | R5 fail |
| PROGRESS records three reviewer rounds and repairs to real issues. The final documents retain the above gaps. | Confirmed: independent review found useful issues but did not establish complete readiness. Actual reviewer prompts/results are absent from the transcript, so their exact reasoning cannot be reconstructed. | Process limitation |
| `tests/validate_blueprint.py` at the source baseline checks fences, local links, and discovery symlinks. | Confirmed: success says nothing about R1–R5 or agent output quality. | Verification limitation |

The instructions already required before/after changes, executable validation
chains, independent review, and readable summaries. Their remaining process gap
was that discovery, task prose, approval prose, and review closure could each be
completed separately: no single component map supplied the summary, no retained
scenario walkthrough demonstrated the error producer at each entry point, and
no final evidence-backed result for all five criteria survived the repair rounds.
These are observed omissions in the instructions and output. They explain how
the old proposal could appear complete; they do not establish the model's hidden
reasoning or prove this is the only cause.

The transcript records reads of the installed skill, entry rules, blueprint, and
relevant checkout code. It does not include all tool outputs or the model's
internal context. “Wrong package”, “lost context”, or “model too weak” are not
confirmed causes. Model configuration, compaction, cost, and elapsed agent work
remain unknown. A package matching today does not prove every instruction was
retained or followed during that earlier run.

## Changed preparation mechanism

The candidate keeps revision 4.1.0, schema 4, and the existing batch sections.
It orders preparation around request provenance, a shared component map,
scenario walkthroughs, checks, and a derived approval draft. R1–R5 results with
references live in PROGRESS; a material failure/unknown prevents readiness.
Repairs update the owning design, affected checks, and summary, then reconcile
all criteria. A reviewer still provides one independent safeguard where warranted;
adding reviewers is not the change. A new session recovers the original request,
revisions, decisions, unresolved results, and next action from durable records.

## Example of a short approval package

This is an illustrative correction based on the inspected code, not a rewritten
B119 batch or a claim that its full plan is ready. In a real prepare run these
changes must first be reconciled into FEATURE/IMPLEMENTATION and reviewed at new
revisions. It deliberately exposes the remaining product boundary instead of
making an implementation-ready claim from a polished summary.

### Przykład dla operatora

B119: FEATURE revision 2, IMPLEMENTATION revision 3. To proponowana korekta
prezentacji; pliki batcha nie zostały zmienione.

Otwarcie „Zmień” pobierze świeże godziny. Klik sprawdzi wybraną godzinę bez
rezerwacji, a po odmowie pokaże modal i zaznaczy najbliższą dostępną. „Zamawiam”
ponownie sprawdzi dostępność. Miejsce zajmie dopiero obecny hold przy zapisie.
Minimum strefy i model rezerwacji zostają.

| Komponent | Dziś → proponowana zmiana i interfejs |
| --- | --- |
| Panele odbioru/dowozu, `CartAvailability`, `Delivery` | Odbiór rozwija HTML, dowóz odświeża wycenę przy adresie. Otwarcie panelu będzie pobierać listę; zwinięty panel jej nie odpytuje. Klik zaczeka na walidację. Przed wyceną zachowamy token i czas wybranego okna, które obecne `Delivery#quote` kasuje. |
| `Public::CartRecoveryController` → `Public::CartRecovery` | Nowe `cart_recovery[intent]`: `select_slot` lub `select_window`; brak pola zachowa obsługę dodania pozycji. Nowe `anchor_at`, czas ISO 8601 z `promised_starts_at` pokazanego okna, pomoże wybrać zastępstwo. Kontroler dopuści i przekaże te pola do serwisu. |
| `Public::PickupSlotState` → `PickupSlotsQuery` | Pusty koszyk odbioru przekażemy jako `cart_items: nil`, aby sprawdzać domyślną pojemność zamiast pustych obciążeń. Pełny koszyk zachowa własne obciążenia. Podpis, lokalizacja, otwarcie i czas slotu nadal podlegają walidacji. |
| Walidacja dowozu w `CartRecovery`, logika `DeliverySelection`, `DeliveryCartQuote` | Dodamy sprawdzenie tokenu bez zakupu. Legacy użyje podpisanego okna i `DeliveryPromises.available?`; flota użyje `DeliveryOffer.verify` oraz `valid?` z liniami koszyka, zaakceptowanym adresem, lokalizacją, czasem i `OfferTravel`. Płatność i zgoda na zakup pozostaną w checkout. Świeża wycena dostarczy zastępstwo; porównanie tokenów z dwóch wycen nie sprawdza dostępności. |
| `Orders::Checkout`, kontrolery zamówienia/SMS, `PickupSlotsRecoveryPayload` | Presenter odbioru dostanie linie koszyka i odrzucony slot. Recovery dowozu po odmowie checkout dostanie nowy `delivery_window_starts_at`, czas z oferty klienta dopuszczony przez `CHECKOUT_ATTRIBUTE_KEYS`. Posłuży tylko do wyboru zastępstwa po wycofaniu transakcji. Wspólna lista parametrów SMS nie dodaje walidacji dowozu. |
| `Pickup#applyRecovery`, `Delivery#applyRecovery`, `Completion`, `cart_owners.js` | Nowe `pickup_slot.replacement` ma token, czas, etykiety, `date` i `day_label`; `delivery.replacement` ma kształt obecnego okna. Częściowa odpowiedź pomija `day_groups`/`windows`. Klient najpierw odświeży otrzymaną listę, potem zaznaczy zastępstwo, także z innego dnia. Późniejsze czyszczenie błędnego wyboru nie skasuje zastępstwa. |

SMS dla odbioru idzie przez `CheckoutPreflight → read_only_call → PickupSelection`.
Po sukcesie wysyła kod, bez zamówienia i holdu. Zapis używa osobnej ścieżki
checkout. Proponuję usunąć obietnicę nowego sprawdzenia dowozu przed SMS:
pierwotne żądanie jej nie zawiera, a obecny dowóz wymaga płatności online.

`intent`, oba parametry czasu i współdzielenie odczytowej walidacji to proponowane
decyzje techniczne. Produktowo trzeba rozstrzygnąć pusty koszyk dowozu: zarówno
legacy, jak i flota wymagają pozycji. Nie zakładam fikcyjnego obciążenia. Kontrakt
musi też rozstrzygnąć brak następcy, błąd sieci i wygaśnięcie oferty. Obecny timer
usuwa wybór przed checkout, więc samo recovery checkout nie spełni obietnicy modalu.
Reguła wyboru najbliższej godziny i remisu pozostaje propozycją agenta.

Sprawdzenia obejmą zapełnienie terminu między wyborem a żądaniem, brak holdu przy
kliknięciu i przed SMS, współbieżny zapis do limitu, osobno odbiór, legacy i flotę,
liczbę żądań przy zamkniętym/otwartym panelu oraz zaznaczenie zastępstwa w
przeglądarce. Test walidacji uruchomi rzeczywistą odmowę; test kontrolera sprawdzi
`replacement` w odpowiedzi. Do tego skupione specy i RuboCop zmienionych plików.
Testy aplikacji nie zostały tu uruchomione.

To pakiet do wskazanych decyzji, nie zgoda na implementację. Po ich rozstrzygnięciu
nowe rewizje muszą przejść R1–R5 i określić zakres wykonania, commitów oraz
push/PR. Obecna praca nie upoważnia do publikacji.

## Native reviewer trial result

One read-only native subagent review ran on 2026-10-01 in this task, identity
`/root/proposal_trial`, with a fresh context and no inherited author conversation.
The prompt supplied the retained input, source prepare skill and blueprint,
application code/HEAD, R1–R5, and read-only limits. It prohibited reading the
maintainer's report or starting more agents. It did not supply expected findings.
The earlier review history embedded in the original PROGRESS remained part of the
historical input; this was not a claim of total blinding to all past findings.
The native model was inherited; no cheaper-worker model selection was tested.

The evaluated instruction and input identities were:

| File | SHA256 |
| --- | --- |
| `feature_execution_blueprint.md` | `74becd7a9efd5f2bc559ae3ec7f1e53266f32f3e0faa24374c0af768b655044f` |
| `skills/workflow-prepare/SKILL.md` | `fdbf0ecc1a1a32e49bd20830f3a796bae169507bda7958ee24351ba10b6604ab` |
| `skills/entry-rules.md` | `9a814cb06f9284df18a577a28ecb83e3d0e3f956bf47c0e2251ba3470d9a0abb` |
| `tests/fixtures/b119-proposal.txt` | `358373817d2369a04dbc627f0ca09aceb4b92535ae461179da6f9bad6c5e3428` |

After the trial, two trailing spaces on the original `/workflow-prepare` line
were removed for `git diff --check`. No requirement or batch document changed.
The committed fixture SHA256 is
`7cf01b3c4f7957e6932a2aa6a772363151f208ffd9dea53a7e94094727a79bcd`;
the table above retains the identity actually supplied to the reviewer.

| Criterion | Reviewer result | Returned evidence |
| --- | --- | --- |
| R1 | fail | Empty delivery cart has no accepting path; preserved offer expiry bypasses the promised modal. |
| R2 | fail | Missing delivery error producer before SMS; `Delivery#quote` clears the token before refresh can validate it. |
| R3 | fail | Empty delivery cart/expiry scenarios are unresolved; V003 expects pickup replacement at service level although T002 builds it in the controller presenter. |
| R4 | fail | Missing changes to the preflight validator and to the responsibilities of `Delivery#quote`. Several other interfaces are already usefully described. |
| R5 | fail | False SMS → hold/order graph edge; checkout time parameter and owners omitted from summary. |

The coordinator checked these additional findings in code:

- `app/services/delivery_promises.rb:114–116` and
  `app/services/own_fleet/delivery_offer.rb:91–95`: both delivery implementations
  need cart lines; the pickup-only empty-cart fix does not solve this.
- `app/javascript/controllers/cart/delivery.js:36–41`: `quote` clears the token
  and windows before requesting a quote. T003 does not specify preserving the
  previously selected window for its promised invalid-selection recovery.
- The same file, `71–75` and `90–91`: expiry clears the token, then payment
  readiness needs that token. The old C7 explicitly preserves this behavior,
  so the intended modal cannot rely only on a later checkout rejection.
- `app/services/orders/checkout.rb:200–202,279–284` and
  `app/controllers/public/orders_controller.rb:100–111`: the checkout service
  returns the pickup error; the controller adds the presenter. V003's service
  assertion and T002's response owner are inconsistent.

The trial independently caught the expected missing validator, graph error,
incomplete interface presentation, and path-coverage defects. The vocabulary
critique was the coordinator's finding, not a separately reported reviewer result.
The reviewer also preserved useful existing decisions: `intent`, omission of
partial catalog fields, pickup empty-cart normalization, signed fleet verification,
cross-day replacement and applying selection after rendering. Rejecting this
proposal did not mean rejecting every technical choice.

This is an actual agent review of an old proposal using candidate instructions.
It is not an agent-generated replacement FEATURE/IMPLEMENTATION, a fresh Cursor
`workflow-prepare` run, a delivery trial, or an A/B comparison. The manual example
above demonstrates the presentation and honest decision boundary only. It does
not pass R1–R5 as a complete executable proposal. No conclusion about success
rate, number of future review rounds, cost, or productivity follows from one
review. The next authorized Cursor preparation must test the whole process on
new revisions; no repeated preparation/delivery loop ran here.

## Repository verification

- `python3 -B tests/validate_blueprint.py`: passed, 10 Markdown documents and
  37 local links, including this report and discovery checks. Historical `.txt` inputs are not
  executable instructions or Markdown quality tests.
- `python3 -B tests/test_check_package.py`: six package-comparison tests passed.
- `git diff --check` and manual diff review: source changes stay in preparation,
  shared entry recovery, and the supporting regression evidence/checks.
- Application code matches HEAD; all 2374 tracked/nonignored untracked file hashes
  match the pre-edit snapshot, confirming read-only use. No application tests,
  installation refresh, feature implementation, push, or PR publication occurred.

These checks verify repository documents and package tooling. The separate native
review above is the only agent behavior trial performed for this change.
