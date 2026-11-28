import os
import io
import json
import base64
import hashlib
import datetime
import urllib.parse
import requests
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components

# ----------------- PAGE CONFIGURATION -----------------
st.set_page_config(
    page_title="DHRUVAA News • ధ్రువ న్యూస్",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "dhruvaa_cms_db.json"

# ----------------- SECURITY & HELPER FUNCTIONS -----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()

def load_logo_base64() -> str:
    for fname in ["dhruva logo.png", "DHRUVAA.png", "DHRUVAA.jpg", "dhruvaa.png", "dhruvaa.jpg", "DHRUVAA NEWS.jpg"]:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""

def image_to_base64(uploaded_file, max_width=1080) -> str:
    img = Image.open(uploaded_file).convert("RGB")
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def word_count(text: str) -> int:
    return len([w for w in text.strip().split() if w])

def transliterate_to_telugu(text: str) -> str:
    if not text.strip():
        return ""
    lines = text.split("\n")
    converted_lines = []
    url = "https://inputtools.google.com/request?text={}&itc=te-t-i0-und&num=1"
    headers = {"User-Agent": "Mozilla/5.0"}

    for line in lines:
        words = line.split()
        out_words = []
        for word in words:
            if word.isdigit() or word in [",", ".", "!", "?", "-", ":", ";", "(", ")"]:
                out_words.append(word)
                continue
            try:
                res = requests.get(url.format(urllib.parse.quote(word)), headers=headers, timeout=4)
                data = res.json()
                if data[0] == "SUCCESS" and data[1][0][1]:
                    out_words.append(data[1][0][1][0])
                else:
                    out_words.append(word)
            except Exception:
                out_words.append(word)
        converted_lines.append(" ".join(out_words))
    return "\n".join(converted_lines)

def auto_translate_text(text: str, target_lang: str) -> str:
    """Free sentence-by-sentence translator between Telugu ('te') and English ('en')."""
    if not text.strip():
        return ""
    clean_text = text.replace("*", "").strip()
    sentences = [s.strip() for s in clean_text.split("\n") if s.strip()]
    translated_parts = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for sent in sentences:
        try:
            url = (
                f"https://translate.googleapis.com/translate_a/single?client=gtx"
                f"&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(sent)}"
            )
            res = requests.get(url, headers=headers, timeout=5)
            data = res.json()
            chunk = "".join([part[0] for part in data[0] if part[0]])
            translated_parts.append(chunk)
        except Exception:
            translated_parts.append(sent)
    return "\n".join(translated_parts)

def get_youtube_embed_url(url: str) -> str:
    u = url.strip()
    if "youtube.com/watch?v=" in u:
        vid = u.split("watch?v=")[1].split("&")[0]
        return f"https://www.youtube.com/embed/{vid}"
    if "youtu.be/" in u:
        vid = u.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/embed/{vid}"
    if "youtube.com/live/" in u:
        vid = u.split("youtube.com/live/")[1].split("?")[0]
        return f"https://www.youtube.com/embed/{vid}"
    if "youtube.com/shorts/" in u:
        vid = u.split("youtube.com/shorts/")[1].split("?")[0]
        return f"https://www.youtube.com/embed/{vid}"
    return ""

def get_default_db():
    today_str = datetime.date.today().strftime("%d %b %Y")
    return {
        "stories": [
            {
                "id": 1003,
                "status": "Published",
                "category": "BREAKING • తాజా వార్త",
                "location": "హైదరాబాద్ / HYDERABAD",
                "time": f"{today_str} • Live",
                "te_title": "ప్రజా సమస్యల సత్వర పరిష్కారానికి ప్రత్యేక డిజిటల్ వేదిక ప్రారంభం",
                "te_summary": "పట్టణ మరియు గ్రామీణ ప్రాంతాల్లోని మౌలిక వసతుల సమస్యలను తక్షణమే అధికారుల దృష్టికి తీసుకెళ్లేందుకు కొత్త డిజిటల్ కార్యాచరణ అమల్లోకి వచ్చింది. తాగునీరు, రహదారులు, విద్యుత్ సరఫరా మరియు పారిశుద్ధ్య ఫిర్యాదులపై 24 గంటల్లో స్పందించాలని ఉన్నతాధికారులు స్పష్టమైన ఆదేశాలు జారీ చేశారు. ప్రతి మండల కేంద్రంలో ప్రత్యేక పర్యవేక్షణ అధికారిని నియమించి, ప్రజల నుండి వచ్చే వినతులను ఎప్పటికప్పుడు సమీక్షించనున్నారు. క్షేత్రస్థాయిలో పనుల నాణ్యతను తనిఖీ చేసేందుకు ప్రత్యేక బృందాలు పర్యటిస్తాయని, నిర్లక్ష్యం వహించే సిబ్బందిపై కఠిన చర్యలు తీసుకుంటామని అధికారులు హెచ్చరించారు.",
                "en_title": "Special Digital Grievance Redressal Drive Launched Across All Mandals",
                "en_summary": "Authorities have rolled out a rapid-response digital mechanism to resolve civic and infrastructure complaints across urban and rural mandals within 24 hours. Priority is being accorded to drinking water supply, road repairs, uninterrupted electricity, and sanitation works. Dedicated nodal officers have been appointed at every mandal headquarters to monitor incoming petitions in real time and ensure transparent follow-up. Special inspection squads will conduct surprise field visits to verify the quality of ongoing civil works, with strict disciplinary action warned against administrative negligence.",
                "image_b64": "",
                "video_url": "",
                "reporter": "DHRUVAA State Bureau",
                "reporter_user": "admin",
                "editor": "Senior Desk Editor",
                "approved_by": "Admin (Head of App)",
                "views": 1420
            }
        ],
        # Admin-controlled login accounts ONLY (No public registration)
        "users": [
            {
                "username": "admin",
                "password_hash": hash_password("Dhruvaa@2026"),
                "full_name": "Sumanth Muthamala (Admin)",
                "role": "Admin",
                "zone": "State Headquarters",
                "active": True
            }
        ],
        "ads": [
            {
                "id": 1,
                "sponsor": "DHRUVAA Digital Promotions",
                "tagline": "మీ వ్యాపార ప్రకటనల కోసం సంప్రదించండి • Advertise on DHRUVAA News App & Web",
                "link": "https://dhruvaa-news.streamlit.app",
                "image_b64": "",
                "active": True
            }
        ],
        "epaper": {
            "edition_title": f"DHRUVAA Daily E-Paper • {today_str}",
            "pdf_or_drive_link": "",
            "page_image_b64": "",
            "highlights": "నేటి ప్రత్యేక సంచిక: రాష్ట్ర రాజకీయాలు, జిల్లా వార్తలు, ఉద్యోగ సమాచారం మరియు క్రీడా విశేషాలు."
        },
        "youtube_live": {
            "channel_title": "DHRUVAA NEWS LIVE • ధ్రువ న్యూస్ లైవ్",
            "live_url": "https://www.youtube.com/watch?v=jfKfPfyJRdk",
            "ticker": "🔴 BREAKING: DHRUVAA News App & Web Simultaneous Publishing Live Now!"
        },
        "notifications": [
            {
                "id": 1,
                "time": f"{today_str} • Just Now",
                "title": "🔴 BREAKING ALERT: DHRUVAA News 160-Word Edition Live",
                "message": "Read crisp 160-word verified news in Telugu & English across Mobile and Web."
            }
        ]
    }

def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "stories" in data:
                    if "users" not in data or not data["users"]:
                        data["users"] = get_default_db()["users"]
                    return data
        except Exception:
            pass
    return get_default_db()

def save_db(db_data):
    try:
        db_data["stories"] = db_data["stories"][:100]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(db_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ----------------- SESSION STATE INIT -----------------
if "cms_db" not in st.session_state:
    st.session_state.cms_db = load_db()
if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None  # Dict: {username, full_name, role, zone}
if "cms_section" not in st.session_state:
    st.session_state.cms_section = "News Upload"

# ----------------- MOBILE APP UI STYLING -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 0.55rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.65rem !important;
        padding-right: 0.65rem !important;
        max-width: 560px !important;
    }
    html, body, p, div:not([data-testid="stIconMaterial"]), input, textarea, button {
        font-family: 'Plus Jakarta Sans', 'Noto Sans Telugu', sans-serif !important;
    }
    span[data-testid="stIconMaterial"], .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
    }
    .stApp {
        background-color: #f1f5f9;
    }
    .dhruvaa-topbar {
        background: linear-gradient(135deg, #0f172a 0%, #b91c1c 100%);
        color: #ffffff;
        padding: 11px 15px;
        border-radius: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        box-shadow: 0 4px 14px rgba(185, 28, 28, 0.25);
    }
    .dhruvaa-brand {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .dhruvaa-badge {
        background: #facc15;
        color: #0f172a;
        font-weight: 900;
        font-size: 16px;
        padding: 4px 9px;
        border-radius: 8px;
    }
    .dhruvaa-title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 0.5px;
        line-height: 1.1;
    }
    .dhruvaa-sub {
        font-size: 11px;
        color: #fde68a;
        font-weight: 600;
    }
    .ticker-strip {
        background: #fef2f2;
        border: 1px solid #fecaca;
        color: #991b1b;
        padding: 6px 10px;
        border-radius: 9px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .login-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
    }
    div.stButton > button {
        border-radius: 11px !important;
        font-weight: 700 !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #b91c1c, #dc2626) !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

db = st.session_state.cms_db

# ----------------- TOP MOBILE APP HEADER -----------------
logo_b64 = load_logo_base64()
logo_inline = (
    f'<img src="data:image/png;base64,{logo_b64}" style="height:36px; border-radius:6px; background:#fff; padding:2px;">'
    if logo_b64 else
    '<div class="dhruvaa-badge">DN</div>'
)

pending_count = len([s for s in db["stories"] if s["status"] != "Published"])
auth = st.session_state.auth_user
cms_tab_label = f"🔐 Staff Login" if not auth else f"🎛️ {auth['role']} Desk ({pending_count})"

st.markdown(f"""
<div class="dhruvaa-topbar">
    <div class="dhruvaa-brand">
        {logo_inline}
        <div>
            <div class="dhruvaa-title">DHRUVAA NEWS</div>
            <div class="dhruvaa-sub">ధ్రువ న్యూస్ • App & Web Live</div>
        </div>
    </div>
    <div style="text-align:right;">
        <span style="font-size:11px; background:rgba(255,255,255,0.18); padding:4px 9px; border-radius:20px; font-weight:700;">
            🔴 LIVE
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

latest_ticker = db["notifications"][0]["title"] if db.get("notifications") else db["youtube_live"]["ticker"]
st.markdown(f'<div class="ticker-strip">🔔 {latest_ticker}</div>', unsafe_allow_html=True)

# ----------------- PRIMARY APP NAVIGATION -----------------
nav_reader, nav_epaper, nav_live, nav_cms = st.tabs([
    "📱 News Feed",
    "📰 E-Paper",
    "📺 YouTube Live",
    cms_tab_label
])

# ================= TAB 1: PUBLIC READER NEWS FEED (NO LOGIN REQUIRED) =================
with nav_reader:
    published_stories = [s for s in db["stories"] if s["status"] == "Published"]

    c_lang, c_cat = st.columns([1.15, 1.25])
    with c_lang:
        lang_choice = st.radio(
            "Language",
            ["తెలుగు", "English", "Bilingual"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with c_cat:
        categories = ["ALL NEWS"] + sorted(list({item["category"] for item in published_stories}))
        selected_cat = st.selectbox("Category", categories, label_visibility="collapsed")

    filtered_feed = (
        published_stories
        if selected_cat == "ALL NEWS"
        else [n for n in published_stories if n["category"] == selected_cat]
    )

    if not filtered_feed:
        st.info("No published stories in this category yet.")
    else:
        total_cards = len(filtered_feed)
        if st.session_state.card_idx >= total_cards:
            st.session_state.card_idx = 0

        item = filtered_feed[st.session_state.card_idx]

        active_ads = [a for a in db.get("ads", []) if a.get("active")]
        ad_banner_html = ""
        if active_ads:
            ad = active_ads[st.session_state.card_idx % len(active_ads)]
            ad_img = f'<img src="data:image/jpeg;base64,{ad["image_b64"]}" style="width:100%; max-height:70px; object-fit:cover; border-radius:6px; margin-bottom:4px;">' if ad.get("image_b64") else ""
            ad_banner_html = f"""
            <div style="margin-top:10px; background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:7px 10px;">
                {ad_img}
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:11px;">
                    <span style="font-weight:800; color:#92400e;">📢 AD • {ad['sponsor']}</span>
                    <a href="{ad.get('link','#')}" target="_blank" style="color:#b91c1c; font-weight:800; text-decoration:none;">Visit ➔</a>
                </div>
                <div style="font-size:11.5px; color:#78350f; margin-top:2px;">{ad['tagline']}</div>
            </div>
            """

        if item.get("image_b64"):
            media_html = f'<img src="data:image/jpeg;base64,{item["image_b64"]}" style="width:100%; height:225px; object-fit:cover; display:block;">'
        else:
            media_html = f"""
            <div style="width:100%; height:150px; background: linear-gradient(135deg, #0f172a 0%, #991b1b 70%, #d97706 100%); display:flex; flex-direction:column; justify-content:center; align-items:center; color:white; padding:14px; text-align:center;">
                <div style="font-size:24px; font-weight:900; letter-spacing:1.4px;">DHRUVAA NEWS</div>
                <div style="font-size:12.5px; color:#fef3c7; font-weight:700; margin-top:4px;">ధ్రువ న్యూస్ • {item['category']}</div>
            </div>
            """

        if lang_choice == "తెలుగు":
            headline_html = f'<div style="font-size:20px; font-weight:800; color:#0f172a; line-height:1.35; margin-bottom:8px;">{item["te_title"]}</div>'
            body_html = f'<div style="font-size:15px; color:#1e293b; line-height:1.68; text-align:justify;">{item["te_summary"]}</div>'
        elif lang_choice == "English":
            headline_html = f'<div style="font-size:19.5px; font-weight:800; color:#0f172a; line-height:1.3; margin-bottom:8px;">{item["en_title"]}</div>'
            body_html = f'<div style="font-size:14.5px; color:#1e293b; line-height:1.62; text-align:justify;">{item["en_summary"]}</div>'
        else:
            headline_html = f"""
            <div style="font-size:19px; font-weight:800; color:#0f172a; line-height:1.32; margin-bottom:4px;">{item["te_title"]}</div>
            <div style="font-size:16px; font-weight:700; color:#991b1b; line-height:1.3; margin-bottom:8px;">{item["en_title"]}</div>
            """
            body_html = f"""
            <div style="font-size:14.5px; color:#1e293b; line-height:1.65; margin-bottom:8px; text-align:justify;">{item["te_summary"]}</div>
            <div style="font-size:13.5px; color:#475569; line-height:1.58; border-top:1px dashed #cbd5e1; padding-top:7px; text-align:justify;">{item["en_summary"]}</div>
            """

        video_btn_html = ""
        if item.get("video_url"):
            safe_vurl = item["video_url"].strip()
            video_btn_html = f"""
            <a href="{safe_vurl}" target="_blank" style="display:block; margin-top:10px; background:#fef2f2; border:1px solid #fecaca; color:#b91c1c; text-align:center; padding:8px; border-radius:8px; font-size:13px; font-weight:800; text-decoration:none;">
                ▶ Watch Full Video Report / వీడియో చూడండి
            </a>
            """

        card_widget = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 2px;
                background: transparent;
                font-family: 'Plus Jakarta Sans', 'Noto Sans Telugu', sans-serif;
            }}
            #news-card {{
                background: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
                border: 1px solid #e2e8f0;
            }}
            .media-box {{ position: relative; }}
            .cat-tag {{
                position: absolute;
                top: 12px;
                left: 12px;
                background: #b91c1c;
                color: #ffffff;
                font-size: 11px;
                font-weight: 800;
                padding: 4px 10px;
                border-radius: 6px;
            }}
            .brand-watermark {{
                position: absolute;
                bottom: 10px;
                right: 12px;
                background: rgba(15, 23, 42, 0.88);
                color: #facc15;
                font-size: 11px;
                font-weight: 800;
                padding: 3px 9px;
                border-radius: 5px;
            }}
            .content-pad {{ padding: 14px 16px 14px 16px; }}
            .meta-row {{
                display: flex;
                justify-content: space-between;
                font-size: 11.5px;
                font-weight: 700;
                color: #b91c1c;
                margin-bottom: 6px;
            }}
            .card-footer {{
                margin-top: 11px;
                padding-top: 8px;
                border-top: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
                color: #64748b;
                font-weight: 700;
            }}
            .share-btn {{
                width: 100%;
                margin-top: 10px;
                background: #15803d;
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
                font-weight: 800;
                cursor: pointer;
            }}
        </style>
        </head>
        <body>
            <div id="news-card">
                <div class="media-box">
                    {media_html}
                    <div class="cat-tag">{item['category']}</div>
                    <div class="brand-watermark">DHRUVAA NEWS</div>
                </div>
                <div class="content-pad">
                    <div class="meta-row">
                        <span>📍 {item['location']}</span>
                        <span>🕒 {item['time']}</span>
                    </div>
                    {headline_html}
                    {body_html}
                    {video_btn_html}
                    {ad_banner_html}
                    <div class="card-footer">
                        <span>By {item.get('reporter', 'DHRUVAA Desk')} • 👁️ {item.get('views', 100)}</span>
                        <span>Card {st.session_state.card_idx + 1}/{total_cards} • App & Web</span>
                    </div>
                </div>
            </div>
            <button class="share-btn" onclick="saveShareCard()">📲 Download WhatsApp News Card (HD Image)</button>
            <div id="dl-msg" style="text-align:center; font-size:12px; font-weight:700; color:#15803d; margin-top:5px;"></div>
            <script>
                async function saveShareCard() {{
                    const msg = document.getElementById('dl-msg');
                    msg.innerText = "⏳ Creating DHRUVAA 160-word share card...";
                    await document.fonts.ready;
                    const card = document.getElementById('news-card');
                    const canvas = await html2canvas(card, {{ scale: 2.5, useCORS: true, backgroundColor: "#ffffff" }});
                    const link = document.createElement('a');
                    link.download = "DHRUVAA_News_{item['id']}.jpg";
                    link.href = canvas.toDataURL("image/jpeg", 0.95);
                    link.click();
                    msg.innerText = "✅ Saved! Ready to share on WhatsApp & Instagram.";
                }}
            </script>
        </body>
        </html>
        """
        card_height = 790 if lang_choice == "Bilingual" else 660
        components.html(card_widget, height=card_height, scrolling=True)

        nav1, nav2, nav3 = st.columns([1, 1.1, 1])
        with nav1:
            if st.button("⬅️ Prev", use_container_width=True):
                st.session_state.card_idx = (st.session_state.card_idx - 1) % total_cards
                st.rerun()
        with nav2:
            if st.button("🔄 Latest", use_container_width=True):
                st.session_state.card_idx = 0
                st.rerun()
        with nav3:
            if st.button("Next ➡️", type="primary", use_container_width=True):
                st.session_state.card_idx = (st.session_state.card_idx + 1) % total_cards
                st.rerun()

# ================= TAB 2: E-PAPER READER =================
with nav_epaper:
    ep = db.get("epaper", {})
    st.markdown(f"### 📰 {ep.get('edition_title', 'DHRUVAA Daily E-Paper')}")
    st.info(ep.get("highlights", "Daily Digital Newspaper Edition"))
    if ep.get("page_image_b64"):
        st.markdown(
            f'<img src="data:image/jpeg;base64,{ep["page_image_b64"]}" style="width:100%; border-radius:10px; border:1px solid #cbd5e1;">',
            unsafe_allow_html=True
        )
    if ep.get("pdf_or_drive_link"):
        st.link_button("📥 Open / Download Full E-Paper PDF", ep["pdf_or_drive_link"], type="primary", use_container_width=True)
    elif not ep.get("page_image_b64"):
        st.caption("Admin can upload today's E-Paper front page or PDF link inside the Admin Desk.")

# ================= TAB 3: YOUTUBE & LIVE =================
with nav_live:
    yt = db.get("youtube_live", {})
    st.markdown(f"### 📺 {yt.get('channel_title', 'DHRUVAA NEWS LIVE')}")
    embed_src = get_youtube_embed_url(yt.get("live_url", ""))
    if embed_src:
        components.html(
            f'<iframe width="100%" height="260" src="{embed_src}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="border-radius:12px;"></iframe>',
            height=270
        )
    elif yt.get("live_url"):
        st.link_button("▶ Open YouTube Live Stream", yt["live_url"], type="primary", use_container_width=True)

    video_stories = [s for s in db["stories"] if s["status"] == "Published" and s.get("video_url")]
    if video_stories:
        st.markdown("#### 🎬 Recent Video Bulletins")
        for vs in video_stories:
            st.markdown(f"**{vs['te_title']}** ({vs['location']})")
            st.link_button("▶ Watch Video", vs["video_url"], use_container_width=True)

# ================= TAB 4: AUTHENTICATED CMS & ADMIN PORTAL =================
with nav_cms:
    # ---------- A. LOGIN SCREEN (STRICTLY ADMIN-ISSUED ACCOUNTS ONLY) ----------
    if not st.session_state.auth_user:
        st.markdown("""
        <div class="login-card">
            <div style="font-size:18px; font-weight:800; color:#0f172a; margin-bottom:4px;">🔐 DHRUVAA Editorial & Admin Login</div>
            <div style="font-size:12.5px; color:#64748b; margin-bottom:12px;">
                Authorized Staff & Admin Access Only. New staff logins are issued exclusively by the Administrator.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("staff_login_form"):
            l_user = st.text_input("Username", placeholder="Enter your assigned username")
            l_pass = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("🔓 Sign In to DHRUVAA Desk", type="primary", use_container_width=True)

            if login_btn:
                matched_user = None
                for u in db["users"]:
                    if u["username"].lower() == l_user.strip().lower() and u["password_hash"] == hash_password(l_pass):
                        matched_user = u
                        break

                if not matched_user:
                    st.error("❌ Invalid username or password.")
                elif not matched_user.get("active", True):
                    st.error("⛔ Your account has been suspended by the Admin.")
                else:
                    st.session_state.auth_user = {
                        "username": matched_user["username"],
                        "full_name": matched_user["full_name"],
                        "role": matched_user["role"],
                        "zone": matched_user.get("zone", "State")
                    }
                    st.session_state.cms_section = "News Upload"
                    st.rerun()

        st.caption("Default Master Admin — Username: `admin` | Password: `Dhruvaa@2026` (Change in Staff Management after first login)")

    # ---------- B. LOGGED-IN ROLE-BASED DASHBOARD ----------
    else:
        role = auth["role"]  # 'Admin', 'News Editor', or 'Reporter'

        # Logged-In Header Bar + Logout
        h_col1, h_col2 = st.columns([2.6, 1])
        with h_col1:
            st.markdown(f"**👤 {auth['full_name']}** (`{role}` • {auth['zone']})")
        with h_col2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.auth_user = None
                st.rerun()

        # Role-Filtered Navigation Tiles
        if role == "Admin":
            r1c1, r1c2 = st.columns(2)
            with r1c1:
                if st.button("📰 News Upload\nవార్తల ప్రచురణ", use_container_width=True):
                    st.session_state.cms_section = "News Upload"
            with r1c2:
                if st.button("🔐 Staff & Logins\nసిబ్బంది లాగిన్ నియంత్రణ", use_container_width=True):
                    st.session_state.cms_section = "Staff Management"

            r2c1, r2c2 = st.columns(2)
            with r2c1:
                if st.button(f"🛡️ Approval Center ({pending_count})\nవార్తల ఆమోదం", use_container_width=True):
                    st.session_state.cms_section = "Approval Center"
            with r2c2:
                if st.button("📣 Advertisements\nప్రకటనల నిర్వహణ", use_container_width=True):
                    st.session_state.cms_section = "Advertisements"

            r3c1, r3c2 = st.columns(2)
            with r3c1:
                if st.button("📖 E-Paper\nరోజువారీ పేపర్", use_container_width=True):
                    st.session_state.cms_section = "E-Paper"
            with r3c2:
                if st.button("▶️ YouTube & Live\nవీడియోలు, లైవ్", use_container_width=True):
                    st.session_state.cms_section = "YouTube & Live"

            r4c1, r4c2 = st.columns(2)
            with r4c1:
                if st.button("🔔 Notifications\nబ్రేకింగ్ అలర్ట్స్", use_container_width=True):
                    st.session_state.cms_section = "Notifications"
            with r4c2:
                if st.button("📈 Reports\nవీక్షణలు, గణాంకాలు", use_container_width=True):
                    st.session_state.cms_section = "Reports"

        elif role == "News Editor":
            e1, e2 = st.columns(2)
            with e1:
                if st.button("📰 News Upload\nవార్తల ప్రచురణ", use_container_width=True):
                    st.session_state.cms_section = "News Upload"
            with e2:
                if st.button(f"🛡️ Editor Verification ({pending_count})\nవార్తల పరిశీలన", use_container_width=True):
                    st.session_state.cms_section = "Approval Center"

        else:  # Reporter
            rep1, rep2 = st.columns(2)
            with rep1:
                if st.button("📰 Submit News\nవార్త పంపండి", use_container_width=True):
                    st.session_state.cms_section = "News Upload"
            with rep2:
                if st.button("📋 My Submissions\nనా వార్తల స్థితి", use_container_width=True):
                    st.session_state.cms_section = "My Submissions"

        st.divider()
        sec = st.session_state.cms_section

        # ---------------- 1. NEWS UPLOAD (ALL ROLES) ----------------
        if sec == "News Upload":
            st.markdown("#### 📰 News Upload • వార్తల ప్రచురణ (Up to 160 Words)")

            with st.expander("🔤 Free Tanglish ➔ Telugu & Two-Way Auto-Translator", expanded=False):
                t_in = st.text_input("Tanglish to Telugu:", placeholder="e.g., Nedu Hyderabad lo pratyeka samavesam jarigindi")
                if st.button("Convert Tanglish ➔ Telugu"):
                    if t_in.strip():
                        st.code(transliterate_to_telugu(t_in), language=None)

                tr_src = st.text_area("Paste Telugu OR English text to auto-translate:", height=80)
                tr1, tr2 = st.columns(2)
                with tr1:
                    if st.button("Translate ➔ English", use_container_width=True):
                        if tr_src.strip():
                            st.code(auto_translate_text(tr_src, "en"), language=None)
                with tr2:
                    if st.button("Translate ➔ తెలుగు", use_container_width=True):
                        if tr_src.strip():
                            st.code(auto_translate_text(tr_src, "te"), language=None)

            with st.form("cms_news_upload_form", clear_on_submit=True):
                st.text_input("Reporter Name", value=auth["full_name"], disabled=True)
                u_cat = st.selectbox(
                    "Category",
                    [
                        "BREAKING • తాజా వార్త",
                        "POLITICS • రాజకీయం",
                        "DISTRICT • జిల్లా వార్తలు",
                        "STATE • రాష్ట్రం",
                        "SPORTS • క్రీడలు",
                        "CINEMA • సినిమా",
                        "TECH & YOUTH • యువత"
                    ]
                )
                u_loc = st.text_input("Location / Mandal / District", value=auth["zone"])
                u_photo = st.file_uploader("📸 Attach News Photo", type=["jpg", "jpeg", "png", "webp"])
                u_video = st.text_input("🎬 Video Link (YouTube / Drive / Reel URL)", placeholder="https://...")

                u_te_title = st.text_input("తెలుగు హెడ్‌లైన్ (Telugu Headline)")
                u_te_body = st.text_area("తెలుగు వార్త (Up to 160 Words Summary)", height=140)

                u_en_title = st.text_input("English Headline")
                u_en_body = st.text_area("English News Summary (Up to 160 Words)", height=140)

                if role == "Admin":
                    publish_mode = st.radio(
                        "Publishing Action",
                        [
                            "Publish Live Immediately (Admin Final Approval)",
                            "Send to Approval Queue (Step 1)"
                        ]
                    )
                else:
                    st.info("ℹ️ Your submission will be sent to the **News Editor** and **Admin** for verification before going live.")
                    publish_mode = "Send to Approval Queue (Step 1)"

                if st.form_submit_button("🚀 Submit Story", type="primary", use_container_width=True):
                    if not u_te_title.strip() and not u_en_title.strip():
                        st.error("Please enter at least a Telugu or English headline.")
                    else:
                        img_str = image_to_base64(u_photo) if u_photo is not None else ""
                        now_time = datetime.datetime.now().strftime("%d %b %Y • %I:%M %p")
                        is_direct = (role == "Admin" and "Publish Live Immediately" in publish_mode)

                        new_story = {
                            "id": int(datetime.datetime.now().timestamp()),
                            "status": "Published" if is_direct else "Pending Editor",
                            "category": u_cat,
                            "location": u_loc.strip() or auth["zone"],
                            "time": now_time,
                            "te_title": u_te_title.strip() or u_en_title.strip(),
                            "te_summary": u_te_body.strip() or u_en_body.strip(),
                            "en_title": u_en_title.strip() or u_te_title.strip(),
                            "en_summary": u_en_body.strip() or u_te_body.strip(),
                            "image_b64": img_str,
                            "video_url": u_video.strip(),
                            "reporter": auth["full_name"],
                            "reporter_user": auth["username"],
                            "editor": auth["full_name"] if is_direct else "Awaiting Editor",
                            "approved_by": auth["full_name"] if is_direct else "Pending Admin",
                            "views": 1
                        }
                        db["stories"].insert(0, new_story)
                        save_db(db)
                        if is_direct:
                            st.success("✅ Approved & Published Live on App and Web!")
                        else:
                            st.success("✅ Submitted! Sent to News Editor & Admin Approval Center.")

        # ---------------- 2. REPORTER MY SUBMISSIONS ----------------
        elif sec == "My Submissions" and role == "Reporter":
            st.markdown("#### 📋 My Submitted Stories")
            my_stories = [s for s in db["stories"] if s.get("reporter_user") == auth["username"]]
            if not my_stories:
                st.info("You haven't submitted any stories yet.")
            else:
                for ms in my_stories:
                    st.markdown(f"**[{ms['status']}]** {ms['te_title']} — *{ms['time']}*")

        # ---------------- 3. APPROVAL CENTER (ADMIN & NEWS EDITOR) ----------------
        elif sec == "Approval Center" and role in ["Admin", "News Editor"]:
            st.markdown("#### 🛡️ Approval Center • వార్తల ఆమోదం")
            if role == "News Editor":
                st.caption("As News Editor, verify & edit drafts below and forward them to the Admin for final live publishing.")
            else:
                st.caption("As Admin, review, edit, grant final live approval, or unpublish/delete any story.")

            for idx, story in enumerate(db["stories"]):
                with st.expander(f"[{story['status']}] {story['te_title'][:48]}...", expanded=(story["status"] != "Published")):
                    st.markdown(f"**Reporter:** {story.get('reporter')} | **Location:** {story.get('location')} | **Status:** `{story['status']}`")
                    ed_te_title = st.text_input("Telugu Headline", value=story["te_title"], key=f"ed_tt_{story['id']}")
                    ed_te_body = st.text_area(
                        f"Telugu Summary ({word_count(story['te_summary'])}/160 words)",
                        value=story["te_summary"],
                        height=130,
                        key=f"ed_tb_{story['id']}"
                    )
                    ed_en_title = st.text_input("English Headline", value=story["en_title"], key=f"ed_et_{story['id']}")
                    ed_en_body = st.text_area(
                        f"English Summary ({word_count(story['en_summary'])}/160 words)",
                        value=story["en_summary"],
                        height=130,
                        key=f"ed_eb_{story['id']}"
                    )

                    if role == "News Editor":
                        if st.button("✍️ Verify & Forward to Admin", type="primary", key=f"step2_{story['id']}", use_container_width=True):
                            db["stories"][idx]["te_title"] = ed_te_title
                            db["stories"][idx]["te_summary"] = ed_te_body
                            db["stories"][idx]["en_title"] = ed_en_title
                            db["stories"][idx]["en_summary"] = ed_en_body
                            db["stories"][idx]["editor"] = auth["full_name"]
                            if db["stories"][idx]["status"] != "Published":
                                db["stories"][idx]["status"] = "Pending Head Approval"
                            save_db(db)
                            st.success("✅ Verified and forwarded to Admin!")
                            st.rerun()

                    elif role == "Admin":
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            if st.button("✅ Final Approve & Live", type="primary", key=f"app_{story['id']}", use_container_width=True):
                                db["stories"][idx]["te_title"] = ed_te_title
                                db["stories"][idx]["te_summary"] = ed_te_body
                                db["stories"][idx]["en_title"] = ed_en_title
                                db["stories"][idx]["en_summary"] = ed_en_body
                                db["stories"][idx]["approved_by"] = auth["full_name"]
                                db["stories"][idx]["status"] = "Published"
                                save_db(db)
                                st.success("✅ Published Live on App & Web!")
                                st.rerun()
                        with b2:
                            if st.button("⏸️ Hold / Unpublish", key=f"hold_{story['id']}", use_container_width=True):
                                db["stories"][idx]["status"] = "Pending Head Approval"
                                save_db(db)
                                st.warning("Moved back to approval queue.")
                                st.rerun()
                        with b3:
                            if st.button("🗑️ Delete", key=f"del_{story['id']}", use_container_width=True):
                                db["stories"].pop(idx)
                                save_db(db)
                                st.rerun()

        # ---------------- 4. STAFF & LOGIN MANAGEMENT (ADMIN ONLY) ----------------
        elif sec == "Staff Management" and role == "Admin":
            st.markdown("#### 🔐 Staff Login Management (Admin Exclusive)")
            st.caption("Create, suspend, reset passwords, or delete staff accounts. Reporters cannot register themselves.")

            with st.form("admin_create_user_form", clear_on_submit=True):
                st.markdown("**➕ Issue New Staff Login**")
                new_full = st.text_input("Full Name (e.g., Karthik Reddy)")
                new_uname = st.text_input("Assign Username (e.g., karthik_rep)")
                new_pwd = st.text_input("Assign Password", type="password")
                new_role = st.selectbox("Assign Role", ["Reporter", "News Editor", "Admin"])
                new_zone = st.text_input("Assigned District / Bureau", value="Hyderabad / Telangana")

                if st.form_submit_button("✅ Create Staff Login Account", type="primary", use_container_width=True):
                    if not new_full.strip() or not new_uname.strip() or not new_pwd.strip():
                        st.error("All fields (Name, Username, Password) are required.")
                    elif any(u["username"].lower() == new_uname.strip().lower() for u in db["users"]):
                        st.error("That username already exists. Choose a unique username.")
                    else:
                        db["users"].append({
                            "username": new_uname.strip(),
                            "password_hash": hash_password(new_pwd),
                            "full_name": new_full.strip(),
                            "role": new_role,
                            "zone": new_zone.strip(),
                            "active": True
                        })
                        save_db(db)
                        st.success(f"✅ Login created for **{new_full}** (`{new_uname}` • {new_role})")
                        st.rerun()

            st.markdown("#### 👥 Active & Suspended Staff Accounts")
            for i, u in enumerate(db["users"]):
                status_tag = "🟢 Active" if u.get("active", True) else "🔴 Suspended"
                with st.expander(f"{u['full_name']} (@{u['username']}) — {u['role']} [{status_tag}]"):
                    st.write(f"**Zone:** {u.get('zone', 'State')} | **Role:** `{u['role']}`")

                    # Reset Password
                    rst_pwd = st.text_input("Set New Password", type="password", key=f"rst_pwd_{u['username']}")
                    c_u1, c_u2, c_u3 = st.columns(3)
                    with c_u1:
                        if st.button("🔑 Update Password", key=f"btn_rst_{u['username']}", use_container_width=True):
                            if rst_pwd.strip():
                                db["users"][i]["password_hash"] = hash_password(rst_pwd)
                                save_db(db)
                                st.success("Password updated!")
                    with c_u2:
                        if u["username"] != "admin":
                            toggle_label = "⛔ Suspend" if u.get("active", True) else "✅ Activate"
                            if st.button(toggle_label, key=f"btn_tog_{u['username']}", use_container_width=True):
                                db["users"][i]["active"] = not u.get("active", True)
                                save_db(db)
                                st.rerun()
                    with c_u3:
                        if u["username"] != "admin":
                            if st.button("🗑️ Delete Login", key=f"btn_del_{u['username']}", use_container_width=True):
                                db["users"].pop(i)
                                save_db(db)
                                st.rerun()

        # ---------------- 5. ADVERTISEMENTS (ADMIN ONLY) ----------------
        elif sec == "Advertisements" and role == "Admin":
            st.markdown("#### 📣 Advertisements • ప్రకటనల నిర్వహణ")
            with st.form("add_ad_form", clear_on_submit=True):
                ad_sponsor = st.text_input("Sponsor / Business Name")
                ad_tagline = st.text_input("Ad Text / Offer Details")
                ad_link = st.text_input("Target URL / WhatsApp Link", value="https://dhruvaa-news.streamlit.app")
                ad_banner = st.file_uploader("Banner Image (Optional)", type=["jpg", "jpeg", "png"])
                if st.form_submit_button("➕ Publish Ad on Feed", type="primary", use_container_width=True):
                    if ad_sponsor.strip() and ad_tagline.strip():
                        b_img = image_to_base64(ad_banner, max_width=800) if ad_banner else ""
                        db["ads"].insert(0, {
                            "id": int(datetime.datetime.now().timestamp()),
                            "sponsor": ad_sponsor.strip(),
                            "tagline": ad_tagline.strip(),
                            "link": ad_link.strip(),
                            "image_b64": b_img,
                            "active": True
                        })
                        save_db(db)
                        st.success("Ad live across news cards!")
                        st.rerun()

            for i, ad in enumerate(db["ads"]):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{ad['sponsor']}**: {ad['tagline']}")
                with c2:
                    if st.button("Delete", key=f"del_ad_{i}"):
                        db["ads"].pop(i)
                        save_db(db)
                        st.rerun()

        # ---------------- 6. E-PAPER (ADMIN ONLY) ----------------
        elif sec == "E-Paper" and role == "Admin":
            st.markdown("#### 📖 E-Paper Management • రోజువారీ పేపర్")
            with st.form("epaper_form"):
                ep_title = st.text_input("Edition Title", value=db["epaper"].get("edition_title", ""))
                ep_highlights = st.text_area("Today's Front-Page Highlights", value=db["epaper"].get("highlights", ""))
                ep_link = st.text_input("Full PDF / Google Drive Link", value=db["epaper"].get("pdf_or_drive_link", ""))
                ep_img = st.file_uploader("Upload Front Page Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
                if st.form_submit_button("💾 Update Daily E-Paper", type="primary", use_container_width=True):
                    db["epaper"]["edition_title"] = ep_title
                    db["epaper"]["highlights"] = ep_highlights
                    db["epaper"]["pdf_or_drive_link"] = ep_link
                    if ep_img:
                        db["epaper"]["page_image_b64"] = image_to_base64(ep_img, max_width=1200)
                    save_db(db)
                    st.success("✅ E-Paper updated live!")

        # ---------------- 7. YOUTUBE & LIVE (ADMIN ONLY) ----------------
        elif sec == "YouTube & Live" and role == "Admin":
            st.markdown("#### ▶️ YouTube & Live • వీడియోలు, లైవ్")
            with st.form("yt_live_form"):
                yt_title = st.text_input("Channel / Live Stream Title", value=db["youtube_live"].get("channel_title", ""))
                yt_url = st.text_input("YouTube Live or Video URL", value=db["youtube_live"].get("live_url", ""))
                yt_tick = st.text_input("Live Scrolling Ticker", value=db["youtube_live"].get("ticker", ""))
                if st.form_submit_button("💾 Update Live Stream", type="primary", use_container_width=True):
                    db["youtube_live"]["channel_title"] = yt_title
                    db["youtube_live"]["live_url"] = yt_url
                    db["youtube_live"]["ticker"] = yt_tick
                    save_db(db)
                    st.success("✅ YouTube & Live settings updated!")

        # ---------------- 8. NOTIFICATIONS (ADMIN ONLY) ----------------
        elif sec == "Notifications" and role == "Admin":
            st.markdown("#### 🔔 Notifications • బ్రేకింగ్ అలర్ట్స్")
            with st.form("notif_form", clear_on_submit=True):
                n_title = st.text_input("Breaking Alert Headline", placeholder="🔴 BREAKING: ...")
                n_msg = st.text_area("Alert Details", height=80)
                if st.form_submit_button("📢 Broadcast Breaking Alert", type="primary", use_container_width=True):
                    if n_title.strip():
                        db["notifications"].insert(0, {
                            "id": int(datetime.datetime.now().timestamp()),
                            "time": datetime.datetime.now().strftime("%d %b %Y • %I:%M %p"),
                            "title": n_title.strip(),
                            "message": n_msg.strip()
                        })
                        save_db(db)
                        st.success("✅ Breaking Alert pushed to top ticker!")
                        st.rerun()

            for n in db.get("notifications", [])[:10]:
                st.markdown(f"- **{n['title']}** ({n['time']}) — {n['message']}")

        # ---------------- 9. REPORTS (ADMIN ONLY) ----------------
        elif sec == "Reports" and role == "Admin":
            st.markdown("#### 📈 Reports • వీక్షణలు, గణాంకాలు")
            total_stories = len(db["stories"])
            pub_stories = len([s for s in db["stories"] if s["status"] == "Published"])
            pend_editor = len([s for s in db["stories"] if s["status"] == "Pending Editor"])
            pend_head = len([s for s in db["stories"] if s["status"] == "Pending Head Approval"])
            total_views = sum(s.get("views", 0) for s in db["stories"])

            m1, m2, m3 = st.columns(3)
            m1.metric("Published Live", pub_stories)
            m2.metric("Pending Approval", pend_editor + pend_head)
            m3.metric("Total Readers", f"{total_views:,}")

            st.markdown("**Editorial Pipeline & Staff Summary:**")
            st.write(f"- Active Staff Accounts: **{len([u for u in db['users'] if u.get('active', True)])}**")
            st.write(f"- Step 1/2 (Awaiting News Editor): **{pend_editor}**")
            st.write(f"- Step 3 (Awaiting Admin Final Approval): **{pend_head}**")
            st.write(f"- Step 4 (Live on App & Web): **{pub_stories}** of {total_stories} total stories")
