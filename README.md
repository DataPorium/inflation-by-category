# US inflation by category in Python: which prices are rising fastest

Rank 25 US consumer price categories by how much prices rose over the past 12 months: gasoline, electricity, rent, shelter, groceries, restaurants, new and used cars, car insurance, airline fares, medical care, apparel and more. Save the ranking as CSV, draw a bar chart, and download the monthly history of any category back to 2000. The data is the official US consumer price index (CPI).

```bash
python inflation_by_category.py --history shelter,rent,food_at_home --since 2020-01
```

## Quick start

```bash
git clone https://github.com/DataPorium/inflation-by-category.git
cd inflation-by-category
pip install -r requirements.txt
export DATAPORIUM_API_KEY="YOUR_API_KEY"
python inflation_by_category.py
```

It writes to `output/`:

| File | What it holds |
|---|---|
| `latest.csv` | every category in the newest month: 12-month change (`yoy_pct`), 1-month change (`mom_pct`) and the index |
| `latest.png` | a bar chart of the 12-month changes |
| `history.csv` | with `--history`: the monthly rows of the categories you chose |

## Options

| Option | Meaning |
|---|---|
| `--history shelter,rent` | Also save the monthly history of these categories |
| `--since 2015-01` | First month of the history (default 2020-01) |
| `--out folder` | Where to write the files (default `output`) |
| `--no-chart` | Skip the chart |

Category keys: `core`, `services`, `services_less_energy`, `goods_less_food_energy`, `food`, `food_at_home`, `food_away_from_home`, `energy`, `gasoline`, `electricity`, `utility_gas`, `shelter`, `rent`, `owners_equivalent_rent`, `transportation`, `new_vehicles`, `used_cars_trucks`, `motor_vehicle_insurance`, `airline_fares`, `transportation_services`, `medical_care`, `medical_care_services`, `apparel`, `recreation`, `education_communication`.

The 12-month change uses the index that is not seasonally adjusted and the 1-month change uses the seasonally adjusted one, as in the official tables. Prices for October 2025 were not collected, so most 12-month changes for October 2026 are empty; when most changes of the newest month are empty, the script ranks the month before instead.

## How it works

One endpoint of the DataPorium API, through the [Python library](https://github.com/DataPorium/dataporium-python):

```python
from dataporium import DataPorium

dp = DataPorium()
latest = dp.inflation_categories(latest=True, sort="yoy_pct")                    # newest month, ranked
rent = dp.inflation_categories(category="shelter,rent", month_from="2020-01", order="asc")
```

## Get an API key

The script uses the [DataPorium](https://dataporium.tech) financial data API with your own API key. Sign up at [dataporium.tech](https://dataporium.tech/pricing) and subscribe to the Premium plan; the key is in your account settings. Then set it once in your terminal:

```bash
export DATAPORIUM_API_KEY="YOUR_API_KEY"     # macOS and Linux
setx DATAPORIUM_API_KEY "YOUR_API_KEY"       # Windows (open a new terminal afterwards)
```

Keep the key out of code you commit or share.

## More

- Python library used here: [dataporium-python](https://github.com/DataPorium/dataporium-python)
- JavaScript and TypeScript: [dataporium-js](https://github.com/DataPorium/dataporium-js)
- Examples in curl, R, Google Sheets and Excel: [financial-data-api](https://github.com/DataPorium/financial-data-api)
- Use the same data in Claude, ChatGPT or Cursor: [dataporium-mcp](https://github.com/DataPorium/dataporium-mcp)
- API documentation: <https://dataporium.tech/api-docs>

## License

MIT. Use of the API and its data is governed by the DataPorium [Terms of Use](https://dataporium.tech/terms-of-use). Data is for information only and is not investment advice.
