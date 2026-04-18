"""
Smart Stock Insight Platform — Flask Backend
=============================================
Fetches REAL-TIME stock data from Yahoo Finance via the yfinance library.
Serves the static frontend and exposes a JSON API.
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import yfinance as yf
from datetime import datetime
import os

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# ─── Stock ticker mapping (NSE symbols used by Yahoo Finance) ───
STOCK_MAP = {
    "reliance": {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries Ltd.",
        "ticker_display": "NSE: RELIANCE",
        "sectors": [
            {"label": "Energy",  "cls": "energy"},
            {"label": "Telecom", "cls": "telecom"},
            {"label": "Retail",  "cls": "retail"}
        ],
        "description": "Reliance Industries Limited is an Indian multinational conglomerate, ranked among the top companies worldwide by revenue. It operates across energy, petrochemicals, textiles, natural resources, retail, and telecommunications."
    },
    "tcs": {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services",
        "ticker_display": "NSE: TCS",
        "sectors": [
            {"label": "IT Services", "cls": "it"},
            {"label": "Consulting",  "cls": "consulting"}
        ],
        "description": "Tata Consultancy Services (TCS) is a global leader in IT services, consulting, and business solutions. It is part of the Tata Group and serves clients across 150+ countries with a strong focus on innovation and digital transformation."
    },
    "infosys": {
        "symbol": "INFY.NS",
        "name": "Infosys Ltd.",
        "ticker_display": "NSE: INFY",
        "sectors": [
            {"label": "IT Services", "cls": "it"},
            {"label": "Consulting",  "cls": "consulting"}
        ],
        "description": "Infosys Limited is a global leader in next-generation digital services and consulting. Founded in Pune, it enables clients in more than 56 countries to navigate their digital transformation journey."
    },
    "hdfcbank": {
        "symbol": "HDFCBANK.NS",
        "name": "HDFC Bank Ltd.",
        "ticker_display": "NSE: HDFCBANK",
        "sectors": [
            {"label": "Banking",            "cls": "banking"},
            {"label": "Financial Services",  "cls": "finance"}
        ],
        "description": "HDFC Bank is India's largest private sector bank by assets. It offers a wide range of banking products and financial services to corporate and retail customers."
    },
    "wipro": {
        "symbol": "WIPRO.NS",
        "name": "Wipro Ltd.",
        "ticker_display": "NSE: WIPRO",
        "sectors": [
            {"label": "IT Services", "cls": "it"},
            {"label": "Consulting",  "cls": "consulting"}
        ],
        "description": "Wipro Limited is a leading global information technology, consulting and business process services company. It harnesses cognitive computing, hyper-automation, cloud, and emerging technologies."
    },
    "bajajfinance": {
        "symbol": "BAJFINANCE.NS",
        "name": "Bajaj Finance Ltd.",
        "ticker_display": "NSE: BAJFINANCE",
        "sectors": [
            {"label": "NBFC",            "cls": "finance"},
            {"label": "Consumer Lending", "cls": "lending"}
        ],
        "description": "Bajaj Finance is India's largest non-banking financial company (NBFC) by AUM. It provides consumer finance, SME finance, commercial lending, and wealth management services."
    },
    "hul": {
        "symbol": "HINDUNILVR.NS",
        "name": "Hindustan Unilever Ltd.",
        "ticker_display": "NSE: HINDUNILVR",
        "sectors": [
            {"label": "FMCG",           "cls": "fmcg"},
            {"label": "Consumer Goods",  "cls": "retail"}
        ],
        "description": "Hindustan Unilever Limited is India's largest FMCG company with a heritage of over 90 years. Its portfolio includes brands like Surf Excel, Dove, Lux, Lifebuoy, and Kwality Wall's."
    },
    "itc": {
        "symbol": "ITC.NS",
        "name": "ITC Ltd.",
        "ticker_display": "NSE: ITC",
        "sectors": [
            {"label": "FMCG",   "cls": "fmcg"},
            {"label": "Hotels",  "cls": "hospitality"},
            {"label": "Agri",    "cls": "agri"}
        ],
        "description": "ITC is a diversified conglomerate with businesses spanning FMCG, hotels, paperboards, packaging, agri-business, and information technology."
    },
    "adanient": {
        "symbol": "ADANIENT.NS",
        "name": "Adani Enterprises Ltd.",
        "ticker_display": "NSE: ADANIENT",
        "sectors": [
            {"label": "Infrastructure", "cls": "infra"},
            {"label": "Energy",         "cls": "energy"},
            {"label": "Mining",          "cls": "mining"}
        ],
        "description": "Adani Enterprises is the flagship company of the Adani Group, one of India's largest conglomerates. It operates across mining, solar manufacturing, airports, roads, data centers, and new energy."
    },
    "sbi": {
        "symbol": "SBIN.NS",
        "name": "State Bank of India",
        "ticker_display": "NSE: SBIN",
        "sectors": [
            {"label": "Banking",       "cls": "banking"},
            {"label": "Public Sector", "cls": "psu"}
        ],
        "description": "State Bank of India is India's largest public sector bank and one of the world's largest banks by assets. With over 22,000 branches and 65,000+ ATMs, SBI serves millions of customers."
    },
    "icicibank": {
        "symbol": "ICICIBANK.NS",
        "name": "ICICI Bank Ltd.",
        "ticker_display": "NSE: ICICIBANK",
        "sectors": [
            {"label": "Banking",           "cls": "banking"},
            {"label": "Financial Services", "cls": "finance"}
        ],
        "description": "ICICI Bank is India's second-largest private sector bank by assets. It offers a wide range of banking and financial services to retail, SME, and corporate customers across India and globally."
    },
    "axisbank": {
        "symbol": "AXISBANK.NS",
        "name": "Axis Bank Ltd.",
        "ticker_display": "NSE: AXISBANK",
        "sectors": [
            {"label": "Banking",           "cls": "banking"},
            {"label": "Financial Services", "cls": "finance"}
        ],
        "description": "Axis Bank is the third-largest private sector bank in India. It offers a spectrum of financial services to large and mid-size corporates, MSME, agriculture, and retail businesses."
    },
    "kotakbank": {
        "symbol": "KOTAKBANK.NS",
        "name": "Kotak Mahindra Bank",
        "ticker_display": "NSE: KOTAKBANK",
        "sectors": [
            {"label": "Banking",           "cls": "banking"},
            {"label": "Financial Services", "cls": "finance"}
        ],
        "description": "Kotak Mahindra Bank is a leading private sector bank in India offering a full suite of financial services including retail banking, corporate banking, investment banking, and wealth management."
    },
    "sunpharma": {
        "symbol": "SUNPHARMA.NS",
        "name": "Sun Pharmaceutical Ltd.",
        "ticker_display": "NSE: SUNPHARMA",
        "sectors": [
            {"label": "Pharmaceuticals", "cls": "fmcg"},
            {"label": "Healthcare",      "cls": "consulting"}
        ],
        "description": "Sun Pharmaceutical Industries is India's largest pharmaceutical company and the world's fourth-largest specialty generics company. It manufactures branded and generic medicinal products."
    },
    "drreddy": {
        "symbol": "DRREDDY.NS",
        "name": "Dr. Reddy's Laboratories",
        "ticker_display": "NSE: DRREDDY",
        "sectors": [
            {"label": "Pharmaceuticals", "cls": "fmcg"},
            {"label": "Healthcare",      "cls": "consulting"}
        ],
        "description": "Dr. Reddy's Laboratories is an Indian multinational pharmaceutical company. It produces finished dosage forms, active pharmaceutical ingredients (APIs), and biosimilars for global markets."
    },
    "maruti": {
        "symbol": "MARUTI.NS",
        "name": "Maruti Suzuki India Ltd.",
        "ticker_display": "NSE: MARUTI",
        "sectors": [
            {"label": "Automobiles",    "cls": "infra"},
            {"label": "Manufacturing",  "cls": "energy"}
        ],
        "description": "Maruti Suzuki India Limited is India's largest passenger car manufacturer with over 40% market share. A subsidiary of Suzuki Motor Corporation, it sells popular models like Swift, Baleno, and Brezza."
    },
    "tatamotors": {
        "symbol": "TATAMOTORS.NS",
        "name": "Tata Motors Ltd.",
        "ticker_display": "NSE: TATAMOTORS",
        "sectors": [
            {"label": "Automobiles",  "cls": "infra"},
            {"label": "EV",           "cls": "energy"}
        ],
        "description": "Tata Motors is India's largest automobile manufacturer by revenue. It owns Jaguar Land Rover and has an extensive portfolio of commercial and passenger vehicles including Electric Vehicles."
    },
    "tatasteel": {
        "symbol": "TATASTEEL.NS",
        "name": "Tata Steel Ltd.",
        "ticker_display": "NSE: TATASTEEL",
        "sectors": [
            {"label": "Steel",        "cls": "mining"},
            {"label": "Manufacturing","cls": "infra"}
        ],
        "description": "Tata Steel is one of the world's top steel producers with a significant presence in India and Europe. It is part of the Tata Group and operates some of the most technologically advanced steel plants globally."
    },
    "hcltech": {
        "symbol": "HCLTECH.NS",
        "name": "HCL Technologies Ltd.",
        "ticker_display": "NSE: HCLTECH",
        "sectors": [
            {"label": "IT Services",  "cls": "it"},
            {"label": "Consulting",   "cls": "consulting"}
        ],
        "description": "HCL Technologies is a global technology company that helps enterprises reimagine their businesses for the digital age through services, products, and platforms across IT and business services."
    },
    "techm": {
        "symbol": "TECHM.NS",
        "name": "Tech Mahindra Ltd.",
        "ticker_display": "NSE: TECHM",
        "sectors": [
            {"label": "IT Services",   "cls": "it"},
            {"label": "Telecom Tech",  "cls": "telecom"}
        ],
        "description": "Tech Mahindra is a global IT company enabling digital transformation for 1,100+ customers across 90+ countries. A Mahindra Group company, it specializes in telecom, BFSI, and enterprise IT services."
    },
    "titan": {
        "symbol": "TITAN.NS",
        "name": "Titan Company Ltd.",
        "ticker_display": "NSE: TITAN",
        "sectors": [
            {"label": "Consumer Goods",  "cls": "retail"},
            {"label": "Luxury",          "cls": "fmcg"}
        ],
        "description": "Titan Company is India's most iconic consumer lifestyle company and part of the Tata Group. It owns popular brands like Tanishq (jewellery), Titan (watches), and Fastrack."
    },
    "ultracemco": {
        "symbol": "ULTRACEMCO.NS",
        "name": "UltraTech Cement Ltd.",
        "ticker_display": "NSE: ULTRACEMCO",
        "sectors": [
            {"label": "Cement",         "cls": "infra"},
            {"label": "Infrastructure",  "cls": "mining"}
        ],
        "description": "UltraTech Cement is India's largest cement company and the third-largest in the world outside China. It is part of the Aditya Birla Group with a massive installed capacity across India and overseas."
    },
    "nestleind": {
        "symbol": "NESTLEIND.NS",
        "name": "Nestle India Ltd.",
        "ticker_display": "NSE: NESTLEIND",
        "sectors": [
            {"label": "FMCG",          "cls": "fmcg"},
            {"label": "Food & Beverages", "cls": "retail"}
        ],
        "description": "Nestlé India is a subsidiary of Nestlé S.A., Switzerland. It is one of India's leading FMCG companies, known for iconic brands like Maggi noodles, KitKat, Nescafé, and Munch."
    },
    "powergrid": {
        "symbol": "POWERGRID.NS",
        "name": "Power Grid Corporation",
        "ticker_display": "NSE: POWERGRID",
        "sectors": [
            {"label": "Power",          "cls": "energy"},
            {"label": "Public Sector",   "cls": "psu"}
        ],
        "description": "Power Grid Corporation of India is a state-owned electric utilities company that owns and operates the national electricity transmission network. It is a Maharatna PSU under the Ministry of Power."
    },
    "ntpc": {
        "symbol": "NTPC.NS",
        "name": "NTPC Ltd.",
        "ticker_display": "NSE: NTPC",
        "sectors": [
            {"label": "Power Generation", "cls": "energy"},
            {"label": "Public Sector",    "cls": "psu"}
        ],
        "description": "NTPC Limited is India's largest power generating company and a Maharatna Central Public Sector Enterprise. It has a diversified portfolio of thermal, hydro, solar, and wind power plants."
    },
    "lnt": {
        "symbol": "LT.NS",
        "name": "Larsen & Toubro Ltd.",
        "ticker_display": "NSE: LT",
        "sectors": [
            {"label": "Infrastructure", "cls": "infra"},
            {"label": "Engineering",    "cls": "consulting"}
        ],
        "description": "Larsen & Toubro is a major technology, engineering, construction, manufacturing and financial services conglomerate. It has a global presence and is a dominant player in infrastructure projects across India and overseas."
    },
    "mahindra": {
        "symbol": "M&M.NS",
        "name": "Mahindra & Mahindra Ltd.",
        "ticker_display": "NSE: M&M",
        "sectors": [
            {"label": "Automobiles", "cls": "infra"},
            {"label": "Tractors",    "cls": "agri"}
        ],
        "description": "Mahindra & Mahindra is a leading Indian multinational automotive manufacturing corporation. It is best known for SUVs, tractors, and commercial vehicles, and is a key player in India's EV transition."
    },
    "ongc": {
        "symbol": "ONGC.NS",
        "name": "Oil & Natural Gas Corp.",
        "ticker_display": "NSE: ONGC",
        "sectors": [
            {"label": "Oil & Gas",     "cls": "energy"},
            {"label": "Public Sector", "cls": "psu"}
        ],
        "description": "Oil and Natural Gas Corporation (ONGC) is India's largest crude oil and natural gas company, contributing over 70% of India's domestic production. It is a Maharatna PSU with significant global operations."
    },
    "coalindia": {
        "symbol": "COALINDIA.NS",
        "name": "Coal India Ltd.",
        "ticker_display": "NSE: COALINDIA",
        "sectors": [
            {"label": "Mining",        "cls": "mining"},
            {"label": "Public Sector", "cls": "psu"}
        ],
        "description": "Coal India Limited is the world's largest coal producer and one of the largest corporate employers. A Maharatna PSU, it accounts for over 80% of India's coal production and is critical to the country's energy security."
    },
    "airtel": {
        "symbol": "BHARTIARTL.NS",
        "name": "Bharti Airtel Ltd.",
        "ticker_display": "NSE: BHARTIARTL",
        "sectors": [
            {"label": "Telecom",  "cls": "telecom"},
            {"label": "DTH",      "cls": "it"}
        ],
        "description": "Bharti Airtel is one of India's leading telecommunications companies and a global brand operating in 18 countries. It offers mobile, broadband, DTH, and enterprise solutions and is a major player in the 5G rollout."
    },
    "cipla": {
        "symbol": "CIPLA.NS",
        "name": "Cipla Ltd.",
        "ticker_display": "NSE: CIPLA",
        "sectors": [
            {"label": "Pharmaceuticals", "cls": "fmcg"},
            {"label": "Healthcare",      "cls": "consulting"}
        ],
        "description": "Cipla is a leading global pharmaceutical company focused on agile and sustainable growth. It has a portfolio of 1,500+ products in over 80 countries, with a strong emphasis on affordable generics and respiratory medicine."
    },
    "divislab": {
        "symbol": "DIVISLAB.NS",
        "name": "Divi's Laboratories Ltd.",
        "ticker_display": "NSE: DIVISLAB",
        "sectors": [
            {"label": "Pharma APIs",     "cls": "fmcg"},
            {"label": "Life Sciences",   "cls": "consulting"}
        ],
        "description": "Divi's Laboratories is one of India's top pharmaceutical manufacturers, specializing in Active Pharmaceutical Ingredients (APIs) and intermediates. It is a key global supplier for major innovator pharma companies."
    },
    "asianpaint": {
        "symbol": "ASIANPAINT.NS",
        "name": "Asian Paints Ltd.",
        "ticker_display": "NSE: ASIANPAINT",
        "sectors": [
            {"label": "Paints",          "cls": "retail"},
            {"label": "Consumer Goods",  "cls": "fmcg"}
        ],
        "description": "Asian Paints is India's largest paint company and ranks among the top 10 decorative coatings companies in the world. It operates in 15 countries across Asia, Middle East, South Pacific, and Africa."
    },
    "pidilite": {
        "symbol": "PIDILITIND.NS",
        "name": "Pidilite Industries Ltd.",
        "ticker_display": "NSE: PIDILITIND",
        "sectors": [
            {"label": "Adhesives",        "cls": "infra"},
            {"label": "Consumer Goods",   "cls": "retail"}
        ],
        "description": "Pidilite Industries is India's leading manufacturer of adhesives and sealants. Known for iconic brands like Fevicol and Dr. Fixit, it dominates the adhesives market and has a strong presence in construction chemicals."
    },
    "hindzinc": {
        "symbol": "HINDZINC.NS",
        "name": "Hindustan Zinc Ltd.",
        "ticker_display": "NSE: HINDZINC",
        "sectors": [
            {"label": "Zinc & Lead",  "cls": "mining"},
            {"label": "Silver",       "cls": "energy"}
        ],
        "description": "Hindustan Zinc is the world's second-largest zinc producer and the world's largest integrated zinc-lead producer. A subsidiary of Vedanta, it also produces significant quantities of silver as a by-product."
    },
    "vedanta": {
        "symbol": "VEDL.NS",
        "name": "Vedanta Ltd.",
        "ticker_display": "NSE: VEDL",
        "sectors": [
            {"label": "Metals",   "cls": "mining"},
            {"label": "Oil & Gas","cls": "energy"}
        ],
        "description": "Vedanta Limited is a diversified natural resources company with businesses in zinc, lead, silver, copper, iron ore, steel, aluminium, power, and oil & gas. It is a subsidiary of Vedanta Resources plc."
    },
    "jswsteel": {
        "symbol": "JSWSTEEL.NS",
        "name": "JSW Steel Ltd.",
        "ticker_display": "NSE: JSWSTEEL",
        "sectors": [
            {"label": "Steel",         "cls": "mining"},
            {"label": "Manufacturing", "cls": "infra"}
        ],
        "description": "JSW Steel is India's leading integrated steel company and part of the JSW Group. With a capacity of over 28 MTPA, it manufactures flat and long steel products and has operations in India, the US, and Europe."
    },
    "bpcl": {
        "symbol": "BPCL.NS",
        "name": "Bharat Petroleum Corp. Ltd.",
        "ticker_display": "NSE: BPCL",
        "sectors": [
            {"label": "Oil Refining",  "cls": "energy"},
            {"label": "Public Sector", "cls": "psu"}
        ],
        "description": "Bharat Petroleum Corporation Limited is a Maharatna oil refining and marketing PSU. It operates major refineries in Mumbai and Kochi, and has a vast network of petrol stations and LPG distribution across India."
    },
    "zomato": {
        "symbol": "ZOMATO.NS",
        "name": "Zomato Ltd.",
        "ticker_display": "NSE: ZOMATO",
        "sectors": [
            {"label": "Food Tech",   "cls": "it"},
            {"label": "Quick Commerce", "cls": "retail"}
        ],
        "description": "Zomato is India's largest food delivery and quick commerce platform. It connects millions of customers with restaurants and operates Blinkit for grocery delivery. A pioneer of India's new-age consumer tech economy."
    }
}


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/stock/<key>")
def get_stock(key):
    """
    Returns real-time stock data + AI analysis for the given key.
    Uses Yahoo Finance for live data. Computes RSI, SMA, volatility,
    volume trend, and predicted next-day price.
    """
    stock_meta = STOCK_MAP.get(key)
    if not stock_meta:
        return jsonify({"error": f"Unknown stock key: {key}"}), 404

    symbol = stock_meta["symbol"]

    try:
        ticker = yf.Ticker(symbol)

        # ── Current quote ──
        info = ticker.fast_info
        current_price = round(float(info.last_price), 2)
        prev_close    = round(float(info.previous_close), 2)
        day_open      = round(float(info.open), 2)
        day_high      = round(float(info.day_high), 2)
        day_low       = round(float(info.day_low), 2)

        market_cap_raw = float(info.market_cap)
        if market_cap_raw >= 1e12:
            market_cap_str = f"₹{market_cap_raw / 1e12:.1f}L Cr"
        elif market_cap_raw >= 1e7:
            market_cap_str = f"₹{market_cap_raw / 1e7:.0f} Cr"
        else:
            market_cap_str = f"₹{market_cap_raw:,.0f}"

        change_val = round(current_price - prev_close, 2)
        change_pct = round((change_val / prev_close) * 100, 2) if prev_close else 0

        # ── Historical data (fetch enough for indicators) ──
        hist = ticker.history(period="3mo")
        history = []
        if not hist.empty:
            recent = hist.tail(10)
            for date, row in recent.iterrows():
                history.append({
                    "date":   date.strftime("%d %b %Y"),
                    "open":   round(float(row["Open"]), 2),
                    "high":   round(float(row["High"]), 2),
                    "low":    round(float(row["Low"]), 2),
                    "close":  round(float(row["Close"]), 2),
                    "volume": int(row["Volume"])
                })

        # ══════════════════════════════════════════
        # AI ANALYSIS — computed server-side
        # ══════════════════════════════════════════
        analysis = compute_analysis(hist, current_price)

        return jsonify({
            "key":            key,
            "name":           stock_meta["name"],
            "ticker_display": stock_meta["ticker_display"],
            "symbol":         symbol,
            "sectors":        stock_meta["sectors"],
            "description":    stock_meta["description"],
            "current_price":  current_price,
            "prev_close":     prev_close,
            "open":           day_open,
            "day_high":       day_high,
            "day_low":        day_low,
            "market_cap":     market_cap_str,
            "change_val":     change_val,
            "change_pct":     change_pct,
            "history":        history,
            "analysis":       analysis,
            "fetched_at":     datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ══════════════════════════════════════════════════════════════
# AI ANALYSIS ENGINE v3.0 — Multi-Factor Scoring System
# ══════════════════════════════════════════════════════════════

def compute_analysis(hist, current_price):
    """
    Advanced multi-factor AI analysis engine.
    Computes: RSI, SMA crossover, volatility, volume trend,
    price momentum, trend strength, support/resistance,
    risk level, predicted price (WMA+momentum), and smart insight.
    Scoring: normalized -10 to +10 scale.
    """
    if hist is None or hist.empty or len(hist) < 14:
        return {"error": "Insufficient data for analysis"}

    closes  = [round(float(c), 2) for c in hist["Close"].tolist()]
    highs   = [round(float(h), 2) for h in hist["High"].tolist()]
    lows    = [round(float(l), 2) for l in hist["Low"].tolist()]
    volumes = [int(v) for v in hist["Volume"].tolist()]

    # ════════════════════════════════════════
    # 1. RSI (Relative Strength Index, 14-period)
    # ════════════════════════════════════════
    rsi = compute_rsi(closes, 14)

    # ════════════════════════════════════════
    # 2. SMA-5 and SMA-10 Crossover
    # ════════════════════════════════════════
    sma5  = round(sum(closes[-5:]) / 5, 2)
    sma10 = round(sum(closes[-10:]) / 10, 2) if len(closes) >= 10 else sma5

    if current_price > sma5 > sma10:
        sma_signal = "BULLISH"
        sma_detail = "Price above both SMA-5 and SMA-10 — strong upward momentum."
    elif current_price < sma5 < sma10:
        sma_signal = "BEARISH"
        sma_detail = "Price below both SMA-5 and SMA-10 — downward pressure."
    elif sma5 > sma10:
        sma_signal = "BULLISH"
        sma_detail = "SMA-5 above SMA-10 (golden cross setup) — mildly bullish."
    elif sma5 < sma10:
        sma_signal = "BEARISH"
        sma_detail = "SMA-5 below SMA-10 (death cross setup) — mildly bearish."
    else:
        sma_signal = "NEUTRAL"
        sma_detail = "SMA lines converging — no clear directional bias."

    # ════════════════════════════════════════
    # 3. Volatility (10-day standard deviation)
    # ════════════════════════════════════════
    last10_closes = closes[-10:]
    mean_10 = sum(last10_closes) / len(last10_closes)
    variance = sum((x - mean_10) ** 2 for x in last10_closes) / len(last10_closes)
    volatility = round(variance ** 0.5, 2)
    volatility_pct = round((volatility / mean_10) * 100, 2)

    if volatility_pct > 3:
        vol_label = "HIGH"
    elif volatility_pct > 1.5:
        vol_label = "MODERATE"
    else:
        vol_label = "LOW"

    # ════════════════════════════════════════
    # 4. Volume Trend
    # ════════════════════════════════════════
    avg_vol_5  = sum(volumes[-5:]) / 5
    avg_vol_10 = sum(volumes[-10:]) / 10 if len(volumes) >= 10 else avg_vol_5
    vol_change = round(((avg_vol_5 - avg_vol_10) / avg_vol_10) * 100, 1) if avg_vol_10 else 0

    if vol_change > 15:
        vol_trend = "INCREASING"
    elif vol_change < -15:
        vol_trend = "DECREASING"
    else:
        vol_trend = "STABLE"

    # ════════════════════════════════════════
    # 5. Price Momentum (last 3-day % change)
    # ════════════════════════════════════════
    if len(closes) >= 4:
        momentum_3d = round(((closes[-1] - closes[-4]) / closes[-4]) * 100, 2)
    else:
        momentum_3d = 0.0

    # ════════════════════════════════════════
    # 6. Trend Strength (slope-based)
    # ════════════════════════════════════════
    slope_5d  = compute_slope(closes[-5:])
    slope_10d = compute_slope(closes[-10:]) if len(closes) >= 10 else slope_5d

    # Normalized trend strength: slope relative to price
    slope_pct = abs(slope_5d / mean_10 * 100) if mean_10 else 0

    if slope_pct > 1.0:
        trend_strength = "STRONG"
        trend_strength_value = min(100, int(slope_pct * 30))
    elif slope_pct > 0.35:
        trend_strength = "MODERATE"
        trend_strength_value = int(40 + slope_pct * 25)
    else:
        trend_strength = "WEAK"
        trend_strength_value = max(10, int(slope_pct * 60))

    trend_direction = "UP" if slope_5d > 0 else ("DOWN" if slope_5d < 0 else "FLAT")

    # ════════════════════════════════════════
    # 7. Support & Resistance (10-day range)
    # ════════════════════════════════════════
    last10_highs = highs[-10:] if len(highs) >= 10 else highs
    last10_lows  = lows[-10:] if len(lows) >= 10 else lows

    resistance = round(max(last10_highs), 2)
    support    = round(min(last10_lows), 2)
    price_range = resistance - support

    # Proximity alerts
    dist_to_support    = current_price - support
    dist_to_resistance = resistance - current_price

    if price_range > 0:
        pct_from_support    = round((dist_to_support / price_range) * 100, 1)
        pct_from_resistance = round((dist_to_resistance / price_range) * 100, 1)
    else:
        pct_from_support = 50.0
        pct_from_resistance = 50.0

    if pct_from_support < 15:
        sr_alert = "NEAR SUPPORT"
        sr_alert_detail = f"Price is very close to recent support (₹{support:,.2f}). Potential bounce zone."
    elif pct_from_resistance < 15:
        sr_alert = "NEAR RESISTANCE"
        sr_alert_detail = f"Price is near recent resistance (₹{resistance:,.2f}). Watch for breakout or reversal."
    else:
        sr_alert = "MID-RANGE"
        sr_alert_detail = f"Price is between support (₹{support:,.2f}) and resistance (₹{resistance:,.2f})."

    # ════════════════════════════════════════
    # 8. Risk Indicator
    # ════════════════════════════════════════
    risk_score = 0
    if volatility_pct > 3:
        risk_score += 3
    elif volatility_pct > 1.5:
        risk_score += 2
    else:
        risk_score += 1

    if sr_alert == "NEAR RESISTANCE":
        risk_score += 1
    if vol_trend == "INCREASING":
        risk_score += 1

    if risk_score >= 4:
        risk_level = "HIGH"
    elif risk_score >= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # ════════════════════════════════════════
    # 9. Predicted Next-Day Price (WMA + Momentum)
    # ════════════════════════════════════════
    predicted_price = predict_next_price_v2(closes[-10:], sma5, sma10, current_price, momentum_3d)

    predicted_change = round(predicted_price - current_price, 2)
    predicted_change_pct = round((predicted_change / current_price) * 100, 2)

    if predicted_change > 0:
        price_direction = "UP"
    elif predicted_change < 0:
        price_direction = "DOWN"
    else:
        price_direction = "FLAT"

    # ════════════════════════════════════════
    # 10. Multi-Factor AI Scoring (-10 to +10)
    # ════════════════════════════════════════
    sub_scores = {}

    # Factor 1: RSI (weight 2.0)
    if rsi < 20:
        sub_scores["rsi"] = 2.0
    elif rsi < 30:
        sub_scores["rsi"] = 1.5
    elif rsi < 40:
        sub_scores["rsi"] = 0.8
    elif rsi < 60:
        sub_scores["rsi"] = 0.0
    elif rsi < 70:
        sub_scores["rsi"] = -0.8
    elif rsi < 80:
        sub_scores["rsi"] = -1.5
    else:
        sub_scores["rsi"] = -2.0

    # Factor 2: SMA crossover (weight 2.5)
    if sma_signal == "BULLISH" and current_price > sma5:
        sub_scores["sma"] = 2.5
    elif sma_signal == "BULLISH":
        sub_scores["sma"] = 1.5
    elif sma_signal == "BEARISH" and current_price < sma5:
        sub_scores["sma"] = -2.5
    elif sma_signal == "BEARISH":
        sub_scores["sma"] = -1.5
    else:
        sub_scores["sma"] = 0.0

    # Factor 3: Volume trend (weight 1.5)
    if vol_trend == "INCREASING":
        sub_scores["volume"] = 1.5 if sub_scores.get("sma", 0) > 0 else -1.0
    elif vol_trend == "DECREASING":
        sub_scores["volume"] = -0.5
    else:
        sub_scores["volume"] = 0.0

    # Factor 4: Volatility risk (weight 1.0)
    if vol_label == "LOW" and sub_scores.get("sma", 0) > 0:
        sub_scores["volatility"] = 0.5
    elif vol_label == "HIGH":
        sub_scores["volatility"] = -1.0
    else:
        sub_scores["volatility"] = 0.0

    # Factor 5: Price momentum 3-day (weight 2.0)
    if momentum_3d > 2:
        sub_scores["momentum"] = 2.0
    elif momentum_3d > 0.5:
        sub_scores["momentum"] = 1.0
    elif momentum_3d > -0.5:
        sub_scores["momentum"] = 0.0
    elif momentum_3d > -2:
        sub_scores["momentum"] = -1.0
    else:
        sub_scores["momentum"] = -2.0

    # Sum all sub-scores → clamp to [-10, +10]
    raw_score = sum(sub_scores.values())
    ai_score = round(max(-10, min(10, raw_score)), 1)

    # Signal from AI score
    if ai_score >= 8:
        overall_signal = "STRONG BUY"
        signal_color = "green"
    elif ai_score >= 4:
        overall_signal = "BUY"
        signal_color = "green"
    elif ai_score > -4:
        overall_signal = "HOLD"
        signal_color = "amber"
    elif ai_score > -8:
        overall_signal = "SELL"
        signal_color = "red"
    else:
        overall_signal = "STRONG SELL"
        signal_color = "red"

    # ════════════════════════════════════════
    # Confidence (based on indicator agreement)
    # ════════════════════════════════════════
    directions = []
    if sub_scores["rsi"] > 0: directions.append(1)
    elif sub_scores["rsi"] < 0: directions.append(-1)
    else: directions.append(0)

    if sub_scores["sma"] > 0: directions.append(1)
    elif sub_scores["sma"] < 0: directions.append(-1)
    else: directions.append(0)

    if sub_scores["momentum"] > 0: directions.append(1)
    elif sub_scores["momentum"] < 0: directions.append(-1)
    else: directions.append(0)

    if sub_scores["volume"] > 0: directions.append(1)
    elif sub_scores["volume"] < 0: directions.append(-1)
    else: directions.append(0)

    # Agreement: how many indicators agree with the majority
    if directions:
        avg_dir = sum(directions) / len(directions)
        agreement = abs(avg_dir)  # 0 to 1
    else:
        agreement = 0

    slope_strength = min(1.0, abs(slope_5d) / (mean_10 * 0.01)) if mean_10 else 0
    vol_confirm = 0.15 if vol_trend == "INCREASING" and ai_score != 0 else 0

    confidence = 50 + int(agreement * 25) + int(slope_strength * 12) + int(vol_confirm * 8)
    confidence = max(50, min(95, confidence))

    # ════════════════════════════════════════
    # Smart Insight Text
    # ════════════════════════════════════════
    insight = generate_smart_insight(
        rsi, sma_signal, vol_trend, vol_label, momentum_3d,
        trend_strength, trend_direction, sr_alert, risk_level,
        overall_signal, predicted_change_pct, current_price, sma5
    )

    return {
        "rsi":                  round(rsi, 1),
        "sma5":                 sma5,
        "sma10":                sma10,
        "sma_signal":           sma_signal,
        "sma_detail":           sma_detail,
        "volatility":           volatility,
        "volatility_pct":       volatility_pct,
        "volatility_label":     vol_label,
        "avg_volume_5d":        int(avg_vol_5),
        "avg_volume_10d":       int(avg_vol_10),
        "volume_change_pct":    vol_change,
        "volume_trend":         vol_trend,
        "momentum_3d":          momentum_3d,
        "trend_strength":       trend_strength,
        "trend_strength_value": trend_strength_value,
        "trend_direction":      trend_direction,
        "support":              support,
        "resistance":           resistance,
        "sr_alert":             sr_alert,
        "sr_alert_detail":      sr_alert_detail,
        "pct_from_support":     pct_from_support,
        "pct_from_resistance":  pct_from_resistance,
        "risk_level":           risk_level,
        "risk_score":           risk_score,
        "predicted_price":      predicted_price,
        "predicted_change":     predicted_change,
        "predicted_change_pct": predicted_change_pct,
        "price_direction":      price_direction,
        "overall_signal":       overall_signal,
        "signal_color":         signal_color,
        "ai_score":             ai_score,
        "sub_scores":           sub_scores,
        "confidence":           confidence,
        "insight":              insight
    }


# ── Helper: Compute slope of a series ──
def compute_slope(values):
    """Simple linear regression slope."""
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    return numerator / denominator if denominator else 0.0


def compute_rsi(closes, period=14):
    """Calculate RSI using the standard method."""
    if len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    recent_deltas = deltas[-period:]
    gains  = [d if d > 0 else 0 for d in recent_deltas]
    losses = [-d if d < 0 else 0 for d in recent_deltas]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def predict_next_price_v2(closes, sma5, sma10, current_price, momentum_3d):
    """
    Improved prediction: WMA + momentum adjustment.
    Formula: predicted = (0.5 * SMA5 + 0.3 * SMA10 + 0.2 * current) + momentum_adj
    The momentum adjustment factors in the 3-day trend.
    """
    # Base prediction from weighted moving averages
    base = (0.5 * sma5) + (0.3 * sma10) + (0.2 * current_price)

    # Momentum adjustment: scale 3-day momentum into a price offset
    # If momentum is +2%, adjust predicted price slightly upward
    momentum_factor = (momentum_3d / 100) * current_price * 0.3
    predicted = base + momentum_factor

    return round(predicted, 2)


def generate_smart_insight(rsi, sma_signal, vol_trend, vol_label,
                           momentum_3d, trend_strength, trend_direction,
                           sr_alert, risk_level, overall_signal,
                           predicted_change_pct, current_price, sma5):
    """Generate a human-readable AI insight paragraph."""
    parts = []

    # Momentum description
    if momentum_3d > 1:
        parts.append(f"Stock shows bullish momentum (+{momentum_3d:.1f}% in 3 days)")
    elif momentum_3d < -1:
        parts.append(f"Stock under selling pressure ({momentum_3d:.1f}% in 3 days)")
    else:
        parts.append("Price movement has been relatively flat recently")

    # RSI context
    if rsi < 30:
        parts.append(f"RSI at {rsi:.0f} indicates oversold conditions — potential buying opportunity")
    elif rsi > 70:
        parts.append(f"RSI at {rsi:.0f} suggests overbought levels — correction possible")
    elif rsi < 45:
        parts.append(f"RSI in lower-neutral zone ({rsi:.0f})")
    elif rsi > 55:
        parts.append(f"RSI in upper-neutral zone ({rsi:.0f})")
    else:
        parts.append(f"RSI at {rsi:.0f} is balanced")

    # Volume context
    if vol_trend == "INCREASING" and sma_signal == "BULLISH":
        parts.append("Rising volume confirms the bullish trend")
    elif vol_trend == "INCREASING" and sma_signal == "BEARISH":
        parts.append("Rising volume adds weight to selling pressure")
    elif vol_trend == "DECREASING":
        parts.append("Declining volume suggests weakening conviction")

    # Support/Resistance
    if sr_alert == "NEAR SUPPORT":
        parts.append("Price is near key support — watch for a bounce")
    elif sr_alert == "NEAR RESISTANCE":
        parts.append("Price is approaching resistance — breakout or rejection ahead")

    # Prediction
    if predicted_change_pct > 0.3:
        parts.append(f"Our model predicts a +{predicted_change_pct:.1f}% move in the next session")
    elif predicted_change_pct < -0.3:
        parts.append(f"Model forecasts a {predicted_change_pct:.1f}% decline next session")
    else:
        parts.append("Prediction is near-flat for the next session")

    # Risk warning
    if risk_level == "HIGH":
        parts.append("⚠️ High risk — trade with caution")

    return ". ".join(parts) + "."


if __name__ == "__main__":
    print("\n🚀  Smart Stock Insight Platform is running!")
    print("   Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)
