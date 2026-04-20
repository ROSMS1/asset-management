import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import date, datetime
import os

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Asset Management – MTN Congo",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = os.path.join(os.path.dirname(__file__), "asset_management.db")

# ─── CONSTANTES (modèle Asset Database) ──────────────────────────────────────
REGIONS       = ["SOUTH", "PNR", "BRAZZAVILLE_POOL", "NORTH_CENTRE", "NORTH"]
NETWORK_TYPES = ["ZTE", "HUAWEI", "ERICSSON", "NOKIA", "MTN"]
STATUSES      = ["OK", "NOK", "Faulty", "Missing", "Under Repair"]
ITEM_NAMES    = [
    "A/C", "ACDB", "ATS", "Generator 1", "Generator 2",
    "Rectifier", "Solar", "Battery", "Transmission", "Other"
]
ITEM_DESCRIPTIONS = [
    "A/C cooling", "ACDB Types", "ATS", "Battery charger alternator",
    "DG alternator", "DG battery", "DG controller board", "DG regulator card",
    "Engine", "Generator", "Generator/Alternator Type", "Injection pump",
    "Radiator pump", "Backup Batteries Count", "Number of Controller",
    "Number of module", "Rectifier", "Controller solar", "Solar Panel", "Other"
]
OEM_VENDORS = [
    "GREENPOLE", "DEEP SEA", "STAMFORD", "MARIBAT", "PERKINS",
    "LEROY SOMER", "SACRED SUN", "SHOTO", "EPROTECH", "ZTE",
    "HUAWEI", "Other"
]
MOVEMENT_TYPES   = ["Site → Site", "Site → Warehouse", "Warehouse → Site", "Site → Repair", "Repair → Site"]
MOVEMENT_STATUSES = ["En Transit", "Livré", "Confirmé", "Annulé"]

# ─── DATABASE ─────────────────────────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS assets (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        site_id          TEXT NOT NULL,
        site_name        TEXT NOT NULL,
        region           TEXT,
        serial_number    TEXT,
        part_number      TEXT,
        item_description TEXT,
        oem_vendor       TEXT,
        item_name        TEXT,
        network_type     TEXT,
        status           TEXT DEFAULT 'OK',
        install_date     TEXT,
        comments         TEXT,
        created_at       TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS spare_movements (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        movement_date   TEXT NOT NULL,
        movement_type   TEXT,
        item_description TEXT,
        serial_number   TEXT,
        part_number     TEXT,
        oem_vendor      TEXT,
        qty             INTEGER DEFAULT 1,
        from_site_id    TEXT,
        from_site_name  TEXT,
        to_site_id      TEXT,
        to_site_name    TEXT,
        reason          TEXT,
        technician      TEXT,
        status          TEXT DEFAULT 'En Transit',
        reception_date  TEXT,
        comments        TEXT,
        created_at      TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def load_assets():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM assets ORDER BY id DESC", conn)
    conn.close()
    return df

def load_movements():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM spare_movements ORDER BY movement_date DESC", conn)
    conn.close()
    return df

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: #1a1a2e !important; }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
.metric-card {
    border-radius: 10px; padding: 16px 20px;
    text-align: center; color: white; margin-bottom: 8px;
}
.metric-card .val { font-size: 2rem; font-weight: 800; }
.metric-card .lbl { font-size: 0.82rem; opacity: 0.85; margin-top: 2px; }
.sec-title {
    font-size: 1.1rem; font-weight: 700; color: #0f3460;
    border-bottom: 2px solid #e94560;
    padding-bottom: 3px; margin: 14px 0 10px 0;
}
.move-card {
    border-radius: 8px; padding: 12px 16px;
    margin: 6px 0; font-size: 0.88rem;
    border-left: 4px solid #0f3460;
    background: #f0f4ff;
}
.move-card.transit  { border-color: #dd6b20; background: #fef3e2; }
.move-card.livre    { border-color: #38a169; background: #f0fff4; }
.move-card.confirme { border-color: #0f3460; background: #ebf4ff; }
.move-card.annule   { border-color: #e53e3e; background: #fff5f5; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏗️ Asset Management")
    st.markdown("**MTN Congo – South Region**")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🏠 Dashboard",
        "➕ Nouvel Asset",
        "📋 Base de Données Assets",
        "🔄 Mouvement Spare Parts",
        "➕ Nouveau Mouvement",
        "📊 Rapports",
    ])
    st.markdown("---")
    st.markdown(f"📅 **{date.today().strftime('%d/%m/%Y')}**")

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.title("📊 Dashboard – Asset Management")
    df  = load_assets()
    mdf = load_movements()

    total_assets = len(df)
    ok_assets    = len(df[df["status"] == "OK"]) if total_assets else 0
    nok_assets   = len(df[df["status"].isin(["NOK","Faulty"])]) if total_assets else 0
    total_moves  = len(mdf)
    in_transit   = len(mdf[mdf["status"] == "En Transit"]) if total_moves else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, lbl, bg in [
        (c1, total_assets, "Total Assets",      "#0f3460"),
        (c2, ok_assets,    "✅ Status OK",       "#38a169"),
        (c3, nok_assets,   "⚠️ NOK / Faulty",   "#e53e3e"),
        (c4, total_moves,  "🔄 Mouvements",      "#6b46c1"),
        (c5, in_transit,   "🚚 En Transit",      "#dd6b20"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card" style="background:{bg}"><div class="val">{val}</div><div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    if total_assets == 0 and total_moves == 0:
        st.info("Aucun asset enregistré. Commencez par **➕ Nouvel Asset**.")
    else:
        st.markdown("---")
        col_a, col_b = st.columns(2)

        if total_assets > 0:
            with col_a:
                st.markdown('<div class="sec-title">Assets par Item Name</div>', unsafe_allow_html=True)
                item_df = df["item_name"].value_counts().reset_index()
                item_df.columns = ["Item", "Nombre"]
                fig1 = px.bar(item_df, x="Item", y="Nombre",
                              color_discrete_sequence=["#0f3460"])
                fig1.update_layout(margin=dict(t=10,b=10), height=280, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig1, use_container_width=True)

            with col_b:
                st.markdown('<div class="sec-title">Assets par Région</div>', unsafe_allow_html=True)
                reg_df = df.groupby(["region","status"]).size().reset_index(name="n")
                fig2 = px.bar(reg_df, x="region", y="n", color="status", barmode="stack",
                              color_discrete_map={"OK":"#38a169","NOK":"#e53e3e",
                                                  "Faulty":"#dd6b20","Missing":"#c53030",
                                                  "Under Repair":"#d69e2e"})
                fig2.update_layout(margin=dict(t=10,b=10), height=280, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig2, use_container_width=True)

        if total_moves > 0:
            col_c, col_d = st.columns(2)
            with col_c:
                st.markdown('<div class="sec-title">Mouvements par Statut</div>', unsafe_allow_html=True)
                mv_df = mdf["status"].value_counts().reset_index()
                mv_df.columns = ["Statut","Nombre"]
                fig3 = px.pie(mv_df, names="Statut", values="Nombre", hole=0.4,
                              color_discrete_map={"En Transit":"#dd6b20","Livré":"#38a169",
                                                  "Confirmé":"#0f3460","Annulé":"#e53e3e"})
                fig3.update_layout(margin=dict(t=10,b=10), height=270)
                st.plotly_chart(fig3, use_container_width=True)

            with col_d:
                st.markdown('<div class="sec-title">Mouvements par Type</div>', unsafe_allow_html=True)
                mt_df = mdf["movement_type"].value_counts().reset_index()
                mt_df.columns = ["Type","Nombre"]
                fig4 = px.bar(mt_df, x="Type", y="Nombre",
                              color_discrete_sequence=["#6b46c1"])
                fig4.update_layout(margin=dict(t=10,b=10), height=270, xaxis_title="", yaxis_title="")
                st.plotly_chart(fig4, use_container_width=True)

        # Derniers mouvements
        if total_moves > 0:
            st.markdown('<div class="sec-title">5 Derniers Mouvements</div>', unsafe_allow_html=True)
            cols_mv = ["movement_date","movement_type","item_description",
                       "from_site_name","to_site_name","qty","status","technician"]
            st.dataframe(mdf[cols_mv].head(5).rename(columns={
                "movement_date":"Date","movement_type":"Type",
                "item_description":"Article","from_site_name":"De",
                "to_site_name":"Vers","qty":"Qté",
                "status":"Statut","technician":"Technicien"
            }), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# NOUVEL ASSET
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Nouvel Asset":
    st.title("➕ Enregistrer un Nouvel Asset")
    st.caption("Modèle fidèle à la feuille **Asset Database** du fichier Excel")
    st.markdown("---")

    with st.form("form_asset", clear_on_submit=True):
        st.markdown('<div class="sec-title">🏗️ Informations du Site</div>', unsafe_allow_html=True)
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1: site_id   = st.text_input("Site ID *", placeholder="ex: 4126")
        with r1c2: site_name = st.text_input("Site Name *", placeholder="ex: AQUARIUM")
        with r1c3: region    = st.selectbox("Région", REGIONS)

        st.markdown('<div class="sec-title">🔧 Informations de l\'Asset</div>', unsafe_allow_html=True)
        r2c1, r2c2 = st.columns(2)
        with r2c1: serial_number = st.text_input("Serial Number", placeholder="ex: G2K20LP0482")
        with r2c2: part_number   = st.text_input("Part Number",   placeholder="ex: ZTE-001")

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            item_desc_choice = st.selectbox("Item Description", ITEM_DESCRIPTIONS)
            if item_desc_choice == "Other":
                item_desc_choice = st.text_input("Précisez l'Item Description")
        with r3c2:
            item_name_choice = st.selectbox("Item Name (Catégorie)", ITEM_NAMES)

        r4c1, r4c2, r4c3 = st.columns(3)
        with r4c1:
            oem_vendor_choice = st.selectbox("OEM Vendor", OEM_VENDORS)
            if oem_vendor_choice == "Other":
                oem_vendor_choice = st.text_input("Précisez le Vendor")
        with r4c2: network_type  = st.selectbox("Network Type", NETWORK_TYPES)
        with r4c3: status        = st.selectbox("Status", STATUSES)

        install_date = st.date_input("Install Date", value=date.today())
        comments     = st.text_area("Comments", height=70)

        if st.form_submit_button("💾 Enregistrer l'Asset", type="primary", use_container_width=True):
            if not site_id.strip() or not site_name.strip():
                st.error("⚠️ Site ID et Site Name sont obligatoires.")
            else:
                conn = get_conn()
                conn.execute("""
                    INSERT INTO assets
                    (site_id, site_name, region, serial_number, part_number,
                     item_description, oem_vendor, item_name, network_type,
                     status, install_date, comments, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (site_id.strip(), site_name.strip(), region, serial_number,
                      part_number, item_desc_choice, oem_vendor_choice,
                      item_name_choice, network_type, status,
                      install_date.isoformat(), comments, now_str()))
                conn.commit(); conn.close()
                st.success("✅ Asset enregistré avec succès !")
                st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# BASE DE DONNÉES ASSETS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Base de Données Assets":
    st.title("📋 Base de Données Assets")
    df = load_assets()

    if df.empty:
        st.info("Aucun asset enregistré.")
    else:
        st.markdown("### 🔍 Filtres")
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1: f_region = st.multiselect("Région",       REGIONS)
        with fc2: f_status = st.multiselect("Statut",       STATUSES)
        with fc3: f_item   = st.multiselect("Item Name",    ITEM_NAMES)
        with fc4: f_vendor = st.multiselect("OEM Vendor",   OEM_VENDORS)

        mask = pd.Series([True]*len(df))
        if f_region: mask &= df["region"].isin(f_region)
        if f_status: mask &= df["status"].isin(f_status)
        if f_item:   mask &= df["item_name"].isin(f_item)
        if f_vendor: mask &= df["oem_vendor"].isin(f_vendor)
        filtered = df[mask]

        st.markdown(f"**{len(filtered)} asset(s) trouvé(s)**")
        st.dataframe(filtered[[
            "id","site_id","site_name","region","serial_number","part_number",
            "item_description","oem_vendor","item_name","network_type",
            "status","install_date","comments"
        ]].rename(columns={
            "id":"SN","site_id":"Site ID","site_name":"Site Name",
            "region":"Region","serial_number":"Serial Number",
            "part_number":"Part Number","item_description":"Item Description",
            "oem_vendor":"OEM Vendor","item_name":"Item Name",
            "network_type":"Network Type","status":"Status",
            "install_date":"Install Date","comments":"Comments"
        }), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("### ✏️ Mettre à jour un Asset")
        id_list = filtered["id"].tolist()
        if id_list:
            sel = st.selectbox("Sélectionner l'Asset (SN)",
                id_list,
                format_func=lambda x: f"#{x} – {df[df['id']==x]['site_name'].values[0]} – {df[df['id']==x]['item_description'].values[0]}")
            row = df[df["id"]==sel].iloc[0]
            with st.form(f"edit_asset_{sel}"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    idx = STATUSES.index(row["status"]) if row["status"] in STATUSES else 0
                    new_status = st.selectbox("Status", STATUSES, index=idx)
                with ec2: new_serial = st.text_input("Serial Number", value=row["serial_number"] or "")
                with ec3: new_part   = st.text_input("Part Number",   value=row["part_number"] or "")
                new_comments = st.text_area("Comments", value=row["comments"] or "")
                if st.form_submit_button("💾 Sauvegarder", type="primary"):
                    conn = get_conn()
                    conn.execute("""
                        UPDATE assets SET status=?, serial_number=?,
                        part_number=?, comments=? WHERE id=?
                    """, (new_status, new_serial, new_part, new_comments, sel))
                    conn.commit(); conn.close()
                    st.success("✅ Asset mis à jour !"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# MOUVEMENT SPARE PARTS — LISTE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Mouvement Spare Parts":
    st.title("🔄 Mouvements des Spare Parts")
    mdf = load_movements()

    if mdf.empty:
        st.info("Aucun mouvement enregistré. Cliquez sur **➕ Nouveau Mouvement**.")
    else:
        st.markdown("### 🔍 Filtres")
        mc1, mc2, mc3 = st.columns(3)
        with mc1: f_mtype  = st.multiselect("Type de Mouvement", MOVEMENT_TYPES)
        with mc2: f_mst    = st.multiselect("Statut",            MOVEMENT_STATUSES)
        with mc3: f_mitem  = st.text_input("Rechercher un Article", placeholder="ex: DG battery")

        mmask = pd.Series([True]*len(mdf))
        if f_mtype: mmask &= mdf["movement_type"].isin(f_mtype)
        if f_mst:   mmask &= mdf["status"].isin(f_mst)
        if f_mitem: mmask &= mdf["item_description"].str.contains(f_mitem, case=False, na=False)
        filtered_m = mdf[mmask]

        st.markdown(f"**{len(filtered_m)} mouvement(s)**")

        # Affichage en cartes visuelles
        for _, r in filtered_m.iterrows():
            css = {"En Transit":"transit","Livré":"livre",
                   "Confirmé":"confirme","Annulé":"annule"}.get(r["status"], "")
            icon_mv = {"Site → Site":"🔀","Site → Warehouse":"🏭",
                       "Warehouse → Site":"📦","Site → Repair":"🔧",
                       "Repair → Site":"✅"}.get(r["movement_type"], "🔄")
            st.markdown(f"""
            <div class="move-card {css}">
                {icon_mv} <b>{r['movement_type']}</b>
                &nbsp;|&nbsp; 📅 {str(r['movement_date'])[:10]}
                &nbsp;|&nbsp; Statut : <b>{r['status']}</b><br/>
                🔩 <b>{r['item_description']}</b>
                &nbsp;|&nbsp; S/N : {r['serial_number'] or '—'}
                &nbsp;|&nbsp; Qté : {r['qty']}<br/>
                📍 <b>De :</b> {r['from_site_name']} ({r['from_site_id']})
                &nbsp;→&nbsp;
                <b>Vers :</b> {r['to_site_name']} ({r['to_site_id']})<br/>
                👤 Technicien : {r['technician'] or '—'}
                &nbsp;|&nbsp; Raison : {r['reason'] or '—'}
                {f"<br/>📬 Réception : {str(r['reception_date'])[:10]}" if r['reception_date'] else ""}
                {f"<br/>💬 {r['comments']}" if r['comments'] else ""}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ✏️ Mettre à jour le statut d'un mouvement")
        mid_list = filtered_m["id"].tolist()
        if mid_list:
            sel_m = st.selectbox("Sélectionner le Mouvement",
                mid_list,
                format_func=lambda x: f"#{x} – {mdf[mdf['id']==x]['item_description'].values[0]} – {mdf[mdf['id']==x]['from_site_name'].values[0]} → {mdf[mdf['id']==x]['to_site_name'].values[0]}")
            mrow = mdf[mdf["id"]==sel_m].iloc[0]
            with st.form(f"upd_mv_{sel_m}"):
                uc1, uc2 = st.columns(2)
                with uc1:
                    idx_ms = MOVEMENT_STATUSES.index(mrow["status"]) if mrow["status"] in MOVEMENT_STATUSES else 0
                    new_mst = st.selectbox("Nouveau Statut", MOVEMENT_STATUSES, index=idx_ms)
                with uc2:
                    new_recep = st.date_input("Date de Réception", value=date.today())
                new_mcomments = st.text_area("Commentaires", value=mrow["comments"] or "")
                if st.form_submit_button("💾 Mettre à Jour", type="primary"):
                    conn = get_conn()
                    conn.execute("""
                        UPDATE spare_movements SET status=?, reception_date=?, comments=?
                        WHERE id=?
                    """, (new_mst,
                          new_recep.isoformat() if new_mst in ["Livré","Confirmé"] else mrow["reception_date"],
                          new_mcomments, sel_m))
                    conn.commit(); conn.close()
                    st.success("✅ Mouvement mis à jour !"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# NOUVEAU MOUVEMENT SPARE PART
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Nouveau Mouvement":
    st.title("➕ Enregistrer un Mouvement de Spare Part")
    st.caption("Traçabilité complète des déplacements de matériels entre sites")
    st.markdown("---")

    assets_df = load_assets()

    with st.form("form_movement", clear_on_submit=True):
        st.markdown('<div class="sec-title">📅 Informations du Mouvement</div>', unsafe_allow_html=True)
        nm1, nm2 = st.columns(2)
        with nm1: mv_date = st.date_input("Date du Mouvement *", value=date.today())
        with nm2: mv_type = st.selectbox("Type de Mouvement *", MOVEMENT_TYPES)

        st.markdown('<div class="sec-title">🔩 Article / Spare Part</div>', unsafe_allow_html=True)

        # Option : lier à un asset existant
        link_asset = st.checkbox("Lier à un asset existant de la base de données")
        if link_asset and not assets_df.empty:
            asset_sel = st.selectbox("Sélectionner l'Asset",
                assets_df["id"].tolist(),
                format_func=lambda x: f"#{x} – {assets_df[assets_df['id']==x]['site_name'].values[0]} – {assets_df[assets_df['id']==x]['item_description'].values[0]} – S/N: {assets_df[assets_df['id']==x]['serial_number'].values[0]}")
            asset_row = assets_df[assets_df["id"]==asset_sel].iloc[0]
            mv_item   = asset_row["item_description"]
            mv_serial = asset_row["serial_number"] or ""
            mv_part   = asset_row["part_number"] or ""
            mv_vendor = asset_row["oem_vendor"] or ""
            st.info(f"✅ Asset sélectionné : **{mv_item}** | S/N: {mv_serial} | Vendor: {mv_vendor}")
        else:
            na1, na2, na3, na4 = st.columns(4)
            with na1:
                mv_item_sel = st.selectbox("Item Description", ITEM_DESCRIPTIONS)
                mv_item = mv_item_sel if mv_item_sel != "Other" else st.text_input("Précisez l'article")
            with na2: mv_serial = st.text_input("Serial Number", placeholder="ex: ANG10413")
            with na3: mv_part   = st.text_input("Part Number")
            with na4:
                mv_vendor_sel = st.selectbox("OEM Vendor", OEM_VENDORS)
                mv_vendor = mv_vendor_sel if mv_vendor_sel != "Other" else st.text_input("Précisez le Vendor")

        mv_qty = st.number_input("Quantité *", min_value=1, value=1)

        st.markdown('<div class="sec-title">📍 Site de Départ → Site de Destination</div>', unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("**🔴 Site de Départ**")
            from_site_id   = st.text_input("Site ID Départ *", placeholder="ex: 4126")
            from_site_name = st.text_input("Site Name Départ *", placeholder="ex: AQUARIUM")
        with sc2:
            st.markdown("**🟢 Site de Destination**")
            to_site_id   = st.text_input("Site ID Destination *", placeholder="ex: 4036")
            to_site_name = st.text_input("Site Name Destination *", placeholder="ex: BANDZOKO")

        st.markdown('<div class="sec-title">👤 Responsabilité & Raison</div>', unsafe_allow_html=True)
        nr1, nr2 = st.columns(2)
        with nr1: mv_technician = st.text_input("Technicien Responsable *", placeholder="ex: Edna/Eric")
        with nr2: mv_status     = st.selectbox("Statut Initial", MOVEMENT_STATUSES)

        mv_reason   = st.text_area("Raison du Mouvement *",
            placeholder="ex: Remplacement batterie défectueuse sur site BANDZOKO", height=75)
        mv_comments = st.text_area("Commentaires additionnels", height=60)

        reception_date = None
        if mv_status in ["Livré", "Confirmé"]:
            reception_date = st.date_input("Date de Réception", value=date.today())

        if st.form_submit_button("💾 Enregistrer le Mouvement", type="primary", use_container_width=True):
            if not from_site_id or not from_site_name or not to_site_id or not to_site_name:
                st.error("⚠️ Les sites de départ et destination sont obligatoires.")
            elif not mv_reason.strip():
                st.error("⚠️ La raison du mouvement est obligatoire.")
            else:
                conn = get_conn()
                conn.execute("""
                    INSERT INTO spare_movements
                    (movement_date, movement_type, item_description, serial_number,
                     part_number, oem_vendor, qty, from_site_id, from_site_name,
                     to_site_id, to_site_name, reason, technician, status,
                     reception_date, comments, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (mv_date.isoformat(), mv_type, mv_item, mv_serial,
                      mv_part, mv_vendor, mv_qty,
                      from_site_id.strip(), from_site_name.strip(),
                      to_site_id.strip(), to_site_name.strip(),
                      mv_reason, mv_technician, mv_status,
                      reception_date.isoformat() if reception_date else None,
                      mv_comments, now_str()))
                conn.commit(); conn.close()
                st.success("✅ Mouvement enregistré avec succès !")
                st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# RAPPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Rapports":
    st.title("📊 Rapports & Analyses")
    df  = load_assets()
    mdf = load_movements()

    tab1, tab2, tab3 = st.tabs(["📦 Assets par Site", "🔄 Historique Mouvements", "📈 Statistiques"])

    with tab1:
        if df.empty:
            st.info("Aucun asset.")
        else:
            sites = df["site_name"].unique().tolist()
            sel_site = st.selectbox("Sélectionner un Site", ["Tous"] + sites)
            if sel_site != "Tous":
                site_df = df[df["site_name"] == sel_site]
            else:
                site_df = df
            st.markdown(f"**{len(site_df)} assets** pour **{sel_site}**")
            st.dataframe(site_df[[
                "site_id","site_name","region","serial_number",
                "item_description","oem_vendor","item_name",
                "network_type","status","install_date"
            ]].rename(columns={
                "site_id":"Site ID","site_name":"Site","region":"Région",
                "serial_number":"S/N","item_description":"Description",
                "oem_vendor":"Vendor","item_name":"Item",
                "network_type":"Network","status":"Status",
                "install_date":"Install Date"
            }), use_container_width=True, hide_index=True)

    with tab2:
        if mdf.empty:
            st.info("Aucun mouvement.")
        else:
            st.dataframe(mdf[[
                "movement_date","movement_type","item_description",
                "serial_number","qty","from_site_name","to_site_name",
                "technician","status","reception_date","reason","comments"
            ]].rename(columns={
                "movement_date":"Date","movement_type":"Type",
                "item_description":"Article","serial_number":"S/N",
                "qty":"Qté","from_site_name":"De","to_site_name":"Vers",
                "technician":"Technicien","status":"Statut",
                "reception_date":"Date Réception",
                "reason":"Raison","comments":"Commentaires"
            }), use_container_width=True, hide_index=True)

    with tab3:
        if not df.empty:
            st.markdown('<div class="sec-title">Assets par OEM Vendor</div>', unsafe_allow_html=True)
            vd = df["oem_vendor"].value_counts().reset_index()
            vd.columns = ["Vendor","Nombre"]
            figv = px.pie(vd, names="Vendor", values="Nombre", hole=0.35)
            figv.update_layout(height=320, margin=dict(t=10,b=10))
            st.plotly_chart(figv, use_container_width=True)

        if not mdf.empty:
            st.markdown('<div class="sec-title">Top Sites – Mouvements sortants</div>', unsafe_allow_html=True)
            from_counts = mdf["from_site_name"].value_counts().reset_index()
            from_counts.columns = ["Site","Mouvements Sortants"]
            figt = px.bar(from_counts, x="Site", y="Mouvements Sortants",
                          color_discrete_sequence=["#6b46c1"])
            figt.update_layout(height=300, margin=dict(t=10,b=10), xaxis_title="")
            st.plotly_chart(figt, use_container_width=True)
