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
            "confirm_delete": "ลบข้อความนี้?"
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
            "confirm_delete": "Delete this?"
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
            "confirm_delete": "삭제하시겠습니까?"
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
            "confirm_delete": "削除しますか？"
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
            "confirm_delete": "确定删除吗？"

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
        {
            "name": "Hyunsuk", 
            "img": "hyunsuk.jpg",
            "birthday": "1999.04.21", 
            "height": "171 cm", 
            "mbti": "ENFP",
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
                "th": ["🦔 **English Name:** Danny Choi", "💎 **Gemstone:** Garnet (โกเมน)", "🩸 **Blood Type:** A", "⚽ **Hobby:** ฟุตบอล, ช้อปปิ้ง", "7️⃣ **Fav Number:** 7"],
                "en": ["🦔 **English Name:** Danny Choi", "💎 **Gemstone:** Garnet", "🩸 **Blood Type:** A", "⚽ **Hobby:** Soccer, Shopping", "7️⃣ **Fav Number:** 7"],
                "kr": ["🦔 **영어 이름:** Danny Choi", "💎 **보석:** 가넷", "🩸 **혈액형:** A형", "⚽ **취미:** 축구, 쇼핑", "7️⃣ **좋아하는 숫자:** 7"],
                "jp": ["🦔 **英語名:** Danny Choi", "💎 **宝石:** ガーネット", "🩸 **血液型:** A型", "⚽ **趣味:** サッカー, 買い物", "7️⃣ **好きな数字:** 7"],
                "cn": ["🦔 **英文名:** Danny Choi", "💎 **宝石:** 石榴石", "🩸 **血型:** A型", "⚽ **爱好:** 足球, 购物", "7️⃣ **幸运数字:** 7"]
            },
            "songs": ["VolKno", "KING KONG"], 
            "covers": ["Humble"]
        },
        {
            "name": "Jihoon", 
            "img": "jihoon.jpg",
            "birthday": "2000.03.14", 
            "height": "178 cm", 
            "mbti": "ENTJ",
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
                "th": ["🐶 **English Name:** Jun Park", "💎 **Gemstone:** Amethyst (อเมทิสต์)", "🩸 **Blood Type:** B", "✈️ **Dream:** นักบิน", "🔴 **Color:** Red"],
                "en": ["🐶 **English Name:** Jun Park", "💎 **Gemstone:** Amethyst", "🩸 **Blood Type:** B", "✈️ **Dream:** Pilot", "🔴 **Color:** Red"],
                "kr": ["🐶 **영어 이름:** Jun Park", "💎 **보석:** 자수정", "🩸 **혈액형:** B형", "✈️ **꿈:** 파일럿", "🔴 **색깔:** 빨강"],
                "jp": ["🐶 **英語名:** Jun Park", "💎 **宝石:** アメジスト", "🩸 **血液型:** B型", "✈️ **夢:** パイロット", "🔴 **色:** 赤"],
                "cn": ["🐶 **英文名:** Jun Park", "💎 **宝石:** 紫水晶", "🩸 **血型:** B型", "✈️ **梦想:** 飞行员", "🔴 **颜色:** 红色"]
            },
            "songs": ["The Way To", "MOVE"], 
            "covers": ["Ko Ko Bop"]
        },
        {
            "name": "Yoshi", 
            "img": "yoshi.jpg",
            "birthday": "2000.05.15", 
            "height": "179 cm", 
            "mbti": "INFP",
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
                "th": ["🐯 **English Name:** Jaden", "💎 **Gemstone:** Aquamarine (อความารีน)", "🩸 **Blood Type:** A", "🏎️ **Dream:** นักแข่งรถ", "🇯🇵 **Origin:** Kobe, Japan"],
                "en": ["🐯 **English Name:** Jaden", "💎 **Gemstone:** Aquamarine", "🩸 **Blood Type:** A", "🏎️ **Dream:** Racer", "🇯🇵 **Origin:** Kobe, Japan"],
                "kr": ["🐯 **영어 이름:** Jaden", "💎 **보석:** 아쿠아마린", "🩸 **혈액형:** A형", "🏎️ **꿈:** 레이서", "🇯🇵 **출신:** 일본 고베"],
                "jp": ["🐯 **英語名:** Jaden", "💎 **宝石:** アクアマリン", "🩸 **血液型:** A型", "🏎️ **夢:** レーサー", "🇯🇵 **出身:** 神戸"],
                "cn": ["🐯 **英文名:** Jaden", "💎 **宝石:** 海蓝宝", "🩸 **血型:** A型", "🏎️ **梦想:** 赛车手", "🇯🇵 **出身:** 神户"]
            },
            "songs": ["STUPID", "KING KONG"], 
            "covers": ["Still Life"]
        },
        {
            "name": "Junkyu", 
            "img": "junkyu.jpg",
            "birthday": "2000.09.09", 
            "height": "178 cm", 
            "mbti": "INFJ",
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
                "th": ["🐨 **English Name:** David Kim", "💎 **Gemstone:** Diamond (เพชร)", "🩸 **Blood Type:** O", "🐱 **Pets:** Ruby, Aengdu", "👕 **Physique:** Physical Genius"],
                "en": ["🐨 **English Name:** David Kim", "💎 **Gemstone:** Diamond", "🩸 **Blood Type:** O", "🐱 **Pets:** Ruby, Aengdu", "👕 **Physique:** Physical Genius"],
                "kr": ["🐨 **영어 이름:** David Kim", "💎 **보석:** 다이아몬드", "🩸 **혈액형:** O형", "🐱 **반려묘:** 루비, 앵두", "👕 **피지컬:** 피지컬 천재"],
                "jp": ["🐨 **英語名:** David Kim", "💎 **宝石:** ダイヤモンド", "🩸 **血液型:** O型", "🐱 **ペット:** Ruby, Aengdu", "👕 **体格:** フィジカル天才"],
                "cn": ["🐨 **英文名:** David Kim", "💎 **宝石:** 钻石", "🩸 **血型:** O型", "🐱 **宠物:** Ruby, Aengdu", "👕 **身材:** 脸蛋天才"]
            },
            "songs": ["MOVE", "YELLOW"], 
            "covers": ["Latch"]
        },
        {
            "name": "Jaehyuk", 
            "img": "jaehyuk.jpg",
            "birthday": "2001.07.23", 
            "height": "178 cm", 
            "mbti": "INFP",
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
                "th": ["🦁 **English Name:** Kevin Yoon", "💎 **Gemstone:** Pearl (ไข่มุก)", "🩸 **Blood Type:** O", "🤚 **Hand:** Left-handed", "💖 **Charm:** Sweet"],
                "en": ["🦁 **English Name:** Kevin Yoon", "💎 **Gemstone:** Pearl", "🩸 **Blood Type:** O", "🤚 **Hand:** Left-handed", "💖 **Charm:** Sweet"],
                "kr": ["🦁 **영어 이름:** Kevin Yoon", "💎 **보석:** 진주", "🩸 **혈액형:** O형", "🤚 **손:** 왼손잡이", "💖 **매력:** 다정함"],
                "jp": ["🦁 **英語名:** Kevin Yoon", "💎 **宝石:** 真珠", "🩸 **血液型:** O型", "🤚 **利き手:** 左利き", "💖 **魅力:** 優しい"],
                "cn": ["🦁 **英文名:** Kevin Yoon", "💎 **宝石:** 珍珠", "🩸 **血型:** O型", "🤚 **惯用手:** 左手", "💖 **魅力:** 温柔"]
            },
            "songs": ["MOVE", "Wonderland"], 
            "covers": ["Ring Ring"]
        },
        {
            "name": "Asahi", 
            "img": "asahi.jpg",
            "birthday": "2001.08.20", 
            "height": "172 cm", 
            "mbti": "INFP",
            "display_name": {"th": "ฮามาดะ อาซาฮิ", "en": "Hamada Asahi", "kr": "하마다 아사히", "jp": "浜田朝光", "cn": "滨田朝光"},
            "position": {"th": "ลีดเดอร์ (2025+), T5", "en": "Leader (2025+), T5", "kr": "리더 (2025+), T5", "jp": "リーダー (2025+), T5", "cn": "队长 (2025+), T5"},
            "nickname": {"th": "Robot", "en": "Robot", "kr": "로봇", "jp": "ロボット", "cn": "机器人"},
            "history": {
                "th": "จากโอซาก้า ชื่อแปลว่า 'แสงยามเช้า' รับตำแหน่ง Leader คู่กับจุนกยู (2025)",
                "en": "From Osaka. Name means 'Morning Sunshine'. Co-Leader (2025).",
                "kr": "오사카 출신. 이름 뜻은 '아침 햇살'. 공동 리더 (2025).",
                "jp": "大阪出身。名前の意味は「朝の光」。共同リーダー (2025)。",
                "cn": "来自大阪。名字意为'晨光'。共同队长 (2025)。"
            },
            "facts": {
                "th": ["🤖 **English Name:** Arthur", "💎 **Gemstone:** Ruby (ทับทิม)", "🩸 **Blood Type:** AB", "⚽ **Hobby:** Football", "🎨 **Skill:** Art"],
                "en": ["🤖 **English Name:** Arthur", "💎 **Gemstone:** Ruby", "🩸 **Blood Type:** AB", "⚽ **Hobby:** Football", "🎨 **Skill:** Art"],
                "kr": ["🤖 **영어 이름:** Arthur", "💎 **보석:** 루비", "🩸 **혈액형:** AB형", "⚽ **취미:** 축구", "🎨 **특기:** 예술"],
                "jp": ["🤖 **英語名:** Arthur", "💎 **宝石:** ルビー", "🩸 **血液型:** AB型", "⚽ **趣味:** サッカー", "🎨 **特技:** アート"],
                "cn": ["🤖 **英文名:** Arthur", "💎 **宝石:** 红宝石", "🩸 **血型:** AB型", "⚽ **爱好:** 足球", "🎨 **特长:** 艺术"]
            },
            "songs": ["THANK YOU", "CLAP!"], 
            "covers": ["Lay Me Down"]
        },
        {
            "name": "Doyoung", 
            "img": "doyoung.jpg",
            "birthday": "2003.12.04", 
            "height": "177 cm", 
            "mbti": "ESTP",
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
                "th": ["🐰 **English Name:** Sam", "💎 **Gemstone:** Sapphire (ไพลิน)", "🩸 **Blood Type:** B", "✝️ **Name:** Nicholas", "🍳 **Skill:** Cooking"],
                "en": ["🐰 **English Name:** Sam", "💎 **Gemstone:** Sapphire", "🩸 **Blood Type:** B", "✝️ **Name:** Nicholas", "🍳 **Skill:** Cooking"],
                "kr": ["🐰 **영어 이름:** Sam", "💎 **보석:** 사파이어", "🩸 **혈액형:** B형", "✝️ **세례명:** 니콜라스", "🍳 **특기:** 요리"],
                "jp": ["🐰 **英語名:** Sam", "💎 **宝石:** サファイア", "🩸 **血液型:** B型", "✝️ **洗礼名:** ニコラス", "🍳 **特技:** 料理"],
                "cn": ["🐰 **英文名:** Sam", "💎 **宝石:** 蓝宝石", "🩸 **血型:** B型", "✝️ **洗礼名:** Nicholas", "🍳 **特长:** 烹饪"]
            },
            "songs": ["WONDERLAND", "MOVE"], 
            "covers": ["Freedom"]
        },
        {
            "name": "Haruto", 
            "img": "haruto.jpg",
            "birthday": "2004.04.05", 
            "height": "183.2 cm", 
            "mbti": "INFP",
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
                "th": ["🦋 **English Name:** Travis", "💎 **Gemstone:** Opal (โอปอล)", "🩸 **Blood Type:** B", "📏 **Height:** 183.2 cm", "🇯🇵 **Origin:** Fukuoka"],
                "en": ["🦋 **English Name:** Travis", "💎 **Gemstone:** Opal", "🩸 **Blood Type:** B", "📏 **Height:** 183.2 cm", "🇯🇵 **Origin:** Fukuoka"],
                "kr": ["🦋 **영어 이름:** Travis", "💎 **보석:** 오팔", "🩸 **혈액형:** B형", "📏 **신장:** 183.2 cm", "🇯🇵 **출신:** 후쿠오카"],
                "jp": ["🦋 **英語名:** Travis", "💎 **宝石:** オパール", "🩸 **血液型:** B型", "📏 **身長:** 183.2 cm", "🇯🇵 **出身:** 福岡"],
                "cn": ["🦋 **英文名:** Travis", "💎 **宝石:** 蛋白石", "🩸 **血型:** B型", "📏 **身高:** 183.2 cm", "🇯🇵 **出身:** 福冈"]
            },
            "songs": ["G.O.A.T", "KING KONG"], 
            "covers": ["FLASH"]
        },
        {
            "name": "Jeongwoo", 
            "img": "jeongwoo.jpg",
            "birthday": "2004.09.28", 
            "height": "181 cm", 
            "mbti": "ISFP",
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
                "th": ["🐺 **English Name:** Justin", "💎 **Gemstone:** Topaz (โทพาซ)", "🩸 **Blood Type:** O", "🤚 **Hand:** Left-handed", "🎤 **Role:** Main Vocal"],
                "en": ["🐺 **English Name:** Justin", "💎 **Gemstone:** Topaz", "🩸 **Blood Type:** O", "🤚 **Hand:** Left-handed", "🎤 **Role:** Main Vocal"],
                "kr": ["🐺 **영어 이름:** Justin", "💎 **보석:** 토파즈", "🩸 **혈액형:** O형", "🤚 **손:** 왼손잡이", "🎤 **역할:** 메인보컬"],
                "jp": ["🐺 **英語名:** Justin", "💎 **宝石:** トパーズ", "🩸 **血液型:** O型", "🤚 **利き手:** 左利き", "🎤 **役割:** メインボーカル"],
                "cn": ["🐺 **英文名:** Justin", "💎 **宝石:** 托帕石", "🩸 **血型:** O型", "🤚 **惯用手:** 左手", "🎤 **担当:** 主唱"]
            },
            "songs": ["PARADISE", "DARARI"], 
            "covers": ["Superstar"]
        },
        {
            "name": "Junghwan", 
            "img": "junghwan.jpg",
            "birthday": "2005.02.18", 
            "height": "180.3 cm", 
            "mbti": "ENFP-T",
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
                "th": ["🐮 **English Name:** John", "💎 **Gemstone:** Turquoise (เทอร์ควอยซ์)", "🩸 **Blood Type:** B", "🥋 **Team:** K-TIGERS", "❄️ **Season:** Winter"],
                "en": ["🐮 **English Name:** John", "💎 **Gemstone:** Turquoise", "🩸 **Blood Type:** B", "🥋 **Team:** K-TIGERS", "❄️ **Season:** Winter"],
                "kr": ["🐮 **영어 이름:** John", "💎 **보석:** 터키석", "🩸 **혈액형:** B형", "🥋 **팀:** K-TIGERS", "❄️ **계절:** 겨울"],
                "jp": ["🐮 **英語名:** John", "💎 **宝石:** ターコイズ", "🩸 **血液型:** B型", "🥋 **チーム:** K-TIGERS", "❄️ **季節:** 冬"],
                "cn": ["🐮 **英文名:** John", "💎 **宝石:** 绿松石", "🩸 **血型:** B型", "🥋 **队伍:** K-TIGERS", "❄️ **季节:** 冬天"]
            },
            "songs": ["B.O.M.B", "MOVE"], 
            "covers": ["Lie"]
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
            c1, c2 = st.columns([1.5, 2.5])
            with c1:
                img_src = get_image_src(member_img, member_name)
                safe_name = urllib.parse.quote(member_name)
                st.markdown(f'<img src="{img_src}" style="width:100%; border-radius:15px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); margin-bottom: 20px;" onerror="this.src=\'https://ui-avatars.com/api/?name={safe_name}&background=32E0C4&color=fff&size=400\'">', unsafe_allow_html=True)
                
                # ... (ส่วนแสดงสถิติเหมือนเดิม) ...
                st.markdown(f"""
                <div class="stat-row">
                    <div class="stat-item"><span class="stat-label">{t.get('birth', 'Birth')}</span><span class="stat-val">{sel.get('birthday', '-')}</span></div>
                    <div class="stat-item"><span class="stat-label">{t.get('height', 'Height')}</span><span class="stat-val">{sel.get('height', '-')}</span></div>
                </div>
                <div class="stat-row"><div class="stat-item"><span class="stat-label">MBTI</span><span class="stat-val">{sel.get('mbti', '-')}</span></div></div>
                <div style="text-align:center; margin-top:-10px; color:#32E0C4; font-weight:900; font-size:1.3rem;">"{sel.get('nickname', {}).get(lang, '-')}"</div>
                """, unsafe_allow_html=True)
                
                days, _ = get_next_birthday(sel.get('birthday', '2000.01.01'))
                st.markdown(f"""
                <div style="text-align:center; margin-top:20px; padding:15px; background:var(--glass); border-radius:12px; border:1px solid var(--border);">
                    <div style="font-size:0.8rem; color:#888; margin-bottom:5px;">🎂 {t.get('birthday_countdown', 'Birthday')}</div>
                    <div style="font-size:1.8rem; font-weight:900; color:var(--primary);">{days}</div>
                    <div style="font-size:0.8rem; color:#888;">{t.get('days', 'days')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                is_favorite = member_name in st.session_state.favorites
                fav_text = t.get('remove_favorite', '❤️ Remove') if is_favorite else t.get('add_favorite', '💖 Add')
                if st.button(fav_text, use_container_width=True, key=f"fav_{member_name}"):
                    toggle_favorite(member_name)
                    st.rerun()
            
            with c2:
                # ... (ส่วนแสดงผลด้านขวาเหมือนเดิม) ...
                display_name = sel.get('display_name', {}).get(lang, member_name)
                cn_name = sel.get('display_name', {}).get('cn', '')
                cn_name_html = f'<span class="profile-cn-name">{cn_name}</span>' if cn_name else ''
                position = sel.get('position', {}).get(lang, '-')
                st.markdown(f"<div class='profile-header'>{display_name}{cn_name_html}</div><div class='profile-sub'>{position}</div>", unsafe_allow_html=True)
                
                tab1, tab2, tab3 = st.tabs([f"📖 {t.get('tab1', 'Profile')}", f"🎵 {t.get('tab2', 'Songs')}", f"🎤 {t.get('tab3', 'Covers')}"])
                
                with tab1:
                    history = sel.get('history', {}).get(lang, "No information available")
                    st.markdown(f"""<div class="story-container"><div class="story-icon-header">✨ {t.get('story_title', 'Story')}</div><div class="story-content">{history}</div></div>""", unsafe_allow_html=True)
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
                
                with tab2:
                    for s in sel.get('songs', []): st.markdown(f'<a href="https://www.youtube.com/results?search_query=TREASURE+{member_name}+{s}" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎵 {s}</span><span>↗</span></div></a>', unsafe_allow_html=True)
                
                with tab3:
                    for c in sel.get('covers', []): st.markdown(f'<a href="https://www.youtube.com/results?search_query=TREASURE+{member_name}+{c}+cover" target="_blank" class="song-link"><div class="song-card"><span class="song-title">🎧 {c}</span><span>↗</span></div></a>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- แก้ไขปุ่มปิด: ให้ล้าง query params ด้วย ---
            if st.button(f"✕ {t.get('close', 'Close')}", use_container_width=True, type="primary", key="close_modal"):
                if 'selected_member' in st.session_state: 
                    del st.session_state.selected_member
                # ล้างค่าใน URL เพื่อไม่ให้เด้งกลับมาอีก
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