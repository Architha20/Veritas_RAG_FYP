"""
VeritasRAG Architecture Diagram — PPT-friendly (16:9, simplified)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ── Figure: 16:9 ratio, moderate DPI for crisp PPT export ──────────────────
fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=120)
ax.set_xlim(0, 133)
ax.set_ylim(32, 75)
ax.axis('off')
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

# ── Palette ─────────────────────────────────────────────────────────────────
C_RAG   = '#E3F2FD'
C_RAG_E = '#1565C0'
C_MID   = '#FFF8E1'
C_MID_E = '#E65100'
C_VER   = '#EDE7F6'
C_VER_E = '#4527A0'
C_OUT   = '#E0F7FA'
C_OUT_E = '#00838F'
C_ARR   = '#37474F'
C_TXT   = '#212121'


# ── Helpers ──────────────────────────────────────────────────────────────────
def box(x, y, w, h, label, fc, ec, fs=10, fw='bold', lw=1.8,
        bs="round,pad=0.3,rounding_size=0.5"):
    p = FancyBboxPatch((x, y), w, h, boxstyle=bs,
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(p)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=fs, fontweight=fw, color=C_TXT, zorder=3)

def arrow(x1, y1, x2, y2, color=C_ARR, lw=2.0):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='-|>', mutation_scale=18,
        linewidth=lw, color=color, zorder=4))

def label(x, y, txt, fs=8.5, color='#546E7A', ha='center'):
    ax.text(x, y, txt, ha=ha, va='center', fontsize=fs,
            color=color, style='italic', zorder=5)


# ════════════════════════════════════════════════════════════════════════════
# TITLE
# ════════════════════════════════════════════════════════════════════════════
ax.text(66.5, 71.5,
        "VeritasRAG — Hallucination Flagging Middleware",
        ha='center', va='center', fontsize=14, fontweight='bold', color=C_TXT)
ax.text(66.5, 68.5,
        "Sits between any RAG pipeline and the end user · verifies grounding claim-by-claim",
        ha='center', va='center', fontsize=9, style='italic', color='#757575')


# ════════════════════════════════════════════════════════════════════════════
# ROW 1  –  top-level flow  (y=44…60)
# ════════════════════════════════════════════════════════════════════════════

# [User Query]
box(4, 47, 18, 10, "User\nQuery", '#F5F5F5', '#90A4AE', fs=10)

# Arrow → RAG Pipeline
arrow(22, 52, 30, 52)
label(26, 54.5, "query")

# [RAG Pipeline]
box(30, 44, 26, 16, "RAG Pipeline\n(LLM + Vector DB\nretrieved chunks)",
    C_RAG, C_RAG_E, fs=9.5)

# Arrow → Middleware
arrow(56, 52, 65, 52, color=C_RAG_E, lw=2.2)
label(60.5, 54.5, "response +\nchunks", color=C_RAG_E)

# ════════════════════════════════════════════════════════════════════════════
# ROW 1  –  VeritasRAG Middleware container  (y=36…65)
# ════════════════════════════════════════════════════════════════════════════
mid_box = FancyBboxPatch((64, 35), 56, 30,
                         boxstyle="round,pad=0.4,rounding_size=0.8",
                         linewidth=2.2, edgecolor=C_MID_E,
                         facecolor=C_MID, zorder=1)
ax.add_patch(mid_box)
ax.text(92, 63.5, "VeritasRAG Middleware", ha='center', va='center',
        fontsize=11, fontweight='bold', color=C_MID_E, zorder=2)

# Three internal steps  (horizontal inside middleware)
# Step A  – Claim Decomposer
box(67, 41, 14, 12, "① Claim\nDecomposer", '#FCE4EC', '#AD1457', fs=9)
# Step B  – Verification Engine
box(85, 41, 18, 12, "② Verification\nEngine\n(NLI / Embedding)", C_VER, C_VER_E, fs=8.5)
# Step C  – Score Aggregator
box(107, 41, 10, 12, "③ Score\nAggregator", '#FFF3E0', '#E65100', fs=8.5)

# Arrows inside middleware
arrow(81, 47, 85, 47)
arrow(103, 47, 107, 47)

# Arrow OUT of middleware → Output
arrow(120, 52, 120, 52)   # placeholder for next section
arrow(117, 47, 124, 47, color=C_MID_E, lw=2.2)
label(120.5, 49.5, "grounding\nscores", color=C_MID_E)

# Vertical arrow: RAG response enters middleware (top of claim decomposer)
arrow(65, 52, 67, 47, color=C_RAG_E, lw=2.0)


# ════════════════════════════════════════════════════════════════════════════
# OUTPUT LAYER  (x=124…133, y=36…65)
# ════════════════════════════════════════════════════════════════════════════
box(124, 40, 8, 14, "Verified\nResponse\n+ Overlay", C_OUT, C_OUT_E, fs=8.5)


# ════════════════════════════════════════════════════════════════════════════
# LEGEND
# ════════════════════════════════════════════════════════════════════════════
handles = [
    mpatches.Patch(facecolor=C_RAG,   edgecolor=C_RAG_E, label='RAG Pipeline'),
    mpatches.Patch(facecolor=C_MID,   edgecolor=C_MID_E, label='VeritasRAG Middleware'),
    mpatches.Patch(facecolor=C_VER,   edgecolor=C_VER_E, label='Verification Engine'),
    mpatches.Patch(facecolor=C_OUT,   edgecolor=C_OUT_E, label='Output Layer'),
]
ax.legend(handles=handles, loc='lower center',
          bbox_to_anchor=(0.5, -0.01), ncol=4, frameon=True,
          fontsize=8.5, facecolor='white', edgecolor='#BDBDBD')


# ════════════════════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════════════════════
plt.tight_layout(pad=0.5)
output_path = "veritasrag_architecture.png"
plt.savefig(output_path, dpi=180, bbox_inches='tight',
            facecolor='white')
plt.close()
print(f"[OK] Diagram saved -> {output_path}")