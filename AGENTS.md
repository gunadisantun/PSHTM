# PSHTM Instagram Agent

- This repository is dedicated to PSHTM Instagram automation only.
- Do not add Vercel, Next.js, or unrelated application code.
- Do not use or generate a PSHTM logo in daily posts.
- Use the text identity at the bottom of every post: `Pusat Studi Hukum, Teknologi dan Media` and `IKA FH UNDIP`.
- Always use the official Indonesian term `Pelindungan Data Pribadi (PDP)`. Never write `Perlindungan Data Pribadi` when referring to Indonesia's PDP legal regime.
- Keep official PDP terminology consistent, including `Undang-Undang Pelindungan Data Pribadi`, `Pengendali Data Pribadi`, `Prosesor Data Pribadi`, `Subjek Data Pribadi`, and `Kegagalan Pelindungan Data Pribadi`.
- Default output size is 1080x1350 (4:5).
- Default timezone is Asia/Jakarta.
- Scheduled publishing time is 07:00 WIB.
- Keep Instagram credentials and any AI API credentials in GitHub Actions Secrets only.
- Prefer AI-generated imagery/backgrounds without embedded editorial text. Render headline, body copy, source, handle, and institutional identity deterministically in code so spelling and legal terminology remain accurate.

## Mandatory news verification rules

- Daily-news posts must be genuinely current. The normal freshness window is the previous 24 hours from the scheduled run time.
- Do not treat an old event as new merely because it appears in a newly indexed article, search result, repost, explainer, anniversary story, or retrospective.
- Verify both the article publication/update timestamp and the actual date of the underlying event or regulatory action.
- Prefer primary sources whenever available: regulator, court, government, official company filing/statement, or other authoritative institution.
- For consequential claims, corroborate the primary source with at least one reputable independent news source when reasonably available.
- If no primary source is available, require at least two credible independent sources before publication.
- For legal/regulatory news, verify the procedural status and describe it accurately: proposal, draft, consultation, enacted, effective, investigation, decision, appeal, stayed, overturned, final, or other applicable status.
- Never imply that a proposal or draft is already binding law.
- Verify names, dates, jurisdictions, regulators, monetary amounts, currencies, legal instruments, and material factual claims before generating the post.
- Reject candidates whose publication date, event date, source credibility, or legal status cannot be confidently verified.
- Do not publish recycled news from outside the freshness window merely to fill the daily slot.
- If there is no sufficiently important and verified story within the freshness window, skip the daily news post rather than publish stale or uncertain information.
- Sensitive topics, allegations, politics, criminal matters, litigation, cybersecurity incidents, and data breaches require especially careful sourcing and neutral wording.

- New or sensitive topics should remain in dry-run/review mode until explicitly approved.
