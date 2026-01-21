import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_DIR = r"C:\Users\sevco\Documents\diplomka\Keratoacanthoma_spatial_transcriptomics\analysis\01_fibroblast_Lacina\skripts_report3\Keratoacanthoma_app"

SECTIONS = {
    "01_PCA": "PCA Analysis",
    "02_Volcano": "Volcano Plots",
    "03_Heatmaps": "Expression Patterns",
    "04_Boxplots": "Gene Expression Plots"
}

# Values from your decideTests(fit2) output
SUMMARY_STATS = {
    "SCC_vs_MatchedCtrl": [125, 34],
    "KAF_I_vs_MatchedCtrl": [13, 26],
    "KAF_S_vs_MatchedCtrl": [36, 39],
    "SCC_vs_KAF_All": [42, 39],
    "KAF_S_vs_KAF_I": [171, 250],
    "SCC_vs_KAF_I": [193, 231],
    "SCC_vs_KAF_S": [48, 26],
    "SCC_Effect_vs_KAF_Effect": [97, 39],
    "SCC_Effect_vs_KAF_I_Effect": [72, 39],
    "SCC_Effect_vs_KAF_S_Effect": [84, 36],
    "DF_SCC_vs_DF_KAF_I": [379, 507],
    "DF_SCC_vs_DF_KAF_S": [105, 143],
    "DF_KAF_S_vs_DF_KAF_I": [347, 495]
}

COMMENTS = {
    "01_UMAP_Samples_sub_DE_list": "UMAP projection of samples based on DE genes",
    "01_PCA_before_BC_all_genes": "Initial variance before batch correction",
    "01_PCA_after_BC_all_genes": "Variance after ComBat correction",
    "01_PCA_after_BC_top500_IQR": "Top 500 variable genes PCA",
}

# ============================================================================
# SCAN DIRECTORIES
# ============================================================================
def scan_images(base_path):
    results = {}
    valid_extensions = ('.png', '.PNG', '.jpg', '.jpeg', '.svg', '.html')
    for section_key, section_name in SECTIONS.items():
        section_path = os.path.join(base_path, section_key)
        if not os.path.exists(section_path):
            results[section_key] = {"name": section_name, "files": []}
            continue
        # Sort files, putting .html first in lists if applicable
        files = [f for f in os.listdir(section_path) if f.endswith(valid_extensions)]
        files.sort()
        results[section_key] = {"name": section_name, "files": files}
    return results

def find_overview_files(base_path):
    """Modified to find the new UMAP files"""
    pca_path = os.path.join(base_path, "01_PCA")
    overview = {"umap_static": "", "umap_interactive": ""}
    if os.path.exists(pca_path):
        for f in os.listdir(pca_path):
            if "01_UMAP_Samples_sub_DE_list.png" in f:
                overview["umap_static"] = "01_PCA/" + f
            elif "02_UMAP_Genes_sub_DE_list_interactive.html" in f:
                overview["umap_interactive"] = "01_PCA/" + f
    return overview

# ============================================================================
# HTML GENERATION
# ============================================================================
def generate_html(data, overview):
    # 1. Build Tab Buttons
    tab_btns_list = []
    for i, (k, v) in enumerate(data.items()):
        active_class = "active" if i == 0 else ""
        btn = '<button class="tab-btn %s" onclick="openTab(event, \'%s\')">%s</button>' % (active_class, k, v["name"])
        tab_btns_list.append(btn)
    final_tab_btns = "\n".join(tab_btns_list)

    # 2. Build Tab Contents
    tab_contents_list = []
    for i, (k, v) in enumerate(data.items()):
        active_class = "active" if i == 0 else ""
        
        stats_table = ""
        if k == "02_Volcano":
            rows = []
            for name, vals in SUMMARY_STATS.items():
                rows.append('<tr><td>%s</td><td class="stat-down">%d</td><td class="stat-up">%d</td><td>%d</td></tr>' % (name, vals[0], vals[1], vals[0]+vals[1]))
            stats_table = '<div class="stats-summary-container"><table class="stats-table"><thead><tr><th>Comparison</th><th>DN</th><th>UP</th><th>Total</th></tr></thead><tbody>%s</tbody></table></div>' % "".join(rows)

        items_html = []
        for f in v["files"]:
            clean_name = f.replace("03_Volcano_", "").replace("04_Heatmap_", "").replace("_sig.png","").replace(".png","").replace(".html","").replace("_sig","")
            comment = COMMENTS.get(clean_name, "")
            
            row_stat = ""
            if k == "02_Volcano" and clean_name in SUMMARY_STATS:
                s = SUMMARY_STATS[clean_name]
                row_stat = '<span class="row-stat-badge">DN:%d | UP:%d</span>' % (s[0], s[1])

            sig_badge = '<span class="badge-sig">SIG</span>' if "_sig" in f.lower() else ""
            
            row = """
            <li class="item-row" onclick="viewItem('%s/%s', '%s', this)">
                <div class="item-top-row">
                    <span class="item-name">%s</span>
                    <div>
                        %s %s
                        <a href="%s/%s" target="_blank" class="new-tab-icon" onclick="event.stopPropagation();">↗</a>
                    </div>
                </div>
                <div class="item-comment">%s</div>
            </li>""" % (k, f, clean_name, clean_name, row_stat, sig_badge, k, f, comment)
            items_html.append(row)

        display_style = "flex" if i == 0 else "none"
        tab_contents_list.append("""
        <div id="%s" class="tab-content %s" style="height: 100%%; display: %s; flex-direction: column;">
            %s
            <input type="text" class="search-input" placeholder="Search %s..." onkeyup="filterList(this, '%s-list')">
            <div class="items-list-container"><ul style="list-style:none" id="%s-list">%s</ul></div>
        </div>""" % (k, active_class, display_style, stats_table, v["name"], k, k, "".join(items_html)))
    
    final_tab_contents = "\n".join(tab_contents_list)

    # Overview Logic for UMAP
    umap_static_html = '<img src="%s" onclick="viewItem(\'%s\', \'UMAP: Samples\')">' % (overview["umap_static"], overview["umap_static"]) if overview["umap_static"] else '<p class="placeholder-text">Static UMAP N/A</p>'
    umap_inter_html = '<iframe src="%s" style="width:100%%; height:350px; border:none; border-radius:4px;"></iframe>' % (overview["umap_interactive"]) if overview["umap_interactive"] else '<p class="placeholder-text">Interactive UMAP N/A</p>'

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kera Project | Analysis Portal</title>
    <style>
        :root {{
            --bg-color: #f8fafc; --card-bg: #ffffff; --primary: #1e293b; --accent: #3b82f6;
            --sig-bg: #f0fdf4; --sig-text: #166534; --border: #e2e8f0; --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: var(--bg-color); color: var(--primary); overflow-x: hidden; }}
        .header {{ background: white; padding: 30px; border-bottom: 1px solid var(--border); text-align: center; }}
        .main-container {{ max-width: 1500px; margin: 0 auto; padding: 30px; }}
        
        /* Overview Dashboard Sizing */
        .overview-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }}
        .card {{ background: white; border-radius: 8px; border: 1px solid var(--border); box-shadow: var(--shadow); overflow: hidden; }}
        .card-header {{ padding: 10px 15px; background: #f1f5f9; font-size: 0.75rem; font-weight: bold; color: #475569; text-transform: uppercase; }}
        .card-body {{ padding: 15px; text-align: center; min-height: 380px; display: flex; align-items: center; justify-content: center; }}
        .card-body img {{ max-width: 100%; max-height: 350px; cursor: pointer; border-radius: 4px; }}

        .explorer-layout {{ display: grid; grid-template-columns: 420px 1fr; gap: 30px; height: 900px; align-items: stretch; }}
        .list-column {{ height: 100%; display: flex; flex-direction: column; overflow: hidden; }}
        .tabs-nav {{ display: flex; gap: 5px; margin-bottom: 15px; flex-shrink: 0; }}
        .tab-btn {{ padding: 6px 12px; background: #e2e8f0; border: none; border-radius: 15px; font-size: 0.8rem; cursor: pointer; }}
        .tab-btn.active {{ background: var(--accent); color: white; }}
        .search-input {{ width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 15px; flex-shrink: 0; }}
        
        .stats-summary-container {{ margin-bottom: 15px; background: white; border: 1px solid var(--border); border-radius: 8px; padding: 10px; flex-shrink: 0; }}
        .stats-table {{ width: 100%; border-collapse: collapse; font-size: 0.7rem; }}
        .stats-table th {{ border-bottom: 2px solid var(--border); padding: 4px; text-align: left; color: #64748b; }}
        .stats-table td {{ border-bottom: 1px solid #f1f5f9; padding: 4px; }}
        .stat-down {{ color: #ef4444; font-weight: bold; }}
        .stat-up {{ color: #22c55e; font-weight: bold; }}

        .items-list-container {{ flex-grow: 1; overflow-y: auto; background: white; border: 1px solid var(--border); border-radius: 8px; }}
        .item-row {{ padding: 12px 15px; border-bottom: 1px solid #f1f5f9; display: flex; flex-direction: column; cursor: pointer; }}
        .item-row.selected {{ background: #eff6ff; border-left: 4px solid var(--accent); }}
        .item-name {{ font-family: monospace; font-weight: bold; color: var(--accent); font-size: 0.95rem; }}
        .item-comment {{ font-size: 0.75rem; color: #94a3b8; font-style: italic; }}

        .viewer-column {{ height: 100%; background: white; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow); padding: 20px; display: flex; flex-direction: column; overflow: hidden; }}
        .viewer-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #f1f5f9; padding-bottom: 10px; flex-shrink: 0; }}
        .viewer-body {{ flex-grow: 1; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #fff; }}
        #mainViewerImg {{ max-width: 100%; max-height: 100%; object-fit: contain; display: none; }}
        #mainViewerFrame {{ width: 100%; height: 100%; border: none; display: none; }}
        
        .badge-sig {{ font-size: 0.6rem; background: var(--sig-bg); color: var(--sig-text); padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
        .new-tab-icon {{ text-decoration: none; color: #cbd5e1; margin-left: 8px; font-size: 1rem; }}
        .tab-content {{ display: none; }}
        .placeholder-text {{ color: #94a3b8; font-style: italic; }}
    </style>
</head>
<body>
<header class="header">
    <h1>Keratoacanthoma Spatial Transcriptomics</h1>
    <p class="subtitle">Fibroblast Population Analysis Portfolio</p>
</header>
<main class="main-container">
    <div class="overview-grid">
        <div class="card">
            <div class="card-header">UMAP: Samples</div>
            <div class="card-body">{umap_static_html}</div>
        </div>
        <div class="card">
            <div class="card-header">UMAP: Genes (Interactive)</div>
            <div class="card-body">{umap_inter_html}</div>
        </div>
    </div>
    <div class="explorer-layout">
        <div class="list-column">
            <nav class="tabs-nav">{final_tab_btns}</nav>
            {final_tab_contents}
        </div>
        <div class="viewer-column" id="viewerContainer">
            <div id="viewerHeader" class="viewer-header" style="display:none">
                <span id="viewerTitle" style="font-weight:bold;"></span>
                <a id="fullImageLink" href="#" target="_blank" style="font-size:0.75rem; color:var(--accent); text-decoration:none; border:1px solid var(--accent); padding:4px 10px; border-radius:5px;">Open Original ↗</a>
            </div>
            <div class="viewer-body">
                <p id="placeholder" class="placeholder-text">Select a plot to visualize</p>
                <img id="mainViewerImg" src="" alt="Viewer">
                <iframe id="mainViewerFrame" src=""></iframe>
            </div>
        </div>
    </div>
</main>
<script>
    function openTab(evt, tabId) {{
        var contents = document.getElementsByClassName("tab-content");
        for (var i = 0; i < contents.length; i++) {{
            contents[i].style.display = "none";
            contents[i].classList.remove("active");
        }}
        var buttons = document.getElementsByClassName("tab-btn");
        for (var i = 0; i < buttons.length; i++) buttons[i].classList.remove("active");
        
        var target = document.getElementById(tabId);
        target.style.display = "flex";
        target.classList.add("active");
        evt.currentTarget.classList.add("active");
    }}
    function filterList(input, listId) {{
        var filter = input.value.toUpperCase();
        var rows = document.getElementById(listId).getElementsByClassName("item-row");
        for (var i = 0; i < rows.length; i++) {{
            var name = rows[i].querySelector(".item-name").innerText;
            var comment = rows[i].querySelector(".item-comment").innerText;
            rows[i].style.display = (name + " " + comment).toUpperCase().indexOf(filter) > -1 ? "" : "none";
        }}
    }}
    function viewItem(src, title, element) {{
        document.getElementById("placeholder").style.display = "none";
        document.getElementById("viewerHeader").style.display = "flex";
        document.getElementById("viewerTitle").innerText = title;
        document.getElementById("fullImageLink").href = src;
        
        const img = document.getElementById("mainViewerImg");
        const frame = document.getElementById("mainViewerFrame");
        
        if (src.endsWith(".html")) {{
            img.style.display = "none";
            frame.src = src;
            frame.style.display = "block";
        }} else {{
            frame.style.display = "none";
            img.src = src;
            img.style.display = "block";
        }}
        
        var rows = document.getElementsByClassName("item-row");
        for (var i = 0; i < rows.length; i++) rows[i].classList.remove("selected");
        if(element) element.classList.add("selected");
    }}
</script>
</body>
</html>"""
    return html_template

if __name__ == "__main__":
    data = scan_images(BASE_DIR)
    overview = find_overview_files(BASE_DIR)
    html_content = generate_html(data, overview)
    output_path = os.path.join(BASE_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success! Portal with UMAP dashboard generated.")