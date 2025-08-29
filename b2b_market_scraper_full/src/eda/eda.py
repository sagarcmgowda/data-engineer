import argparse, pandas as pd, numpy as np, json, os, math
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

def generate_sample(path: str, n: int = 200):
    import random
    cats = ['industrial_machinery','electronics','textiles']
    cities = ['Mumbai, Maharashtra','Delhi, Delhi','Ahmedabad, Gujarat','Shenzhen, Guangdong','Guangzhou, Guangdong','Bengaluru, Karnataka']
    titles = ['CNC Lathe Machine','Surface Grinder','Cotton Fabric','LED Smart TV','Bluetooth Headphones','Three Phase Motor']
    currency = ['INR','USD']
    rows = []
    for i in range(n):
        c = random.choice(cats)
        t = random.choice(titles)
        city = random.choice(cities)
        cur = random.choice(currency)
        pmin = random.uniform(10, 1000)
        pmax = pmin + random.uniform(0, 500)
        rows.append({
            'site': random.choice(['indiamart','alibaba']),
            'category': c,
            'title': t,
            'price_raw': None,
            'min_order': '10 Piece',
            'product_url': None,
            'company_name': f'Company {i%50}',
            'company_url': None,
            'location': city,
            'description': None,
            'price_min': round(pmin,2),
            'price_max': round(pmax,2),
            'currency': cur,
            'city': city.split(',')[0],
            'state': city.split(',')[-1].strip(),
            'price_mid': round((pmin+pmax)/2,2)
        })
    pd.DataFrame(rows).to_csv(path, index=False)

def top_n(series, n=15):
    vc = series.value_counts().head(n)
    return vc

def plot_bar(series, title, outpath):
    plt.figure()
    series.plot(kind='bar')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

def plot_hist(series, title, outpath, bins=30):
    plt.figure()
    series.dropna().plot(kind='hist', bins=bins)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

def keyword_tfidf(texts, topk=30):
    vec = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vec.fit_transform(texts.fillna(''))
    scores = np.asarray(X.mean(axis=0)).ravel()
    idx = np.argsort(scores)[::-1][:topk]
    terms = [vec.get_feature_names_out()[i] for i in idx]
    vals = scores[idx]
    return pd.Series(vals, index=terms)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=False, help='Clean CSV from normalize step')
    ap.add_argument('--report', default='outputs/eda_summary.json')
    ap.add_argument('--generate-sample', action='store_true', help='Generate a synthetic dataset if no input is provided')
    args = ap.parse_args()

    os.makedirs('outputs/figures', exist_ok=True)

    if not args.input and args.generate-sample:
        args.input = 'data/sample_clean.csv'
        os.makedirs('data', exist_ok=True)
        generate_sample(args.input, 300)

    if not args.input or not os.path.exists(args.input):
        raise SystemExit('Please pass --input <clean.csv> or use --generate-sample')

    df = pd.read_csv(args.input)

    # Summary stats
    summary = {
        'rows': int(len(df)),
        'sites': df['site'].value_counts().to_dict() if 'site' in df.columns else {},
        'categories': df['category'].value_counts().to_dict() if 'category' in df.columns else {},
        'price_min': {
            'count': int(df['price_min'].notnull().sum()),
            'mean': float(df['price_min'].mean(skipna=True)) if 'price_min' in df.columns else None
        },
        'price_max': {
            'count': int(df['price_max'].notnull().sum()),
            'mean': float(df['price_max'].mean(skipna=True)) if 'price_max' in df.columns else None
        }
    }

    # Visualizations
    if 'category' in df.columns:
        cat_top = top_n(df['category'], 10)
        plot_bar(cat_top, 'Top Categories', 'outputs/figures/top_categories.png')

    if 'price_mid' in df.columns:
        plot_hist(df['price_mid'], 'Price Mid Distribution', 'outputs/figures/price_hist.png', bins=40)

    if 'state' in df.columns:
        state_top = top_n(df['state'].dropna(), 12)
        plot_bar(state_top, 'Top Supplier States/Regions', 'outputs/figures/top_states.png')

    # Keywords from titles
    if 'title' in df.columns:
        kws = keyword_tfidf(df['title'], 30)
        plot_bar(kws, 'Top TF-IDF keywords (titles)', 'outputs/figures/top_keywords.png')

    # Save a concise report
    with open(args.report, 'w') as f:
        json.dump(summary, f, indent=2)

    print('EDA done. Charts saved in outputs/figures and summary at', args.report)
