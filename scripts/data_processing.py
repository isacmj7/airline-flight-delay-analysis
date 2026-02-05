"""
Data processing for flight delay analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_flight_data(filepath=None, sample_size=None):
    """Load flight data from CSV file."""
    if filepath is None:
        project_root = Path(__file__).parent.parent
        filepath = project_root / "data" / "flights.csv"
    
    if sample_size:
        df = pd.read_csv(filepath, nrows=sample_size, low_memory=False)
    else:
        df = pd.read_csv(filepath, low_memory=False)
    
    print(f"Loaded flight data: {len(df)} rows")
    return df


def clean_flight_data(df):
    """Clean flight data."""
    df_clean = df.copy()
    
    # Standardize column names (handle different naming conventions)
    column_mapping = {
        'FlightDate': 'FL_DATE',
        'FL_DATE': 'FL_DATE',
        'Airline': 'OP_CARRIER',
        'Reporting_Airline': 'OP_CARRIER',
        'CARRIER': 'OP_CARRIER',
        'OP_UNIQUE_CARRIER': 'OP_CARRIER',
        'Origin': 'ORIGIN',
        'ORIGIN': 'ORIGIN',
        'Dest': 'DEST',
        'DEST': 'DEST',
        'DepDelay': 'DEP_DELAY',
        'DEP_DELAY': 'DEP_DELAY',
        'ArrDelay': 'ARR_DELAY',
        'ARR_DELAY': 'ARR_DELAY',
        'Cancelled': 'CANCELLED',
        'CANCELLED': 'CANCELLED',
        'Diverted': 'DIVERTED',
        'DIVERTED': 'DIVERTED',
        'CarrierDelay': 'CARRIER_DELAY',
        'CARRIER_DELAY': 'CARRIER_DELAY',
        'WeatherDelay': 'WEATHER_DELAY',
        'WEATHER_DELAY': 'WEATHER_DELAY',
        'NASDelay': 'NAS_DELAY',
        'NAS_DELAY': 'NAS_DELAY',
        'SecurityDelay': 'SECURITY_DELAY',
        'SECURITY_DELAY': 'SECURITY_DELAY',
        'LateAircraftDelay': 'LATE_AIRCRAFT_DELAY',
        'LATE_AIRCRAFT_DELAY': 'LATE_AIRCRAFT_DELAY'
    }
    
    for old_name, new_name in column_mapping.items():
        if old_name in df_clean.columns:
            df_clean = df_clean.rename(columns={old_name: new_name})
    
    # Convert date column if present
    date_col = 'FL_DATE' if 'FL_DATE' in df_clean.columns else None
    if date_col is None:
        for col in df_clean.columns:
            if 'date' in col.lower():
                date_col = col
                break
    
    if date_col:
        df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
        df_clean['MONTH'] = df_clean[date_col].dt.month
        df_clean['DAY_OF_WEEK'] = df_clean[date_col].dt.dayofweek
        df_clean['YEAR'] = df_clean[date_col].dt.year
    
    # Fill missing delay values with 0
    delay_cols = ['DEP_DELAY', 'ARR_DELAY', 'CARRIER_DELAY', 'WEATHER_DELAY', 
                  'NAS_DELAY', 'SECURITY_DELAY', 'LATE_AIRCRAFT_DELAY']
    
    for col in delay_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(0)
    
    # Create delay flag (delayed if arrival delay > 15 minutes)
    if 'ARR_DELAY' in df_clean.columns:
        df_clean['IS_DELAYED'] = (df_clean['ARR_DELAY'] > 15).astype(int)
    
    print(f"Cleaned: {len(df_clean)} rows")
    return df_clean


def get_delay_stats(df):
    """Get overall delay statistics."""
    stats = {}
    
    if 'ARR_DELAY' in df.columns:
        stats['total_flights'] = len(df)
        stats['delayed_flights'] = len(df[df['ARR_DELAY'] > 15])
        stats['delay_rate'] = stats['delayed_flights'] / stats['total_flights'] * 100
        stats['avg_delay'] = df['ARR_DELAY'].mean()
        stats['max_delay'] = df['ARR_DELAY'].max()
    
    if 'CANCELLED' in df.columns:
        stats['cancelled_flights'] = df['CANCELLED'].sum()
        stats['cancellation_rate'] = stats['cancelled_flights'] / stats['total_flights'] * 100
    
    return stats


def get_carrier_stats(df):
    """Get statistics by carrier."""
    if 'OP_CARRIER' not in df.columns or 'ARR_DELAY' not in df.columns:
        return None
    
    carrier_stats = df.groupby('OP_CARRIER').agg({
        'ARR_DELAY': ['count', 'mean', 'std'],
        'IS_DELAYED': 'mean' if 'IS_DELAYED' in df.columns else 'count'
    }).round(2)
    
    carrier_stats.columns = ['total_flights', 'avg_delay', 'std_delay', 'delay_rate']
    carrier_stats['delay_rate'] = carrier_stats['delay_rate'] * 100
    carrier_stats = carrier_stats.sort_values('total_flights', ascending=False)
    
    return carrier_stats


def get_airport_stats(df, airport_col='ORIGIN'):
    """Get statistics by airport."""
    if airport_col not in df.columns or 'ARR_DELAY' not in df.columns:
        return None
    
    airport_stats = df.groupby(airport_col).agg({
        'ARR_DELAY': ['count', 'mean']
    }).round(2)
    
    airport_stats.columns = ['total_flights', 'avg_delay']
    airport_stats = airport_stats.sort_values('total_flights', ascending=False)
    
    return airport_stats


def get_delay_causes(df):
    """Get delay causes breakdown."""
    delay_cols = ['CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 
                  'SECURITY_DELAY', 'LATE_AIRCRAFT_DELAY']
    
    causes = {}
    for col in delay_cols:
        if col in df.columns:
            # Count flights with this type of delay
            delayed = df[df[col] > 0]
            causes[col.replace('_DELAY', '')] = {
                'count': len(delayed),
                'total_minutes': delayed[col].sum(),
                'avg_minutes': delayed[col].mean()
            }
    
    return causes


def get_monthly_stats(df):
    """Get statistics by month."""
    if 'MONTH' not in df.columns or 'ARR_DELAY' not in df.columns:
        return None
    
    monthly = df.groupby('MONTH').agg({
        'ARR_DELAY': ['count', 'mean'],
        'IS_DELAYED': 'mean' if 'IS_DELAYED' in df.columns else 'count'
    }).round(2)
    
    monthly.columns = ['total_flights', 'avg_delay', 'delay_rate']
    monthly['delay_rate'] = monthly['delay_rate'] * 100
    
    return monthly


def get_yearly_stats(df):
    """Get statistics by year."""
    if 'YEAR' not in df.columns or 'ARR_DELAY' not in df.columns:
        return None
    
    yearly = df.groupby('YEAR').agg({
        'ARR_DELAY': ['count', 'mean'],
        'IS_DELAYED': 'mean' if 'IS_DELAYED' in df.columns else 'count'
    }).round(2)
    
    yearly.columns = ['total_flights', 'avg_delay', 'delay_rate']
    yearly['delay_rate'] = yearly['delay_rate'] * 100
    
    return yearly


def export_for_tableau(df, output_dir=None):
    """Export summary data for Tableau."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "tableau"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Yearly summary
    yearly = get_yearly_stats(df)
    if yearly is not None:
        yearly.to_csv(output_dir / "yearly_summary_tableau.csv")
        print("Exported yearly summary")
    
    # Monthly summary
    monthly = get_monthly_stats(df)
    if monthly is not None:
        monthly.to_csv(output_dir / "monthly_summary_tableau.csv")
        print("Exported monthly summary")
    
    # Carrier summary
    carrier = get_carrier_stats(df)
    if carrier is not None:
        carrier.to_csv(output_dir / "carrier_summary_tableau.csv")
        print("Exported carrier summary")
    
    # Origin airport summary
    origin_stats = get_airport_stats(df, 'ORIGIN')
    if origin_stats is not None:
        origin_stats.head(50).to_csv(output_dir / "origin_airports_tableau.csv")
        print("Exported origin airports")
    
    # Destination airport summary
    dest_stats = get_airport_stats(df, 'DEST')
    if dest_stats is not None:
        dest_stats.head(50).to_csv(output_dir / "dest_airports_tableau.csv")
        print("Exported destination airports")
    
    print(f"All exports saved to {output_dir}")


if __name__ == "__main__":
    df = load_flight_data(sample_size=100000)
    df_clean = clean_flight_data(df)
    
    stats = get_delay_stats(df_clean)
    print(f"\nStats: {stats}")
