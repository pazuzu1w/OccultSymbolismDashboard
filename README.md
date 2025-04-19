# 🔮 Occult Symbolism Dashboard

![Ancient Knowledge](https://via.placeholder.com/1200x400?text=Ancient+Knowledge+Visualized)

## 📜 Overview

The Occult Symbolism Dashboard is a data visualization platform that maps the hidden connections between esoteric symbols, traditions, and concepts throughout history. This project combines ancient knowledge with modern technology to create an interactive exploration tool.

> "The universe is full of magical things patiently waiting for our wits to grow sharper." — Eden Phillpotts

## ✨ Features

### 🕸️ Network Visualization
- Force-directed graph showing connections between occult symbols
- Interactive node exploration with detailed information panels
- Relationship strength visualization using connection weights

### 📊 Data Analysis
- Timeline visualization spanning from ancient times to modern day
- Element distribution analysis across traditions
- Geographic mapping of esoteric practices
- Tradition comparison tools

### 🔍 Knowledge Discovery
- Advanced search capabilities for symbols, traditions, and elements
- Automatic data scraping from authoritative sources
- Database synchronization with continuous expansion
- CLI tool for manual database management

## 🛠️ Tech Stack

### Backend
- **Python Flask** - Web application framework
- **SQLAlchemy ORM** - Database management
- **RESTful API** - Data access endpoints
- **Web Scrapers** - Automated data acquisition

### Frontend
- **D3.js** - Force-directed network visualization 
- **Plotly.js** - Interactive data charts
- **Bootstrap 5** - Responsive design
- **Dark Theme UI** - Mystical aesthetic

### Database
- **Symbol Models** - Detailed information about occult symbols
- **Tradition Models** - Historical context for esoteric practices
- **Connection Models** - Relationship mapping between symbols
- **Element Models** - Categorization by elemental associations

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/pazuzu1w/occult-symbolism-dashboard.git
cd occult-symbolism-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python db_setup.py

# Run the application
python run.py