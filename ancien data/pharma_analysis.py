import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Configuration du style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# =====================================
# CHARGEMENT DES DONNÉES
# =====================================

print("📂 Chargement des données...")
df = pd.read_csv('/home/claude/pharma_dataset.csv')
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month
df['month_name'] = df['date'].dt.strftime('%B')

print(f"✅ {len(df):,} transactions chargées\n")

# =====================================
# ANALYSES
# =====================================

print("="*60)
print("📊 ANALYSES DÉTAILLÉES")
print("="*60)

# 1. Analyse temporelle
print("\n1️⃣ ÉVOLUTION MENSUELLE")
monthly_sales = df.groupby('month').agg({
    'sales': 'sum',
    'revenue': 'sum'
}).reset_index()

print(monthly_sales.to_string(index=False))

# 2. Analyse par catégorie
print("\n2️⃣ PERFORMANCE PAR CATÉGORIE")
category_stats = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'std'],
    'revenue': 'sum',
    'price': 'mean'
}).round(2)
category_stats.columns = ['Ventes_totales', 'Ventes_moy', 'Écart_type', 'Revenue_total', 'Prix_moyen']
print(category_stats.sort_values('Revenue_total', ascending=False).to_string())

# 3. Corrélation température-ventes
print("\n3️⃣ CORRÉLATION TEMPÉRATURE - VENTES")
correlation = df[['temperature', 'sales', 'price', 'revenue']].corr()
print(correlation.to_string())

# 4. Performance pharmacies
print("\n4️⃣ TOP 10 PHARMACIES (par revenue)")
top_pharmacies = df.groupby('pharmacy_id')['revenue'].sum().sort_values(ascending=False).head(10)
print(top_pharmacies.to_string())

# 5. Impact weekend
print("\n5️⃣ IMPACT WEEKEND vs SEMAINE")
weekend_analysis = df.groupby('is_weekend').agg({
    'sales': ['sum', 'mean'],
    'revenue': 'sum'
}).round(2)
weekend_analysis.index = ['Semaine', 'Weekend']
print(weekend_analysis.to_string())

# =====================================
# VISUALISATIONS
# =====================================

print("\n\n🎨 Génération des visualisations...")

fig = plt.figure(figsize=(20, 12))

# 1. Évolution mensuelle des ventes
ax1 = plt.subplot(3, 3, 1)
monthly_sales_plot = df.groupby('month')['sales'].sum()
ax1.plot(monthly_sales_plot.index, monthly_sales_plot.values, 
         marker='o', linewidth=2, markersize=8, color='#2E86AB')
ax1.fill_between(monthly_sales_plot.index, monthly_sales_plot.values, alpha=0.3, color='#2E86AB')
ax1.set_xlabel('Mois', fontsize=10, fontweight='bold')
ax1.set_ylabel('Ventes totales', fontsize=10, fontweight='bold')
ax1.set_title('📈 Évolution Mensuelle des Ventes', fontsize=12, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3)
ax1.set_xticks(range(1, 13))

# 2. Revenue par région
ax2 = plt.subplot(3, 3, 2)
region_revenue = df.groupby('region')['revenue'].sum().sort_values(ascending=True)
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(region_revenue)))
ax2.barh(region_revenue.index, region_revenue.values, color=colors)
ax2.set_xlabel('Revenue (MAD)', fontsize=10, fontweight='bold')
ax2.set_title('🌍 Revenue par Région', fontsize=12, fontweight='bold', pad=15)
ax2.grid(axis='x', alpha=0.3)
for i, v in enumerate(region_revenue.values):
    ax2.text(v, i, f' {v/1e6:.1f}M', va='center', fontsize=9)

# 3. Distribution des prix
ax3 = plt.subplot(3, 3, 3)
ax3.hist(df['price'], bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
ax3.axvline(df['price'].mean(), color='red', linestyle='--', linewidth=2, label=f"Moyenne: {df['price'].mean():.2f} MAD")
ax3.axvline(df['price'].median(), color='green', linestyle='--', linewidth=2, label=f"Médiane: {df['price'].median():.2f} MAD")
ax3.set_xlabel('Prix (MAD)', fontsize=10, fontweight='bold')
ax3.set_ylabel('Fréquence', fontsize=10, fontweight='bold')
ax3.set_title('💰 Distribution des Prix', fontsize=12, fontweight='bold', pad=15)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)

# 4. Ventes par saison
ax4 = plt.subplot(3, 3, 4)
season_order = ['hiver', 'printemps', 'été', 'automne']
season_sales = df.groupby('season')['sales'].sum().reindex(season_order)
colors_season = ['#5DADE2', '#52BE80', '#F4D03F', '#E67E22']
wedges, texts, autotexts = ax4.pie(season_sales.values, labels=season_sales.index, 
                                     autopct='%1.1f%%', startangle=90, colors=colors_season,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})
ax4.set_title('❄️🌸☀️🍂 Répartition Saisonnière', fontsize=12, fontweight='bold', pad=15)

# 5. Top 10 catégories
ax5 = plt.subplot(3, 3, 5)
top_categories = df.groupby('category')['sales'].sum().sort_values(ascending=False).head(10)
ax5.bar(range(len(top_categories)), top_categories.values, color='#E74C3C')
ax5.set_xticks(range(len(top_categories)))
ax5.set_xticklabels(top_categories.index, rotation=45, ha='right', fontsize=9)
ax5.set_ylabel('Ventes totales', fontsize=10, fontweight='bold')
ax5.set_title('💊 Top 10 Catégories', fontsize=12, fontweight='bold', pad=15)
ax5.grid(axis='y', alpha=0.3)

# 6. Température vs Ventes (scatter)
ax6 = plt.subplot(3, 3, 6)
sample_data = df.sample(min(1000, len(df)))
scatter = ax6.scatter(sample_data['temperature'], sample_data['sales'], 
                     c=sample_data['price'], cmap='coolwarm', alpha=0.5, s=30)
ax6.set_xlabel('Température (°C)', fontsize=10, fontweight='bold')
ax6.set_ylabel('Ventes', fontsize=10, fontweight='bold')
ax6.set_title('🌡️ Température vs Ventes', fontsize=12, fontweight='bold', pad=15)
plt.colorbar(scatter, ax=ax6, label='Prix (MAD)')
ax6.grid(True, alpha=0.3)

# 7. Heatmap ventes par région et saison
ax7 = plt.subplot(3, 3, 7)
heatmap_data = df.pivot_table(values='sales', index='region', columns='season', aggfunc='sum')
heatmap_data = heatmap_data[season_order]  # Réordonner les colonnes
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax7, cbar_kws={'label': 'Ventes'})
ax7.set_title('🔥 Ventes: Région × Saison', fontsize=12, fontweight='bold', pad=15)
ax7.set_xlabel('Saison', fontsize=10, fontweight='bold')
ax7.set_ylabel('Région', fontsize=10, fontweight='bold')

# 8. Comparaison Weekend vs Semaine
ax8 = plt.subplot(3, 3, 8)
weekend_sales = df.groupby('is_weekend')['sales'].sum()
labels = ['Semaine', 'Weekend']
ax8.bar(labels, weekend_sales.values, color=['#3498DB', '#E67E22'], width=0.6)
ax8.set_ylabel('Ventes totales', fontsize=10, fontweight='bold')
ax8.set_title('📅 Weekend vs Semaine', fontsize=12, fontweight='bold', pad=15)
ax8.grid(axis='y', alpha=0.3)
for i, v in enumerate(weekend_sales.values):
    ax8.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# 9. Évolution quotidienne (moyenne mobile 7 jours)
ax9 = plt.subplot(3, 3, 9)
daily_sales = df.groupby('date')['sales'].sum().reset_index()
daily_sales['MA7'] = daily_sales['sales'].rolling(window=7).mean()
ax9.plot(daily_sales['date'], daily_sales['sales'], alpha=0.3, color='gray', label='Quotidien')
ax9.plot(daily_sales['date'], daily_sales['MA7'], linewidth=2, color='#C0392B', label='Moyenne Mobile 7j')
ax9.set_xlabel('Date', fontsize=10, fontweight='bold')
ax9.set_ylabel('Ventes', fontsize=10, fontweight='bold')
ax9.set_title('📊 Tendance Quotidienne (MA7)', fontsize=12, fontweight='bold', pad=15)
ax9.legend(fontsize=9)
ax9.grid(True, alpha=0.3)
plt.setp(ax9.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('/home/claude/pharma_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Graphiques sauvegardés: pharma_analysis.png")

# =====================================
# INSIGHTS CLÉS
# =====================================

print("\n" + "="*60)
print("💡 INSIGHTS CLÉS")
print("="*60)

# Meilleur mois
best_month = monthly_sales.loc[monthly_sales['sales'].idxmax()]
print(f"\n🏆 Meilleur mois: Mois {int(best_month['month'])} avec {int(best_month['sales']):,} ventes")

# Meilleure région
best_region = df.groupby('region')['revenue'].sum().idxmax()
best_region_revenue = df.groupby('region')['revenue'].sum().max()
print(f"🌟 Meilleure région: {best_region} ({best_region_revenue/1e6:.2f}M MAD)")

# Catégorie la plus rentable
best_category = df.groupby('category')['revenue'].sum().idxmax()
best_category_revenue = df.groupby('category')['revenue'].sum().max()
print(f"💊 Catégorie la plus rentable: {best_category} ({best_category_revenue/1e6:.2f}M MAD)")

# Impact température
temp_corr = df[['temperature', 'sales']].corr().iloc[0, 1]
print(f"🌡️  Corrélation température-ventes: {temp_corr:.3f}")
if temp_corr < -0.2:
    print("   → Forte corrélation négative: plus il fait froid, plus les ventes augmentent")
elif temp_corr > 0.2:
    print("   → Forte corrélation positive: plus il fait chaud, plus les ventes augmentent")
else:
    print("   → Corrélation faible")

# Weekend impact
weekend_diff = df.groupby('is_weekend')['sales'].mean()
reduction = (1 - weekend_diff[True] / weekend_diff[False]) * 100
print(f"📅 Impact weekend: {reduction:.1f}% de réduction des ventes moyennes")

print("\n" + "="*60)
print("✅ Analyse terminée!")
print("="*60)
