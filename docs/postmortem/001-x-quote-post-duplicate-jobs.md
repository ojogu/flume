# Postmortem — X quote posts created duplicate jobs and an "API key" error on web

## Incident Summary

| Field | Detail |
|---|---|
| **Date** | 2026-11-07 (first occurrence in logs) to 2026-11-18 (fixed) |
| **Duration** | About 11 days; undetected for roughly 9 of them |
| **Severity** | Medium |
| **Status** | Resolved |

**One-line summary:** Downloading a link to an X quote post that carries a video created an empty parent job plus two identical child jobs, and the web download button then failed with "Missing X-API-Key header". The extra jobs also consumed monthly quota until the user could no longer submit.

---

## Timeline

Times are UTC, taken from the backend and worker logs.

| Time | Event |
|---|---|
| Nov 4, Nov 5, Nov 7 01:43 | Single-video X links download normally (one job, one download task). |
| Nov 7 09:13 | First quote post (`olajiire101`) is submitted. The worker starts two download tasks with IDs that differ from the job's ID. These are child jobs. |
| Nov 7 09:13:45 | `GET /internal/jobs/{parent}/download` fails with "No completed steps found". About one second later `GET /v1/job/{parent}/download` fails with "Missing X-API-Key header". |
| Nov 7 09:15, 09:16 | The same link is submitted twice more, apparently as retries. Each creates another parent and two more children. |
| Nov 7 21:45, Nov 9 18:51 | Two more quote posts (`UnkleAyo`, `Thriving_Faith`) show the same pattern. |
| Nov 10 13:04 | A plain single-video tweet downloads normally. The problem depends on the post, not on a deploy. |
| Nov 16 | Reported by the user. Diagnosed from the logs and from running yt-dlp against the affected posts. |
| Nov 18 10:34–10:38 | Fix deployed (containers recreated; backend and worker run from the bind-mounted source). |
| Nov 18 10:44 | A submit fails with the generic "Something went wrong. Please try again." The request authenticated and then logged nothing. |
| Nov 18 ~10:45 | Cause found: the user's web key counted 20 jobs this month against a limit of 20. Ten of them were playlist children created by this bug. The server had returned an unlogged 429. |
| Nov 18 | Monthly count changed to ignore playlist children. The counted total went from 20 to 10, which unblocked the user. |
| Nov 18 10:51 | The `olajiire101` link was resubmitted: one job, one orchestrator task, one download task (same ID as the job), no errors in the logs. |
| Nov 18 | The user confirmed duplicates are gone and the history folder displays correctly, including for the earlier duplicated jobs. |

---

## Impact

- At least 5 quote-post submissions were affected in the logs (Nov 7 to Nov 9), all from one logged-in web user. One tweet was submitted three times within three minutes.
- Each submission showed three history rows: an empty parent (titled with the raw URL, status "Succeeded" but not downloadable) and two child rows.
- The download button on the result page failed with an API-key message. The video was only retrievable by opening a child row in history.
- **Quota:** the extra jobs consumed 10 of the user's 20 monthly slots. On Nov 18 the user hit the limit and could not submit anything, and the page showed a generic error that did not say why.
- No data loss. Single-video links were unaffected.

---

## Root Cause

1. An X quote post carries two media items: the post's own media and the video being quoted. yt-dlp reports this as a **two-entry playlist**. Entry 1 is the post's own media (created seconds before the post) and entry 2 is the quoted video (created much earlier). This was confirmed visually on two tweets.
2. The playlist fan-out (`_handle_playlist` in `backend/celery_app/orchestrator.py`) was written for real playlists, where each entry has its own URL. X gives **both entries the same URL**, the tweet. Each child therefore got `source_uri = tweet URL`.
3. The download step (`download()` in `backend/src/service/downloader.py`) passed that URL back to yt-dlp, which resolved it as a two-entry playlist again. Neither child knew which entry it owned. Both wrote `input.mp4`, and entry 1 won. This last step is inferred from the code and from both children producing the same video, and was not run.

### Contributing causes

- **A parent with no file looks like a finished job.** It has no download steps, and its status is computed from its children, so it showed "Succeeded". The web UI polled the parent and offered a download that could not work.
- **A wrong-route fallback.** When the logged-in download failed, `web/src/components/web/JobResult.tsx` opened `/v1/job/{id}/download` in a new tab. That route needs an `X-API-Key` header a browser tab cannot send. It hid the real error ("No completed steps found") behind a misleading one.
- **Children counted toward the monthly limit.** `count_jobs_this_month` counted every job, so a quote post used three slots and a playlist uses N+1.
- **The limit error was invisible.** Logged-in submits go through `apiClient`, which throws a different error class from the one the submit handler recognizes, so every server error for a logged-in user became "Something went wrong". The server also returned the 429 without logging anything.
- **No automated tests.** The backend has no test directory, so nothing covered a playlist whose entries share a URL.
- **No detection.** Nothing alerted on a parent job that could not be downloaded.

---

## What Went Well

- The logs had everything needed. Worker task IDs that differed from job IDs exposed the two-children pattern, and the paired "No completed steps" and "Missing X-API-Key header" errors pointed at the exact route.
- The behavior reproduced outside the app with `yt-dlp -J`, which made the entries inspectable.
- Media IDs encode creation time, which separated the post's own media from the quoted video.
- On Nov 18 the silent request pointed straight at the one code path that returns without logging. A read-only query of the user's job count confirmed the limit within minutes.

---

## What Went Wrong

- The problem went unnoticed for about 9 days, and was found by a user rather than by monitoring.
- The "API key" error pointed at auth, not playlists, which made the symptom easy to misread.
- Early diagnosis leaned on reading the code. Several guesses were wrong (including that the second entry was a GIF, and which entry was the quoted video) until the posts were checked by hand.
- The quota side effect was noticed during the investigation but set aside as a separate issue. It then blocked the user a week later. Side effects that consume a user-visible limit should be treated as part of the bug.
- Backend debug logging prints full Google OAuth tokens during login, and the frontend proxy logs the `access-token` in the callback URL. This was noticed while reading logs and is not fixed.

---

## Action Items

| Action | Owner | Priority | Status |
|---|---|---|---|
| Orchestrator: treat a multi-entry result whose entries share one URL as a single job for entry 1 (`backend/celery_app/orchestrator.py`) | Unassigned | High | Done |
| Downloader: pass `playlist_items` and unwrap the playlist so a job fetches exactly one entry (`backend/src/service/downloader.py`) | Unassigned | High | Done |
| Web: remove the `/v1/.../download` fallback and show an error toast (`web/src/components/web/JobResult.tsx`) | Unassigned | High | Done |
| Verify a quote post end to end (one job, one download, no errors) | Unassigned | High | Done (`olajiire101`; user confirmed duplicates are gone) |
| Playlist-as-folder: top-level history listing, child counts, children endpoint, folder page, thumbnails and metadata | Unassigned | Medium | Done (user confirmed the folder displays correctly, including earlier duplicates) |
| Count top-level jobs only in `count_jobs_this_month` | Unassigned | High | Done |
| Convert `apiClient` errors to `ApiError` in `submitJobAuth` so logged-in users see the real message | Unassigned | Medium | Done in code; takes effect with a frontend rebuild |
| Log every monthly-limit rejection | Unassigned | Medium | Done; not yet triggered, so unverified |
| Verify a real YouTube playlist end to end (parent plus one job per video, each downloading its own video) | Unassigned | High | Open |
| Add backend tests for the same-URL and distinct-URL playlist branches and the child-count and top-level queries (needs a test setup first) | Unassigned | Medium | Open |
| Double-submit guard on the web form | Unassigned | Low | Open |
| Alert on parent jobs whose children succeeded but which have no downloadable output | Unassigned | Low | Open |
| Stop logging OAuth tokens in backend debug logs and the `access-token` in the frontend proxy log | Unassigned | High | Open |
| Decide the product rule for genuine multi-video posts with no quote (today they yield entry 1 only) | Unassigned | Low | Open |

---

## Lessons Learned

- An assumption such as "each playlist entry has its own URL" should be checked where it is used, especially when a new platform behavior (here, X quote posts) can break it.
- A fallback that silently takes a different code path can hide the real error. Prefer one clear failure message.
- A job's status should reflect whether it is usable, not only whether its children finished.
- Every rejected request should leave a log line. A silent 429 made a quota problem look like a mystery.
- If a bug creates extra records, check what else counts those records, such as quotas, limits and totals.
- Reproducing with the real tool (yt-dlp) and the real logs answered in minutes what code reading had only guessed at.

---

*Postmortems are blameless. The goal is to understand what happened, not to assign fault. See [README](./readme.md) for the full documentation guide.*
