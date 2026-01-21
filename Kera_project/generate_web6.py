import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_DIR = r"C:\Users\sevco\Documents\diplomka\Keratoacanthoma_spatial_transcriptomics\analysis\01_fibroblast_Lacina\skripts_report3\Keratoacanthoma_app"

SECTIONS = {
    "01_PCA": "PCA",
    "02_Volcano": "Volcano Plots",
    "03_Heatmaps": "Heatmaps",
    "04_Boxplots": "Gene Expression plots",
}

COMMENTS = {
# 01_PCA
    "01_PCA_before_BC_all_genes": "Raw unsupervised clustering; shows initial variance and batch effects",
    "01_PCA_after_BC_all_genes": "Clustering after ComBat correction for Sentrix ID batch effects",
    "01_PCA_after_BC_top500_IQR": "Variance-driven clustering using the top 500 most variable genes (IQR)",
    "01_PCA_Samples_sub_DE_list": "Sample separation based exclusively on significantly deregulated genes",
    "01_PCA_Genes_sub_DE_list": "Gene 'Universe' plot; genes colored by the sample group where they peak",

# # 02_Volcano
#     "03_Volcano_SCC_vs_MatchedCtrl": "SCC Fibroblasts vs matched Dermal Fibroblast controls",
#     "03_Volcano_KAF_I_vs_MatchedCtrl": "Induced Kera Fibroblasts vs matched Dermal Fibroblast controls",
#     "03_Volcano_KAF_S_vs_MatchedCtrl": "Sporadic Kera Fibroblasts vs matched Dermal Fibroblast controls",
#     "03_Volcano_SCC_vs_KAF_All": "Direct comparison: SCC Fibroblasts vs all Keratoacanthoma Fibroblasts",
#     "03_Volcano_KAF_S_vs_KAF_I": "Comparison between Sporadic and Induced Keratoacanthoma populations",
#     "03_Volcano_SCC_Effect_vs_KAF_Effect": "Interaction analysis: Genes where the 'CAF-response' differs between SCC and KAF",

# # 03_Heatmaps
#     "04_Heatmap_SCC_vs_MatchedCtrl": "Z-score signature of top DE genes in SCC vs Matched Controls",
#     "04_Heatmap_KAF_I_vs_MatchedCtrl": "Z-score signature of top DE genes in Induced Kera vs Matched Controls",
#     "04_Heatmap_KAF_S_vs_MatchedCtrl": "Z-score signature of top DE genes in Sporadic Kera vs Matched Controls",
#     "04_Heatmap_SCC_vs_KAF_All": "Expression profile of genes differentiating SCC from Kera populations",
#     "04_Heatmap_SCC_Effect_vs_KAF_Effect": "Signature of genes showing distinct interaction effects between pathologies",
}

# ============================================================================
# SCAN DIRECTORIES
# ============================================================================
def scan_images(base_path):
    results = {}
    valid_extensions = ('.png', '.PNG', '.jpg', '.jpeg', '.svg')
    for section_key, section_name in SECTIONS.items():
        section_path = os.path.join(base_path, section_key)
        if not os.path.exists(section_path):
            results[section_key] = {"name": section_name, "files": []}
            continue
        files = [f for f in os.listdir(section_path) if f.endswith(valid_extensions)]
        files.sort()
        results[section_key] = {"name": section_name, "files": files}
    return results

def find_overview_images(base_path):
    pca_path = os.path.join(base_path, "01_PCA")
    overview = {"samples": "", "genes": ""}
    if os.path.exists(pca_path):
        for f in os.listdir(pca_path):
            if "01_PCA_Samples_sub_DE_list" in f and f.endswith(('.png', '.PNG')):
                overview["samples"] = "01_PCA/" + f
            elif "01_PCA_Genes_sub_DE_list" in f and f.endswith(('.png', '.PNG')):
                overview["genes"] = "01_PCA/" + f
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
        
        items_html = []
        if not v["files"]:
            items_html.append('<li class="item-row">No files</li>')
        else:
            for f in v["files"]:
                is_sig = "_sig" in f.lower()
                clean_name = f.replace("_sig.png","").replace(".png","").replace("_sig","")
                comment = COMMENTS.get(clean_name, "")
                sig_badge = '<span class="badge-sig">SIG</span>' if is_sig else ""
                
                # We use event.stopPropagation() so clicking the icon doesn't trigger the viewer
                row = """
                <li class="item-row" onclick="viewImage('%s/%s', '%s', this)">
                    <div class="item-top-row">
                        <span class="item-name">%s</span>
                        <div>
                            %s
                            <a href="%s/%s" target="_blank" class="new-tab-icon" title="Open in new tab" onclick="event.stopPropagation();">↗</a>
                        </div>
                    </div>
                    <div class="item-comment">%s</div>
                </li>""" % (k, f, clean_name, clean_name, sig_badge, k, f, comment)
                items_html.append(row)

        content_div = """
        <div id="%s" class="tab-content %s">
            <input type="text" class="search-input" placeholder="Search %s..." onkeyup="filterList(this, '%s-list')">
            <div class="items-list-container">
                <ul style="list-style:none" id="%s-list">
                    %s
                </ul>
            </div>
        </div>""" % (k, active_class, v["name"], k, k, "".join(items_html))
        tab_contents_list.append(content_div)
    
    final_tab_contents = "\n".join(tab_contents_list)

    # 3. PCA Overviews
    pca_samples_html = '<img src="%s" onclick="viewImage(\'%s\', \'Samples PCA\')">' % (overview["samples"], overview["samples"]) if overview["samples"] else '<p class="placeholder-text">N/A</p>'
    pca_genes_html = '<img src="%s" onclick="viewImage(\'%s\', \'Genes PCA\')">' % (overview["genes"], overview["genes"]) if overview["genes"] else '<p class="placeholder-text">N/A</p>'

    # 4. Final Assembly
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kera Project | Analysis Portal</title>
    <style>
        :root {{
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --primary: #1e293b;
            --accent: #3b82f6;
            --sig-bg: #f0fdf4;
            --sig-text: #166534;
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, sans-serif; background: var(--bg-color); color: var(--primary); }}
        .header {{ background: white; padding: 30px; border-bottom: 1px solid var(--border); text-align: center; }}
        h1 {{ font-size: 1.5rem; margin-bottom: 5px; }}
        .subtitle {{ color: #64748b; font-size: 0.9rem; }}
        .main-container {{ max-width: 1400px; margin: 0 auto; padding: 30px; }}
        
        /* Overview PCA section */
        .overview-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 40px; }}
        .card {{ background: white; border-radius: 8px; border: 1px solid var(--border); box-shadow: var(--shadow); overflow: hidden; }}
        .card-header {{ padding: 10px 15px; background: #f1f5f9; font-size: 0.75rem; font-weight: bold; color: #475569; text-transform: uppercase; }}
        .card-body {{ padding: 15px; text-align: center; }}
        .card-body img {{ max-width: 100%; height: auto; border-radius: 4px; cursor: pointer; }}

        .explorer-layout {{ display: grid; grid-template-columns: 420px 1fr; gap: 30px; align-items: start; }}
        
        /* List column */
        .list-column {{ position: sticky; top: 20px; height: calc(100vh - 100px); display: flex; flex-direction: column; }}
        .tabs-nav {{ display: flex; gap: 5px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px; }}
        .tab-btn {{ padding: 6px 12px; background: #e2e8f0; border: none; border-radius: 15px; font-size: 0.8rem; cursor: pointer; white-space: nowrap; }}
        .tab-btn.active {{ background: var(--accent); color: white; }}
        .search-input {{ width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 15px; }}
        .items-list-container {{ flex-grow: 1; overflow-y: auto; background: white; border: 1px solid var(--border); border-radius: 8px; }}
        
        /* Row items */
        .item-row {{ padding: 12px 15px; border-bottom: 1px solid #f1f5f9; display: flex; flex-direction: column; cursor: pointer; }}
        .item-row:hover {{ background: #f8fafc; }}
        .item-row.selected {{ background: #eff6ff; border-left: 4px solid var(--accent); }}
        .item-top-row {{ display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 4px; }}
        .item-name {{ font-family: monospace; font-weight: bold; color: var(--accent); font-size: 0.95rem; }}
        .item-comment {{ font-size: 0.75rem; color: #94a3b8; font-style: italic; }}
        
        .new-tab-icon {{ text-decoration: none; color: #cbd5e1; font-weight: bold; margin-left: 8px; font-size: 1rem; transition: color 0.2s; }}
        .new-tab-icon:hover {{ color: var(--accent); }}

        /* Viewer window */
        .viewer-column {{ position: sticky; top: 20px; background: white; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow); padding: 20px; text-align: center; min-height: 600px; display: flex; flex-direction: column; }}
        .viewer-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px solid #f1f5f9; }}
        #viewerTitle {{ font-size: 1.1rem; font-weight: bold; color: var(--primary); }}
        .open-full-btn {{ font-size: 0.75rem; color: var(--accent); text-decoration: none; border: 1px solid var(--accent); padding: 4px 10px; border-radius: 5px; font-weight: 500; }}
        .open-full-btn:hover {{ background: var(--accent); color: white; }}
        
        .viewer-body {{ flex-grow: 1; display: flex; align-items: center; justify-content: center; }}
        #mainViewerImg {{ max-width: 100%; max-height: 75vh; object-fit: contain; border-radius: 4px; display: none; }}
        .placeholder-text {{ color: #94a3b8; font-style: italic; }}
        
        .badge-sig {{ font-size: 0.6rem; background: var(--sig-bg); color: var(--sig-text); padding: 2px 6px; border-radius: 4px; font-weight: bold; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
<header class="header">
    <h1>Keratoacanthoma Project</h1>
    <p class="subtitle">Cancer associated fibroblast | Analysis</p>
</header>
<main class="main-container">
    <div class="overview-grid">
        <div class="card">
            <div class="card-header">PCA: Samples</div>
            <div class="card-body">{pca_samples_html}</div>
        </div>
        <div class="card">
            <div class="card-header">PCA: Top Genes</div>
            <div class="card-body">{pca_genes_html}</div>
        </div>
    </div>
    <div class="explorer-layout">
        <div class="list-column">
            <nav class="tabs-nav">{final_tab_btns}</nav>
            {final_tab_contents}
        </div>
        <div class="viewer-column" id="viewerContainer">
            <div id="viewerHeader" class="viewer-header" style="display:none">
                <span id="viewerTitle"></span>
                <a id="fullImageLink" href="#" target="_blank" class="open-full-btn">Open Full Image ↗</a>
            </div>
            <div class="viewer-body">
                <p id="placeholder" class="placeholder-text">Select an item from the list to visualize</p>
                <img id="mainViewerImg" src="" alt="Plot Viewer">
            </div>
        </div>
    </div>
</main>
<script>
    function openTab(evt, tabId) {{
        var contents = document.getElementsByClassName("tab-content");
        for (var i = 0; i < contents.length; i++) contents[i].classList.remove("active");
        var buttons = document.getElementsByClassName("tab-btn");
        for (var i = 0; i < buttons.length; i++) buttons[i].classList.remove("active");
        document.getElementById(tabId).classList.add("active");
        evt.currentTarget.classList.add("active");
    }}
    function filterList(input, listId) {{
        var filter = input.value.toUpperCase();
        var rows = document.getElementById(listId).getElementsByClassName("item-row");
        for (var i = 0; i < rows.length; i++) {{
            var name = rows[i].querySelector(".item-name").innerText;
            var comment = rows[i].querySelector(".item-comment").innerText;
            var combined = (name + " " + comment).toUpperCase();
            rows[i].style.display = combined.indexOf(filter) > -1 ? "" : "none";
        }}
    }}
    function viewImage(src, title, element) {{
        document.getElementById("placeholder").style.display = "none";
        document.getElementById("viewerHeader").style.display = "flex";
        document.getElementById("viewerTitle").innerText = title;
        document.getElementById("fullImageLink").href = src;
        
        const img = document.getElementById("mainViewerImg");
        img.src = src;
        img.style.display = "inline-block";
        
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
    overview = find_overview_images(BASE_DIR)
    html_content = generate_html(data, overview)
    output_path = os.path.join(BASE_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success! Portal with multi-view options generated.")