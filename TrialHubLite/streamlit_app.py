import streamlit as st
import sqlite3
import pandas as pd
import io
from datetime import datetime, timedelta
import pytz

# --- Global Timezone ---
vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
now_vn = datetime.now(vn_tz)
# Get local date as naive datetime for comparison
today_vn = now_vn.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
current_dt_naive = now_vn.replace(tzinfo=None)

def parse_trial_datetime(date_str, time_str):
    try:
        # Parse date
        d = datetime.strptime(str(date_str), "%d/%m/%Y")
        # Parse time
        t_str = str(time_str).lower().replace('h', ':').replace('g', ':').strip()
        if ':' not in t_str:
            if t_str.isdigit():
                t_str += ":00"
            else:
                return d # Date only
        
        parts = t_str.split(':')
        h = int(parts[0])
        m = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        return d.replace(hour=h, minute=m)
    except:
        return None

# --- Page Config ---
st.set_page_config(
    page_title="TrialHub Lite – MindX Trial Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    /* Header Styling */
    .main .block-container {
        padding-top: 2rem;
    }
    
    h1, h2, h3 {
        color: #1e40af; /* MindX Dark Blue */
    }

    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        color: #1e40af;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1e40af;
        color: white;
    }

    /* Buttons */
    .stButton button {
        background-color: #10b981; /* MindX Green */
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #059669;
        color: white;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #1e40af;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b; /* Slate 800 */
        color: white;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stExpander {
        background-color: #334155; /* Slate 700 */
        border-radius: 5px;
        margin-bottom: 10px;
        border: none;
    }
    
    [data-testid="stSidebar"] .stExpander details {
        border-color: #475569;
    }

    [data-testid="stSidebar"] .stExpander summary {
        color: white !important;
        font-weight: 500;
    }
    
    [data-testid="stSidebar"] .stExpander summary:hover {
        color: #38bdf8 !important; /* Sky 400 */
    }
    
    /* Divider */
    [data-testid="stSidebar"] hr {
        border-color: #475569;
    }
</style>
""", unsafe_allow_html=True)

def import_trials_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df_import = pd.read_csv(uploaded_file)
        else:
            df_import = pd.read_excel(uploaded_file)
            
        # Normalize columns
        # Map: STT->stt, Ngày/Date->trial_date, Thời gian/Time->time, Link->meet_link, 
        # Môn/Subject->subject, SĐT/Phone->phone, Tình trạng/Status->status, 
        # Note/Ghi chú->note, Phụ trách/Evaluator->evaluator, TVV/Creator->creator
        
        col_map = {}
        for col in df_import.columns:
            c = str(col).lower().strip()
            if 'stt' in c: col_map[col] = 'stt'
            elif 'ngày' in c or 'date' in c: col_map[col] = 'trial_date'
            elif 'thời gian' in c or 'time' in c: col_map[col] = 'time'
            elif 'link' in c: col_map[col] = 'meet_link'
            elif 'môn' in c or 'subject' in c: col_map[col] = 'subject'
            elif 'sđt' in c or 'phone' in c: col_map[col] = 'phone'
            elif 'tình trạng' in c or 'status' in c: col_map[col] = 'status'
            elif 'note' in c or 'ghi chú' in c: col_map[col] = 'note'
            elif 'phụ trách' in c or 'evaluator' in c: col_map[col] = 'evaluator'
            elif 'tvv' in c or 'creator' in c: col_map[col] = 'creator'
            
        df_import = df_import.rename(columns=col_map)
        
        # Ensure required columns exist
        required_cols = ['trial_date', 'phone', 'subject', 'status']
        missing = [c for c in required_cols if c not in df_import.columns]
        
        return df_import, missing
    except Exception as e:
        return None, str(e)

# --- Database Functions ---
@st.cache_resource
def get_connection():
    return sqlite3.connect("trialhub.db", check_same_thread=False)

conn = get_connection()

# Use cache_data for performance, invalidate when data changes
@st.cache_data(ttl=60) 
def load_data():
    try:
        # We use a new connection here to be safe with threading or just rely on the cached resource?
        # Better to query and return DF.
        query = "SELECT * FROM trials ORDER BY id DESC"
        # We can't pickle the sqlite connection easily if it's in the args, but here we use global 'conn'
        # To make it robust with cache, we might want to just run the query.
        # Note: pandas read_sql might need a fresh cursor or connection if the global one is closed (it shouldn't be).
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def clear_cache():
    load_data.clear()

def save_batch_changes(edited_rows, original_df):
    """
    Saves changes from st.data_editor's session state (edited_rows) to SQLite.
    edited_rows is a dict: {row_index: {col_name: new_value, ...}}
    Note: row_index corresponds to the index of the DataFrame passed to data_editor.
    If filter is applied, we must ensure we map back to the correct DB ID.
    We set existing dataframe index to 'id' before passing to editor to make this easy.
    """
    try:
        cursor = conn.cursor()
        count = 0
        for row_id, changes in edited_rows.items():
            # row_id is the primary key 'id' because we set df.index = id
            updates = []
            params = []
            for col, val in changes.items():
                updates.append(f"{col} = ?")
                params.append(val)
            
            if updates:
                params.append(row_id)
                sql = f"UPDATE trials SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, params)
                count += 1
                
        conn.commit()
        clear_cache() # Clear cache to refresh data next load
        return count
    except Exception as e:
        st.error(f"Lỗi save batch: {e}")
        return 0

def update_single_row(row_id, data):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE trials SET 
            trial_date=?, time=?, meet_link=?, subject=?, phone=?, 
            status=?, note=?, evaluator=?, creator=?
            WHERE id=?
        """, (
            data['trial_date'], data['time'], data['meet_link'], 
            data['subject'], data['phone'], data['status'], 
            data['note'], data['evaluator'], data['creator'], 
            row_id
        ))
        conn.commit()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Lỗi update row: {e}")
        return False

def add_trial(data):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trials (stt, trial_date, time, meet_link, subject, phone, status, note, evaluator, creator)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('stt'), data.get('trial_date'), data.get('time'), 
            data.get('meet_link'), data.get('subject'), data.get('phone'), 
            data.get('status'), data.get('note'), data.get('evaluator'), 
            data.get('creator')
        ))
        conn.commit()
        clear_cache()
        return True
    except Exception as e:
        st.error(f"Error adding trial: {e}")
        return False

# --- Styling Logic (Global) ---
def highlight_rows(row):
    status = str(row['status']).lower()
    
    # Colors
    COLOR_RED = 'background-color: #fecaca' # Fail
    COLOR_GREEN = 'background-color: #d1fae5' # Done
    COLOR_GRAY = 'background-color: #f3f4f6; color: #9ca3af' # Cancel
    COLOR_ORANGE = 'background-color: #ffedd5' # Urgent
    
    if 'gãy' in status or 'gáy' in status:
        return [COLOR_RED] * len(row)
    if 'hủy' in status:
        return [COLOR_GRAY] * len(row)
    if 'đã trial' in status or 'thích' in status or 'done' in status:
        return [COLOR_GREEN] * len(row)
    
    # Urgent: Today or < 2 hours
    try:
        dt = parse_trial_datetime(row['trial_date'], row['time'])
        if dt:
            # Check if today
            if dt.date() == today_vn.date():
                return [COLOR_ORANGE] * len(row)
            
            # Check < 2 hours from now
            diff = dt - current_dt_naive
            if timedelta(hours=0) <= diff <= timedelta(hours=2):
                return [COLOR_ORANGE] * len(row)
    except:
        pass
        
    return [''] * len(row)

# --- Data Loading (Global) ---
df = load_data()
df_export = df.copy() # Prepare export/filtering base

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>MindX TrialHub 🚀</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Session State for User Name
    if 'user_name' not in st.session_state:
        st.session_state.user_name = "Admin"
    
    user_name = st.text_input("👤 Tên TVV / Người dùng:", value=st.session_state.user_name)
    st.session_state.user_name = user_name
    
    st.success(f"Xin chào, **{st.session_state.user_name}**! 👋")
    st.markdown("---")

    # --- 1. Filters ---
    with st.expander("🔍 Bộ lọc danh sách", expanded=True):
        # Date Range
        filter_date = st.date_input("📅 Khoảng thời gian", [])
        
        # Filter Options
        all_subjects = ["Coding", "Art", "Robotics", "Khác"]
        all_statuses = ["Chờ trial", "Đã trial", "Hủy lịch", "Reschedule", "Gãy", "Gáy"]
        
        filter_subject = st.multiselect("📚 Môn học", all_subjects)
        filter_status = st.multiselect("yw Trạng thái", all_statuses)
        filter_evaluator = st.text_input("👨‍🏫 Người đánh giá")

    st.markdown("---")

    # --- 2. Import Excel/CSV ---
    with st.expander("📥 Import Trial từ Excel/CSV", expanded=False):
        uploaded_file = st.file_uploader("Chọn file .xlsx hoặc .csv", type=['xlsx', 'csv'])
        
        if uploaded_file:
            df_preview, missing_cols = import_trials_from_file(uploaded_file)
            
            if isinstance(missing_cols, str):
                st.error(f"Lỗi đọc file: {missing_cols}")
            else:
                st.caption("Xem trước 5 dòng đầu:")
                st.dataframe(df_preview.head(5), height=150)
                
                if missing_cols:
                    st.warning(f"Thiếu cột: {', '.join(missing_cols)}")
                    st.info("Các cột này sẽ để trống.")
                
                if st.button("🚀 Import vào database", type="primary"):
                    try:
                        cursor = conn.cursor()
                        count = 0
                        for _, row in df_preview.iterrows():
                            # Check duplicates (Phone + Date)
                            phone = str(row.get('phone', '')).strip()
                            
                            # Handle date format variations
                            t_date = row.get('trial_date', '')
                            if isinstance(t_date, datetime):
                                t_date = t_date.strftime("%d/%m/%Y")
                            else:
                                t_date = str(t_date).split(' ')[0] # Remove time if present
                                
                            # Simple duplicate check
                            cursor.execute("SELECT id FROM trials WHERE phone=? AND trial_date=?", (phone, t_date))
                            if cursor.fetchone():
                                continue
                                
                            cursor.execute("""
                                INSERT INTO trials (stt, trial_date, time, meet_link, subject, phone, status, note, evaluator, creator)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                row.get('stt', ''), t_date, row.get('time', ''), 
                                row.get('meet_link', ''), row.get('subject', ''), phone, 
                                row.get('status', 'Chờ trial'), row.get('note', ''), 
                                row.get('evaluator', ''), st.session_state.user_name
                            ))
                            count += 1
                        conn.commit()
                        st.success(f"Đã import thành công {count} dòng!")
                        st.balloons()
                        # st.rerun() # Let user see message first
                    except Exception as e:
                        st.error(f"Lỗi import: {e}")

    st.markdown("---")

    # --- 3. Export & Backup ---
    with st.expander("💾 Export & Backup", expanded=False):
        # Filter Logic for Export
        df_export = df.copy()
        
        if not df_export.empty:
            # Apply Sidebar Filters
            if len(filter_date) == 2:
                start_date, end_date = filter_date
                df_export['date_temp'] = pd.to_datetime(df_export['trial_date'], format='%d/%m/%Y', errors='coerce').dt.date
                df_export = df_export[(df_export['date_temp'] >= start_date) & (df_export['date_temp'] <= end_date)]
                df_export = df_export.drop(columns=['date_temp'])
                
            if filter_subject:
                mask_sub = df_export['subject'].apply(lambda x: any(s.lower() in str(x).lower() for s in filter_subject))
                df_export = df_export[mask_sub]
                
            if filter_status:
                mask_stat = df_export['status'].apply(lambda x: any(s.lower() in str(x).lower() for s in filter_status))
                df_export = df_export[mask_stat]
                
            if filter_evaluator:
                df_export = df_export[df_export['evaluator'].str.contains(filter_evaluator, case=False, na=False)]
                
            # Apply Search Term (from session state if available, or just skip for export if not critical)
            # Note: Search term is in main content, so it might not be updated here yet if user just typed it.
            # But usually export is done after viewing.
            search_term_global = st.session_state.get("search_term", "")
            if search_term_global:
                mask = df_export.apply(lambda x: x.astype(str).str.contains(search_term_global, case=False).any(), axis=1)
                df_export = df_export[mask]

            # 1. Export Excel
            buffer = io.BytesIO()
            try:
                # Apply style
                df_export.style.apply(highlight_rows, axis=1).to_excel(buffer, engine='openpyxl', index=False)
            except:
                # Fallback
                df_export.to_excel(buffer, engine='openpyxl', index=False)
                
            buffer.seek(0)
            st.download_button(
                label="📥 Export Excel (Filtered)",
                data=buffer,
                file_name=f"trialhub_export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Không có dữ liệu để export.")

        # 2. Backup DB
        try:
            with open("trialhub.db", "rb") as f:
                db_bytes = f.read()
            st.download_button(
                label="📦 Tải backup DB",
                data=db_bytes,
                file_name=f"trialhub_backup_{datetime.now().strftime('%Y%m%d')}.db",
                mime="application/x-sqlite3"
            )
        except Exception as e:
            st.error(f"Lỗi đọc DB: {e}")

# --- RE-WRITING THE LOGIC FLOW FOR REPLACEMENT ---
# The replacement chunk covers lines 174 to 268 (Sidebar + old Data Loading).
# I will replace it with:
# 1. Data Loading (moved up)
# 2. Sidebar UI (Filters)
# 3. Filter Application
# 4. Sidebar UI (Import)
# 5. Sidebar UI (Export)

    # ... (See actual replacement content)

# --- Main Content ---
st.title("TrialHub Lite – MindX Trial Management")

# Tabs
# --- Navigation (Hyperswitch Fix) ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📊 Dashboard"

# Use radio for persistence (st.tabs resets on Enter key in some contexts)
selected_tab = st.radio(
    "", 
    ["📊 Dashboard", "📋 Danh sách Trial", "➕ Thêm Trial mới"],
    horizontal=True,
    label_visibility="collapsed",
    key="active_tab"
)
st.markdown("---")

# --- Tab 1: Dashboard ---
if selected_tab == "📊 Dashboard":
    st.header("Tổng quan")
    # df is already loaded globally
    
    if not df.empty:
        # Pre-process dates
        # Assuming format dd/mm/yyyy
        df['date_obj'] = pd.to_datetime(df['trial_date'], format='%d/%m/%Y', errors='coerce')
        
        # 1. Tổng Trial
        total_trials = len(df)
        
        # 2. Trial hôm nay
        # Compare date part only
        trials_today_count = len(df[df['date_obj'] == today_vn])
        
        # 3. Sắp tới (7 ngày tới)
        # From tomorrow to today+7
        next_7_days = today_vn + timedelta(days=7)
        upcoming_count = len(df[(df['date_obj'] > today_vn) & (df['date_obj'] <= next_7_days)])
        
        # 4. Đã trial
        completed_count = len(df[df['status'].str.contains('Đã trial|Done', case=False, na=False)])
        
        # 5. Gáy (Gãy)
        # User requested "Gáy", data often has "Gãy". Matching both or "G" generally if specific?
        # Let's match "Gãy" or "Gáy"
        broken_count = len(df[df['status'].str.contains('Gãy|Gáy', case=False, na=False)])
        
        # 6. Hủy lịch
        cancelled_count = len(df[df['status'].str.contains('Hủy', case=False, na=False)])
        
        # 7. Coding (%)
        coding_count = len(df[df['subject'].str.contains('Coding', case=False, na=False)])
        coding_pct = (coding_count / total_trials * 100) if total_trials > 0 else 0
        
        # 8. Art (%)
        art_count = len(df[df['subject'].str.contains('Art', case=False, na=False)])
        art_pct = (art_count / total_trials * 100) if total_trials > 0 else 0
        
        # Row 1
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Tổng Trial", total_trials)
        with c2:
            st.metric("Hôm nay", trials_today_count, delta=f"{trials_today_count} trial")
        with c3:
            st.metric("Sắp tới (7 ngày)", upcoming_count)
        with c4:
            st.metric("Đã trial", completed_count, delta="Hoàn thành", delta_color="normal")
            
        # Row 2
        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.metric("Gãy / Fail", broken_count, delta="-Fail", delta_color="inverse")
        with c6:
            st.metric("Hủy lịch", cancelled_count, delta="-Cancel", delta_color="inverse")
        with c7:
            st.metric("Coding", f"{coding_pct:.1f}%", delta=f"{coding_count} trial")
        with c8:
            st.metric("Art", f"{art_pct:.1f}%", delta=f"{art_count} trial")
            
        st.markdown("---")
        st.markdown("### Biểu đồ trạng thái")
        st.bar_chart(df['status'].value_counts())
    else:
        st.warning("Chưa có dữ liệu.")

# --- Tab 2: Danh sách Trial ---
if selected_tab == "📋 Danh sách Trial":
    st.header("Danh sách Trial")
    
    # 1. Prepare Display Data
    # df_display is already filtered in the main scope (lines 535-560 in previous version)
    # But wait, the previous code block for Tab 2 was replaced partly.
    # We need to make sure we access the correct filtered dataframe.
    # In the provided file content, `df_display` was created around line 535.
    # We will assume `df_display` is available or re-create it if needed.
    # Actually, the user asked to replace "The entire 'Danh sách Trial' tab code".
    # So we should include the filtering logic for the VIEW here if it was inside the tab, 
    # but in the previous file state, it was seemingly inside `with tab2`.
    # Let's check lines 496-591 of the file provided in context... yes, it is inside `with tab2`.
    
    if not df.empty:
        # --- Local Filtering (View) ---
        df_view = df.copy()
        
        # Search Term
        search_term_key = "search_box_tab2"
        search_term = st.text_input("🔍 Tìm kiếm toàn cục", placeholder="Nhập SĐT, Tên, Note...", key=search_term_key)
        
        if search_term:
            mask = df_view.apply(lambda x: x.astype(str).str.contains(search_term, case=False).any(), axis=1)
            df_view = df_view[mask]
            
        # Sidebar Filters (Global variables `filter_date`, `filter_subject`, etc. are available from sidebar scope)
        if len(filter_date) == 2:
            start_date, end_date = filter_date
            df_view['date_temp'] = pd.to_datetime(df_view['trial_date'], format='%d/%m/%Y', errors='coerce').dt.date
            df_view = df_view[(df_view['date_temp'] >= start_date) & (df_view['date_temp'] <= end_date)]
            
        if filter_subject:
            df_view = df_view[df_view['subject'].apply(lambda x: any(s.lower() in str(x).lower() for s in filter_subject))]
            
        if filter_status:
            df_view = df_view[df_view['status'].apply(lambda x: any(s.lower() in str(x).lower() for s in filter_status))]
            
        if filter_evaluator:
            df_view = df_view[df_view['evaluator'].str.contains(filter_evaluator, case=False, na=False)]

        # --- 2. Edit Interface ---
        
        # Set Index to ID for reliable updates
        df_view = df_view.set_index('id')
        
        # Styling
        styled_df = df_view.style.apply(highlight_rows, axis=1)
        
        # Check for unsaved changes (visual indicator)
        # We look at session state
        editor_key = "data_editor_tab2"
        edited_rows = st.session_state.get(editor_key, {}).get("edited_rows", {})
        has_unsaved = len(edited_rows) > 0
        
        col_btn, col_msg = st.columns([1, 3])
        with col_btn:
            if st.button("💾 Lưu thay đổi", type="primary", disabled=not has_unsaved):
                count = save_batch_changes(edited_rows, df)
                if count > 0:
                    st.toast(f"Đã lưu thành công {count} thay đổi!", icon="✅")
                    st.rerun()
                else:
                    st.info("Không có thay đổi nào để lưu.")
        
        with col_msg:
            if has_unsaved:
                st.markdown(f"<span style='color:red; font-weight:bold;'>● Có {len(edited_rows)} dòng chưa lưu!</span>", unsafe_allow_html=True)
        
        # Data Editor
        st.data_editor(
            styled_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "note": st.column_config.TextColumn("Note", width="medium"),
                "meet_link": st.column_config.LinkColumn("Link"),
                "status": st.column_config.SelectboxColumn("Status", options=all_statuses),
                "subject": st.column_config.SelectboxColumn("Subject", options=all_subjects),
                "stt": st.column_config.TextColumn("STT"), # Show STT
            },
            key=editor_key
        )
        
        st.caption("ℹ️ Chỉnh sửa trực tiếp trên bảng và bấm **'Lưu thay đổi'**.")
        
        # --- 3. Inline Edit Fallback (Expander) ---
        st.markdown("---")
        with st.expander("🛠️ Sửa Trial (Form chi tiết)", expanded=False):
            st.info("Nhập ID của trial cần sửa (xem cột đầu bảng hoặc cột ID nếu có)")
            # Create a list of available IDs for convenience? No, text input is faster for lookup if specific.
            # Or a selectbox if list is small. List filtered is better.
            
            # Since df_view is filtered, let's offer IDs from viewing
            available_ids = df_view.index.tolist()
            if available_ids:
                selected_id_edit = st.selectbox("Chọn ID Trial:", [None] + available_ids)
            else:
                selected_id_edit = None
                st.warning("Không có trial nào trong danh sách lọc.")
            
            if selected_id_edit:
                # Get row data
                try:
                    row_data = df.set_index('id').loc[selected_id_edit]
                    
                    with st.form(key=f"edit_form_{selected_id_edit}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            # Date parsing for default value
                            try:
                                d_default = datetime.strptime(row_data['trial_date'], "%d/%m/%Y")
                            except:
                                d_default = datetime.now()
                                
                            e_date = st.date_input("Ngày", value=d_default)
                            e_time = st.text_input("Giờ", value=row_data['time'])
                            e_subject = st.selectbox("Môn", all_subjects, index=all_subjects.index(row_data['subject']) if row_data['subject'] in all_subjects else 0)
                            e_phone = st.text_input("SĐT", value=row_data['phone'])
                        
                        with c2:
                            e_status = st.selectbox("Trạng thái", all_statuses, index=all_statuses.index(row_data['status']) if row_data['status'] in all_statuses else 0)
                            e_link = st.text_input("Link", value=row_data['meet_link'])
                            e_eval = st.text_input("Evaluator", value=row_data['evaluator'])
                            e_note = st.text_area("Note", value=row_data['note'], height=100)
                            
                        if st.form_submit_button("Cập nhật Trial này"):
                            update_data = {
                                'trial_date': e_date.strftime("%d/%m/%Y"),
                                'time': e_time,
                                'meet_link': e_link,
                                'subject': e_subject,
                                'phone': e_phone,
                                'status': e_status,
                                'note': e_note,
                                'evaluator': e_eval,
                                'creator': row_data['creator'] # Keep creator
                            }
                            if update_single_row(selected_id_edit, update_data):
                                st.success("Cập nhật thành công!")
                                st.rerun()
                except Exception as ex:
                    st.error(f"Lỗi load form: {ex}")
        
    else:
        st.info("Danh sách trống.")

# --- Tab 3: Thêm Trial mới ---
if selected_tab == "➕ Thêm Trial mới":
    st.header("Thêm Trial mới")
    
    with st.form("add_trial_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_date = st.date_input("Ngày Trial", value=datetime.now())
            new_time = st.time_input("Giờ Trial", value=datetime.strptime("19:00", "%H:%M"))
            new_subject = st.selectbox("Môn học", ["Coding", "Art", "Robotics", "Khác"])
            new_phone = st.text_input("Số điện thoại")
            
        with col2:
            new_link = st.text_input("Link Meet")
            new_status = st.selectbox("Trạng thái", ["Chờ trial", "Đã trial", "Hủy lịch", "Reschedule"])
            new_evaluator = st.text_input("Người đánh giá")
            new_note = st.text_area("Ghi chú (Note)", height=200)
            
        submitted = st.form_submit_button("Lưu Trial")
        
        if submitted:
            # Format date and time to string for DB
            date_str = new_date.strftime("%d/%m/%Y")
            time_str = new_time.strftime("%H:%M")
            
            new_data = {
                'stt': "New", 
                'trial_date': date_str,
                'time': time_str,
                'meet_link': new_link,
                'subject': new_subject,
                'phone': new_phone,
                'status': new_status,
                'note': new_note,
                'evaluator': new_evaluator,
                'creator': st.session_state.user_name
            }
            
            if add_trial(new_data):
                st.success("Đã thêm Trial mới thành công!")
                st.rerun()
