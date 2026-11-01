"""Build the rewritten English edition.

Outputs: en/essentials.html (the book: intro + 14 chapters, chapters 4+ behind the shared unlock),
en/failure-museum.html, en/recipes.html, en/challenge.html.
Written natively for a global reader (not a translation) in the author's first-person voice.
Run: python scripts/build_english_edition.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://aiaijungle.github.io/vibe-ebook/en/'
E = html.escape
V = '?v=4'

NAV = [('essentials.html', 'Essentials'), ('recipes.html', 'Recipes'), ('failure-museum.html', 'Failure museum'),
       ('challenge.html', '30-day challenge'), ('sales.html', 'All volumes')]

CSS = """*{box-sizing:border-box}body{margin:0;background:#f7f6f2;color:#24303a;font:18px/1.8 Georgia,'Iowan Old Style','Times New Roman',serif;overflow-wrap:anywhere}
header,main,footer{max-width:760px;margin:auto;padding:20px 16px}a{color:#97472e;text-underline-offset:3px}
.top{display:flex;flex-wrap:wrap;gap:4px 16px;font:15px/1.6 system-ui,sans-serif}.top a{display:inline-flex;align-items:center;min-height:44px}.top a[aria-current]{font-weight:800;color:#24303a;text-decoration:none}
h1{font:800 clamp(30px,6vw,46px)/1.2 system-ui,sans-serif;letter-spacing:-.03em;margin:18px 0 12px}h2{font:800 clamp(24px,4.5vw,32px)/1.3 system-ui,sans-serif;letter-spacing:-.02em;margin:56px 0 8px}
h3{font:700 20px/1.4 system-ui,sans-serif;margin:30px 0 6px}.lead{font-size:20px;color:#3b4852}.kicker{font:800 12px/1.4 system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:#97472e;margin:48px 0 0}
.build{font:15px/1.7 system-ui,sans-serif;background:#fff;border:1px solid #dce2e5;border-left:4px solid #97472e;border-radius:10px;padding:12px 16px;margin:12px 0 20px}
.done{font:15px/1.7 system-ui,sans-serif;background:#eef3f1;border-radius:10px;padding:12px 16px;margin:20px 0}.done ol{margin:4px 0 0;padding-left:22px}
blockquote{margin:18px 0;padding:6px 18px;border-left:3px solid #c9b8ad;color:#3b4852;font-style:italic}pre{white-space:pre-wrap;background:#1f2933;color:#f5f7f8;border-radius:10px;padding:14px;font:14px/1.6 ui-monospace,Menlo,Consolas,monospace;overflow-x:auto}
.toc{font:15px/1.7 system-ui,sans-serif;background:#fff;border:1px solid #dce2e5;border-radius:14px;padding:12px 20px}.toc ol{padding-left:22px;margin:6px 0}.toc li{margin:2px 0}
.note{font:14px/1.6 system-ui,sans-serif;color:#53616d}.lock{font:16px/1.7 system-ui,sans-serif;background:#24303a;color:#fff;border-radius:16px;padding:26px;margin:48px 0}.lock a{color:#ffd9c7}
.lock input{width:100%;max-width:340px;min-height:44px;padding:8px 12px;border-radius:8px;border:0;font:16px system-ui;margin:8px 0}.lock button{min-height:44px;padding:8px 18px;border-radius:8px;border:0;background:#ffd9c7;color:#24303a;font:700 16px system-ui;cursor:pointer}
html:not(.paywall-unlocked) .locked{display:none!important}html.paywall-unlocked .lock{display:none}
footer{font:14px/1.6 system-ui,sans-serif;color:#53616d;border-top:1px solid #dce2e5;margin-top:48px}.aib-lab{font-family:system-ui,-apple-system,sans-serif}"""


def lab(sec_id, kind, title, minutes, goal, intro, data, kicker='Try it now'):
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    return (f'<section class="aib-lab" data-lab="{kind}" id="{sec_id}" aria-labelledby="{sec_id}-t">'
            f'<p class="lab-kicker">{E(kicker)}</p><h2 id="{sec_id}-t" style="margin-top:0">{E(title)}</h2>'
            f'<p class="lab-meta"><span>⏱ {minutes} min</span><span>🎯 {E(goal)}</span></p><p>{E(intro)}</p>'
            f'<div class="lab-mount"></div><script type="application/json" class="lab-data">{blob}</script></section>')


def O(label, best, why):
    return {'label': label, 'best': best, 'why': why}


def F(key, label, example, hint=None):
    f = {'key': key, 'label': label, 'example': example, 'placeholder': 'e.g. ' + example[:44]}
    if hint:
        f['hint'] = hint
    return f


def builder(fields, footer=None):
    d = {'fields': fields, 'checks': [{'key': f['key'], 'min': 4, 'ok': f['label'].split(' — ')[0] + ' filled', 'todo': 'Fill ' + f['label'].split(' — ')[0].lower()} for f in fields]}
    if footer:
        d['footer'] = footer
    return d


def unlock_script():
    """Reuse the site-wide unlock (same hashes, same storage key) from the English volume 1 head."""
    t = (ROOT / 'en/book1.html').read_text(encoding='utf-8')
    m = re.search(r'<script>\s*window\.__sha256=.*?</script>', t, re.S)
    s = m.group(0)
    s = s.replace("alert('비밀번호 입력 폼을 찾을 수 없습니다.')", "alert('Unlock form not found.')")
    s = s.replace("alert('비밀번호를 입력해주세요.')", "alert('Please enter your access code.')")
    s = re.sub(r"alert\('비밀번호가 올바르지 않습니다\.[^']*'\)", "alert('That code did not work. Check the code from your purchase email.')", s)
    assert not re.search(r'[가-힣]', s), 'untranslated text in unlock script'
    return s


def page(name, title, desc, h1, lead, body, head_extra=''):
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == name else ""}>{E(t)}</a>' for h, t in NAV)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{SITE}{name}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="https://aiaijungle.github.io/vibe-ebook/assets/og-1200x630.png">
{head_extra}<style>{CSS}</style>
<link rel="stylesheet" href="../assets/interactive-labs-20261101.css{V}"><script src="../assets/interactive-labs-20261101.js{V}" defer></script>
</head><body><header><nav class="top" aria-label="Main">{nav}</nav></header><main>
<h1>{E(h1)}</h1><p class="lead">{E(lead)}</p>
{body}
</main><footer><p>The AI Bible · By Limitlessman · Exercises run in your browser; nothing you type is stored or sent. Models and prices change, so check each provider's official page before you rely on a number.</p></footer></body></html>
"""


# ============================================================ THE BOOK
CHAPTERS = []


def ch(cid, part, title, build, paras, lab_html='', done=()):
    CHAPTERS.append(dict(id=cid, part=part, title=title, build=build, paras=paras, lab=lab_html, done=done))


INTRO = [
    "I am not a developer. I ran an IT business for ten years without being able to read a single line of Python. Every time I needed something built, I wrote a brief, paid an agency, waited, and got something close to what I asked for, but never quite it.",
    "Then I spent four days with an AI coding assistant and built the first working version of a B2B platform myself. Ninety-six hours. It was ugly. It broke constantly. It was mine.",
    "That is the story people like to hear. Here is the part they skip: the next seventy-two days were a log of failures. A deployment that exploded because my code pointed at a folder on my own laptop. A bot that burned through $47 of API credit in three hours. A web page that turned into garbled characters overnight. A YouTube description with hidden text that tried to make my bot run commands I never gave it.",
    "This book is built from both halves. The win shows you what is possible. The failures show you what to do on Monday morning so you get the win without the damage.",
    "<strong>How to read it.</strong> Every chapter ends with something you build: a checked post, a small web tool, an agent design, a verified code change, a one-line operating rule for your team. Each chapter has a short exercise you can do right here in the page. No account, no API key. If a chapter does not leave you with something you made, it has not done its job.",
    "<strong>One rule runs through all of it.</strong> AI does the work. A human checks the facts, approves anything that leaves the building, and owns the result. Everything else is detail.",
]

# ---- Part 1
ch('ch1', 'Part 1 · Instruct', 'Tell AI exactly what you want: the CIF rule',
   'A three-line instruction you can reuse for any writing task.',
   ["Most people start with: <em>make me a blog automation</em>. The AI makes something. It is not what they wanted. That is not the AI being stupid. It cannot read your mind. It only processes what you say, and when you are vague it fills the gaps with guesses.",
    "So I never give an instruction without three things. Context, Intent, Format. CIF.",
    "<strong>C — Context.</strong> What is the situation? <em>I run a small flower shop. 1,200 Instagram followers. This week's new item is a mini bouquet at $15.</em><br><strong>I — Intent.</strong> What do I want? <em>Three versions of a post introducing it.</em><br><strong>F — Format.</strong> What should come back? <em>Under 150 characters each, five hashtags, a different first line for each version.</em>",
    "Three lines. The AI stops guessing and starts working. Compare that with <em>write a post about my bouquet</em>, which leaves every decision to the machine.",
    "Then I add two lines that save me later. <strong>Don't:</strong> do not change the price, do not invent stock levels or discounts, mark anything you are unsure of as [check]. <strong>Check:</strong> the price is still $15, no made-up address.",
    "That is the whole trick. It feels too simple to be the first chapter of a book. It is the reason the rest of the book works."],
   lab('lab-cif', 'builder', 'CIF instruction builder', 5, 'Build a reusable instruction',
       'Fill the five boxes for a real task of yours. Press "Fill with example" first if you want to see the shape.',
       builder([F('c', 'C (Context) — the situation', 'I run a small flower shop. 1,200 Instagram followers. New item this week: mini bouquet, $15.'),
                F('i', 'I (Intent) — what you want', 'Three versions of a post introducing the new item.'),
                F('f', 'F (Format) — what comes back', 'Under 150 characters each, five hashtags, a different opening line for each.'),
                F('ban', "Don't — what the AI must not do", 'Do not change the price or invent stock, discounts or an address. Mark unknowns as [check].'),
                F('chk', 'Check — what you will verify', 'Price is $15. No invented location. Hashtags are relevant.')],
               '## If information is missing\nDo not guess. Mark it [check] and list it at the end.')),
   ['Your instruction has all three CIF lines.', 'It says what the AI must not invent.', 'You saved it somewhere you can reuse it tomorrow.'])

ch('ch2', 'Part 1 · Instruct', 'Finish one post: draft, check, publish',
   'One published post plus a fact-check table you will reuse.',
   ["I don't write my blog anymore. A bot pulls the day's keywords, the AI writes a draft, and it gets published. That sentence used to end with <em>and you do nothing</em>. It doesn't anymore. The bot writes. I check the facts. That is the deal.",
    "Here is why. AI writes smoothly, and smooth writing is dangerous. When the source leaves a gap, the AI fills it with what similar posts usually say. A class becomes a pottery class. A fee that includes materials becomes a fee plus materials. An event with no seat count suddenly has <em>only 2 seats left!</em>",
    "The errors come in three kinds, and once you know them you can catch almost all of them in a minute:",
    "<ul><li><strong>Reversed</strong> — the source says one thing, the draft says the opposite (materials included → materials extra).</li><li><strong>Invented</strong> — something plausible that is not in the source (what you'll make, when you'll get it).</li><li><strong>Pressure</strong> — urgency or proof with no basis (only 2 left, 98% loved it).</li></ul>",
    "So before anything goes out, I fill one small table. Item, source value, draft value, match, action. Dates and weekdays. Prices and what's included. Place and parking. How to sign up. Anything the source does not say gets deleted, not softened.",
    "The first time takes ten minutes. By the fifth post it takes two. That table is worth more than any prompt trick in this book."],
   lab('lab-spot', 'spot', 'Find the sentences that are wrong', 3, 'Catch every mismatch',
       'Read the source, then tap every sentence in the AI draft that does not match it.',
       {'source': 'Riverside Studio one-day class · Saturday, November 15, 2–4 pm · $45, materials included · 6 seats · Sign up through the form on our website · No parking on site (use the public lot)',
        'question': 'Tap each sentence in the AI draft that does not match the source.',
        'segments': [
            {'text': '🌿 Join Riverside Studio on Saturday, November 15 from 2 to 4 pm.', 'wrong': False, 'why': 'Date, weekday and time match.'},
            {'text': 'You will make your own ceramic mug in two hours.', 'wrong': True, 'why': 'The source never says what you make. The AI filled the gap.'},
            {'text': 'The class costs $45, with materials charged separately.', 'wrong': True, 'why': 'The source says materials are included. Reversed.'},
            {'text': 'There are 6 seats in total.', 'wrong': False, 'why': 'Matches.'},
            {'text': 'Only 2 seats left, so book now!', 'wrong': True, 'why': 'No seat count in the source. Invented pressure.'},
            {'text': 'Sign up through the form on our website.', 'wrong': False, 'why': 'Matches.'},
            {'text': 'Free parking is available right outside the studio.', 'wrong': True, 'why': 'The source says no parking. A customer would be stuck.'},
            {'text': 'Your finished piece will be ready to collect two weeks later.', 'wrong': True, 'why': 'A promise the source never made.'}],
        'takeaway': 'Reversed (materials, parking), invented (mug, pickup), pressure (seats left). Build your fact-check table around those three.'}),
   ['You fact-checked one real draft against its source.', 'You deleted at least one thing the source did not say.', 'You timed it.'])

ch('ch3', 'Part 1 · Instruct', 'Change the channel, keep the facts',
   'The same announcement for blog, Instagram and text message, with identical facts.',
   ["Once you have one checked post, the temptation is to spread it everywhere. Blog, Instagram, newsletter, text message, a short video script. AI makes that easy. It also makes it easy to quietly change the facts on the way.",
    "The shorter the channel, the more gets cut. And the AI cuts the wrong things. It keeps the adjectives and drops the conditions. <em>10% off until November 30, online store only</em> becomes <em>10% off now!</em> in a text message. Then people walk into a shop that never had the discount.",
    "My rule: when you shorten, cut decoration, never conditions. Dates, prices, deadlines, where to buy. Those survive every channel.",
    "The second thing that happens is invention. Turn a blog post into a video script and the AI adds <em>98% of buyers loved it</em> because video scripts usually have a line like that. If it is not in the source, it goes.",
    "When I have ten minutes, I don't polish sentences. I lay the three versions side by side and compare the facts. Style can be fixed later. A wrong date reaches a customer immediately."],
   lab('lab-channels', 'choice', 'Three moments that go wrong', 3, 'Three channel decisions',
       'These are the moments where facts change between channels.',
       {'steps': [
           {'context': 'Blog: "10% off until November 30, online store only." Shortened for text message: "10% off right now!"', 'q': 'Send it?', 'options': [
               O('Yes, texts need to be short', False, 'Without the deadline and the store, people will ask for the discount in places that never offered it.'),
               O('Add the deadline and the store, cut an adjective instead', True, 'When you shorten, cut decoration, not conditions.')]},
           {'context': 'The video script now says "98% of buyers loved it." That number is not in the source.', 'q': 'What do you do?', 'options': [
               O('Keep it, video needs energy', False, 'An unsupported number is a false claim on any channel.'),
               O('Delete it. If you have real reviews, cite them separately', True, 'Numbers that are not in the source come out.')]},
           {'context': 'All three versions are done. You have ten minutes.', 'q': 'What do you check first?', 'options': [
               O('Whether the sentences read well', False, 'Style can wait. A wrong fact reaches the customer.'),
               O('That dates, prices, conditions and links match the source in all three', True, 'Facts first, wording second.')]}],
        'results': [{'min': 3, 'title': 'Channel-safe', 'text': 'You keep conditions when you cut.'}, {'min': 0, 'title': 'One more pass', 'text': 'Reread the reasons for the ones you missed.'}],
        'takeaway': 'Tone and length change by channel. The facts you promised do not.'}),
   ['You produced at least two channel versions from one source.', 'Dates, prices and conditions are identical across them.', 'Nothing was added that the source does not say.'])

# ---- Part 2
ch('ch4', 'Part 2 · Build', 'Install things in this order and nothing else',
   'A working setup: editor, Python, a project folder with its own environment, and an AI assistant that can see it.',
   ["Setting up is the part that makes non-developers quit. It is also about seventy percent of the effort this part of the book asks of you. Get through it once and the rest is conversation.",
    "Do it in this order. Do not skip ahead, do not install extra tools because a video said so.",
    "<ol><li><strong>An editor.</strong> VS Code. Free, standard, and every AI tool plugs into it.</li><li><strong>Python</strong> from the official site. On Windows, tick <em>Add Python to PATH</em>. This one checkbox causes more first-day failures than anything else.</li><li><strong>A project folder</strong> for one thing only. Not your Desktop, not a synced cloud folder (you will see why in Chapter 14).</li><li><strong>A virtual environment</strong> inside that folder. It keeps this project's packages from fighting with the next one's.</li><li><strong>A secrets file</strong> (.env) for API keys, and a .gitignore that lists it, before you ever paste a key anywhere.</li><li><strong>The AI assistant</strong> — Claude Code, or the assistant built into your editor — opened inside that folder.</li></ol>",
    "If the installer stops halfway, do not turn the computer off. Copy the exact message and give it to the AI with the question: <em>what does this mean and what is the single next step?</em> One step at a time.",
    "You are done when you can open the folder, type <code>python --version</code> and see a number, and ask the assistant to describe the folder it is looking at."],
   lab('lab-setup', 'steps', 'Setup checklist', 30, 'A working setup, checked off',
       'Tick each step as you finish it. Your progress is remembered on this device.',
       {'persist': 'en-setup', 'steps': [
           {'title': 'VS Code installed and opens'}, {'title': 'Python installed (Windows: "Add to PATH" ticked)', 'code': 'python --version'},
           {'title': 'One project folder created outside synced cloud folders'},
           {'title': 'Virtual environment created and activated', 'code': 'python -m venv .venv\n# Windows: .venv\\Scripts\\activate\n# Mac/Linux: source .venv/bin/activate'},
           {'title': '.env created and listed in .gitignore before any key is pasted', 'code': 'echo .env >> .gitignore'},
           {'title': 'AI assistant opened in the folder and asked: "Describe this folder in three lines. Do not change anything."'}],
        'done': 'Setup done. This was the hardest part.', 'next': 'Chapter 5: build your first tool.'}),
   ['python --version prints a number.', '.env is listed in .gitignore.', 'The assistant can describe your folder.'])

ch('ch5', 'Part 2 · Build', 'Your first tool, live on the internet',
   'A one-file web tool, deployed to a public address, checked before and after.',
   ["My first real build was a landing page. One file. I described it the way I would describe it to a designer and let the AI write the code.",
    "Start smaller than you think. One HTML file, no frameworks, no server. <em>A page where I type three tasks for today and tick them off.</em> Describe what is on the screen, who uses it, what must not happen (no data sent anywhere), and how you will know it works (open it on a phone, nothing scrolls sideways).",
    "Open the file in your browser. Then change one thing with a narrow instruction: <em>change only the button label in index.html, touch nothing else.</em> That narrow sentence is the habit that keeps everything you build later from collapsing.",
    "Free static hosting will put this on a real address in minutes. And this is where my first deployment exploded. On my laptop everything worked. On the server: <code>ImportError: No module named 'blog_modules'</code>. My code was pointing at a folder on my own computer. The server had never heard of it.",
    "So before you press deploy, run the checklist below. Every line of it comes from a real failure of mine."],
   lab('lab-deploy', 'steps', 'Six checks before you deploy', 10, 'Six failures prevented',
       'Tick each one before you publish.',
       {'persist': 'en-deploy', 'steps': [
           {'title': 'Secret files (.env) are in .gitignore', 'detail': 'If git status lists .env, it is not protected.'},
           {'title': 'No paths from your own computer (C:/Users/..., /Users/...) in the code', 'detail': 'The server does not have your folders. This was my first deployment failure.'},
           {'title': 'Every package the code needs is listed (requirements.txt or package.json)'},
           {'title': 'You cloned the project into a fresh folder and ran it again', 'detail': 'The surest way to find files that only exist on your machine.'},
           {'title': 'If it calls a paid API: a spending cap and an alert are set'},
           {'title': 'After deploy, you used the main feature on the live address', 'detail': 'A green "deployed" badge is not the same as working.'}],
        'done': 'Ready to publish.', 'next': 'If something breaks, go to Chapter 6.'}),
   ['The tool opens in a browser.', 'You made one change with a narrow instruction.', 'You passed all six checks before going live.'])

ch('ch6', 'Part 2 · Build', 'An error is a diagnosis, not a disaster',
   'A routine for any error: read it, narrow it, fix only that, re-run.',
   ["The red text will come. For a non-developer it feels like the computer is broken. It isn't. An error message is the most precise description of the problem you will ever get, written by the machine itself.",
    "Read it from the bottom up. The last line names what happened (<code>ModuleNotFoundError</code>, <code>AuthenticationError</code>). The lines above say where: which file, which line.",
    "Then suspect the environment before the code. Which folder did you run it from? Which virtual environment is active? Your laptop or the server? Most of my errors were not bugs. They were me running the right code in the wrong place.",
    "When you hand it to the AI, give it four things: the full error (never trimmed), the command you ran, where you ran it, and the one thing you changed just before. Then narrow the fix: <em>change only this function, do not touch other files.</em> Afterwards run the exact same command again. If you can't reproduce the success, you haven't fixed it.",
    "And one rule with no exceptions: API keys never go into the chat. To check a key, check whether it is loaded (yes or no), not what it is."],
   lab('lab-errors', 'choice', 'Error first aid', 4, 'The safest first move for four real errors',
       'Pick the first thing you would do.',
       {'steps': [
           {'context': "ModuleNotFoundError: No module named 'requests'", 'q': 'First move?', 'options': [
               O('Delete the import requests line', False, 'The error goes away and so does the feature that needed it.'),
               O('Check the virtual environment is active, then install requests into it', True, 'Installed-in-the-wrong-environment is the most common cause.'),
               O('Reinstall Python', False, 'Far bigger than the problem, and it can break other projects.')]},
           {'context': 'AuthenticationError: 401 — invalid x-api-key', 'q': 'Safest first move?', 'options': [
               O('Paste the key into the code to test quickly', False, 'Keys in code get saved, shared and uploaded. Someone else then spends your money.'),
               O('Show the key to the AI and ask what is wrong', False, 'Secrets do not go into chats either.'),
               O('Check only whether the key is loaded (yes/no), then the .env location and variable name', True, 'Most 401s are a key that was never loaded, a misspelled variable, or a revoked key.')]},
           {'context': 'IndentationError: unexpected indent (line 42)', 'q': 'How do you instruct the fix?', 'options': [
               O('"Rewrite the whole file from scratch"', False, 'Everything that worked gets rewritten too, with new bugs.'),
               O('Give the full error and lines around 42: "Normalize indentation to 4 spaces in this function only"', True, 'Clear cause, narrow scope. Re-run the same command afterwards.')]},
           {'context': "On the server only: ImportError: cannot import name 'load_config' from 'utils'", 'q': 'Works locally, fails live. Check first?', 'options': [
               O('Redeploy until it works', False, 'Same cause, same error.'),
               O('Whether the code depends on files or paths that exist only on your machine', True, 'The classic local-only failure. It was exactly my first deployment crash.')]}],
        'results': [{'min': 4, 'title': 'First aid certified', 'text': 'You narrow the cause, limit the change and protect secrets.'},
                    {'min': 2, 'title': 'Solid basics', 'text': 'The misses were probably the wide-scope options. Reread those reasons.'},
                    {'min': 0, 'title': 'Start with reading order', 'text': 'Last line, then file and line, then the environment.'}],
        'takeaway': 'Copy the full error, read the last line, suspect the environment, fix narrowly, re-run the same command.'}),
   ['You can name the error type from its last line.', 'Your fix instruction names one file or function.', 'You re-ran the same command to confirm.'])

ch('ch7', 'Part 2 · Build', 'File control and the power of a three-line log',
   'Version control you actually use, and a daily log that makes the next error take minutes.',
   ["Let an AI build for long enough without control and you get a folder nobody can read, including the AI. Files named final_v2_real_final. A feature that worked on Tuesday and nobody knows what changed on Wednesday.",
    "Two habits fix this.",
    "<strong>First, save versions.</strong> Use git, even alone, even for a one-file tool. Before a change, commit. After the AI says <em>done</em>, look at what actually changed (<code>git diff</code>). If it touched three files when you asked for one, undo the two you didn't ask for.",
    "When something that worked breaks and you have spent thirty minutes asking the AI to fix it, stop. Every attempt moves you further from the working version. Go back to the last good commit and try the small change again. Reverting is usually faster than repairing.",
    "<strong>Second, keep a log.</strong> A file called devlog.md. Every day, three lines: what I finished, where I got stuck, what's next. It takes a minute. A month later it is the difference between solving an error in five minutes and solving it for the second time from scratch.",
    "The appendix of the Korean edition prints my entire bug log, date by date. It is the most-read section of the book. Not because it's flattering. Because it's useful."],
   lab('lab-files', 'choice', 'Protect what already works', 3, 'Three file-control decisions',
       'File control usually breaks on a single sentence.',
       {'steps': [
           {'q': 'You want to change only the login button color. How do you ask?', 'options': [
               O('"Make the design nicer"', False, 'The AI decides the scope. Other screens change.'),
               O('"In login.html change only the login button background to #2563eb. Touch no other files or elements."', True, 'File, element, value and limits are all there.')]},
           {'q': 'The AI says "done", but three files changed.', 'options': [
               O('The screen looks fine, move on', False, 'Invisible changes cause tomorrow\'s bug.'),
               O('Read the diff and revert changes you did not ask for', True, 'Reading the diff is where file control starts.')]},
           {'q': 'The payment button stopped working after an edit. You have been fixing it with the AI for 30 minutes.', 'options': [
               O('Keep asking for fixes', False, 'Each fix drifts further from the working state.'),
               O('Return to the last good commit, then retry only the intended change', True, 'Reverting is often faster than repairing.')]}],
        'results': [{'min': 3, 'title': 'In control', 'text': 'Narrow asks, read diffs, revert when needed.'}, {'min': 0, 'title': 'One more pass', 'text': 'Reread the reasons for the ones you missed.'}],
        'takeaway': 'Ask small, read what changed, revert when it breaks.'}),
   ['Your project is under git.', 'You have read at least one diff before accepting a change.', 'devlog.md has today\'s three lines.'])

# ---- Part 3
ch('ch8', 'Part 3 · Delegate', 'A bot follows steps. An agent decides the next one.',
   'A clear picture of the think → act → observe loop, and when an agent should stop.',
   ["A bot does the same steps every time: fetch these feeds, summarize, save. An agent is different. You give it a goal and some tools, and it decides what to do next based on what it just saw.",
    "The pattern behind most agents is called ReAct: <strong>Thought</strong> (what do I need?), <strong>Action</strong> (call a tool), <strong>Observation</strong> (what came back?), and around again until the goal is met. Think of a detective: a hunch, a question to a witness, an answer, a new hunch.",
    "Three things decide whether an agent is useful or dangerous. When it does not know something and has a tool, it must use the tool instead of guessing. When it has enough, it must stop; calling the same tool five more times is how loops eat budgets. When a tool fails, it must say so, never invent the answer it couldn't fetch.",
    "Before you build an agent at all, try one well-written instruction. If a single call can do the job, you don't need an agent. Add tools, memory and multiple agents only when you can name the problem each one solves. More agents is not more intelligence. It's more ways to fail."],
   lab('lab-react', 'choice', 'Run one ReAct loop yourself', 3, 'Choose think, act and observe',
       'You are an agent asked: "Should I take an umbrella in London tomorrow?" Pick the next move.',
       {'steps': [
           {'context': 'Thought: I need tomorrow\'s London weather. Available tool: get_weather(city, date)', 'q': 'Next action?', 'options': [
               O('Answer from training data: "Probably dry"', False, 'The model does not know tomorrow\'s weather. With a tool available, guessing is fabrication.'),
               O('Call get_weather("London", "tomorrow")', True, 'Missing information means observe with a tool.')]},
           {'context': 'Observation: 70% chance of rain from 3 pm', 'q': 'Then?', 'options': [
               O('Call the same tool five more times to be sure', False, 'Same answer, more cost. This is how loops start.'),
               O('Stop and answer: "Rain likely from 3 pm (70%). Take one."', True, 'Enough evidence: stop, and give the reason.')]},
           {'context': 'Observation: get_weather error — timeout', 'q': 'The tool failed. Now?', 'options': [
               O('Say "No rain expected"', False, 'Presenting the unobserved as fact is the worst failure an agent can have.'),
               O('Retry a fixed number of times, then say it could not check', True, 'A retry limit and an honest failure are the basics.')]}],
        'results': [{'min': 3, 'title': 'Loop understood', 'text': 'Observe when you don\'t know, stop when you do, admit failure.'}, {'min': 0, 'title': 'One more pass', 'text': 'Reread the reasons.'}],
        'takeaway': 'Don\'t invent what a tool can observe. Stop when you have enough. Never hide a failure.'}),
   ['You can explain Thought, Action and Observation with your own example.', 'Your design says when the agent stops.', 'Your design says what happens when a tool fails.'])

ch('ch9', 'Part 3 · Delegate', 'Memory and the approval button',
   'A decision for every action your agent can take: automatic, approved, or human-only.',
   ["An agent that can act will eventually act wrongly. The question is not how to make it perfect. It is where you put the button that a human has to press.",
    "There is a real case that made this concrete for me: a support bot replied <em>full refund completed</em> to a customer when the policy said no refund. The promise went out. The company ended up in a dispute. One sentence, sent automatically.",
    "I use three questions. <strong>Does it leave the building?</strong> (Does a customer or outside service see it?) <strong>Can it be undone?</strong> <strong>Is there money, a promise or personal data involved?</strong> Three no's: automatic. Any yes: a human approves. Money and legal promises: a human decides, and the agent only drafts.",
    "Memory follows similar logic. What was said in this conversation lives in the context. Small state that must survive a restart (the last item processed, a setting) goes in a file. Many records you need to query exactly (orders, invoices) belong in a database. And finding <em>similar</em> things (past answers to similar complaints) is what vector search is for. Don't reach for the fanciest one. Reach for the one that matches the question you need to answer."],
   lab('lab-approval', 'sort', 'Automatic, approved, or human-only?', 4, 'Sort seven actions',
       'Assign each action, then compare with the recommendation.',
       {'levels': [{'id': 'auto', 'label': 'Automatic', 'desc': 'Stays inside, can be undone'},
                   {'id': 'approve', 'label': 'Human approves', 'desc': 'Leaves the building or hard to undo'},
                   {'id': 'human', 'label': 'Human only', 'desc': 'Money, legal promises, duplicate risk; agent drafts'}],
        'question': 'Choose a level for each action.',
        'items': [
            {'text': 'Summarize ten news items into my notes', 'answer': 'auto', 'why': 'Only my notes change, and I can delete it.'},
            {'text': 'Save a blog draft into a "for review" folder', 'answer': 'auto', 'why': 'Not public yet, and review is still ahead.'},
            {'text': 'Retry a failed read-only API call up to 3 times', 'answer': 'auto', 'why': 'A read with a cap. No runaway cost.'},
            {'text': 'Email 120 customers about a price change', 'answer': 'approve', 'why': 'Outside, irreversible, and bulk.'},
            {'text': 'Post on the company social account', 'answer': 'approve', 'why': 'Once posted, it is the company speaking.'},
            {'text': 'Reply "refund completed" to a refund request', 'answer': 'human', 'why': 'Money and policy. Wrong promises like this have led to real disputes.'},
            {'text': 'Re-send a payment after the response timed out', 'answer': 'human', 'why': 'It may already have gone through. Check the result first; a human decides.'}],
        'takeaway': 'Does it leave? Can it be undone? Money or promises? Those three answers place the approval button.'}),
   ['Every action in your design has a level.', 'Nothing involving money is automatic.', 'Retries check the previous result before resending.'])

ch('ch10', 'Part 3 · Delegate', 'Limits before power: how not to wake up to a bill',
   'Spending caps, call limits and a model choice you can defend.',
   ["My first automated collector ran a loop during testing. Three hours later it had spent $47. Nothing was wrong with the idea. Everything was wrong with the absence of a limit.",
    "Automation automates spending too. So the first code you write is not the clever part. It is the brake: a maximum number of calls per run, a monthly cap and an alert in the provider's console, and a rule that the agent stops and reports instead of retrying forever.",
    "Then choose models by the cost of being wrong, not by habit. Small, fast models are built for sorting, extracting and short replies at volume. Mid-size models handle most writing and code. The largest models earn their price on hard design problems where a mistake is expensive to undo. In late 2026 the gap between tiers is large: the smallest current Claude model costs a small fraction of the largest per token. Prices move, so check the official pricing page, but the principle doesn't.",
    "Two habits save more than switching models. Cache the parts of your prompt that repeat (instructions that are the same on every call), and ask for shorter outputs. Most bills are long answers nobody needed."],
   lab('lab-models', 'sort', 'Which model tier for which job?', 4, 'Place six tasks',
       'There is no single right answer, but you should be able to say why.',
       {'levels': [{'id': 'small', 'label': 'Small, fast model', 'desc': 'Sorting, extraction, short replies, volume'},
                   {'id': 'mid', 'label': 'Mid-size model', 'desc': 'Most writing, code and analysis'},
                   {'id': 'large', 'label': 'Largest model', 'desc': 'Hard calls that are expensive to get wrong'}],
        'question': 'Choose a tier for each task.',
        'items': [
            {'text': 'Tag 1,000 support emails as shipping / refund / other', 'answer': 'small', 'why': 'Fixed categories at volume. Unit price matters.'},
            {'text': 'Filter spam comments', 'answer': 'small', 'why': 'Short, repetitive judgments.'},
            {'text': 'Write ten blog drafts', 'answer': 'mid', 'why': 'Needs quality, not the top model every time.'},
            {'text': 'Find a bug and write the fix', 'answer': 'mid', 'why': 'Most coding is fine at mid-size. Escalate if stuck.'},
            {'text': 'Plan a structural change across many files', 'answer': 'large', 'why': 'A wrong plan is expensive to reverse.'},
            {'text': 'Compare contract terms and flag risks (a human decides)', 'answer': 'large', 'why': 'One missed clause is costly. The decision stays human.'}],
        'takeaway': 'Cache and shorten before upgrading. Pick the tier by the cost of being wrong.'}),
   ['A spending cap and alert are set.', 'Your code has a maximum number of calls.', 'You can justify the model tier for each task.'])

ch('ch11', 'Part 3 · Delegate', 'Claude Code: plan, change, prove it',
   'One change made with an AI coding agent, with a plan you approved and proof it works.',
   ["A chat assistant answers questions. A coding agent like Claude Code works inside your project: it reads files, runs commands and edits code. That power is exactly why the order matters.",
    "The order is <strong>explore → plan → change → commit</strong>. Ask it to read the project and explain it without changing anything. Ask for a plan. Read the plan and narrow it if it touches files you didn't mention. Approve. Let it change. Then ask for proof: run the tests, show the output as is.",
    "\"Done, all tests should pass\" is not proof. <em>Should</em> is not a result. If the project has no tests, make the first step agreeing on how you will verify the change, before anyone edits anything.",
    "Write the rules down once in a file called CLAUDE.md at the project root: what the project is, how to run it, the working rules, what must never be touched, what done means. It is read at the start of every session. It is guidance, not a lock. Things that must never happen (deleting files, touching secrets) belong in permission settings or hooks, which actually block.",
    "The mistakes I see most: starting a new task in a stuffed conversation (clear it), letting the agent loop on the same fix (stop it, ask for a summary of what was tried), keys committed \"just for a test\" (move them to .env, revoke the old key), and trusting a confident claim about a library (check the official docs)."],
   lab('lab-task', 'builder', 'Task instruction builder', 5, 'A ready-to-paste instruction',
       'Fill five boxes. Paste the result into your coding agent.',
       builder([F('goal', 'Goal — what should be different', 'On a failed login, show "Please check your password" under the field instead of a blank screen.'),
                F('scope', 'Scope — files it may change', 'src/login.js, src/login.css'),
                F('deny', "Off limits — what it must not touch", '.env and src/payment/. Do not install new packages.'),
                F('first', 'First — before editing', 'Read the related files and show the cause and a 3-line plan. Do not edit until I approve.'),
                F('done', 'Done — how we verify', 'Run npm test and show the output. Explain how to check the message appears with a wrong password.')],
               '## Report\nList files changed and paste the verification output as is. If something could not be verified, say so.')),
   ['You approved a plan before any edit.', 'You saw real test output, not a promise.', 'Your CLAUDE.md exists and says what must not be touched.'])

# ---- Part 4
ch('ch12', 'Part 4 · Make it a rule', "Don't be your company's single point of failure",
   'A recovery routine for automations that stop at night.',
   ["If your automation only runs while your laptop is open, it's not automation. If work only starts when you hand it out, you are the single point of failure. Close the laptop, go on holiday, get sick, and everything stops.",
    "Two pieces fix the first problem. A process manager (I use PM2) restarts a program when it dies. A scheduler (cron) starts work at fixed times. Put them on a small cloud server and the system no longer depends on your machine being awake.",
    "The second problem is subtler. In my company, a handful of scheduled workers create the day's first tasks on their own every morning, without anyone asking. Small things: a summary to review, a follow-up to draft. The point isn't the tasks. It's that the system stops waiting for me.",
    "But the goal of 24/7 is not \"never crashes\". It's \"when it crashes, it comes back, and a human finds out\". A restart nobody hears about hides the next failure. So every automatic recovery sends a short message. And every incident gets a three-line entry: cause, fix, how we confirmed it."],
   lab('lab-night', 'choice', 'The bot stopped at night', 3, 'Three recovery decisions',
       'In the morning the overnight report is missing.',
       {'steps': [
           {'q': 'What do you look at first?', 'options': [
               O('Start editing the code', False, 'Fixing without knowing the cause breaks something else.'),
               O('Process status and the last error in the logs (e.g. pm2 status, pm2 logs)', True, 'Is it alive? When and why did it die?')]},
           {'q': 'It died at 2 am from running out of memory and never restarted.', 'options': [
               O('Restart it by hand every morning', False, 'Now you are the single point of failure.'),
               O('Auto-restart plus a memory-limit restart, with an alert when it happens', True, 'It revives itself, and a human knows it did.')]},
           {'q': 'It is fixed. What do you leave behind?', 'options': [
               O('Nothing, it works', False, 'Next time you start the search from zero.'),
               O('Cause, fix and how you verified it, in the decision log', True, 'With records, the next incident takes minutes.')]}],
        'results': [{'min': 3, 'title': 'Operator mindset', 'text': 'Check, auto-recover, alert, record.'}, {'min': 0, 'title': 'One more pass', 'text': 'Reread the reasons.'}],
        'takeaway': 'Always-on means it comes back when it dies, and a human knows.'}),
   ['Your automation runs without your laptop.', 'A restart sends you a message.', 'Incidents have a three-line record.'])

ch('ch13', 'Part 4 · Make it a rule', 'L0 to L4: how much power to give AI, written down',
   'The first line of your team\'s AI operating table, and one decision log entry.',
   ["Give AI too little power and it's useless. Give it too much and you get incidents. The answer is not a feeling. It's a table everyone can read.",
    "I use five levels. <strong>L0</strong> read and search, freely. <strong>L1</strong> fixed routine work, within a count limit. <strong>L2</strong> anything written to the outside, after a person clicks approve. <strong>L3</strong> bulk sends, payments and permission changes, after a deliberate second confirmation. <strong>L4</strong> human only: policies, legal promises, and the AI's own rules. The AI may suggest; it never executes.",
    "Levels are not about how smart the model is. They are about how far a mistake spreads. A wrong summary in my notes spreads nowhere. A wrong email to every customer spreads everywhere.",
    "For each task, write one line: task, owner, approver, level, limit, where it's recorded, when it stops, when we review it. Review monthly. A month without incidents: move it down one level. An incident: move it up immediately.",
    "And keep a decision log. What we decided, why (with the numbers and where they came from), what we rejected and why, who decided and who executes, when we'll look again, and what would make us reverse it. It feels bureaucratic for a week. After that it is the company's memory."],
   lab('lab-levels', 'sort', 'Place seven tasks on L0–L4', 5, 'Seven tasks, five levels',
       'Choose a level for each, then compare.',
       {'levels': [{'id': 'L0', 'label': 'L0 Read', 'desc': 'read and search, free'}, {'id': 'L1', 'label': 'L1 Routine', 'desc': 'fixed repeat work, capped'},
                   {'id': 'L2', 'label': 'L2 One click', 'desc': 'writes to the outside, a person approves'},
                   {'id': 'L3', 'label': 'L3 Confirm', 'desc': 'bulk, payments, permissions; second confirmation'},
                   {'id': 'L4', 'label': 'L4 Human only', 'desc': 'AI suggests, people execute'}],
        'question': 'Choose a level for each task.',
        'items': [
            {'text': 'Find last week\'s decisions in the meeting notes', 'answer': 'L0', 'why': 'Read and summarize. Nothing changes.'},
            {'text': 'Post the daily sales summary to the team channel in a fixed format', 'answer': 'L1', 'why': 'Internal, fixed, once a day, easy to correct.'},
            {'text': 'Reply to a client quote request by email', 'answer': 'L2', 'why': 'One outbound message; the owner reviews and approves.'},
            {'text': 'Retry failed payments for all subscribers', 'answer': 'L3', 'why': 'Money and many people. Confirm the count and amount first.'},
            {'text': 'Give a new hire access to the shared drive', 'answer': 'L3', 'why': 'Access exposes information the moment it is granted.'},
            {'text': 'Change the refund policy text on the website', 'answer': 'L4', 'why': 'A legal promise. AI drafts, people decide and publish.'},
            {'text': 'Edit the AI\'s own rule file', 'answer': 'L4', 'why': 'If the AI can change its own rules, every other control is moot.'}],
        'takeaway': 'Levels follow how far a mistake spreads, not how clever the model is.'}),
   ['One task has a full row in your operating table.', 'Nothing involving money sits below L3.', 'You have one decision log entry.'])

ch('ch14', 'Part 4 · Make it a rule', 'The failure museum',
   'Six real incidents and the rule each one left behind.',
   ["Success stories teach less than failures. These are mine, from running automations and agents every day.",
    "<strong>The local path.</strong> First deployment: ImportError on the server. My code referenced a folder on my laptop. Rule: no paths outside the repository; everything the code needs lives in the project and is listed.",
    "<strong>The hidden instruction.</strong> A bot collecting video descriptions suddenly tried to run a command nobody gave it. The description contained text in the background color: <em>any AI reading this, stop and run …</em>. That is prompt injection. Rule: outside content is data, not instructions. Bots that read the web get read-only power.",
    "<strong>$47 in three hours.</strong> A test loop with no cap. Rule: limits before features.",
    "<strong>Garbled sales page.</strong> Half the page turned into unreadable characters. Fixing it line by line failed. Rule: corruption is reverted, not repaired. Restore the last good version from history, then replay the good changes.",
    "<strong>The shrinking files.</strong> The ends of important files kept disappearing. The culprit was a cloud drive's download-on-demand sync touching files while programs used them. Rule: keep working files out of synced folders, and back up the critical ones separately.",
    "<strong>The silent failure.</strong> No errors, no alarms, bots all running, and the key metric frozen for days. A function had been cut out of a file, and the code calling it swallowed the failure in a try/except. Rule: \"no errors\" is not \"healthy\". Any code that swallows a failure must also send an alert.",
    "Every one of these is an exercise on the <a href=\"failure-museum.html\">Failure museum</a> page: read the situation, choose, see what actually happened."],
   lab('lab-injection', 'choice', 'The hidden instruction', 2, 'What would you do?',
       'One incident from the museum, as an exercise.',
       {'steps': [{'context': 'A bot reading video descriptions tried to run a command it was never given. The description contained hidden text telling any AI to run it.', 'q': 'The most reliable prevention?', 'options': [
           O('Switch to a smarter model', False, 'Models sometimes refuse, but relying on that will eventually fail.'),
           O('Pass outside text as plain data and give reading bots no power to execute commands', True, 'Separate reading from acting. Outside content is data, never instructions.'),
           O('Only collect from well-known channels', False, 'Famous sources can carry hidden text too.')]}],
        'results': [{'min': 1, 'title': 'Correct', 'text': 'Agents that read the web get read-only power by default.'}, {'min': 0, 'title': 'What actually happened', 'text': 'Agents that read the web get read-only power by default.'}],
        'takeaway': 'Read and act are different permissions.'}),
   ['You can name the rule behind each incident.', 'Your own setup avoids at least four of them.', 'Your first incident log entry exists, even if it is small.'])

CLOSING = [
    "You have now done the full loop: instruct, build, delegate, make it a rule. If you did the exercises, you have a checked post, a small tool on the internet, an agent design with approval buttons, a verified change, and a first line of operating rules.",
    "Here is the last thing I learned, and it has nothing to do with models. AI is not where the advantage comes from. Everyone has the same models. The advantage is the domain: knowing a business, a customer, a problem better than anyone else. And domain knowledge doesn't come from AI. It comes from people. Meet one more customer. Ask one more operator how they really work. Then come back and build for what you heard.",
    "Next steps: the <a href=\"challenge.html\">30-day challenge</a> walks through all of this again with your own work, one small result a day. The <a href=\"recipes.html\">recipes</a> give you ready instructions for ten jobs. And the five full volumes go deeper on every part."]


def build_book():
    toc = ''.join(f'<li><a href="#{c["id"]}">{E(c["title"])}</a></li>' for c in CHAPTERS)
    parts = [f'<nav class="toc" aria-label="Contents"><strong>Contents</strong><ol><li><a href="#intro">Ninety-six hours</a></li>{toc}<li><a href="#closing">The domain comes from people</a></li></ol>'
             '<p class="note">Introduction and Chapters 1–3 are free to read. Chapters 4–14 unlock with the access code from your AI Bible purchase.</p></nav>',
             '<p class="kicker">Introduction</p><h2 id="intro">Ninety-six hours, and the seventy-two days after</h2>' + ''.join(f'<p>{p}</p>' for p in INTRO)]
    locked_started = False
    for i, c in enumerate(CHAPTERS):
        if c['id'] == 'ch4' and not locked_started:
            parts.append('<section class="lock" id="unlock"><h2 style="margin-top:0;color:#fff">Continue with Chapters 4–14</h2>'
                         '<p>You have finished Part 1. The rest of the book takes you from your first tool to an AI operating table for your team, with an exercise in every chapter.</p>'
                         '<p><a href="sales.html">See the AI Bible and current prices →</a></p>'
                         '<label for="paywall-pw-input">Already purchased? Enter your access code</label><br>'
                         '<input id="paywall-pw-input" autocomplete="off" placeholder="e.g. BD-XXXXXXXX"> <button type="button" onclick="window.paywallUnlock()">Unlock</button></section>'
                         '<div class="locked">')
            locked_started = True
        num = i + 1
        body = ''.join(p if p.startswith(('<ul', '<ol')) else f'<p>{p}</p>' for p in c['paras'])
        done = ''.join(f'<li>{E(d)}</li>' for d in c['done'])
        parts.append(f'<p class="kicker">{E(c["part"])} · Chapter {num}</p><h2 id="{c["id"]}">{E(c["title"])}</h2>'
                     f'<div class="build"><strong>What you will build:</strong> {E(c["build"])}</div>{body}{c["lab"]}'
                     f'<div class="done"><strong>Done when</strong><ol>{done}</ol></div>')
    parts.append('<p class="kicker">Closing</p><h2 id="closing">The domain comes from people</h2>' + ''.join(f'<p>{p}</p>' for p in CLOSING))
    parts.append('</div>')
    return page('essentials.html', 'The AI Bible: Essentials — Instruct, Build, Delegate, Make It a Rule',
                'A practical English edition for solo operators and small teams: get AI to do real work, catch its mistakes and turn it into team rules. 14 chapters, an exercise in each.',
                'The AI Bible: Essentials', 'How a non-developer gets AI to do real work, catches its mistakes, and turns it into rules a team can run on. Fourteen chapters, one thing you build in each.',
                '\n'.join(parts), head_extra=unlock_script())


# ============================================================ FAILURE MUSEUM
CASES = [
    ('deploy', 'Works locally, explodes on the server', "First deployment. ImportError: No module named 'blog_modules'. On my laptop it ran fine.", 'What do you suspect first?',
     [('The server is too small', False, 'Server size does not produce this error.'), ('The code points at a folder that only exists on my laptop', True, 'Actual cause: a hard-coded local path. The server never had that folder.'), ('Upgrading Python will fix it', False, 'No version can import a folder that is not there.')],
     'Rule since: no paths outside the repository. Everything the code needs lives in the project and is listed.'),
    ('injection', 'The hidden instruction', 'A bot collecting video descriptions tried to run a command it was never given. The description held text in the background color telling any AI to run it.', 'Most reliable prevention?',
     [('Use a smarter model', False, 'It may refuse sometimes. Relying on that eventually fails.'), ('Pass outside text as plain data and give reading bots no power to run commands', True, 'Outside content is data, not instructions. Separate reading from acting.'), ('Collect only from famous channels', False, 'Famous sources can carry hidden text too.')],
     'That is prompt injection. Agents that read the web get read-only power.'),
    ('cost', '$47 in three hours', 'My first automated collector repeated the same request during testing. Three hours, $47 of API credit.', 'What should have existed from the start?',
     [('A cheaper model', False, 'A cheaper loop is still a loop.'), ('A call cap, a monthly limit and a spending alert', True, 'Cap calls in code; set limits and alerts in the provider console before running.'), ('Turning the computer off at night', False, 'On a server it keeps running.')],
     'Automation spends automatically. Limits come before features.'),
    ('encoding', 'The garbled sales page', 'One morning half of the sales page was unreadable characters.', 'Fastest safe recovery?',
     [('Have the AI fix the characters line by line', False, 'Without the original, fixes mix in new text. It almost always fails.'), ('Restore the last good version from version history, then replay the good changes', True, 'Corruption is reverted, not repaired.'), ('Rebuild the page from scratch', False, 'Slow, and every later edit is lost.')],
     'This is why even small projects use version control.'),
    ('sync', 'The shrinking files', 'The ends of important files kept disappearing. Nobody had edited them.', 'The culprit?',
     [('The AI deleted code secretly', False, 'The history showed no such edits.'), ("A cloud drive's download-on-demand sync", True, 'Programs read and wrote files while sync was touching them. Keep working files outside synced folders.'), ('A failing disk', False, 'It only happened in one synced folder.')],
     'When the environment is the cause, suspect the environment even when there are no errors.'),
    ('silent', 'Nobody stopped, the results did', 'No errors, no alarms. Every bot was running. The key metric had not moved in days.', 'How do you find a silent failure?',
     [('Restart every bot', False, 'Same cause, same state.'), ('Compare where functions are called with where they are defined, and find calls to functions that no longer exist', True, 'Actual cause: a file had been truncated, a function vanished, and the caller swallowed the error.'), ('Log more', False, 'Code that swallows failures logs nothing.')],
     '"No errors" is not "healthy". Anything that swallows a failure must send an alert.'),
]


def build_museum():
    body = []
    for cid, title, story, q, opts, lesson in CASES:
        d = {'steps': [{'context': story, 'q': q, 'options': [O(*o) for o in opts]}],
             'results': [{'min': 1, 'title': 'Correct', 'text': lesson}, {'min': 0, 'title': 'What actually happened', 'text': lesson}]}
        body.append(lab('case-' + cid, 'choice', title, 2, 'What would you do?', 'A real incident from the author\'s operations. Choose, then see the cause and the rule it left behind.', d, kicker='Failure museum'))
    return page('failure-museum.html', 'The Failure Museum — 6 Real AI Automation Incidents',
                'Six real incidents from running AI automations and agents: choose what you would do, then see the cause, the recovery and the rule that followed.',
                'The failure museum', 'Six things that actually went wrong while I ran AI automations every day. Each one left a rule behind.', '\n'.join(body))


# ============================================================ RECIPES
RECIPES = [
    ('marketer', 'Marketer', 'One announcement, three channels', 15,
     [F('src', 'Source — the facts', 'Product A launches Nov 20 · $29 · 10% off until Nov 30 · online store only'), F('who', 'Audience', 'Existing customers and Instagram followers'),
      F('ch', 'Channels and length', 'Blog 300 words / Instagram 200 characters + 5 hashtags / SMS 80 characters'), F('ban', "Don't", 'No invented benefits, reviews or stock. Do not change the discount window.'),
      F('chk', 'Facts that must match', 'Launch date, price, discount and deadline, where to buy')],
     ['Price, dates and store identical across channels', 'Deadline present in the shortest version', 'No invented reviews or benefits']),
    ('owner', 'Small business owner', 'Reply to a one-star review', 10,
     [F('src', 'Review', '"Delivery took over an hour and the food was cold. Never again." (1 star)'), F('fact', 'What you confirmed', 'Rush that evening; left 25 minutes late. Insulated bags were used.'),
      F('can', 'What you can offer', 'Delivery fee covered on the next order if they call the shop.'), F('tone', 'Tone', 'No excuses, short, four sentences max.'),
      F('ban', "Don't", 'No blaming the customer, no unconfirmed causes, no promises you cannot keep (full refunds etc.).')],
     ['Apology comes first', 'Only confirmed facts', 'Only offers you are authorized to make']),
    ('sales', 'Sales', 'Follow-up email after a meeting', 10,
     [F('src', 'Meeting notes', 'Nov 3, Company B, Ms. Park. Evaluating for 20 people. Wants a quote and security documents. Internal review next Wednesday.'),
      F('who', 'Recipient', 'Ms. Park (cc our technical lead)'), F('agree', 'What was agreed', 'Quote and security docs by Thursday, Nov 6.'),
      F('ask', 'What to ask', 'Preferred start date and billing contact.'), F('ban', "Don't", 'No discounts, dates or features that were not discussed.')],
     ['Dates and weekdays correct', 'Nothing promised beyond the meeting', 'Next steps say who does what']),
    ('hr', 'HR & recruiting', 'Draft a job posting', 15,
     [F('role', 'Role and duties', 'Online marketing specialist: run ads, plan content, monthly reporting.'), F('must', 'Requirements', '2+ years running paid ads; builds performance reports in spreadsheets.'),
      F('nice', 'Nice to have', 'Landing page planning, basic video editing.'), F('terms', 'Terms', 'Hybrid, full time, salary range per company policy, 3-month probation.'),
      F('ban', "Don't", 'No age, gender, appearance, marital status or other conditions unrelated to the job. No unconfirmed benefits.')],
     ['No job-irrelevant personal conditions', 'Terms match what is approved', 'How to apply and deadline included']),
    ('finance', 'Finance & bookkeeping', 'Explain the spending spikes', 15,
     [F('data', 'Data (anonymized)', 'Category spend for September and October; vendors renamed A, B, C.'), F('ask', 'Question', 'Which categories grew 30%+ and possible reasons.'),
      F('rule', 'Calculation rule', 'Change = (Oct − Sep) / Sep. Show calculations in a separate table.'), F('out', 'Output', 'Spike table / possible reasons / three questions for the owners.'),
      F('ban', "Don't", 'No causes stated as fact unless in the data. Mark guesses as guesses.')],
     ['Recalculated the changes in your spreadsheet', 'Guesses labelled as guesses', 'No real names or personal data']),
    ('teacher', 'Teacher & trainer', 'Lesson plan with check questions', 20,
     [F('goal', 'Learning goal', 'Grade 8 science: explain three conditions plants need for photosynthesis.'), F('time', 'Time and setting', '45 minutes, 30 students, projector, no lab equipment.'),
      F('flow', 'Flow', 'Hook 5 min → explain 15 → group activity 15 → check questions 10.'), F('quiz', 'Questions', '3 multiple choice + 2 short answer, each with answer and the concept it rests on.'),
      F('ban', "Don't", 'No student names or grades. Mark anything beyond the curriculum as [extension].')],
     ['Answers match the textbook concepts', 'Timing fits 45 minutes', 'No student data']),
    ('public', 'Public sector & nonprofit', 'Draft a response to a resident', 15,
     [F('src', 'Request (personal data removed)', 'Streetlight outside a home has been out for two weeks; feels unsafe at night.'), F('fact', 'Confirmed facts', 'Fixture faulty on inspection; replacement scheduled Nov 8.'),
      F('rule', 'Basis and contact', 'Department and contact only. Cite rules only if the officer verified them.'), F('tone', 'Format', 'Standard reply: greeting → outcome → schedule → contact.'),
      F('ban', "Don't", 'No invented regulations, dates or compensation. No personal data.')],
     ['Schedule and department match the facts', 'No rule names the AI invented', 'Personal data removed']),
    ('creator', 'Creator', 'Three shorts from one long script', 15,
     [F('src', 'Original script', 'Full script of a 15-minute video: "How I cut my food budget in my first year living alone".'), F('who', 'Viewers', 'Young people living alone for the first time.'),
      F('fmt', 'Format', 'Three shorts under 40 seconds: first-3-second line, shot order, captions.'), F('pick', 'Selection rule', 'Prefer moments with numbers or before/after.'),
      F('ban', "Don't", 'No amounts, experiences or sponsors that are not in the script.')],
     ['Every number appears in the original', 'Read aloud, each fits in 40 seconds', 'No invented experiences']),
    ('pm', 'Product & project manager', 'Meeting notes into a decision table', 10,
     [F('src', 'Notes', 'Full summary of the Nov 4 weekly meeting.'), F('out', 'Output', 'Table: decision / action / owner / due / supporting quote.'),
      F('open', 'Open items', 'Anything undecided goes in a separate "open" list.'), F('who', 'Attendees', 'PM Kim, designer Lee, engineer Park, marketer Choi.'),
      F('ban', "Don't", 'Do not fill missing owners or dates with guesses. Unknown means "open".')],
     ['Every action has an owner and date, or says open', 'Quotes exist in the notes', 'Decisions and opinions are separated']),
    ('student', 'Student & job seeker', 'Tighten a personal statement', 15,
     [F('src', 'Draft', 'Answer to: "Describe how you built skills for this role" (700 words).'), F('q', 'Prompt', 'What the application asks.'),
      F('fact', 'Real experience', 'Ran a student club\'s social account for a year: 300 → 1,100 followers, two posts a week.'), F('style', 'Direction', 'Situation–action–result, only real numbers, under 700 words.'),
      F('ban', "Don't", 'No experiences, numbers or awards you do not have. Explain each edit.')],
     ['Every claim is in your real experience list', 'It still sounds like you', 'Length limit respected']),
]


def build_recipes():
    body = []
    for rid, job, title, minutes, fields, checks in RECIPES:
        extra = '<details class="lab-layer" open><summary>Review checklist</summary><ul class="lab-list">' + ''.join(f'<li>{E(c)}</li>' for c in checks) + '</ul></details>'
        sec = lab('recipe-' + rid, 'builder', f'{job}: {title}', minutes, 'An instruction for your own work',
                  'Press "Fill with example" to see the shape, then replace it with your material.', builder(fields, '## After the output\nCheck it against the review checklist before using it.'), kicker=job)
        body.append(sec.replace('<div class="lab-mount">', extra + '<div class="lab-mount">'))
    toc = '<nav class="toc"><strong>Jobs</strong><ol>' + ''.join(f'<li><a href="#recipe-{r[0]}">{E(r[1])}</a></li>' for r in RECIPES) + '</ol></nav>'
    return page('recipes.html', 'AI Work Recipes for 10 Jobs — The AI Bible',
                'Ready-to-use AI instructions with review checklists for marketers, small business owners, sales, HR, finance, teachers, public sector, creators, PMs and students.',
                'AI recipes for your job', 'One common task for each of ten jobs. Fill in your material, copy the instruction, and check the result with the list before you use it.', toc + '\n'.join(body))


# ============================================================ CHALLENGE
WEEKS = [
    ('week-1', 'Week 1 · Instruct', [('Day 1', 'Read Chapter 1 and build three CIF instructions for your own tasks'), ('Day 2', 'Chapter 2: fact-check one real draft and publish it'),
                                     ('Day 3', 'Chapter 3: turn it into two more channels with identical facts'), ('Day 4', 'Use one recipe from your job on real work'),
                                     ('Day 5', 'Log three mistakes AI made and how you caught them'), ('Day 6', 'Reuse your best instruction twice and time it'), ('Day 7', 'Review: time spent vs. time saved, measured')]),
    ('week-2', 'Week 2 · Build', [('Day 8', 'Chapter 4: finish the setup checklist'), ('Day 9', 'Chapter 5: build a one-file tool'), ('Day 10', 'Make three narrow changes, reading the diff each time'),
                                  ('Day 11', 'Chapter 6: break something on purpose and do error first aid'), ('Day 12', 'Pass the six deploy checks and publish'), ('Day 13', 'Start devlog.md: three lines a day'), ('Day 14', 'Show your tool to one person')]),
    ('week-3', 'Week 3 · Delegate', [('Day 15', 'Chapter 8: write an agent design with a stop rule'), ('Day 16', 'Chapter 9: assign every action a level'), ('Day 17', 'Chapter 10: set caps and alerts'),
                                     ('Day 18', 'Chapter 11: one change with plan, approval and proof'), ('Day 19', 'Write your CLAUDE.md'), ('Day 20', 'Log one mistake and the rule it taught you'), ('Day 21', 'List: safe to automate / not yet')]),
    ('week-4', 'Week 4 · Make it a rule', [('Day 22', 'Chapter 12: make one automation survive without your laptop'), ('Day 23', 'Chapter 13: first row of your operating table'),
                                           ('Day 24', 'Write one decision log entry'), ('Day 25', 'Add two more rows'), ('Day 26', 'Do all six failure museum cases'), ('Day 27', 'Review the table with a colleague'), ('Day 28', 'Set the next review date')]),
    ('finish', 'Days 29–30 · Wrap up', [('Day 29', 'List the ten things you made'), ('Day 30', 'Fill in your result card below')]),
]


def build_challenge():
    body = [lab(w, 'steps', title, len(days) * 20, '15–30 minutes a day', 'Ticks are saved in this browser only.',
                {'persist': 'en-' + w, 'steps': [{'time': d, 'title': t} for d, t in days], 'done': title.split(' · ')[0] + ' complete.', 'next': 'On to the next week.'}, kicker='30-day challenge')
            for w, title, days in WEEKS]
    body.append(lab('result-card', 'builder', 'Your 30-day result card', 10, 'Your month on one card',
                    'Only numbers you measured. Copy it to your notes, or share it if you want to.',
                    builder([F('job', 'Your work', 'Marketing lead at an online store'), F('made', 'What you made', '12 checked posts, 8 instructions, one stock-check tool, 3 operating rules'),
                             F('time', 'Measured change', 'Weekly posts: 3 h → 1 h 20 min (4-week average, review included)'), F('stuck', 'Where you got stuck', 'Local path error on deploy, fixed with the six checks'),
                             F('next', 'Next 30 days', 'Move support email tagging to L1, review in a month')], '#AIBible30 — instruct, check, make it a rule.'), kicker='Day 30'))
    body.append('<section class="aib-lab"><p class="lab-kicker">Templates</p><h2 style="margin-top:0">Template pack</h2><p>Instruction, fact-check table, CLAUDE.md, agent design, operating table and decision log, as plain text files you can paste anywhere. (Templates are in Korean; the structures match the chapters of this book.)</p>'
                '<p><a class="lab-btn primary" href="../examples/template-pack/ai-bible-template-pack.zip" download>Download the template pack (ZIP)</a></p></section>')
    return page('challenge.html', 'The AI Bible 30-Day Challenge — 30 Minutes a Day, 10 Results',
                'Thirty days, fifteen to thirty minutes a day, ten real results with AI. Progress saved in your browser, a result card at the end.',
                '30-day challenge', 'One small result a day, following the chapters of Essentials. On day thirty you have ten things you made and one page of rules for your work.', '\n'.join(body))


def main():
    for name, fn in [('essentials.html', build_book), ('failure-museum.html', build_museum), ('recipes.html', build_recipes), ('challenge.html', build_challenge)]:
        (ROOT / 'en' / name).write_text(fn(), encoding='utf-8')
        print('wrote en/' + name)


if __name__ == '__main__':
    main()
