import os
import io
import json
import base64
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

DATA_FILE = "dhruvaa_feed.json"

# ----------------- HELPER FUNCTIONS -----------------
def load_logo_base64() -> str:
    """Loads DHRUVAA.png from repository root if uploaded."""
    for fname in ["DHRUVAA.png", "dhruvaa.png", "DHRUVAA.jpg", "dhruvaa.jpg"]:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    return ""

def image_to_base64(uploaded_file, max_width=1080) -> str:
    """Compresses uploaded mobile photos for fast 4G/5G loading."""
    img = Image.open(uploaded_file).convert("RGB")
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def transliterate_to_telugu(text: str) -> str:
    """Free, unlimited phonetic Tanglish-to-Telugu converter (no API key needed)."""
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

def get_default_news():
    today_str = datetime.date.today().strftime("%d %b %Y")
    return [
        {
            "id": 103,
            "category": "BREAKING • తాజా వార్త",
            "location": "హైదరాబాద్ / HYDERABAD",
            "time": f"{today_str} • Just Now",
            "te_title": "ప్రజా సమస్యల పరిష్కారానికి ప్రత్యేక డిజిటల్ వేదిక ప్రారంభం",
            "te_summary": "పట్టణ మరియు గ్రామీణ ప్రాంతాల్లోని మౌలిక వసతుల సమస్యలను తక్షణమే అధికారుల దృష్టికి తీసుకెళ్లేందుకు కొత్త డిజిటల్ కార్యాచరణ అమల్లోకి వచ్చింది. తాగునీరు, రహదారులు, విద్యుత్ ఫిర్యాదులపై 24 గంటల్లో స్పందించాలని ఆదేశాలు జారీ అయ్యాయి.",
            "en_title": "Special Digital Grievance Redressal Drive Launched Across Districts",
            "en_summary": "Authorities have rolled out a rapid-response digital mechanism to resolve civic and infrastructure complaints across urban and rural mandals within 24 hours, prioritizing drinking water, road repairs, and power supply.",
            "image_b64": "",
            "video_url": "",
            "reporter": "DHRUVAA Bureau"
        },
        {
            "id": 102,
            "category": "STATE • రాష్ట్రం",
            "location": "తెలంగాణ & ఏపీ / TS & AP",
            "time": f"{today_str} • 1 hr ago",
            "te_title": "రైతులకు గుడ్ న్యూస్: మార్కెట్ యార్డుల్లో కొనుగోళ్ల వేగవంతం",
            "te_summary": "వ్యవసాయ మార్కెట్ యార్డుల్లో ధాన్యం కొనుగోలు కేంద్రాలను పూర్తిస్థాయిలో సిద్ధం చేసినట్లు అధికారులు ప్రకటించారు. రైతులకు మద్దతు ధర అందేలా ప్రత్యేక పర్యవేక్షణ బృందాలను ఏర్పాటు చేశారు.",
            "en_title": "Procurement Centers Geared Up Across Market Yards for Farmers",
            "en_summary": "Agriculture officials confirmed that grain procurement centers are fully operational across major market yards with dedicated monitoring teams to ensure minimum support price and swift payments.",
            "image_b64": "",
            "video_url": "",
            "reporter": "DHRUVAA Agri Desk"
        },
        {
            "id": 101,
            "category": "TECH & YOUTH • యువత",
            "location": "విజయవాడ / VIJAYAWADA",
            "time": f"{today_str} • 3 hrs ago",
            "te_title": "యువతకు నైపుణ్యాభివృద్ధి శిక్షణ: ఉచిత ఉద్యోగ మేళా",
            "te_summary": "నిరుద్యోగ యువతకు ఐటీ మరియు బ్యాంకింగ్ రంగాల్లో ఉపాధి కల్పించేందుకు ఈ వారాంతంలో మెగా జాబ్ మేళా నిర్వహించనున్నారు. ఆసక్తి గల అభ్యర్థులు నేరుగా హాజరుకావచ్చని నిర్వాహకులు తెలిపారు.",
            "en_title": "Mega Skill Development & Recruitment Drive Scheduled This Weekend",
            "en_summary": "A large-scale job fair connecting graduates with opportunities in IT, banking, and logistics sectors will be held this weekend with on-spot interviews and free career counseling.",
            "image_b64": "",
            "video_url": "",
            "reporter": "DHRUVAA Youth Desk"
        }
    ]

def load_news_feed():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass
    return get_default_news()

def save_news_feed(feed_list):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(feed_list[:60], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ----------------- SESSION STATE INIT -----------------
if "news_feed" not in st.session_state:
    st.session_state.news_feed = load_news_feed()
if "card_idx" not in st.session_state:
    st.session_state.card_idx = 0
if "lang_mode" not in st.session_state:
    st.session_state.lang_mode = "తెలుగు"

# ----------------- MOBILE APP UI STYLING (ANDROID & iOS READY) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

    /* Hide Streamlit chrome so it feels like a native Android/iOS mobile app */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 0.7rem !important;
        padding-right: 0.7rem !important;
        max-width: 520px !important;
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
        padding: 12px 16px;
        border-radius: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
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
        letter-spacing: 0.5px;
    }
    .dhruvaa-title {
        font-size: 19px;
        font-weight: 800;
        letter-spacing: 0.6px;
        line-height: 1.1;
    }
    .dhruvaa-sub {
        font-size: 11px;
        color: #fde68a;
        font-weight: 600;
    }
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.55rem 0.8rem !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #b91c1c, #dc2626) !important;
        color: white !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- TOP MOBILE APP HEADER -----------------
logo_b64 = load_logo_base64()
logo_inline = (
    f'<img src="data:image/png;base64,{logo_b64}" style="height:36px; border-radius:6px; background:#fff; padding:2px;">'
    if logo_b64 else
    '<div class="dhruvaa-badge">DN</div>'
)

st.markdown(f"""
<div class="dhruvaa-topbar">
    <div class="dhruvaa-brand">
        {logo_inline}
        <div>
            <div class="dhruvaa-title">DHRUVAA NEWS</div>
            <div class="dhruvaa-sub">ధ్రువ న్యూస్ • Fast Short News</div>
        </div>
    </div>
    <div style="font-size:11px; background:rgba(255,255,255,0.16); padding:4px 10px; border-radius:20px; font-weight:700;">
        🔴 LIVE
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- NAVIGATION TABS -----------------
tab_reader, tab_publish = st.tabs(["📱 News Feed (రీడ్)", "✍️ Post News (రిపోర్టర్)"])

# ================= TAB 1: WAY2NEWS-STYLE SHORT CARD READER =================
with tab_reader:
    # Language & Category Filter Bar
    c_lang, c_cat = st.columns([1.15, 1.25])
    with c_lang:
        lang_choice = st.radio(
            "Language",
            ["తెలుగు", "English", "Bilingual"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with c_cat:
        categories = ["ALL NEWS"] + sorted(list({item["category"] for item in st.session_state.news_feed}))
        selected_cat = st.selectbox("Category", categories, label_visibility="collapsed")

    filtered_feed = (
        st.session_state.news_feed
        if selected_cat == "ALL NEWS"
        else [n for n in st.session_state.news_feed if n["category"] == selected_cat]
    )

    if not filtered_feed:
        st.info("No stories in this category yet.")
    else:
        total_cards = len(filtered_feed)
        if st.session_state.card_idx >= total_cards:
            st.session_state.card_idx = 0

        item = filtered_feed[st.session_state.card_idx]

        # Prepare Card Visual (Photo or Branded News Banner)
        if item.get("image_b64"):
            media_html = f'<img src="data:image/jpeg;base64,{item["image_b64"]}" style="width:100%; height:235px; object-fit:cover; display:block;">'
        else:
            media_html = f"""
            <div style="width:100%; height:170px; background: linear-gradient(135deg, #1e293b 0%, #991b1b 70%, #d97706 100%); display:flex; flex-direction:column; justify-content:center; align-items:center; color:white; padding:16px; text-align:center;">
                <div style="font-size:26px; font-weight:900; letter-spacing:1.5px;">DHRUVAA NEWS</div>
                <div style="font-size:13px; color:#fef3c7; font-weight:700; margin-top:4px;">ధ్రువ న్యూస్ • {item['category']}</div>
            </div>
            """

        # Language Content Block
        if lang_choice == "తెలుగు":
            headline_html = f'<div style="font-size:21px; font-weight:800; color:#0f172a; line-height:1.35; margin-bottom:8px;">{item["te_title"]}</div>'
            body_html = f'<div style="font-size:15.5px; color:#334155; line-height:1.68; text-align:justify;">{item["te_summary"]}</div>'
        elif lang_choice == "English":
            headline_html = f'<div style="font-size:20px; font-weight:800; color:#0f172a; line-height:1.3; margin-bottom:8px;">{item["en_title"]}</div>'
            body_html = f'<div style="font-size:14.8px; color:#334155; line-height:1.62; text-align:justify;">{item["en_summary"]}</div>'
        else:
            headline_html = f"""
            <div style="font-size:19.5px; font-weight:800; color:#0f172a; line-height:1.32; margin-bottom:4px;">{item["te_title"]}</div>
            <div style="font-size:16.5px; font-weight:700; color:#991b1b; line-height:1.3; margin-bottom:8px;">{item["en_title"]}</div>
            """
            body_html = f"""
            <div style="font-size:14.8px; color:#1e293b; line-height:1.65; margin-bottom:8px; text-align:justify;">{item["te_summary"]}</div>
            <div style="font-size:13.8px; color:#475569; line-height:1.58; border-top:1px dashed #cbd5e1; padding-top:7px; text-align:justify;">{item["en_summary"]}</div>
            """

        video_btn_html = ""
        if item.get("video_url"):
            safe_vurl = item["video_url"].strip()
            video_btn_html = f"""
            <a href="{safe_vurl}" target="_blank" style="display:block; margin-top:10px; background:#fef2f2; border:1px solid #fecaca; color:#b91c1c; text-align:center; padding:8px; border-radius:8px; font-size:13px; font-weight:800; text-decoration:none;">
                ▶ Watch Full Video Report / వీడియో చూడండి
            </a>
            """

        # Render Way2News Card + Client-Side JPEG Share Poster Generator
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
            .media-box {{
                position: relative;
            }}
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
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            }}
            .brand-watermark {{
                position: absolute;
                bottom: 10px;
                right: 12px;
                background: rgba(15, 23, 42, 0.85);
                color: #facc15;
                font-size: 11px;
                font-weight: 800;
                padding: 3px 9px;
                border-radius: 5px;
            }}
            .content-pad {{
                padding: 15px 16px 14px 16px;
            }}
            .meta-row {{
                display: flex;
                justify-content: space-between;
                font-size: 11.5px;
                font-weight: 700;
                color: #b91c1c;
                margin-bottom: 6px;
            }}
            .card-footer {{
                margin-top: 12px;
                padding-top: 9px;
                border-top: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 11px;
                color: #64748b;
                font-weight: 700;
            }}
            .share-bar {{
                display: flex;
                gap: 8px;
                margin-top: 10px;
            }}
            .share-btn {{
                flex: 1;
                background: #15803d;
                color: #fff;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
                font-weight: 800;
                cursor: pointer;
                text-align: center;
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
                    <div class="card-footer">
                        <span>By {item.get('reporter', 'DHRUVAA Desk')}</span>
                        <span>Card {st.session_state.card_idx + 1} of {total_cards} • DHRUVAA</span>
                    </div>
                </div>
            </div>

            <div class="share-bar">
                <button class="share-btn" onclick="saveShareCard()">📲 Download WhatsApp News Card (HD Image)</button>
            </div>
            <div id="dl-msg" style="text-align:center; font-size:12px; font-weight:700; color:#15803d; margin-top:5px;"></div>

            <script>
                async function saveShareCard() {{
                    const msg = document.getElementById('dl-msg');
                    msg.innerText = "⏳ Creating DHRUVAA share card...";
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
        card_height = 610 if lang_choice == "Bilingual" else 535
        components.html(card_widget, height=card_height, scrolling=True)

        # Bottom Mobile Thumb Navigation (Previous / Next Story)
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

# ================= TAB 2: REPORTER / ADMIN INSTANT PUBLISH =================
with tab_publish:
    st.markdown("#### ✍️ Publish Instant Short News to DHRUVAA Feed")

    with st.expander("🔤 Free Tanglish ➔ Telugu Typing Tool (Unlimited)", expanded=False):
        tanglish_txt = st.text_input("Type Telugu in English letters:", placeholder="e.g., Nedu Hyderabad lo bhari varsham kurustondi")
        if st.button("Convert to Telugu"):
            if tanglish_txt.strip():
                st.code(transliterate_to_telugu(tanglish_txt), language=None)

    with st.form("publish_news_form", clear_on_submit=True):
        p_cat = st.selectbox(
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
        p_loc = st.text_input("Location / Mandal / District", value="హైదరాబాద్ / HYDERABAD")
        p_photo = st.file_uploader("📸 Upload News Photo (Camera or Gallery)", type=["jpg", "jpeg", "png", "webp"])
        p_video = st.text_input("🎬 Video Link (Optional YouTube / Drive / Reel URL)", placeholder="https://...")

        p_te_title = st.text_input("తెలుగు హెడ్‌లైన్ (Telugu Headline)")
        p_te_body = st.text_area("తెలుగు సంక్షిప్త వార్త (Telugu 60-Word Summary)", height=110)

        p_en_title = st.text_input("English Headline")
        p_en_body = st.text_area("English Short Summary (60 Words)", height=110)

        p_reporter = st.text_input("Reporter / Bureau Name", value="DHRUVAA Reporter")

        submitted = st.form_submit_button("🚀 Publish Live on DHRUVAA News", type="primary", use_container_width=True)
        if submitted:
            if not p_te_title.strip() and not p_en_title.strip():
                st.error("Please enter at least a Telugu or English headline.")
            else:
                img_str = image_to_base64(p_photo) if p_photo is not None else ""
                now_time = datetime.datetime.now().strftime("%d %b %Y • %I:%M %p")
                new_story = {
                    "id": int(datetime.datetime.now().timestamp()),
                    "category": p_cat,
                    "location": p_loc.strip() or "DHRUVAA Bureau",
                    "time": now_time,
                    "te_title": p_te_title.strip() or p_en_title.strip(),
                    "te_summary": p_te_body.strip() or p_en_body.strip(),
                    "en_title": p_en_title.strip() or p_te_title.strip(),
                    "en_summary": p_en_body.strip() or p_te_body.strip(),
                    "image_b64": img_str,
                    "video_url": p_video.strip(),
                    "reporter": p_reporter.strip() or "DHRUVAA Desk"
                }
                st.session_state.news_feed.insert(0, new_story)
                save_news_feed(st.session_state.news_feed)
                st.session_state.card_idx = 0
                st.success("✅ Published live to DHRUVAA News! Switch to the 'News Feed' tab to view & share.")
