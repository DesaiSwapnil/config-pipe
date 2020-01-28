import pandas as pd
import argparse
import json



def transaction_process(input_csv, base_price_filter_low, base_price_filter_high, tax_rate, output_csv):
    data = pd.read_csv(input_csv)
    
    if base_price_filter_low:
        data = data[data["base_price"] >= base_price_filter_low]
    
    if base_price_filter_high:
        data = data[data["base_price"] < base_price_filter_high]
    
    data["final_price"] = round((1 + tax_rate) * data["base_price"],2)
    data = data.groupby(["customer_id", "transaction_id"]).agg({"date":max, "final_price":sum, "item_id":"count"} ).reset_index()
    data.columns = ["customer_id", "transaction_id", "date", "total_price", "num_items"]
    
    data.to_csv(output_csv, index=False)
    return data
    
    

def customer_process(input_csv, date_filter_start, date_filter_end, price_normalizer, output_cols, output_csv):
    data = pd.read_csv(input_csv)
    data["date"] = pd.to_datetime(data["date"])
    
    if date_filter_start:
        data = data[data["date"] >= date_filter_start]
    
    if date_filter_end:
        data = data[data["date"] < date_filter_end]
    
    data["max_price"] = data["total_price"]
    data["date_min"] = data["date"]
    data["date_max"] = data["date"]
    data = data.groupby(["customer_id"]).agg({"transaction_id": "count", "date_min": min, "date_max": max, "max_price": max, "total_price": sum , "num_items": sum}).reset_index()
    data["num_transactions"] = data["transaction_id"]
    del data["transaction_id"]
    
    if price_normalizer == "items":
        data["total_price_norm"] = data["total_price"] / data["num_items"]
        
    elif price_normalizer == "transactions":
        data["total_price_norm"] = data["total_price"] / data["num_transactions"]
    
    data = data[output_cols]
    data.to_csv(output_csv, index=False)
    return data
    



if __name__ == "__main__":
    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", dest="config",
                        help="Absolute path to configuration file.")
    args = parser.parse_args()

    # Ensure a config was passed to the script.
    if not args.config:
        print("No configuration file provided.")
        exit()
    else:
        with open(args.config, "r") as inp:
        config = json.load(inp)

    transaction_process(**config["transaction_process"])
    customer_process(**config["customer_process"])
