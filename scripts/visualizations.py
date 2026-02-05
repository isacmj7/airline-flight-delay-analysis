"""
Visualizations for flight delay analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#34495e']


def save_fig(fig, filename, output_dir=None):
    """Save figure to file."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "visualizations"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    fig.savefig(output_dir / filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_yearly_trend(df, output_dir=None):
    """Plot yearly delay trend."""
    if 'YEAR' not in df.columns:
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    yearly = df.groupby('YEAR').agg({
        'ARR_DELAY': 'mean',
        'IS_DELAYED': 'mean'
    }).reset_index()
    
    ax.plot(yearly['YEAR'], yearly['ARR_DELAY'], marker='o', linewidth=2, 
            markersize=10, color=COLORS[0], label='Avg Delay (min)')
    ax.fill_between(yearly['YEAR'], yearly['ARR_DELAY'], alpha=0.2, color=COLORS[0])
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Average Arrival Delay (minutes)', fontsize=12)
    ax.set_title('Flight Delay Trend (2018-2022)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    for _, row in yearly.iterrows():
        ax.annotate(f'{row["ARR_DELAY"]:.1f}', (row['YEAR'], row['ARR_DELAY']),
                   textcoords='offset points', xytext=(0, 10), ha='center', fontsize=10)
    
    plt.tight_layout()
    save_fig(fig, '01_yearly_delay_trend.png', output_dir)


def plot_monthly_pattern(df, output_dir=None):
    """Plot monthly delay pattern."""
    if 'MONTH' not in df.columns:
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    monthly = df.groupby('MONTH')['ARR_DELAY'].mean().reset_index()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    bars = ax.bar(monthly['MONTH'], monthly['ARR_DELAY'], color=COLORS[0])
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Average Arrival Delay (minutes)', fontsize=12)
    ax.set_title('Flight Delays by Month', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', (bar.get_x() + bar.get_width()/2, height),
                   textcoords='offset points', xytext=(0, 5), ha='center', fontsize=9)
    
    plt.tight_layout()
    save_fig(fig, '02_monthly_pattern.png', output_dir)


def plot_day_of_week(df, output_dir=None):
    """Plot delay pattern by day of week."""
    if 'DAY_OF_WEEK' not in df.columns:
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    daily = df.groupby('DAY_OF_WEEK')['ARR_DELAY'].mean().reset_index()
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    bars = ax.bar(daily['DAY_OF_WEEK'], daily['ARR_DELAY'], color=COLORS[2])
    ax.set_xticks(range(7))
    ax.set_xticklabels(day_names)
    
    ax.set_xlabel('Day of Week', fontsize=12)
    ax.set_ylabel('Average Arrival Delay (minutes)', fontsize=12)
    ax.set_title('Flight Delays by Day of Week', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    save_fig(fig, '03_day_of_week_pattern.png', output_dir)


def plot_top_carriers(df, n=10, output_dir=None):
    """Plot top carriers by number of flights and delay performance."""
    if 'OP_CARRIER' not in df.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Top carriers by flight count
    carrier_counts = df['OP_CARRIER'].value_counts().head(n)
    
    bars1 = axes[0].barh(range(len(carrier_counts)), carrier_counts.values, color=COLORS[0])
    axes[0].set_yticks(range(len(carrier_counts)))
    axes[0].set_yticklabels(carrier_counts.index)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('Number of Flights', fontsize=12)
    axes[0].set_title(f'Top {n} Airlines by Flight Volume', fontsize=13, fontweight='bold')
    
    for bar, val in zip(bars1, carrier_counts.values):
        axes[0].text(val + 1000, bar.get_y() + bar.get_height()/2, f'{val:,.0f}', 
                    va='center', fontsize=9)
    
    # Average delay by carrier
    carrier_delay = df.groupby('OP_CARRIER')['ARR_DELAY'].mean().sort_values(ascending=False).head(n)
    
    colors = [COLORS[1] if v > 0 else COLORS[2] for v in carrier_delay.values]
    bars2 = axes[1].barh(range(len(carrier_delay)), carrier_delay.values, color=colors)
    axes[1].set_yticks(range(len(carrier_delay)))
    axes[1].set_yticklabels(carrier_delay.index)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('Average Arrival Delay (minutes)', fontsize=12)
    axes[1].set_title(f'Top {n} Airlines by Average Delay', fontsize=13, fontweight='bold')
    
    for bar, val in zip(bars2, carrier_delay.values):
        axes[1].text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}', 
                    va='center', fontsize=9)
    
    plt.suptitle('Airline Performance Comparison', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, '04_carrier_analysis.png', output_dir)


def plot_top_airports(df, n=15, output_dir=None):
    """Plot top airports by delays."""
    if 'ORIGIN' not in df.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top origin airports by delay
    origin_delay = df.groupby('ORIGIN')['ARR_DELAY'].mean().sort_values(ascending=False).head(n)
    
    bars1 = axes[0].barh(range(len(origin_delay)), origin_delay.values, color=COLORS[1])
    axes[0].set_yticks(range(len(origin_delay)))
    axes[0].set_yticklabels(origin_delay.index, fontsize=10)
    axes[0].invert_yaxis()
    axes[0].set_xlabel('Average Arrival Delay (minutes)', fontsize=12)
    axes[0].set_title('Top Origin Airports by Avg Delay', fontsize=13, fontweight='bold')
    
    # Top destination airports by delay
    dest_delay = df.groupby('DEST')['ARR_DELAY'].mean().sort_values(ascending=False).head(n)
    
    bars2 = axes[1].barh(range(len(dest_delay)), dest_delay.values, color=COLORS[3])
    axes[1].set_yticks(range(len(dest_delay)))
    axes[1].set_yticklabels(dest_delay.index, fontsize=10)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('Average Arrival Delay (minutes)', fontsize=12)
    axes[1].set_title('Top Destination Airports by Avg Delay', fontsize=13, fontweight='bold')
    
    plt.suptitle('Airport Delay Analysis', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, '05_airport_delays.png', output_dir)


def plot_delay_causes(df, output_dir=None):
    """Plot delay causes breakdown."""
    delay_cols = ['CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 
                  'SECURITY_DELAY', 'LATE_AIRCRAFT_DELAY']
    
    available_cols = [col for col in delay_cols if col in df.columns]
    if not available_cols:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Count of flights affected by each delay type
    counts = {}
    totals = {}
    for col in available_cols:
        counts[col.replace('_DELAY', '')] = len(df[df[col] > 0])
        totals[col.replace('_DELAY', '')] = df[col].sum()
    
    # Pie chart for delay distribution
    labels = list(counts.keys())
    sizes = list(counts.values())
    colors_pie = COLORS[:len(labels)]
    
    wedges, texts, autotexts = axes[0].pie(sizes, labels=labels, autopct='%1.1f%%', 
                                           colors=colors_pie, explode=[0.02]*len(labels))
    axes[0].set_title('Flight Delays by Cause (Count)', fontsize=13, fontweight='bold')
    
    # Bar chart for total delay minutes
    labels = list(totals.keys())
    values = [v / 1000000 for v in totals.values()]  # Convert to millions
    
    bars = axes[1].barh(range(len(labels)), values, color=COLORS[:len(labels)])
    axes[1].set_yticks(range(len(labels)))
    axes[1].set_yticklabels(labels, fontsize=11)
    axes[1].invert_yaxis()
    axes[1].set_xlabel('Total Delay (Million Minutes)', fontsize=12)
    axes[1].set_title('Total Delay Minutes by Cause', fontsize=13, fontweight='bold')
    
    for bar, val in zip(bars, values):
        axes[1].text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.1f}M', 
                    va='center', fontsize=10)
    
    plt.suptitle('Delay Causes Analysis', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, '06_delay_causes.png', output_dir)


def plot_delay_distribution(df, output_dir=None):
    """Plot delay distribution histogram."""
    if 'ARR_DELAY' not in df.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Filter to reasonable delay range
    delays = df['ARR_DELAY'][(df['ARR_DELAY'] >= -30) & (df['ARR_DELAY'] <= 120)]
    
    # Histogram
    axes[0].hist(delays, bins=50, color=COLORS[0], edgecolor='white', alpha=0.7)
    axes[0].axvline(x=0, color='green', linestyle='--', linewidth=2, label='On Time')
    axes[0].axvline(x=15, color='red', linestyle='--', linewidth=2, label='15 min threshold')
    axes[0].set_xlabel('Arrival Delay (minutes)', fontsize=12)
    axes[0].set_ylabel('Number of Flights', fontsize=12)
    axes[0].set_title('Distribution of Flight Delays', fontsize=13, fontweight='bold')
    axes[0].legend()
    
    # On-time vs Delayed pie chart
    on_time = len(df[df['ARR_DELAY'] <= 15])
    delayed = len(df[df['ARR_DELAY'] > 15])
    
    axes[1].pie([on_time, delayed], labels=['On Time (≤15 min)', 'Delayed (>15 min)'],
               autopct='%1.1f%%', colors=[COLORS[2], COLORS[1]], explode=[0, 0.05])
    axes[1].set_title('On-Time Performance', fontsize=13, fontweight='bold')
    
    plt.suptitle('Flight Delay Distribution', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, '07_delay_distribution.png', output_dir)


def plot_cancellation_analysis(df, output_dir=None):
    """Plot cancellation analysis."""
    if 'CANCELLED' not in df.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Cancellation rate by carrier
    if 'OP_CARRIER' in df.columns:
        carrier_cancel = df.groupby('OP_CARRIER')['CANCELLED'].mean().sort_values(ascending=False).head(10) * 100
        
        bars = axes[0].barh(range(len(carrier_cancel)), carrier_cancel.values, color=COLORS[1])
        axes[0].set_yticks(range(len(carrier_cancel)))
        axes[0].set_yticklabels(carrier_cancel.index)
        axes[0].invert_yaxis()
        axes[0].set_xlabel('Cancellation Rate (%)', fontsize=12)
        axes[0].set_title('Cancellation Rate by Airline', fontsize=13, fontweight='bold')
        
        for bar, val in zip(bars, carrier_cancel.values):
            axes[0].text(val + 0.1, bar.get_y() + bar.get_height()/2, f'{val:.2f}%', 
                        va='center', fontsize=9)
    
    # Cancellation rate by month
    if 'MONTH' in df.columns:
        monthly_cancel = df.groupby('MONTH')['CANCELLED'].mean() * 100
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        axes[1].bar(range(1, 13), monthly_cancel.values, color=COLORS[3])
        axes[1].set_xticks(range(1, 13))
        axes[1].set_xticklabels(month_names)
        axes[1].set_xlabel('Month', fontsize=12)
        axes[1].set_ylabel('Cancellation Rate (%)', fontsize=12)
        axes[1].set_title('Cancellation Rate by Month', fontsize=13, fontweight='bold')
    
    plt.suptitle('Flight Cancellation Analysis', fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    save_fig(fig, '08_cancellation_analysis.png', output_dir)


def create_all_visualizations(df, output_dir=None):
    """Create all charts."""
    print("Creating visualizations...")
    
    plot_yearly_trend(df, output_dir)
    print("  - Yearly trend")
    
    plot_monthly_pattern(df, output_dir)
    print("  - Monthly pattern")
    
    plot_day_of_week(df, output_dir)
    print("  - Day of week pattern")
    
    plot_top_carriers(df, output_dir=output_dir)
    print("  - Carrier analysis")
    
    plot_top_airports(df, output_dir=output_dir)
    print("  - Airport delays")
    
    plot_delay_causes(df, output_dir)
    print("  - Delay causes")
    
    plot_delay_distribution(df, output_dir)
    print("  - Delay distribution")
    
    plot_cancellation_analysis(df, output_dir)
    print("  - Cancellation analysis")
    
    print("Done!")


if __name__ == "__main__":
    from data_processing import load_flight_data, clean_flight_data
    
    df = load_flight_data(sample_size=100000)
    df_clean = clean_flight_data(df)
    create_all_visualizations(df_clean)
