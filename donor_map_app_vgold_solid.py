"""
=================================================================================
DONOR MAP VISUALIZATION APPLICATION
=================================================================================

This Streamlit application visualizes donor data on an interactive map with 
support for both point markers and H3 hexagonal aggregation.

CONFIGURATION SECTION:
Modify the variables below to customize the application for your data source.
=================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from snowflake.snowpark.context import get_active_session
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

# =================================================================================
# CONFIGURATION SECTION - CUSTOMIZE THESE VALUES
# =================================================================================

# --- Database Configuration ---
DATABASE_NAME = "demo_geocode"
SCHEMA_NAME = "address_processing"
VIEW_NAME = "geocoded_donors_map_view"

# --- Application Settings ---
APP_TITLE = "🎓 Donor Analytics Map"
PAGE_ICON = "🗺️"
DEFAULT_ZIP_CODE = "29650"  # Default zip code filter

# --- Map Settings ---
DEFAULT_POINT_SIZE = 5
MIN_POINT_SIZE = 1
MAX_POINT_SIZE = 10
DEFAULT_H3_RESOLUTION = 8

# --- Filter Configuration ---
# Add or remove fields here to customize filters
FILTER_CONFIG = {
    'zip_code': {
        'enabled': True,
        'label': 'Zip Code',
        'column': 'ZIP',
        'type': 'multiselect',
        'allow_select_all': True
    },
    'state': {
        'enabled': True,
        'label': 'State',
        'column': 'STATE',
        'type': 'multiselect',
        'allow_select_all': True
    },
    'donor_level': {
        'enabled': True,
        'label': 'Donor Level',
        'column': 'DONOR_LEVEL',
        'type': 'multiselect',
        'allow_select_all': True
    },
    'donor_department': {
        'enabled': True,
        'label': 'Donor Department',
        'column': 'DONOR_DEPARTMENT',
        'type': 'multiselect',
        'allow_select_all': True
    },
    'donor_name': {
        'enabled': True,
        'label': 'Donor Name',
        'column': 'DONOR_NAME',
        'type': 'multiselect',
        'allow_select_all': True
    },
    'donation_amount': {
        'enabled': True,
        'label': 'Donation Amount',
        'column': 'DONATION_AMOUNT',
        'type': 'slider'
    },
    'graduation_date': {
        'enabled': True,
        'label': 'Graduation Date',
        'column': 'GRADUATION_DATE',
        'type': 'date_slider'
    },
    'last_donation_date': {
        'enabled': True,
        'label': 'Last Donation Date',
        'column': 'LAST_DONATION_DATE',
        'type': 'date_slider'
    }
}

# --- Tooltip Configuration ---
# Customize what appears in map tooltips
POINT_TOOLTIP_FIELDS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Donor Level', 'column': 'DONOR_LEVEL'},
    {'label': 'Donation Amount', 'column': 'DONATION_AMOUNT', 'format': 'currency'}
]

HEX_TOOLTIP_FIELDS = [
    {'label': 'Number of Donors', 'column': 'donor_count', 'format': 'number'},
    {'label': 'Sum Donation Amount', 'column': 'total_donations', 'format': 'currency'}
]

# --- Dataframe Configuration ---
# Customize which columns appear in the data table
DATAFRAME_COLUMNS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Address', 'column': 'FORMATTED_ADDRESS'},
    {'label': 'Donor Level', 'column': 'DONOR_LEVEL'},
    {'label': 'Sum of Donations', 'column': 'DONATION_AMOUNT', 'format': 'currency'},
    {'label': 'Graduation Date', 'column': 'GRADUATION_DATE', 'format': 'date'}
]

# --- Color Quartile Configuration ---
# Colors for quartile-based coloring (highest to lowest)
QUARTILE_COLORS = {
    'Q1_HIGH': [0, 255, 0, 200],      # Green - Top 25%
    'Q2': [65, 105, 225, 200],        # Blue - 50-75th percentile
    'Q3': [255, 165, 0, 200],         # Orange - 25-50th percentile
    'Q4_LOW': [255, 0, 0, 200]        # Red - Bottom 25%
}

# --- Chart Configuration ---
# Add or modify chart configurations
CHART_CONFIG = {
    'donations_by_level': {
        'enabled': True,
        'title': 'Donations by Donor Level',
        'type': 'pie'
    },
    'donations_by_department': {
        'enabled': True,
        'title': 'Donations by Department',
        'type': 'bar'
    },
    'donations_over_time': {
        'enabled': True,
        'title': 'Donations Over Time',
        'type': 'line'
    },
    'donor_level_distribution': {
        'enabled': True,
        'title': 'Donor Level Distribution',
        'type': 'bar'
    },
    'top_donors': {
        'enabled': True,
        'title': 'Top 10 Donors',
        'type': 'bar'
    },
    'geographic_distribution': {
        'enabled': True,
        'title': 'Donations by Zip Code',
        'type': 'bar'
    }
}

# --- Map Styles ---
MAP_STYLES = {
    "CARTO Light (Minimalist)": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    "CARTO Dark Matter": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    "CARTO Voyager (Full Detail)": "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
    "CARTO Positron No Labels": "https://basemaps.cartocdn.com/gl/basic-gl-style/style.json",
}

# =================================================================================
# END CONFIGURATION SECTION
# =================================================================================


# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to make filter buttons smaller
st.markdown("""
    <style>
    /* Make filter control buttons much smaller and less prominent */
    div.stButton > button {
        padding: 0.15rem 0.4rem !important;
        font-size: 0.65rem !important;
        height: auto !important;
        min-height: 1.2rem !important;
        line-height: 1.1 !important;
        font-weight: 400 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Get Snowflake session
@st.cache_resource
def get_snowflake_session():
    """Get the active Snowflake session"""
    return get_active_session()

session = get_snowflake_session()

# Load donor data
@st.cache_data(ttl=600)
def load_donor_data():
    """Load donor data from Snowflake view"""
    query = f"""
        SELECT 
            *,
            CONCAT_WS(', ', STREET, CITY, STATE, ZIP) AS FORMATTED_ADDRESS
        FROM {DATABASE_NAME}.{SCHEMA_NAME}.{VIEW_NAME}
        WHERE LAT IS NOT NULL 
        AND LONG IS NOT NULL
    """
    df = session.sql(query).to_pandas()
    
    # Convert date columns to datetime
    date_columns = ['GRADUATION_DATE', 'LAST_DONATION_DATE', 'GEOCODED_TIMESTAMP']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Truncate ZIP codes to first 5 digits
    if 'ZIP' in df.columns:
        df['ZIP'] = df['ZIP'].astype(str).str[:5]
    
    return df

# Helper function to get quartile color
def get_quartile_color(value, quartiles):
    """Assign color based on quartile (higher values = better color)"""
    if pd.isna(value) or value == 0:
        return [128, 128, 128, 200]  # Gray for missing/zero
    
    if value >= quartiles[0.75]:
        return QUARTILE_COLORS['Q1_HIGH']  # Top 25% - Green
    elif value >= quartiles[0.50]:
        return QUARTILE_COLORS['Q2']  # 50-75% - Blue
    elif value >= quartiles[0.25]:
        return QUARTILE_COLORS['Q3']  # 25-50% - Orange
    else:
        return QUARTILE_COLORS['Q4_LOW']  # Bottom 25% - Red

# Format value based on type
def format_value(value, fmt_type=None):
    """Format values for display"""
    if pd.isna(value):
        return "N/A"
    
    if fmt_type == 'currency':
        return f"${int(value):,}"  # No cents, dollars only
    elif fmt_type == 'number':
        return f"{int(value):,}"
    elif fmt_type == 'date':
        if isinstance(value, (datetime, date)):
            return value.strftime('%Y-%m-%d')
        return str(value)
    else:
        return str(value)

# Helper function for multiselect with select all/deselect all
def multiselect_with_select_all(label, options, default, key=None):
    """Create a multiselect with All / None buttons"""
    
    # Use a unique key for this filter's multiselect widget
    ms_key = f"ms_{key}" if key else f"ms_{label.lower().replace(' ', '_')}"
    
    # Initialize session state with default values if not exists
    if ms_key not in st.session_state:
        st.session_state[ms_key] = list(default) if isinstance(default, list) else default
    
    # Label on top
    st.write(f"**{label}**")
    
    # Buttons below label in two columns
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("All", key=f"btn_all_{key}", use_container_width=True):
            # Update the multiselect's session state directly
            st.session_state[ms_key] = list(options)
    
    with btn_col2:
        if st.button("None", key=f"btn_none_{key}", use_container_width=True):
            # Update the multiselect's session state directly
            st.session_state[ms_key] = []
    
    # Multiselect - key parameter automatically manages state via session_state
    # Do NOT use default parameter when using key - they conflict!
    selected = st.multiselect(
        label,
        options=options,
        key=ms_key,
        label_visibility="collapsed"
    )
    
    return selected

# Create points map
def create_points_map(df, point_size_multiplier, map_url):
    """Create points map with quartile-based coloring"""
    valid_df = df.dropna(subset=['LAT', 'LONG']).copy()
    
    if valid_df.empty:
        st.error("❌ No valid coordinates available")
        return None
    
    st.info(f"📍 Showing {len(valid_df)} donors")
    
    # Calculate quartiles for color coding
    quartiles = valid_df['DONATION_AMOUNT'].quantile([0.25, 0.50, 0.75])
    
    data = []
    for _, row in valid_df.iterrows():
        donation_amount = float(row.get('DONATION_AMOUNT', 0))
        color = get_quartile_color(donation_amount, quartiles)
        
        # Build tooltip data
        tooltip_data = {
            'lat': float(row['LAT']),
            'lon': float(row['LONG']),
            'color': color,
            'radius': 20
        }
        
        # Add configured tooltip fields
        for field in POINT_TOOLTIP_FIELDS:
            key = field['label'].lower().replace(' ', '_')
            value = row.get(field['column'], 'N/A')
            tooltip_data[key] = format_value(value, field.get('format'))
        
        data.append(tooltip_data)
    
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=point_size_multiplier * 100,
        radius_min_pixels=3,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position=['lon', 'lat'],
        get_radius='radius',
        get_fill_color='color',
        get_line_color=[0, 0, 0],
    )
    
    center_lat = valid_df['LAT'].mean()
    center_lon = valid_df['LONG'].mean()
    
    # Build tooltip HTML dynamically
    tooltip_html = ""
    for field in POINT_TOOLTIP_FIELDS:
        key = field['label'].lower().replace(' ', '_')
        tooltip_html += f"<b>{field['label']}:</b> {{{key}}}<br/>"
    
    tooltip = {
        "html": tooltip_html.rstrip("<br/>"),
        "style": {
            "backgroundColor": 'rgba(31, 78, 121, 0.9)',
            "color": "white",
            "fontSize": "14px",
            "padding": "10px",
            "borderRadius": "5px"
        }
    }
    
    deck = pdk.Deck(
        map_style=map_url,
        layers=[scatter_layer],
        tooltip=tooltip,
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=10,
            pitch=0
        ),
    )
    
    return deck

# Create H3 hexagon map
def create_h3_hexagon_map(df, resolution, map_url):
    """Create H3 hexagon map with quartile-based coloring"""
    h3_column = f'H3_LEVEL_{resolution}'
    
    if h3_column not in df.columns:
        st.error(f"H3 column {h3_column} not found")
        return None
    
    df_filtered = df[df[h3_column].notna()].copy()
    
    if df_filtered.empty:
        st.error(f"❌ No H3 data for resolution {resolution}")
        return None
    
    # Aggregate by H3 cell
    h3_agg = df_filtered.groupby(h3_column).agg({
        'RECORD_ID': 'count',
        'DONATION_AMOUNT': 'sum',
        'LAT': 'mean',
        'LONG': 'mean'
    }).round(2)
    
    h3_agg.columns = ['donor_count', 'total_donations', 'center_lat', 'center_lon']
    h3_agg = h3_agg.reset_index()
    
    if h3_agg.empty:
        st.error("❌ No aggregated data")
        return None
    
    st.success(f"✅ {len(h3_agg)} H3 hexagons")
    
    # Calculate quartiles for color coding
    quartiles = h3_agg['total_donations'].quantile([0.25, 0.50, 0.75])
    
    # Assign colors based on quartiles
    h3_agg['color'] = h3_agg['total_donations'].apply(
        lambda x: get_quartile_color(x, quartiles)
    )
    
    # Format tooltip fields
    for field in HEX_TOOLTIP_FIELDS:
        col = field['column']
        if col in h3_agg.columns:
            key = f"{col}_formatted"
            h3_agg[key] = h3_agg[col].apply(lambda x: format_value(x, field.get('format')))
    
    avg_latitude = h3_agg['center_lat'].mean()
    avg_longitude = h3_agg['center_lon'].mean()
    
    # Build tooltip HTML dynamically
    tooltip_html = f"<b>H3 Cell:</b> {{{h3_column}}}<br/>"
    for field in HEX_TOOLTIP_FIELDS:
        key = f"{field['column']}_formatted"
        tooltip_html += f"<b>{field['label']}:</b> {{{key}}}<br/>"
    
    tooltip = {
        "html": tooltip_html.rstrip("<br/>"),
        "style": {
            "backgroundColor": 'rgba(255, 87, 0, 0.9)',
            "color": "white",
            "fontSize": "14px",
            "padding": "10px",
            "borderRadius": "5px"
        }
    }
    
    h3_layer = pdk.Layer(
        "H3HexagonLayer",
        h3_agg,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        opacity=0.7,
        get_hexagon=h3_column,
        get_fill_color="color",
        get_line_color=[255, 255, 255],
        line_width_min_pixels=1,
    )

    deck = pdk.Deck(
        map_style=map_url,
        layers=[h3_layer],
        tooltip=tooltip,
        initial_view_state=pdk.ViewState(
            latitude=avg_latitude,
            longitude=avg_longitude,
            zoom=9,
            pitch=0
        ),
    )
    
    return deck

# Main application
def main():
    # Title
    st.markdown(f'<h1 style="font-size: 3rem; color: #1f4e79; text-align: center; font-weight: bold; margin-bottom: 1rem;">{APP_TITLE}</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading donor data..."):
        donor_data = load_donor_data()
        
        if donor_data.empty:
            st.error("No donor data found")
            st.stop()
    
    # =================================================================================
    # FILTERS SECTION (Above Map)
    # =================================================================================
    st.markdown("### 🔍 Filters")
    
    filter_cols = st.columns(5)
    filtered_data = donor_data.copy()
    
    # Dynamic filter creation based on configuration
    col_idx = 0
    
    # Zip Code filter (with default)
    if FILTER_CONFIG['zip_code']['enabled']:
        with filter_cols[col_idx % 5]:
            zip_options = sorted(donor_data[FILTER_CONFIG['zip_code']['column']].dropna().unique().tolist())
            if DEFAULT_ZIP_CODE in zip_options:
                default_zips = [DEFAULT_ZIP_CODE]
            else:
                default_zips = zip_options
            
            selected_zips = multiselect_with_select_all(
                FILTER_CONFIG['zip_code']['label'],
                options=zip_options,
                default=default_zips,
                key='zip_code'
            )
            
            if selected_zips:
                filtered_data = filtered_data[filtered_data[FILTER_CONFIG['zip_code']['column']].isin(selected_zips)]
        col_idx += 1
    
    # State filter
    if FILTER_CONFIG['state']['enabled']:
        with filter_cols[col_idx % 5]:
            state_options = sorted(donor_data[FILTER_CONFIG['state']['column']].dropna().unique().tolist())
            selected_states = multiselect_with_select_all(
                FILTER_CONFIG['state']['label'],
                options=state_options,
                default=state_options,
                key='state'
            )
            
            if selected_states:
                filtered_data = filtered_data[filtered_data[FILTER_CONFIG['state']['column']].isin(selected_states)]
        col_idx += 1
    
    # Donor Level filter
    if FILTER_CONFIG['donor_level']['enabled']:
        with filter_cols[col_idx % 5]:
            level_options = sorted(donor_data[FILTER_CONFIG['donor_level']['column']].dropna().unique().tolist())
            selected_levels = multiselect_with_select_all(
                FILTER_CONFIG['donor_level']['label'],
                options=level_options,
                default=level_options,
                key='donor_level'
            )
            
            if selected_levels:
                filtered_data = filtered_data[filtered_data[FILTER_CONFIG['donor_level']['column']].isin(selected_levels)]
        col_idx += 1
    
    # Donor Department filter
    if FILTER_CONFIG['donor_department']['enabled']:
        with filter_cols[col_idx % 5]:
            dept_options = sorted(donor_data[FILTER_CONFIG['donor_department']['column']].dropna().unique().tolist())
            selected_depts = multiselect_with_select_all(
                FILTER_CONFIG['donor_department']['label'],
                options=dept_options,
                default=dept_options,
                key='donor_department'
            )
            
            if selected_depts:
                filtered_data = filtered_data[filtered_data[FILTER_CONFIG['donor_department']['column']].isin(selected_depts)]
        col_idx += 1
    
    # Donor Name filter
    if FILTER_CONFIG['donor_name']['enabled']:
        with filter_cols[col_idx % 5]:
            name_options = sorted(donor_data[FILTER_CONFIG['donor_name']['column']].dropna().unique().tolist())
            selected_names = multiselect_with_select_all(
                FILTER_CONFIG['donor_name']['label'],
                options=name_options,
                default=name_options,
                key='donor_name'
            )
            
            if selected_names:
                filtered_data = filtered_data[filtered_data[FILTER_CONFIG['donor_name']['column']].isin(selected_names)]
        col_idx += 1
    
    # Add spacing between filter rows
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Second row of filters
    filter_cols2 = st.columns(3)
    
    # Donation Amount slider
    if FILTER_CONFIG['donation_amount']['enabled']:
        with filter_cols2[0]:
            min_donation = int(donor_data[FILTER_CONFIG['donation_amount']['column']].min())
            max_donation = int(donor_data[FILTER_CONFIG['donation_amount']['column']].max())
            
            # Initialize slider state if not exists
            if 'donation_slider' not in st.session_state:
                st.session_state.donation_slider = (min_donation, max_donation)
            
            # Label on top
            st.write(f"**{FILTER_CONFIG['donation_amount']['label']}**")
            
            # Small reset button below label
            reset_col1, reset_col2, reset_col3 = st.columns([1, 2, 2])
            with reset_col1:
                if st.button("Reset", key="reset_donation", use_container_width=True):
                    st.session_state.donation_slider = (min_donation, max_donation)
            
            donation_range = st.slider(
                FILTER_CONFIG['donation_amount']['label'],
                min_value=min_donation,
                max_value=max_donation,
                value=st.session_state.donation_slider,
                format="$%d",
                key="donation_slider",
                label_visibility="collapsed"
            )
            
            filtered_data = filtered_data[
                (filtered_data[FILTER_CONFIG['donation_amount']['column']] >= donation_range[0]) &
                (filtered_data[FILTER_CONFIG['donation_amount']['column']] <= donation_range[1])
            ]
    
    # Graduation Date slider
    if FILTER_CONFIG['graduation_date']['enabled']:
        with filter_cols2[1]:
            grad_dates = donor_data[FILTER_CONFIG['graduation_date']['column']].dropna()
            if not grad_dates.empty:
                min_grad = grad_dates.min().date()
                max_grad = grad_dates.max().date()
                
                # Initialize slider state if not exists
                if 'grad_slider' not in st.session_state:
                    st.session_state.grad_slider = (min_grad, max_grad)
                
                # Label on top
                st.write(f"**{FILTER_CONFIG['graduation_date']['label']}**")
                
                # Small reset button below label
                reset_col1, reset_col2, reset_col3 = st.columns([1, 2, 2])
                with reset_col1:
                    if st.button("Reset", key="reset_grad", use_container_width=True):
                        st.session_state.grad_slider = (min_grad, max_grad)
                
                grad_range = st.slider(
                    FILTER_CONFIG['graduation_date']['label'],
                    min_value=min_grad,
                    max_value=max_grad,
                    value=st.session_state.grad_slider,
                    key="grad_slider",
                    label_visibility="collapsed"
                )
                
                filtered_data = filtered_data[
                    (filtered_data[FILTER_CONFIG['graduation_date']['column']].dt.date >= grad_range[0]) &
                    (filtered_data[FILTER_CONFIG['graduation_date']['column']].dt.date <= grad_range[1])
                ]
    
    # Last Donation Date slider
    if FILTER_CONFIG['last_donation_date']['enabled']:
        with filter_cols2[2]:
            last_donation_dates = donor_data[FILTER_CONFIG['last_donation_date']['column']].dropna()
            if not last_donation_dates.empty:
                min_last = last_donation_dates.min().date()
                max_last = last_donation_dates.max().date()
                
                # Initialize slider state if not exists
                if 'last_donation_slider' not in st.session_state:
                    st.session_state.last_donation_slider = (min_last, max_last)
                
                # Label on top
                st.write(f"**{FILTER_CONFIG['last_donation_date']['label']}**")
                
                # Small reset button below label
                reset_col1, reset_col2, reset_col3 = st.columns([1, 2, 2])
                with reset_col1:
                    if st.button("Reset", key="reset_last_donation", use_container_width=True):
                        st.session_state.last_donation_slider = (min_last, max_last)
                
                last_donation_range = st.slider(
                    FILTER_CONFIG['last_donation_date']['label'],
                    min_value=min_last,
                    max_value=max_last,
                    value=st.session_state.last_donation_slider,
                    key="last_donation_slider",
                    label_visibility="collapsed"
                )
                
                filtered_data = filtered_data[
                    (filtered_data[FILTER_CONFIG['last_donation_date']['column']].dt.date >= last_donation_range[0]) &
                    (filtered_data[FILTER_CONFIG['last_donation_date']['column']].dt.date <= last_donation_range[1])
                ]
    
    st.markdown("---")
    
    # =================================================================================
    # TABS: MAP VIEW & ANALYTICS
    # =================================================================================
    tab1, tab2 = st.tabs(["🗺️ Map View", "📊 Analytics & Charts"])
    
    with tab1:
        # KPIs
        st.markdown("### 📊 Key Metrics")
        kpi_cols = st.columns(5)
        
        with kpi_cols[0]:
            st.metric("Total Donors", f"{len(filtered_data):,}")
        with kpi_cols[1]:
            st.metric("Total Donations", f"${int(filtered_data['DONATION_AMOUNT'].sum()):,}")
        with kpi_cols[2]:
            st.metric("Avg Donation", f"${int(filtered_data['DONATION_AMOUNT'].mean()):,}")
        with kpi_cols[3]:
            st.metric("Max Donation", f"${int(filtered_data['DONATION_AMOUNT'].max()):,}")
        with kpi_cols[4]:
            st.metric("Unique Zip Codes", f"{filtered_data['ZIP'].nunique():,}")
        
        st.markdown("---")
        
        # Map Controls
        st.markdown("### 🗺️ Map Configuration")
        map_control_cols = st.columns([2, 2, 2, 2])
        
        with map_control_cols[0]:
            map_type = st.radio("Map Type", ["Individual Points", "H3 Hexagonal Grid"], key="map_type")
        
        with map_control_cols[1]:
            if map_type == "H3 Hexagonal Grid":
                h3_resolution = st.slider("H3 Resolution", min_value=7, max_value=9, value=DEFAULT_H3_RESOLUTION, key="h3_resolution")
            else:
                point_size = st.slider("Point Size", min_value=MIN_POINT_SIZE, max_value=MAX_POINT_SIZE, value=DEFAULT_POINT_SIZE, key="point_size")
        
        with map_control_cols[2]:
            style_name = st.selectbox("Base Map Style", options=list(MAP_STYLES.keys()), index=2)
        
        selected_map_style_url = MAP_STYLES[style_name]
        
        # Display map
        if not filtered_data.empty:
            if map_type == "H3 Hexagonal Grid":
                result = create_h3_hexagon_map(filtered_data, h3_resolution, selected_map_style_url)
            else:
                result = create_points_map(filtered_data, point_size, selected_map_style_url)
            
            if result is not None:
                st.pydeck_chart(result)
                
                # Legend
                st.markdown("#### 🎨 Color Legend (Based on Donation Amount)")
                legend_cols = st.columns(4)
                with legend_cols[0]:
                    st.markdown('<span style="color: rgb(0, 255, 0); font-size: 20px;">●</span> **Green**: Top 25% (Highest)', unsafe_allow_html=True)
                with legend_cols[1]:
                    st.markdown('<span style="color: rgb(65, 105, 225); font-size: 20px;">●</span> **Blue**: 50-75th Percentile', unsafe_allow_html=True)
                with legend_cols[2]:
                    st.markdown('<span style="color: rgb(255, 165, 0); font-size: 20px;">●</span> **Orange**: 25-50th Percentile', unsafe_allow_html=True)
                with legend_cols[3]:
                    st.markdown('<span style="color: rgb(255, 0, 0); font-size: 20px;">●</span> **Red**: Bottom 25% (Lowest)', unsafe_allow_html=True)
            else:
                st.error("❌ Unable to create map")
        else:
            st.warning("⚠️ No data to display with current filters")
        
        st.markdown("---")
        
        # =================================================================================
        # DATAFRAME (Below Map)
        # =================================================================================
        st.markdown("### 📋 Donor Data")
        
        if not filtered_data.empty:
            # Prepare display dataframe with configured columns
            display_df = filtered_data.copy()
            
            # Create display columns mapping
            display_columns = {}
            for col_config in DATAFRAME_COLUMNS:
                if col_config['column'] in display_df.columns:
                    display_columns[col_config['column']] = col_config['label']
            
            # Select and rename columns
            df_to_show = display_df[list(display_columns.keys())].rename(columns=display_columns)
            
            # Format currency and date columns
            for col_config in DATAFRAME_COLUMNS:
                label = col_config['label']
                if label in df_to_show.columns:
                    if col_config.get('format') == 'currency':
                        df_to_show[label] = df_to_show[label].apply(lambda x: format_value(x, 'currency'))
                    elif col_config.get('format') == 'date':
                        df_to_show[label] = df_to_show[label].apply(lambda x: format_value(x, 'date'))
            
            st.dataframe(df_to_show, use_container_width=True, height=400)
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                "📥 Download Full Data (CSV)",
                data=csv,
                file_name=f"donor_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data to display with current filters")
    
    with tab2:
        st.markdown("### 📊 Donor Analytics & Insights")
        
        if filtered_data.empty:
            st.warning("⚠️ No data to display with current filters")
        else:
            # Row 1: Pie and Bar charts
            chart_row1 = st.columns(2)
            
            # Chart 1: Donations by Donor Level (Pie)
            if CHART_CONFIG['donations_by_level']['enabled']:
                with chart_row1[0]:
                    level_data = filtered_data.groupby('DONOR_LEVEL')['DONATION_AMOUNT'].sum().reset_index()
                    level_data = level_data.sort_values('DONATION_AMOUNT', ascending=False)
                    
                    fig_pie = px.pie(
                        level_data,
                        values='DONATION_AMOUNT',
                        names='DONOR_LEVEL',
                        title=CHART_CONFIG['donations_by_level']['title'],
                        hole=0.3
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            # Chart 2: Donations by Department (Bar)
            if CHART_CONFIG['donations_by_department']['enabled']:
                with chart_row1[1]:
                    dept_data = filtered_data.groupby('DONOR_DEPARTMENT')['DONATION_AMOUNT'].sum().reset_index()
                    dept_data = dept_data.sort_values('DONATION_AMOUNT', ascending=True)
                    
                    fig_bar1 = px.bar(
                        dept_data,
                        x='DONATION_AMOUNT',
                        y='DONOR_DEPARTMENT',
                        orientation='h',
                        title=CHART_CONFIG['donations_by_department']['title'],
                        labels={'DONATION_AMOUNT': 'Total Donations ($)', 'DONOR_DEPARTMENT': 'Department'}
                    )
                    st.plotly_chart(fig_bar1, use_container_width=True)
            
            # Row 2: Line and Bar charts
            chart_row2 = st.columns(2)
            
            # Chart 3: Donations Over Time (Line)
            if CHART_CONFIG['donations_over_time']['enabled']:
                with chart_row2[0]:
                    time_data = filtered_data.copy()
                    time_data['YEAR_MONTH'] = time_data['LAST_DONATION_DATE'].dt.to_period('M').astype(str)
                    time_agg = time_data.groupby('YEAR_MONTH')['DONATION_AMOUNT'].sum().reset_index()
                    
                    fig_line = px.line(
                        time_agg,
                        x='YEAR_MONTH',
                        y='DONATION_AMOUNT',
                        title=CHART_CONFIG['donations_over_time']['title'],
                        labels={'YEAR_MONTH': 'Month', 'DONATION_AMOUNT': 'Total Donations ($)'},
                        markers=True
                    )
                    fig_line.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_line, use_container_width=True)
            
            # Chart 4: Donor Level Distribution (Bar)
            if CHART_CONFIG['donor_level_distribution']['enabled']:
                with chart_row2[1]:
                    level_count = filtered_data['DONOR_LEVEL'].value_counts().reset_index()
                    level_count.columns = ['DONOR_LEVEL', 'COUNT']
                    
                    fig_bar2 = px.bar(
                        level_count,
                        x='DONOR_LEVEL',
                        y='COUNT',
                        title=CHART_CONFIG['donor_level_distribution']['title'],
                        labels={'DONOR_LEVEL': 'Donor Level', 'COUNT': 'Number of Donors'},
                        color='COUNT',
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_bar2, use_container_width=True)
            
            # Row 3: Top Donors and Geographic Distribution
            chart_row3 = st.columns(2)
            
            # Chart 5: Top 10 Donors (Bar)
            if CHART_CONFIG['top_donors']['enabled']:
                with chart_row3[0]:
                    top_donors = filtered_data.nlargest(10, 'DONATION_AMOUNT')[['DONOR_NAME', 'DONATION_AMOUNT']]
                    top_donors = top_donors.sort_values('DONATION_AMOUNT', ascending=True)
                    
                    fig_top = px.bar(
                        top_donors,
                        x='DONATION_AMOUNT',
                        y='DONOR_NAME',
                        orientation='h',
                        title=CHART_CONFIG['top_donors']['title'],
                        labels={'DONATION_AMOUNT': 'Donation Amount ($)', 'DONOR_NAME': 'Donor'},
                        color='DONATION_AMOUNT',
                        color_continuous_scale='Greens'
                    )
                    st.plotly_chart(fig_top, use_container_width=True)
            
            # Chart 6: Geographic Distribution (Bar)
            if CHART_CONFIG['geographic_distribution']['enabled']:
                with chart_row3[1]:
                    zip_data = filtered_data.groupby('ZIP')['DONATION_AMOUNT'].sum().reset_index()
                    zip_data = zip_data.sort_values('DONATION_AMOUNT', ascending=False).head(10)
                    
                    fig_geo = px.bar(
                        zip_data,
                        x='ZIP',
                        y='DONATION_AMOUNT',
                        title=CHART_CONFIG['geographic_distribution']['title'] + ' (Top 10)',
                        labels={'ZIP': 'Zip Code', 'DONATION_AMOUNT': 'Total Donations ($)'},
                        color='DONATION_AMOUNT',
                        color_continuous_scale='Oranges'
                    )
                    st.plotly_chart(fig_geo, use_container_width=True)
            
            # Additional Summary Statistics
            st.markdown("---")
            st.markdown("### 📈 Summary Statistics")
            
            stats_cols = st.columns(4)
            
            with stats_cols[0]:
                st.markdown("**Donation Statistics**")
                st.write(f"• Mean: ${filtered_data['DONATION_AMOUNT'].mean():,.2f}")
                st.write(f"• Median: ${filtered_data['DONATION_AMOUNT'].median():,.2f}")
                st.write(f"• Std Dev: ${filtered_data['DONATION_AMOUNT'].std():,.2f}")
            
            with stats_cols[1]:
                st.markdown("**Donation Counts**")
                st.write(f"• Total Count: {filtered_data['DONATION_COUNT'].sum():,.0f}")
                st.write(f"• Avg per Donor: {filtered_data['DONATION_COUNT'].mean():,.1f}")
                st.write(f"• Max Count: {filtered_data['DONATION_COUNT'].max():,.0f}")
            
            with stats_cols[2]:
                st.markdown("**Geographic Coverage**")
                st.write(f"• Unique Zips: {filtered_data['ZIP'].nunique()}")
                st.write(f"• Unique Cities: {filtered_data['CITY'].nunique()}")
                st.write(f"• Unique States: {filtered_data['STATE'].nunique()}")
            
            with stats_cols[3]:
                st.markdown("**Donor Segmentation**")
                st.write(f"• Donor Levels: {filtered_data['DONOR_LEVEL'].nunique()}")
                st.write(f"• Departments: {filtered_data['DONOR_DEPARTMENT'].nunique()}")
                st.write(f"• Avg Grad Year: {filtered_data['GRADUATION_DATE'].dt.year.mean():.0f}")

if __name__ == "__main__":
    main()

