---
name: allo-av-understanding
description: Use the Allo audio/video understanding HTTP API to submit media files, poll asynchronous jobs, retrieve ASR/OCR timeline evidence, generate summaries, translate extracted evidence, and answer questions grounded in video evidence. Use when the user asks to analyze, summarize, transcribe, OCR, query, or inspect an audio/video file or an existing job_id.
tools: []
version: "1.0.0"
author: lemon7Cy
---

# Allo Audio/Video Understanding

## Purpose

Use this skill to access the Allo audio/video understanding service. The service turns uploaded audio/video into structured evidence before any higher-level reasoning is performed.

The service can provide:

- Media metadata: duration, resolution, codecs, bitrate.
- ASR transcript segments.
- Key frame OCR / screen evidence.
- A unified timeline that aligns transcript, OCR, and frame references.
- LLM summary, chapters, keywords, warnings, and action items.
- Evidence-grounded QA over the processed media.
- Optional translation of extracted evidence.

Default service endpoints:

```text
Base URL: http://221.0.79.252:8090
Demo URL: http://221.0.79.252:8090/demo/
Health:   http://221.0.79.252:8090/health
```

The base URL can be overridden with:

```bash
export AV_UNDERSTANDING_BASE_URL="http://host:port"
```

## When To Use

Use this skill when the user asks to:

- Summarize an audio/video file.
- Transcribe a video or meeting recording.
- Extract OCR / screen text evidence from a video.
- Inspect or continue an existing `job_id`.
- Ask questions about a processed video.
- Produce evidence with timestamps from audio/video content.
- Build an agent capability around the audio/video understanding API.

Do not use this skill for unrelated general QA, pure local ffmpeg tasks, or generic file management.

## Core Rule: This Is An Asynchronous Job API

The upload endpoint does not mean the media has been fully processed. Upload only creates a job and returns a `job_id`.

Always follow this lifecycle:

1. Submit media and save `job_id`.
2. Poll `GET /api/jobs/{job_id}` until `status` is `done` or `failed`.
3. Only after `status=done`, fetch timeline, summary, translation, or QA results.
4. If polling stops before completion (service unreachable or explicit timeout), return the `job_id` and current status to the user. Do not upload the same file again unless the user explicitly asks.

For long videos, expect processing to take time because the backend may run media decoding, ASR, OCR, evidence fusion, and LLM summarization.

## Polling Policy: Wait Until Done, Gate On Service Health

Processing time cannot be predicted reliably. A short video may still take longer than any estimate. Therefore the default polling policy is:

- Keep polling `GET /api/jobs/{job_id}` until `status` is `done` or `failed`. Do not stop just because an estimated wait time passed.
- If a status query fails, check `GET /health`. If the service is alive, keep polling. The job is still progressing on the server.
- Only give up when the service itself stays unreachable for many consecutive checks (default: 36 checks). Even then, the remote job may still be running, so always preserve the `job_id` and resume later.

Duration-based estimates are soft budgets used only as progress signals, never as hard timeouts:

| Media duration | Soft wait budget (informational) |
| --- | ---: |
| < 5 minutes | 600 seconds |
| 5-15 minutes | 1200 seconds |
| 15-30 minutes | 2400 seconds |
| 30-60 minutes | 3600 seconds |
| > 60 minutes | Do not wait in foreground. Submit, return `job_id`, and resume later. |

When a soft budget is exceeded, the script emits a `soft_budget_exceeded` event and continues polling as long as the service is healthy. A video under 5 minutes that finishes at 610 seconds will still return its real result.

## Helper Script

A helper script is included:

```bash
bash scripts/media_understanding.sh health
bash scripts/media_understanding.sh submit /absolute/path/to/video.mp4
bash scripts/media_understanding.sh analyze /absolute/path/to/video.mp4 auto
bash scripts/media_understanding.sh recommend-wait /absolute/path/to/video.mp4
bash scripts/media_understanding.sh job JOB_ID
bash scripts/media_understanding.sh poll JOB_ID 5 forever
bash scripts/media_understanding.sh wait JOB_ID forever 5
bash scripts/media_understanding.sh timeline JOB_ID
bash scripts/media_understanding.sh summary JOB_ID
bash scripts/media_understanding.sh translation JOB_ID zh-CN
bash scripts/media_understanding.sh qa JOB_ID "What is this video mainly about?" 5
bash scripts/media_understanding.sh video-url JOB_ID
```

Environment variables used by the script:

```text
AV_UNDERSTANDING_BASE_URL                default: http://221.0.79.252:8090
AV_UNDERSTANDING_POLL_INTERVAL           default: 5 seconds
AV_UNDERSTANDING_MAX_WAIT_SECONDS        default: forever (poll until done/failed while service is healthy; set a number for a hard timeout)
AV_UNDERSTANDING_MAX_UNREACHABLE_CHECKS  default: 36 consecutive failed liveness checks before giving up
```

## API Contract

### Health Check

```bash
curl -sS "$AV_UNDERSTANDING_BASE_URL/health"
```

Expected response:

```json
{"status":"ok"}
```

### Submit Media

```bash
curl -sS -X POST "$AV_UNDERSTANDING_BASE_URL/api/videos" \
  -F "file=@/absolute/path/to/media.mp4"
```

Important response fields:

- `job_id`
- `status`
- `filename`
- `message`
- `error`

### Query Job Status

```bash
curl -sS "$AV_UNDERSTANDING_BASE_URL/api/jobs/JOB_ID"
```

Important fields:

- `job_id`
- `status`: typically `queued`, `processing`, `done`, or `failed`
- `message`
- `error`
- `filename`
- `metadata_path`
- `timeline_path`
- `created_at`
- `updated_at`

### Poll Job Until Ready

Use the helper script instead of writing ad hoc polling logic:

```bash
bash scripts/media_understanding.sh poll JOB_ID 5 forever
```

This emits JSON-line progress events such as:

```json
{"event":"poll","elapsed_seconds":10,"job_id":"...","status":"processing","message":"...","error":""}
{"event":"soft_budget_exceeded","elapsed_seconds":620,"soft_budget_seconds":600,"job_id":"...","note":"recommended wait budget exceeded; service is still processing, continuing to poll"}
{"event":"service_unreachable","elapsed_seconds":700,"job_id":"...","consecutive_bad_checks":3,"max_bad_checks":36}
```

Exit behavior:

- exit `0`: job finished with `status=done`
- exit `2`: job failed
- exit `3`: hard wait timeout (only when a numeric max_wait was given); the remote job may still be running
- exit `4`: service stayed unreachable for too many consecutive checks; the remote job may still be running
- exit `5`: service is healthy but job status could not be read (likely an invalid `job_id`)

On exit `3` or `4`, preserve the `job_id` and resume later with `wait JOB_ID forever 5`.

### Fetch Timeline Evidence

```bash
curl -sS "$AV_UNDERSTANDING_BASE_URL/api/jobs/JOB_ID/timeline"
```

Important fields:

- `metadata`
- `transcript`
- `timeline`
- frame paths / frame URLs
- OCR text when available

Typical timeline items contain:

- `start`
- `end`
- `frame`
- `frame_url`
- `transcript`
- `ocr`

Use timeline evidence for timestamped answers.

### Fetch Summary

```bash
curl -sS "$AV_UNDERSTANDING_BASE_URL/api/jobs/JOB_ID/summary"
```

Force refresh only when necessary:

```bash
curl -sS "$AV_UNDERSTANDING_BASE_URL/api/jobs/JOB_ID/summary?refresh=true"
```

Important fields:

- `source`
- `summary`
- `chapters`
- `keywords`
- `action_items`
- `warnings`
- `generated_at`

### Translate Evidence

```bash
curl -sS "$AV_UNDERSTANDING_BASE_URL/api/jobs/JOB_ID/translation?target_language=zh-CN"
```

Translation may be slow. Only call it when the user explicitly needs translated evidence or a translated view.

### Evidence-Grounded QA

```bash
curl -sS -X POST "$AV_UNDERSTANDING_BASE_URL/api/jobs/JOB_ID/qa" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this video mainly about?","top_k":5}'
```

Important fields:

- `answer`
- `citations`
- `source`
- `warnings`

If QA returns no citations or a weak fallback answer, do not invent evidence. Fall back to summary + timeline + transcript + OCR and clearly state that the QA retrieval did not find direct citations.

### Video Stream And Frames

```text
GET /api/jobs/JOB_ID/video
GET /artifacts/JOB_ID/frames/<frame-file>.jpg
```

These are mainly useful for UI playback and frame preview. Most agent workflows should rely on timeline, summary, and QA endpoints.

## Recommended Workflows

### Workflow A: User Provides A Media File

1. Run health check.
2. Submit the file and capture `job_id`.
3. Poll the job until `done` or `failed`. Do not stop polling just because an estimated time passed; while `/health` is alive, keep waiting.
4. If done, fetch `timeline` and `summary`.
5. If polling had to stop (service unreachable), return the `job_id`, current status, and continuation command.
6. Do not re-upload unless explicitly requested.

Example:

```bash
bash scripts/media_understanding.sh analyze /absolute/path/to/video.mp4 auto
```

With `auto`, the helper script tries to detect media duration with `ffprobe`, uses the duration table as a soft budget, and polls until the job is `done` or `failed` while the service stays healthy. Videos longer than 60 minutes are only submitted; the `job_id` is returned without foreground waiting.

If polling had to stop early, respond with:

```text
The media job has been submitted and is still processing. job_id=JOB_ID. Continue later with: bash scripts/media_understanding.sh wait JOB_ID forever 5
```

### Workflow B: User Provides An Existing job_id

1. Query `job JOB_ID`.
2. If `status=done`, fetch `summary` and `timeline`.
3. If `status=failed`, report the backend error.
4. If still processing, poll if appropriate; otherwise return the current status and ask the user to continue later.

### Workflow C: User Asks A Question About A Processed Video

1. Ensure the job is `done`.
2. Call `qa JOB_ID "question" 5`.
3. If citations are present, answer with citations and timestamps.
4. If QA is weak or empty, use `summary` and `timeline` as fallback evidence.

## Answering Guidelines

Prefer concise outputs with evidence:

1. Short answer or conclusion.
2. Key supporting timestamps.
3. Relevant ASR/OCR evidence.
4. Caveats, especially if QA returned fallback or citations are missing.

When possible, cite time ranges:

```text
At 00:54-01:16, the speaker discusses RAG, Tool, MCP, and Skill as core Agent components.
```

Do not claim that the video was fully analyzed unless `GET /api/jobs/{job_id}` returned `status=done`.

Do not discard a `job_id` after timeout. The `job_id` is the durable handle for resuming the task.

## Failure Handling

- Health check fails: report service unavailable and do not upload.
- Upload fails: report server response and do not retry blindly.
- Polling stopped early (hard timeout or service unreachable): report not-ready state, keep `job_id`, and provide a continuation command (`wait JOB_ID forever 5`).
- Job failed: report backend `error` and `message`.
- Summary/timeline unavailable while job is not done: poll or tell the user the job is still processing.
- QA returns no citations: use summary/timeline fallback and disclose that QA retrieval did not find direct matches.

## Minimal Smoke Test

Use this known job ID only for testing connectivity if still present on the server:

```bash
bash scripts/media_understanding.sh job 7aa8c86b-d887-487d-84d6-387e79368db9
bash scripts/media_understanding.sh summary 7aa8c86b-d887-487d-84d6-387e79368db9
```
