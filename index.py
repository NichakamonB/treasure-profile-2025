import streamlit as st
import base64
import os
import urllib.parse
import random
from typing import Dict, List, Optional
import warnings

# ============================================
# 📱 PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="TREASURE WORLD 2026", 
    layout="wide", 
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# ============================================
# 🖼️ IMAGE UTILITIES
# ============================================
@st.cache_data
def get_img_as_base64(file_path: str) -> str:
    """Load and encode image to base64 from a file path"""
    paths_to_check = [
        file_path,
        os.path.join("images", file_path),
        os.path.join(os.path.dirname(__file__), file_path),
        os.path.join(os.path.dirname(__file__), "images", file_path)
    ]
    
    for path in paths_to_check:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception as e:
                warnings.warn(f"Error reading {path}: {e}")
                continue
    return ""

def get_image_src(image_source: str, name_for_avatar: str = "Member") -> str:
    # 1. Try Local File
    b64 = get_img_as_base64(image_source)
    if b64:
        return f"data:image/jpeg;base64,{b64}"
    
    # 2. Try URL
    if image_source.startswith("http"):
        return image_source
        
    # 3. Fallback
    safe_name = urllib.parse.quote(name_for_avatar)
    return f"https://ui-avatars.com/api/?name={safe_name}&background=32E0C4&color=fff&size=400&font-size=0.33"

# ============================================
# 🌍 LANGUAGE SYSTEM
# ============================================
@st.cache_data
def get_ui_text() -> Dict:
    return {
        "th": {
            "sub": "LOVE PULSE : มินิอัลบั้มชุดที่ 3 | 2026",
            "touch": "แตะที่ตัวสมาชิกเพื่อดูประวัติ",
            "close": "ปิดหน้าต่าง",
            "tab1": "ประวัติ & สตอรี่",
            "tab2": "เพลงฮิต",
            "tab3": "คัฟเวอร์",
            "birth": "วันเกิด",
            "height": "ส่วนสูง",
            "select": "เลือกดูรายชื่อสมาชิก",
            "search": "ค้นหาสมาชิก",
            "favorite": "สมาชิกโปรด",
            "story_title": "เส้นทางสู่ดวงดาว",
            "facts_title": "เกร็ดน่ารู้",
            "rec_title": "✨ แนะนำสำหรับคุณ",
            "rec_playlist_1": "🎬 OFFICIAL M/V",
            "rec_playlist_2": "💎 TREASURE MAP",
            "error_member": "ไม่พบข้อมูลสมาชิก"
        },
        "en": {
            "sub": "LOVE PULSE : THE 3RD MINI ALBUM | 2026",
            "touch": "TOUCH MEMBER TO VIEW PROFILE",
            "close": "CLOSE PROFILE",
            "tab1": "STORY & FACTS",
            "tab2": "SONGS",
            "tab3": "COVERS",
            "birth": "BIRTH",
            "height": "HEIGHT",
            "select": "MEMBER SELECTOR",
            "search": "Search members",
            "favorite": "Favorites",
            "story_title": "THE STORY",
            "facts_title": "QUICK FACTS",
            "rec_title": "✨ Recommended",
            "rec_playlist_1": "🎬 OFFICIAL M/V",
            "rec_playlist_2": "💎 TREASURE MAP",
            "error_member": "Member not found"
        },
        "kr": {
            "sub": "LOVE PULSE : 세 번째 미니 앨범 | 2026",
            "touch": "멤버를 터치하여 프로필 보기",
            "close": "닫기",
            "tab1": "프로필 & 스토리",
            "tab2": "대표곡",
            "tab3": "커버곡",
            "birth": "생일",
            "height": "신장",
            "select": "멤버 선택",
            "search": "멤버 검색",
            "favorite": "즐겨찾기",
            "story_title": "스토리",
            "facts_title": "TMI",
            "rec_title": "✨ 추천",
            "rec_playlist_1": "🎬 공식 뮤직비디오",
            "rec_playlist_2": "💎 트레저맵",
            "error_member": "멤버를 찾을 수 없습니다"
        },
        "jp": {
            "sub": "LOVE PULSE : サード・ミニアルバム | 2026",
            "touch": "メンバーをタップしてプロフィールを見る",
            "close": "閉じる",
            "tab1": "プロフィール",
            "tab2": "代表曲",
            "tab3": "カバー",
            "birth": "誕生日",
            "height": "身長",
            "select": "メンバー選択",
            "search": "メンバー検索",
            "favorite": "お気に入り",
            "story_title": "ストーリー",
            "facts_title": "トリビア",
            "rec_title": "✨ おすすめ",
            "rec_playlist_1": "🎬 公式M/V",
            "rec_playlist_2": "💎 TREASURE MAP",
            "error_member": "メンバーが見つかりません"
        },
        "cn": {
            "sub": "LOVE PULSE : 第三张迷你专辑 | 2026",
            "touch": "点击成员查看资料",
            "close": "关闭",
            "tab1": "简介 & 故事",
            "tab2": "热门歌曲",
            "tab3": "翻唱",
            "birth": "生日",
            "height": "身高",
            "select": "选择成员",
            "search": "搜索成员",
            "favorite": "最爱",
            "story_title": "星路历程",
            "facts_title": "趣味档案",
            "rec_title": "✨ 推荐",
            "rec_playlist_1": "🎬 官方M/V",
            "rec_playlist_2": "💎 宝石盒综艺",
            "error_member": "未找到成员"
        }
    }

def initialize_session_state(members):
    if "lang" in st.query_params:
        st.session_state.lang_code = st.query_params["lang"]
    if 'lang_code' not in st.session_state:
        st.session_state.lang_code = "th"
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    if 'param_processed' not in st.session_state:
        st.session_state.param_processed = False

def set_language(code: str):
    st.session_state.lang_code = code
    st.session_state.param_processed = False

def toggle_favorite(member_name: str):
    if member_name in st.session_state.favorites:
        st.session_state.favorites.remove(member_name)
    else:
        st.session_state.favorites.append(member_name)

# ============================================
# 🎨 ENHANCED CSS
# ============================================
def inject_custom_css():
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Prompt:wght@300;500;700&family=Noto+Sans+KR:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');

    :root { --primary: #32E0C4; --glass: rgba(255, 255, 255, 0.05); --border: rgba(255, 255, 255, 0.1); --text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .stApp { background: radial-gradient(circle at 50% 10%, #1a2a3a 0%, #000000 90%); font-family: 'Prompt', 'Noto Sans KR', 'Noto Sans SC', sans-serif; color: white; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    header {visibility: visible !important; background: transparent !important;}
    [data-testid="stSidebarCollapsedControl"] { color: var(--primary) !important; background-color: rgba(0,0,0,0.5); border-radius: 50%; }
    
    section[data-testid="stSidebar"] { background-color: rgba(20, 25, 30, 0.95); border-right: 1px solid var(--border); }
    div[data-testid="stSidebarNav"] { display: none; }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; margin-top: 0 !important; max-width: 1400px !important; }
    div[data-testid="column"] .stButton button { background: transparent !important; border: none !important; font-size: 2rem !important; padding: 0px !important; margin: 0px !important; line-height: 1 !important; opacity: 0.4; transition: all 0.3s ease; }
    div[data-testid="column"] .stButton button:hover { transform: scale(1.3) !important; opacity: 1 !important; text-shadow: 0 0 20px rgba(50, 224, 196, 0.9); }
    
    .hero-container { text-align: center; margin-top: -20px; animation: fadeIn 1.5s ease-in-out; }
    .hero-title { font-family: 'Montserrat', sans-serif; font-size: clamp(3rem, 8vw, 5rem); font-weight: 900; letter-spacing: -3px; background: linear-gradient(135deg, #fff 0%, #32E0C4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 40px rgba(50, 224, 196, 0.4); margin: 0; line-height: 1.1; animation: glow 2s ease-in-out infinite alternate; }
    .hero-subtitle { font-size: clamp(0.9rem, 2vw, 1.2rem); color: #8899a6; letter-spacing: 3px; margin-top: 8px; text-transform: uppercase; }
    .social-bar { display: flex; justify-content: center; gap: 15px; margin-top: 25px; flex-wrap: wrap; }
    .social-btn { display: inline-flex; align-items: center; justify-content: center; width: 55px; height: 55px; border-radius: 50%; background: var(--glass); border: 2px solid var(--border); color: white; font-size: 1.6rem; text-decoration: none; transition: all 0.4s; backdrop-filter: blur(10px); }
    .social-btn:hover { background: rgba(50, 224, 196, 0.2); border-color: var(--primary); transform: translateY(-8px) scale(1.1); box-shadow: 0 8px 25px rgba(50, 224, 196, 0.5); }
    
    .stTextInput input { background: var(--glass) !important; border: 1px solid var(--border) !important; border-radius: 15px !important; color: white !important; padding: 12px 20px !important; }
    .stTextInput input:focus { border-color: var(--primary) !important; box-shadow: 0 0 20px rgba(50, 224, 196, 0.3) !important; }
    
    .map-frame { background: var(--glass); backdrop-filter: blur(15px); border: 1px solid var(--border); border-radius: 30px; padding: 15px; box-shadow: 0 30px 80px rgba(0,0,0,0.7); max-width: 1100px; margin: 1.5rem auto 3rem auto; position: relative; animation: slideUp 1s ease-out; }
    .main-image { width: 100%; border-radius: 20px; display: block; transition: transform 0.3s ease; }
    .map-frame:hover .main-image { transform: scale(1.02); }
    .hotspot { position: absolute; cursor: pointer; z-index: 10; border-radius: 50%; background: rgba(50, 224, 196, 0.02); border: 2px solid rgba(255, 255, 255, 0.3); transition: all 0.4s; }
    .hotspot:hover { border-color: var(--primary); background: rgba(50, 224, 196, 0.25); transform: scale(1.15); box-shadow: 0 0 30px rgba(50, 224, 196, 0.6); }
    
    .member-card-link { text-decoration: none !important; display: block; }
    .member-card-overlay { position: relative; border-radius: 15px; overflow: hidden; aspect-ratio: 3/4; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: all 0.3s ease; border: 2px solid rgba(255, 255, 255, 0.1); }
    .member-card-overlay:hover { transform: translateY(-5px) scale(1.03); border-color: var(--primary); box-shadow: 0 15px 30px rgba(50, 224, 196, 0.4); }
    .member-img-full { width: 100%; height: 100%; object-fit: cover; display: block; }
    .member-name-overlay { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 60%, transparent 100%); color: white; padding: 20px 5px 10px 5px; text-align: center; font-weight: 700; font-size: 1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8); letter-spacing: 0.5px; }
    
    .rec-card { background: var(--glass); border-radius: 12px; padding: 15px; margin-bottom: 20px; border: 1px solid var(--border); text-align: center; transition: all 0.3s ease; }
    .rec-card:hover { transform: translateY(-3px); border-color: var(--primary); background: rgba(50,224,196,0.1); }
    .rec-img { width: 100%; border-radius: 10px; margin-bottom: 10px; aspect-ratio: 16/9; object-fit: cover; }
    
    div[data-testid="stDialog"] div[role="dialog"] { width: 90vw !important; max-width: 1500px !important; background: rgba(15, 20, 25, 0.98) !important; border: 2px solid var(--primary) !important; border-radius: 25px !important; backdrop-filter: blur(20px) !important; }
    .profile-header { font-family: 'Montserrat', sans-serif; font-size: clamp(2.5rem, 5vw, 3.5rem); font-weight: 800; color: var(--primary); line-height: 1; text-shadow: 0 0 30px rgba(50, 224, 196, 0.5); }
    .profile-cn-name { font-size: clamp(1.2rem, 3vw, 1.8rem); color: #888; font-weight: 400; margin-left: 10px; }
    .profile-sub { font-size: clamp(1.1rem, 2.5vw, 1.5rem); color: rgba(255,255,255,0.85); margin-bottom: 25px; border-bottom: 2px solid var(--border); padding-bottom: 15px; }
    .stat-row { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; background: var(--glass); padding: 20px; border-radius: 15px; border: 1px solid var(--border); }
    .stat-item { text-align: center; flex: 1; }
    .stat-label { font-size: 0.85rem; color: #999; display: block; text-transform: uppercase; }
    .stat-val { font-size: 1.5rem; font-weight: 700; color: #fff; }
    
    .story-container { background: rgba(255, 255, 255, 0.03); border-radius: 16px; padding: 25px; border: 1px solid rgba(50, 224, 196, 0.15); position: relative; margin-top: 15px; margin-bottom: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
    .story-icon-header { position: absolute; top: -18px; left: 20px; background: #0e1117; padding: 5px 15px; border-radius: 20px; border: 1px solid rgba(50, 224, 196, 0.3); color: var(--primary); font-weight: bold; font-size: 0.9rem; letter-spacing: 1px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
    .story-content { color: #e0e0e0; line-height: 1.8; font-size: 1.05rem; font-weight: 300; }
    
    .facts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-top: 10px; }
    .fact-card-modern { background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 10px; text-align: center; transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100px; }
    .fact-card-modern:hover { background: rgba(50, 224, 196, 0.08); border-color: var(--primary); transform: translateY(-3px); }
    .fact-icon-modern { font-size: 1.8rem; margin-bottom: 8px; filter: drop-shadow(0 0 5px rgba(50, 224, 196, 0.4)); }
    .fact-label-modern { font-size: 0.7rem; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }
    .fact-value-modern { font-size: 0.95rem; color: #fff; font-weight: 600; line-height: 1.2; word-break: break-word; }
    
    .song-link { text-decoration: none; }
    .song-card { display: flex; align-items: center; justify-content: space-between; background: var(--glass); padding: 20px; border-radius: 12px; margin-bottom: 12px; border: 1px solid var(--border); transition: all 0.3s ease; }
    .song-card:hover { background: rgba(50, 224, 196, 0.15); border-color: var(--primary); transform: translateX(8px); }
    .song-title { color: white; font-weight: 600; font-size: 1.15rem; }
    .favorite-heart { position: absolute; top: 10px; right: 10px; font-size: 1.5rem; filter: drop-shadow(0 0 5px rgba(255, 0, 0, 0.5)); animation: heartbeat 1.5s infinite; z-index: 10; }
    
    @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideUp { from { opacity: 0; transform: translateY(50px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes glow { from { text-shadow: 0 0 20px rgba(50, 224, 196, 0.3); } to { text-shadow: 0 0 40px rgba(50, 224, 196, 0.7); } }
    @keyframes heartbeat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    
    @media (max-width: 768px) { .hero-title { font-size: 3rem !important; } .stat-row { flex-direction: column !important; gap: 10px !important; } div[data-testid="stDialog"] div[role="dialog"] { width: 95vw !important; } }
</style>
""", unsafe_allow_html=True)

# ============================================
# 📊 MEMBER DATA
# ============================================
@st.cache_data
def get_members_data() -> List[Dict]:
    return [
        {
            "name": "Hyunsuk", 
            "img": "hyunsuk.jpg",
            "birthday": "1999.04.21", "height": "171 cm", "mbti": "ENFP",
            "display_name": {"th": "ชเว ฮยอนซอก", "en": "Choi Hyunsuk", "kr": "최현석", "jp": "チェ・ヒョンソク", "cn": "崔玹硕"},
            "position": {"th": "แร็ปเปอร์, แดนซ์", "en": "Rapper, Dancer", "kr": "래퍼, 댄서", "jp": "ラッパー, ダンサー", "cn": "Rapper, 舞担"},
            "nickname": {"th": "Hedgehog", "en": "Hedgehog", "kr": "칠현석", "jp": "ヒョンソク", "cn": "脆现硕"},
            "history": {
                "th": "พี่ใหญ่ของวง เกิดที่คังนัม ได้รับแรงบันดาลใจจาก BIGBANG ผ่านรายการ MIXNINE (อันดับ 5) ปัจจุบันเป็นเสาหลักของวง (Former Leader 2020-2024)",
                "en": "Eldest member, born in Gangnam. Inspired by BIGBANG. MIXNINE rank 5. Former Leader (2020-2024).",
                "kr": "강남 출신 맏형. 빅뱅을 보고 꿈을 키움. 믹스나인 5위. 전 리더 (2020-2024).",
                "jp": "江南出身の最年長。BIGBANGに憧れる。MIXNINE 5位。元リーダー (2020-2024)。",
                "cn": "出生于江南的大哥。BIGBANG的粉丝。MIXNINE第5名。前队长 (2020-2024)。"
            },
            "facts": {
                "th": ["🦔 **English Name:** Danny Choi", "⚽ **Hobby:** ฟุตบอล, ช้อปปิ้ง", "7️⃣ **Fav Number:** 7"],
                "en": ["🦔 **English Name:** Danny Choi", "⚽ **Hobby:** Soccer, Shopping", "7️⃣ **Fav Number:** 7"],
                "kr": ["🦔 **영어 이름:** Danny Choi", "⚽ **취미:** 축구, 쇼핑", "7️⃣ **좋아하는 숫자:** 7"],
                "jp": ["🦔 **英語名:** Danny Choi", "⚽ **趣味:** サッカー, 買い物", "7️⃣ **好きな数字:** 7"],
                "cn": ["🦔 **英文名:** Danny Choi", "⚽ **爱好:** 足球, 购物", "7️⃣ **幸运数字:** 7"]
            },
            "songs": ["VolKno", "KING KONG"], "covers": ["Humble"]
        },
        {
            "name": "Jihoon", "img": "jihoon.jpg",
            "birthday": "2000.03.14", "height": "178 cm", "mbti": "ENTJ",
            "display_name": {"th": "พัค จีฮุน", "en": "Park Jihoon", "kr": "박지훈", "jp": "パク・ジフン", "cn": "朴志焄"},
            "position": {"th": "เมนแดนซ์, T5", "en": "Main Dancer, T5", "kr": "메인 댄서, T5", "jp": "メインダンサー, T5", "cn": "主舞, T5"},
            "nickname": {"th": "Hoonie", "en": "Hoonie", "kr": "후니", "jp": "フニ", "cn": "Hoonie"},
            "history": { 
                "th": "จากปูซาน เคยฝันอยากเป็นนักบิน ฝึกมา 4 ปี เป็นสมาชิกยูนิต T5 และอดีตลีดเดอร์ (2020-2024)",
                "en": "From Busan, dreamed of being a pilot. Trained 4 years. Member of T5 and former Leader (2020-2024).",
                "kr": "부산 출신, 파일럿이 꿈이었음. 4년 연습. T5 멤버이자 전 리더.",
                "jp": "釜山出身、パイロットが夢だった。練習生4年。T5メンバーで元リーダー。",
                "cn": "来自釜山，曾梦想成为飞行员。练习4年。T5成员及前队长。"
            },
            "facts": {
                "th": ["🐯 **English Name:** Jun Park", "✈️ **Dream:** นักบิน", "🔴 **Color:** Red"],
                "en": ["🐯 **English Name:** Jun Park", "✈️ **Dream:** Pilot", "🔴 **Color:** Red"],
                "kr": ["🐯 **영어 이름:** Jun Park", "✈️ **꿈:** 파일럿", "🔴 **색깔:** 빨강"],
                "jp": ["🐯 **英語名:** Jun Park", "✈️ **夢:** パイロット", "🔴 **色:** 赤"],
                "cn": ["🐯 **英文名:** Jun Park", "✈️ **梦想:** 飞行员", "🔴 **颜色:** 红色"]
            },
            "songs": ["The Way To", "MOVE"], "covers": ["Ko Ko Bop"]
        },
        {
            "name": "Yoshi", "img": "yoshi.jpg",
            "birthday": "2000.05.15", "height": "179 cm", "mbti": "INFP",
            "display_name": {"th": "คาเนโมโตะ โยชิโนริ", "en": "Kanemoto Yoshinori", "kr": "요시노리", "jp": "金本芳典", "cn": "金本芳典"},
            "position": {"th": "เมนแร็ปเปอร์", "en": "Main Rapper", "kr": "메인 래퍼", "jp": "メインラッパー", "cn": "主Rapper"},
            "nickname": {"th": "Dark Horse", "en": "Dark Horse", "kr": "다크호스", "jp": "ダークホース", "cn": "黑马"},
            "history": {
                "th": "เกิดที่โกเบ ญี่ปุ่น เป็นลูกครึ่งเกาหลี-ญี่ปุ่น รุ่นที่ 4 (Zainichi) ฝันอยากเป็นนักแข่งรถ",
                "en": "Born in Kobe, 4th gen Zainichi Korean. Dreamed of being a racer.",
                "kr": "고베 출신 재일교포 4세. 레이서가 꿈이었음.",
                "jp": "神戸出身の在日韓国人4世。レーサーになるのが夢だった。",
                "cn": "出生于神户的第四代在日韩裔。曾梦想成为赛车手。"
            },
            "facts": {
                "th": ["🐯 **English Name:** Jaden", "🏎️ **Dream:** นักแข่งรถ", "🎨 **Hobby:** Graffiti"],
                "en": ["🐯 **English Name:** Jaden", "🏎️ **Dream:** Racer", "🎨 **Hobby:** Graffiti"],
                "kr": ["🐯 **영어 이름:** Jaden", "🏎️ **꿈:** 레이서", "🎨 **취미:** 그래피티"],
                "jp": ["🐯 **英語名:** Jaden", "🏎️ **夢:** レーサー", "🎨 **趣味:** グラフィティ"],
                "cn": ["🐯 **英文名:** Jaden", "🏎️ **梦想:** 赛车手", "🎨 **爱好:** 涂鸦"]
            },
            "songs": ["STUPID", "KING KONG"], "covers": ["Fancy"]
        },
        {
            "name": "Junkyu", "img": "junkyu.jpg",
            "birthday": "2000.09.09", "height": "178 cm", "mbti": "INFJ",
            "display_name": {"th": "คิม จุนกยู", "en": "Kim Junkyu", "kr": "김준규", "jp": "キム・ジュンギュ", "cn": "金俊奎"},
            "position": {"th": "ลีดเดอร์ (2025+), T5", "en": "Leader (2025+), T5", "kr": "리더 (2025+), T5", "jp": "リーダー (2025+), T5", "cn": "队长 (2025+), T5"},
            "nickname": {"th": "Handsome Koala", "en": "Handsome Koala", "kr": "코알라", "jp": "コアラ", "cn": "帅气考拉"},
            "history": {
                "th": "อดีตนายแบบเด็ก รับตำแหน่ง Leader ใหม่ตั้งแต่ปี 2025 เป็นสมาชิกยูนิต T5",
                "en": "Former child model. New Leader since 2025. T5 Member.",
                "kr": "아역 모델 출신. 2025년부터 새 리더. T5 멤버.",
                "jp": "元子役モデル。2025年から新リーダー。T5メンバー。",
                "cn": "前童模。2025年起担任新队长。T5成员。"
            },
            "facts": {
                "th": ["🐨 **English Name:** David Kim", "🐱 **Pets:** Ruby, Aengdu", "👕 **Physique:** Physical Genius"],
                "en": ["🐨 **English Name:** David Kim", "🐱 **Pets:** Ruby, Aengdu", "👕 **Physique:** Physical Genius"],
                "kr": ["🐨 **영어 이름:** David Kim", "🐱 **반려묘:** 루비, 앵두", "👕 **피지컬:** 피지컬 천재"],
                "jp": ["🐨 **英語名:** David Kim", "🐱 **ペット:** Ruby, Aengdu", "👕 **体格:** フィジカル天才"],
                "cn": ["🐨 **英文名:** David Kim", "🐱 **宠物:** Ruby, Aengdu", "👕 **身材:** 脸蛋天才"]
            },
            "songs": ["MOVE", "YELLOW"], "covers": ["Latch"]
        },
        {
            "name": "Jaehyuk", "img": "jaehyuk.jpg",
            "birthday": "2001.07.23", "height": "178 cm", "mbti": "INFP",
            "display_name": {"th": "ยุน แจฮยอก", "en": "Yoon Jaehyuk", "kr": "윤재혁", "jp": "ユン・ジェヒョク", "cn": "尹材赫"},
            "position": {"th": "โวคอล, T5", "en": "Vocalist, T5", "kr": "보컬, T5", "jp": "ボーカル, T5", "cn": "副主唱, T5"},
            "nickname": {"th": "Chow Chow", "en": "Chow Chow", "kr": "윤다정", "jp": "ジェヒョク", "cn": "尹多情"},
            "history": {
                "th": "ถูกแมวมองจาก YG ทาบทามข้างถนน สมาชิก T5",
                "en": "Street-casted by YG. Member of T5.",
                "kr": "YG 길거리 캐스팅. T5 멤버.",
                "jp": "YGにスカウトされた。T5メンバー。",
                "cn": "YG街头星探发掘。T5成员。"
            },
            "facts": {
                "th": ["🦁 **English Name:** Kevin Yoon", "🤚 **Hand:** Left-handed", "💖 **Charm:** Sweet"],
                "en": ["🦁 **English Name:** Kevin Yoon", "🤚 **Hand:** Left-handed", "💖 **Charm:** Sweet"],
                "kr": ["🦁 **영어 이름:** Kevin Yoon", "🤚 **손:** 왼손잡이", "💖 **매력:** 다정함"],
                "jp": ["🦁 **英語名:** Kevin Yoon", "🤚 **利き手:** 左利き", "💖 **魅力:** 優しい"],
                "cn": ["🦁 **英文名:** Kevin Yoon", "🤚 **惯用手:** 左手", "💖 **魅力:** 温柔"]
            },
            "songs": ["MOVE", "Wonderland"], "covers": ["Ring Ring"]
        },
        {
            "name": "Asahi", "img": "asahi.jpg",
            "birthday": "2001.08.20", "height": "172 cm", "mbti": "INFP",
            "display_name": {"th": "ฮามาดะ อาซาฮิ", "en": "Hamada Asahi", "kr": "하마다 아사히", "jp": "浜田朝光", "cn": "滨田朝光"},
            "position": {"th": "ลีดเดอร์ (2025+), T5", "en": "Leader (2025+), T5", "kr": "리더 (2025+), T5", "jp": "リーダー (2025+), T5", "cn": "队长 (2025+), T5"},
            "nickname": {"th": "Robot", "en": "Robot", "kr": "로봇", "jp": "ロボット", "cn": "机器人"},
            "history": {
                "th": "จากโอซาก้า ชื่อแปลว่า 'แสงยามเช้า' รับตำแหน่ง Leader คู่กับจุนกยู (2025)",
                "en": "From Osaka. Name means 'Morning Sunshine'. Co-Leader (2025).",
                "kr": "오사카 출신. 이름 뜻은 '아침 햇살'. 공동 리더 (2025).",
                "jp": "大阪出身。名前の意味は「朝の光」。共同リーダー (2025)。",
                "cn": "来自大阪。名字意为“晨光”。共同队长 (2025)。"
            },
            "facts": {
                "th": ["🤖 **English Name:** Arthur", "⚽ **Hobby:** Football", "🎨 **Skill:** Art"],
                "en": ["🤖 **English Name:** Arthur", "⚽ **Hobby:** Football", "🎨 **Skill:** Art"],
                "kr": ["🤖 **영어 이름:** Arthur", "⚽ **취미:** 축구", "🎨 **특기:** 예술"],
                "jp": ["🤖 **英語名:** Arthur", "⚽ **趣味:** サッカー", "🎨 **特技:** アート"],
                "cn": ["🤖 **英文名:** Arthur", "⚽ **爱好:** 足球", "🎨 **特长:** 艺术"]
            },
            "songs": ["THANK YOU", "CLAP!"], "covers": ["Lay Me Down"]
        },
        {
            "name": "Doyoung", "img": "doyoung.jpg",
            "birthday": "2003.12.04", "height": "177 cm", "mbti": "ESTP",
            "display_name": {"th": "คิม โดยอง", "en": "Kim Doyoung", "kr": "김도영", "jp": "キム・ドヨン", "cn": "金道荣"},
            "position": {"th": "เมนแดนซ์, T5", "en": "Main Dancer, T5", "kr": "메인 댄서, T5", "jp": "メインダンサー, T5", "cn": "主舞, T5"},
            "nickname": {"th": "Dobby", "en": "Dobby", "kr": "도비", "jp": "ドビ", "cn": "Dobby"},
            "history": {
                "th": "เริ่มเต้นตั้งแต่ ป.3 สมาชิก T5 และมีความสามารถด้านสเก็ตบอร์ด",
                "en": "Started dancing in 3rd grade. T5 Member. Loves skateboarding.",
                "kr": "초3 때 춤 시작. T5 멤버. 스케이트보드 매니아.",
                "jp": "小3からダンスを始める。T5メンバー。スケボー好き。",
                "cn": "三年级开始跳舞。T5成员。热爱滑板。"
            },
            "facts": {
                "th": ["🛹 **English Name:** Sam", "✝️ **Name:** Nicholas (Baptismal)", "🍳 **Skill:** Cooking"],
                "en": ["🛹 **English Name:** Sam", "✝️ **Name:** Nicholas (Baptismal)", "🍳 **Skill:** Cooking"],
                "kr": ["🛹 **영어 이름:** Sam", "✝️ **세례명:** 니콜라스", "🍳 **특기:** 요리"],
                "jp": ["🛹 **英語名:** Sam", "✝️ **洗礼名:** ニコラス", "🍳 **特技:** 料理"],
                "cn": ["🛹 **英文名:** Sam", "✝️ **洗礼名:** Nicholas", "🍳 **特长:** 烹饪"]
            },
            "songs": ["WONDERLAND", "MOVE"], "covers": ["Freedom"]
        },
        {
            "name": "Haruto", "img": "haruto.jpg",
            "birthday": "2004.04.05", "height": "183.2 cm", "mbti": "INFP",
            "display_name": {"th": "วาตานาเบะ ฮารุโตะ", "en": "Watanabe Haruto", "kr": "와타나베 하루토", "jp": "渡辺温斗", "cn": "渡边温斗"},
            "position": {"th": "เมนแร็ปเปอร์", "en": "Main Rapper", "kr": "메인 래퍼", "jp": "メインラッパー", "cn": "主Rapper"},
            "nickname": {"th": "Ruto", "en": "Ruto", "kr": "루토", "jp": "ルト", "cn": "Ruto"},
            "history": {
                "th": "จากฟุกุโอกะ ส่วนสูง 183.2 ซม. สูงที่สุดในวง วิชวลและแร็ปเปอร์เสียงต่ำ",
                "en": "From Fukuoka. Tallest (183.2cm). Visual & Low-tone rapper.",
                "kr": "후쿠오카 출신. 최장신 (183.2cm). 비주얼 & 로우톤 래퍼.",
                "jp": "福岡出身。最長身 (183.2cm)。ビジュアル担当。",
                "cn": "来自福冈。最高 (183.2cm)。门面 & 低音Rapper。"
            },
            "facts": {
                "th": ["🦋 **English Name:** Travis", "📏 **Height:** 183.2 cm", "📝 **Skill:** Lyrics"],
                "en": ["🦋 **English Name:** Travis", "📏 **Height:** 183.2 cm", "📝 **Skill:** Lyrics"],
                "kr": ["🦋 **영어 이름:** Travis", "📏 **신장:** 183.2 cm", "📝 **특기:** 작사"],
                "jp": ["🦋 **英語名:** Travis", "📏 **身長:** 183.2 cm", "📝 **特技:** 作詞"],
                "cn": ["🦋 **英文名:** Travis", "📏 **身高:** 183.2 cm", "📝 **特长:** 作词"]
            },
            "songs": ["G.O.A.T", "KING KONG"], "covers": ["FLASH"]
        },
        {
            "name": "Jeongwoo", "img": "jeongwoo.jpg",
            "birthday": "2004.09.28", "height": "181 cm", "mbti": "ISFP",
            "display_name": {"th": "พัค จองอู", "en": "Park Jeongwoo", "kr": "박정우", "jp": "パク・ジョンウ", "cn": "朴炡禹"},
            "position": {"th": "เมนโวคอล", "en": "Main Vocalist", "kr": "메인 보컬", "jp": "メインボーカル", "cn": "主唱"},
            "nickname": {"th": "Vocal King", "en": "Vocal King", "kr": "보컬 킹", "jp": "ボーカルキング", "cn": "声乐天才"},
            "history": {
                "th": "เด็กหนุ่มจากอิกซาน ถนัดซ้าย จบจาก SOPA",
                "en": "From Iksan. Left-handed. SOPA Graduate.",
                "kr": "익산 출신. 왼손잡이. 서공예 졸업.",
                "jp": "益山出身。左利き。SOPA卒業。",
                "cn": "来自益山。左撇子。毕业于SOPA。"
            },
            "facts": {
                "th": ["🐺 **English Name:** Justin", "🤚 **Hand:** Left-handed", "🎤 **Role:** Main Vocal"],
                "en": ["🐺 **English Name:** Justin", "🤚 **Hand:** Left-handed", "🎤 **Role:** Main Vocal"],
                "kr": ["🐺 **영어 이름:** Justin", "🤚 **손:** 왼손잡이", "🎤 **역할:** 메인보컬"],
                "jp": ["🐺 **英語名:** Justin", "🤚 **利き手:** 左利き", "🎤 **役割:** メインボーカル"],
                "cn": ["🐺 **英文名:** Justin", "🤚 **惯用手:** 左手", "🎤 **担当:** 主唱"]
            },
            "songs": ["PARADISE", "DARARI"], "covers": ["Superstar"]
        },
        {
            "name": "Junghwan", "img": "junghwan.jpg",
            "birthday": "2005.02.18", "height": "180.3 cm", "mbti": "ENFP-T",
            "display_name": {"th": "โซ จองฮวาน", "en": "So Junghwan", "kr": "소정환", "jp": "ソ・ジョンファン", "cn": "苏庭焕"},
            "position": {"th": "น้องเล็ก, T5", "en": "Maknae, T5", "kr": "막내, T5", "jp": "末っ子, T5", "cn": "忙内, T5"},
            "nickname": {"th": "Super King Cow Baby", "en": "Super King Cow Baby", "kr": "소해금", "jp": "ジョンファン", "cn": "超级牛宝宝"},
            "history": {
                "th": "อดีตสมาชิก K-TIGERS ฝันอยากเป็นนักเทควันโด ชอบฤดูหนาว",
                "en": "Former K-TIGERS. Dreamed of Taekwondo. Loves Winter.",
                "kr": "전 K-TIGERS. 태권도 선수가 꿈. 겨울을 좋아함.",
                "jp": "元K-TIGERS。テコンドー選手が夢。冬が好き。",
                "cn": "前K-TIGERS成员。梦想成为跆拳道运动员。喜欢冬天。"
            },
            "facts": {
                "th": ["🐮 **English Name:** John", "🥋 **Team:** K-TIGERS", "❄️ **Season:** Winter"],
                "en": ["🐮 **English Name:** John", "🥋 **Team:** K-TIGERS", "❄️ **Season:** Winter"],
                "kr": ["🐮 **영어 이름:** John", "🥋 **팀:** K-TIGERS", "❄️ **계절:** 겨울"],
                "jp": ["🐮 **英語名:** John", "🥋 **チーム:** K-TIGERS", "❄️ **季節:** 冬"],
                "cn": ["🐮 **英文名:** John", "🥋 **队伍:** K-TIGERS", "❄️ **季节:** 冬天"]
            },
            "songs": ["B.O.M.B", "MOVE"], "covers": ["Lie"]
        }
    ]

def render_sidebar(members: List[Dict], t: Dict, lang: str):
    """Render the sidebar with recommendations"""
    with st.sidebar:
        st.markdown(f"<h2 style='color:#32E0C4; text-align:center;'>{t['rec_title']}</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top:0;'>", unsafe_allow_html=True)
        
        # 1. Recommended Playlist (Official M/V)
        st.markdown(f"<div style='text-align:center; margin-bottom:10px; color:#aaa; font-size:0.9rem;'>{t['rec_playlist_1']}</div>", unsafe_allow_html=True)
        
        playlist_url_1 = "https://www.youtube.com/watch?v=zjJs3I4hsCg&list=PLG4U66ceLh82hyGL6sE6Cp1nG2uNLtlAm&pp=0gcJCbUEOCosWNin"
        cover_img_1 = "https://i.ytimg.com/vi/zjJs3I4hsCg/hqdefault.jpg"
        
        st.markdown(f"""
        <a href="{playlist_url_1}" target="_blank" style="text-decoration:none;">
            <div class="rec-card" style="padding:0; overflow:hidden; position:relative;">
                <img src="{cover_img_1}" style="width:100%; display:block; opacity:0.9; transition:0.3s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.9">
                <div style="position:absolute; bottom:0; left:0; width:100%; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); color:#32E0C4; padding:10px; font-weight:bold; font-size:0.9rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">
                    ▶ WATCH M/V
                </div>
            </div>
        </a>
        <div style="text-align:center; font-size:0.8rem; color:#888; margin-top:5px;">
            TREASURE - M/V 💎
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Recommended Playlist (T-MAP)
        st.markdown(f"<div style='text-align:center; margin-bottom:10px; color:#aaa; font-size:0.9rem;'>{t['rec_playlist_2']}</div>", unsafe_allow_html=True)
        
        playlist_url_2 = "https://www.youtube.com/playlist?list=PLG4U66ceLh80BCE_NxXdEsltXlgpchO6R"
        cover_img_2 = "https://i.ytimg.com/vi/M4oBygBkgGQ/hqdefault.jpg"
        
        st.markdown(f"""
        <a href="{playlist_url_2}" target="_blank" style="text-decoration:none;">
            <div class="rec-card" style="padding:0; overflow:hidden; position:relative;">
                <img src="{cover_img_2}" style="width:100%; display:block; opacity:0.9; transition:0.3s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.9">
                <div style="position:absolute; bottom:0; left:0; width:100%; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); color:#32E0C4; padding:10px; font-weight:bold; font-size:0.9rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">
                    ▶ TREASURE MAP
                </div>
            </div>
        </a>
        <div style="text-align:center; font-size:0.8rem; color:#888; margin-top:5px;">
            Variety Show 🤣
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 🎯 MAIN APPLICATION
# ============================================
def main():
    members = get_members_data()
    initialize_session_state(members)
    inject_custom_css()
    
    ui_text = get_ui_text()
    lang = st.session_state.lang_code
    t = ui_text[lang]
    
    # Sidebar
    render_sidebar(members, t, lang)
    
    # ====== FLAG SELECTOR ======
    c_spacer, c_th, c_en, c_kr, c_jp, c_cn = st.columns([10, 0.7, 0.7, 0.7, 0.7, 0.7])
    with c_th: st.button("🇹🇭", on_click=set_language, args=("th",), key="f_th")
    with c_en: st.button("🇬🇧", on_click=set_language, args=("en",), key="f_en")
    with c_kr: st.button("🇰🇷", on_click=set_language, args=("kr",), key="f_kr")
    with c_jp: st.button("🇯🇵", on_click=set_language, args=("jp",), key="f_jp")
    with c_cn: st.button("🇨🇳", on_click=set_language, args=("cn",), key="f_cn")
    
    # ====== HERO SECTION ======
    st.markdown(f"""
    <div class="hero-container">
        <h1 class="hero-title">TREASURE</h1>
        <p class="hero-subtitle">{t['sub']}</p>
        <div class="social-bar">
            <a href="https://www.instagram.com/yg_treasure_official/" target="_blank" class="social-btn">📸</a>
            <a href="https://www.facebook.com/OfficialTreasure" target="_blank" class="social-btn">📘</a>
            <a href="https://weverse.io/treasure/feed" target="_blank" class="social-btn">🍀</a>
            <a href="https://www.youtube.com/@TREASURE" target="_blank" class="social-btn">📺</a>
            <a href="https://twitter.com/treasuremembers" target="_blank" class="social-btn">🐦</a>
        </div>
    </div><br>
    """, unsafe_allow_html=True)
    
    # ====== SEARCH BAR ======
    search_query = st.text_input(label="search", placeholder=f"🔍 {t['search']}...", label_visibility="collapsed")
    filtered_members = [m for m in members if search_query.lower() in m['display_name'][lang].lower() or search_query.lower() in m['name'].lower()] if search_query else members
    
    # ====== QUERY PARAMETER HANDLER ======
    if "id" in st.query_params and not st.session_state.param_processed:
        try:
            idx = int(st.query_params["id"])
            if 0 <= idx < len(members):
                st.session_state.selected_member = members[idx]
                st.session_state.param_processed = True
                st.query_params.clear()
                st.rerun()
        except ValueError:
            st.query_params.clear()
    
    # ====== IMAGE MAP (URL Placeholder) ======
    group_img_src = get_image_src("group.jpg") 
    if "placeholder" in group_img_src:
         group_img_src = "https://kprofiles.com/wp-content/uploads/2020/01/TREASURE-Concept-Photo-1-scaled.jpg"

    st.markdown(f"""
    <div class="map-frame"><img src="{group_img_src}" class="main-image"></div>
    <p style="text-align:center;color:#666;font-size:0.9rem;margin-top:-10px;">{t['touch']}</p>
    """, unsafe_allow_html=True)
    
    # ====== MODAL DIALOG ======
    if "selected_member" in st.session_state:
        show_member_modal(st.session_state.selected_member, t, lang)
    
    # ====== MEMBER GRID ======
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.session_state.favorites:
        st.markdown(f"<h4 style='text-align:center; color:#32E0C4; margin-bottom:20px;'>💖 {t['favorite']}</h4>", unsafe_allow_html=True)
        fav_members = [m for m in members if m['name'] in st.session_state.favorites]
        render_member_grid(fav_members, t, lang, show_heart=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"<h4 style='text-align:center; color:#32E0C4; margin-bottom:20px; opacity:0.8;'>{t['select']}</h4>", unsafe_allow_html=True)
    if not filtered_members:
        st.info(f"🔍 {t['error_member']}")
    else:
        render_member_grid(filtered_members, t, lang)
    
    # ====== FOOTER ======
    st.markdown("""
    <div style="text-align:center; margin-top:60px; padding: 25px; border-top: 1px solid rgba(255,255,255,0.1); opacity:0.6; font-size:0.85rem;">
        <p style="margin:0;">💎 TREASURE MAKER PROJECT 2026</p>
    </div>
    """, unsafe_allow_html=True)

def render_member_grid(members: List[Dict], t: Dict, lang: str, show_heart: bool = False):
    cols_per_row = 5
    for i in range(0, len(members), cols_per_row):
        cols = st.columns(min(cols_per_row, len(members) - i))
        for j, col in enumerate(cols):
            with col:
                real_idx = i + j
                m = members[real_idx]
                img_src = get_image_src(m['img'], m['name']) 
                heart_html = f'<div class="favorite-heart">❤️</div>' if show_heart else ''
                st.markdown(f'''<div style="position: relative;"><a href="?id={real_idx}&lang={lang}" target="_self" class="member-card-link"><div class="member-card-overlay">{heart_html}<img src="{img_src}" class="member-img-full" alt="{m['display_name'][lang]}"><div class="member-name-overlay">{m['display_name'][lang]}</div></div></a></div>''', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

def show_member_modal(sel: Dict, t: Dict, lang: str):
    @st.dialog(f"💎 {sel['name']}", width="large")
    def modal_content():
        c1, c2 = st.columns([1.5, 2.5])
        with c1:
            st.markdown(f'<img src="{get_image_src(sel["img"])}" style="width:100%; border-radius:15px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); margin-bottom: 20px;">', unsafe_allow_html=True)
            st.markdown(f"""<div class="stat-row"><div class="stat-item"><span class="stat-label">{t['birth']}</span><span class="stat-val">{sel['birthday']}</span></div><div class="stat-item"><span class="stat-label">{t['height']}</span><span class="stat-val">{sel['height']}</span></div></div><div class="stat-row"><div class="stat-item"><span class="stat-label">MBTI</span><span class="stat-val">{sel['mbti']}</span></div></div><div style="text-align:center; margin-top:-10px; color:#32E0C4; font-weight:900; font-size:1.3rem;">"{sel['nickname'][lang]}"</div>""", unsafe_allow_html=True)
            fav_text = "Remove" if sel['name'] in st.session_state.favorites else "Add to Favorites"
            if st.button(f"❤️ {fav_text}", use_container_width=True, key=f"fav_{sel['name']}"):
                toggle_favorite(sel['name'])
                st.rerun()
        with c2:
            cn_name_html = f'<span class="profile-cn-name">{sel["display_name"].get("cn", "")}</span>'
            st.markdown(f"<div class='profile-header'>{sel['display_name'][lang]}{cn_name_html}</div><div class='profile-sub'>{sel['position'][lang]}</div>", unsafe_allow_html=True)
            tab1, tab2, tab3 = st.tabs([f"📖 {t['tab1']}", f"🎵 {t['tab2']}", f"🎤 {t['tab3']}"])
            with tab1:
                st.markdown(f"""<div class="story-container"><div class="story-icon-header">✨ {t['story_title']}</div><div class="story-content">{sel.get('history', {}).get(lang, "-")}</div></div>""", unsafe_allow_html=True)
                st.markdown(f"<h4 style='color:#32E0C4; margin-bottom:10px; margin-top:20px;'>{t['facts_title']}</h4>", unsafe_allow_html=True)
                facts_html = '<div class="facts-grid">'
                for fact_str in sel.get('facts', {}).get(lang, []):
                    try:
                        parts = fact_str.split("**")
                        if len(parts) >= 3:
                            facts_html += f"""<div class="fact-card-modern"><div class="fact-icon-modern">{parts[0].strip()}</div><div class="fact-label-modern">{parts[1].replace(":", "").strip()}</div><div class="fact-value-modern">{parts[2].strip()}</div></div>"""
                        else:
                            facts_html += f'<div class="fact-card-modern"><div class="fact-value-modern">{fact_str}</div></div>'
                    except:
                         facts_html += f'<div class="fact-card-modern"><div class="fact-value-modern">{fact_str}</div></div>'
                facts_html += '</div>'
                st.markdown(facts_html, unsafe_allow_html=True)
            with tab2:
                for s in sel.get('songs', []): st.markdown(f"""<a href="https://www.youtube.com/results?search_query=TREASURE+{sel['name']}+{s}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎵 {s}</span><span>↗</span></div></a>""", unsafe_allow_html=True)
            with tab3:
                for c in sel.get('covers', []): st.markdown(f"""<a href="https://www.youtube.com/results?search_query=TREASURE+{sel['name']}+{c}+cover" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎧 {c}</span><span>↗</span></div></a>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"✕ {t['close']}", use_container_width=True, type="primary"):
            del st.session_state.selected_member
            st.rerun()
    modal_content()

if __name__ == "__main__":
    main()