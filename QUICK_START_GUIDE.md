# Quick Start Guide - Donor Map Application

## 🚀 5-Minute Setup

### 1. Update Database Connection (Lines 36-38)

```python
DATABASE_NAME = "demo_geocode"          # Your database
SCHEMA_NAME = "address_processing"      # Your schema
VIEW_NAME = "geocoded_donors_map_view"  # Your view name
```

### 2. Update Application Title (Lines 40-43)

```python
APP_TITLE = "🎓 Donor Analytics Map"    # Change this
PAGE_ICON = "🗺️"                        # Change emoji
DEFAULT_ZIP_CODE = "29650"              # Default filter value
```

### 3. That's it! Run the app.

---

## 🎯 Common Customizations

### Add a New Filter

**Step 1**: Add to `FILTER_CONFIG` (around line 50):

```python
'my_new_filter': {
    'enabled': True,
    'label': 'My Filter Name',
    'column': 'DATABASE_COLUMN_NAME',
    'type': 'multiselect',
    'allow_select_all': True
}
```

**Step 2**: Add filter logic (around line 430, following existing pattern):

```python
if FILTER_CONFIG['my_new_filter']['enabled']:
    with filter_cols[col_idx % 4]:
        options = sorted(donor_data[FILTER_CONFIG['my_new_filter']['column']].dropna().unique().tolist())
        selected = st.multiselect(
            FILTER_CONFIG['my_new_filter']['label'],
            options=options,
            default=options
        )
        if selected:
            filtered_data = filtered_data[filtered_data[FILTER_CONFIG['my_new_filter']['column']].isin(selected)]
    col_idx += 1
```

---

### Add Field to Point Tooltip (Lines 95-99)

```python
POINT_TOOLTIP_FIELDS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Donor Level', 'column': 'DONOR_LEVEL'},
    {'label': 'Donation Amount', 'column': 'DONATION_AMOUNT', 'format': 'currency'},
    {'label': 'New Field', 'column': 'YOUR_COLUMN', 'format': 'currency'}  # ADD THIS
]
```

**Format options**: `'currency'`, `'number'`, `'date'`, or omit for plain text

---

### Add Column to Data Table (Lines 107-113)

```python
DATAFRAME_COLUMNS = [
    {'label': 'Name', 'column': 'DONOR_NAME'},
    {'label': 'Address', 'column': 'FORMATTED_ADDRESS'},
    {'label': 'New Column', 'column': 'YOUR_COLUMN', 'format': 'currency'},  # ADD THIS
    # ... existing columns
]
```

---

### Change Color Scheme (Lines 115-120)

```python
QUARTILE_COLORS = {
    'Q1_HIGH': [0, 255, 0, 200],      # [Red, Green, Blue, Alpha] 0-255
    'Q2': [65, 105, 225, 200],
    'Q3': [255, 165, 0, 200],
    'Q4_LOW': [255, 0, 0, 200]
}
```

**Example Purple Gradient**:
```python
'Q1_HIGH': [128, 0, 255, 200],   # Purple
'Q2': [180, 100, 200, 200],
'Q3': [220, 180, 230, 200],
'Q4_LOW': [255, 200, 255, 200]
```

---

### Disable a Chart (Lines 123-145)

Set `'enabled': False` for any chart:

```python
'donations_by_level': {
    'enabled': False,  # Chart won't show
    'title': 'Donations by Donor Level',
    'type': 'pie'
}
```

---

## 🗺️ Feature Checklist

### Map Features
- ✅ Toggle between Points and H3 Hexagons
- ✅ Adjustable point size (1-10 slider)
- ✅ H3 resolution selector (7, 8, 9)
- ✅ Multiple base map styles
- ✅ Quartile-based color coding (Green/Blue/Orange/Red)
- ✅ Interactive tooltips

### Filters (All Above Map)
- ✅ Zip Code (multiselect, default: 29650)
- ✅ Donor Level (multiselect)
- ✅ Donor Department (multiselect)
- ✅ Donor Name (multiselect)
- ✅ Donation Amount (range slider)
- ✅ Graduation Date (date range slider)
- ✅ Last Donation Date (date range slider)

### Point Tooltips
- ✅ Name
- ✅ Donor Level
- ✅ Donation Amount

### Hexagon Tooltips
- ✅ Number of Donors
- ✅ Sum Donation Amount

### Data Table (Below Map)
- ✅ Name
- ✅ Address (formatted: Street, City, State, Zip)
- ✅ Donor Level
- ✅ Sum of Donations
- ✅ Graduation Date
- ✅ CSV Download

### Analytics Tab Charts
- ✅ Donations by Donor Level (Pie)
- ✅ Donations by Department (Horizontal Bar)
- ✅ Donations Over Time (Line)
- ✅ Donor Level Distribution (Bar)
- ✅ Top 10 Donors (Horizontal Bar)
- ✅ Geographic Distribution (Bar)
- ✅ Summary Statistics

---

## 📋 Configuration File Structure

```
Lines 36-43:   Database & App Settings
Lines 50-94:   Filter Configuration
Lines 95-99:   Point Tooltip Fields
Lines 101-105: Hexagon Tooltip Fields
Lines 107-113: Dataframe Columns
Lines 115-120: Color Scheme
Lines 123-145: Chart Configuration
Lines 147-153: Map Styles
```

---

## 🎨 Color Quartile System

The app automatically divides donors into 4 groups based on donation amount:

| Quartile | Color | Range | Meaning |
|----------|-------|-------|---------|
| Q1 | 🟢 Green | 75-100% | Highest donors |
| Q2 | 🔵 Blue | 50-75% | Upper-middle |
| Q3 | 🟠 Orange | 25-50% | Lower-middle |
| Q4 | 🔴 Red | 0-25% | Lowest donors |

---

## 🔍 Where to Find Things

| What You Want | Where to Look |
|---------------|---------------|
| Change database connection | Lines 36-38 |
| Change app title | Line 41 |
| Add/remove filters | Lines 50-94 + Lines 420-550 |
| Change tooltip fields | Lines 95-105 |
| Change data table columns | Lines 107-113 |
| Change colors | Lines 115-120 |
| Enable/disable charts | Lines 123-145 |
| Modify point map | Function `create_points_map()` (~line 250) |
| Modify hexagon map | Function `create_h3_hexagon_map()` (~line 315) |

---

## ⚡ Performance Tips

1. **Cache Duration**: Data is cached for 10 minutes (600 seconds)
   - Change on line 164: `@st.cache_data(ttl=600)`

2. **Limit Multiselect Options**: For very large datasets, consider limiting:
   ```python
   # Instead of showing all names (thousands), show top 100
   name_options = sorted(donor_data['DONOR_NAME'].value_counts().head(100).index.tolist())
   ```

3. **Default Filters**: Start with restrictive defaults (like single zip code) for faster loading

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No map showing | Check LAT/LONG are not NULL in view |
| Filters not working | Verify column names match exactly (case-sensitive) |
| H3 not working | Ensure H3_LEVEL_7, H3_LEVEL_8, H3_LEVEL_9 columns exist |
| Charts missing | Check `'enabled': True` in CHART_CONFIG |
| Wrong default zip | Change DEFAULT_ZIP_CODE on line 43 |

---

## 📞 Need More Detail?

See the full **README_DONOR_MAP.md** for:
- Detailed configuration explanations
- How to add custom aggregations
- Advanced customization examples
- Complete troubleshooting guide
- Schema requirements

---

**Version**: 1.0  
**File**: `donor_map_app.py`  
**Updated**: November 2025

