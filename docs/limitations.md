# Honest limits: what this data can't tell you

Every dataset has edges. These are this one's — stated up front so no finding gets over-read.

## 1. A filing is intent, not a hire

One row = one Labor Condition Application filing: a company taking the formal first step to sponsor a foreign worker. It is a solid, paid-for signal of *willingness to sponsor repeatedly*. It is not proof anyone got hired, got a visa, or stayed. Employer rankings in this analysis rank **filing activity**, not headcount.

## 2. No OPT signal

Nothing in this data says anything about OPT hiring — the first rung of the OPT → STEM OPT → H-1B ladder. The analysis reads sponsorship willingness; the entry path before it is invisible here.

## 3. Employer names are messy — counts understate real sponsors

Names are recorded as filed, variants and all. Wayfair appears three ways in this data:

| Recorded name   | Filings |
|-----------------|---------|
| WAYFAIR LLC     | 1,234   |
| Wayfair LLC     | 250     |
| "Wayfair LLC " (trailing space) | 791 |

The top-15 chart uses the single most common spelling per employer, so it *understates* companies with many variants — Wayfair's true total here is 2,275, nearly double its charted bar. I left names as recorded rather than hand-merging them: in this data that's a deep hole (Amazon and Cognizant each appear under a dozen spellings), and a rushed merge risks breaking numbers that otherwise check out.

## 4. One combined file — doubling can't be ruled out

The source is Kaggle's single combined disclosure file (2.82 GB, 96 columns), not five files I stitched together. A genuinely separate filing and a row doubled inside that combined file look identical. The duplicate analysis treats repeats as real filings (one batch repeats 131 times — that's sponsorship behavior, not a data error; 32,867 exact duplicates are kept deliberately), but a small fraction of doubling can't be ruled out. Filing volume is read as a sign of intent, not a literal worker count.

## 5. The years include the pandemic

FY2020–2024 covers COVID-era labor market shocks. The 2021 peak (~30k filings) and the 2020 trough (~21k) partly reflect that context, not just structural sponsorship trends. Year-to-year moves should be read with that in mind; the through-line that matters is the floor — filings never drop below ~21,000 in any year.

## 6. Wage units have typos — means are unreliable here

A few rows have the pay unit recorded wrong (an annual salary tagged "per hour" becomes $407M/year after conversion). Every pay figure in this analysis is a **median**, which those rows can't move. Any reading based on averages from this data is distorted; the overall mean ($169,853) vs median ($108,181) shows how far.

## 7. The STEM split is by construction, not discovery

STEM status and the role groups are both derived from the same occupation codes, so general-business roles *can't* be STEM and analytics roles *have* to be. The 0% / 100% split confirms a known rule (HR, consulting, and management jobs aren't STEM-designated; computing ones are) — it isn't something the data revealed. The volume and pay comparisons are the findings; this one is context.

## 8. The IT-manager exclusion is a judgment call

2,583 Computer and Information Systems Managers were pulled out of the business group because they're an IT occupation inside SOC family 11, and at a $168K median they dragged the group figure up $10K. The rule is title-based and auditable, but a few other IT-adjacent managers may remain in the group. The exclusion is documented in `../src/h1b_ma.py` (`assign_role_groups`) so anyone can re-run it either way.
