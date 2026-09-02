# Daily GitHub green squares

One Python script. GitHub Actions runs it every day so the PC can be off.
Use the same script locally only for backfill.

```text
python mmm___forever___pls.py once --push
python mmm___forever___pls.py backfill --days 180 --min 1 --max 3 --push
```

Author email must be listed at https://github.com/settings/emails or the
commit will not attach to your graph.

## Recommended setup (PC does not need to stay on)

1. Create a new **public** repo, not a fork. Default branch `main`.
2. Push this folder.
3. Copy an email from GitHub → Settings → Emails
   (private noreply `ID+USERNAME@users.noreply.github.com` is fine).
4. Repo → Settings → Secrets and variables → Actions
   - Name: `GIT_EMAIL`
   - Value: that email
5. Repo → Settings → Actions → General → Workflow permissions → Read and write.
6. Actions tab → **Daily green square** → Run workflow once.

Confirm the commit shows **your** avatar, not `github-actions[bot]`.
The square can take up to 24 hours.

Cron is `0 12 * * *` UTC (07:00 CDT). GitHub can delay scheduled jobs a bit;
they still land on that UTC calendar day.

## Backfill past days (run once on your machine)

```bash
git clone https://github.com/YOUR_USER/YOUR_REPO.git
cd YOUR_REPO
git config user.name "YOUR_USER"
git config user.email "YOUR_GITHUB_EMAIL"
python mmm___forever___pls.py backfill --days 180 --min 1 --max 3
git log --pretty=fuller | more
python mmm___forever___pls.py once --push
```

`--push` on backfill will send the whole batch in one go after all local
commits are created.

## Optional: Windows Task Scheduler fallback

Only useful if Actions is disabled. The PC must be on at the trigger time.

```powershell
cd C:\path\to\github-daily-green
python mmm___forever___pls.py once --push
```

Task Scheduler → Create Task → Daily → Action: `python.exe` with those args.
This will miss days the machine is asleep.

## Stop

Disable the workflow or delete the repo. Deleting the repo eventually
removes those squares after GitHub rebuilds the graph.
