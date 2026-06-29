# Coronado Fourth of July Week — itinerary site

A little handwritten-style webpage for the annual gathering. You edit one plain-text
file (`itinerary.md`); a script turns it into the webpage; GitHub publishes it
automatically so everyone can open one link.

## Files

| File | What it is | Do you edit it? |
|------|------------|-----------------|
| `itinerary.md` | All the content — days, plans, World Cup matches | **Yes — this is the main one** |
| `template.html` | The design (fonts, colors, layout) | Only for look-and-feel changes |
| `build.py` | Turns the markdown into the webpage | No |
| `.github/workflows/deploy.yml` | Auto-builds and publishes on every push | No |

The finished webpage (`Coronado_July4_2026.html` / `index.html`) is **generated** —
you don't edit it by hand, and you don't need to commit it.

## One-time setup (about 5 minutes)

1. Create a new repository on https://github.com/new (a **public** repo — free GitHub
   Pages needs that; the link is unlisted, but anyone with it can view). Name it
   whatever you like, e.g. `coronado-itinerary`.
2. Add these files to the repo. Easiest no-terminal way:
   - On the repo page, click **Add file → Upload files**, and drag in
     `itinerary.md`, `template.html`, `build.py`, `README.md`, and `.gitignore`.
   - The workflow file lives in a folder, so add it separately: **Add file →
     Create new file**, type `.github/workflows/deploy.yml` as the name (GitHub makes
     the folders for you), paste in the contents of that file, and commit.
3. Turn on Pages: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. That's it. Open the **Actions** tab and watch the first deploy run (~1 minute).
   Your live link will be:

       https://<your-username>.github.io/<repo-name>/

   Share that link with everyone.

## Editing later

Pick whichever is easier:

- **Quick content tweaks, right in the browser:** open `itinerary.md` on GitHub, click
  the pencil ✏️, make changes, and **Commit**. The site rebuilds and updates itself in
  about a minute.
- **Bigger changes / design:** come back to this Cowork chat, have the edits made to
  `itinerary.md` or `template.html`, then upload the updated file(s) to the repo
  (**Add file → Upload files** replaces a file with the same name). The push triggers a
  fresh deploy automatically.

No need to touch `build.py` or the workflow — GitHub runs them for you.

## Editing the content (`itinerary.md`)

- A day starts with `## Weekday, Month Day` — add `| Some Note` for the red tag.
- Schedule lines: `- TIME | Title | optional note`
- Match lines: `- TIME | Country v Country` (flags are added automatically)
- Featured "we're all watching this" match: start with `!` and add `@ where`:
  `- ! 5:00p | USA v Bosnia | @ Mission Beach Watch Party | Leave 3:30p | https://...`
- A guess gets a trailing `?`; a venue placeholder is `Round of 16 · Seattle`.
- Times can be ranges (`9:00–11:00a`), single (`5:00p`), `Late`, or `TBD`.

## Preview on your own computer (optional)

If you have Python 3 installed, run `python3 build.py` in this folder and open the
generated `Coronado_July4_2026.html` in a browser. (No extra packages needed.)
