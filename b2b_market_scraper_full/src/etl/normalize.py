import argparse, json, pandas as pd, numpy as np
from pathlib import Path
from ..utils.text import clean_whitespace, extract_price
from ..storage.writer import write_tabular

def load_jsonl(path: str):
    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return pd.DataFrame(rows)

def normalize(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    # Price parsing
    parsed = out['price_raw'].apply(lambda x: extract_price(x) if pd.notnull(x) else (None, None, None))
    out['price_min'], out['price_max'], out['currency'] = zip(*parsed)
    # Location split (city/state heuristic)
    out[['city','state']] = out['location'].fillna('').str.split(',', n=1, expand=True)
    out['city'] = out['city'].str.strip().replace({'': None})
    out['state'] = out['state'].str.strip().replace({'': None})
    # Text cleanups
    for col in ['title', 'company_name', 'min_order', 'description', 'category']:
        if col in out.columns:
            out[col] = out[col].astype(str).map(clean_whitespace)
    # Derived: price_mid
    out['price_mid'] = out[['price_min','price_max']].mean(axis=1)
    # Drop exact duplicates
    out = out.drop_duplicates(subset=['site','product_url','title','company_name'])
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', nargs='+', required=True, help='One or more JSONL files')
    ap.add_argument('--out-csv', default='data/clean.csv')
    ap.add_argument('--out-parquet', default='data/clean.parquet')
    args = ap.parse_args()

    frames = [load_jsonl(p) for p in args.inputs]
    df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    norm = normalize(df)
    write_tabular(norm, args.out_csv, args.out_parquet)
    print(f'Wrote {args.out_csv} ({len(norm)} rows) and {args.out_parquet}')
