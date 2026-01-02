Hier ist der **finale, vollständig verifizierte Python-Code**. Er erfüllt alle deine Anforderungen:

1. **Detaillierte Timeline:** Unterteilt in **IST** (mit den 7 Schritten), **Verschwendung** (explizit ausgewiesen) und **SOLL** (Lean-Optimiert).
2. **Belastungskurve:** Exakte Datenpunkte wie besprochen (inkl. Flaschenhals bei QS und Unterforderung bei Puffer).
3. **Prozessschritte:** "Pass" wurde durch **"Bandlauf / Automatik"** ersetzt.
4. **12 KPIs:** Die Bezeichnungen sind gemäss der Schärfung aktualisiert und werden als Report ausgegeben.

Du kannst diesen Code direkt in einer Python-Umgebung (Jupyter Notebook, Colab oder lokal) ausführen.

```python
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. DATENBASIS & KONFIGURATION
# ---------------------------------------------------------

# Prozess-Schritte (Labels)
steps_ist = [
    "Anmeldung & Erfassung", 
    "Vorbereitung Material", 
    "Transport zum Band", 
    "Bandlauf / Automatik", 
    "Pufferlager / Stau", 
    "QS-Prüfung (Manuell)", 
    "Verpackung & Ausgabe"
]

# Zeitdauer in Minuten (IST)
durations_ist = [15, 20, 10, 25, 15, 20, 15]
# Startzeiten berechnen (kumulativ)
starts_ist = [0]
for d in durations_ist[:-1]:
    starts_ist.append(starts_ist[-1] + d)

# Verschwendungs-Analyse (Wo verlieren wir Zeit?)
# Diese Blöcke visualisieren die "Muda" (Verschwendung) parallel zum IST
waste_blocks = [
    (15, 10),  # Warten nach Anmeldung
    (35, 10),  # Unnötiger Transport
    (70, 15),  # Liegezeit im Puffer
    (85, 5)    # Nacharbeit in QS
]

# SOLL-Zustand (LEAN Flow) - Gestrafft, kein Puffer, schnellere QS
# Schritte: Digital Check-In (5), JIT Prep (15), Band (25), Auto-QS (5), Direktausgabe (10)
durations_soll = [5, 15, 25, 5, 10]
starts_soll = [0]
for d in durations_soll[:-1]:
    starts_soll.append(starts_soll[-1] + d)
labels_soll = ["Dig. Check-In", "JIT Prep", "Band (Opt.)", "Auto-QS", "Direktausgabe"]

# Belastungs-Daten (Auslastung in %)
load_labels = ["Anmeldung", "Vorbereitung", "Transport", "Bandlauf", "Puffer/Stau", "QS-Prüfung", "Ausgabe"]
load_values = [85, 60, 20, 95, 10, 115, 70] # 115% ist der Flaschenhals, 10% & 20% sind Verschwendung

# ---------------------------------------------------------
# 2. VISUALISIERUNG (Matplotlib)
# ---------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [1, 1]})
plt.subplots_adjust(hspace=0.4)

# --- PLOT 1: TIMELINE (Gantt) ---

# Y-Positionen
y_ist = 30
y_waste = 20
y_soll = 10
height = 8

# Farben
color_ist = '#3498db'   # Blau
color_waste = '#e74c3c' # Rot
color_soll = '#2ecc71'  # Grün

# 1. IST-Timeline zeichnen
for i, (start, duration) in enumerate(zip(starts_ist, durations_ist)):
    ax1.broken_barh([(start, duration)], (y_ist, height), facecolors=color_ist, edgecolor='white')
    # Text Label mittig im Balken
    ax1.text(start + duration/2, y_ist + height/2, steps_ist[i], 
             ha='center', va='center', color='white', fontsize=8, fontweight='bold', rotation=0)

# 2. Verschwendung zeichnen
for start, duration in waste_blocks:
    ax1.broken_barh([(start, duration)], (y_waste, height), facecolors=color_waste, hatch='//', edgecolor='white')

# 3. SOLL-Timeline zeichnen
for i, (start, duration) in enumerate(zip(starts_soll, durations_soll)):
    ax1.broken_barh([(start, duration)], (y_soll, height), facecolors=color_soll, edgecolor='white')
    ax1.text(start + duration/2, y_soll + height/2, labels_soll[i], 
             ha='center', va='center', color='white', fontsize=8, fontweight='bold')

# Formatierung Timeline
ax1.set_ylim(5, 45)
ax1.set_xlim(0, 130)
ax1.set_xlabel('Prozessdauer (Minuten)')
ax1.set_yticks([y_soll + height/2, y_waste + height/2, y_ist + height/2])
ax1.set_yticklabels(['SOLL (Lean)', 'Verschwendung (Muda)', 'IST (Detailliert)'])
ax1.set_title('Prozess-Vergleich: IST vs. VERSCHWENDUNG vs. SOLL', fontsize=14, fontweight='bold')
ax1.grid(True, axis='x', linestyle='--', alpha=0.5)

# Legende manuell hinzufügen
patch_ist = mpatches.Patch(color=color_ist, label='Wertschöpfung / Prozess')
patch_waste = mpatches.Patch(color=color_waste, hatch='//', label='Identifizierte Verschwendung')
patch_soll = mpatches.Patch(color=color_soll, label='Optimierter LEAN-Prozess')
ax1.legend(handles=[patch_ist, patch_waste, patch_soll], loc='upper right')


# --- PLOT 2: BELASTUNGSKURVE ---

# Farben basierend auf Werten (Rot für Überlast, Gelb für Unterlast)
colors_load = []
for val in load_values:
    if val > 100:
        colors_load.append('#c0392b') # Dunkelrot (Überlast)
    elif val < 30:
        colors_load.append('#f1c40f') # Gelb (Unterlast/Verschwendung)
    else:
        colors_load.append('#34495e') # Dunkelblau (Normal)

bars = ax2.bar(load_labels, load_values, color=colors_load, width=0.6)

# Referenzlinie bei 100%
ax2.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label='Kapazitätsgrenze (100%)')

# Labels auf den Balken
for bar in bars:
    height_val = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, height_val + 2, f'{height_val}%', ha='center', va='bottom', fontweight='bold')

# Formatierung Belastungskurve
ax2.set_ylabel('Auslastung (%)')
ax2.set_title('Detaillierte Belastungskurve (IST-Zustand)', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 130)
ax2.grid(True, axis='y', linestyle='--', alpha=0.3)
ax2.legend()

# Annotationen für Flaschenhals und Verschwendung
ax2.annotate('FLASCHENHALS', xy=(5, 115), xytext=(5, 125),
             arrowprops=dict(facecolor='black', shrink=0.05), ha='center', color='red', fontweight='bold')
ax2.annotate('Verschwendung\n(Keine Wertschöpfung)', xy=(4, 10), xytext=(4, 40),
             arrowprops=dict(facecolor='black', shrink=0.05), ha='center', fontsize=9)

plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# 3. TEXT-REPORT: DIE 12 GESCHÄRFTEN KPIs
# ---------------------------------------------------------
kpi_data = {
    "Nr.": range(1, 13),
    "Alter Begriff": ["Dauer", "Menge", "Fehler", "Kosten", "Warten", "Arbeit", "Nutzung", "Personal", "Termine", "Stimmung", "Takt", "Rückstau"],
    "NEUER KPI (Geschärft)": [
        "Durchlaufzeit (Lead Time)", 
        "Netto-Output pro Stunde", 
        "First Pass Yield (FPY)", 
        "Prozesskosten pro Transaktion", 
        "Flusseffizienz (%)", 
        "WIP (Work in Process)", 
        "OEE (Gesamtanlageneffektivität)", 
        "Produktivität pro FTE", 
        "OTIF (On Time In Full)", 
        "Mitarbeiter-NPS (eNPS)", 
        "Zykluszeit-Varianz", 
        "Backlog-Age (Rückstandsalter)"
    ],
    "Beschreibung / Fokus": [
        "Gesamtzeit Start bis Ende inkl. Liegezeiten",
        "Nutzbarer Output bereinigt um Ausschuss",
        "% Einheiten ohne Nacharbeit (Right First Time)",
        "Gemeinkosten auf Vorgang heruntergebrochen",
        "Verhältnis Wertschöpfung zu Durchlaufzeit",
        "Anzahl offener Vorgänge im System (Stau-Treiber)",
        "Verfügbarkeit x Leistung x Qualität (Band)",
        "Output im Verhältnis zur eingesetzten Arbeitskraft",
        "Pünktlich UND vollständig geliefert",
        "Weiterempfehlungsrate des Prozesses durch MA",
        "Stabilität des Taktes (Schwankungsmessung)",
        "Alter des ältesten unerledigten Auftrags"
    ]
}

df_kpi = pd.DataFrame(kpi_data)

print("\n" + "="*80)
print("FINALER KPI REPORT (LEAN MANAGEMENT)")
print("="*80)
# Saubere Formatierung für die Konsole
print(df_kpi.to_string(index=False, justify='left'))
print("="*80)

```
