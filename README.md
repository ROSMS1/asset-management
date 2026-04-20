# 🏗️ Asset Management – MTN Congo

Application web/mobile de gestion des assets terrain et des mouvements de spare parts,
basée sur le modèle du fichier **Asset_Management_Template_Global_2024.xlsx**.

## 🚀 Lancement

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📱 Pages de l'application

| Page | Description |
|------|-------------|
| 🏠 **Dashboard** | KPIs globaux, graphiques assets et mouvements |
| ➕ **Nouvel Asset** | Formulaire complet (modèle Asset Database) |
| 📋 **Base de Données Assets** | Liste filtrée + mise à jour |
| 🔄 **Mouvement Spare Parts** | Historique visuel des mouvements |
| ➕ **Nouveau Mouvement** | Enregistrer un déplacement de spare part |
| 📊 **Rapports** | Analyses par site, vendor, mouvements |

## 📐 Modèle des données

### Assets (Asset Database)
`SN | Site ID | Site Name | Region | Serial Number | Part Number |
Item Description | OEM Vendor | Item Name | Network Type | Status |
Install Date | Comments`

### Spare Part Movements (nouvelle rubrique)
`Date | Type (Site→Site / Site→WH / WH→Site) | Article | Serial Number |
Qty | Site Départ | Site Destination | Technicien | Raison | Statut |
Date Réception | Commentaires`

## 🗄️ Base de données
SQLite locale : `asset_management.db` (créée automatiquement)
