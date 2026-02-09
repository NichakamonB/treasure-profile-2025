import streamlit as st
import base64
import os
import urllib.parse
import random
import json
import uuid
import gspread  # <--- เพิ่มตัวนี้
from google.oauth2.service_account import Credentials
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# ============================================
# 📱 PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="TREASURE WORLD 2026",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.youtube.com/@TREASURE',
        'Report a bug': None,
        'About': "💎 TREASURE Official Fan Application 2026 - Created with ❤️ by TEUME"
    }
)

# ============================================
# 🔧 CONFIGURATION
# ============================================
class AppConfig:
    DEFAULT_LANGUAGE = "th"
    SUPPORTED_LANGUAGES = ["th", "en", "kr", "jp", "cn"]
    COLS_PER_ROW = 5
    PREFERENCES_FILE = "user_preferences.json"

# ============================================
# 💾 USER PREFERENCES MANAGER
# ============================================
class UserPreferences:
    def __init__(self, pref_file: str = AppConfig.PREFERENCES_FILE):
        self.pref_file = Path(pref_file)
    
    def load_all(self) -> dict:
        try:
            if self.pref_file.exists():
                with open(self.pref_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_all(self, data: dict) -> bool:
        try:
            with open(self.pref_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def load_favorites(self) -> List[str]:
        data = self.load_all()
        return data.get('favorites', [])
    
    def save_favorites(self, favorites: List[str]) -> bool:
        data = self.load_all()
        data['favorites'] = favorites
        return self.save_all(data)
    
    def load_theme(self) -> str:
        data = self.load_all()
        return data.get('theme', 'dark')
    
    def save_theme(self, theme: str) -> bool:
        data = self.load_all()
        data['theme'] = theme
        return self.save_all(data)
    
# ============================================
# 💬 COMMENT SYSTEM (GSPREAD VERSION - FIX)
# ============================================
class CommentSystem:
    def __init__(self):
        self.sheet = None
        try:
            # 1. เชื่อมต่อโดยใช้ gspread (ไม่ง้อ st-gsheets)
            # ดึงข้อมูลจาก secrets.toml
            if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                secrets = st.secrets["connections"]["gsheets"]
                creds_info = secrets["service_account_info"]
                sheet_url = secrets["spreadsheet"]
                
                # กำหนดสิทธิ์
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
                
                # สร้าง Credential
                creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
                client = gspread.authorize(creds)
                
                # เปิด Google Sheet
                self.sheet = client.open_by_url(sheet_url).sheet1
            else:
                # กรณีรันครั้งแรกแล้วยังไม่ได้สร้าง secrets.toml
                pass 
                
        except Exception as e:
            st.error(f"Database Connection Error: {str(e)}")

    def load_comments(self) -> List[Dict]:
        if not self.sheet: return []
        try:
            # ดึงข้อมูลทั้งหมดมาเป็น List of Dicts โดยตรง
            return self.sheet.get_all_records()
        except:
            return []

    def add_comment(self, name, member, message, owner_id):
        if not self.sheet: 
            st.error("Cannot connect to Database")
            return
        
        try:
            # เตรียมข้อมูล (เรียงตามคอลัมน์ใน Google Sheet)
            # 1:id, 2:owner_id, 3:timestamp, 4:name, 5:member, 6:message, 7:avatar
            new_row = [
                str(uuid.uuid4()), 
                str(owner_id),     
                datetime.now().strftime("%Y-%m-%d %H:%M"), 
                name,              
                member,            
                message,           
                random.choice(["💎", "💙", "🐯", "🐨", "🐰", "🦋", "🐺", "🐮", "🦔", "🤖"]) 
            ]
            
            # แทรกบรรทัดใหม่ที่แถว 2 (ต่อจากหัวตาราง)
            self.sheet.insert_row(new_row, 2)
        except Exception as e:
            st.error(f"Save Error: {str(e)}")

    def delete_comment(self, comment_id):
        if not self.sheet: return
        try:
            # ค้นหา Cell ที่มี ID นี้
            cell = self.sheet.find(comment_id)
            if cell:
                self.sheet.delete_rows(cell.row)
        except:
            pass

    def edit_comment(self, comment_id, new_message):
        if not self.sheet: return
        try:
            # ค้นหา Cell ที่มี ID นี้
            cell = self.sheet.find(comment_id)
            if cell:
                # แก้ไข Column ที่ 6 (Message) และ 3 (Timestamp)
                self.sheet.update_cell(cell.row, 6, new_message) 
                self.sheet.update_cell(cell.row, 3, datetime.now().strftime("%Y-%m-%d %H:%M") + " (Edited)")
        except:
            pass

        

def render_cheer_board(t: Dict, members: List[Dict]):
    comment_sys = CommentSystem()
    
    # Initialize State
    if 'editing_id' not in st.session_state:
        st.session_state.editing_id = None

    # ดึง User ID ปัจจุบัน (ต้องมีใน session_state จาก initialize_session_state)
    current_user_id = st.session_state.get('user_session_id', '')

    # --- ส่วนหัวข้อ ---
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: var(--primary); text-shadow: 0 0 20px rgba(50,224,196,0.5);">{t.get('cheer_title', 'CHEER BOARD')}</h1>
        <p style="color: var(--secondary-text);">{t.get('cheer_desc', 'Send love to TREASURE')}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- INPUT FORM ---
    if st.session_state.editing_id is None:
        with st.container():
            st.markdown('<div style="background: var(--glass); padding: 20px; border-radius: 15px; border: 1px solid var(--primary);">', unsafe_allow_html=True)
            
            with st.form("cheer_form", clear_on_submit=True):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    is_anon = st.session_state.get("chk_anon", False)
                    if is_anon:
                        val_name = t.get('anon_name', "Teume")
                        st.text_input(t.get('form_name', "Name"), value=val_name, disabled=True, key="input_name_disabled")
                        final_name = val_name
                    else:
                        user_name = st.text_input(t.get('form_name', "Name"), placeholder="Teume...", key="input_name_enabled")
                        final_name = user_name
                    st.checkbox(t.get('anon_label', "Send Anonymously"), key="chk_anon")

                with col2:
                    dev_option = t.get('select_dev', "To: Developer")
                    options = [t.get('select_all', "To: TREASURE")] + [m['name'] for m in members] + [dev_option]
                    member_select = st.selectbox(t.get('form_tag', "Tag Member"), options)
                
                msg_input = st.text_area(t.get('form_msg', "Message"), placeholder="Write something nice...", height=100)
                
                submitted = st.form_submit_button(t.get('btn_send', "Send"), use_container_width=True)
                
                if submitted:
                    if final_name and msg_input:
                        # ส่ง current_user_id ไปบันทึกด้วย
                        comment_sys.add_comment(final_name, member_select, msg_input, current_user_id)
                        st.success(t.get('success_msg', "Sent!"))
                        st.rerun()
                    else:
                        st.warning("Please fill in all fields")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- DISPLAY COMMENTS ---
    st.markdown(f"<h3 style='margin-top: 40px; color: var(--primary); border-bottom: 1px solid var(--border); padding-bottom: 10px;'>{t.get('recent_comments', 'Recent Comments')}</h3>", unsafe_allow_html=True)
    
    is_admin = st.session_state.get('is_admin_active', False)

    comments = comment_sys.load_comments()
    
    if not comments:
        st.info("No comments yet. Be the first one! 💎")
    else:
        # CSS สำหรับปุ่มเล็ก
        st.markdown("""
        <style>
            .small-btn button {
                padding: 0px 5px !important;
                font-size: 0.75rem !important;
                min-height: 0px !important;
                height: 28px !important;
                line-height: 1 !important;
                border: 1px solid var(--border) !important;
                background-color: rgba(255,255,255,0.05) !important;
            }
            .small-btn button:hover {
                border-color: var(--primary) !important;
                color: var(--primary) !important;
                background-color: rgba(50, 224, 196, 0.1) !important;
            }
        </style>
        """, unsafe_allow_html=True)

        for i, c in enumerate(comments):
            c_id = c.get('id', str(i))
            owner_id = c.get('owner_id', '')
            
            is_dev_msg = "Developer" in c.get('member', '') or "ผู้พัฒนา" in c.get('member', '') or "开发者" in c.get('member', '')
            border_color = "#FFD700" if is_dev_msg else "var(--primary)"

            # ตรวจสอบสิทธิ์: เป็น Admin หรือ เจ้าของข้อความ
            is_owner = (owner_id == current_user_id) and (current_user_id != '')
            can_manage = is_admin or is_owner

            # --- EDIT MODE ---
            if st.session_state.editing_id == c_id and can_manage:
                with st.container():
                    st.markdown(f'<div style="background:var(--glass); padding:15px; border-radius:12px; border:2px solid {border_color}; margin-bottom:15px;">', unsafe_allow_html=True)
                    st.caption(f"Editing...")
                    edit_text = st.text_area("Edit", value=c.get('message', ''), key=f"edit_area_{c_id}", label_visibility="collapsed")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(t.get('btn_save_edit', "Save"), key=f"save_{c_id}", use_container_width=True, type="primary"):
                            comment_sys.edit_comment(c_id, edit_text)
                            st.session_state.editing_id = None
                            st.rerun()
                    with c2:
                        if st.button(t.get('btn_cancel', "Cancel"), key=f"cancel_{c_id}", use_container_width=True):
                            st.session_state.editing_id = None
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # --- VIEW MODE ---
            else:
                with st.container():
                    # 1. ส่วนเนื้อหาข้อความ
                    # ถ้ามีสิทธิ์จัดการ (can_manage) เราจะปิด border ด้านล่าง เพื่อให้เชื่อมกับกล่องปุ่ม
                    bottom_style = "border-bottom: none; border-bottom-left-radius: 0; border-bottom-right-radius: 0; margin-bottom: 0px;" if can_manage else "border-bottom: 1px solid var(--border); border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; margin-bottom: 15px;"
                    
                    st.markdown(f"""
                    <div style="
                        background: var(--glass); 
                        padding: 15px 15px 5px 15px;
                        border-top-left-radius: 12px;
                        border-top-right-radius: 12px;
                        border-left: 4px solid {border_color};
                        border-right: 1px solid var(--border);
                        border-top: 1px solid var(--border);
                        {bottom_style}
                    ">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <div style="font-weight: bold; color: {border_color}; font-size: 0.9rem;">
                                {c.get('avatar', '💎')} {c.get('name', 'Teume')}
                                <span style="font-size: 0.75rem; color: #888; font-weight: normal;"> ➤ {c.get('member', 'TREASURE')}</span>
                            </div>
                            <div style="font-size: 0.7rem; color: #666;">{c.get('timestamp', '')}</div>
                        </div>
                        <div style="color: var(--text-color); font-size: 0.95rem; line-height: 1.4; white-space: pre-wrap;">{c.get('message', '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 2. ส่วนปุ่ม (แสดงเฉพาะถ้ามีสิทธิ์)
                    if can_manage:
                        st.markdown(f"""
                        <div style="
                            background: var(--glass);
                            padding: 0px 10px 10px 10px;
                            border-bottom-left-radius: 12px;
                            border-bottom-right-radius: 12px;
                            border-left: 4px solid {border_color};
                            border-right: 1px solid var(--border);
                            border-bottom: 1px solid var(--border);
                            margin-bottom: 15px;
                        ">
                        """, unsafe_allow_html=True)
                        
                        # ใช้ Columns จัดปุ่มไปขวาสุด (8 ส่วนว่าง : 1 ปุ่ม : 1 ปุ่ม)
                        c1, c2, c3 = st.columns([8, 1, 1])
                        
                        with c2:
                            st.markdown('<div class="small-btn">', unsafe_allow_html=True)
                            if st.button("✏️", key=f"ed_{c_id}", help="Edit"):
                                st.session_state.editing_id = c_id
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with c3:
                            st.markdown('<div class="small-btn">', unsafe_allow_html=True)
                            if st.button("🗑️", key=f"del_{c_id}", help="Delete"):
                                comment_sys.delete_comment(c_id)
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True) # ปิด div กล่องปุ่ม


# ============================================
# 🔐 ADMIN MODAL
# ============================================
@st.dialog("🔐 Admin Login")
def admin_login_modal():
    st.write("Enter Admin Password / กรุณาใส่รหัสผ่าน")
    password = st.text_input("Password", type="password", key="modal_password_input") # เปลี่ยน key เพื่อความชัวร์
    
    if st.button("Login", use_container_width=True, type="primary"):
        if password == "teume123":  # รหัสผ่าน
            st.session_state.is_admin_active = True
            st.success("Access Granted! ✅")
            st.rerun()
        else:
            st.error("Incorrect Password ❌")

# ============================================
# 🖼️ IMAGE UTILITIES
# ============================================
@st.cache_data(ttl=3600)
def get_img_as_base64(file_path: str) -> str:
    primary_paths = [os.path.join("images", file_path), os.path.join(os.path.dirname(__file__), "images", file_path)]
    for path in primary_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                continue
    return ""

def get_image_src(image_source: str, name_for_avatar: str = "Member") -> str:
    try:
        if image_source and not image_source.startswith("http"):
            b64 = get_img_as_base64(image_source)
            if b64: return f"data:image/jpeg;base64,{b64}"
        if image_source and image_source.startswith("http"):
            return image_source
        safe_name = urllib.parse.quote(name_for_avatar)
        return f"https://ui-avatars.com/api/?name={safe_name}&background=32E0C4&color=fff&size=400&font-size=0.33"
    except Exception:
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
            "tab4": "สถิติ",
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
            "error_member": "ไม่พบข้อมูลสมาชิก",
            "stats": "สถิติทั้งหมด",
            "total_members": "สมาชิก",
            "your_favorites": "รายการโปรดของคุณ",
            "total_songs": "เพลงทั้งหมด",
            "random_member": "🎲 สุ่มสมาชิก",
            "theme": "เปลี่ยนธีม",
            "light": "☀️ สว่าง",
            "dark": "🌙 มืด",
            "birthday_countdown": "🎂 นับถอยหลังวันเกิด",
            "days": "วัน",
            "add_favorite": "💖 เพิ่มเป็นสมาชิกโปรด",
            "remove_favorite": "❤️ ลบออกจากรายการโปรด",
            "added_favorite": "เพิ่มเป็นสมาชิกโปรดแล้ว! ❤️",
            "removed_favorite": "ลบออกจากรายการโปรดแล้ว",
            "loading": "กำลังโหลด...",
            "tab_group": "เกี่ยวกับวง",
            "debut_date": "วันที่เดบิวต์",
            "fandom": "ชื่อแฟนคลับ",
            "origin": "จุดกำเนิด",
            "shows": "รายการวาไรตี้",
            "albums": "ผลงานเด่น",
            "group_desc": "TREASURE เป็นบอยแบนด์จากค่าย YG Entertainment ที่ก่อตั้งผ่านรายการเซอร์ไววัล 'YG Treasure Box' โดดเด่นด้วยพลังการแสดงและดนตรีที่หลากหลาย",
            "award_title": "รางวัลและความสำเร็จ",
            "award_desc": "🏆 Rookie of the Year (2020)\n🏆 MAMA Worldwide Fans' Choice\n🌏 'HELLO' Asia Tour Sold Out",
            "menu_home": "🏠 หน้าหลัก / สมาชิก",
            "menu_about": "🏢 เกี่ยวกับวง TREASURE",
            "menu_cheer": "💬 ส่งกำลังใจ / Fan Zone",
            "cheer_title": "💎 TEUME CHEER BOARD",
            "cheer_desc": "ส่งข้อความให้กำลังใจเมมเบอร์ที่คุณรัก!ถึงแม้น้องๆ อาจจะไม่ได้มาอ่านด้วยตัวเองทันที แต่การเขียนข้อความดีๆก็เป็นพลังบวกให้กับด้อม",
            "form_name": "ชื่อของคุณ (Your Name)",
            "form_tag": "เมนของคุณ / ส่งถึงใคร?",
            "form_msg": "ข้อความ (Message)",
            "btn_send": "🚀 ส่งข้อความ",
            "recent_comments": "ข้อความล่าสุด",
            "select_all": "💙 ถึง: TREASURE (วง)",
            "success_msg": "ส่งข้อความเรียบร้อยแล้ว!",
            "anon_label": "🥷 ส่งแบบไม่ระบุตัวตน",
            "anon_name": "ทึเม (ไม่ระบุชื่อ)",
            "select_dev": "👨‍💻 ถึง: ผู้พัฒนาแอป (Developer)",
            "btn_edit": "✏️ แก้ไข",
            "btn_delete": "🗑️ ลบ",
            "btn_save_edit": "💾 บันทึก",
            "btn_cancel": "❌ ยกเลิก",
            "confirm_delete": "ลบข้อความนี้?",
            "bio_title": "ชีวประวัติโดยย่อ"
        },
        "en": {
            "sub": "LOVE PULSE : THE 3RD MINI ALBUM | 2026",
            "touch": "TOUCH MEMBER TO VIEW PROFILE",
            "close": "CLOSE PROFILE",
            "tab1": "STORY & FACTS",
            "tab2": "SONGS",
            "tab3": "COVERS",
            "tab4": "STATS",
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
            "error_member": "Member not found",
            "stats": "Statistics",
            "total_members": "Members",
            "your_favorites": "Your Favorites",
            "total_songs": "Total Songs",
            "random_member": "🎲 Random Member",
            "theme": "Theme",
            "light": "☀️ Light",
            "dark": "🌙 Dark",
            "birthday_countdown": "🎂 Birthday Countdown",
            "days": "days",
            "add_favorite": "💖 Add to Favorites",
            "remove_favorite": "❤️ Remove from Favorites",
            "added_favorite": "Added to favorites! ❤️",
            "removed_favorite": "Removed from favorites",
            "loading": "Loading...",
            "tab_group": "ABOUT GROUP",
            "debut_date": "Debut Date",
            "fandom": "Fandom Name",
            "origin": "Origin",
            "shows": "Variety Shows",
            "albums": "Discography",
            "group_desc": "TREASURE is a boy band under YG Entertainment formed through the survival show 'YG Treasure Box', known for their energetic performances and versatile music.",
            "award_title": "Awards & Achievements",
            "award_desc": "🏆 Rookie of the Year (2020)\n🏆 MAMA Worldwide Fans' Choice\n🌏 'HELLO' Asia Tour Sold Out",
            "menu_home": "🏠 Home / Members",
            "menu_about": "🏢 About TREASURE",
            "menu_cheer": "💬 Fan Zone / Cheer",
            "cheer_title": "💎 TEUME CHEER BOARD",
            "cheer_desc": "Send your love and support to members! Even if the members don't see it right away, your kind words bring positive energy to the fandom!",
            "form_name": "Your Name",
            "form_tag": "Who is your bias? / To whom?",
            "form_msg": "Message",
            "btn_send": "🚀 Send Cheer",
            "recent_comments": "Recent Cheers",
            "select_all": "💙 To: TREASURE (All)",
            "success_msg": "Message sent successfully!",
            "anon_label": "🥷 Send Anonymously",
            "anon_name": "Teume (Anonymous)",
            "select_dev": "👨‍💻 To: Developer",
            "btn_edit": "✏️ Edit",
            "btn_delete": "🗑️ Delete",
            "btn_save_edit": "💾 Save",
            "btn_cancel": "❌ Cancel",
            "confirm_delete": "Delete this?",
            "bio_title": "Biography"
        },
        "kr": {
            "sub": "LOVE PULSE : 세 번째 미니 앨범 | 2026",
            "touch": "멤버를 터치하여 프로필 보기",
            "close": "닫기",
            "tab1": "프로필 & 스토리",
            "tab2": "대표곡",
            "tab3": "커버곡",
            "tab4": "통계",
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
            "error_member": "멤버를 찾을 수 없습니다",
            "stats": "통계",
            "total_members": "멤버",
            "your_favorites": "내 즐겨찾기",
            "total_songs": "전체 곡",
            "random_member": "🎲 랜덤 멤버",
            "theme": "테마",
            "light": "☀️ 라이트",
            "dark": "🌙 다크",
            "birthday_countdown": "🎂 생일 카운트다운",
            "days": "일 후",
            "add_favorite": "💖 즐겨찾기 추가",
            "remove_favorite": "❤️즐겨찾기 삭제",
            "added_favorite": "즐겨찾기에 추가되었습니다! ❤️",
            "removed_favorite": "즐겨찾기에서 삭제되었습니다",
            "loading": "로딩 중...",
            "tab_group": "그룹 소개",
            "debut_date": "데뷔일",
            "fandom": "팬덤명",
            "origin": "결성",
            "shows": "예능",
            "albums": "디스코그래피",
            "group_desc": "트레저는 YG 엔터테인먼트 소속 보이그룹으로, 서바이벌 프로그램 'YG 보석함'을 통해 결성되었습니다.",
            "award_title": "수상 및 성과",
            "award_desc": "🏆 2020년 신인상 수상\n🏆 MAMA 월드와이드 팬스 초이스\n🌏 'HELLO' 아시아 투어 전석 매진",
            "menu_home": "🏠 홈 / 멤버",
            "menu_about": "🏢 트레저 소개",
            "menu_cheer": "💬 팬 존 / 응원하기",
            "cheer_title": "💎 트레저 메이커 응원 게시판",
            "cheer_desc": "멤버들에게 사랑의 메시지를 보내세요! 멤버들이 바로 보지 못하더라도, 여러분의 따뜻한 말은 팬덤에게 큰 힘이 됩니다!",
            "form_name": "닉네임 (Nickname)",
            "form_tag": "최애 멤버 / 받는 사람",
            "form_msg": "응원 메시지",
            "btn_send": "🚀 응원 보내기",
            "recent_comments": "최신 응원글",
            "select_all": "💙 TO: 트레저 (전체)",
            "success_msg": "메시지가 전송되었습니다! 💌",
            "anon_label": "🥷 익명으로 보내기",
            "anon_name": "트메 (익명)",
            "select_dev": "👨‍💻 TO: 개발자 (Developer)",
            "btn_edit": "✏️ 수정",
            "btn_delete": "🗑️ 삭제",
            "btn_save_edit": "💾 저장",
            "btn_cancel": "❌ 취소",
            "confirm_delete": "삭제하시겠습니까?",
            "bio_title": "약력"
        },
        "jp": {
            "sub": "LOVE PULSE : サード・ミニアルバム | 2026",
            "touch": "メンバーをタップしてプロフィールを見る",
            "close": "閉じる",
            "tab1": "プロフィール",
            "tab2": "代表曲",
            "tab3": "カバー",
            "tab4": "統計",
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
            "error_member": "メンバーが見つかりません",
            "stats": "統計",
            "total_members": "メンバー",
            "your_favorites": "お気に入り",
            "total_songs": "総曲数",
            "random_member": "🎲 ランダム",
            "theme": "テーマ",
            "light": "☀️ ライト",
            "dark": "🌙 ダーク",
            "birthday_countdown": "🎂 誕生日カウントダウン",
            "days": "日",
            "add_favorite": "💖 お気に入り追加",
            "remove_favorite": "❤️ お気に入り削除",
            "added_favorite": "お気に入りに追加されました! ❤️",
            "removed_favorite": "お気に入りから削除されました",
            "loading": "読み込み中...",
            "tab_group": "グループについて",
            "debut_date": "デビュー日",
            "fandom": "ファンダム名",
            "origin": "結成",
            "shows": "バラエティ",
            "albums": "ディスコグラフィ",
            "group_desc": "TREASUREはYGエンターテインメント所属のボーイズグループで、サバイバル番組「YG宝石箱」を通じて結成されました。",
            "award_title": "受賞歴",
            "award_desc": "🏆 2020年 新人賞受賞\n🏆 MAMA Worldwide Fans' Choice\n🌏 'HELLO' アジアツアー全席完売",
            "menu_home": "🏠 ホーム / メンバー",
            "menu_about": "🏢 TREASUREについて",
            "menu_cheer": "💬 ファンゾーン / 応援",
            "cheer_title": "💎 TEUME 応援ボード",
            "cheer_desc": "メンバーに愛と応援を送りましょう！ メンバーにすぐ届かなくても、あなたの温かい言葉はファンダムの大きな力になります！",
            "form_name": "ニックネーム (Nickname)",
            "form_tag": "推しメン / 宛先",
            "form_msg": "メッセージ",
            "btn_send": "🚀 応援を送る",
            "recent_comments": "最近のメッセージ",
            "select_all": "💙 TO: TREASURE (全員)",
            "success_msg": "メッセージが送信されました！ 💌",
            "anon_label": "🥷 匿名で送信",
            "anon_name": "トゥメ (匿名)",
            "select_dev": "👨‍💻 TO: 開発者 (Developer)",
            "btn_edit": "✏️ 編集",
            "btn_delete": "🗑️ 削除",
            "btn_save_edit": "💾 保存",
            "btn_cancel": "❌ キャンセル",
            "confirm_delete": "削除しますか？",
            "bio_title": "略歴"
        },
        "cn": {
            "sub": "LOVE PULSE : 第三张迷你专辑 | 2026",
            "touch": "点击成员查看资料",
            "close": "关闭",
            "tab1": "简介 & 故事",
            "tab2": "热门歌曲",
            "tab3": "翻唱",
            "tab4": "统计",
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
            "error_member": "未找到成员",
            "stats": "统计数据",
            "total_members": "成员",
            "your_favorites": "我的最爱",
            "total_songs": "歌曲总数",
            "random_member": "🎲 随机成员",
            "theme": "主题",
            "light": "☀️ 明亮",
            "dark": "🌙 暗黑",
            "birthday_countdown": "🎂 生日倒计时",
            "days": "天",
            "add_favorite": "💖 添加最爱",
            "remove_favorite": "❤️ 移除最爱",
            "added_favorite": "已添加到最爱! ❤️",
            "removed_favorite": "已从最爱移除",
            "loading": "加载中...",
            "tab_group": "关于组合",
            "debut_date": "出道日期",
            "fandom": "粉丝名称",
            "origin": "起源",
            "shows": "综艺节目",
            "albums": "音乐作品",
            "group_desc": "TREASURE是YG娱乐旗下的男子组合，通过生存节目《YG宝石盒》结成，以充满活力的表演和多样化的音乐风格著称。",
            "award_title": "奖项与成就",
            "award_desc": "🏆 2020年 新人奖\n🏆 MAMA Worldwide Fans' Choice\n🌏 'HELLO' 亚洲巡演售罄",
            "menu_home": "🏠 主页 / 成员",
            "menu_about": "🏢 关于TREASURE",
            "menu_cheer": "💬 粉丝专区 / 应援",
            "cheer_title": "💎 TEUME 应援板",
            "cheer_desc": "给成员们发送充满爱意的应援吧！即使成员们无法第一时间看到，温暖的留言也能为饭圈带来正能量！",
            "form_name": "昵称 (Nickname)",
            "form_tag": "本命 / 发送给",
            "form_msg": "应援留言",
            "btn_send": "🚀 发送应援",
            "recent_comments": "最新留言",
            "select_all": "💙 TO: TREASURE (全员)",
            "success_msg": "发送成功！ 💌",
            "anon_label": "🥷 匿名发送",
            "anon_name": "TEUME (匿名)",
            "select_dev": "👨‍💻 TO: 开发者 (Developer)",
            "btn_edit": "✏️ 编辑",
            "btn_delete": "🗑️ 删除",
            "btn_save_edit": "💾 保存",
            "btn_cancel": "❌ 取消",
            "confirm_delete": "确定删除吗？",
            "bio_title": "传记"

        }
    }

# ============================================
# 🔄 SESSION STATE MANAGEMENT
# ============================================
def initialize_session_state(members: List[Dict]):
    # Initialize preferences manager
    if 'preferences' not in st.session_state:
        st.session_state.preferences = UserPreferences()
    
    # Load language
    if 'lang_code' not in st.session_state:
        if "lang" in st.query_params and st.query_params["lang"] in AppConfig.SUPPORTED_LANGUAGES:
            st.session_state.lang_code = st.query_params["lang"]
        else:
            st.session_state.lang_code = AppConfig.DEFAULT_LANGUAGE
            
    if 'favorites' not in st.session_state:
        st.session_state.favorites = st.session_state.preferences.load_favorites()
        
    if 'theme' not in st.session_state:
        st.session_state.theme = st.session_state.preferences.load_theme()
        
    if 'visit_count' not in st.session_state:
        st.session_state.visit_count = {}
    
    if 'page' not in st.session_state:
        st.session_state.page = 'members'

    # --- ส่วนที่แก้ไข: เช็ค ID จาก URL ทุกครั้งที่มีการโหลดหน้า ---
    if "id" in st.query_params:
        try:
            idx = int(st.query_params["id"])
            if 0 <= idx < len(members):
                # ถ้า ID เปลี่ยน หรือยังไม่มี selected_member ให้เซ็ตค่า
                current_id = -1
                if 'selected_member' in st.session_state:
                    # หา index ของสมาชิกปัจจุบันเพื่อเทียบ
                    current_name = st.session_state.selected_member.get('name')
                    current_id = next((i for i, m in enumerate(members) if m['name'] == current_name), -1)
                
                if current_id != idx:
                    st.session_state.selected_member = members[idx]
                    st.session_state.page = 'members'
        except (ValueError, TypeError, KeyError):
            pass

def set_language(code: str):
    st.session_state.lang_code = code

def toggle_favorite(member_name: str):
    if member_name in st.session_state.favorites:
        st.session_state.favorites.remove(member_name)
    else:
        st.session_state.favorites.append(member_name)
    st.session_state.preferences.save_favorites(st.session_state.favorites)

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
    st.session_state.preferences.save_theme(st.session_state.theme)

def track_visit(member_name: str):
    if member_name not in st.session_state.visit_count:
        st.session_state.visit_count[member_name] = 0
    st.session_state.visit_count[member_name] += 1

# ============================================
# 🎨 ENHANCED CSS
# ============================================
@st.cache_data
def get_theme_config(theme: str) -> dict:
    if theme == "light":
        return {
            "bg_gradient": "radial-gradient(circle at 50% 10%, #e3f2fd 0%, #ffffff 90%)",
            "primary_color": "#1976d2",
            "glass_bg": "rgba(255, 255, 255, 0.8)",
            "border_color": "rgba(0, 0, 0, 0.1)",
            "text_color": "#333",
            "card_bg": "rgba(255, 255, 255, 0.9)",
            "secondary_text": "#666"
        }
    else:
        return {
            "bg_gradient": "radial-gradient(circle at 50% 10%, #1a2a3a 0%, #000000 90%)",
            "primary_color": "#32E0C4",
            "glass_bg": "rgba(255, 255, 255, 0.05)",
            "border_color": "rgba(255, 255, 255, 0.1)",
            "text_color": "white",
            "card_bg": "rgba(255, 255, 255, 0.05)",
            "secondary_text": "#8899a6"
        }

def inject_custom_css():
    theme = st.session_state.get('theme', 'dark')
    config = get_theme_config(theme)
    
    st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&family=Prompt:wght@300;500;700&family=Noto+Sans+KR:wght@400;700&family=Noto+Sans+SC:wght@400;700&display=swap');

    :root {{ 
        --primary: {config['primary_color']}; 
        --glass: {config['glass_bg']}; 
        --border: {config['border_color']}; 
        --text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        --card-bg: {config['card_bg']};
        --text-color: {config['text_color']};
        --secondary-text: {config['secondary_text']};
    }}
    
    /* ----- MINI STATS IN SIDEBAR ----- */
    .mini-stat-container {{
        display: flex;
        justify-content: space-between;
        gap: 5px;
        margin-bottom: 20px;
        background: var(--glass);
        padding: 10px;
        border-radius: 12px;
        border: 1px solid var(--border);
        backdrop-filter: blur(10px);
    }}
    .mini-stat-box {{
        text-align: center;
        flex: 1;
    }}
    .mini-stat-number {{
        font-size: 1.2rem;
        font-weight: 800;
        color: var(--primary);
        line-height: 1.2;
    }}
    .mini-stat-label {{
        font-size: 0.6rem;
        color: var(--secondary-text);
        text-transform: uppercase;
        margin-top: 2px;
    }}
    .mini-stat-icon {{
        font-size: 0.8rem;
        margin-bottom: 2px;
        display: block;
    }}
    
    /* ----- VARIETY SHOW BUTTONS (New) ----- */
    .variety-btn {{
        background: var(--glass);
        border: 1px solid var(--border);
        color: {config['text_color']} !important;
        padding: 10px 15px;
        border-radius: 10px;
        display: block;
        transition: all 0.3s ease;
        margin-bottom: 10px;
        text-decoration: none !important;
        cursor: pointer;
        text-align: center;
        font-size: 0.95rem;
        font-weight: 500;
    }}
    .variety-btn:hover {{
        border-color: var(--primary);
        color: var(--primary) !important;
        transform: translateX(5px);
        background: rgba(50, 224, 196, 0.1);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    
    .stApp {{ 
        background: {config['bg_gradient']}; 
        font-family: 'Prompt', 'Noto Sans KR', 'Noto Sans SC', sans-serif; 
        color: {config['text_color']}; 
        transition: all 0.5s ease;
    }}
    
    #MainMenu {{visibility: hidden;}} 
    footer {{visibility: hidden;}} 
    header {{visibility: visible !important; background: transparent !important;}}
    [data-testid="stSidebarCollapsedControl"] {{ 
        color: var(--primary) !important; 
        background-color: rgba(0,0,0,0.5); 
        border-radius: 50%; 
    }}
    
    section[data-testid="stSidebar"] {{ 
        background-color: {config['card_bg']}; 
        border-right: 1px solid var(--border); 
        backdrop-filter: blur(10px); 
    }}
    
    .block-container {{ 
        padding-top: 1rem !important; 
        padding-bottom: 2rem !important; 
        margin-top: 0 !important; 
        max-width: 1400px !important; 
    }}
    
    div[data-testid="column"] .stButton button {{ 
        background: transparent !important; 
        border: none !important; 
        font-size: 2rem !important; 
        padding: 0px !important; 
        margin: 0px !important; 
        line-height: 1 !important; 
        opacity: 0.4; 
        transition: all 0.3s ease; 
    }}
    div[data-testid="column"] .stButton button:hover {{ 
        transform: scale(1.3) !important; 
        opacity: 1 !important; 
        text-shadow: 0 0 20px rgba(50, 224, 196, 0.9); 
    }}
    
    .hero-container {{ 
        text-align: center; 
        margin-top: -20px; 
        animation: fadeIn 1.5s ease-in-out; 
    }}
    .hero-title {{ 
        font-family: 'Montserrat', sans-serif; 
        font-size: clamp(3rem, 8vw, 5rem); 
        font-weight: 900; 
        letter-spacing: -3px; 
        background: linear-gradient(135deg, {config['text_color']} 0%, var(--primary) 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        text-shadow: 0 0 40px rgba(50, 224, 196, 0.4); 
        margin: 0; 
        line-height: 1.1; 
        animation: glow 2s ease-in-out infinite alternate; 
    }}
    .hero-subtitle {{ 
        font-size: clamp(0.9rem, 2vw, 1.2rem); 
        color: var(--secondary-text); 
        letter-spacing: 3px; 
        margin-top: 8px; 
        text-transform: uppercase; 
    }}
    
    .social-bar {{ 
        display: flex; 
        justify-content: center; 
        gap: 15px; 
        margin-top: 25px; 
        flex-wrap: wrap; 
    }}
    .social-btn {{ 
        display: inline-flex; 
        align-items: center; 
        justify-content: center; 
        width: 55px; 
        height: 55px; 
        border-radius: 50%; 
        background: var(--glass); 
        border: 2px solid var(--border); 
        color: {config['text_color']}; 
        font-size: 1.6rem; 
        text-decoration: none; 
        transition: all 0.4s; 
        backdrop-filter: blur(10px); 
    }}
    .social-btn:hover {{ 
        background: rgba(50, 224, 196, 0.2); 
        border-color: var(--primary); 
        transform: translateY(-8px) scale(1.1); 
        box-shadow: 0 8px 25px rgba(50, 224, 196, 0.5); 
    }}
    
    .stTextInput input {{ 
        background: var(--glass) !important; 
        border: 1px solid var(--border) !important; 
        border-radius: 15px !important; 
        color: {config['text_color']} !important; 
        padding: 12px 20px !important; 
    }}
    .stTextInput input:focus {{ 
        border-color: var(--primary) !important; 
        box-shadow: 0 0 20px rgba(50, 224, 196, 0.3) !important; 
    }}
    
    .map-frame {{ 
        background: var(--glass); 
        backdrop-filter: blur(15px); 
        border: 1px solid var(--border); 
        border-radius: 30px; 
        padding: 15px; 
        box-shadow: 0 30px 80px rgba(0,0,0,0.3); 
        max-width: 1100px; 
        margin: 1.5rem auto 3rem auto; 
        position: relative; 
        animation: slideUp 1s ease-out; 
    }}
    .main-image {{ 
        width: 100%; 
        border-radius: 20px; 
        display: block; 
        transition: transform 0.3s ease; 
    }}
    .map-frame:hover .main-image {{ transform: scale(1.02); }}
    
    .member-card-link {{ text-decoration: none !important; display: block; }}
    .member-card-overlay {{ 
        position: relative; 
        border-radius: 15px; 
        overflow: hidden; 
        aspect-ratio: 3/4; 
        cursor: pointer; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3); 
        transition: all 0.3s ease; 
        border: 2px solid var(--border); 
        background: var(--card-bg);
    }}
    .member-card-overlay:hover {{ 
        transform: translateY(-5px) scale(1.03); 
        border-color: var(--primary); 
        box-shadow: 0 15px 30px rgba(50, 224, 196, 0.4); 
    }}
    .member-img-full {{ 
        width: 100%; 
        height: 100%; 
        object-fit: cover; 
        display: block; 
    }}
    .member-name-overlay {{ 
        position: absolute; 
        bottom: 0; 
        left: 0; 
        width: 100%; 
        background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.6) 60%, transparent 100%); 
        color: white; 
        padding: 20px 5px 10px 5px; 
        text-align: center; 
        font-weight: 700; 
        font-size: 1rem; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.8); 
        letter-spacing: 0.5px; 
    }}
    
    .rec-card {{ 
        background: var(--glass); 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 20px; 
        border: 1px solid var(--border); 
        text-align: center; 
        transition: all 0.3s ease; 
        backdrop-filter: blur(10px);
    }}
    .rec-card:hover {{ 
        transform: translateY(-3px); 
        border-color: var(--primary); 
        background: rgba(50,224,196,0.1); 
    }}
    
    div[data-testid="stDialog"] div[role="dialog"] {{ 
        width: 90vw !important; 
        max-width: 1500px !important; 
        background: {"rgba(255, 255, 255, 0.95)" if theme == "light" else "rgba(15, 20, 25, 0.98)"} !important; 
        border: 2px solid var(--primary) !important; 
        border-radius: 25px !important; 
        backdrop-filter: blur(20px) !important; 
    }}
    
    .profile-header {{ 
        font-family: 'Montserrat', sans-serif; 
        font-size: clamp(2.5rem, 5vw, 3.5rem); 
        font-weight: 800; 
        color: var(--primary); 
        line-height: 1; 
        text-shadow: 0 0 30px rgba(50, 224, 196, 0.5); 
    }}
    .profile-cn-name {{ 
        font-size: clamp(1.2rem, 3vw, 1.8rem); 
        color: #888; 
        font-weight: 400; 
        margin-left: 10px; 
    }}
    .profile-sub {{ 
        font-size: clamp(1.1rem, 2.5vw, 1.5rem); 
        color: var(--secondary-text); 
        margin-bottom: 25px; 
        border-bottom: 2px solid var(--border); 
        padding-bottom: 15px; 
    }}
    
    .stat-row {{ 
        display: flex; 
        justify-content: space-between; 
        gap: 15px; 
        margin-bottom: 25px; 
        background: var(--glass); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid var(--border); 
        backdrop-filter: blur(10px);
    }}
    .stat-item {{ text-align: center; flex: 1; }}
    .stat-label {{ 
        font-size: 0.85rem; 
        color: #999; 
        display: block; 
        text-transform: uppercase; 
    }}
    .stat-val {{ 
        font-size: 1.5rem; 
        font-weight: 700; 
        color: {config['text_color']}; 
    }}
    
    .story-container {{ 
        background: var(--glass); 
        border-radius: 16px; 
        padding: 25px; 
        border: 1px solid rgba(50, 224, 196, 0.15); 
        position: relative; 
        margin-top: 15px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.2); 
        backdrop-filter: blur(10px);
    }}
    .story-icon-header {{ 
        position: absolute; 
        top: -18px; 
        left: 20px; 
        background: {"#fff" if theme == "light" else "#0e1117"}; 
        padding: 5px 15px; 
        border-radius: 20px; 
        border: 1px solid rgba(50, 224, 196, 0.3); 
        color: var(--primary); 
        font-weight: bold; 
        font-size: 0.9rem; 
        letter-spacing: 1px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); 
    }}
    .story-content {{ 
        color: {"#333" if theme == "light" else "#e0e0e0"}; 
        line-height: 1.8; 
        font-size: 1.05rem; 
        font-weight: 300; 
    }}
    
    .facts-grid {{ 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); 
        gap: 12px; 
        margin-top: 10px; 
    }}
    .fact-card-modern {{ 
        background: linear-gradient(145deg, var(--glass) 0%, rgba(255,255,255,0.01) 100%); 
        border: 1px solid var(--border); 
        border-radius: 12px; 
        padding: 15px 10px; 
        text-align: center; 
        transition: all 0.3s ease; 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        min-height: 100px; 
        backdrop-filter: blur(10px);
    }}
    .fact-card-modern:hover {{ 
        background: rgba(50, 224, 196, 0.08); 
        border-color: var(--primary); 
        transform: translateY(-3px); 
    }}
    .fact-icon-modern {{ 
        font-size: 1.8rem; 
        margin-bottom: 8px; 
        filter: drop-shadow(0 0 5px rgba(50, 224, 196, 0.4)); 
    }}
    .fact-label-modern {{ 
        font-size: 0.7rem; 
        color: #888; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        margin-bottom: 2px; 
    }}
    .fact-value-modern {{ 
        font-size: 0.95rem; 
        color: {config['text_color']}; 
        font-weight: 600; 
        line-height: 1.2; 
        word-break: break-word; 
    }}
    
    .song-link {{ text-decoration: none; }}
    .song-card {{ 
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
        background: var(--glass); 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 12px; 
        border: 1px solid var(--border); 
        transition: all 0.3s ease; 
        backdrop-filter: blur(10px);
    }}
    .song-card:hover {{ 
        background: rgba(50, 224, 196, 0.15); 
        border-color: var(--primary); 
        transform: translateX(8px); 
    }}
    .song-title {{ 
        color: {config['text_color']}; 
        font-weight: 600; 
        font-size: 1.15rem; 
    }}
    
    .favorite-heart {{ 
        position: absolute; 
        top: 10px; 
        right: 10px; 
        font-size: 1.5rem; 
        filter: drop-shadow(0 0 5px rgba(255, 0, 0, 0.5)); 
        animation: heartbeat 1.5s infinite; 
        z-index: 10; 
    }}
    
    .stats-box {{ 
        background: var(--glass); 
        border-radius: 15px; 
        padding: 20px; 
        text-align: center; 
        border: 1px solid var(--border); 
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }}
    .stats-box:hover {{ 
        border-color: var(--primary); 
        transform: translateY(-5px); 
        box-shadow: 0 10px 30px rgba(50, 224, 196, 0.3); 
    }}
    .stats-number {{ 
        font-size: 2.5rem; 
        font-weight: 900; 
        color: var(--primary); 
        margin: 10px 0; 
    }}
    .stats-label {{ 
        font-size: 0.9rem; 
        color: #888; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
    }}
    
    .birthday-card {{
        background: var(--glass);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }}
    .birthday-card:hover {{
        border-color: var(--primary);
        transform: translateX(5px);
    }}
    
    @keyframes fadeIn {{ 
        from {{ opacity: 0; transform: translateY(30px); }} 
        to {{ opacity: 1; transform: translateY(0); }} 
    }}
    @keyframes slideUp {{ 
        from {{ opacity: 0; transform: translateY(50px); }} 
        to {{ opacity: 1; transform: translateY(0); }} 
    }}
    @keyframes glow {{ 
        from {{ text-shadow: 0 0 20px rgba(50, 224, 196, 0.3); }} 
        to {{ text-shadow: 0 0 40px rgba(50, 224, 196, 0.7); }} 
    }}
    @keyframes heartbeat {{ 
        0%, 100% {{ transform: scale(1); }} 
        50% {{ transform: scale(1.1); }} 
    }}
    
    @media (max-width: 768px) {{ 
        .hero-title {{ font-size: 3rem !important; }} 
        .stat-row {{ flex-direction: column !important; gap: 10px !important; }} 
        div[data-testid="stDialog"] div[role="dialog"] {{ width: 95vw !important; }}
        .social-bar {{ gap: 8px; }}
        .social-btn {{ width: 45px; height: 45px; font-size: 1.2rem; }}
        .facts-grid {{ grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)) !important; }}
    }}
</style>
""", unsafe_allow_html=True)

# ============================================
# 📊 MEMBER DATA
# ============================================
@st.cache_data
def get_members_data() -> List[Dict]:
    return [
        # --- 1. HYUNSUK ---
        {
            "name": "Hyunsuk",
            "img": "hyunsuk.jpg",
            "history_image": "https://i.pinimg.com/736x/8d/95/92/8d959265972f05633725597906967735.jpg",
            "birthday": "1999.04.21",
            "height": "171 cm",
            "mbti": "ENFP",
            "display_name": {"th": "ชเว ฮยอนซอก", "en": "Choi Hyunsuk", "kr": "최현석", "jp": "チェ・ヒョンソク", "cn": "崔玹硕"},
            "position": {"th": "ลีดเดอร์, แร็ปเปอร์, แดนซ์", "en": "Leader, Rapper, Dancer", "kr": "리더, 래퍼, 댄서", "jp": "リーダー, ラッパー", "cn": "队长, Rapper"},
            "nickname": {"th": "7chill", "en": "7chill", "kr": "7chill", "jp": "7chill", "cn": "7chill"},
            "history": {
                "th": "พี่ใหญ่และผู้นำแฟชั่นของวง ผ่านรายการ MIXNINE (อันดับ 5) เป็นเด็กฝึกยาวนานที่สุดในวง",
                "en": "Eldest member and fashionista. MIXNINE Rank 5. Longest trainee period.",
                "kr": "팀의 맏형이자 패셔니스타. 믹스나인 5위. 연습생 기간이 가장 길었음.",
                "jp": "最年長でファッショニスタ。MIXNINE 5位。練習生期間が一番長い。",
                "cn": "大哥和时尚达人。MIXNINE第5名。练习生时间最长。"
            },
            "biography": {
                "th": "ชเว ฮยอนซอก เข้ามาเป็นเด็กฝึกของ YG ในปี 2015 ผ่านการออดิชั่นแบบส่วนตัว เขาเป็นที่รู้จักครั้งแรกผ่านรายการ MIXNINE ในปี 2017 และได้อันดับที่ 5 ในรอบไฟนอล แต่โชคร้ายที่การเดบิวต์ถูกยกเลิก เขาไม่ย่อท้อและกลับมาแข่งขันในรายการ YG Treasure Box จนได้รับเลือกเป็นสมาชิกคนสุดท้ายของ TREASURE 7 (ไลน์อัพแรก) และกลายเป็นลีดเดอร์ที่พึ่งพาได้ของวงในที่สุด",
                "en": "Choi Hyunsuk joined YG in 2015 via private audition. Ranked 5th in MIXNINE (2017) but debut was cancelled. Joined YG Treasure Box and became the final member of the first lineup, now leading the group.",
                "kr": "2015년 입사. 믹스나인 5위를 기록했으나 데뷔 무산. 이후 YG 보석함에서 최종 멤버로 선발되어 리더가 됨.",
                "jp": "2015年入社。MIXNINEで5位になるもデビュー白紙。YG宝石箱で最終メンバーに選ばれリーダーに。",
                "cn": "2015年加入YG。MIXNINE获得第5名但出道取消。后通过YG宝石盒成为最终成员并担任队长。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** A", "💎 **Gemstone:** Garnet", "🐶 **Eng Name:** Danny Choi", "⚽ **Hobby:** ช้อปปิ้ง, ฟุตบอล", "🎵 **Role:** Composer"],
                "en": ["🩸 **Blood Type:** A", "💎 **Gemstone:** Garnet", "🐶 **Eng Name:** Danny Choi", "⚽ **Hobby:** Shopping, Soccer", "🎵 **Role:** Composer"],
                "kr": ["🩸 **혈액형:** A형", "💎 **보석:** 가넷", "🐶 **영어 이름:** Danny Choi", "⚽ **취미:** 쇼핑, 축구", "🎵 **역할:** 작곡"],
                "jp": ["🩸 **血液型:** A型", "💎 **宝石:** ガーネット", "🐶 **英語名:** Danny Choi", "⚽ **趣味:** 買い物", "🎵 **役割:** 作曲"],
                "cn": ["🩸 **血型:** A型", "💎 **宝石:** 石榴石", "🐶 **英文名:** Danny Choi", "⚽ **爱好:** 购物", "🎵 **担当:** 作曲"]
            },
            "songs": ["VolKno", "Wonderland"],
            "covers": ["Humble"]
        },
        # --- 2. JIHOON ---
        {
            "name": "Jihoon",
            "img": "jihoon.jpg",
            "history_image": "",
            "birthday": "2000.03.14",
            "height": "178 cm",
            "mbti": "ENTJ",
            "display_name": {"th": "พัค จีฮุน", "en": "Park Jihoon", "kr": "박지훈", "jp": "パク・ジフン", "cn": "朴志焄"},
            "position": {"th": "ลีดเดอร์, เมนแดนซ์, โวคอล", "en": "Leader, Main Dancer, Vocal", "kr": "리더, 메인 댄서, 보컬", "jp": "リーダー, メインダンサー", "cn": "队长, 主舞"},
            "nickname": {"th": "Hoonie", "en": "Hoonie", "kr": "후니", "jp": "フニ", "cn": "Hoonie"},
            "history": {
                "th": "จากปูซาน เคยออกจาก YG แล้วกลับมาใหม่ผ่านรายการ Treasure Box เป็นคนที่มีความเป็นผู้นำสูง",
                "en": "From Busan. Left YG once but returned for Treasure Box. High leadership skills.",
                "kr": "부산 출신. YG 퇴사 후 보석함으로 복귀. 리더십이 강함.",
                "jp": "釜山出身。一度YGを去ったが宝石箱で復帰。リーダーシップが強い。",
                "cn": "来自釜山。曾离开YG后回归。领导力强。"
            },
            "biography": {
                "th": "จีฮุนเข้ามาเป็นเด็กฝึกในปี 2016 แต่ต้องออกจาก YG ไปช่วงหนึ่ง เขาไม่ละทิ้งความฝันและกลับมาท้าทายอีกครั้งในรายการ YG Treasure Box ด้วยทักษะการเต้นที่พัฒนาขึ้นอย่างก้าวกระโดดและความเป็นผู้นำที่โดดเด่น ทำให้เขาได้รับเลือกให้เดบิวต์และเป็นลีดเดอร์คู่กับฮยอนซอก",
                "en": "Jihoon joined in 2016 but left shortly after. He returned for YG Treasure Box with improved skills, earning his spot and co-leader role.",
                "kr": "2016년 입사 후 퇴사했으나, 보석함으로 재도전하여 향상된 실력으로 데뷔 및 공동 리더 발탁.",
                "jp": "2016年に入社したが退社。宝石箱で再挑戦し、実力を証明してデビューと共同リーダーの座を掴んだ。",
                "cn": "2016年加入后曾退出。通过宝石盒回归，凭借实力出道并成为共同队长。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Amethyst", "🐶 **Eng Name:** Jun Park", "💪 **Skill:** Pilates", "📷 **Hobby:** ถ่ายรูป"],
                "en": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Amethyst", "🐶 **Eng Name:** Jun Park", "💪 **Skill:** Pilates", "📷 **Hobby:** Photography"],
                "kr": ["🩸 **혈액형:** B형", "💎 **보석:** 자수정", "🐶 **영어 이름:** Jun Park", "💪 **특기:** 필라테스", "📷 **취미:** 사진"],
                "jp": ["🩸 **血液型:** B型", "💎 **宝石:** アメジスト", "🐶 **英語名:** Jun Park", "💪 **特技:** ピラティス", "📷 **趣味:** 写真"],
                "cn": ["🩸 **血型:** B型", "💎 **宝石:** 紫水晶", "🐶 **英文名:** Jun Park", "💪 **特长:** 普拉提", "📷 **爱好:** 摄影"]
            },
            "songs": ["The Way To", "HOLD IT IN"],
            "covers": ["UGLY"]
        },
        # --- 3. YOSHI ---
        {
            "name": "Yoshi",
            "img": "yoshi.jpg",
            "history_image": "",
            "birthday": "2000.05.15",
            "height": "179 cm",
            "mbti": "INFP",
            "display_name": {"th": "คาเนโมโตะ โยชิโนริ", "en": "Kanemoto Yoshinori", "kr": "요시노리", "jp": "金本芳典", "cn": "金本芳典"},
            "position": {"th": "แร็ปเปอร์", "en": "Rapper", "kr": "래퍼", "jp": "ラッパー", "cn": "Rapper"},
            "nickname": {"th": "Tiger", "en": "Tiger", "kr": "호랑이", "jp": "トラ", "cn": "老虎"},
            "history": {
                "th": "เกิดที่โกเบ แฟชั่นนิสต้าที่รักศิลปะ เคยฝันอยากเป็นนักแข่งรถ มีสไตล์แร็ปเสียงสูง (High tone)",
                "en": "Born in Kobe. Fashionista loving art. Dreamed of racing. Known for high-tone rap.",
                "kr": "고베 출신. 예술을 사랑하는 패셔니스타. 하이톤 랩이 특징.",
                "jp": "神戸出身。アート好きのファッショニスタ。ハイトーンラップが特徴。",
                "cn": "生于神户。热爱艺术的时尚达人。以高音Rapper著称。"
            },
            "biography": {
                "th": "โยชิเกิดและโตที่ญี่ปุ่น เขาผ่านการออดิชั่นของ YG Japan แม้จะสูญเสียคุณพ่อไปตั้งแต่เด็ก แต่เขาก็มุ่งมั่นทำตามความฝันเพื่อครอบครัว ในรายการ Treasure Box เขาแสดงให้เห็นถึงพัฒนาการที่ก้าวกระโดดจนได้รับเลือกเข้าสู่ทีม Magnum (ยูนิตที่ 2) ก่อนจะรวมเป็น TREASURE",
                "en": "Born in Japan, passed YG Japan audition. Despite losing his father young, he pursued his dream for his family. Selected for Magnum in Treasure Box before merging into TREASURE.",
                "kr": "일본 출신으로 YG Japan 오디션 합격. 어린 시절 아버지를 여의었으나 꿈을 포기하지 않음. 매그넘 멤버로 선발됨.",
                "jp": "日本出身、YG Japanオーディション合格。幼い頃に父を亡くすが夢を追う。マグナムのメンバーとして選ばれた。",
                "cn": "生于日本，通过YG Japan选秀。虽早年丧父但坚持梦想。入选Magnum成员。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** A", "💎 **Gemstone:** Aquamarine", "🐶 **Eng Name:** Jaden", "🎸 **Hobby:** กีตาร์", "🥋 **Skill:** Beatbox"],
                "en": ["🩸 **Blood Type:** A", "💎 **Gemstone:** Aquamarine", "🐶 **Eng Name:** Jaden", "🎸 **Hobby:** Guitar", "🥋 **Skill:** Beatbox"],
                "kr": ["🩸 **혈액형:** A형", "💎 **보석:** 아쿠아마린", "🐶 **영어 이름:** Jaden", "🎸 **취미:** 기타", "🥋 **특기:** 비트박스"],
                "jp": ["🩸 **血液型:** A型", "💎 **宝石:** アクアマリン", "🐶 **英語名:** Jaden", "🎸 **趣味:** ギター", "🥋 **特技:** ビートボックス"],
                "cn": ["🩸 **血型:** A型", "💎 **宝石:** 海蓝宝", "🐶 **英文名:** Jaden", "🎸 **爱好:** 吉他", "🥋 **特长:** Beatbox"]
            },
            "songs": ["STUPID", "JIKJIN"],
            "covers": ["Still Life"]
        },
        # --- 4. JUNKYU ---
        {
            "name": "Junkyu",
            "img": "junkyu.jpg",
            "history_image": "",
            "birthday": "2000.09.09",
            "height": "178 cm",
            "mbti": "INFJ",
            "display_name": {"th": "คิม จุนกยู", "en": "Kim Junkyu", "kr": "김준규", "jp": "キム・ジュンギュ", "cn": "金俊奎"},
            "position": {"th": "โวคอล, วิชวล", "en": "Vocalist, Visual", "kr": "보컬, 비주얼", "jp": "ボーカル, ビジュアル", "cn": "主唱, 门面"},
            "nickname": {"th": "Koala", "en": "Koala", "kr": "코알라", "jp": "コアラ", "cn": "考拉"},
            "history": {
                "th": "อดีตนายแบบเด็ก ฉายา 'Physical Genius' เสียงร้องเป็นเอกลักษณ์ (YG Style) บุคลิกขี้เล่น",
                "en": "Former child model. 'Physical Genius'. Unique YG-style vocals. Playful.",
                "kr": "아역 모델 출신. '피지컬 천재'. 독특한 YG 스타일 보컬. 장난기 많음.",
                "jp": "元子役。「フィジカル天才」。ユニークなYGボイス。遊び心がある。",
                "cn": "前童模。'脸蛋天才'。独特的YG嗓音。性格顽皮。"
            },
            "biography": {
                "th": "จุนกยูเข้า YG ในปี 2013 เคยเข้าร่วมรายการ MIXNINE แต่ตกรอบ ซึ่งทำให้เขาสูญเสียความมั่นใจ แต่ในรายการ YG Treasure Box เขาได้ก้าวข้ามขีดจำกัดของตัวเองและพิสูจน์ฝีมือจนกลายเป็นหนึ่งในสมาชิกที่ได้รับความนิยมสูงสุดและได้เดบิวต์เป็นคนแรกๆ",
                "en": "Joined YG in 2013. Lost confidence after MIXNINE elimination but regained it in Treasure Box, becoming a top member and debuting early.",
                "kr": "2013년 입사. 믹스나인 탈락으로 위축되었으나 보석함에서 극복하고 인기 멤버로 등극.",
                "jp": "2013年入社。MIXNINE脱落で自信を失うも宝石箱で克服し、人気メンバーとしてデビュー。",
                "cn": "2013年加入。虽在MIXNINE淘汰但在宝石盒中重拾自信，成为人气成员。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** O", "💎 **Gemstone:** Diamond", "🐶 **Eng Name:** David", "🎹 **Skill:** Piano", "🐱 **Cats:** Ruby, Aengdu"],
                "en": ["🩸 **Blood Type:** O", "💎 **Gemstone:** Diamond", "🐶 **Eng Name:** David", "🎹 **Skill:** Piano", "🐱 **Cats:** Ruby, Aengdu"],
                "kr": ["🩸 **혈액형:** O형", "💎 **보석:** 다이아몬드", "🐶 **영어 이름:** David", "🎹 **특기:** 피아노", "🐱 **반려묘:** 루비, 앵두"],
                "jp": ["🩸 **血液型:** O型", "💎 **宝石:** ダイヤモンド", "🐶 **英語名:** David", "🎹 **特技:** ピアノ", "🐱 **猫:** ルビー, エンドゥ"],
                "cn": ["🩸 **血型:** O型", "💎 **宝石:** 钻石", "🐶 **英文名:** David", "🎹 **特长:** 钢琴", "🐱 **宠物:** Ruby, Aengdu"]
            },
            "songs": ["MOVE", "I WANT YOUR LOVE"],
            "covers": ["Latch"]
        },
        # --- 5. JAEHYUK ---
        {
            "name": "Jaehyuk",
            "img": "jaehyuk.jpg",
            "history_image": "",
            "birthday": "2001.07.23",
            "height": "178 cm",
            "mbti": "INFP",
            "display_name": {"th": "ยุน แจฮยอก", "en": "Yoon Jaehyuk", "kr": "윤재혁", "jp": "ユン・ジェヒョク", "cn": "尹材赫"},
            "position": {"th": "โวคอล", "en": "Vocalist", "kr": "보컬", "jp": "ボーカル", "cn": "副主唱"},
            "nickname": {"th": "Chow Chow", "en": "Chow Chow", "kr": "윤다정", "jp": "ジェヒョク", "cn": "尹多情"},
            "history": {
                "th": "ถูกแมวมองจากค่ายใหญ่ทาบทามข้างถนน! เป็นคนอบอุ่น พัฒนาตัวเองอย่างหนักจนได้เดบิวต์",
                "en": "Street-casted by major agencies! Warm personality. Worked hard to debut.",
                "kr": "대형 기획사 길거리 캐스팅! 따뜻한 성격. 노력으로 데뷔 성공.",
                "jp": "大手事務所にスカウトされた！温かい性格。努力でデビューを掴んだ。",
                "cn": "被大社街头星探发掘！性格温暖。努力出道。"
            },
            "biography": {
                "th": "แจฮยอกถูกแคสติ้งข้างถนนโดย YG (และค่ายใหญ่อื่นๆ) เขาฝึกได้ไม่นานก่อนเข้าร่วม Treasure Box ทำให้ช่วงแรกตามคนอื่นไม่ทัน แต่ด้วยความพยายามที่ไม่ยอมแพ้ เขาพัฒนาตัวเองอย่างรวดเร็วจนประธาน YG ประทับใจและเลือกให้เป็นสมาชิกของ TREASURE ในที่สุด",
                "en": "Street-casted by YG. Had short training before Treasure Box but improved rapidly through sheer effort, impressing YG to select him.",
                "kr": "YG 길거리 캐스팅. 짧은 연습 기간에도 불구하고 엄청난 노력으로 급성장하여 데뷔 멤버로 발탁됨.",
                "jp": "YGにスカウト。練習期間は短かったが、猛烈な努力で急成長し、デビューメンバーに選ばれた。",
                "cn": "YG街头星探发掘。练习时间虽短，但凭借巨大努力飞速进步，最终入选。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** O", "💎 **Gemstone:** Pearl", "🐶 **Eng Name:** Kevin", "🤚 **Hand:** Left-handed", "💍 **Charm:** Ring Ring"],
                "en": ["🩸 **Blood Type:** O", "💎 **Gemstone:** Pearl", "🐶 **Eng Name:** Kevin", "🤚 **Hand:** Left-handed", "💍 **Charm:** Ring Ring"],
                "kr": ["🩸 **혈액형:** O형", "💎 **보석:** 진주", "🐶 **영어 이름:** Kevin", "🤚 **손:** 왼손잡이", "💍 **매력:** 링링"],
                "jp": ["🩸 **血液型:** O型", "💎 **宝石:** 真珠", "🐶 **英語名:** Kevin", "🤚 **利き手:** 左利き", "💍 **魅力:** Ring Ring"],
                "cn": ["🩸 **血型:** O型", "💎 **宝石:** 珍珠", "🐶 **英文名:** Kevin", "🤚 **惯用手:** 左手", "💍 **魅力:** Ring Ring"]
            },
            "songs": ["HELLO", "CLAP!"],
            "covers": ["DON'T FLIRT"]
        },
        # --- 6. ASAHI ---
        {
            "name": "Asahi",
            "img": "asahi.jpg",
            "history_image": "",
            "birthday": "2001.08.20",
            "height": "172 cm",
            "mbti": "INFP",
            "display_name": {"th": "ฮามาดะ อาซาฮิ", "en": "Hamada Asahi", "kr": "하마다 아사히", "jp": "浜田朝光", "cn": "滨田朝光"},
            "position": {"th": "โวคอล, วิชวล", "en": "Vocalist, Visual", "kr": "보컬, 비주얼", "jp": "ボーカル, ビジュアル", "cn": "副主唱, 门面"},
            "nickname": {"th": "Robot", "en": "Robot", "kr": "로봇", "jp": "ロボット", "cn": "机器人"},
            "history": {
                "th": "จากโอซาก้า มีโลกส่วนตัวสูงและอารมณ์ขันหน้าตาย (4D) เก่งศิลปะและแต่งเพลง (Orange, Thank You)",
                "en": "From Osaka. 4D personality. Talented in art/composing (Orange, Thank You).",
                "kr": "오사카 출신. 4차원 성격. 예술과 작곡 능력 보유 (오렌지, 땡큐).",
                "jp": "大阪出身。4次元な性格。アートと作曲の才能（オレンジ、Thank You）。",
                "cn": "来自大阪。四次元性格。擅长艺术和作曲（Orange, Thank You）。"
            },
            "biography": {
                "th": "อาซาฮิเข้าร่วม YG ในปี 2018 เขาเป็นคนเงียบๆ ในรายการ Treasure Box แต่ฉายแววความสามารถด้านการแต่งเพลงและศิลปะ เขาเป็นสมาชิกคนสุดท้ายที่ถูกประกาศชื่อในยูนิต Magnum ก่อนจะรวมเป็น TREASURE",
                "en": "Joined YG in 2018. Quiet in Treasure Box but showed composing/art talent. Final member announced for Magnum before merger.",
                "kr": "2018년 입사. 조용하지만 작곡과 예술에 재능을 보임. 매그넘의 마지막 멤버로 발표됨.",
                "jp": "2018年入社。静かだが作曲とアートの才能を発揮。マグナムの最後のメンバーとして発表された。",
                "cn": "2018年加入。虽然安静但展现了作曲和艺术天赋。Magnum最后公布的成员。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** AB", "💎 **Gemstone:** Ruby", "🐶 **Eng Name:** Arthur", "🎨 **Hobby:** Drawing", "⚽ **Sport:** Football"],
                "en": ["🩸 **Blood Type:** AB", "💎 **Gemstone:** Ruby", "🐶 **Eng Name:** Arthur", "🎨 **Hobby:** Drawing", "⚽ **Sport:** Football"],
                "kr": ["🩸 **혈액형:** AB형", "💎 **보석:** 루비", "🐶 **영어 이름:** Arthur", "🎨 **취미:** 그림", "⚽ **운동:** 축구"],
                "jp": ["🩸 **血液型:** AB型", "💎 **宝石:** ルビー", "🐶 **英語名:** Arthur", "🎨 **趣味:** 絵画", "⚽ **スポーツ:** サッカー"],
                "cn": ["🩸 **血型:** AB型", "💎 **宝石:** 红宝石", "🐶 **英文名:** Arthur", "🎨 **爱好:** 绘画", "⚽ **运动:** 足球"]
            },
            "songs": ["ORANGE", "THANK YOU"],
            "covers": ["Lay Me Down"]
        },
        # --- 7. DOYOUNG ---
        {
            "name": "Doyoung",
            "img": "doyoung.jpg",
            "history_image": "",
            "birthday": "2003.12.04",
            "height": "177 cm",
            "mbti": "ESTP",
            "display_name": {"th": "คิม โดยอง", "en": "Kim Doyoung", "kr": "김도영", "jp": "キム・ドヨン", "cn": "金道荣"},
            "position": {"th": "เมนแดนซ์, โวคอล", "en": "Main Dancer, Vocalist", "kr": "메인 댄서, 보컬", "jp": "メインダンサー, ボーカル", "cn": "主舞, 副主唱"},
            "nickname": {"th": "Dobby", "en": "Dobby", "kr": "도비", "jp": "ドビ", "cn": "Dobby"},
            "history": {
                "th": "เข้า YG ตอนอายุ 11 ปี เป็นแฟชั่นนิสต้า ทักษะการเต้นเฉียบคมและไลน์เต้นสวยงาม",
                "en": "Joined YG at 11. Fashionista. Sharp and beautiful dance lines.",
                "kr": "11세에 YG 입사. 패셔니스타. 춤선이 예쁘고 정확함.",
                "jp": "11歳でYG入社。ファッショニスタ。ダンスのラインが美しい。",
                "cn": "11岁加入YG。时尚达人。舞蹈线条优美。"
            },
            "biography": {
                "th": "โดยองเริ่มฝึกเต้นมาตั้งแต่เด็กและเข้า YG ตั้งแต่อายุ 11 ปี เขาฝึกพร้อมกับจุนกยูมาอย่างยาวนาน ในรายการ Treasure Box เขาเกือบไม่ได้เดบิวต์แต่ด้วยความสามารถที่โดดเด่นทำให้เขาได้รับโอกาสในยูนิต Magnum",
                "en": "Started dancing young, joined YG at 11. Trained long with Junkyu. Almost didn't debut but his skills earned him a spot in Magnum.",
                "kr": "어릴 때부터 춤을 췄고 11세에 입사. 준규와 오랜 연습. 탈락 위기였으나 실력으로 매그넘 합류.",
                "jp": "幼少期からダンスを始め11歳で入社。ジュンギュと長く練習。脱落の危機を実力で乗り越えマグナムへ。",
                "cn": "从小跳舞，11岁加入。与俊奎一起练习很久。凭实力入选Magnum。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Sapphire", "🐶 **Eng Name:** Sam", "🛹 **Hobby:** Skateboarding", "🍳 **Skill:** Cooking"],
                "en": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Sapphire", "🐶 **Eng Name:** Sam", "🛹 **Hobby:** Skateboarding", "🍳 **Skill:** Cooking"],
                "kr": ["🩸 **혈액형:** B형", "💎 **보석:** 사파이어", "🐶 **영어 이름:** Sam", "🛹 **취미:** 스케이트보드", "🍳 **특기:** 요리"],
                "jp": ["🩸 **血液型:** B型", "💎 **宝石:** サファイア", "🐶 **英語名:** Sam", "🛹 **趣味:** スケボー", "🍳 **特技:** 料理"],
                "cn": ["🩸 **血型:** B型", "💎 **宝石:** 蓝宝石", "🐶 **英文名:** Sam", "🛹 **爱好:** 滑板", "🍳 **特长:** 烹饪"]
            },
            "songs": ["DARARI", "HELLO"],
            "covers": ["Babushka Boi - A$AP Rocky"]
        },
        # --- 8. HARUTO ---
        {
            "name": "Haruto",
            "img": "haruto.jpg",
            "history_image": "",
            "birthday": "2004.04.05",
            "height": "183.2 cm",
            "mbti": "INFP",
            "display_name": {"th": "วาตานาเบะ ฮารุโตะ", "en": "Watanabe Haruto", "kr": "와타나베 하루토", "jp": "渡辺温斗", "cn": "渡边温斗"},
            "position": {"th": "เมนแร็ปเปอร์, วิชวล", "en": "Main Rapper, Visual", "kr": "메인 래퍼, 비주얼", "jp": "メインラッパー, ビジュアル", "cn": "主Rapper, 门面"},
            "nickname": {"th": "Ruto", "en": "Ruto", "kr": "루토", "jp": "ルト", "cn": "Ruto"},
            "history": {
                "th": "จากฟุกุโอกะ สูงที่สุดในวง (183+ ซม.) แร็ปโทนต่ำมีเสน่ห์ (Deep Voice) ครอบครัวเป็นแฟนคลับ BIGBANG",
                "en": "From Fukuoka. Tallest member. Deep voice rapper. Family loves BIGBANG.",
                "kr": "후쿠오카 출신. 최장신. 로우톤 래퍼. 가족이 빅뱅 팬.",
                "jp": "福岡出身。最長身。低音ラッパー。家族がBIGBANGファン。",
                "cn": "来自福冈。最高成员。低音Rapper。全家是BIGBANG粉丝。"
            },
            "biography": {
                "th": "ฮารุโตะเข้า YG Japan เมื่อปี 2017 คุณแม่ของเขาเป็นแฟนคลับตัวยงของ BIGBANG ทำให้เขาซึมซับดนตรีมาตั้งแต่เด็ก ในรายการ Treasure Box เขาโดดเด่นด้วยเสียงแร็ปที่ต่ำและหน้าตาที่หล่อเหลา จนได้เดบิวต์เป็นสมาชิกคนแรกของยูนิต Treasure",
                "en": "Joined YG Japan in 2017. His mom is a huge BIGBANG fan. Stood out with his deep voice/visuals in Treasure Box, debut member #1.",
                "kr": "2017년 YG Japan 입사. 어머니가 빅뱅 팬. 보석함에서 낮은 목소리와 비주얼로 주목받아 트레저 첫 멤버로 확정.",
                "jp": "2017年YG Japan入社。母がBIGBANGファン。宝石箱で低音ボイスとビジュアルで注目され、最初のデビューメンバーに。",
                "cn": "2017年加入YG Japan。母亲是BIGBANG粉丝。凭低音和颜值成为首位确定出道的成员。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Opal", "🐶 **Eng Name:** Travis", "😴 **Hobby:** Sleeping", "🎳 **Skill:** Bowling"],
                "en": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Opal", "🐶 **Eng Name:** Travis", "😴 **Hobby:** Sleeping", "🎳 **Skill:** Bowling"],
                "kr": ["🩸 **혈액형:** B형", "💎 **보석:** 오팔", "🐶 **영어 이름:** Travis", "😴 **취미:** 잠자기", "🎳 **특기:** 볼링"],
                "jp": ["🩸 **血液型:** B型", "💎 **宝石:** オパール", "🐶 **英語名:** Travis", "😴 **趣味:** 寝ること", "🎳 **特技:** ボウリング"],
                "cn": ["🩸 **血型:** B型", "💎 **宝石:** 蛋白石", "🐶 **英文名:** Travis", "😴 **爱好:** 睡觉", "🎳 **特长:** 保龄球"]
            },
            "songs": ["G.O.A.T", "VolKno"],
            "covers": ["Stack It Up"]
        },
        # --- 9. JEONGWOO ---
        {
            "name": "Jeongwoo",
            "img": "jeongwoo.jpg",
            "history_image": "",
            "birthday": "2004.09.28",
            "height": "181 cm",
            "mbti": "ISFP",
            "display_name": {"th": "พัค จองอู", "en": "Park Jeongwoo", "kr": "박정우", "jp": "パク・ジョンウ", "cn": "朴炡禹"},
            "position": {"th": "เมนโวคอล", "en": "Main Vocalist", "kr": "메인 보컬", "jp": "メインボーカル", "cn": "主唱"},
            "nickname": {"th": "Choco Jeongwoo", "en": "Choco Jeongwoo", "kr": "초코 정우", "jp": "チョコ・ジョンウ", "cn": "巧克力炡禹"},
            "history": {
                "th": "จากอิกซาน เพื่อนสนิทจองฮวาน (Ik-san Boys) เสียงร้องทรงพลัง (Vocal Genius) Mood Maker ของวง",
                "en": "From Iksan. Junghwan's best friend. Powerful vocals. Mood maker.",
                "kr": "익산 출신. 정환의 절친. 파워풀한 보컬. 분위기 메이커.",
                "jp": "益山出身。ジョンファンの親友。パワフルなボーカル。ムードメーカー。",
                "cn": "来自益山。庭焕好友。强力主唱。气氛制造者。"
            },
            "biography": {
                "th": "จองอูสมัครออดิชั่นเข้า YG พร้อมกับจองฮวานจากสถาบันเดียวกันที่อิกซาน เขาได้รับการยกย่องว่าเป็น 'Vocal Genius' ตั้งแต่เริ่มรายการ Treasure Box แม้จะฝึกมาไม่นาน แต่พรสวรรค์ของเขาทำให้ได้รับเลือกเป็นหนึ่งในเมนโวคอลของวง",
                "en": "Auditioned with Junghwan from Iksan. Praised as 'Vocal Genius' in Treasure Box despite short training. Selected as Main Vocal.",
                "kr": "익산에서 정환과 함께 오디션 합격. 짧은 연습생 기간에도 '보컬 천재'로 불리며 메인 보컬로 선발됨.",
                "jp": "益山でジョンファンと共に合格。練習期間は短かったが「ボーカル天才」と呼ばれメインボーカルに。",
                "cn": "与庭焕一同在益山入选。练习虽短但被称为'声乐天才'，入选主唱。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** O", "💎 **Gemstone:** Topaz", "🐶 **Eng Name:** Justin", "👂 **Charm:** Ears", "👕 **Shoulders:** Broad"],
                "en": ["🩸 **Blood Type:** O", "💎 **Gemstone:** Topaz", "🐶 **Eng Name:** Justin", "👂 **Charm:** Ears", "👕 **Shoulders:** Broad"],
                "kr": ["🩸 **혈액형:** O형", "💎 **보석:** 토파즈", "🐶 **영어 이름:** Justin", "👂 **매력:** 귀", "👕 **어깨:** 넓음"],
                "jp": ["🩸 **血液型:** O型", "💎 **宝石:** トパーズ", "🐶 **英語名:** Justin", "👂 **魅力:** 耳", "👕 **肩:** 広い"],
                "cn": ["🩸 **血型:** O型", "💎 **宝石:** 托帕石", "🐶 **英文名:** Justin", "👂 **魅力:** 耳朵", "👕 **肩膀:** 宽肩"]
            },
            "songs": ["DARARI", "MMM"],
            "covers": ["Superstar", "Life Is Worth Living", "Weight In Gold ", "Nothing's Gonna Change My Love For You"]
        },
        # --- 10. JUNGHWAN ---
        {
            "name": "Junghwan",
            "img": "junghwan.jpg",
            "history_image": "",
            "birthday": "2005.02.18",
            "height": "180.3 cm",
            "mbti": "ENFP-T",
            "display_name": {"th": "โซ จองฮวาน", "en": "So Junghwan", "kr": "소정환", "jp": "ソ・ジョンファン", "cn": "苏庭焕"},
            "position": {"th": "โวคอล, แดนซ์, มักเน่", "en": "Vocalist, Dancer, Maknae", "kr": "보컬, 댄서, 막내", "jp": "ボーカル, ダンサー, 末っ子", "cn": "副主唱, 舞担, 忙内"},
            "nickname": {"th": "Super King Cow Baby", "en": "Super King Cow Baby", "kr": "소해금", "jp": "ジョンファン", "cn": "超级牛宝宝"},
            "history": {
                "th": "น้องเล็ก (Maknae) อดีตสมาชิก K-TIGERS เก่งเทควันโดและอะโครบาติก เติบโตไวมาก",
                "en": "Maknae. Former K-TIGERS. Skilled in Taekwondo/Acrobatics. Grows fast.",
                "kr": "막내. 전 K-TIGERS. 태권도와 아크로바틱 능숙. 폭풍 성장.",
                "jp": "末っ子。元K-TIGERS。テコンドーとアクロバットが得意。成長が早い。",
                "cn": "忙内。前K-TIGERS。擅长跆拳道和杂技。暴风成长。"
            },
            "biography": {
                "th": "จองฮวานเป็นสมาชิกอายุน้อยที่สุด เคยอยู่ในทีมเทควันโดระดับประเทศ K-TIGERS มาก่อน เขาเริ่มต้นใน Treasure Box ด้วยลุคเด็กน้อยแต่มีความสามารถล้นเหลือ จนได้อันดับ 1 ในการประกาศผลรอบสุดท้าย และกลายเป็นสมาชิกคนแรกของ TREASURE",
                "en": "Youngest member, formerly in K-TIGERS taekwondo team. Ranked 1st in Treasure Box finale, becoming the very first confirmed TREASURE member.",
                "kr": "막내이자 전 K-TIGERS 출신. 보석함 최종 1위를 차지하며 트레저의 첫 번째 멤버로 확정됨.",
                "jp": "最年少で元K-TIGERS。宝石箱で最終1位となり、TREASUREの最初のメンバーとして確定した。",
                "cn": "忙内，前K-TIGERS成员。在宝石盒获得最终第一名，成为TREASURE首位确定成员。"
            },
            "facts": {
                "th": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Turquoise", "🐶 **Eng Name:** John", "🍩 **Food:** Donuts", "🥋 **Skill:** Taekwondo"],
                "en": ["🩸 **Blood Type:** B", "💎 **Gemstone:** Turquoise", "🐶 **Eng Name:** John", "🍩 **Food:** Donuts", "🥋 **Skill:** Taekwondo"],
                "kr": ["🩸 **혈액형:** B형", "💎 **보석:** 터키석", "🐶 **영어 이름:** John", "🍩 **음식:** 도넛", "🥋 **특기:** 태권도"],
                "jp": ["🩸 **血液型:** B型", "💎 **宝石:** ターコイズ", "🐶 **英語名:** John", "🍩 **食べ物:** ドーナツ", "🥋 **特技:** テコンドー"],
                "cn": ["🩸 **血型:** B型", "💎 **宝石:** 绿松石", "🐶 **英文名:** John", "🍩 **食物:** 甜甜圈", "🥋 **特长:** 跆拳道"]
            },
            "songs": ["BOY", "I LOVE YOU"],
            "covers": ["Lie", "소정환의 졸업"]
        }
    ]
# ============================================
# 🎂 BIRTHDAY COUNTDOWN
# ============================================
def get_next_birthday(birthday_str: str) -> Tuple[int, datetime]:
    try:
        if not birthday_str or birthday_str == '-':
            return 365, datetime.now()
        parts = birthday_str.split('.')
        if len(parts) != 3: return 365, datetime.now()
        today = datetime.now()
        month, day = int(parts[1]), int(parts[2])
        next_birthday = datetime(today.year, month, day)
        if next_birthday < today:
            next_birthday = datetime(today.year + 1, month, day)
        days_until = (next_birthday - today).days
        return days_until, next_birthday
    except (ValueError, IndexError, TypeError):
        return 365, datetime.now()

def render_birthday_section(members: List[Dict], t: Dict, lang: str):
    st.markdown(f"<h3 style='text-align:center; color: var(--primary); margin: 30px 0 20px 0;'>{t.get('birthday_countdown', '🎂 Birthday Countdown')}</h3>", unsafe_allow_html=True)
    upcoming = []
    for m in members:
        days, date = get_next_birthday(m.get('birthday', '2000.01.01'))
        upcoming.append((m, days, date))
    upcoming.sort(key=lambda x: x[1])
    cols = st.columns(min(3, len(upcoming)))
    for i, (member, days, date) in enumerate(upcoming[:3]):
        with cols[i]:
            member_display_name = member.get('display_name', {}).get(lang, member.get('name', 'Member'))
            member_birthday = member.get('birthday', '-')
            st.markdown(f"""
            <div class="birthday-card">
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🎂</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: var(--primary); margin-bottom: 5px;">{member_display_name}</div>
                    <div style="font-size: 0.9rem; color: #888; margin-bottom: 10px;">{member_birthday}</div>
                    <div style="font-size: 1.5rem; font-weight: 900; color: var(--primary);">{days}</div>
                    <div style="font-size: 0.8rem; color: #888;">{t.get('days', 'days')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# 📱 SIDEBAR
# ============================================
def render_sidebar(members: List[Dict], t: Dict, lang: str):

    current_params = st.query_params.to_dict()
        
    st.markdown("""
        <style>
            .lang-container {
                display: flex;
                justify-content: flex-end;
                gap: 12px;
                margin-bottom: 10px;
                flex-wrap: wrap;
            }
            .lang-btn {
                text-decoration: none;
                font-size: 1.8rem;
                filter: grayscale(100%);
                opacity: 0.6;
                transition: all 0.3s ease;
                line-height: 1;
                cursor: pointer;
            }
            .lang-btn:hover {
                transform: scale(1.2);
                filter: grayscale(0%);
                opacity: 1;
            }
            .lang-btn.active {
                filter: grayscale(0%);
                opacity: 1;
                transform: scale(1.1);
                text-shadow: 0 0 15px rgba(50, 224, 196, 0.6);
            }
            @media (max-width: 768px) {
                .lang-container {
                    justify-content: center;
                }
            }
        </style>
        """, unsafe_allow_html=True)

    lang_options = {'th': '🇹🇭', 'en': '🇬🇧', 'kr': '🇰🇷', 'jp': '🇯🇵', 'cn': '🇨🇳'}
        
    html_content = '<div class="lang-container">'
    for code, flag in lang_options.items():
            params = current_params.copy()
            params['lang'] = code
            query_string = urllib.parse.urlencode(params)
            is_active = "active" if lang == code else ""
            html_content += f'<a href="?{query_string}" target="_self" class="lang-btn {is_active}">{flag}</a>'
    html_content += '</div>'
        
    st.markdown(html_content, unsafe_allow_html=True)
    
    with st.sidebar:
        total_songs = sum(len(m.get('songs', [])) for m in members)
        st.markdown(f"<h2 style='color:#32E0C4; text-align:center;'>{t.get('rec_title', '✨ Recommended')}</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top:0;'>", unsafe_allow_html=True)
        
        # MINI STATS
        st.markdown(f"""
        <div class="mini-stat-container">
            <div class="mini-stat-box">
                <span class="mini-stat-icon">👥</span>
                <div class="mini-stat-number">{len(members)}</div>
                <div class="mini-stat-label">{t.get('total_members', 'Members')}</div>
            </div>
            <div class="mini-stat-box" style="border-left: 1px solid var(--border); border-right: 1px solid var(--border);">
                <span class="mini-stat-icon">💖</span>
                <div class="mini-stat-number">{len(st.session_state.favorites)}</div>
                <div class="mini-stat-label">Favs</div>
            </div>
            <div class="mini-stat-box">
                <span class="mini-stat-icon">🎵</span>
                <div class="mini-stat-number">{total_songs}+</div>
                <div class="mini-stat-label">Songs</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- NAVIGATION BUTTONS ---
        st.markdown(f"<h4 style='color:var(--secondary-text); font-size:0.9rem; margin-bottom:10px;'>MENU</h4>", unsafe_allow_html=True)
        
        if st.button(f"{t.get('menu_home', '🏠 Home / Members')}", use_container_width=True, type="primary" if st.session_state.page == 'members' else "secondary"):
            st.session_state.page = 'members'
            st.rerun()
            
        if st.button(f"{t.get('menu_about', '🏢 About Group')}", use_container_width=True, type="primary" if st.session_state.page == 'about' else "secondary"):
            st.session_state.page = 'about'
            st.rerun()
            
        if st.button(f"{t.get('menu_cheer', '💬 Fan Zone')}", use_container_width=True, type="primary" if st.session_state.page == 'cheer' else "secondary"):
            st.session_state.page = 'cheer'
            st.rerun()

        st.markdown("---")
        
        st.markdown(f"<div style='text-align:center; margin-bottom:10px; color:#aaa; font-size:0.9rem;'>{t.get('rec_playlist_1', '🎬 OFFICIAL M/V')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <a href="https://www.youtube.com/watch?v=zjJs3I4hsCg&list=PLG4U66ceLh82hyGL6sE6Cp1nG2uNLtlAm" target="_blank" style="text-decoration:none;">
            <div class="rec-card" style="padding:0; overflow:hidden; position:relative;">
                <img src="https://i.ytimg.com/vi/zjJs3I4hsCg/hqdefault.jpg" style="width:100%; display:block; opacity:0.9; transition:0.3s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.9">
                <div style="position:absolute; bottom:0; left:0; width:100%; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); color:#32E0C4; padding:10px; font-weight:bold; font-size:0.9rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">▶ WATCH DANCE PRACTICE VIDEO</div>
            </div>
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; margin-bottom:10px; color:#aaa; font-size:0.9rem;'>{t.get('rec_playlist_2', '💎 TREASURE MAP')}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <a href="https://www.youtube.com/playlist?list=PLG4U66ceLh80BCE_NxXdEsltXlgpchO6R" target="_blank" style="text-decoration:none;">
            <div class="rec-card" style="padding:0; overflow:hidden; position:relative;">
                <img src="https://i.ytimg.com/vi/M4oBygBkgGQ/hqdefault.jpg" style="width:100%; display:block; opacity:0.9; transition:0.3s;" onmouseover="this.style.opacity=1" onmouseout="this.style.opacity=0.9">
                <div style="position:absolute; bottom:0; left:0; width:100%; background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); color:#32E0C4; padding:10px; font-weight:bold; font-size:0.9rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8);">▶ TREASURE MAP</div>
            </div>
        </a>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        
        # ตรวจสอบสถานะ Admin
        is_admin_active = st.session_state.get('is_admin_active', False)
        
        # จัด Layout ปุ่มให้อยู่ตรงกลางสวยๆ
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if is_admin_active:
                # ถ้าล็อกอินแล้ว ปุ่มจะเป็นสีเขียว กดเพื่อ Logout
                if st.button("🔓 Active", key="btn_admin_logout", type="primary", use_container_width=True, help="Click to Logout"):
                    st.session_state.is_admin_active = False
                    st.rerun()
            else:
                # ถ้ายังไม่ล็อกอิน ปุ่มจะเป็นรูปกุญแจ กดเพื่อเรียก Modal
                if st.button("🔐", key="btn_admin_login", use_container_width=True, help="Admin Login"):
                    admin_login_modal()

# ============================================
# 🎯 MEMBER GRID RENDERING
# ============================================
def render_member_grid(members: List[Dict], t: Dict, lang: str, all_members: List[Dict], show_heart: bool = False):
    cols_per_row = AppConfig.COLS_PER_ROW
    for i in range(0, len(members), cols_per_row):
        cols = st.columns(min(cols_per_row, len(members) - i))
        for j, col in enumerate(cols):
            with col:
                real_idx = i + j
                if real_idx < len(members):
                    m = members[real_idx]
                    try:
                        member_name = m.get('name', 'Member')
                        member_img = m.get('img', '')
                        member_display_name = m.get('display_name', {}).get(lang, member_name)
                        img_src = get_image_src(member_img, member_name)
                        heart_html = '<div class="favorite-heart">❤️</div>' if show_heart else ''
                        actual_idx = next((idx for idx, member in enumerate(all_members) if member.get('name') == member_name), 0)
                        safe_name = urllib.parse.quote(member_name)
                        st.markdown(f'''<div style="position: relative;">
<a href="?id={actual_idx}&lang={lang}" target="_self" class="member-card-link">
<div class="member-card-overlay">
        {heart_html}
<img src="{img_src}" class="member-img-full" alt="{member_display_name}" onerror="this.src='https://ui-avatars.com/api/?name={safe_name}&background=32E0C4&color=fff&size=400'">
<div class="member-name-overlay">{member_display_name}</div>
</div>
</a></div>''', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

# ============================================
# 🏢 GROUP INFO RENDERER (UPDATED LINKS)
# ============================================
def render_group_info(t: Dict, lang: str):
    """Render About Group section (Full Page)"""
    
    links = {
        "tmap": "https://www.youtube.com/results?search_query=TREASURE+MAP+EP.1",
        "tmi": "https://www.youtube.com/results?search_query=TREASURE+T.M.I",
        "3min": "https://www.youtube.com/results?search_query=3+Minute+TREASURE",
        "fact": "https://www.youtube.com/results?search_query=TREASURE+Fact+Check",
        "ttalk": "https://www.youtube.com/results?search_query=TREASURE+T-Talk",
        "solo": "https://www.youtube.com/results?search_query=TREASURE+Shining+Solo"
    }

    st.markdown(f"""
<div style="background: var(--glass); border-radius: 20px; padding: 30px; border: 1px solid var(--border); margin-bottom: 30px;">
    <h2 style="color: var(--primary); text-align: center; margin-bottom: 20px;">💎 TREASURE PROFILE</h2>
        
<div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin-bottom: 30px;">
    <div style="flex: 1; min-width: 250px; background: rgba(50, 224, 196, 0.1); padding: 15px; border-radius: 12px; text-align: center;">
    <div style="font-size: 2rem;">📅</div>
    <div style="font-weight: bold; color: var(--primary);">{t.get('debut_date', 'Debut Date')}</div>
    <div>August 7, 2020</div>
    </div>
<div style="flex: 1; min-width: 250px; background: rgba(50, 224, 196, 0.1); padding: 15px; border-radius: 12px; text-align: center;">
    <div style="font-size: 2rem;">💎</div>
    <div style="font-weight: bold; color: var(--primary);">{t.get('fandom', 'Fandom')}</div>
    <div>Treasure Maker (Teume)</div>
    </div>
<div style="flex: 1; min-width: 250px; background: rgba(50, 224, 196, 0.1); padding: 15px; border-radius: 12px; text-align: center;">
    <div style="font-size: 2rem;">📺</div>
    <div style="font-weight: bold; color: var(--primary);">{t.get('origin', 'Origin')}</div>
    <div>YG Treasure Box</div>
    </div>
</div>

<p style="text-align: center; line-height: 1.6; margin-bottom: 30px; font-size: 1.1rem; color: var(--text-color);">
            {t.get('group_desc', '')}
</p>

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
<div style="background: var(--card-bg); padding: 20px; border-radius: 15px; border: 1px solid var(--border);">
<h3 style="color: var(--primary);">💿 {t.get('albums', 'Discography')}</h3>
<ul style="list-style-type: none; padding: 0; line-height: 1.8;">
    <li>✨ <strong>2020:</strong> THE FIRST STEP Series (Chapter 1, 2, 3)</li>
    <li>🔥 <strong>2021:</strong> THE FIRST STEP: TREASURE EFFECT</li>
    <li>⚡ <strong>2022:</strong> THE SECOND STEP: CHAPTER ONE & TWO</li>
    <li>🚀 <strong>2023:</strong> REBOOT (2nd Full Album)</li>
    <li>🦍 <strong>2024:</strong> KING KONG (Digital Single)</li>
    <li>🔮 <strong>2026:</strong> LOVE PULSE (Latest)</li>
</ul>
</div>
<div style="display: flex; flex-direction: column; gap: 20px;">
<div style="background: var(--card-bg); padding: 20px; border-radius: 15px; border: 1px solid var(--border);">
<h3 style="color: var(--primary);">🎬 {t.get('shows', 'Web Shows')}</h3>
<div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        
<a href="{links['tmap']}" target="_blank" class="variety-btn" style="border-color: var(--primary); background: rgba(50, 224, 196, 0.1);">
        💎 Treasure Map ↗
    </a>
<a href="{links['tmi']}" target="_blank" class="variety-btn">T.M.I ↗</a>
<a href="{links['3min']}" target="_blank" class="variety-btn">3-Minute Treasure ↗</a>
<a href="{links['fact']}" target="_blank" class="variety-btn">Fact Check ↗</a>
<a href="{links['ttalk']}" target="_blank" class="variety-btn">T-Talk ↗</a>
<a href="{links['solo']}" target="_blank" class="variety-btn">✨ Shining Solo ↗</a>

</div>
</div>
                
<div style="background: var(--card-bg); padding: 20px; border-radius: 15px; border: 1px solid var(--border); flex: 1;">
    <h3 style="color: var(--primary);">{t.get('award_title', 'Awards')}</h3>
<div style="white-space: pre-line; line-height: 1.6;">
                        {t.get('award_desc', '')}
</div>
</div>
</div>
</div>
</div>
    """, unsafe_allow_html=True)

# ============================================
# 💬 MEMBER MODAL
# ============================================
def show_member_modal(sel: Dict, t: Dict, lang: str, all_members: List[Dict]):
    @st.dialog(f"💎 {sel.get('name', 'Member')}", width="large")
    def modal_content():
        try:
            member_name = sel.get('name', 'Member')
            member_img = sel.get('img', '')
            history_img = sel.get('history_image', '')
            
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                img_src = get_image_src(member_img, member_name)
                safe_name = urllib.parse.quote(member_name)
                st.markdown(f'<img src="{img_src}" style="width:100%; border-radius:15px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); margin-bottom: 20px;" onerror="this.src=\'https://ui-avatars.com/api/?name={safe_name}&background=32E0C4&color=fff&size=400\'">', unsafe_allow_html=True)
                
                # Stats Row (Birth/Height)
                st.markdown(f"""
                <div class="stat-row">
                    <div class="stat-item"><span class="stat-label">{t.get('birth', 'Birth')}</span><span class="stat-val">{sel.get('birthday', '-')}</span></div>
                    <div class="stat-item"><span class="stat-label">{t.get('height', 'Height')}</span><span class="stat-val">{sel.get('height', '-')}</span></div>
                </div>
                <div class="stat-row"><div class="stat-item"><span class="stat-label">MBTI</span><span class="stat-val">{sel.get('mbti', '-')}</span></div></div>
                <div style="text-align:center; margin-top:-10px; color:#32E0C4; font-weight:900; font-size:1.3rem;">"{sel.get('nickname', {}).get(lang, '-')}"</div>
                """, unsafe_allow_html=True)
                
                # Birthday Countdown
                days, _ = get_next_birthday(sel.get('birthday', '2000.01.01'))
                st.markdown(f"""
                <div style="text-align:center; margin-top:20px; padding:15px; background:var(--glass); border-radius:12px; border:1px solid var(--border);">
                    <div style="font-size:0.8rem; color:#888; margin-bottom:5px;">🎂 {t.get('birthday_countdown', 'Birthday')}</div>
                    <div style="font-size:1.8rem; font-weight:900; color:var(--primary);">{days}</div>
                    <div style="font-size:0.8rem; color:#888;">{t.get('days', 'days')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Favorite Button
                is_favorite = member_name in st.session_state.favorites
                fav_text = t.get('remove_favorite', '❤️ Remove') if is_favorite else t.get('add_favorite', '💖 Add')
                if st.button(fav_text, use_container_width=True, key=f"fav_{member_name}"):
                    toggle_favorite(member_name)
                    st.rerun()
            
            with c2:
                display_name = sel.get('display_name', {}).get(lang, member_name)
                cn_name = sel.get('display_name', {}).get('cn', '')
                cn_name_html = f'<span class="profile-cn-name">{cn_name}</span>' if cn_name else ''
                position = sel.get('position', {}).get(lang, '-')
                st.markdown(f"<div class='profile-header'>{display_name}{cn_name_html}</div><div class='profile-sub'>{position}</div>", unsafe_allow_html=True)
                
                tab1, tab2, tab3 = st.tabs([f"📖 {t.get('tab1', 'Profile')}", f"🎵 {t.get('tab2', 'Songs')}", f"🎤 {t.get('tab3', 'Covers')}"])
                
                with tab1:
                    # 1. History Image & Text (Story)
                    history_html = ""
                    if history_img:
                        hist_src = get_image_src(history_img, "Story")
                        history_html = f'<img src="{hist_src}" style="width:100%; border-radius:10px; margin-bottom:15px; border:1px solid var(--border); box-shadow:0 4px 10px rgba(0,0,0,0.2);">'

                    history_text = sel.get('history', {}).get(lang, "No information available")
                    
                    st.markdown(f"""
                        <div class="story-container">
                            <div class="story-icon-header">✨ {t.get('story_title', 'Story')}</div>
                            {history_html}
<div class="story-content" style="margin-bottom:15px;">{history_text}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # 2. Facts Grid (เกร็ดน่ารู้)
                    st.markdown(f"<h4 style='color:#32E0C4; margin-bottom:10px; margin-top:20px;'>{t.get('facts_title', 'Facts')}</h4>", unsafe_allow_html=True)
                    facts_html = '<div class="facts-grid">'
                    for fact_str in sel.get('facts', {}).get(lang, []):
                        try:
                            parts = fact_str.split("**")
                            if len(parts) >= 3:
                                facts_html += f'<div class="fact-card-modern"><div class="fact-icon-modern">{parts[0].strip()}</div><div class="fact-label-modern">{parts[1].replace(":", "").strip()}</div><div class="fact-value-modern">{parts[2].strip()}</div></div>'
                            else: facts_html += f'<div class="fact-card-modern"><div class="fact-value-modern">{fact_str}</div></div>'
                        except: facts_html += f'<div class="fact-card-modern"><div class="fact-value-modern">{fact_str}</div></div>'
                    st.markdown(facts_html + '</div>', unsafe_allow_html=True)

                    # 3. Biography (ย้ายมาไว้ตรงนี้ ตามที่คุณชี้ในรูป) 👇👇👇
                    st.markdown("<br>", unsafe_allow_html=True) # เว้นบรรทัดนิดนึง
                    biography_text = sel.get('biography', {}).get(lang, "")
                    if biography_text:
                        with st.expander(f"📜 {t.get('bio_title', 'Full Biography')}", expanded=False):
                            st.markdown(f"<div style='line-height:1.8; color:var(--text-color);'>{biography_text}</div>", unsafe_allow_html=True)
                
                with tab2:
                    for s in sel.get('songs', []): st.markdown(f'<a href="https://www.youtube.com/results?search_query=TREASURE+{member_name}+{s}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎵 {s}</span><span>↗</span></div></a>', unsafe_allow_html=True)
                
                with tab3:
                    for c in sel.get('covers', []): st.markdown(f'<a href="https://www.youtube.com/results?search_query=TREASURE+{member_name}+{c}+cover" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎧 {c}</span><span>↗</span></div></a>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button(f"✕ {t.get('close', 'Close')}", use_container_width=True, type="primary", key="close_modal"):
                if 'selected_member' in st.session_state: 
                    del st.session_state.selected_member
                st.query_params.clear()
                st.rerun()
                
        except Exception as e:
            st.error(f"⚠️ Error: {str(e)}")
            
    modal_content()

# ============================================
# 🚀 MAIN APP EXECUTION
# ============================================
def main():
    try:
        members = get_members_data()
        if not members:
            st.error("❌ Cannot load member data")
            return
            
        initialize_session_state(members)
        inject_custom_css()
        
        ui_text = get_ui_text()
        lang = st.session_state.get('lang_code', 'th')
        t = ui_text.get(lang, ui_text['th'])
        
        render_sidebar(members, t, lang)
        
        # Hero Section
        st.markdown(f"""
        <div class="hero-container">
            <h1 class="hero-title">TREASURE</h1>
            <p class="hero-subtitle">{t.get('sub', 'LOVE PULSE : THE 3RD MINI ALBUM | 2026')}</p>
            <div class="social-bar">
                <a href="https://www.instagram.com/yg_treasure_official/" target="_blank" class="social-btn">📸</a>
                <a href="https://www.facebook.com/OfficialTreasure" target="_blank" class="social-btn">📘</a>
                <a href="https://weverse.io/treasure/feed" target="_blank" class="social-btn">🍀</a>
                <a href="https://www.youtube.com/@TREASURE" target="_blank" class="social-btn">📺</a>
                <a href="https://twitter.com/treasuremembers" target="_blank" class="social-btn">🐦</a>
            </div>
        </div><br>
        """, unsafe_allow_html=True)
        
        # --- PAGE SWITCHING LOGIC ---
        if st.session_state.page == 'members':
            st.markdown("<br>", unsafe_allow_html=True)
            render_birthday_section(members, t, lang)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Search
            search_query = st.text_input(
                label="search", 
                placeholder=f"🔍 {t.get('search', 'Search members')}...", 
                label_visibility="collapsed",
                key="member_search"
            )
            
            filtered_members = [
                m for m in members 
                if search_query.lower() in m.get('display_name', {}).get(lang, '').lower() 
                or search_query.lower() in m.get('name', '').lower()
            ] if search_query else members
            
            # Modal
            if "selected_member" in st.session_state:
                show_member_modal(st.session_state.selected_member, t, lang, members)
            
            # Group Image
            group_img_src = get_image_src("group.jpg", "TREASURE") 
            if "placeholder" in group_img_src or "ui-avatars" in group_img_src:
                group_img_src = "https://kprofiles.com/wp-content/uploads/2020/01/TREASURE-Concept-Photo-1-scaled.jpg"

            st.markdown(f"""
            <div class="map-frame">
                <img src="{group_img_src}" class="main-image" alt="TREASURE Group Photo">
            </div>
            <p style="text-align:center;color:#666;font-size:0.9rem;margin-top:-10px;">{t.get('touch', 'Touch member to view profile')}</p>
            """, unsafe_allow_html=True)
            
            # Member Grid
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            if st.session_state.favorites:
                st.markdown(f"<h4 style='text-align:center; color:#32E0C4; margin-bottom:20px;'>💖 {t.get('favorite', 'Favorites')}</h4>", unsafe_allow_html=True)
                fav_members = [m for m in members if m.get('name', '') in st.session_state.favorites]
                render_member_grid(fav_members, t, lang, members, show_heart=True)
                st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown(f"<h4 style='text-align:center; color:#32E0C4; margin-bottom:20px; opacity:0.8;'>{t.get('select', 'Select Member')}</h4>", unsafe_allow_html=True)
            
            if not filtered_members:
                st.info(f"🔍 {t.get('error_member', 'Member not found')}")
            else:
                render_member_grid(filtered_members, t, lang, members)
                
        elif st.session_state.page == 'about':
            render_group_info(t, lang)
        
        elif st.session_state.page == 'cheer':
            render_cheer_board(t, members)

        # Footer
        st.markdown(f"""
        <div style="text-align:center; margin-top:60px; padding: 25px; border-top: 1px solid rgba(255,255,255,0.1); opacity:0.6; font-size:0.85rem;">
            <p style="margin:0;">💎 TREASURE MAKER PROJECT 2026</p>
            <p style="margin:5px 0 0 0; font-size:0.75rem;">Theme: {st.session_state.theme.title()} Mode | Favorites: {len(st.session_state.favorites)}</p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"⚠️ Critical Error: {str(e)}")
        st.exception(e)
        if st.button("🔄 Reset App", type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":

    main()
