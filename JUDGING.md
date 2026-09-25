# Judging Strategy

## Assignment Strategy
Judges are assigned tracks based on their expertise. The `judge_tracks` table maps judges to one or multiple tracks. During an active event, a judge is only expected to review projects that fall within their assigned tracks.

## Isolation
Role isolation is our highest priority for judging integrity.
- In `main.py`, the `get_judge_scores` endpoint strictly validates that the requesting user's `session` cookie matches a user with the `judge` role.
- If a judge attempts to query scores for a different `judge_id`, the API returns a `403 Forbidden` response.
- This logic exists exclusively in the backend controller. UI hiding is insufficient; the data is completely inaccessible via curl or browser tools for unauthorized peers.

## Scoring Math
Scores are recorded across multiple criteria (e.g., functionality and quality). Currently, our API returns the raw sum of these metrics, but the schema isolates them so that an organizer could introduce custom weighting per track in the future.

## Normalization Method (Future Work)
Because some judges score harshly and others generously, raw averages can penalize projects reviewed by strict judges.
While we have not implemented the mathematical proof for the Bonus Challenge, our relational model supports calculating a judge's historical average and variance across all their reviews, which can be used to normalize their scores into standard deviations (Z-scores) before final ranking.
