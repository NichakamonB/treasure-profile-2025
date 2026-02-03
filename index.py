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

# --- ฟังก์ชันแปลงรูป (Smart Path: หาเองว่ารูปอยู่ไหน) ---
def get_img_as_base64(file_path):
    # ลองหาในโฟลเดอร์ปัจจุบันก่อน (Root)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    # ถ้าไม่เจอ ลองหาในโฟลเดอร์ images/ (เผื่อไว้)
    elif os.path.exists(f"images/{file_path}"):
        with open(f"images/{file_path}", "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
        
    return ""

# ====== 🎨 SUPER PREMIUM CSS ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800&family=Prompt:wght@300;500;700&display=swap');

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
        font-size: 3.5rem; 
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

    .fact-box {
        background: linear-gradient(90deg, rgba(50, 224, 196, 0.05) 0%, transparent 100%);
        border-left: 5px solid #32E0C4;
        padding: 15px 20px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 1.1rem;
        line-height: 1.6;
    }

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

    /* WIDE DIALOG */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 80vw !important;
        max-width: 1400px !important;
        background: rgba(15, 20, 25, 0.95) !important;
        border: 1px solid #32E0C4 !important;
        border-radius: 20px !important;
    }
    
    .stButton button { border-radius: 12px !important; height: 50px; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# ====== DATA (FIXED IMAGE PATHS & DOYOUNG SONG) ======
members = [
    # แถวบน
    {
        "name": "Jeongwoo", "name_thai": "พัค จองอู", "position": "Main Vocalist", 
        "img": "jeongwoo.jpg", "birthday": "28 Sep 2004", "height": "181 cm", "mbti": "ISFP", 
        "name_korean": "박정우", "nickname": "Vocal King",
        "facts": ["🐺 **Vocal Genius:** ฉายา 'Vocal King' แห่งอิกซาน", "🏫 **Education:** จบจาก SOPA", "🤣 **Mood Maker:** เป็นคนตลกธรรมชาติ", "✨ **Dedication:** ไม่เคยขาดซ้อมเลยแม้แต่วันเดียว"],
        "songs": ["LAST NIGHT", "PARADISE", "HOLD IT IN"], 
        "covers": ["Superstar (Ruben Studdard)", "Weight in Gold"]
    },
    {
        "name": "Haruto", "name_thai": "วาตานาเบะ ฮารุโตะ", "position": "Main Rapper", 
        "img": "haruto.jpg", "birthday": "5 Apr 2004", "height": "185 cm", "mbti": "INFP", 
        "name_korean": "하루토", "nickname": "Face Genius",
        "facts": ["🦋 **Visual & Voice:** Face Genius + Low Tone Rap", "📏 **Tallest:** สูงที่สุดในวง (185 cm)", "🏠 **Origin:** ฟุกุโอกะ ญี่ปุ่น", "📝 **Songwriter:** แต่งแร็ปเกือบทุกเพลง"],
        "songs": ["KING KONG", "VolKno (Unit)", "G.O.A.T"], 
        "covers": ["FLASH (Solo Song)", "Dat $tick"]
    },
    {
        "name": "Jihoon", "name_thai": "พัค จีฮุน", "position": "Main Dancer, Lead Vocalist", 
        "img": "jihoon.jpg", "birthday": "14 Mar 2000", "height": "178 cm", "mbti": "ENTJ", 
        "name_korean": "박지훈", "nickname": "Hoonie",
        "facts": ["🐯 **Leadership:** อดีต Leader ที่เข้มแข็ง", "🎤 **MC Skills:** พูดเก่ง ดำเนินรายการดีเยี่ยม", "💃 **Power Dancer:** ไลน์เต้นแข็งแรง", "💪 **Strength:** แข็งแรงมาก"],
        "songs": ["KING KONG", "LAST NIGHT", "THE WAY TO"], 
        "covers": ["Song Goes Off", "Ko Ko Bop"]
    },
    {
        "name": "Yoshi", "name_thai": "โยชิโนริ", "position": "Main Rapper", 
        "img": "yoshi.jpg", "birthday": "15 May 2000", "height": "179 cm", "mbti": "INFP", 
        "name_korean": "요시", "nickname": "Dark Horse",
        "facts": ["🐯 **High Tone Rap:** แร็ปเสียงสูงดุดัน", "🎨 **Artistic:** รักศิลปะและแฟชั่น", "🇰🇷 **Heritage:** ลูกครึ่งเกาหลี (รุ่นที่ 4)", "🎵 **Producer:** แต่งเพลง 'STUPID'"],
        "songs": ["STUPID (Composed)", "KING KONG", "VolKno"], 
        "covers": ["Fancy (Drake)", "Be Like Me"]
    },
    {
        "name": "Junghwan", "name_thai": "โซ จองฮวาน", "position": "Maknae, Lead Dancer", 
        "img": "junghwan.jpg", "birthday": "18 Feb 2005", "height": "180.3 cm", "mbti": "ENFP-T", 
        "name_korean": "소정환", "nickname": "Super King Cow Baby",
        "facts": ["🐮 **King Cow Baby:** น้องเล็กตัวโต", "🥋 **Athlete:** อดีตนักกีฬาเทควันโด K-Tigers", "🕺 **Natural Dancer:** เต้นเก่ง เรียนรู้ไว", "🍩 **Foodie:** รักการกินเป็นชีวิตจิตใจ"],
        "songs": ["KING KONG", "CLAP! (Unit)", "B.O.M.B"], 
        "covers": ["Supermarket Flowers", "Lie (Jimin)"]
    },
    {
        "name": "Junkyu", "name_thai": "คิม จุนกยู", "position": "Leader (2025), Main Vocal", 
        "img": "junkyu.jpg", "birthday": "9 Sep 2000", "height": "178 cm", "mbti": "INFJ", 
        "name_korean": "김준규", "nickname": "Handsome Koala",
        "facts": ["🐨 **Unique Voice:** เสียงเอกลักษณ์ (YG Style)", "👑 **New Leader:** ผู้นำวงคนใหม่ (2025)", "🎵 **Hit Maker:** แต่งเพลงเก่ง (MOVE, BETTER)", "🤣 **Meme King:** ตลกธรรมชาติ"],
        "songs": ["LAST NIGHT", "MOVE (T5)", "BETTER"], 
        "covers": ["Latch", "Beautiful"]
    },
    
    # แถวล่าง
    {
        "name": "Doyoung", "name_thai": "คิม โดยอง", "position": "Main Dancer, Vocalist", 
        "img": "doyoung.jpg", "birthday": "4 Dec 2003", "height": "177 cm", "mbti": "ESTP", 
        "name_korean": "김도영", "nickname": "Dobby",
        "facts": [
            "🛹 **Skater Boy:** เจ้าชายสเก็ตบอร์ดสุดเท่",
            "🕺 **Clean Dance:** ไลน์เต้น 'คม' และ 'สะอาด' ที่สุด",
            "🍳 **Chef:** ทำอาหารและอบขนมเก่งมาก",
            "🧣 **Style:** แฟชั่นนิสต้าสายสตรีท"
        ],
        "songs": ["KING KONG", "WONDERLAND", "B.L.T"], 
        # แก้ไขตามคำขอ: ใช้ Babushka Boi แทน Lady
        "covers": ["Babushka Boi (Dance Perf.)", "Freedom (iKON)"]
    },
    {
        "name": "Jaehyuk", "name_thai": "ยุน แจฮยอก", "position": "Vocalist", 
        "img": "jaehyuk.jpg", "birthday": "23 Jul 2001", "height": "178 cm", "mbti": "INFP", 
        "name_korean": "윤재혁", "nickname": "Chow Chow",
        "facts": ["🦁 **Casting Legend:** ถูกจีบทุกค่ายเพราะหน้าตาดี", "🥰 **Sweetheart:** อบอุ่น ใส่ใจคนรอบข้าง", "🤚 **Lefty:** ถนัดมือซ้าย", "✨ **Growth:** พัฒนาการก้าวกระโดด"],
        "songs": ["LAST NIGHT", "MOVE (T5)", "Wonderland"], 
        "covers": ["Ring Ring", "My Type"]
    },
    {
        "name": "Hyunsuk", "name_thai": "ชเว ฮยอนซอก", "position": "Main Rapper, Main Dancer", 
        "img": "hyunsuk.jpg", "birthday": "21 Apr 1999", "height": "171 cm", "mbti": "ENFP", 
        "name_korean": "최현석", "nickname": "Hedgehog",
        "facts": ["🦔 **The Pillar:** พี่ใหญ่และอดีต Leader", "👗 **Fashionista:** แต่งตัวจัดจ้านที่สุด", "⚽ **Football Fan:** แฟนบอลตัวยง", "🎧 **Producer:** โปรดิวเซอร์หลักของวง"],
        "songs": ["KING KONG", "G.O.A.T", "VolKno"], 
        "covers": ["Humble", "Oll' Ready"]
    },
    {
        "name": "Asahi", "name_thai": "ฮามาดะ อาซาฮิ", "position": "Leader (2025), Visual", 
        "img": "asahi.jpg", "birthday": "20 Aug 2001", "height": "172 cm", "mbti": "INFP", 
        "name_korean": "아사히", "nickname": "Robot Sahi",
        "facts": ["🤖 **Robot Sahi:** ตลกหน้าตาย", "👑 **New Leader:** ผู้นำสายอาร์ต (2025)", "🎨 **Artist:** วาดรูปสวย ถ่ายรูปเก่ง", "🎹 **Composer:** เจ้าพ่อเพลง Ballad"],
        "songs": ["LAST NIGHT", "THANK YOU", "ORANGE"], 
        "covers": ["Lay Me Down", "Yamai"]
    }
]

# ====== HEADER & HERO ======
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">TREASURE</h1>
    <p class="hero-subtitle">REBOOT : THE NEW ERA 2025</p>
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

# ====== IMAGE MAP (GLASS) ======
group_img_path = "group.jpg" # ใช้ Path แบบ Root เพื่อรองรับ GitHub

img_b64 = get_img_as_base64(group_img_path)

if img_b64:
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
    st.error("❌ ไม่พบไฟล์รูป group.jpg ในโฟลเดอร์ Root")

# ====== POPUP MODAL (BIG & WIDE) ======
if "selected_member" in st.session_state:
    sel = st.session_state.selected_member
    
    @st.dialog(f"💎 {sel['name']}")
    def show_modal():
        c1, c2 = st.columns([1.5, 2.5])
        
        with c1:
            img_code = get_img_as_base64(sel['img'])
            if img_code:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:15px;">', unsafe_allow_html=True)
            else:
                st.info("No Image")
            
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
        img_code = get_img_as_base64(m['img'])
        if img_code:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)

st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
cols2 = st.columns(5)
for i in range(5):
    idx = i + 5
    with cols2[i]:
        m = members[idx]
        if st.button(f"{m['name']}", key=f"g2_{idx}", use_container_width=True):
            st.session_state.selected_member = m
            st.rerun()
        img_code = get_img_as_base64(m['img'])
        if img_code:
            st.markdown(f'<img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:10px;">', unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown("""
<div style="text-align:center; margin-top:50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); opacity:0.5; font-size:0.8rem;">
    TREASURE MAKER PROJECT 2025 | DESIGNED WITH STREAMLIT
</div>
""", unsafe_allow_html=True)