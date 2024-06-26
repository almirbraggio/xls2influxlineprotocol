# xls2influxlineprotocol

## Requirements

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

1. Setup the input file (`file_path`)
2. Configure the necessary columns to import (`col_names`, `col_types` and `col_ids`)
3. Fix your data using pandas dataframes functions.
4. Organize your line protocol as: `<measurement>[,<tag_key>=<tag_value>[,<tag_key>=<tag_value>]] <field_key>=<field_value>[,<field_key>=<field_value>] [<timestamp>]`
5. Run with `python main.py` inside the venv.
6. Access your InfluxDB and import the txt file setting up the timing precision (ex. nanoseconds)

## Reference

https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html
https://docs.influxdata.com/influxdb/v2/reference/syntax/line-protocol/

## Author

Almir A. Braggio
