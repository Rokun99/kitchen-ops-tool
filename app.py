import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. DATENBASIS & LOGIK
# ---------------------------------------------------------

# IST-Prozess (Sequentiell)
# Schritt 3 wurde von "Pass" auf "Bandlauf" umgestellt/integriert,
# hier als expliziter Schritt "Transport zum Band" und dann "Bandlauf".
steps_ist = [
    "Anmeldung & Erfassung", 
    "Vorbereitung Material", 
    "Transport zum Band", 
    "Bandlauf / Automatik", 
    "Pufferlager / Stau", 
    "QS-Prüfung (Manuell)", 
    "Verpackung & Ausgabe"
]
durations_ist = [15, 20, 10, 25, 15, 20, 15]

# Startzeiten IST berechnen
starts_ist = [0]
for d in durations_ist[:-1]:
    starts_ist.append(starts_ist[-1] + d)
total_time_ist = sum(durations_ist)

# Verschwendung (Muda) - Parallel visualisiert
# (Startzeit, Dauer) -> Diese Zeiten sind in den IST-Dauern enthalten, aber nicht wertschöpfend
waste_blocks = [
    (15, 10),  # Warten auf Slot (nach Anmeldung)
    (35, 10),  # Transportweg (unnötig lang)
    (70, 15),  # Liegezeit im Puffer (vor QS)
    (85, 5)    # Nacharbeit / Rüstzeit in QS
]
total_waste_time = sum([w[1] for w in waste_blocks])

# SOLL-Prozess (LEAN / Optimiert)
# Keine Puffer, Automatisierung, Parallelisierung
durations_soll = [5, 15, 25, 5, 10]
steps_soll = ["Dig. Check-In", "JIT Prep", "Band (Opt.)", "Auto-QS", "Direktausgabe"]
starts_soll = [0]
for d in durations_soll[:-1]:
    starts_soll.append(starts_soll[-1] + d)
total_time_soll = sum(durations_soll)

# Belastungs-Daten (Auslastung in %) für den IST-Zustand
# "Pass" ist entfernt, Fokus auf Band und Engpässe
load_labels = ["Anmeldung", "Vorbereitung", "Transport", "Bandlauf", "Puffer", "QS-Prüfung", "Ausgabe"]
load_values = [85, 60, 20, 95, 10, 115, 70] 
# Logik: 115% = Überlast (Flaschenhals), <30% = Unterlast (Verschwendung)

# ---------------------------------------------------------
# 2. VISUALISIERUNG
# ---------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [1, 1]})
plt.subplots_adjust(hspace=0.4)

# --- CHART 1: TIMELINE (Gantt) ---

# Einstellungen
y_ist = 30
y_waste = 20
y_soll = 10
bar_height = 8

# 1. IST-Zustand
for i, (start, duration) in enumerate(zip(starts_ist, durations_ist)):
    ax1.broken_barh([(start, duration)], (y_ist, bar_height), facecolors='#3498db', edgecolor='white')
    ax1.text(start + duration/2, y_ist + bar_height/2, steps_ist[i], 
             ha='center', va='center', color='white', fontsize=8, fontweight='bold')

# 2. Verschwendung (explizit darunter)
for start, duration in waste_blocks:
    ax1.broken_barh([(start, duration)], (y_waste, bar_height), facecolors='#e74c3c', hatch='///', edgecolor='white')
    # Label nur wenn Platz ist
    if duration >= 10:
        ax1.text(start + duration/2, y_waste + bar_height/2, "Verschwendung", 
                 ha='center', va='center', color='white', fontsize=7, rotation=0)

# 3. SOLL-Zustand
for i, (start, duration) in enumerate(zip(starts_soll, durations_soll)):
    ax1.broken_barh([(start, duration)], (y_soll, bar_height), facecolors='#2ecc71', edgecolor='white')
    ax1.text(start + duration/2, y_soll + bar_height/2, steps_soll[i], 
             ha='center', va='center', color='white', fontsize=8, fontweight='bold')

# Formatierung Timeline
ax1.set_ylim(5, 45)
ax1.set_xlim(0, total_time_ist + 10)
ax1.set_xlabel('Durchlaufzeit (Minuten) - KPI: Lead Time')
ax1.set_yticks([y_soll + bar_height/2, y_waste + bar_height/2, y_ist + bar_height/2])
ax1.set_yticklabels(['SOLL (Lean)', 'Verschwendung (Muda)', 'IST (Detailliert)'])
ax1.set_title('Prozess-Analyse: Von IST zu SOLL (Eliminierung von Waste)', fontsize=14, fontweight='bold')
ax1.grid(True, axis='x', linestyle='--', alpha=0.5)

# Legende
p_ist = mpatches.Patch(color='#3498db', label='IST-Prozess')
p_waste = mpatches.Patch(color='#e74c3c', hatch='///', label='Identifizierte Verschwendung')
p_soll = mpatches.Patch(color='#2ecc71', label='SOLL-Prozess (Optimiert)')
ax1.legend(handles=[p_ist, p_waste, p_soll], loc='upper right')


# --- CHART 2: BELASTUNGSKURVE (Load Curve) ---

# Farb-Logik für Load Curve
colors = ['#c0392b' if x > 100 else '#f1c40f' if x < 30 else '#2c3e50' for x in load_values]

bars = ax2.bar(load_labels, load_values, color=colors, width=0.6)

# Kritische Linien
ax2.axhline(y=100, color='red', linestyle='-', linewidth=2, label='Max. Kapazität (100%)')
ax2.axhline(y=85, color='green', linestyle='--', linewidth=1, label='Optimale Auslastung (85%)')

# Labels auf Balken
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height}%', ha='center', va='bottom', fontweight='bold')

# Annotationen
ax2.annotate('ENGPASS (QS)', xy=(5, 115), xytext=(5, 130),
             arrowprops=dict(facecolor='red', shrink=0.05), ha='center', color='red', fontweight='bold')
ax2.annotate('Verschwendung\n(Warten/Transport)', xy=(2, 20), xytext=(2, 50),
             arrowprops=dict(facecolor='black', shrink=0.05), ha='center')

ax2.set_ylabel('Auslastung (%)')
ax2.set_ylim(0, 140)
ax2.set_title('Detaillierte Belastungskurve (IST) - Identifikation Engpässe & Leerlauf', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()

# ---------------------------------------------------------
# 3. MANAGEMENT REPORT & KPIs (Text Output)
# ---------------------------------------------------------

# Berechnung der Delta-Werte (Einsparungen)
savings_time = total_time_ist - total_time_soll
savings_percent = (savings_time / total_time_ist) * 100
efficiency_ist = ((total_time_ist - total_waste_time) / total_time_ist) * 100

# DataFrame für die 12 geschärften KPIs
kpi_definitions = [
    ("01", "Durchlaufzeit (Lead Time)", f"{total_time_ist} min -> {total_time_soll} min", "Gesamtzeit drastisch reduziert"),
    ("02", "Netto-Output pro Stunde", "Steigend", "Durch Auflösung des QS-Engpasses"),
    ("03", "First Pass Yield (FPY)", "Zu messen", "Ziel: 98% ohne Nacharbeit"),
    ("04", "Prozesskosten / Transaktion", "Sinkend", "Weniger Personalbindung pro Stück"),
    ("05", "Flusseffizienz", f"IST: {efficiency_ist:.1f}%", "Anteil Wertschöpfung an Gesamtzeit"),
    ("06", "WIP (Work in Process)", "Reduziert", "Kein Pufferlager mehr im SOLL"),
    ("07", "OEE (Band)", "95% (IST)", "Band ist gut ausgelastet, aber Zubringer fehlt"),
    ("08", "Produktivität pro FTE", "Steigend", "Weniger Wartezeit = Mehr Output"),
    ("09", "OTIF (On Time In Full)", "Ziel: 100%", "Pünktliche Lieferung"),
    ("10", "Mitarbeiter-NPS", "Zu messen", "Weniger Frust durch glatten Prozess"),
    ("11", "Zykluszeit-Varianz", "Stabilisiert", "Automatisierung reduziert Schwankung"),
    ("12", "Backlog-Age", "Minimiert", "Stau vor QS aufgelöst")
]

df_kpi = pd.DataFrame(kpi_definitions, columns=["Nr", "KPI (Geschärft)", "Wert / Status", "Kommentar"])

print("\n" + "="*80)
print(f" MANAGEMENT SUMMARY: POTENTIAL-ANALYSE")
print("="*80)
print(f" IST-Durchlaufzeit : {total_time_ist} Minuten")
print(f" SOLL-Durchlaufzeit: {total_time_soll} Minuten")
print(f" -> ZEITERSPARNIS  : {savings_time} Minuten (-{savings_percent:.1f}%)")
print(f" -> FLUSSEFFIZIENZ : {efficiency_ist:.1f}% (im IST-Zustand)")
print("-" * 80)
print(" DETAIL-REPORT DER 12 KPIs:")
print("-" * 80)
print(df_kpi.to_string(index=False, justify='left'))
print("="*80)
