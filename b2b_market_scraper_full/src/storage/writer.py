import json, os
from typing import Iterable, Dict, List, Optional
import pandas as pd

def write_jsonl(path: str, items: Iterable[Dict]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')

def to_dataframe(items: List[Dict]) -> pd.DataFrame:
    return pd.DataFrame(items)

def write_tabular(df: pd.DataFrame, out_csv: Optional[str] = None, out_parquet: Optional[str] = None):
    if out_csv:
        os.makedirs(os.path.dirname(out_csv), exist_ok=True)
        df.to_csv(out_csv, index=False)
    if out_parquet:
        os.makedirs(os.path.dirname(out_parquet), exist_ok=True)
        df.to_parquet(out_parquet, index=False)
