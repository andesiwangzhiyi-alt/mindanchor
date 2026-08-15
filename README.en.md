# 锚 · MindAnchor

> **Gently pull the drifting you back.**
> An on-the-spot crisis guide for intrusive thoughts / rumination (thought OCD): **break the loop → lower the anxiety → anchor your attention back to the present.**

![version](https://img.shields.io/badge/version-v0.1-brightgreen) ![license](https://img.shields.io/badge/license-MIT-blue) ![platform](https://img.shields.io/badge/platform-PWA%20%7C%20Mobile%20%7C%20Desktop-lightgrey)

A **100% local, fully offline, data-never-leaves-your-device** open-source PWA. When intrusive thoughts hit under stress, launch a ~5-minute guided protocol that helps you hit the brakes with clinically grounded techniques: **interrupt the loop → physiological breathing to lower anxiety → sensory grounding → park the thought in a "worry parking lot."**

> ⚠️ **Important disclaimer**: This project is a self-help crisis tool. It is **not medical advice and does not replace professional treatment**. If symptoms seriously affect your life, please seek professional help (in the US: 988 Suicide & Crisis Lifeline; UK: NHS 111; or your local mental health services).

---

## ✨ Features

### 🆘 Emergency Protocol (when an episode hits, ~5 min, exit anytime)

| Phase | Duration | What it does | Basis |
|---|---|---|---|
| 1. Interrupt | 8 s | Full-screen alert + vibration to break the loop | Attention redirection / stimulus interruption |
| 2. Breathe | 6 rounds | Physiological sigh breathing (double inhale + long exhale) | Stanford physiological sigh research |
| 3. Ground | ~2 min | 5-4-3-2-1 sensory grounding | Grounding techniques |
| 4. Park | Free | Worry parking lot + scheduled worry time + **urge surfing** | Worry postponement + ERP |

### 🧘 Daily Prevention

- **5-minute micro-practice**: Settle → label the thought → allow the anxiety → observe the urge → reclaim agency (ACT/ERP techniques, streak tracking)
- **Exposure ladder**: L1→L5 self-defined exposure tasks, challenge them step by step

### 📈 Self-Observation

- **SUDS 0-100 scale**: the standard clinical subjective anxiety unit, with 4 severity labels
- **Anxiety evidence follow-up**: re-rate 30 minutes later to prove "anxiety does come down on its own"
- **7-day trend chart**: episode count + average SUDS (pure canvas, zero external dependencies)

### 💬 AI Companion (optional)

- Plugs into any OpenAI-compatible endpoint (defaults to [worldcodes.online](https://worldcodes.online)) for CBT/ERP-guided conversation
- Suggests ERP micro-experiments by theme (checking / contamination / intrusive thoughts / relationships)
- Built-in crisis detection: self-harm-related phrasing triggers help-resource messages

---

## 🚀 Quick Start

### Desktop
```bash
git clone https://github.com/andesiwangzhiyi-alt/mindanchor.git
cd mindanchor/app
python -m http.server 8123 --bind 127.0.0.1
# open http://127.0.0.1:8123 in your browser
```
On Windows, just double-click `scripts/start.bat` to launch.

### Mobile (same Wi-Fi)
1. Find your computer's LAN IP (`ipconfig` on Windows / `ifconfig` on macOS/Linux)
2. Open `http://<your-LAN-IP>:8123` in your phone's browser
3. Browser menu → **Add to Home Screen** — after that it opens fullscreen, supports vibration, and **works offline** (auto-cached on first visit)

### AI Companion Setup (optional)
Settings → AI Companion → fill in:
- Endpoint (default `https://worldcodes.online/v1`)
- API Key
- Model name (e.g. `claude-sonnet-4-6`)

The key is stored only in your local browser. Nothing is uploaded.

---

## 📁 Project Structure

```
mindanchor/
├── app/                        # The app itself (pure frontend, no build step)
│   ├── index.html              # Single-file app: all UI + logic (heavily commented)
│   ├── manifest.webmanifest    # PWA manifest (installable to home screen)
│   ├── sw.js                   # Service Worker (offline cache)
│   └── icons/                  # App icons (breathing-ring design)
├── scripts/                    # Dev tooling
│   ├── start.bat               # One-click launcher for Windows
│   ├── make_icon.py            # Icon generator (PIL)
│   └── test_v01.py             # Playwright regression tests (34 assertions)
├── docs/                       # Documentation (Chinese)
│   ├── 使用指南.md              # Detailed usage guide
│   ├── 设计方案.md              # Design rationale & clinical basis
│   ├── 调研报告-OCD数字干预.md   # Survey of digital OCD interventions
│   └── 开源项目源码分析.md       # Analysis of 4 related open-source projects
├── research/                   # Reproducible research scripts & data
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT
└── README.md                   # This document (中文) / README.en.md (English)
```

---

## 🔒 Privacy & Data

- All data (records, practices, ladder, chats) lives only in browser **localStorage** — zero cloud upload
- Fully offline-capable, no CDN dependencies
- Clear everything anytime from Settings / History

---

## 🧠 Design Sources

This project draws on the following public projects (see [docs/开源项目源码分析.md](docs/开源项目源码分析.md) for details):

- **krishna** (CBT/ERP conversation state machine, vignette scene library) → AI companion
- **OCDetour** (delayed-compulsion timer) → worry parking lot / scheduled worry time
- **ocd-practice** (5-minute meditation scripts, SUDS scale, exposure ladder) → daily practice & scale
- **ERPMate** (anxiety-over-time curve) → anxiety evidence follow-up

Clinical techniques referenced: CBT, ERP, ACT cognitive defusion, worry postponement, physiological sigh breathing.

---

## 📜 License

[MIT](LICENSE). Fork, remix, and suggest — all welcome.

**Remember**: a tool is a crutch, not the treatment itself. If intrusive thoughts keep disrupting your life, please seek professional therapy.

---

*English translation of the [Chinese README](README.md). If you spot a mistranslation, PRs are welcome.*
