# Donor Map Visualization Application

## 📖 Overview

This Streamlit application provides an interactive map visualization of donor data with support for both individual point markers and H3 hexagonal aggregation. The application is designed to be highly customizable, allowing easy modification of filters, tooltips, data fields, and charts without deep code changes.

## 🚀 Features

- **Interactive Map Visualization**
  - Toggle between individual point markers and H3 hexagonal grid
  - Adjustable point sizes and H3 resolution levels (7, 8, 9)
  - Quartile-based color coding (Green → Blue → Orange → Red)
  - Multiple base map styles

- **Advanced Filtering**
  - Zip Code (multiselect)
  - Donor Level (multiselect)
  - Donor Department (multiselect)
  - Donor Name (multiselect)
  - Donation Amount (slider)
  - Graduation Date (date range slider)
  - Last Donation Date (date range slider)

- **Customizable Tooltips**
  - **Points**: Name, Donor Level, Donation Amount
  - **Hexagons**: Number of Donors, Sum Donation Amount

- **Data Table**
  - Displays filtered data below the map
  - Configurable columns: Name, Address, Donor Level, Sum of Donations, Graduation Date
  - CSV download functionality

- **Analytics Dashboard**
  - Multiple chart types: Pie, Bar, Line
  - Donations by Donor Level
  - Donations by Department
  - Donations Over Time
  - Donor Level Distribution
  - Top 10 Donors
  - Geographic Distribution
  - Summary Statistics

## 📊 Data Source

The application reads from the following Snowflake view:

```sql
demo_geocode.address_processing.geocoded_donors_map_view
```

### Required View Columns

- `RECORD_ID` - Unique donor identifier
- `DONOR_NAME` - Donor's name
- `DONOR_DEPARTMENT` - Department affiliation
- `DONATION_AMOUNT` - Total donation amount
- `DONATION_COUNT` - Number of donations
- `GRADUATION_DATE` - Graduation date
- `LAST_DONATION_DATE` - Date of last donation
- `DONOR_LEVEL` - Donor classification level
- `STREET`, `CITY`, `STATE`, `ZIP` - Address components
- `LAT`, `LONG` - Geographic coordinates
- `H3_LEVEL_7`, `H3_LEVEL_8`, `H3_LEVEL_9` - H3 cell identifiers

## ⚙️ Configuration Guide

All major configuration is located at the top of `donor_map_app.py` in the **CONFIGURATION SECTION**. Modify these variables to customize the application for your needs.

### 1. Database Configuration

```python
DATABASE_NAME = "demo_geocode"
SCHEMA_NAME = "address_processing"
VIEW_NAME = "geocoded_donors_map_view"
```

**To Change**: Update these values to point to your Snowflake database, schema, and view.

---

### 2. Application Settings

```python
APP_TITLE = "🎓 Donor Analytics Map"
PAGE_ICON = "🗺️"
DEFAULT_ZIP_CODE = "29650"
```

**To Change**: 
- Modify `APP_TITLE` to change the page title
- Change `PAGE_ICON` to use a different emoji
- Set `DEFAULT_ZIP_CODE` to your preferred default filter value

---

### 3. Filter Configuration

Filters are configured in the `FILTER_CONFIG` dictionary. Each filter has the following structure:

```python
'filter_name': {
    'enabled': True,           # Set to False to disable this filter
    'label': 'Display Name',   # Label shown in UI
    'column': 'COLUMN_NAME',   # Database column name
    'type': 'multiselect',     # Filter type
    'allow_select_all': True   # Allow "select all" option
}
```

**Filter Types**:
- `multiselect` - Dropdown with multiple selections
- `slider` - Numeric range slider
- `date_slider` - Date range slider

**To Add a New Filter**:

1. Add a new entry to `FILTER_CONFIG`:

```python
'new_filter': {
    'enabled': True,
    'label': 'My New Filter',
    'column': 'MY_COLUMN_NAME',
    'type': 'multiselect',
    'allow_select_all': True
}
```

2. Add the filter logic in the main application (around line 400-500):

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

### 4. Tooltip Configuration

#### Point Tooltips

Modify `POINT_TOOLTIP_FIELDS` to change what appears when hovering over points:

```python
POINT_TOOLTIP_FIELDS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Donor Level', 'column': 'DONOR_LEVEL'},
    {'label': 'Donation Amount', 'column': 'DONATION_AMOUNT', 'format': 'currency'}
]
```

**To Add a New Field**:

```python
{'label': 'Display Name', 'column': 'DB_COLUMN', 'format': 'currency'}
```

**Format Options**:
- `'currency'` - Formats as $X,XXX.XX
- `'number'` - Formats as X,XXX
- `'date'` - Formats as YYYY-MM-DD
- Omit format for plain text

#### Hexagon Tooltips

Modify `HEX_TOOLTIP_FIELDS` similarly:

```python
HEX_TOOLTIP_FIELDS = [
    {'label': 'Number of Donors', 'column': 'donor_count', 'format': 'number'},
    {'label': 'Sum Donation Amount', 'column': 'total_donations', 'format': 'currency'}
]
```

**Note**: Hexagon fields use aggregated data. Available columns are created in the `create_h3_hexagon_map` function (around line 350).

---

### 5. Dataframe Configuration

Modify `DATAFRAME_COLUMNS` to change which columns appear in the data table below the map:

```python
DATAFRAME_COLUMNS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Address', 'column': 'FORMATTED_ADDRESS'},
    {'label': 'Donor Level', 'column': 'DONOR_LEVEL'},
    {'label': 'Sum of Donations', 'column': 'DONATION_AMOUNT', 'format': 'currency'},
    {'label': 'Graduation Date', 'column': 'GRADUATION_DATE', 'format': 'date'}
]
```

**To Add/Remove Columns**: Simply add or remove entries from this list.

---

### 6. Color Configuration

The application uses quartile-based coloring. Modify `QUARTILE_COLORS` to change colors:

```python
QUARTILE_COLORS = {
    'Q1_HIGH': [0, 255, 0, 200],      # Green - Top 25%
    'Q2': [65, 105, 225, 200],        # Blue - 50-75th percentile
    'Q3': [255, 165, 0, 200],         # Orange - 25-50th percentile
    'Q4_LOW': [255, 0, 0, 200]        # Red - Bottom 25%
}
```

**Color Format**: `[Red, Green, Blue, Alpha]` where values are 0-255

**Example - Change to Purple Gradient**:
```python
'Q1_HIGH': [128, 0, 255, 200],   # Purple
'Q2': [180, 100, 200, 200],      # Light purple
'Q3': [220, 180, 230, 200],      # Lighter purple
'Q4_LOW': [255, 200, 255, 200]   # Lightest purple
```

---

### 7. Chart Configuration

Control which charts appear in the Analytics tab:

```python
CHART_CONFIG = {
    'donations_by_level': {
        'enabled': True,
        'title': 'Donations by Donor Level',
        'type': 'pie'
    },
    # ... more charts
}
```

**To Disable a Chart**: Set `'enabled': False`

**To Change Title**: Modify the `'title'` value

**To Add a New Chart**: 
1. Add configuration entry
2. Implement chart logic in the Analytics tab section (around line 700+)

---

### 8. Map Styles

Add or remove base map styles by modifying `MAP_STYLES`:

```python
MAP_STYLES = {
    "Display Name": "https://map-style-url.json",
    # ... more styles
}
```

---

## 🔧 Advanced Customization

### Changing the Color Metric

By default, colors are based on `DONATION_AMOUNT`. To change this:

1. **For Points**: Modify line ~310 in `create_points_map()`:
   ```python
   quartiles = valid_df['YOUR_METRIC_COLUMN'].quantile([0.25, 0.50, 0.75])
   ```

2. **For Hexagons**: Modify line ~335 in `create_h3_hexagon_map()`:
   ```python
   quartiles = h3_agg['YOUR_METRIC_COLUMN'].quantile([0.25, 0.50, 0.75])
   ```

### Adding Custom Aggregations to H3 Hexagons

In the `create_h3_hexagon_map()` function (around line 320), modify the aggregation:

```python
h3_agg = df_filtered.groupby(h3_column).agg({
    'RECORD_ID': 'count',
    'DONATION_AMOUNT': 'sum',
    'YOUR_NEW_COLUMN': 'mean',  # Add your aggregation
    'LAT': 'mean',
    'LONG': 'mean'
}).round(2)
```

Then update column names:
```python
h3_agg.columns = ['donor_count', 'total_donations', 'your_new_metric', 'center_lat', 'center_lon']
```

### Modifying Default View Settings

Change initial map zoom and position in the `initial_view_state` sections:

**Points** (around line 385):
```python
initial_view_state=pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=10,  # Adjust zoom level (higher = closer)
    pitch=0   # Tilt angle (0-60)
)
```

**Hexagons** (around line 465):
```python
initial_view_state=pdk.ViewState(
    latitude=avg_latitude,
    longitude=avg_longitude,
    zoom=9,   # Adjust zoom level
    pitch=0
)
```

---

## 🎨 Color Quartile Explanation

The application automatically calculates quartiles based on the donation amount:

- **🟢 Green (Q1)**: Top 25% - Highest donors (75th-100th percentile)
- **🔵 Blue (Q2)**: Upper-middle 25% (50th-75th percentile)
- **🟠 Orange (Q3)**: Lower-middle 25% (25th-50th percentile)
- **🔴 Red (Q4)**: Bottom 25% - Lowest donors (0-25th percentile)

This color scheme applies to both individual points and H3 hexagons.

---

## 🚦 Running the Application

### In Snowflake (Streamlit in Snowflake)

1. Upload `donor_map_app.py` to your Snowflake stage
2. Create a Streamlit app in Snowflake pointing to the file
3. Grant necessary permissions to access the view
4. Run the application

### Locally (Development)

```bash
# Install dependencies
pip install streamlit pandas numpy pydeck plotly snowflake-snowpark-python

# Run the app
streamlit run donor_map_app.py
```

**Note**: Local development requires Snowflake credentials configured.

---

## 📝 Common Modifications

### Change Default Filters

To change which filters are shown by default:

```python
# Set enabled to False to hide a filter
'donor_name': {
    'enabled': False,  # This filter won't appear
    # ...
}
```

### Change Default Selections

For dropdown filters, modify the logic in the main application (around line 400+):

```python
# Current: All options selected
selected_levels = st.multiselect(
    FILTER_CONFIG['donor_level']['label'],
    options=level_options,
    default=level_options  # Change this to: default=['Gold', 'Platinum']
)
```

### Add a New Chart

1. Add to `CHART_CONFIG`:
```python
'my_new_chart': {
    'enabled': True,
    'title': 'My Custom Chart',
    'type': 'bar'
}
```

2. Add chart code in the Analytics tab (around line 700+):
```python
if CHART_CONFIG['my_new_chart']['enabled']:
    # Your chart code here
    fig = px.bar(...)
    st.plotly_chart(fig, use_container_width=True)
```

---

## 🐛 Troubleshooting

### No Data Showing on Map

1. Check that your view has valid `LAT` and `LONG` values
2. Verify filter settings - try resetting all to "All"
3. Check the SQL query in `load_donor_data()` function

### H3 Hexagons Not Appearing

1. Ensure H3 columns (`H3_LEVEL_7`, `H3_LEVEL_8`, `H3_LEVEL_9`) exist in your view
2. Verify H3 values are properly populated (not NULL)
3. Check the selected H3 resolution matches available data

### Filters Not Working

1. Verify column names in `FILTER_CONFIG` match your view exactly
2. Check for NULL values in filter columns
3. Ensure data types are compatible (dates should be datetime objects)

### Charts Not Displaying

1. Check that required columns exist in the data
2. Verify there's data after filtering
3. Look for error messages in the Streamlit interface

---

## 📦 Dependencies

- `streamlit` - Web application framework
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `pydeck` - Map visualization
- `plotly` - Interactive charts
- `snowflake-snowpark-python` - Snowflake connectivity

---

## 🔒 Security Notes

- The application uses cached data (TTL: 600 seconds) for performance
- No sensitive data should be hardcoded in the configuration
- Snowflake credentials are managed by the Snowpark session

---

## 📞 Support

For questions or issues:
1. Check this README for configuration guidance
2. Review the inline comments in `donor_map_app.py`
3. Verify your data source matches the expected schema

---

## 🎯 Quick Start Checklist

- [ ] Update `DATABASE_NAME`, `SCHEMA_NAME`, `VIEW_NAME` in configuration
- [ ] Verify view contains all required columns
- [ ] Test with default settings
- [ ] Customize filters as needed
- [ ] Modify tooltips for your use case
- [ ] Adjust dataframe columns
- [ ] Enable/disable charts based on requirements
- [ ] Update `APP_TITLE` and branding
- [ ] Test all filters and map controls
- [ ] Deploy to Snowflake

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Compatibility**: Streamlit in Snowflake, Streamlit 1.28+

