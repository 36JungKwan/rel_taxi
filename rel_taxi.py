import streamlit as st
import numpy as np
import pandas as pd

# ================= CẤU HÌNH WEB =================
st.set_page_config(page_title="AI Taxi Driver", layout="wide")
st.title("🚖 Học Tăng Cường: Môi Trường AI Taxi")
st.write("Bài toán kinh điển: Mở rộng không gian trạng thái với Hành khách và Điểm đến.")

# ================= HIỂN THỊ LUẬT CHƠI =================
with st.expander("📖 Xem Luật Chơi Chi Tiết (Taxi MDP)", expanded=False):
    st.markdown(r"""
    * **Bản đồ 5x5:** Bạn là tài xế Taxi 🚕. Có một khu chung cư 🏢 cản đường ở giữa.
    * **Mục tiêu:** Đến góc trái trên (0, 0) để **Đón khách 🧍**, sau đó chở đến góc phải dưới (4, 4) để **Trả khách 🏁**.
    * **Phần thưởng (Rewards):**
        * Mỗi bước di chuyển tốn xăng: **-1 điểm**.
        * Đón/Trả khách sai vị trí (bấm nút lung tung): Phạt nặng **-10 điểm**.
        * Trả khách đúng đích đến thành công: Thưởng lớn **+20 điểm** và kết thúc game.
    * **Điểm đột phá của AI:** Trạng thái giờ đây là một ma trận 3 chiều `[Hàng, Cột, Có_khách_hay_chưa]`.
    """)

# ================= THANH TRƯỢT TƯƠNG TÁC =================
st.sidebar.header("🕹️ Cài Đặt AI")
gamma = st.sidebar.slider(r"Hệ số suy giảm ($\gamma$)", 0.0, 0.99, 0.9, 0.05)
st.sidebar.info("Hệ số càng cao, AI càng sẵn sàng chịu tốn xăng để hướng tới khoản tiền thưởng +20 ở đích đến.")

# Các chướng ngại vật cố định
BUILDINGS = [(1, 2), (2, 2), (3, 2)] # Dãy nhà chắn ở cột 2

# ================= THUẬT TOÁN VALUE ITERATION (3D STATE) =================
@st.cache_data # Dùng cache để thuật toán không phải chạy lại từ đầu trừ khi đổi Gamma
def solve_taxi(gamma):
    # Trạng thái V: [Hàng, Cột, Có_Khách(0/1)] -> Kích thước (5, 5, 2)
    V = np.zeros((5, 5, 2))
    actions = ['⬆️ Lên', '⬇️ Xuống', '⬅️ Trái', '➡️ Phải', '🧍 Đón Khách', '🏁 Trả Khách']
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for _ in range(100):
        V_new = np.copy(V)
        for r in range(5):
            for c in range(5):
                if (r, c) in BUILDINGS: continue # Bỏ qua ô tòa nhà
                
                for has_pass in [0, 1]:
                    # Nếu đã chở khách tới đích -> Game over (Trạng thái kết thúc có Value = 0)
                    if r == 4 and c == 4 and has_pass == 1:
                        V_new[r, c, has_pass] = 0
                        continue
                        
                    v_acts = []
                    for act_idx, act in enumerate(actions):
                        # Bốn nút di chuyển
                        if act_idx < 4:
                            dr, dc = moves[act_idx]
                            nr, nc = r + dr, c + dc
                            # Nếu đâm tường, đâm nhà, ra ngoài biên -> Đứng im và trừ 1
                            if nr < 0 or nr >= 5 or nc < 0 or nc >= 5 or (nr, nc) in BUILDINGS:
                                v_acts.append(-1 + gamma * V[r, c, has_pass])
                            else:
                                v_acts.append(-1 + gamma * V[nr, nc, has_pass])
                                
                        # Nút Đón khách
                        elif act == '🧍 Đón Khách':
                            if r == 0 and c == 0 and has_pass == 0:
                                v_acts.append(-1 + gamma * V[r, c, 1]) # Đón thành công, chuyển sang trạng thái 1
                            else:
                                v_acts.append(-10 + gamma * V[r, c, has_pass]) # Bấm linh tinh phạt -10
                                
                        # Nút Trả khách
                        elif act == '🏁 Trả Khách':
                            if r == 4 and c == 4 and has_pass == 1:
                                v_acts.append(20 + 0) # Trả thành công, lấy 20 điểm và kết thúc
                            else:
                                v_acts.append(-10 + gamma * V[r, c, has_pass]) # Phạt -10
                    
                    V_new[r, c, has_pass] = max(v_acts)
        V = V_new

    # Lấy Chính sách tối ưu Pi*
    Pi = np.full((5, 5, 2), '', dtype=object)
    for r in range(5):
        for c in range(5):
            if (r, c) in BUILDINGS: 
                Pi[r, c, 0] = Pi[r, c, 1] = '🏢'
                continue
            for has_pass in [0, 1]:
                if r == 4 and c == 4 and has_pass == 1:
                    Pi[r, c, has_pass] = '🎉 Xong'
                    continue
                    
                best_val = -float('inf')
                best_act = ''
                for act_idx, act in enumerate(actions):
                    if act_idx < 4:
                        dr, dc = moves[act_idx]
                        nr, nc = r + dr, c + dc
                        val = -1 + gamma * V[r, c, has_pass] if (nr < 0 or nr >= 5 or nc < 0 or nc >= 5 or (nr, nc) in BUILDINGS) else -1 + gamma * V[nr, nc, has_pass]
                    elif act == '🧍 Đón Khách':
                        val = -1 + gamma * V[r, c, 1] if (r == 0 and c == 0 and has_pass == 0) else -10 + gamma * V[r, c, has_pass]
                    elif act == '🏁 Trả Khách':
                        val = 20 if (r == 4 and c == 4 and has_pass == 1) else -10 + gamma * V[r, c, has_pass]
                        
                    if val > best_val:
                        best_val = val
                        best_act = act
                Pi[r, c, has_pass] = best_act
                
    return V, Pi

V_star, Pi_star = solve_taxi(gamma)

# ================= CHIA TABS GIAO DIỆN =================
tab1, tab2 = st.tabs(["🎮 Chơi Trực Tiếp (Tài Xế Thực Tập)", "🔬 Phân Tích Bộ Não AI"])

# --- TAB 1: PHÂN TÍCH AI ---
with tab2:
    st.markdown("💡 **Điểm hay nhất của bài toán này:** AI tự động thay đổi mục tiêu dựa trên trạng thái của hành khách. Nếu chưa có khách, mũi tên chỉ về điểm đón. Khi có khách rồi, mũi tên lập tức đổi hướng chỉ về điểm trả!")
    col_pi0, col_pi1 = st.columns(2)
    with col_pi0:
        st.subheader("1. La bàn khi CHƯA CÓ khách 🧍")
        df_pi0 = pd.DataFrame(Pi_star[:, :, 0], columns=[f"Cột {i}" for i in range(5)], index=[f"Hàng {i}" for i in range(5)])
        st.dataframe(df_pi0, use_container_width=True)
    with col_pi1:
        st.subheader("2. La bàn khi ĐÃ ĐÓN khách 🚖")
        df_pi1 = pd.DataFrame(Pi_star[:, :, 1], columns=[f"Cột {i}" for i in range(5)], index=[f"Hàng {i}" for i in range(5)])
        st.dataframe(df_pi1, use_container_width=True)

# --- TAB 2: CHẾ ĐỘ NGƯỜI CHƠI ---
with tab1:
    st.subheader("Bảng Điều Khiển Taxi 🚕")
    
    # Khởi tạo Game State
    if 'tx_r' not in st.session_state: st.session_state.tx_r = 4
    if 'tx_c' not in st.session_state: st.session_state.tx_c = 0
    if 'tx_has_pass' not in st.session_state: st.session_state.tx_has_pass = 0
    if 'tx_score' not in st.session_state: st.session_state.tx_score = 0
    if 'tx_logs' not in st.session_state: st.session_state.tx_logs = ["Nhận ca làm việc! Hãy đi đón khách ở góc trái trên."]
    if 'tx_game_over' not in st.session_state: st.session_state.tx_game_over = False

    def reset_game():
        st.session_state.tx_r, st.session_state.tx_c = 4, 0
        st.session_state.tx_has_pass = 0
        st.session_state.tx_score = 0
        st.session_state.tx_logs = ["Đã chơi lại từ đầu!"]
        st.session_state.tx_game_over = False

    # Hàm xử lý mọi hành động
    def do_action(action, dr=0, dc=0):
        if st.session_state.tx_game_over: return
        r, c, hp = st.session_state.tx_r, st.session_state.tx_c, st.session_state.tx_has_pass
        ai_move = Pi_star[r, c, hp]
        
        # So sánh tư duy với AI
        msg_ai = f"🤖 AI khuyên: {ai_move}" if action != ai_move else "🤖 AI: Chuẩn!"

        if action in ['⬆️ Lên', '⬇️ Xuống', '⬅️ Trái', '➡️ Phải']:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= 5 or nc < 0 or nc >= 5 or (nr, nc) in BUILDINGS:
                st.session_state.tx_score -= 1
                log = f"Đâm tường/nhà! Phạt -1 điểm. {msg_ai}"
            else:
                st.session_state.tx_r, st.session_state.tx_c = nr, nc
                st.session_state.tx_score -= 1
                log = f"Đi {action}. Trừ -1 điểm xăng. {msg_ai}"
                
        elif action == '🧍 Đón Khách':
            if r == 0 and c == 0 and hp == 0:
                st.session_state.tx_has_pass = 1
                st.session_state.tx_score -= 1
                log = f"✅ Đón khách thành công! Mau tới đích đến. {msg_ai}"
            else:
                st.session_state.tx_score -= 10
                log = f"❌ Bấm đón khách sai chỗ! Phạt -10. {msg_ai}"
                
        elif action == '🏁 Trả Khách':
            if r == 4 and c == 4 and hp == 1:
                st.session_state.tx_score += 20
                st.session_state.tx_game_over = True
                log = f"🎉 TRẢ KHÁCH THÀNH CÔNG! Thưởng +20. Bạn được tổng {st.session_state.tx_score} điểm."
                st.balloons()
            else:
                st.session_state.tx_score -= 10
                log = f"❌ Bấm trả khách sai chỗ/Chưa đón khách! Phạt -10. {msg_ai}"
                
        st.session_state.tx_logs.insert(0, log)

    # GIAO DIỆN GAME
    col_game, col_ctrl = st.columns([1.5, 1])

    with col_game:
        sub_c1, sub_c2 = st.columns(2)
        sub_c1.metric("💵 Tiền lương (Điểm)", st.session_state.tx_score)
        pass_status = "💺 Có khách" if st.session_state.tx_has_pass else "🈳 Ghế trống"
        sub_c2.metric("Trạng thái", pass_status)
        
        # HTML/CSS Grid cho bản đồ Taxi
        html_grid = "<div style='display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; background-color: #343a40; padding: 10px; border-radius: 12px; max-width: 450px; margin: auto;'>"
        for r in range(5):
            for c in range(5):
                content = ""
                bg_color = "#e9ecef" # Màu đường xá
                
                # Vẽ chướng ngại vật
                if (r, c) in BUILDINGS:
                    content, bg_color = "🏢", "#6c757d"
                # Vẽ điểm đón (nếu chưa đón)
                elif r == 0 and c == 0:
                    if not st.session_state.tx_has_pass:
                        content, bg_color = "🧍", "#fff3cd"
                    else:
                        bg_color = "#fff3cd"
                # Vẽ điểm đích
                elif r == 4 and c == 4:
                    content, bg_color = "🏁", "#d1e7dd"
                    
                # Vẽ Taxi đè lên
                if r == st.session_state.tx_r and c == st.session_state.tx_c:
                    content = "🚖" if st.session_state.tx_has_pass else "🚕"
                    bg_color = "#ffc107" # Sáng màu nền taxi
                        
                cell_html = f"<div style='background-color: {bg_color}; border-radius: 8px; aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center; font-size: 2.2rem;'>{content}</div>"
                html_grid += cell_html
        html_grid += "</div><br>"
        st.markdown(html_grid, unsafe_allow_html=True)

    with col_ctrl:
        st.write("**Bảng Điều Khiển**")
        
        # Cụm phím D-pad
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col2: 
            if st.button("⬆️", use_container_width=True): do_action('⬆️ Lên', -1, 0); st.rerun()
        
        btn_col4, btn_col5, btn_col6 = st.columns(3)
        with btn_col4:
            if st.button("⬅️", use_container_width=True): do_action('⬅️ Trái', 0, -1); st.rerun()
        with btn_col5:
            if st.button("⬇️", use_container_width=True): do_action('⬇️ Xuống', 1, 0); st.rerun()
        with btn_col6:
            if st.button("➡️", use_container_width=True): do_action('➡️ Phải', 0, 1); st.rerun()

        st.markdown("---")
        # Nút Hành động đặc biệt
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("🧍 Đón Khách", use_container_width=True, type="primary"): do_action('🧍 Đón Khách'); st.rerun()
        with act_col2:
            if st.button("🏁 Trả Khách", use_container_width=True, type="primary"): do_action('🏁 Trả Khách'); st.rerun()
            
        if st.button("🔄 Chơi Lại", use_container_width=True): reset_game(); st.rerun()

    # NHẬT KÝ
    st.markdown("### 📻 Bộ đàm Taxi:")
    for log in st.session_state.tx_logs[:5]:
        st.info(log)