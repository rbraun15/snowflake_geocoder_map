# Configuration Template Reference

This document provides a quick copy-paste reference for all configuration sections in `donor_map_app.py`.

---

## Database Configuration

```python
DATABASE_NAME = "demo_geocode"
SCHEMA_NAME = "address_processing"
VIEW_NAME = "geocoded_donors_map_view"
```

---

## Application Settings

```python
APP_TITLE = "🎓 Donor Analytics Map"
PAGE_ICON = "🗺️"
DEFAULT_ZIP_CODE = "29650"

DEFAULT_POINT_SIZE = 5
MIN_POINT_SIZE = 1
MAX_POINT_SIZE = 10
DEFAULT_H3_RESOLUTION = 8
```

---

## Filter Configuration Template

```python
FILTER_CONFIG = {
    'filter_name': {
        'enabled': True,              # True/False
        'label': 'Display Label',     # String shown in UI
        'column': 'DATABASE_COLUMN',  # Exact column name from view
        'type': 'multiselect',        # 'multiselect', 'slider', 'date_slider'
        'allow_select_all': True      # For multiselect only
    }
}
```

### Example: Adding a New Multiselect Filter

```python
'donor_status': {
    'enabled': True,
    'label': 'Donor Status',
    'column': 'STATUS',
    'type': 'multiselect',
    'allow_select_all': True
}
```

### Example: Adding a Numeric Slider Filter

```python
'donation_count': {
    'enabled': True,
    'label': 'Number of Donations',
    'column': 'DONATION_COUNT',
    'type': 'slider'
}
```

---

## Tooltip Configuration Templates

### Point Tooltips

```python
POINT_TOOLTIP_FIELDS = [
    {'label': 'Display Name', 'column': 'DB_COLUMN'},                                    # Plain text
    {'label': 'Currency Field', 'column': 'DB_COLUMN', 'format': 'currency'},           # $X,XXX.XX
    {'label': 'Number Field', 'column': 'DB_COLUMN', 'format': 'number'},               # X,XXX
    {'label': 'Date Field', 'column': 'DB_COLUMN', 'format': 'date'}                    # YYYY-MM-DD
]
```

### Hexagon Tooltips

```python
HEX_TOOLTIP_FIELDS = [
    {'label': 'Aggregated Count', 'column': 'aggregated_column_name', 'format': 'number'},
    {'label': 'Aggregated Sum', 'column': 'aggregated_column_name', 'format': 'currency'}
]
```

**Note**: Hexagon columns must be created in the aggregation logic (see Advanced section below).

---

## Dataframe Configuration Template

```python
DATAFRAME_COLUMNS = [
    {'label': 'Column Header', 'column': 'DB_COLUMN'},                          # Plain text
    {'label': 'Dollar Amount', 'column': 'DB_COLUMN', 'format': 'currency'},   # $X,XXX.XX
    {'label': 'Count', 'column': 'DB_COLUMN', 'format': 'number'},              # X,XXX
    {'label': 'Date', 'column': 'DB_COLUMN', 'format': 'date'}                  # YYYY-MM-DD
]
```

---

## Color Configuration Template

```python
# Format: [Red, Green, Blue, Alpha] where each value is 0-255
QUARTILE_COLORS = {
    'Q1_HIGH': [0, 255, 0, 200],      # Top 25% - Green
    'Q2': [65, 105, 225, 200],        # 50-75% - Blue
    'Q3': [255, 165, 0, 200],         # 25-50% - Orange
    'Q4_LOW': [255, 0, 0, 200]        # Bottom 25% - Red
}
```

### Color Scheme Examples

**Red to Blue Gradient**:
```python
'Q1_HIGH': [0, 0, 255, 200],      # Blue
'Q2': [0, 128, 255, 200],         # Light blue
'Q3': [255, 128, 0, 200],         # Orange
'Q4_LOW': [255, 0, 0, 200]        # Red
```

**Monochrome Gradient (Dark to Light Green)**:
```python
'Q1_HIGH': [0, 100, 0, 200],      # Dark green
'Q2': [0, 150, 0, 200],           # Medium green
'Q3': [0, 200, 0, 200],           # Light green
'Q4_LOW': [0, 255, 0, 200]        # Bright green
```

**Purple Gradient**:
```python
'Q1_HIGH': [128, 0, 255, 200],    # Purple
'Q2': [180, 100, 200, 200],       # Light purple
'Q3': [220, 180, 230, 200],       # Lighter purple
'Q4_LOW': [255, 220, 255, 200]    # Very light purple
```

---

## Chart Configuration Template

```python
CHART_CONFIG = {
    'chart_id': {
        'enabled': True,                  # True to show, False to hide
        'title': 'Chart Title',           # Display title
        'type': 'pie'                     # 'pie', 'bar', 'line', etc.
    }
}
```

### Example: Adding a New Chart Config

```python
'donations_by_state': {
    'enabled': True,
    'title': 'Donations by State',
    'type': 'bar'
}
```

---

## Map Styles Template

```python
MAP_STYLES = {
    "Display Name": "map-style-url",
}
```

### Common Map Styles

```python
MAP_STYLES = {
    "Light": "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    "Dark": "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    "Detailed": "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
    "No Labels": "https://basemaps.cartocdn.com/gl/basic-gl-style/style.json",
}
```

---

## Advanced: H3 Hexagon Aggregation Template

To add custom aggregated fields to H3 hexagons, modify the `create_h3_hexagon_map()` function:

```python
# Around line 320 in donor_map_app.py
h3_agg = df_filtered.groupby(h3_column).agg({
    'RECORD_ID': 'count',                  # Counts records
    'DONATION_AMOUNT': 'sum',              # Sums amounts
    'YOUR_COLUMN': 'mean',                 # Average
    'YOUR_COLUMN2': 'max',                 # Maximum
    'LAT': 'mean',
    'LONG': 'mean'
}).round(2)

# Update column names to match
h3_agg.columns = ['donor_count', 'total_donations', 'avg_metric', 'max_metric', 'center_lat', 'center_lon']
```

**Available Aggregation Functions**:
- `'count'` - Count of records
- `'sum'` - Sum of values
- `'mean'` - Average value
- `'median'` - Median value
- `'min'` - Minimum value
- `'max'` - Maximum value
- `'std'` - Standard deviation

---

## Code Implementation Templates

### Adding a Multiselect Filter (Full Implementation)

**Step 1**: Add to configuration section:

```python
'new_filter': {
    'enabled': True,
    'label': 'My Filter',
    'column': 'MY_COLUMN',
    'type': 'multiselect',
    'allow_select_all': True
}
```

**Step 2**: Add filter logic in main() function:

```python
if FILTER_CONFIG['new_filter']['enabled']:
    with filter_cols[col_idx % 4]:
        options = sorted(donor_data[FILTER_CONFIG['new_filter']['column']].dropna().unique().tolist())
        selected = st.multiselect(
            FILTER_CONFIG['new_filter']['label'],
            options=options,
            default=options
        )
        
        if selected:
            filtered_data = filtered_data[filtered_data[FILTER_CONFIG['new_filter']['column']].isin(selected)]
    col_idx += 1
```

---

### Adding a Slider Filter (Full Implementation)

**Step 1**: Add to configuration section:

```python
'new_slider': {
    'enabled': True,
    'label': 'My Slider',
    'column': 'MY_NUMERIC_COLUMN',
    'type': 'slider'
}
```

**Step 2**: Add filter logic in main() function:

```python
if FILTER_CONFIG['new_slider']['enabled']:
    with filter_cols2[0]:  # Use appropriate column position
        min_val = float(donor_data[FILTER_CONFIG['new_slider']['column']].min())
        max_val = float(donor_data[FILTER_CONFIG['new_slider']['column']].max())
        
        slider_range = st.slider(
            FILTER_CONFIG['new_slider']['label'],
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        )
        
        filtered_data = filtered_data[
            (filtered_data[FILTER_CONFIG['new_slider']['column']] >= slider_range[0]) &
            (filtered_data[FILTER_CONFIG['new_slider']['column']] <= slider_range[1])
        ]
```

---

### Adding a Chart (Full Implementation)

**Step 1**: Add to chart configuration:

```python
'my_new_chart': {
    'enabled': True,
    'title': 'My Custom Analysis',
    'type': 'bar'
}
```

**Step 2**: Add chart code in Analytics tab (tab2 section):

```python
if CHART_CONFIG['my_new_chart']['enabled']:
    # Prepare data
    chart_data = filtered_data.groupby('GROUP_COLUMN')['VALUE_COLUMN'].sum().reset_index()
    chart_data = chart_data.sort_values('VALUE_COLUMN', ascending=False)
    
    # Create chart
    fig = px.bar(
        chart_data,
        x='VALUE_COLUMN',
        y='GROUP_COLUMN',
        title=CHART_CONFIG['my_new_chart']['title'],
        labels={'VALUE_COLUMN': 'Value Label', 'GROUP_COLUMN': 'Group Label'},
        orientation='h'
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

---

## View Schema Requirements

Your Snowflake view must include these columns:

### Required Columns
- `RECORD_ID` - Unique identifier
- `LAT` - Latitude (decimal)
- `LONG` - Longitude (decimal)

### Geographic Columns
- `STREET` - Street address
- `CITY` - City name
- `STATE` - State code
- `ZIP` - Zip code

### H3 Columns (for hexagon view)
- `H3_LEVEL_7` - H3 identifier at resolution 7
- `H3_LEVEL_8` - H3 identifier at resolution 8
- `H3_LEVEL_9` - H3 identifier at resolution 9

### Donor Columns
- `DONOR_NAME` - Name
- `DONOR_LEVEL` - Classification level
- `DONOR_DEPARTMENT` - Department
- `DONATION_AMOUNT` - Total donation amount
- `DONATION_COUNT` - Number of donations
- `GRADUATION_DATE` - Graduation date
- `LAST_DONATION_DATE` - Date of last donation

### Generated Columns
- `FORMATTED_ADDRESS` - Auto-generated in query (CONCAT_WS)

---

## SQL Query Template

The app uses this query to load data:

```sql
SELECT 
    *,
    CONCAT_WS(', ', STREET, CITY, STATE, ZIP) AS FORMATTED_ADDRESS
FROM {DATABASE_NAME}.{SCHEMA_NAME}.{VIEW_NAME}
WHERE LAT IS NOT NULL 
AND LONG IS NOT NULL
```

**To modify**: Edit the `load_donor_data()` function around line 167.

---

## Common Customization Scenarios

### Scenario 1: Change Color Metric from Donation Amount to Donation Count

**In `create_points_map()` (line ~310)**:
```python
quartiles = valid_df['DONATION_COUNT'].quantile([0.25, 0.50, 0.75])
donation_count = float(row.get('DONATION_COUNT', 0))
color = get_quartile_color(donation_count, quartiles)
```

**In `create_h3_hexagon_map()` (line ~335)**:
```python
quartiles = h3_agg['donor_count'].quantile([0.25, 0.50, 0.75])
```

---

### Scenario 2: Add "Select All / Deselect All" Functionality

Replace multiselect with checkboxes:

```python
col1, col2 = st.columns([1, 3])
with col1:
    select_all = st.checkbox("Select All", value=True)
with col2:
    if select_all:
        selected = st.multiselect(label, options=options, default=options)
    else:
        selected = st.multiselect(label, options=options, default=[])
```

---

### Scenario 3: Change Initial Map Zoom/Center

**In `create_points_map()` (line ~385)**:
```python
initial_view_state=pdk.ViewState(
    latitude=34.8526,      # Set specific latitude
    longitude=-82.3940,    # Set specific longitude
    zoom=12,               # Higher = closer
    pitch=0
)
```

---

### Scenario 4: Add Percentage to Tooltip

**In tooltip configuration**:
```python
POINT_TOOLTIP_FIELDS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Amount', 'column': 'DONATION_AMOUNT', 'format': 'currency'},
    {'label': 'Percent of Goal', 'column': 'PERCENT_COMPLETE', 'format': 'number'}
]
```

Then format in code:
```python
tooltip_data['percent_of_goal'] = f"{row.get('PERCENT_COMPLETE', 0):.1f}%"
```

---

**Version**: 1.0  
**Last Updated**: November 2025  
**File**: `donor_map_app.py`

