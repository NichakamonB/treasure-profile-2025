import streamlit as st
import base64
import os
import urllib.parse

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="TREASURE WORLD 2026", 
    layout="wide", 
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

# --- ฟังก์ชันแปลงรูป ---
def get_img_as_base64(file_path):
    paths_to_check = [file_path, os.path.join("images", file_path)]
    for path in paths_to_check:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

# ====== 🌍 LANGUAGE SYSTEM ======
if 'lang_code' not in st.session_state:
    st.session_state.lang_code = "th"

def set_language(code):
    st.session_state.lang_code = code

# ====== 🎨 CSS ======
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Prompt:wght@300;500;700&family=Noto+Sans+KR:wght@400;700&display=swap');

    :root { --primary: #32E0C4; --glass: rgba(255, 255, 255, 0.05); }

    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a2a3a 0%, #000000 90%);
        font-family: 'Prompt', 'Noto Sans KR', sans-serif; color: white;
    }
    
    #MainMenu, header, footer {visibility: hidden;}
    section[data-testid="stSidebar"] { display: none; }

    /* --- ดันเนื้อหาขึ้นชิดขอบบน --- */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        margin-top: 0 !important;
    }
    
    /* ปุ่มธงชาติ (ขวาบน) */
    div[data-testid="column"] .stButton button {
        background: transparent !important; border: none !important;
        font-size: 2rem !important; padding: 0px !important; margin: 0px !important;
        line-height: 1 !important; min-height: 0px !important; opacity: 0.6; transition: all 0.2s;
    }
    div[data-testid="column"] .stButton button:hover {
        transform: scale(1.25) !important; opacity: 1 !important; text-shadow: 0 0 15px rgba(50, 224, 196, 0.8);
    }
    
    /* HERO SECTION */
    .hero-container { text-align: center; margin-top: -20px; animation: fadeIn 1.5s ease-in-out; }
    .hero-title {
        font-family: 'Montserrat', sans-serif; font-size: 5rem; font-weight: 900; letter-spacing: -3px;
        background: linear-gradient(to right, #fff, #32E0C4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(50, 224, 196, 0.4); margin: 0; line-height: 1.1;
    }
    .hero-subtitle { font-size: 1.2rem; color: #8899a6; letter-spacing: 4px; margin-top: 5px; text-transform: uppercase; }

    /* SOCIAL MEDIA BUTTONS */
    .social-bar {
        display: flex; justify-content: center; gap: 15px; margin-top: 20px;
    }
    .social-btn {
        display: inline-flex; align-items: center; justify-content: center;
        width: 50px; height: 50px; border-radius: 50%;
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2);
        color: white; font-size: 1.5rem; text-decoration: none; transition: 0.3s;
        backdrop-filter: blur(5px);
    }
    .social-btn:hover {
        background: rgba(50, 224, 196, 0.2); border-color: #32E0C4;
        transform: translateY(-5px); box-shadow: 0 5px 15px rgba(50, 224, 196, 0.4);
    }
    .social-label { font-size: 0.8rem; margin-top: 5px; color: #aaa; }

    /* IMAGE MAP */
    .map-frame {
        background: var(--glass); backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 30px; padding: 10px; box-shadow: 0 30px 60px rgba(0,0,0,0.6);
        max-width: 1100px; margin: 1rem auto 3rem auto; position: relative;
    }
    .main-image { width: 100%; border-radius: 20px; display: block; }
    .hotspot { position: absolute; cursor: pointer; z-index: 10; border-radius: 50%; background: rgba(255, 255, 255, 0.01); border: 2px solid rgba(255, 255, 255, 0.4); transition: all 0.3s ease; }
    .hotspot:hover { border-color: #32E0C4; background: rgba(50, 224, 196, 0.15); transform: scale(1.1); }

    /* WIDE DIALOG */
    div[data-testid="stDialog"] div[role="dialog"] {
        width: 85vw !important; max-width: 1400px !important;
        background: rgba(15, 20, 25, 0.98) !important;
        border: 1px solid #32E0C4 !important; border-radius: 25px !important;
    }

    /* PROFILE UI */
    .profile-header { font-family: 'Montserrat', sans-serif; font-size: 3.5rem; font-weight: 800; color: #32E0C4; margin-bottom: 5px; line-height: 1; text-shadow: 0 0 20px rgba(50, 224, 196, 0.3); }
    .profile-sub { font-size: 1.5rem; color: rgba(255,255,255,0.8); margin-bottom: 25px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; }
    .stat-row { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); }
    .stat-item { text-align: center; width: 100%; }
    .stat-label { font-size: 0.85rem; color: #888; display: block; margin-bottom: 5px; }
    .stat-val { font-size: 1.4rem; font-weight: 700; color: #fff; font-family: 'Montserrat', sans-serif; }
    .fact-box { background: linear-gradient(90deg, rgba(50, 224, 196, 0.05) 0%, transparent 100%); border-left: 5px solid #32E0C4; padding: 15px 20px; border-radius: 8px; margin-bottom: 12px; font-size: 1.1rem; line-height: 1.6; }
    .song-link { text-decoration: none; }
    .song-card { display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.03); padding: 20px 25px; border-radius: 12px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.1); transition: 0.3s; }
    .song-card:hover { background: rgba(50, 224, 196, 0.15); border-color: #32E0C4; transform: scale(1.02); }
    .song-title { color: white; font-weight: 600; font-size: 1.1rem; }
    
    /* ปุ่มกดใน Grid Member */
    div[data-testid="column"] .stButton button[kind="secondary"] {
         border-radius: 15px !important; height: 55px; font-weight: bold !important; 
         background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; 
         color: #ccc !important; opacity: 1 !important; font-size: 1rem !important;
    }
    
    @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
""", unsafe_allow_html=True)

# ====== 🎌 FLAG SELECTOR ======
c_spacer, c_th, c_en, c_kr, c_jp = st.columns([12, 0.7, 0.7, 0.7, 0.7])
with c_th: st.button("🇹🇭", on_click=set_language, args=("th",), key="f_th")
with c_en: st.button("🇬🇧", on_click=set_language, args=("en",), key="f_en")
with c_kr: st.button("🇰🇷", on_click=set_language, args=("kr",), key="f_kr")
with c_jp: st.button("🇯🇵", on_click=set_language, args=("jp",), key="f_jp")

# Language Logic
lang = st.session_state.lang_code
ui = {
    "th": {"sub": "LOVE PULSE : มินิอัลบั้มชุดที่ 3 | 2026", "touch": "แตะที่ตัวสมาชิกเพื่อดูประวัติ", "close": "ปิดหน้าต่าง", "tab1": "ประวัติ", "tab2": "เพลงฮิต", "tab3": "คัฟเวอร์", "birth": "วันเกิด", "height": "ส่วนสูง", "select": "เลือกดูรายชื่อสมาชิก"},
    "en": {"sub": "LOVE PULSE : THE 3RD MINI ALBUM | 2026", "touch": "TOUCH MEMBER TO VIEW PROFILE", "close": "CLOSE PROFILE", "tab1": "FACTS", "tab2": "SONGS", "tab3": "COVERS", "birth": "BIRTH", "height": "HEIGHT", "select": "MEMBER SELECTOR"},
    "kr": {"sub": "LOVE PULSE : 세 번째 미니 앨범 | 2026", "touch": "멤버를 터치하여 프로필 보기", "close": "닫기", "tab1": "프로필", "tab2": "대표곡", "tab3": "커버곡", "birth": "생일", "height": "신장", "select": "멤버 선택"},
    "jp": {"sub": "LOVE PULSE : サード・ミニアルバム | 2026", "touch": "メンバーをタップしてプロフィールを見る", "close": "閉じる", "tab1": "プロフィール", "tab2": "代表曲", "tab3": "カバー", "birth": "誕生日", "height": "身長", "select": "メンバー選択"}
}
t = ui[lang]

# ====== HERO SECTION & SOCIAL LINKS ======
st.markdown(f"""
<div class="hero-container">
    <h1 class="hero-title">TREASURE</h1>
    <p class="hero-subtitle">{t['sub']}</p>
    
<div class="social-bar">
<a href="https://www.instagram.com/yg_treasure_official/" target="_blank" class="social-btn" title="Instagram">📸</a>
<a href="https://www.facebook.com/OfficialTreasure" target="_blank" class="social-btn" title="Facebook">📘</a>
<a href="https://weverse.io/treasure/feed" target="_blank" class="social-btn" title="Weverse">🍀</a>
<a href="https://www.youtube.com/@TREASURE" target="_blank" class="social-btn" title="YouTube">📺</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ====== DATA ======
members = [
    {
        "name": "Jeongwoo", "img": "jeongwoo.jpg", "birthday": "2004.09.28", "height": "181 cm", "mbti": "ISFP",
        "display_name": {"th": "พัค จองอู", "en": "Park Jeongwoo", "kr": "박정우", "jp": "パク・ジョンウ"},
        "position": {"th": "เมนโวคอล", "en": "Main Vocalist", "kr": "메인 보컬", "jp": "メインボーカル"},
        "nickname": {"th": "Vocal King", "en": "Vocal King", "kr": "보컬 킹", "jp": "ボーカルキング"},
        "facts": {
            "th": ["🐺 **Vocal Genius:** ฉายา 'Vocal King' แห่งอิกซาน เสียงทรงพลัง", "🏫 **Education:** จบจาก SOPA เอกดนตรีปฏิบัติ", "🤣 **Mood Maker:** ตลกธรรมชาติและเป็นกันเอง"],
            "en": ["🐺 **Vocal Genius:** Known as the 'Vocal King' of Iksan.", "🏫 **Education:** Graduated from SOPA.", "🤣 **Mood Maker:** Naturally funny and friendly."],
            "kr": ["🐺 **보컬 천재:** 익산의 '보컬 킹'으로 불립니다.", "🏫 **학력:** 서공예 실용음악과 졸업.", "🤣 **분위기 메이커:** 팀의 분위기 메이커."],
            "jp": ["🐺 **天才:** 益山の「ボーカルキング」。", "🏫 **学歴:** SOPA卒業。", "🤣 **ムードメーカー:** 自然と面白い性格。"]
        },
        "songs": ["PARADISE", "LAST NIGHT", "HOLD IT IN"], "covers": ["Superstar", "Weight in Gold"]
    },
    {
        "name": "Haruto", "img": "haruto.jpg", "birthday": "2004.04.05", "height": "185 cm", "mbti": "INFP",
        "display_name": {"th": "วาตานาเบะ ฮารุโตะ", "en": "Watanabe Haruto", "kr": "와타나베 하루토", "jp": "渡辺温斗"},
        "position": {"th": "เมนแร็ปเปอร์", "en": "Main Rapper", "kr": "메인 래퍼", "jp": "メインラッパー"},
        "nickname": {"th": "Face Genius", "en": "Face Genius", "kr": "얼굴 천재", "jp": "顔天才"},
        "facts": {
            "th": ["🦋 **Visual:** Face Genius + Low Tone Rap สุดเท่", "📏 **Tallest:** สูงที่สุดในวง (185 cm)", "📝 **Writer:** แต่งเนื้อแร็ปเองเกือบทุกเพลง"],
            "en": ["🦋 **Visual:** Face Genius with deep low-tone rap.", "📏 **Tallest:** Tallest member (185 cm).", "📝 **Writer:** Writes his own rap lyrics."],
            "kr": ["🦋 **비주얼:** 얼굴 천재 + 매력적인 로우 톤 랩.", "📏 **신장:** 팀 내 최장신 (185cm).", "📝 **작사:** 랩 메이킹 참여."],
            "jp": ["🦋 **ビジュアル:** 顔天才 + 低音ラップ。", "📏 **身長:** チーム最長身 (185cm)。", "📝 **作詞:** ラップ作詞に参加。"]
        },
        "songs": ["PARADISE", "G.O.A.T", "VolKno"], "covers": ["FLASH (Solo)", "Dat $tick"]
    },
    {
        "name": "Jihoon", "img": "jihoon.jpg", "birthday": "2000.03.14", "height": "178 cm", "mbti": "ENTJ",
        "display_name": {"th": "พัค จีฮุน", "en": "Park Jihoon", "kr": "박지훈", "jp": "パク・ジフン"},
        "position": {"th": "เมนแดนซ์", "en": "Main Dancer", "kr": "메인 댄서", "jp": "メインダンサー"},
        "nickname": {"th": "Hoonie", "en": "Hoonie", "kr": "후니", "jp": "フニ"},
        "facts": {
            "th": ["🐯 **Leadership:** อดีต Leader ที่เข้มแข็ง", "🎤 **MC:** สกิลวาไรตี้และพิธีกรดีเยี่ยม", "💃 **Power:** ไลน์เต้นแข็งแรง ล็อคท่าเป๊ะ"],
            "en": ["🐯 **Leadership:** Reliable former leader.", "🎤 **MC:** Great MC and variety skills.", "💃 **Power:** Powerful dance lines."],
            "kr": ["🐯 **리더십:** 든든한 전 리더.", "🎤 **MC:** 뛰어난 진행 능력.", "💃 **파워:** 파워풀한 춤선."],
            "jp": ["🐯 **リーダー:** 頼れる元リーダー。", "🎤 **MC:** 優れた進行能力。", "💃 **パワー:** パワフルなダンス。"]
        },
        "songs": ["PARADISE", "LAST NIGHT", "THE WAY TO"], "covers": ["Song Goes Off", "Ko Ko Bop"]
    },
    {
        "name": "Yoshi", "img": "yoshi.jpg", "birthday": "2000.05.15", "height": "179 cm", "mbti": "INFP",
        "display_name": {"th": "คาเนโมโตะ โยชิโนริริ", "en": "Kanemoto Yoshinori", "kr": "요시노리", "jp": "金本芳典"},
        "position": {"th": "เมนแร็ปเปอร์", "en": "Main Rapper", "kr": "메인 래퍼", "jp": "メインラッパー"},
        "nickname": {"th": "Dark Horse", "en": "Dark Horse", "kr": "다크호스", "jp": "ダークホース"},
        "facts": {
            "th": ["🐯 **Rap Style:** แร็ปเสียงสูง ดุดัน (High Tone)", "🎨 **Art:** รักศิลปะ วาดรูปสวย แต่งตัวเก่ง", "🎵 **Composer:** แต่งเพลง 'STUPID'"],
            "en": ["🐯 **Rap Style:** Aggressive high-tone rap.", "🎨 **Art:** Loves art and fashion.", "🎵 **Composer:** Composed 'STUPID'."],
            "kr": ["🐯 **랩:** 하이톤의 강렬한 랩.", "🎨 **예술:** 미술과 패션을 사랑함.", "🎵 **작곡:** 자작곡 'STUPID'."],
            "jp": ["🐯 **ラップ:** ハイトーンラップ。", "🎨 **芸術:** アートとファッションが好き。", "🎵 **作曲:** 「STUPID」を作曲。"]
        },
        "songs": ["STUPID", "PARADISE", "VolKno"], "covers": ["Fancy", "Be Like Me"]
    },
    {
        "name": "Junghwan", "img": "junghwan.jpg", "birthday": "2005.02.18", "height": "180 cm", "mbti": "ENFP-T",
        "display_name": {"th": "โซ จองฮวาน", "en": "So Junghwan", "kr": "소정환", "jp": "ソ・ジョンファン"},
        "position": {"th": "น้องเล็ก, เมนแดนซ์", "en": "Maknae, Dancer", "kr": "막내, 댄서", "jp": "末っ子, ダンサー"},
        "nickname": {"th": "King Cow Baby", "en": "King Cow Baby", "kr": "소해금", "jp": "ジョンファン"},
        "facts": {
            "th": ["🐮 **Maknae:** น้องเล็กตัวโตและแข็งแรง", "🥋 **Athlete:** อดีตนักกีฬาเทควันโด K-Tigers", "🍩 **Foodie:** รักการกินเป็นชีวิตจิตใจ"],
            "en": ["🐮 **Maknae:** Giant baby maknae.", "🥋 **Athlete:** Former K-Tigers Taekwondo.", "🍩 **Foodie:** Loves eating donuts."],
            "kr": ["🐮 **막내:** 자이언트 막내.", "🥋 **운동:** K-Tigers 태권도 출신.", "🍩 **먹방:** 먹는 것을 좋아함."],
            "jp": ["🐮 **末っ子:** ジャイアントマンネ。", "🥋 **運動:** 元K-Tigersテコンドー。", "🍩 **グルメ:** 食べることが大好き。"]
        },
        "songs": ["PARADISE", "CLAP!", "B.O.M.B"], "covers": ["Supermarket Flowers", "Lie"]
    },
    {
        "name": "Junkyu", "img": "junkyu.jpg", "birthday": "2000.09.09", "height": "178 cm", "mbti": "INFJ",
        "display_name": {"th": "คิม จุนกยู", "en": "Kim Junkyu", "kr": "김준규", "jp": "キム・ジュンギュ"},
        "position": {"th": "ลีดเดอร์ (2025)", "en": "Leader (2025)", "kr": "리더 (2025)", "jp": "リーダー (2025)"},
        "nickname": {"th": "Handsome Koala", "en": "Handsome Koala", "kr": "코알라", "jp": "コアラ"},
        "facts": {
            "th": ["🐨 **Unique Voice:** เสียงเอกลักษณ์ (YG Style)", "👑 **New Leader:** ผู้นำวงคนใหม่ (เริ่มปี 2025)", "🎵 **Hit Maker:** แต่งเพลงเก่ง (MOVE, BETTER)"],
            "en": ["🐨 **Unique Voice:** Unique YG-style voice.", "👑 **New Leader:** New leader starting 2025.", "🎵 **Hit Maker:** Composed MOVE, BETTER."],
            "kr": ["🐨 **음색:** 유니크한 YG 스타일 음색.", "👑 **리더:** 2025년 신임 리더.", "🎵 **작곡:** MOVE, BETTER 작곡."],
            "jp": ["🐨 **歌声:** ユニークな歌声。", "👑 **リーダー:** 2025年の新リーダー。", "🎵 **作曲:** MOVE, BETTERを作曲。"]
        },
        "songs": ["LAST NIGHT", "MOVE", "BETTER"], "covers": ["Latch", "Beautiful"]
    },
    {
        "name": "Doyoung", "img": "doyoung.jpg", "birthday": "2003.12.04", "height": "177 cm", "mbti": "ESTP",
        "display_name": {"th": "คิม โดยอง", "en": "Kim Doyoung", "kr": "김도영", "jp": "キム・ドヨン"},
        "position": {"th": "เมนแดนซ์", "en": "Main Dancer", "kr": "메인 댄서", "jp": "メインダンサー"},
        "nickname": {"th": "Dobby", "en": "Dobby", "kr": "도비", "jp": "ドビ"},
        "facts": {
            "th": ["🛹 **Skater:** เจ้าชายสเก็ตบอร์ด", "🕺 **Clean Dance:** ไลน์เต้นคมและสะอาดที่สุด", "🍳 **Chef:** ทำอาหารและอบขนมเก่งมาก"],
            "en": ["🛹 **Skater:** Loves skateboarding.", "🕺 **Clean Dance:** Precise dance lines.", "🍳 **Chef:** Good at cooking/baking."],
            "kr": ["🛹 **스케이트:** 스케이트보드 매니아.", "🕺 **춤:** 깔끔한 춤선.", "🍳 **요리:** 요리와 베이킹 실력자."],
            "jp": ["🛹 **スケボー:** スケボー好き。", "🕺 **ダンス:** キレイなダンスライン。", "🍳 **料理:** 料理と製菓が得意。"]
        },
        "songs": ["PARADISE", "WONDERLAND", "B.L.T"], "covers": ["Babushka Boi", "Freedom"]
    },
    {
        "name": "Jaehyuk", "img": "jaehyuk.jpg", "birthday": "2001.07.23", "height": "178 cm", "mbti": "INFP",
        "display_name": {"th": "ยุน แจฮยอก", "en": "Yoon Jaehyuk", "kr": "윤재혁", "jp": "ユン・ジェヒョク"},
        "position": {"th": "โวคอล", "en": "Vocalist", "kr": "보컬", "jp": "ボーカル"},
        "nickname": {"th": "Chow Chow", "en": "Chow Chow", "kr": "윤다정", "jp": "ジェヒョク"},
        "facts": {
            "th": ["🦁 **Casting:** ถูกจีบทุกค่ายใหญ่เพราะหน้าตาดี", "🥰 **Sweet:** อบอุ่น ใส่ใจคนรอบข้าง", "🤚 **Lefty:** ถนัดมือซ้าย"],
            "en": ["🦁 **Casting:** Street-casted by top agencies.", "🥰 **Sweet:** Warm and caring personality.", "🤚 **Lefty:** He is left-handed."],
            "kr": ["🦁 **캐스팅:** 대형 기획사 길거리 캐스팅.", "🥰 **성격:** 다정다감한 성격.", "🤚 **왼손잡이:** 왼손잡이임."],
            "jp": ["🦁 **スカウト:** 大手事務所からスカウト。", "🥰 **性格:** 優しくて温かい。", "🤚 **左利き:** 左利きである。"]
        },
        "songs": ["LAST NIGHT", "MOVE", "Wonderland"], "covers": ["Ring Ring", "My Type"]
    },
    {
        "name": "Hyunsuk", "img": "hyunsuk.jpg", "birthday": "1999.04.21", "height": "171 cm", "mbti": "ENFP",
        "display_name": {"th": "ชเว ฮยอนซอก", "en": "Choi Hyunsuk", "kr": "최현석", "jp": "チェ・ヒョンソク"},
        "position": {"th": "แร็ปเปอร์, แดนซ์", "en": "Rapper, Dancer", "kr": "래퍼, 댄서", "jp": "ラッパー, ダンサー"},
        "nickname": {"th": "Hedgehog", "en": "Hedgehog", "kr": "칠현석", "jp": "ヒョンソク"},
        "facts": {
            "th": ["🦔 **Pillar:** พี่ใหญ่และอดีต Leader", "👗 **Fashion:** แต่งตัวจัดจ้านที่สุด", "🎧 **Producer:** โปรดิวเซอร์หลักของวง"],
            "en": ["🦔 **Pillar:** Eldest and main producer.", "👗 **Fashion:** True fashionista.", "🎧 **Producer:** Produces many songs."],
            "kr": ["🦔 **기둥:** 맏형이자 메인 프로듀서.", "👗 **패션:** 패셔니스타.", "🎧 **프로듀서:** 다수의 곡 프로듀싱."],
            "jp": ["🦔 **柱:** 最年長＆メインプロデューサー。", "👗 **ファッション:** ファッショニスタ。", "🎧 **PD:** 多くの曲をプロデュース。"]
        },
        "songs": ["PARADISE", "G.O.A.T", "VolKno"], "covers": ["Humble", "Oll' Ready"]
    },
    {
        "name": "Asahi", "img": "asahi.jpg", "birthday": "2001.08.20", "height": "172 cm", "mbti": "INFP",
        "display_name": {"th": "ฮามาดะ อาซาฮิ", "en": "Hamada Asahi", "kr": "하마다 아사히", "jp": "浜田朝光"},
        "position": {"th": "ลีดเดอร์ (2025)", "en": "Leader (2025)", "kr": "리더 (2025)", "jp": "リーダー (2025)"},
        "nickname": {"th": "Robot", "en": "Robot", "kr": "로봇", "jp": "ロボット"},
        "facts": {
            "th": ["🤖 **Robot:** ตลกหน้าตาย", "👑 **New Leader:** ผู้นำสายอาร์ต (2025)", "🎹 **Composer:** เจ้าพ่อเพลง Ballad"],
            "en": ["🤖 **Robot:** Funny with a poker face.", "👑 **New Leader:** Artistic leader (2025).", "🎹 **Composer:** Ballad genius."],
            "kr": ["🤖 **로봇:** 무표정 개그의 달인.", "👑 **리더:** 2025년 예술적 리더.", "🎹 **작곡:** 발라드 천재."],
            "jp": ["🤖 **ロボット:** 無表情で面白い。", "👑 **リーダー:** 2025年の新リーダー。", "🎹 **作曲:** バラードの天才。"]
        },
        "songs": ["LAST NIGHT", "THANK YOU", "ORANGE"], "covers": ["Lay Me Down", "Yamai"]
    }
]

# ====== LOGIC ======
if "id" in st.query_params:
    try:
        idx = int(st.query_params["id"])
        if 0 <= idx < len(members):
            st.session_state.selected_member = members[idx]
            st.query_params.clear() 
    except: pass

# ====== IMAGE MAP ======
group_img_path = "group.jpg"
img_b64 = get_img_as_base64(group_img_path)

if img_b64:
    st.markdown(f"""
    <div class="map-frame">
        <img src="data:image/jpeg;base64,{img_b64}" class="main-image">
        <a href="?id=0" target="_self" class="hotspot" style="left:6%;top:15%;width:13%;height:35%;"></a>
        <a href="?id=1" target="_self" class="hotspot" style="left:21%;top:15%;width:13%;height:35%;"></a>
        <a href="?id=2" target="_self" class="hotspot" style="left:36%;top:15%;width:13%;height:35%;"></a>
        <a href="?id=3" target="_self" class="hotspot" style="left:51%;top:15%;width:13%;height:35%;"></a>
        <a href="?id=4" target="_self" class="hotspot" style="left:66%;top:15%;width:13%;height:35%;"></a>
        <a href="?id=5" target="_self" class="hotspot" style="left:81%;top:15%;width:13%;height:35%;"></a>
        <a href="?id=6" target="_self" class="hotspot" style="left:17%;top:55%;width:15%;height:40%;"></a>
        <a href="?id=7" target="_self" class="hotspot" style="left:34%;top:55%;width:15%;height:40%;"></a>
        <a href="?id=8" target="_self" class="hotspot" style="left:51%;top:55%;width:15%;height:40%;"></a>
        <a href="?id=9" target="_self" class="hotspot" style="left:69%;top:55%;width:15%;height:40%;"></a>
    </div>
    <p style="text-align:center;color:#666;font-size:0.8rem;margin-top:-10px;letter-spacing:1px;">{t['touch']}</p>
    """, unsafe_allow_html=True)
else:
    st.error("❌ Error: group.jpg not found.")

# ====== POPUP MODAL ======
if "selected_member" in st.session_state:
    sel = st.session_state.selected_member
    
    @st.dialog(f"💎 {sel['name']}")
    def show_modal():
        c1, c2 = st.columns([1.5, 2.5])
        
        with c1:
            img_code = get_img_as_base64(sel['img'])
            if img_code:
                st.markdown(f'<img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-row">
                <div class="stat-item"><span class="stat-label">{t['birth']}</span><span class="stat-val">{sel['birthday']}</span></div>
                <div class="stat-item"><span class="stat-label">{t['height']}</span><span class="stat-val">{sel['height']}</span></div>
                <div class="stat-item"><span class="stat-label">MBTI</span><span class="stat-val">{sel['mbti']}</span></div>
            </div>
            <div style="text-align:center; margin-top:-15px; color:#32E0C4; font-weight:900; font-size:1.2rem;">
                "{sel['nickname'][lang]}"
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"<div class='profile-header'>{sel['display_name'][lang]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='profile-sub'>{sel['position'][lang]}</div>", unsafe_allow_html=True)
            
            tab1, tab2, tab3 = st.tabs([f"🔥 {t['tab1']}", f"🎵 {t['tab2']}", f"🎤 {t['tab3']}"])
            
            with tab1:
                facts = sel['facts'][lang] 
                for f in facts:
                    st.markdown(f"<div class='fact-box'>{f}</div>", unsafe_allow_html=True)
            
            with tab2:
                for s in sel.get('songs', []):
                    query = urllib.parse.quote(f"TREASURE {sel['name']} {s} MV")
                    st.markdown(f"""<a href="https://www.youtube.com/results?search_query={query}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎵 {s}</span><span>↗</span></div></a>""", unsafe_allow_html=True)
            
            with tab3:
                for c in sel.get('covers', []):
                    query = urllib.parse.quote(f"TREASURE {sel['name']} {c} Cover")
                    st.markdown(f"""<a href="https://www.youtube.com/results?search_query={query}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎧 {c}</span><span>↗</span></div></a>""", unsafe_allow_html=True)

        if st.button(t['close'], use_container_width=True):
            del st.session_state.selected_member
            st.rerun()
    
    show_modal()

# ====== MEMBER GRID ======
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align:center; color:#32E0C4; letter-spacing:2px; margin-bottom:20px; opacity:0.7;'>{t['select']}</h4>", unsafe_allow_html=True)

cols1 = st.columns(5)
for i in range(5):
    with cols1[i]:
        m = members[i]
        if st.button(f"{m['display_name'][lang]}", key=f"g1_{i}", use_container_width=True):
            st.session_state.selected_member = m
            st.rerun()
        img_code = get_img_as_base64(m['img'])
        if img_code: st.markdown(f'<img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:12px; margin-bottom:10px;">', unsafe_allow_html=True)

st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
cols2 = st.columns(5)
for i in range(5):
    idx = i + 5
    with cols2[i]:
        m = members[idx]
        if st.button(f"{m['display_name'][lang]}", key=f"g2_{idx}", use_container_width=True):
            st.session_state.selected_member = m
            st.rerun()
        img_code = get_img_as_base64(m['img'])
        if img_code: st.markdown(f'<img src="data:image/jpeg;base64,{img_code}" style="width:100%; border-radius:12px; margin-bottom:10px;">', unsafe_allow_html=True)

# ====== FOOTER ======
st.markdown("""
<div style="text-align:center; margin-top:50px; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); opacity:0.5; font-size:0.8rem;">
    TREASURE MAKER PROJECT 2026 | DESIGNED WITH STREAMLIT
</div>
""", unsafe_allow_html=True)