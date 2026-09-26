"""
Visual HTML Overlay Renderer for VeritasRAG.
Produces an interactive, color-coded visual report of RAG grounding.
"""

from ..core.models import VerificationResult, InferenceType


class HTMLOverlayRenderer:
    """
    Renders VerificationResult into standalone, beautifully styled HTML.
    """

    COLOR_THEMES = {
        InferenceType.GROUNDED: {
            "bg": "#f0fdf4",
            "border": "#22c55e",
            "text": "#15803d",
            "badge_bg": "#dcfce7",
            "icon": "🟢",
            "label": "Grounded",
        },
        InferenceType.INFERRED: {
            "bg": "#fffbeb",
            "border": "#f59e0b",
            "text": "#b45309",
            "badge_bg": "#fef3c7",
            "icon": "🟡",
            "label": "Inferred",
        },
        InferenceType.HALLUCINATED: {
            "bg": "#fef2f2",
            "border": "#ef4444",
            "text": "#b91c1c",
            "badge_bg": "#fee2e2",
            "icon": "🔴",
            "label": "Hallucinated",
        },
        InferenceType.CONTESTED: {
            "bg": "#faf5ff",
            "border": "#a855f7",
            "text": "#7e22ce",
            "badge_bg": "#f3e8ff",
            "icon": "🟣",
            "label": "Contested",
        },
    }

    @classmethod
    def render(cls, result: VerificationResult, title: str = "VeritasRAG Grounding Overlay") -> str:
        # Counters
        grounded_count = sum(1 for o in result.sentence_overlays if o.inference_type == InferenceType.GROUNDED)
        inferred_count = sum(1 for o in result.sentence_overlays if o.inference_type == InferenceType.INFERRED)
        hallucinated_count = sum(1 for o in result.sentence_overlays if o.inference_type == InferenceType.HALLUCINATED)
        total = len(result.sentence_overlays)

        # Build sentence cards
        cards_html = []
        for o in result.sentence_overlays:
            theme = cls.COLOR_THEMES.get(o.inference_type, cls.COLOR_THEMES[InferenceType.HALLUCINATED])
            
            # Evidence block
            if o.cited_chunk_ids:
                citation_pills = " ".join(
                    f"<span style='background:#e2e8f0; color:#334155; font-size:12px; font-weight:600; padding:2px 8px; border-radius:12px;'>📄 {cid}</span>"
                    for cid in o.cited_chunk_ids
                )
                evidence_html = f"""
                <div style='margin-top:8px; font-size:13px; color:#475569;'>
                    <strong>Source Evidence:</strong> {citation_pills}
                    <div style='margin-top:4px; font-style:italic; background:rgba(255,255,255,0.7); padding:6px 10px; border-radius:6px; border-left:3px solid {theme["border"]};'>
                        "{o.top_evidence_excerpt}"
                    </div>
                </div>
                """
            else:
                evidence_html = """
                <div style='margin-top:6px; font-size:12px; color:#dc2626; font-weight:500;'>
                    ⚠️ No supporting evidence found in retrieved chunks.
                </div>
                """

            card = f"""
            <div style='background:{theme["bg"]}; border-left:4px solid {theme["border"]}; border-radius:8px; padding:14px 18px; margin-bottom:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05);'>
                <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                    <div style='font-size:15px; font-weight:500; color:#1e293b; line-height:1.5; flex:1;'>
                        <span style='color:#64748b; font-size:13px; margin-right:6px;'>[{o.sentence_index + 1}]</span>
                        {o.sentence}
                    </div>
                    <div style='margin-left:16px; display:flex; align-items:center; gap:8px;'>
                        <span style='background:{theme["badge_bg"]}; color:{theme["text"]}; font-size:12px; font-weight:700; padding:3px 10px; border-radius:12px;'>
                            {theme["icon"]} {theme["label"].upper()}
                        </span>
                        <span style='font-size:13px; font-weight:600; color:#475569;'>
                            {o.grounding_score:.2f}
                        </span>
                    </div>
                </div>
                {evidence_html}
            </div>
            """
            cards_html.append(card)

        # Classification color
        overall_score_pct = int(result.overall_grounding_score * 100)
        class_color = "#16a34a" if result.overall_grounding_score >= 0.70 else ("#d97706" if result.overall_grounding_score >= 0.45 else "#dc2626")

        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
            margin: 0;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .header-card {{
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            margin-bottom: 24px;
            border: 1px solid #e2e8f0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-top: 16px;
        }}
        .stat-box {{
            background: #f1f5f9;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 20px;
            font-weight: 700;
            color: #0f172a;
        }}
        .stat-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div>
                    <h1 style="margin:0; font-size:22px; font-weight:700; color:#0f172a;">🛡️ VeritasRAG Grounding Report</h1>
                    <p style="margin:4px 0 0 0; color:#64748b; font-size:14px;">Real-time hallucination-flagging middleware verification</p>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:26px; font-weight:800; color:{class_color};">{overall_score_pct}%</span>
                    <div style="font-size:12px; font-weight:600; color:{class_color}; text-transform:uppercase;">
                        {result.overall_classification.replace('_', ' ')}
                    </div>
                </div>
            </div>

            <div style="margin-top:18px; padding:12px; background:#f8fafc; border-radius:8px; border-left:3px solid #3b82f6;">
                <strong style="font-size:13px; color:#475569;">User Query:</strong>
                <div style="font-size:14px; font-weight:500; color:#1e293b; margin-top:2px;">{result.query}</div>
            </div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value" style="color:#16a34a;">{grounded_count}</div>
                    <div class="stat-label">Grounded</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color:#d97706;">{inferred_count}</div>
                    <div class="stat-label">Inferred</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value" style="color:#dc2626;">{hallucinated_count}</div>
                    <div class="stat-label">Hallucinated</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{result.processing_time_ms:.0f}ms</div>
                    <div class="stat-label">Latency</div>
                </div>
            </div>
        </div>

        <h2 style="font-size:17px; font-weight:700; color:#334155; margin-bottom:14px;">
            Detailed Sentence-Level Grounding Breakdown ({total} sentences)
        </h2>

        {"".join(cards_html)}

        <div style="text-align:center; font-size:12px; color:#94a3b8; margin-top:30px;">
            Generated by VeritasRAG Middleware · Models: {", ".join(result.approaches_used) if result.approaches_used else "Ensemble"}
        </div>
    </div>
</body>
</html>"""
        return html_doc
