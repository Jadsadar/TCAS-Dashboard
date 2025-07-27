
# 🎓 TCAS University Program Dashboard

A web-based interactive dashboard that helps prospective university students explore **AI Engineering** and **Computer Engineering** programs across Thailand. With features like dynamic filtering, sorting, charts, and summary statistics, this app is designed for students preparing to attend university in the upcoming academic year.

---

## 📌 Features

- **Dashboard for AI Engineering and COE Programs**
  - Explore tuition costs, number of programs per university, and term information.
- **Interactive Filters**
  - Filter by university, cost range, and sorting preferences.
- **Visual Insights**
  - Compare program costs with bar charts and university-wise program counts.
- **Clean Data Tables**
  - View detailed program info with formatted columns and text wrapping.
- **Designed With Students in Mind**
  - Ideal for high school seniors preparing for TCAS admission decisions.

---

## 🖥️ Live Demo

> _Currently not deployed. Run locally using the steps below._

---

## ⚙️ Requirements

Install all dependencies using:

```bash
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
pandas
selenium
beautifulsoup4
dash
plotly
dash_bootstrap_components
```

---

## 🗂️ Project Structure

```
scraping_test/
│
├── chromedriver-win64/               # ChromeDriver for Selenium scraping
├── data/                             # Contains CSV data for AI and COE programs
│   ├── aie/cleaned_aie.csv
│   └── coe/coe_with_term_and_total.csv
├── venv/                             # Python virtual environment (optional)
├── __pycache__/                      # Python cache files
│
├── app.py                            # Main Dash app and all callbacks
├── main.py                           # Legacy or additional script
├── cost_scraper.py                   # Web scraping script for program data
├── check..ipynb                      # Jupyter notebook (used for testing)
│
├── styles.css                        # Custom CSS (optional)
├── .gitignore                        # Git ignore file
├── requirements.txt                  # Python dependencies
```

---

## 🚀 Getting Started

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/your-username/tcas-dashboard.git
   cd tcas-dashboard
   ```

2. **Set Up Virtual Environment (Optional)**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Requirements**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Data Files Are Present**  
   Make sure the following CSVs exist:
   - `data/aie/cleaned_aie.csv`
   - `data/coe/coe_with_term_and_total.csv`

5. **Run the App**
   ```bash
   python app.py
   ```

6. **View in Browser**  
   Navigate to `http://127.0.0.1:8050/` to start using the dashboard.

---

## 🧠 How It Works

- Built using **Dash** and **Plotly** for fast interactive UI.
- Uses **Pandas** for data processing.
- Charts and tables auto-update based on user-selected filters.
- The scraping logic (in `cost_scraper.py`) can be extended to update the datasets regularly.



