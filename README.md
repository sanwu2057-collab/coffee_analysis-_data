# ☕ Coffee Analysis Data Dashboard

A comprehensive analytics dashboard for coffee consumption and production data built with Streamlit and Plotly.

## Features

✅ **Real-Time KPI Cards** - Track coffee production, consumption, and market metrics  
✅ **Interactive Time-Series Analysis** - Visualize production and sales trends over time  
✅ **Hourly & Daily Demand Trends** - Identify peak consumption patterns  
✅ **Seasonal Trend Analysis** - Compare coffee demand across seasons  
✅ **Rolling Average Analytics** - 1-hour and 4-hour moving averages for trend detection  
✅ **Peak vs Off-Peak Detection** - Segment demand periods with quantile-based analysis  
✅ **Regional Insights** - Analyze coffee consumption by region or location  
✅ **Weekend vs Weekday Comparison** - Pie charts showing consumption distribution  
✅ **Operational Insights** - AI-generated recommendations for production and supply planning  
✅ **Detailed Data Table** - Export and inspect raw data  

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/sanwu2057-collab/coffee_analysis-_data.git
cd coffee_analysis-_data

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

### Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"** and connect your GitHub repository
3. Select this repository and specify `app.py` as the entry point
4. Click **Deploy**

## Usage

1. **Upload Dataset**: Use the sidebar to upload your Coffee Analysis Dataset (`.xlsx` or `.csv` format)
2. **Apply Filters**: 
   - Select date range
   - Choose seasons (Winter, Spring, Summer, Fall)
   - Filter by weekend/weekday
3. **Explore Visualizations**: Interact with charts to zoom, pan, and hover for details
4. **Download Data**: Export the detailed data table for further analysis

## Data Format

The dashboard expects data with the following columns:
- `_id`: Record identifier
- `Timestamp`: Date and time of transaction or production record
- `Production_Count`: Volume of coffee produced
- `Sales_Count`: Volume of coffee sold
- `Consumption_Count`: Volume of coffee consumed

## Dependencies

- **streamlit** - Web app framework
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **plotly** - Interactive visualizations
- **openpyxl** - Excel file support

See `requirements.txt` for specific versions.

## Project Structure

```
coffee_analysis-_data/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Key Metrics

- **Total Production** - Cumulative coffee production in selected period
- **Total Sales** - Cumulative coffee sales
- **Total Consumption** - Cumulative coffee consumption
- **Peak Demand Hour** - Hour with highest coffee sales

## Analytics Features

### Seasonal Analysis
Automatically categorizes data into:
- Winter (Dec, Jan, Feb)
- Spring (Mar, Apr, May)
- Summer (Jun, Jul, Aug)
- Fall (Sep, Oct, Nov)

### Demand Segmentation
Peak periods identified at 75th percentile of sales volume for meaningful segmentation.

### Rolling Averages
- **1-Hour Rolling Average**: Short-term trend smoothing (4 periods)
- **4-Hour Rolling Average**: Medium-term trend identification (16 periods)

## Future Enhancements

- Real-time data integration with coffee production systems
- Predictive demand forecasting with ML models
- Weather correlation analysis
- Supply chain optimization
- Multi-language support
- Mobile-responsive design
- API endpoint for programmatic access

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please create an issue in the GitHub repository.

---

**Built with ❤️ for Coffee Analytics**
