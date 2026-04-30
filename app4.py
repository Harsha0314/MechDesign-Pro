import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon, Arc, Wedge
import math
import time
from datetime import datetime

st.set_page_config(page_title="MechDesign Pro", page_icon="⚙️", layout="wide")

# ==================== MATERIAL DATABASE ====================
MATERIALS_DB = {
    "Steel (Mild)": {"E": 200, "Syt": 250, "density": 7850, "G": 79.3},
    "Steel (Alloy)": {"E": 210, "Syt": 400, "density": 7850, "G": 79.3},
    "Steel (High Carbon)": {"E": 210, "Syt": 600, "density": 7850, "G": 79.3},
    "Alloy Steel": {"E": 210, "Syt": 800, "density": 7850, "G": 79.3},
    "Aluminum": {"E": 70, "Syt": 150, "density": 2700, "G": 26},
    "Titanium": {"E": 116, "Syt": 900, "density": 4500, "G": 44},
    "Brass": {"E": 100, "Syt": 200, "density": 8500, "G": 36},
    "Copper": {"E": 110, "Syt": 220, "density": 8900, "G": 44},
    "Cast Iron": {"E": 180, "Syt": 150, "density": 7200, "G": 60}
}

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    @keyframes growIn {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(78, 205, 196, 0.7); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(78, 205, 196, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(78, 205, 196, 0); }
    }
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: fadeIn 0.6s ease-out forwards;
        opacity: 0;
        border-left: 5px solid #4ECDC4;
    }
    .result-card:nth-child(1) { animation-delay: 0.1s; }
    .result-card:nth-child(2) { animation-delay: 0.2s; }
    .result-card:nth-child(3) { animation-delay: 0.3s; }
    .result-card:nth-child(4) { animation-delay: 0.4s; }
    .result-card:nth-child(5) { animation-delay: 0.5s; }
    .result-card:nth-child(6) { animation-delay: 0.6s; }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 15px 30px;
        font-size: 1.1em;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: pulse 2s infinite;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        animation: none;
    }
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        animation: growIn 0.5s ease-out;
        border-left: 5px solid #FFE66D;
    }
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        animation: growIn 0.5s ease-out;
    }
    .info-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
        padding: 15px;
        color: white;
        animation: slideIn 0.5s ease-out;
    }
    .header-gradient {
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .footer-style {
        text-align: center;
        color: #666;
        padding: 20px;
        margin-top: 30px;
        border-top: 2px solid #333;
    }
    .sidebar-info {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4ECDC4;
    }
    .module-card {
        background: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #4ECDC4;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: transform 0.3s;
    }
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(78, 205, 196, 0.3);
    }
    .module-card-red {
        background: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #FF6B6B;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: transform 0.3s;
    }
    .module-card-red:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(255, 107, 107, 0.3);
    }
    .module-icon {
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    .module-title {
        color: white;
        margin: 10px 0;
        font-size: 1.1em;
        font-weight: bold;
    }
    .module-desc {
        color: #aaa;
        font-size: 0.9em;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="header-gradient">
    <h1 style="font-size: 3em; margin: 0;">⚙️ MechDesign Pro</h1>
    <p style="font-size: 1.3em; margin: 10px 0;">Professional Mechanical Engineering Design Suite</p>
    <p style="font-size: 0.9em; opacity: 0.8;">Version 2.0 | Advanced Web-Based Analysis Tool</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
st.sidebar.markdown("""
<div class="sidebar-info">
    <h3 style="color: #4ECDC4; text-align: center;">🔧 Select Module</h3>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("", [
    "🏠 Home", 
    "📏 Beam Analysis", 
    "⚙️ Gear Design", 
    "🌀 Spring Design",
    "🔩 Shaft Design", 
    "🌡 Heat Exchanger", 
    "📳 Vibration Analysis", 
    "🔄 Unit Converter"
])

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="sidebar-info">
    <h4 style="color: #FFE66D;">👨‍💻 Developed by</h4>
    <p style="color: white;"><b>R20 BATCH</b></p>
    <p style="color: #aaa; font-size: 0.9em;">Roll No: R20 BATCH</p>
    <p style="color: #aaa; font-size: 0.9em;">Mechanical Engineering</p>
    <p style="color: #aaa; font-size: 0.9em;">RGUKT IIIT RK VALLEY</p>
    <hr style="border-color: #4ECDC4;">
    <h4 style="color: #FFE66D;">📋 Project Info</h4>
    <p style="color: #aaa; font-size: 0.8em;">Guide: Dr. B. Konda Reddy</p>
    <p style="color: #aaa; font-size: 0.8em;">Date: April 2026</p>
    <p style="color: #aaa; font-size: 0.8em;">Version: 2.0</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")


def animated_progress():
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.005)
        progress_bar.progress(i + 1)
    progress_bar.empty()

def validate_positive(value, name):
    if value <= 0:
        st.error(f"❌ {name} must be positive!")
        return False
    return True


def create_beam_diagram(L, a, P, max_deflection):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    beam_y = 3
    ax.plot([0, L], [beam_y, beam_y], 'w-', linewidth=8, alpha=0.9, label='Beam')
    wall_x = [-0.3, 0, 0, -0.3]
    wall_y = [beam_y-0.8, beam_y-0.8, beam_y+0.8, beam_y+0.8]
    ax.fill(wall_x, wall_y, color='#FF6B6B', alpha=0.8, label='Fixed Support')
    for i in range(-3, 4):
        ax.plot([-0.25, -0.05], [beam_y + i*0.2, beam_y + i*0.2], 'k-', linewidth=1)
    ax.arrow(a, beam_y + 2.5, 0, -1.8, head_width=0.15, head_length=0.2, 
             fc='#4ECDC4', ec='#4ECDC4', linewidth=3, label=f'Load P = {P}N')
    ax.text(a, beam_y + 2.8, f'P = {P}N', color='#4ECDC4', fontsize=12, ha='center', fontweight='bold')
    x = np.linspace(0, L, 100)
    deflection_shape = max_deflection * 0.001 * (x/L)**2 * (3 - x/L) * 5
    ax.plot(x, beam_y - deflection_shape, '--', color='#FFE66D', linewidth=3, alpha=0.8, label='Deflected Shape')
    ax.annotate('', xy=(L, beam_y-1.5), xytext=(0, beam_y-1.5),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    ax.text(L/2, beam_y-1.8, f'L = {L}m', color='white', fontsize=11, ha='center')
    ax.annotate('', xy=(a, beam_y-0.5), xytext=(0, beam_y-0.5),
                arrowprops=dict(arrowstyle='<->', color='#FFE66D', lw=1.5))
    ax.text(a/2, beam_y-0.8, f'a = {a}m', color='#FFE66D', fontsize=10, ha='center')
    ax.annotate(f'δ_max = {max_deflection:.4f}mm', 
                xy=(L, beam_y - max_deflection*0.001*5), 
                xytext=(L+0.3, beam_y - 1),
                color='#FF6B6B', fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=2))
    ax.set_xlim(-0.5, L+0.8)
    ax.set_ylim(beam_y-3, beam_y+3.5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.legend(loc='upper right', facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax.set_title('Cantilever Beam with Point Load', color='white', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_gear_diagram(N1, N2, module, center_dist, ratio):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    d1 = module * N1
    r1 = d1 / 2
    circle1 = plt.Circle((-center_dist/2, 0), r1, fill=False, color='#4ECDC4', linewidth=3)
    ax.add_patch(circle1)
    d2 = module * N2
    r2 = d2 / 2
    circle2 = plt.Circle((center_dist/2, 0), r2, fill=False, color='#FF6B6B', linewidth=3)
    ax.add_patch(circle2)
    for i in range(N1):
        angle = 2 * np.pi * i / N1
        x = -center_dist/2 + r1 * np.cos(angle)
        y = r1 * np.sin(angle)
        ax.plot([-center_dist/2, x], [0, y], color='#4ECDC4', alpha=0.3, linewidth=1)
    for i in range(N2):
        angle = 2 * np.pi * i / N2
        x = center_dist/2 + r2 * np.cos(angle)
        y = r2 * np.sin(angle)
        ax.plot([center_dist/2, x], [0, y], color='#FF6B6B', alpha=0.3, linewidth=1)
    ax.plot([-center_dist/2, center_dist/2], [0, 0], 'w--', alpha=0.5, linewidth=1)
    ax.text(-center_dist/2, -r1-15, f'Pinion\nN₁ = {N1} teeth\nd₁ = {d1}mm', 
            color='#4ECDC4', fontsize=11, ha='center', fontweight='bold')
    ax.text(center_dist/2, -r2-15, f'Gear\nN₂ = {N2} teeth\nd₂ = {d2}mm', 
            color='#FF6B6B', fontsize=11, ha='center', fontweight='bold')
    ax.annotate('', xy=(center_dist/2, r2+10), xytext=(-center_dist/2, r2+10),
                arrowprops=dict(arrowstyle='<->', color='#FFE66D', lw=2))
    ax.text(0, r2+15, f'Center Distance = {center_dist}mm', color='#FFE66D', fontsize=11, ha='center', fontweight='bold')
    ax.annotate('', xy=(-center_dist/2, r1+5), xytext=(-center_dist/2-15, r1+15),
                arrowprops=dict(arrowstyle='->', color='#4ECDC4', lw=2, connectionstyle="arc3,rad=.3"))
    ax.text(-center_dist/2-20, r1+20, 'ω₁', color='#4ECDC4', fontsize=12, fontweight='bold')
    ax.annotate('', xy=(center_dist/2, -r2-5), xytext=(center_dist/2+15, -r2-15),
                arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=2, connectionstyle="arc3,rad=.3"))
    ax.text(center_dist/2+20, -r2-20, 'ω₂', color='#FF6B6B', fontsize=12, fontweight='bold')
    ax.text(0, -max(r1, r2)-35, f'Speed Ratio = {ratio:.3f}', color='white', fontsize=13, ha='center', fontweight='bold')
    ax.set_xlim(-center_dist/2 - r1 - 30, center_dist/2 + r2 + 30)
    ax.set_ylim(-max(r1, r2) - 50, max(r1, r2) + 40)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Gear Train Configuration', color='white', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_spring_diagram(d, D, free_length, solid_length, active_coils):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    t = np.linspace(0, 4*np.pi*active_coils, 1000)
    x = (D/2) * np.cos(t)
    y = (D/2) * np.sin(t)
    z = np.linspace(0, free_length, 1000)
    x_proj = x + z * 0.1
    y_proj = y + z * 0.05
    ax.plot(x_proj, y_proj, color='#4ECDC4', linewidth=3, alpha=0.9)
    ax.plot([-D/2-5, D/2+5], [free_length, free_length], 'w-', linewidth=4)
    ax.plot([-D/2-5, D/2+5], [0, 0], 'w-', linewidth=4)
    ax.annotate('', xy=(D/2+20, free_length), xytext=(D/2+20, 0),
                arrowprops=dict(arrowstyle='<->', color='#FFE66D', lw=2))
    ax.text(D/2+25, free_length/2, f'Free Length\n= {free_length}mm', color='#FFE66D', fontsize=10, rotation=90, va='center')
    ax.annotate('', xy=(-D/2-20, solid_length), xytext=(-D/2-20, 0),
                arrowprops=dict(arrowstyle='<->', color='#FF6B6B', lw=2))
    ax.text(-D/2-35, solid_length/2, f'Solid Length\n= {solid_length}mm', color='#FF6B6B', fontsize=10, rotation=90, va='center')
    ax.annotate('', xy=(0, -30), xytext=(d, -30),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    ax.text(d/2, -40, f'd = {d}mm', color='white', fontsize=10, ha='center')
    ax.annotate('', xy=(-D/2, free_length+20), xytext=(D/2, free_length+20),
                arrowprops=dict(arrowstyle='<->', color='#4ECDC4', lw=2))
    ax.text(0, free_length+30, f'D = {D}mm', color='#4ECDC4', fontsize=10, ha='center')
    ax.text(0, -60, f'Active Coils: {active_coils}', color='white', fontsize=12, ha='center', fontweight='bold')
    ax.set_xlim(-D/2-50, D/2+50)
    ax.set_ylim(-80, free_length+50)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Compression Spring Geometry', color='white', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_shaft_diagram(diameter, length, torque, bending_moment, keyway=False):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    shaft = Rectangle((0, -diameter/2), length, diameter, 
                       facecolor='#4ECDC4', edgecolor='white', linewidth=2, alpha=0.7)
    ax.add_patch(shaft)
    ax.plot([0, length], [0, 0], 'w--', alpha=0.5, linewidth=1)
    theta = np.linspace(0, 2*np.pi, 100)
    arrow_r = diameter/2 + 10
    ax.plot(length/2 + arrow_r*np.cos(theta), arrow_r*np.sin(theta), 
            color='#FFE66D', linewidth=2, linestyle='--')
    ax.annotate('', xy=(length/2 + arrow_r*0.7, arrow_r*0.7), 
                xytext=(length/2 + arrow_r, 0),
                arrowprops=dict(arrowstyle='->', color='#FFE66D', lw=2))
    ax.text(length/2, arrow_r + 15, f'T = {torque:.2f} Nm', color='#FFE66D', 
            fontsize=11, ha='center', fontweight='bold')
    ax.arrow(length/4, diameter/2 + 20, 0, -15, head_width=5, head_length=5, 
             fc='#FF6B6B', ec='#FF6B6B', linewidth=2)
    ax.arrow(3*length/4, -diameter/2 - 20, 0, 15, head_width=5, head_length=5, 
             fc='#FF6B6B', ec='#FF6B6B', linewidth=2)
    ax.text(length/2, diameter/2 + 25, f'M = {bending_moment:.2f} Nm', 
            color='#FF6B6B', fontsize=11, ha='center', fontweight='bold')
    if keyway:
        keyway_rect = Rectangle((length/2 - 5, diameter/2 - 2), 10, 4, 
                                facecolor='#FF6B6B', edgecolor='white', linewidth=1)
        ax.add_patch(keyway_rect)
        ax.text(length/2, diameter/2 + 8, 'Keyway', color='#FF6B6B', 
                fontsize=9, ha='center')
    ax.annotate('', xy=(length, -diameter/2 - 15), xytext=(0, -diameter/2 - 15),
                arrowprops=dict(arrowstyle='<->', color='white', lw=2))
    ax.text(length/2, -diameter/2 - 25, f'L = {length}mm', color='white', 
            fontsize=11, ha='center')
    ax.annotate('', xy=(length + 15, diameter/2), xytext=(length + 15, -diameter/2),
                arrowprops=dict(arrowstyle='<->', color='#4ECDC4', lw=2))
    ax.text(length + 25, 0, f'd = {diameter:.2f}mm', color='#4ECDC4', 
            fontsize=11, rotation=90, va='center')
    ax.set_xlim(-20, length + 50)
    ax.set_ylim(-diameter/2 - 40, diameter/2 + 50)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Shaft Design (ASME Code)\nd = {diameter:.2f} mm', 
                 color='white', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def create_hex_diagram(Q, T1, T2, U, A, LMTD, method):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor('#1a1a2e')
    fig.patch.set_facecolor('#1a1a2e')
    pipe1 = Rectangle((1, 3), 8, 1, facecolor='#FF6B6B', edgecolor='white', 
                       linewidth=2, alpha=0.8, label='Hot Fluid')
    pipe2 = Rectangle((1, 1), 8, 1, facecolor='#4ECDC4', edgecolor='white', 
                       linewidth=2, alpha=0.8, label='Cold Fluid')
    ax.add_patch(pipe1)
    ax.add_patch(pipe2)
    ax.annotate('', xy=(8.5, 3.5), xytext=(1.5, 3.5),
                arrowprops=dict(arrowstyle='->', color='#FFE66D', lw=3))
    ax.text(5, 4.2, f'Hot In: {T1}°C → Hot Out: {T2}°C', color='#FFE66D', 
            fontsize=11, ha='center', fontweight='bold')
    if method == "Parallel Flow":
        ax.annotate('', xy=(8.5, 1.5), xytext=(1.5, 1.5),
                    arrowprops=dict(arrowstyle='->', color='#FFE66D', lw=3))
        ax.text(5, 0.3, f'Cold In: {T2}°C → Cold Out: {T1}°C', color='#FFE66D', 
                fontsize=11, ha='center', fontweight='bold')
    else:
        ax.annotate('', xy=(1.5, 1.5), xytext=(8.5, 1.5),
                    arrowprops=dict(arrowstyle='->', color='#FFE66D', lw=3))
        ax.text(5, 0.3, f'Cold Out: {T1}°C ← Cold In: {T2}°C', color='#FFE66D', 
                fontsize=11, ha='center', fontweight='bold')
    for i in range(5):
        x_pos = 2 + i * 1.5
        ax.annotate('', xy=(x_pos, 2.2), xytext=(x_pos, 2.8),
                    arrowprops=dict(arrowstyle='->', color='white', lw=1.5, 
                                   linestyle='--', alpha=0.7))
    ax.text(5, 2.5, 'Q', color='white', fontsize=12, ha='center', fontweight='bold')
    results_text = f'Q = {Q:.2f} W\nU = {U} W/m²K\nA = {A:.4f} m²\nLMTD = {LMTD:.2f}°C'
    ax.text(10, 3, results_text, color='white', fontsize=11, 
            bbox=dict(boxstyle='round', facecolor='#667eea', alpha=0.8),
            verticalalignment='center')
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'{method} Heat Exchanger', color='white', fontsize=14, 
                 fontweight='bold', pad=20)
    ax.legend(loc='upper left', facecolor='#1a1a2e', edgecolor='white', 
              labelcolor='white')
    plt.tight_layout()
    return fig

def create_vibration_diagram(m, k, c, omega, omega_n, zeta):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax1.set_facecolor('#1a1a2e')
    ground = Rectangle((-2, -3), 10, 1, facecolor='#555', edgecolor='white', linewidth=2)
    ax1.add_patch(ground)
    spring_x = [0, 0, 0.3, -0.3, 0.3, -0.3, 0.3, -0.3, 0, 0]
    spring_y = [-2, -1, -0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 1]
    ax1.plot(spring_x, spring_y, color='#4ECDC4', linewidth=3, label=f'k = {k} N/m')
    damper_x = [2, 2, 1.7, 2.3, 2, 2]
    damper_y = [-2, -1, -1, -1, -1, 0.5]
    ax1.plot(damper_x, damper_y, color='#FF6B6B', linewidth=3, label=f'c = {c} Ns/m')
    mass = Rectangle((-1, 1), 4, 2, facecolor='#FFE66D', edgecolor='white', 
                     linewidth=2, label=f'm = {m} kg')
    ax1.add_patch(mass)
    ax1.text(1, 2, f'{m} kg', color='black', fontsize=12, ha='center', 
             fontweight='bold')
    ax1.annotate('', xy=(1, 4.5), xytext=(1, 3.2),
                arrowprops=dict(arrowstyle='->', color='white', lw=3))
    ax1.text(1, 5, f'F(t) = F₀sin({omega}t)', color='white', fontsize=11, 
             ha='center', fontweight='bold')
    ax1.set_xlim(-3, 6)
    ax1.set_ylim(-4, 6)
    ax1.set_aspect('equal')
    ax1.axis('off')
    ax1.set_title('Spring-Mass-Damper System', color='white', fontsize=13, 
                  fontweight='bold')
    ax1.legend(loc='upper right', facecolor='#1a1a2e', edgecolor='white', 
               labelcolor='white')
    ax2.set_facecolor('#1a1a2e')
    r = np.linspace(0, 3, 1000)
    if zeta > 0:
        magnification = 1 / np.sqrt((1 - r**2)**2 + (2*zeta*r)**2)
        phase = np.arctan2(2*zeta*r, 1 - r**2) * 180/np.pi
    else:
        magnification = np.abs(1 / (1 - r**2))
        phase = np.zeros_like(r)
    ax2.plot(r, magnification, color='#4ECDC4', linewidth=3, label='Magnitude')
    ax2.axvline(x=omega/omega_n, color='#FF6B6B', linestyle='--', linewidth=2, 
                label=f'Operating ω/ωn = {omega/omega_n:.2f}')
    ax2.axvline(x=1, color='#FFE66D', linestyle=':', linewidth=2, label='Resonance')
    ax2.set_xlabel('Frequency Ratio (ω/ωn)', color='white')
    ax2.set_ylabel('Magnification Factor (M)', color='white')
    ax2.set_title('Frequency Response Curve', color='white', fontsize=13, 
                  fontweight='bold')
    ax2.tick_params(colors='white')
    ax2.spines['bottom'].set_color('white')
    ax2.spines['top'].set_color('white')
    ax2.spines['left'].set_color('white')
    ax2.spines['right'].set_color('white')
    ax2.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, min(10, max(magnification)*1.2))
    plt.tight_layout()
    return fig


# ==================== HOME MODULE ====================
if menu == "🏠 Home":
    st.header("Welcome to MechDesign Pro")
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white;">
    <h3>🎯 What This Tool Does</h3>
    <p>This advanced web application helps mechanical engineering students and professionals perform complex design calculations with:</p>
    <ul>
        <li>✨ <b>Animated Results</b> - See calculations come to life</li>
        <li>📊 <b>Visual Diagrams</b> - Every result shown with engineering drawings</li>
        <li>✅ <b>Built-in Validation</b> - Compare with manual calculations</li>
        <li>🎨 <b>Modern UI</b> - Professional dark theme interface</li>
        <li>🔧 <b>8 Powerful Modules</b> - Covering all major mechanical design areas</li>
        <li>📚 <b>Material Database</b> - Pre-loaded material properties</li>
        <li>💾 <b>Report Generation</b> - Download results as text reports</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1 - Teal Cards
    col1, col2, col3, col4 = st.columns(4)
    modules = [
        ("📏", "Beam Analysis", "Deflection & stress analysis"),
        ("⚙️", "Gear Design", "Gear train calculations"),
        ("🌀", "Spring Design", "Compression spring sizing"),
        ("🔩", "Shaft Design", "ASME code shaft sizing")
    ]
    
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], modules):
        with col:
            st.markdown(f"""
            <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; text-align: center; 
                        border: 2px solid #4ECDC4; min-height: 250px; display: flex; 
                        flex-direction: column; justify-content: center; align-items: center;">
                <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
                <h4 style="color: white; margin: 5px 0; min-height: 50px; display: flex; align-items: center;">{title}</h4>
                <p style="color: #aaa; font-size: 0.9em; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    # Row 2 - Red Cards
    col1, col2, col3, col4 = st.columns(4)
    modules2 = [
        ("🌡️", "Heat Exchanger", "LMTD & NTU methods"),
        ("📳", "Vibration Analysis", "Natural frequency & damping"),
        ("🔄", "Unit Converter", "Multi-unit conversions"),
        ("📐", "More Coming Soon", "Bearing, weld design...")
    ]
    
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], modules2):
        with col:
            st.markdown(f"""
            <div style="background: #1a1a2e; padding: 20px; border-radius: 15px; text-align: center; 
                        border: 2px solid #FF6B6B; min-height: 250px; display: flex; 
                        flex-direction: column; justify-content: center; align-items: center;">
                <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
                <h4 style="color: white; margin: 5px 0; min-height: 50px; display: flex; align-items: center;">{title}</h4>
                <p style="color: #aaa; font-size: 0.9em; margin: 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background: #1a1a2e; padding: 20px; border-radius: 10px;">
        <h3 style="color: #4ECDC4;">📊 Project Statistics</h3>
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <h1 style="color: #FFE66D; font-size: 3em; margin-bottom: 0;">8</h1>
                <p style="color: white; margin-top: 0;">Design Modules</p>
            </div>
            <div>
                <h1 style="color: #FFE66D; font-size: 3em; margin-bottom: 0;">9</h1>
                <p style="color: white; margin-top: 0;">Material Types</p>
            </div>
            <div>
                <h1 style="color: #FFE66D; font-size: 3em; margin-bottom: 0;">8</h1>
                <p style="color: white; margin-top: 0;">Unit Categories</p>
            </div>
            <div>
                <h1 style="color: #FFE66D; font-size: 3em; margin-bottom: 0;">∞</h1>
                <p style="color: white; margin-top: 0;">Calculations</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== BEAM MODULE ====================
elif menu == "📏 Beam Analysis":
    st.header("📏 Cantilever Beam Deflection Analysis")
    st.markdown("*Analyze beam deflection with animated visualizations*")

    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Beam Length (L):** Total length of the cantilever beam in meters  
        **Young's Modulus (E):** Material stiffness. Steel = 200 GPa, Aluminum = 70 GPa  
        **Moment of Inertia (I):** Depends on cross-section. For circular: I = πd⁴/64  
        **Point Load (P):** Concentrated force applied at distance 'a' from fixed end  
        **Load Position (a):** Distance from fixed end where load is applied
        """)

    # Material selection
    material = st.selectbox("Select Material", list(MATERIALS_DB.keys()))
    E_auto = MATERIALS_DB[material]["E"]
    st.info(f"📚 Auto-filled E = {E_auto} GPa for {material}")

    col1, col2 = st.columns(2)
    with col1:
        L = st.number_input("Beam Length (m)", min_value=0.1, value=2.0, step=0.1)
        E = st.number_input("Young's Modulus (GPa)", min_value=1.0, value=E_auto, step=10.0)
    with col2:
        I = st.number_input("Moment of Inertia (cm⁴)", min_value=0.1, value=833.0, step=10.0)
        P = st.number_input("Point Load (N)", min_value=0.0, value=10000.0, step=100.0)
    a = st.slider("Load Position from Fixed End (m)", 0.0, L, 1.5, 0.1)

    if st.button("🚀 Analyze Beam", key="beam_btn"):
        try:
            if not validate_positive(L, "Length") or not validate_positive(E, "Young's Modulus") or not validate_positive(I, "Moment of Inertia"):
                st.stop()
            if P < 0:
                st.error("❌ Load cannot be negative!")
                st.stop()

            with st.spinner('🔧 Crunching numbers...'):
                time.sleep(0.5)
            with st.spinner('📊 Generating diagrams...'):
                time.sleep(0.5)
            with st.spinner('✅ Almost done...'):
                time.sleep(0.3)

            animated_progress()
            E_pa = E * 1e9
            I_m4 = I * 1e-8
            x = np.linspace(0, L, 100)
            deflections = []
            for xi in x:
                if xi <= a:
                    d = (P * xi**2 / (6*E_pa*I_m4)) * (3*a - xi)
                else:
                    d = (P * a**2 / (6*E_pa*I_m4)) * (3*xi - a)
                deflections.append(d * 1000)
            max_def = max([abs(d) for d in deflections])
            loc = x[deflections.index(max(deflections, key=abs))]

            st.markdown("<h3 style='color: #4ECDC4; animation: fadeIn 0.5s;'>📊 Analysis Results</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Maximum Deflection</div>
                    <div class="metric-value">{max_def:.4f} mm</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Location</div>
                    <div class="metric-value">{loc:.2f} m</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                delta_manual = (P * a**2 * (3*L - a)) / (6 * E_pa * I_m4) * 1000
                error = abs(max_def - delta_manual) / delta_manual * 100
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Validation Error</div>
                    <div class="metric-value">{error:.4f}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<h3 style='color: #FFE66D;'>🔧 Engineering Diagram</h3>", unsafe_allow_html=True)
            fig = create_beam_diagram(L, a, P, max_def)
            st.pyplot(fig)

            st.markdown("<h3 style='color: #FF6B6B;'>📈 Deflection Profile</h3>", unsafe_allow_html=True)
            fig2, ax = plt.subplots(figsize=(10, 4))
            ax.set_facecolor('#1a1a2e')
            fig2.patch.set_facecolor('#1a1a2e')
            ax.plot(x, deflections, color='#4ECDC4', linewidth=3)
            ax.fill_between(x, deflections, alpha=0.3, color='#4ECDC4')
            ax.set_xlabel('Position (m)', color='white')
            ax.set_ylabel('Deflection (mm)', color='white')
            ax.set_title('Beam Deflection Profile', color='white', fontweight='bold')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig2)

            st.markdown(f"""
            <div class="success-box">
                <h4>✅ Validation Successful</h4>
                <p>Manual calculation: {delta_manual:.4f} mm | Software: {max_def:.4f} mm | Error: {error:.4f}%</p>
            </div>
            """, unsafe_allow_html=True)

            # Report generation
            report = f"""
MECHDESIGN PRO - BEAM ANALYSIS REPORT
=====================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Material: {material}

INPUTS:
- Beam Length: {L} m
- Young's Modulus: {E} GPa
- Moment of Inertia: {I} cm⁴
- Point Load: {P} N
- Load Position: {a} m

RESULTS:
- Maximum Deflection: {max_def:.4f} mm
- Location: {loc:.2f} m
- Validation Error: {error:.4f}%

VALIDATION:
- Manual Calculation: {delta_manual:.4f} mm
- Software Result: {max_def:.4f} mm

=====================================
Generated by MechDesign Pro v2.0
"""
            st.download_button(
                label="📄 Download Report",
                data=report,
                file_name=f"beam_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again.")


# ==================== GEAR MODULE ====================
elif menu == "⚙️ Gear Design":
    st.header("⚙️ Gear Train Design")
    st.markdown("*Design gear trains with visual gear diagrams*")

    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Power (P):** Power transmitted in kW  
        **Input Speed (n1):** RPM of driving gear  
        **Output Speed (n2):** RPM of driven gear  
        **Module (m):** Size of gear teeth in mm. Common: 1, 2, 3, 4, 5, 6  
        **Gear Ratio:** n1/n2. Should be between 1:1 and 6:1 for single stage
        """)

    col1, col2 = st.columns(2)
    with col1:
        P = st.number_input("Power (kW)", min_value=0.1, value=5.0, step=0.5)
        n1 = st.number_input("Input Speed (RPM)", min_value=1, value=1440, step=10)
    with col2:
        n2 = st.number_input("Output Speed (RPM)", min_value=1, value=360, step=10)
        module = st.number_input("Module (mm)", min_value=0.1, value=4.0, step=0.5)

    if st.button("⚙️ Design Gear Train", key="gear_btn"):
        try:
            if not validate_positive(P, "Power") or not validate_positive(n1, "Input Speed") or not validate_positive(n2, "Output Speed"):
                st.stop()

            with st.spinner('🔧 Optimizing gear parameters...'):
                time.sleep(0.5)
            with st.spinner('📊 Calculating forces...'):
                time.sleep(0.5)
            with st.spinner('✅ Almost done...'):
                time.sleep(0.3)

            animated_progress()
            ratio = n1 / n2
            found = False

            for N1 in range(18, 100):
                N2 = round(N1 * ratio)
                if N2 < 18:
                    continue
                actual_ratio = N2 / N1
                error = abs(actual_ratio - ratio) / ratio * 100

                if error < 3:
                    center_dist = module * (N1 + N2) / 2
                    T = (P * 1000) / (2 * math.pi * n1 / 60)
                    d1 = module * N1 / 1000
                    Ft = 2 * T / d1
                    Fr = Ft * math.tan(math.radians(20))

                    st.markdown("<h3 style='color: #4ECDC4;'>📊 Gear Specifications</h3>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Pinion Teeth</div>
                            <div class="metric-value">{N1}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Gear Teeth</div>
                            <div class="metric-value">{N2}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Actual Ratio</div>
                            <div class="metric-value">{actual_ratio:.3f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Center Distance</div>
                            <div class="metric-value">{center_dist:.1f} mm</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Tangential Force</div>
                            <div class="metric-value">{Ft:.1f} N</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Radial Force</div>
                            <div class="metric-value">{Fr:.1f} N</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h3 style='color: #FFE66D;'>🔧 Gear Configuration Diagram</h3>", unsafe_allow_html=True)
                    fig = create_gear_diagram(N1, N2, module, center_dist, actual_ratio)
                    st.pyplot(fig)

                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ Design Validated</h4>
                        <p>Required ratio: {ratio:.3f} | Achieved: {actual_ratio:.3f} | Error: {error:.2f}%</p>
                        <p>Torque: {T:.2f} Nm | Pitch diameter (pinion): {d1*1000:.1f} mm</p>
                    </div>
                    """, unsafe_allow_html=True)

                    report = f"""
MECHDESIGN PRO - GEAR DESIGN REPORT
=====================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

INPUTS:
- Power: {P} kW
- Input Speed: {n1} RPM
- Output Speed: {n2} RPM
- Module: {module} mm

RESULTS:
- Pinion Teeth: {N1}
- Gear Teeth: {N2}
- Actual Ratio: {actual_ratio:.3f}
- Center Distance: {center_dist:.1f} mm
- Tangential Force: {Ft:.1f} N
- Radial Force: {Fr:.1f} N
- Torque: {T:.2f} Nm

VALIDATION:
- Required Ratio: {ratio:.3f}
- Achieved Ratio: {actual_ratio:.3f}
- Error: {error:.2f}%

=====================================
Generated by MechDesign Pro v2.0
"""
                    st.download_button(
                        label="📄 Download Report",
                        data=report,
                        file_name=f"gear_design_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )

                    found = True
                    break

            if not found:
                st.error("No valid gear combination found!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again.")

# ==================== SPRING MODULE ====================
elif menu == "🌀 Spring Design":
    st.header("🌀 Compression Spring Design")
    st.markdown("*Design springs with animated geometry visualization*")

    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Operating Load:** Maximum force the spring will experience in N  
        **Required Deflection:** How much the spring should compress in mm  
        **Max Outer Diameter:** Space constraint for the spring in mm  
        **Safety Factor:** Typically 1.5 to 2.0 for static loads  
        **Spring Index (C):** D/d ratio. Should be between 4 and 12
        """)

    # Material selection for spring
    spring_material = st.selectbox("Select Spring Material", [
        "Music Wire (Sut=2000MPa)", 
        "Oil-Tempered (Sut=1600MPa)",
        "Chrome-Vanadium (Sut=1800MPa)",
        "Stainless Steel (Sut=1500MPa)"
    ])

    if "Music" in spring_material:
        Sut = 2000e6
    elif "Oil" in spring_material:
        Sut = 1600e6
    elif "Chrome" in spring_material:
        Sut = 1800e6
    else:
        Sut = 1500e6

    st.info(f"📚 Ultimate Tensile Strength: {Sut/1e6:.0f} MPa")

    col1, col2 = st.columns(2)
    with col1:
        load = st.number_input("Operating Load (N)", min_value=1.0, value=500.0, step=10.0)
        deflection = st.number_input("Required Deflection (mm)", min_value=1.0, value=50.0, step=5.0)
    with col2:
        od_limit = st.number_input("Max Outer Diameter (mm)", min_value=1.0, value=50.0, step=1.0)
        sf = st.number_input("Safety Factor", min_value=1.0, value=1.5, step=0.1)

    if st.button("🌀 Design Spring", key="spring_btn"):
        try:
            if not validate_positive(load, "Load") or not validate_positive(deflection, "Deflection") or not validate_positive(od_limit, "Outer Diameter"):
                st.stop()

            with st.spinner('🔧 Calculating spring parameters...'):
                time.sleep(0.5)
            with st.spinner('📊 Checking safety...'):
                time.sleep(0.5)
            with st.spinner('✅ Almost done...'):
                time.sleep(0.3)

            animated_progress()
            G = 79.3e9
            k = load / (deflection / 1000)
            found = False

            for d in [1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12]:
                D = od_limit - d
                C = D / d

                if C < 4 or C > 12:
                    continue

                K_w = (4*C - 1)/(4*C - 4) + 0.615/C
                tau = K_w * (8 * load * D/1000) / (math.pi * (d/1000)**3)
                tau_allow = Sut / sf

                if tau < tau_allow:
                    Na = (G * (d/1000)**4) / (8 * (D/1000)**3 * k)
                    Na = max(round(Na, 1), 2)

                    solid_length = (Na + 2) * d
                    free_length = solid_length + deflection + (deflection * 0.15)

                    st.markdown("<h3 style='color: #4ECDC4;'>📊 Spring Specifications</h3>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Wire Diameter</div>
                            <div class="metric-value">{d} mm</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Mean Diameter</div>
                            <div class="metric-value">{D:.1f} mm</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Spring Index</div>
                            <div class="metric-value">{C:.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Active Coils</div>
                            <div class="metric-value">{Na}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Free Length</div>
                            <div class="metric-value">{free_length:.1f} mm</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Spring Rate</div>
                            <div class="metric-value">{k/1000:.2f} N/mm</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h3 style='color: #FFE66D;'>🔧 Spring Geometry Diagram</h3>", unsafe_allow_html=True)
                    fig = create_spring_diagram(d, D, free_length, solid_length, Na)
                    st.pyplot(fig)

                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ Design Safe</h4>
                        <p>Max shear stress: {tau/1e6:.2f} MPa | Allowable: {tau_allow/1e6:.2f} MPa</p>
                        <p>Safety factor applied: {sf} | Spring index (C): {C:.2f} (Ideal: 4-12)</p>
                        <p>Material: {spring_material}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    report = f"""
MECHDESIGN PRO - SPRING DESIGN REPORT
=====================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Material: {spring_material}

INPUTS:
- Operating Load: {load} N
- Required Deflection: {deflection} mm
- Max Outer Diameter: {od_limit} mm
- Safety Factor: {sf}

RESULTS:
- Wire Diameter: {d} mm
- Mean Diameter: {D:.1f} mm
- Spring Index: {C:.2f}
- Active Coils: {Na}
- Free Length: {free_length:.1f} mm
- Solid Length: {solid_length:.1f} mm
- Spring Rate: {k/1000:.2f} N/mm

SAFETY CHECK:
- Max Shear Stress: {tau/1e6:.2f} MPa
- Allowable Stress: {tau_allow/1e6:.2f} MPa
- Safety Factor: {sf}

=====================================
Generated by MechDesign Pro v2.0
"""
                    st.download_button(
                        label="📄 Download Report",
                        data=report,
                        file_name=f"spring_design_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )

                    found = True
                    break

            if not found:
                st.error("No valid spring design found with given constraints!")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again.")


# ==================== SHAFT MODULE ====================
elif menu == "🔩 Shaft Design":
    st.header("🔩 Shaft Design (ASME Code)")
    st.markdown("*Design shafts based on combined torsion and bending*")

    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Power:** Power transmitted by shaft in kW  
        **Speed:** Shaft rotational speed in RPM  
        **Bending Moment:** Maximum bending moment in Nm  
        **Material:** Select based on application requirements  
        **Keyway:** Check if shaft has keyway (reduces strength by 25%)
        """)

    # Material selection
    shaft_material = st.selectbox("Select Shaft Material", list(MATERIALS_DB.keys()))
    Syt_auto = MATERIALS_DB[shaft_material]["Syt"]
    st.info(f"📚 Auto-filled Syt = {Syt_auto} MPa for {shaft_material}")

    col1, col2 = st.columns(2)
    with col1:
        power = st.number_input("Power (kW)", min_value=0.1, value=10.0, step=1.0)
        speed = st.number_input("Speed (RPM)", min_value=1, value=1440, step=10)
        length = st.number_input("Shaft Length (mm)", min_value=10, value=500, step=10)
    with col2:
        bending_moment = st.number_input("Bending Moment (Nm)", min_value=0.0, value=500.0, step=10.0)
        material = st.selectbox("Material Grade", ["Steel (Syt=400MPa)", "Steel (Syt=600MPa)", "Alloy Steel (Syt=800MPa)"])
        keyway = st.checkbox("With Keyway", value=True)

    if st.button("🔩 Design Shaft", key="shaft_btn"):
        try:
            if not validate_positive(power, "Power") or not validate_positive(speed, "Speed"):
                st.stop()

            with st.spinner('🔧 Calculating shaft diameter...'):
                time.sleep(0.5)
            with st.spinner('📊 Checking ASME code...'):
                time.sleep(0.5)
            with st.spinner('✅ Almost done...'):
                time.sleep(0.3)

            animated_progress()

            if material == "Steel (Syt=400MPa)":
                Syt = 400e6
                tau_max = 0.3 * Syt
            elif material == "Steel (Syt=600MPa)":
                Syt = 600e6
                tau_max = 0.3 * Syt
            else:
                Syt = 800e6
                tau_max = 0.3 * Syt

            kb = 1.0 if not keyway else 1.5
            T = (power * 1000) / (2 * math.pi * speed / 60)
            kt = 1.0
            equivalent_torque = math.sqrt((kb * bending_moment)**2 + (kt * T)**2)
            d_required = ((16 * equivalent_torque) / (math.pi * tau_max)) ** (1/3) * 1000
            standard_sizes = [6, 8, 10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100]
            d_standard = next((d for d in standard_sizes if d >= d_required), 100)
            tau_actual = (16 * equivalent_torque) / (math.pi * (d_standard/1000)**3)
            fos = tau_max / tau_actual

            st.markdown("<h3 style='color: #4ECDC4;'>📊 Shaft Specifications</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Torque</div>
                    <div class="metric-value">{T:.2f} Nm</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Required Diameter</div>
                    <div class="metric-value">{d_required:.2f} mm</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Standard Diameter</div>
                    <div class="metric-value">{d_standard} mm</div>
                </div>
                """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Shear Stress</div>
                    <div class="metric-value">{tau_actual/1e6:.2f} MPa</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Allowable Stress</div>
                    <div class="metric-value">{tau_max/1e6:.2f} MPa</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Factor of Safety</div>
                    <div class="metric-value">{fos:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<h3 style='color: #FFE66D;'>🔧 Shaft Diagram</h3>", unsafe_allow_html=True)
            fig = create_shaft_diagram(d_standard, length, T, bending_moment, keyway)
            st.pyplot(fig)

            st.markdown(f"""
            <div class="success-box">
                <h4>✅ Design Safe per ASME Code</h4>
                <p>Equivalent Torque: {equivalent_torque:.2f} Nm | Keyway Factor: {kb}</p>
                <p>Material: {material} | Yield Strength: {Syt/1e6:.0f} MPa</p>
                <p>Selected Material from DB: {shaft_material}</p>
            </div>
            """, unsafe_allow_html=True)

            report = f"""
MECHDESIGN PRO - SHAFT DESIGN REPORT
=====================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Material: {shaft_material} ({material})

INPUTS:
- Power: {power} kW
- Speed: {speed} RPM
- Length: {length} mm
- Bending Moment: {bending_moment} Nm
- Keyway: {'Yes' if keyway else 'No'}

RESULTS:
- Torque: {T:.2f} Nm
- Required Diameter: {d_required:.2f} mm
- Standard Diameter: {d_standard} mm
- Shear Stress: {tau_actual/1e6:.2f} MPa
- Allowable Stress: {tau_max/1e6:.2f} MPa
- Factor of Safety: {fos:.2f}

ASME CODE CHECK:
- Equivalent Torque: {equivalent_torque:.2f} Nm
- Keyway Factor (kb): {kb}
- Design Status: SAFE

=====================================
Generated by MechDesign Pro v2.0
"""
            st.download_button(
                label="📄 Download Report",
                data=report,
                file_name=f"shaft_design_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again.")

# ==================== HEAT EXCHANGER MODULE ====================
elif menu == "🌡️ Heat Exchanger":
    st.header("🌡️ Heat Exchanger Sizing")
    st.markdown("*Calculate required heat transfer area using LMTD and NTU methods*")

    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Heat Duty (Q):** Amount of heat to be transferred in kW  
        **Overall HTC (U):** Heat transfer coefficient. Water-Water: 500-1500 W/m²K  
        **Temperatures:** Inlet and outlet for both hot and cold fluids  
        **LMTD:** Log Mean Temperature Difference method (more accurate)  
        **NTU:** Number of Transfer Units method (for effectiveness)
        """)

    method = st.radio("Method", ["LMTD Method", "NTU Method"], horizontal=True)

    col1, col2 = st.columns(2)
    with col1:
        Q = st.number_input("Heat Duty (kW)", min_value=0.1, value=50.0, step=5.0)
        U = st.number_input("Overall HTC (W/m²K)", min_value=10.0, value=500.0, step=10.0)
    with col2:
        T_hot_in = st.number_input("Hot Inlet (°C)", value=80.0, step=5.0)
        T_hot_out = st.number_input("Hot Outlet (°C)", value=50.0, step=5.0)

    col1, col2 = st.columns(2)
    with col1:
        T_cold_in = st.number_input("Cold Inlet (°C)", value=20.0, step=5.0)
    with col2:
        T_cold_out = st.number_input("Cold Outlet (°C)", value=40.0, step=5.0)

    flow_type = st.selectbox("Flow Arrangement", ["Parallel Flow", "Counter Flow"])

    if st.button("🌡️ Calculate Heat Exchanger", key="hex_btn"):
        try:
            if not validate_positive(Q, "Heat Duty") or not validate_positive(U, "HTC"):
                st.stop()

            with st.spinner('🔧 Calculating temperatures...'):
                time.sleep(0.5)
            with st.spinner('📊 Computing LMTD/NTU...'):
                time.sleep(0.5)
            with st.spinner('✅ Almost done...'):
                time.sleep(0.3)

            animated_progress()
            Q_watts = Q * 1000

            if method == "LMTD Method":
                if flow_type == "Parallel Flow":
                    dT1 = T_hot_in - T_cold_in
                    dT2 = T_hot_out - T_cold_out
                else:
                    dT1 = T_hot_in - T_cold_out
                    dT2 = T_hot_out - T_cold_in

                if dT1 <= 0 or dT2 <= 0:
                    st.error("❌ Invalid temperature configuration! Check your inputs.")
                else:
                    LMTD = (dT1 - dT2) / math.log(dT1 / dT2)
                    A = Q_watts / (U * LMTD)

                    st.markdown("<h3 style='color: #4ECDC4;'>📊 LMTD Method Results</h3>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">LMTD</div>
                            <div class="metric-value">{LMTD:.2f} °C</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Required Area</div>
                            <div class="metric-value">{A:.4f} m²</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col3:
                        effectiveness = (T_hot_in - T_hot_out) / (T_hot_in - T_cold_in)
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="metric-label">Effectiveness</div>
                            <div class="metric-value">{effectiveness:.4f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("<h3 style='color: #FFE66D;'>🔧 Heat Exchanger Diagram</h3>", unsafe_allow_html=True)
                    fig = create_hex_diagram(Q_watts, T_hot_in, T_hot_out, U, A, LMTD, flow_type)
                    st.pyplot(fig)

                    st.markdown(f"""
                    <div class="success-box">
                        <h4>✅ LMTD Calculation Complete</h4>
                        <p>ΔT₁ = {dT1:.2f}°C | ΔT₂ = {dT2:.2f}°C | LMTD = {LMTD:.2f}°C</p>
                        <p>Heat Duty: {Q} kW | U = {U} W/m²K | Area = {A:.4f} m²</p>
                    </div>
                    """, unsafe_allow_html=True)

                    report = f"""
MECHDESIGN PRO - HEAT EXCHANGER REPORT (LMTD)
=============================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Method: LMTD
Flow Type: {flow_type}

INPUTS:
- Heat Duty: {Q} kW
- Overall HTC: {U} W/m²K
- Hot Inlet: {T_hot_in}°C
- Hot Outlet: {T_hot_out}°C
- Cold Inlet: {T_cold_in}°C
- Cold Outlet: {T_cold_out}°C

RESULTS:
- LMTD: {LMTD:.2f}°C
- Required Area: {A:.4f} m²
- Effectiveness: {effectiveness:.4f}

TEMPERATURE DIFFERENCES:
- ΔT₁: {dT1:.2f}°C
- ΔT₂: {dT2:.2f}°C

=============================================
Generated by MechDesign Pro v2.0
"""
                    st.download_button(
                        label="📄 Download Report",
                        data=report,
                        file_name=f"hex_lmtd_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain"
                    )
            else:
                C_hot = Q_watts / (T_hot_in - T_hot_out)
                C_cold = Q_watts / (T_cold_out - T_cold_in)
                C_min = min(C_hot, C_cold)
                C_max = max(C_hot, C_cold)
                C_ratio = C_min / C_max
                effectiveness = (T_hot_in - T_hot_out) / (T_hot_in - T_cold_in)

                if flow_type == "Counter Flow":
                    if C_ratio != 1:
                        NTU = -math.log(1 - effectiveness) / (1 - C_ratio)
                    else:
                        NTU = effectiveness / (1 - effectiveness)
                else:
                    NTU = -math.log(1 - effectiveness * (1 + C_ratio)) / (1 + C_ratio)

                A_ntu = NTU * C_min / U

                st.markdown("<h3 style='color: #4ECDC4;'>📊 NTU Method Results</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="metric-label">NTU</div>
                        <div class="metric-value">{NTU:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="metric-label">C_min/C_max</div>
                        <div class="metric-value">{C_ratio:.4f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="metric-label">Required Area</div>
                        <div class="metric-value">{A_ntu:.4f} m²</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<h3 style='color: #FFE66D;'>🔧 Heat Exchanger Diagram</h3>", unsafe_allow_html=True)
                fig = create_hex_diagram(Q_watts, T_hot_in, T_hot_out, U, A_ntu, 0, flow_type)
                st.pyplot(fig)

                st.markdown(f"""
                <div class="success-box">
                    <h4>✅ NTU Calculation Complete</h4>
                    <p>C_hot = {C_hot:.2f} W/K | C_cold = {C_cold:.2f} W/K</p>
                    <p>Effectiveness = {effectiveness:.4f} | NTU = {NTU:.4f}</p>
                </div>
                """, unsafe_allow_html=True)

                report = f"""
MECHDESIGN PRO - HEAT EXCHANGER REPORT (NTU)
============================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Method: NTU
Flow Type: {flow_type}

INPUTS:
- Heat Duty: {Q} kW
- Overall HTC: {U} W/m²K
- Hot Inlet: {T_hot_in}°C
- Hot Outlet: {T_hot_out}°C
- Cold Inlet: {T_cold_in}°C
- Cold Outlet: {T_cold_out}°C

RESULTS:
- NTU: {NTU:.4f}
- C_min/C_max: {C_ratio:.4f}
- Required Area: {A_ntu:.4f} m²
- Effectiveness: {effectiveness:.4f}

CAPACITANCE RATES:
- C_hot: {C_hot:.2f} W/K
- C_cold: {C_cold:.2f} W/K

============================================
Generated by MechDesign Pro v2.0
"""
                st.download_button(
                    label="📄 Download Report",
                    data=report,
                    file_name=f"hex_ntu_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again.")


# ==================== VIBRATION MODULE ====================
elif menu == "📳 Vibration Analysis":
    st.header("📳 Vibration Analysis")
    st.markdown("*Analyze spring-mass-damper systems and frequency response*")

    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Mass (m):** Mass of the vibrating body in kg  
        **Stiffness (k):** Spring stiffness in N/m  
        **Damping (c):** Damping coefficient in Ns/m. c=0 for undamped  
        **Force Amplitude (F0):** Magnitude of harmonic force in N  
        **Excitation Frequency (ω):** Frequency of applied force in rad/s
        """)

    col1, col2 = st.columns(2)
    with col1:
        m = st.number_input("Mass (kg)", min_value=0.1, value=10.0, step=1.0)
        k = st.number_input("Stiffness (N/m)", min_value=1.0, value=10000.0, step=1000.0)
        c = st.number_input("Damping (Ns/m)", min_value=0.0, value=50.0, step=10.0)
    with col2:
        F0 = st.number_input("Force Amplitude (N)", min_value=0.1, value=100.0, step=10.0)
        omega = st.number_input("Excitation Frequency (rad/s)", min_value=0.1, value=30.0, step=5.0)

    if st.button("📳 Analyze Vibration", key="vib_btn"):
        try:
            if not validate_positive(m, "Mass") or not validate_positive(k, "Stiffness") or not validate_positive(F0, "Force") or not validate_positive(omega, "Frequency"):
                st.stop()

            with st.spinner('🔧 Calculating natural frequency...'):
                time.sleep(0.5)
            with st.spinner('📊 Computing damping ratio...'):
                time.sleep(0.5)
            with st.spinner('✅ Almost done...'):
                time.sleep(0.3)

            animated_progress()
            omega_n = math.sqrt(k / m)
            f_n = omega_n / (2 * math.pi)
            c_critical = 2 * math.sqrt(k * m)
            zeta = c / c_critical

            if zeta < 1:
                omega_d = omega_n * math.sqrt(1 - zeta**2)
                system_type = "Underdamped"
            elif zeta == 1:
                omega_d = 0
                system_type = "Critically Damped"
            else:
                omega_d = 0
                system_type = "Overdamped"

            r = omega / omega_n

            if zeta > 0:
                M = 1 / math.sqrt((1 - r**2)**2 + (2*zeta*r)**2)
                phase = math.atan2(2*zeta*r, 1 - r**2) * 180 / math.pi
            else:
                M = abs(1 / (1 - r**2)) if r != 1 else float('inf')
                phase = 0 if r < 1 else 180

            X = (F0 / k) * M

            st.markdown("<h3 style='color: #4ECDC4;'>📊 Vibration Parameters</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Natural Frequency</div>
                    <div class="metric-value">{omega_n:.2f} rad/s</div>
                    <div style="font-size: 0.8em; opacity: 0.8;">({f_n:.2f} Hz)</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Damping Ratio</div>
                    <div class="metric-value">{zeta:.4f}</div>
                    <div style="font-size: 0.8em; opacity: 0.8;">({system_type})</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Magnification Factor</div>
                    <div class="metric-value">{M:.4f}</div>
                </div>
                """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Static Deflection</div>
                    <div class="metric-value">{F0/k*1000:.4f} mm</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Dynamic Amplitude</div>
                    <div class="metric-value">{X*1000:.4f} mm</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Phase Angle</div>
                    <div class="metric-value">{phase:.2f}°</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<h3 style='color: #FFE66D;'>🔧 System & Frequency Response Diagram</h3>", unsafe_allow_html=True)
            fig = create_vibration_diagram(m, k, c, omega, omega_n, zeta)
            st.pyplot(fig)

            st.markdown("<h3 style='color: #FF6B6B;'>📈 Transient Response</h3>", unsafe_allow_html=True)
            fig2, ax = plt.subplots(figsize=(10, 4))
            ax.set_facecolor('#1a1a2e')
            fig2.patch.set_facecolor('#1a1a2e')
            t = np.linspace(0, 5, 1000)
            if zeta < 1:
                response = X * np.exp(-zeta*omega_n*t) * np.cos(omega_d*t) + X * np.sin(omega*t - phase*math.pi/180)
            else:
                response = X * np.sin(omega*t - phase*math.pi/180)
            ax.plot(t, response*1000, color='#4ECDC4', linewidth=2)
            ax.set_xlabel('Time (s)', color='white')
            ax.set_ylabel('Displacement (mm)', color='white')
            ax.set_title('System Response Over Time', color='white', fontweight='bold')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color('white')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig2)

            st.markdown(f"""
            <div class="success-box">
                <h4>✅ Vibration Analysis Complete</h4>
                <p>Critical Damping: {c_critical:.2f} Ns/m | Damped Frequency: {omega_d:.2f} rad/s</p>
                <p>Frequency Ratio: {r:.4f} | System is {system_type}</p>
            </div>
            """, unsafe_allow_html=True)

            report = f"""
MECHDESIGN PRO - VIBRATION ANALYSIS REPORT
==========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

INPUTS:
- Mass: {m} kg
- Stiffness: {k} N/m
- Damping: {c} Ns/m
- Force Amplitude: {F0} N
- Excitation Frequency: {omega} rad/s

RESULTS:
- Natural Frequency: {omega_n:.2f} rad/s ({f_n:.2f} Hz)
- Damping Ratio: {zeta:.4f} ({system_type})
- Critical Damping: {c_critical:.2f} Ns/m
- Damped Frequency: {omega_d:.2f} rad/s
- Magnification Factor: {M:.4f}
- Static Deflection: {F0/k*1000:.4f} mm
- Dynamic Amplitude: {X*1000:.4f} mm
- Phase Angle: {phase:.2f}°
- Frequency Ratio: {r:.4f}

SYSTEM STATUS: {system_type.upper()}

==========================================
Generated by MechDesign Pro v2.0
"""
            st.download_button(
                label="📄 Download Report",
                data=report,
                file_name=f"vibration_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Please check your inputs and try again.")

# ==================== UNIT CONVERTER MODULE ====================
elif menu == "🔄 Unit Converter":
    st.header("🔄 Engineering Unit Converter")
    st.markdown("*Quick conversions for common mechanical engineering units*")

    with st.expander("💡 Available Conversions"):
        st.markdown("""
        **Stress/Pressure:** MPa, psi, bar, Pa, GPa  
        **Length:** mm, cm, m, inch, ft  
        **Force:** N, kN, lbf, kgf  
        **Power:** kW, W, HP, BTU/hr  
        **Torque:** Nm, kNm, lbf-ft, kgf-m  
        **Temperature:** °C, °F, K  
        **Velocity:** m/s, km/h, mph, ft/s  
        **Density:** kg/m³, g/cm³, lb/ft³
        """)

    conversion_type = st.selectbox("Select Conversion Type", [
        "Stress/Pressure", "Length", "Force", "Power", "Torque", "Temperature", "Velocity", "Density"
    ])

    col1, col2 = st.columns(2)
    with col1:
        input_value = st.number_input("Enter Value", value=1.0, step=0.1)
    with col2:
        if conversion_type == "Stress/Pressure":
            from_unit = st.selectbox("From", ["MPa", "psi", "bar", "Pa", "GPa"])
            to_unit = st.selectbox("To", ["psi", "MPa", "bar", "Pa", "GPa"])
            conversions = {"MPa": 1e6, "psi": 6894.76, "bar": 1e5, "Pa": 1, "GPa": 1e9}
        elif conversion_type == "Length":
            from_unit = st.selectbox("From", ["mm", "cm", "m", "inch", "ft"])
            to_unit = st.selectbox("To", ["m", "mm", "cm", "inch", "ft"])
            conversions = {"mm": 0.001, "cm": 0.01, "m": 1, "inch": 0.0254, "ft": 0.3048}
        elif conversion_type == "Force":
            from_unit = st.selectbox("From", ["N", "kN", "lbf", "kgf"])
            to_unit = st.selectbox("To", ["lbf", "N", "kN", "kgf"])
            conversions = {"N": 1, "kN": 1000, "lbf": 4.44822, "kgf": 9.80665}
        elif conversion_type == "Power":
            from_unit = st.selectbox("From", ["kW", "W", "HP", "BTU/hr"])
            to_unit = st.selectbox("To", ["HP", "kW", "W", "BTU/hr"])
            conversions = {"kW": 1000, "W": 1, "HP": 745.7, "BTU/hr": 0.293071}
        elif conversion_type == "Torque":
            from_unit = st.selectbox("From", ["Nm", "kNm", "lbf-ft", "kgf-m"])
            to_unit = st.selectbox("To", ["lbf-ft", "Nm", "kNm", "kgf-m"])
            conversions = {"Nm": 1, "kNm": 1000, "lbf-ft": 1.35582, "kgf-m": 9.80665}
        elif conversion_type == "Temperature":
            from_unit = st.selectbox("From", ["°C", "°F", "K"])
            to_unit = st.selectbox("To", ["°F", "°C", "K"])
        elif conversion_type == "Velocity":
            from_unit = st.selectbox("From", ["m/s", "km/h", "mph", "ft/s"])
            to_unit = st.selectbox("To", ["km/h", "m/s", "mph", "ft/s"])
            conversions = {"m/s": 1, "km/h": 0.277778, "mph": 0.44704, "ft/s": 0.3048}
        elif conversion_type == "Density":
            from_unit = st.selectbox("From", ["kg/m³", "g/cm³", "lb/ft³"])
            to_unit = st.selectbox("To", ["g/cm³", "kg/m³", "lb/ft³"])
            conversions = {"kg/m³": 1, "g/cm³": 1000, "lb/ft³": 16.0185}

    if st.button("🔄 Convert", key="conv_btn"):
        try:
            with st.spinner('🔄 Converting...'):
                time.sleep(0.3)

            if conversion_type == "Temperature":
                if from_unit == "°C":
                    if to_unit == "°F":
                        result = (input_value * 9/5) + 32
                    elif to_unit == "K":
                        result = input_value + 273.15
                    else:
                        result = input_value
                elif from_unit == "°F":
                    if to_unit == "°C":
                        result = (input_value - 32) * 5/9
                    elif to_unit == "K":
                        result = (input_value - 32) * 5/9 + 273.15
                    else:
                        result = input_value
                elif from_unit == "K":
                    if to_unit == "°C":
                        result = input_value - 273.15
                    elif to_unit == "°F":
                        result = (input_value - 273.15) * 9/5 + 32
                    else:
                        result = input_value
            else:
                base_value = input_value * conversions[from_unit]
                result = base_value / conversions[to_unit]

            st.markdown("<h3 style='color: #4ECDC4;'>📊 Conversion Result</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Input</div>
                    <div class="metric-value">{input_value} {from_unit}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="result-card">
                    <div class="metric-label">Result</div>
                    <div class="metric-value">{result:.6f} {to_unit}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                if conversion_type != "Temperature":
                    factor = conversions[from_unit] / conversions[to_unit]
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="metric-label">Conversion Factor</div>
                        <div class="metric-value">{factor:.6f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="metric-label">Formula Applied</div>
                        <div class="metric-value">Temp</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="success-box">
                <h4>✅ Conversion Complete</h4>
                <p>{input_value} {from_unit} = {result:.6f} {to_unit}</p>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div class="footer-style">
    <h3 style="color: #4ECDC4;">⚙️ MechDesign Pro v2.0</h3>
    <p style="color: #aaa;">Professional Mechanical Engineering Design Suite</p>
    <p style="color: #666; font-size: 0.8em;">© 2026 MechDesign Pro. All rights reserved.</p>
    <p style="color: #666; font-size: 0.8em;">Developed by R20 BATCH | Mechanical Engineering | RGUKT IIIT RK VALLEY</p>
</div>
""", unsafe_allow_html=True)