# Test Task ProMobility

## Prerequisites

## Overview

This Python project aims to optimize the delivery route for a car visiting all Epicenter stores in Kyiv, starting from the Southern Railway Station. The goal is to determine the optimal sequence of store visits and the ideal departure time that minimizes the total travel and service time.

The project leverages the TomTom Waypoint Optimization API to solve the traveling salesman problem (TSP) and find the most efficient route. It takes into account store opening hours, allows for custom departure time ranges, and can handle API errors gracefully.

## Prerequisites

- **Python 3.x:** Make sure you have Python 3 installed.
- **Virtual Environment (recommended):**  Create a virtual environment to manage project dependencies.
- **TomTom API Key:** Obtain a free API key from TomTom and store it in a `.env` file.
- **Google Maps API Key:** Obtain a free API key from Google Maps and store it in a `.env` file.

## Installation

```bash

git clone https://github.com/Dh-Kh/data_test.git

python3 -m venv venv

source venv/bin/activate (or . venv/bin/activate)

pip install -r requirements.txt

python3 main.py

```

### Project Structure

```bash
.
├── __init__.py
├── main.py
├── Readme.md
└── requirements.txt
```

