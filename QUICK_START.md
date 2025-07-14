# ⚡ Quick Start Guide

Get the Airline Booking Market Demand Analyzer running in 5 minutes!

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Set Up Environment
```bash
cp env.example .env
```

Edit `.env` with your API keys:
```env
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 3: Run the Application
```bash
python run.py
```

## Step 4: Access the Dashboard
Open: http://localhost:8000

## Step 5: Get API Keys (If Needed)

### Amadeus API (Free)
1. Go to https://developers.amadeus.com/
2. Sign up for free account
3. Create new app
4. Copy API Key & Secret

### OpenAI API
1. Go to https://platform.openai.com/
2. Sign up/sign in
3. Create API key
4. Copy the key

## Step 6: Test the Application
1. Click "Fetch Latest Data" in the dashboard
2. Wait 5-10 minutes for data processing
3. Click "Generate New Insights"
4. Explore the charts and filters!

## Troubleshooting

### Common Issues:
- **Module not found**: Run `pip install -r requirements.txt`
- **API errors**: Check your API keys in `.env`
- **Port in use**: Change port in run.py or kill process on port 8000

### Need Help?
- Check the full README.md for detailed instructions
- Review the API documentation at http://localhost:8000/docs
- Check application logs for error messages

---

🚀 **That's it! You're ready to analyze airline market demand!** 