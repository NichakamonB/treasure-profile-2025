import streamlit as st
import base64
import os
import urllib.parse

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="TREASURE WORLD 2025", 
    layout="wide", 
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

# --- ฟังก์ชันแปลงรูป ---
def get_img_as_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode()
    except: return ""
    return ""

# ====== 🎨 SUPER PREMIUM CSS (WIDE EDITION) ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&family=Prompt:wght@300;400;600&display=swap');

    :root {
        --primary: #32E0C4;
        --secondary: #0D1117;
        --glass: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a2a3a 0%, #000000 90%);
        font-family: 'Prompt', sans-serif;
        color: white;
    }
    
    #MainMenu, header, footer {visibility: hidden;}

    /* --- 🚀 FORCE WIDE DIALOG (ส่วนสำคัญที่ทำให้กว้าง) --- */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 80vw !important; /* กว้าง 80% ของหน้าจอ */
        max-width: 1400px !important; /* ลิมิตไม่ให้เกินจอใหญ่ */
        background: rgba(15, 20, 25, 0.95) !important;
        border: 1px solid #32E0C4 !important;
        border-radius: 20px !important;
    }

    /* HERO SECTION */
    .hero-container {
        text-align: center;
        padding: 20px 0;
        margin-top: -30px;
    }
    .hero-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 4.5rem;
        font-weight: 800;
        letter-spacing: -3px;
        background: linear-gradient(to right, #fff, #32E0C4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(50, 224, 196, 0.3);
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #8899a6;
        letter-spacing: 3px;
        margin-top: 5px;
    }

    /* YOUTUBE BUTTON */
    .yt-button {
        display: inline-flex;
        align-items: center;
        background: rgba(255,0,0,0.1);
        border: 1px solid rgba(255,0,0,0.5);
        color: #ffcccc;
        padding: 8px 25px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: 600;
        margin-top: 15px;
        transition: 0.3s;
    }
    .yt-button:hover {
        background: rgba(255,0,0,0.4);
        color: white;
        box-shadow: 0 0 20px rgba(255,0,0,0.6);
        transform: scale(1.05);
    }

    /* IMAGE MAP */
    .map-frame {
        background: var(--glass);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 30px;
        padding: 10px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        max-width: 1100px;
        margin: 1rem auto 3rem auto;
        position: relative;
    }
    .main-image { width: 100%; border-radius: 20px; display: block; }

    /* HOTSPOTS */
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(50, 224, 196, 0.7); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(50, 224, 196, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(50, 224, 196, 0); }
    }
    .hotspot {
        position: absolute; cursor: pointer; z-index: 10;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.01);
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    .hotspot:hover {
        border-color: #32E0C4;
        background: rgba(50, 224, 196, 0.1);
        animation: pulse 1.5s infinite;
    }

    /* --- PROFILE STYLES --- */
    .profile-header {
        font-family: 'Montserrat', sans-serif;
        font-size: 3.5rem; /* ชื่อใหญ่ขึ้น */
        font-weight: 800;
        color: #32E0C4;
        margin-bottom: 5px;
        line-height: 1.1;
        text-shadow: 0 0 20px rgba(50, 224, 196, 0.2);
    }
    .profile-sub {
        font-size: 1.5rem;
        color: rgba(255,255,255,0.8);
        font-weight: 300;
        margin-bottom: 30px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 15px;
    }
    
    /* Stat Grid (แนวนอน) */
    .stat-row {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 25px;
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 15px;
    }
    .stat-item { text-align: center; width: 100%; }
    .stat-label { font-size: 0.8rem; color: #888; display: block; margin-bottom: 2px; }
    .stat-val { font-size: 1.2rem; font-weight: 700; color: #fff; }

    /* Fact Box */
    .fact-box {
        background: linear-gradient(90deg, rgba(50, 224, 196, 0.05) 0%, transparent 100%);
        border-left: 5px solid #32E0C4;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 1.1rem; /* ตัวหนังสือใหญ่อ่านง่าย */
        line-height: 1.6;
    }

    /* Song Cards */
    .song-link { text-decoration: none; }
    .song-card {
        display: flex; align-items: center; justify-content: space-between;
        background: rgba(255,255,255,0.03);
        padding: 18px 25px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid rgba(255,255,255,0.1);
        transition: 0.2s;
    }
    .song-card:hover {
        background: rgba(50, 224, 196, 0.15);
        border-color: #32E0C4;
        transform: scale(1.01);
    }
    .song-title { color: white; font-weight: 600; font-size: 1.1rem; }

    /* Buttons */
    .stButton button {
        border-radius: 12px !important;
        height: 50px;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ====== DATA (EXPANDED) ======
members = [
    # แถวบน
    {
        "name": "Jeongwoo", "name_thai": "พัค จองอู", "position": "Main Vocalist", 
        "img": "images/jeongwoo.jpg", "birthday": "28 Sep 2004", "height": "181 cm", "mbti": "ISFP", 
        "name_korean": "박정우", "nickname": "Vocal King",
        "facts": [
            "🐺 **Vocal Genius:** ฉายา 'Vocal King' แห่งอิกซาน มีเนื้อเสียงที่ทรงพลังและเข้าถึงอารมณ์เพลงได้ดีที่สุดในเจน 4",
            "🏫 **Education:** จบจาก SOPA (School of Performing Arts Seoul) เอกดนตรีปฏิบัติ",
            "🤣 **Mood Maker:** เป็นคนตลกธรรมชาติ มีรีแอคชั่นที่เป็นมีมได้ตลอดเวลา",
            "✨ **Dedication:** ไม่เคยขาดซ้อมเลยแม้แต่วันเดียวตั้งแต่วันแรกที่เป็นเด็กฝึก"
        ],
        "songs": ["LAST NIGHT", "PARADISE", "HOLD IT IN"], 
        "covers": ["Superstar (Ruben Studdard)", "Weight in Gold"]
    },
    {
        "name": "Haruto", "name_thai": "วาตานาเบะ ฮารุโตะ", "position": "Main Rapper", 
        "img": "images/haruto.jpg", "birthday": "5 Apr 2004", "height": "185 cm", "mbti": "INFP", 
        "name_korean": "하루토", "nickname": "Face Genius",
        "facts": [
            "🦋 **Visual & Voice:** โดดเด่นด้วยใบหน้าฟ้าประทาน (Face Genius) ตัดกับเสียงแร็ปทุ้มต่ำ (Low Tone) ที่เป็นเอกลักษณ์",
            "📏 **Tallest:** สมาชิกที่สูงที่สุดในวง (185 cm) และขายาวมาก",
            "🏠 **Origin:** มาจากฟุกุโอกะ ญี่ปุ่น ครอบครัวเป็นแฟนคลับตัวยงของ BIGBANG",
            "📝 **Songwriter:** มีชื่อเครดิตในการแต่งเนื้อเพลงแร็ปเกือบทุกเพลงของวง"
        ],
        "songs": ["KING KONG", "VolKno (Unit)", "G.O.A.T"], 
        "covers": ["FLASH (Solo Song)", "Dat $tick (Rich Brian)"]
    },
    {
        "name": "Jihoon", "name_thai": "พัค จีฮุน", "position": "Main Dancer, Lead Vocalist", 
        "img": "images/jihoon.jpg", "birthday": "14 Mar 2000", "height": "178 cm", "mbti": "ENTJ", 
        "name_korean": "박지훈", "nickname": "Hoonie",
        "facts": [
            "🐯 **Leadership:** อดีต Leader ที่เข้มแข็ง คอยดูแลระเบียบวินัยและเป็นที่พึ่งของน้องๆ",
            "🎤 **MC Skills:** มีทักษะการพูดและการดำเนินรายการยอดเยี่ยม (อดีต MC Inkigayo)",
            "💃 **Power Dancer:** ไลน์เต้นแข็งแรงและล็อคท่าเป๊ะมาก เป็นเสาหลักด้านการเต้น",
            "💪 **Strength:** แข็งแรงมากและชอบออกกำลังกาย กล้ามเนื้อขาแน่นปึ้ก"
        ],
        "songs": ["KING KONG", "LAST NIGHT", "THE WAY TO"], 
        "covers": ["Song Goes Off", "Ko Ko Bop (EXO)"]
    },
    {
        "name": "Yoshi", "name_thai": "โยชิโนริ", "position": "Main Rapper", 
        "img": "images/yoshi.jpg", "birthday": "15 May 2000", "height": "179 cm", "mbti": "INFP", 
        "name_korean": "요시", "nickname": "Dark Horse",
        "facts": [
            "🐯 **High Tone Rap:** แร็ปเปอร์เสียงสูงที่มีสไตล์ดุดันแต่แฝงความเท่",
            "🎨 **Artistic:** รักศิลปะมาก ชอบวาดรูปและแต่งตัวเก่ง (Fashionista)",
            "🇰🇷 **Heritage:** เกิดที่ญี่ปุ่นแต่เป็นลูกครึ่งเกาหลี (รุ่นที่ 4) ชื่อเกาหลีคือ 'คิม บังจอน'",
            "🎵 **Producer:** มีเพลงที่แต่งเองและโปรดิวซ์เองอย่าง 'STUPID'"
        ],
        "songs": ["STUPID (Composed)", "KING KONG", "VolKno"], 
        "covers": ["Fancy (Drake)", "Be Like Me"]
    },
    {
        "name": "Junghwan", "name_thai": "โซ จองฮวาน", "position": "Maknae, Lead Dancer", 
        "img": "images/junghwan.jpg", "birthday": "18 Feb 2005", "height": "180.3 cm", "mbti": "ENFP-T", 
        "name_korean": "소정환", "nickname": "Super King Cow Baby",
        "facts": [
            "🐮 **King Cow Baby:** น้องเล็กที่ตัวโตและแข็งแรงที่สุดคนหนึ่งของวง",
            "🥋 **Athlete:** อดีตนักกีฬาเทควันโดสายดำ (ทีม K-Tigers)",
            "🕺 **Natural Dancer:** มีไลน์เต้นที่ทรงพลังและยืดหยุ่น เรียนรู้ท่าเต้นไวมาก",
            "🍩 **Foodie:** รักการกินเป็นชีวิตจิตใจ โดยเฉพาะโดนัท"
        ],
        "songs": ["KING KONG", "CLAP! (Unit)", "B.O.M.B"], 
        "covers": ["Supermarket Flowers", "Lie (Jimin)"]
    },
    {
        "name": "Junkyu", "name_thai": "คิม จุนกยู", "position": "Leader (2025), Main Vocal", 
        "img": "images/junkyu.jpg", "birthday": "9 Sep 2000", "height": "178 cm", "mbti": "INFJ", 
        "name_korean": "김준규", "nickname": "Handsome Koala",
        "facts": [
            "🐨 **Unique Voice:** เจ้าของเสียงร้องที่เป็นเอกลักษณ์ที่สุด (YG Style Voice)",
            "👑 **New Leader:** รับตำแหน่ง Leader คนใหม่ในปี 2025 (คู่กับอาซาฮิ)",
            "🎵 **Hit Maker:** แต่งเพลงเก่งมาก เช่น 'MOVE', 'BETTER', 'I WANT YOUR LOVE'",
            "🤣 **Meme King:** เป็นคนตลกธรรมชาติ มีสีหน้าที่เป็นมีมได้ตลอดเวลา"
        ],
        "songs": ["LAST NIGHT", "MOVE (T5)", "BETTER"], 
        "covers": ["Latch", "Beautiful"]
    },
    
    # แถวล่าง
    {
        "name": "Doyoung", "name_thai": "คิม โดยอง", "position": "Main Dancer, Vocalist", 
        "img": "images/doyoung.jpg", "birthday": "4 Dec 2003", "height": "177 cm", "mbti": "ESTP", 
        "name_korean": "김도영", "nickname": "Dobby",
        "facts": [
            "🛹 **Skater Boy:** เจ้าชายสเก็ตบอร์ดที่มีความเท่และน่ารัก",
            "🕺 **Clean Dance:** ได้รับการยกย่องว่ามีไลน์เต้นที่ 'คม' และ 'สะอาด' ที่สุดในวง",
            "🍳 **Chef:** ทำอาหารและอบขนมเก่งมาก มักจะทำให้เมมเบอร์ทานเสมอ",
            "🧣 **Style:** ชอบแต่งตัวสไตล์สตรีทและมีเซนส์ด้านแฟชั่น"
        ],
        "songs": ["KING KONG", "WONDERLAND", "B.L.T"], 
        "covers": ["Lady (Modjo)", "Freedom (iKON)"]
    },
    {
        "name": "Jaehyuk", "name_thai": "ยุน แจฮยอก", "position": "Vocalist", 
        "img": "images/jaehyuk.jpg", "birthday": "23 Jul 2001", "height": "178 cm", "mbti": "INFP", 
        "name_korean": "윤재혁", "nickname": "Chow Chow",
        "facts": [
            "🦁 **Casting Legend:** ถูกทาบทามจากค่ายเพลงใหญ่ๆ ครบทุกค่ายเพราะหน้าตาดี",
            "🥰 **Sweetheart:** เป็นคนที่อบอุ่น ใส่ใจคนรอบข้าง และชอบบอกรักเมมเบอร์",
            "🤚 **Lefty:** ถนัดมือซ้าย ซึ่งหายากในไอดอล",
            "✨ **Growth:** พัฒนาการก้าวกระโดดที่สุด จากไม่มีพื้นฐานเต้นจนเก่งรอบด้าน"
        ],
        "songs": ["LAST NIGHT", "MOVE (T5)", "Wonderland"], 
        "covers": ["Ring Ring", "My Type"]
    },
    {
        "name": "Hyunsuk", "name_thai": "ชเว ฮยอนซอก", "position": "Main Rapper, Main Dancer", 
        "img": "images/hyunsuk.jpg", "birthday": "21 Apr 1999", "height": "171 cm", "mbti": "ENFP", 
        "name_korean": "최현석", "nickname": "Hedgehog",
        "facts": [
            "🦔 **The Pillar:** พี่ใหญ่และอดีต Leader ผู้เป็นเสาหลักของวง",
            "👗 **Fashionista:** คลั่งไคล้แฟชั่นมาก แต่งตัวจัดจ้านที่สุดในวง",
            "⚽ **Football Fan:** แฟนบอลตัวยง (Real Madrid)",
            "🎧 **Producer:** อยู่เบื้องหลังเพลงฮิตมากมายของ TREASURE"
        ],
        "songs": ["KING KONG", "G.O.A.T", "VolKno"], 
        "covers": ["Humble", "Oll' Ready"]
    },
    {
        "name": "Asahi", "name_thai": "ฮามาดะ อาซาฮิ", "position": "Leader (2025), Visual", 
        "img": "images/asahi.jpg", "birthday": "20 Aug 2001", "height": "172 cm", "mbti": "INFP", 
        "name_korean": "아사히", "nickname": "Robot Sahi",
        "facts": [
            "🤖 **Robot Sahi:** ฉายาหุ่นยนต์เพราะหน้านิ่งมาก แต่จริงๆ ตลกหน้าตาย",
            "👑 **New Leader:** ผู้นำวงคนใหม่ (2025) ที่มีวิสัยทัศน์ทางศิลปะ",
            "🎨 **Artist:** วาดรูปสวย ถ่ายรูปเก่ง และมีสไตล์ที่เป็นเอกลักษณ์",
            "🎹 **Composer:** เจ้าพ่อเพลง Ballad ของวง (แต่งเพลง Orange, CLAP!)"
        ],
        "songs": ["LAST NIGHT", "THANK YOU", "ORANGE"], 
        "covers": ["Lay Me Down", "Yamai"]
    }
]

# ====== HEADER & HERO ======
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">TREASURE</h1>
    <p class="hero-subtitle">3rd Mini Album: [LOVE PULSE]</p>
    <a href="https://www.youtube.com/@TREASURE" target="_blank" class="yt-button">
        📺 Official YouTube
    </a>
</div>
""", unsafe_allow_html=True)

# ====== LOGIC: CHECK URL ======
if "id" in st.query_params:
    try:
        idx = int(st.query_params["id"])
        if 0 <= idx < len(members):
            st.session_state.selected_member = members[idx]
            st.query_params.clear() 
    except: pass

# ====== IMAGE MAP ======
group_img_path = "images/group.jpg"

if os.path.exists(group_img_path):
    img_b64 = get_img_as_base64(group_img_path)
    
    st.markdown(f"""
    <div class="map-frame">
        <img src="data:image/jpeg;base64,{img_b64}" class="main-image">
    <a href="?id=0" target="_self" class="hotspot" style="left:6%;top:15%;width:13%;height:35%;" title="Jeongwoo"></a>
    <a href="?id=1" target="_self" class="hotspot" style="left:21%;top:15%;width:13%;height:35%;" title="Haruto"></a>
    <a href="?id=2" target="_self" class="hotspot" style="left:36%;top:15%;width:13%;height:35%;" title="Jihoon"></a>
    <a href="?id=3" target="_self" class="hotspot" style="left:51%;top:15%;width:13%;height:35%;" title="Yoshi"></a>
    <a href="?id=4" target="_self" class="hotspot" style="left:66%;top:15%;width:13%;height:35%;" title="Junghwan"></a>
    <a href="?id=5" target="_self" class="hotspot" style="left:81%;top:15%;width:13%;height:35%;" title="Junkyu"></a>
    <a href="?id=6" target="_self" class="hotspot" style="left:17%;top:55%;width:15%;height:40%;" title="Doyoung"></a>
    <a href="?id=7" target="_self" class="hotspot" style="left:34%;top:55%;width:15%;height:40%;" title="Jaehyuk"></a>
    <a href="?id=8" target="_self" class="hotspot" style="left:51%;top:55%;width:15%;height:40%;" title="Hyunsuk"></a>
    <a href="?id=9" target="_self" class="hotspot" style="left:69%;top:55%;width:15%;height:40%;" title="Asahi"></a>
    </div>
    <p style="text-align:center;color:#666;font-size:0.8rem;margin-top:-10px;letter-spacing:1px;">TOUCH MEMBER TO VIEW PROFILE</p>
    """, unsafe_allow_html=True)
else:
    st.error("❌ ไม่พบไฟล์รูป images/group.jpg")

# ====== POPUP MODAL (BIG & WIDE) ======
if "selected_member" in st.session_state:
    sel = st.session_state.selected_member
    
    @st.dialog(f"💎 {sel['name']}")
    def show_modal():
        # Layout: 40% รูปภาพ | 60% ข้อมูล
        c1, c2 = st.columns([1.5, 2.5])
        
        with c1:
            if os.path.exists(sel['img']):
                st.image(sel['img'], use_container_width=True)
            
            # Stat Grid (ใต้รูป)
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-item"><span class="stat-label">BIRTH</span><span class="stat-val">{sel['birthday'][0:6]}</span></div>
                <div class="stat-item"><span class="stat-label">HEIGHT</span><span class="stat-val">{sel['height']}</span></div>
                <div class="stat-item"><span class="stat-label">MBTI</span><span class="stat-val">{sel['mbti']}</span></div>
            </div>
            <div style="text-align:center; margin-top:-15px; color:#32E0C4; font-weight:bold;">
                "{sel['nickname']}"
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div class='profile-header'>{sel['name_thai']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='profile-sub'>{sel['name_korean']} | {sel['position']}</div>", unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs(["🔥 FACTS", "🎵 SONGS", "🎤 COVERS"])
            
            with tab1:
                for f in sel['facts']:
                    st.markdown(f"<div class='fact-box'>{f}</div>", unsafe_allow_html=True)
            
            with tab2:
                st.markdown("#### ✨ Representative Songs")
                for s in sel.get('songs', []):
                    query = urllib.parse.quote(f"TREASURE {sel['name']} {s} MV")
                    st.markdown(f"""<a href="https://www.youtube.com/results?search_query={query}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎵 {s}</span><span>↗</span></div></a>""", unsafe_allow_html=True)
            
            with tab3:
                st.markdown("#### 🎙️ Solo / Special Covers")
                for c in sel.get('covers', []):
                    query = urllib.parse.quote(f"TREASURE {sel['name']} {c} Cover")
                    st.markdown(f"""<a href="https://www.youtube.com/results?search_query={query}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎧 {c}</span><span>↗</span></div></a>""", unsafe_allow_html=True)

        if st.button("CLOSE PROFILE", use_container_width=True):
            del st.session_state.selected_member
            st.rerun()
    
    show_modal()

# ====== MEMBER GRID (5x5) ======
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center; color:#32E0C4; letter-spacing:2px; margin-bottom:20px; opacity:0.7;'>MEMBER SELECTOR</h4>", unsafe_allow_html=True)

cols1 = st.columns(5)
for i in range(5):
    with cols1[i]:
        m = members[i]
        if st.button(f"{m['name']}", key=f"g1_{i}", use_container_width=True):
            st.session_state.selected_member = m
            st.rerun()
        if os.path.exists(m['img']): st.image(m['img'], use_container_width=True)

st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
cols2 = st.columns(5)
for i in range(5):
    idx = i + 5
    with cols2[i]:
        m = members[idx]
        if st.button(f"{m['name']}", key=f"g2_{idx}", use_container_width=True):
            st.session_state.selected_member = m
            st.rerun()
        if os.path.exists(m['img']): st.image(m['img'], use_container_width=True)

# ====== FOOTER ======
st.markdown("""
<div style="text-align:center; margin-top:50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); opacity:0.5; font-size:0.8rem;">
    TREASURE MAKER PROJECT 2025 | DESIGNED WITH STREAMLIT<br>
    Data Source: Kprofiles & Official YouTube
</div>
""", unsafe_allow_html=True)