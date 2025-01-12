
# Theseus Alpha 🔮

Theseus Alpha is an intelligent trading system designed for the HyperLiquid blockchain. It leverages advanced LLM-driven (Large Language Model) analysis to make informed trading decisions. Drawing inspiration from the legendary hero Theseus, the system aims to navigate the labyrinthine complexities of crypto markets with precision and efficiency.

---

## System Architecture

<a href="https://ibb.co/mG4dFhw"><img src="https://i.ibb.co/rmHqf5S/Theseus-final-diagram.png" alt="Theseus-final-diagram" border="0"></a>

Theseus Alpha's architecture is modular and scalable, focusing on three core pillars:

1. **Profile Analysis**: Understanding user trading patterns and risk tolerance.
2. **Decision-Making**: AI-powered analysis to generate actionable trading recommendations.
3. **Execution**: Robust mechanisms for trade placement, error handling, and performance optimization.

### Workflow
1. **Connect**: Establish a connection to the HyperLiquid testnet/mainnet.
2. **Analyze**: Profile spot and perpetual trading behaviors.
3. **Customize**: Adjust profiles based on user preferences.
4. **Advise**: Generate trading advice using OpenAI’s GPT-4.
5. **Execute**: Place trades based on recommendations with safety checks.

---

## Key Features

- **🤔 AI-Driven Trading**: Uses GPT-4 for generating market insights and trade recommendations.
- **📊 Deep Profile Analysis**: Examines historical data and user preferences for both spot and perpetual markets.
- **🛡️ Risk Management**: Implements advanced position sizing and exposure controls.
- **🎯 Smart Execution**: Ensures optimal order execution with slippage and error handling.
- **💡 Real-Time Adaptation**: Dynamically adjusts strategies to match evolving market conditions.
- **📈 Comprehensive Feedback**: Provides reasoning for all trade decisions, enhancing user understanding.

---

## Components

### Profilers

#### Spot Profiler
- Evaluates token holdings, trading history, and risk metrics.
- Highlights portfolio concentration and asset diversity.
- Identifies trading style (e.g., swing trading, scalping).

#### Perpetual Profiler
- Assesses leverage usage, position sizing, and margin usage.
- Computes win rates and profit/loss ratios.
- Determines risk appetite and experience level.

---

### Profile Adjusters
- Customizes trading parameters based on user input.
- Adapts to risk tolerance, preferred markets, and target returns.
- Ensures alignment with individual trading styles.

---

### LLM Trading Advisor
- Analyzes user profiles and preferences.
- Generates spot and perpetual trading recommendations.
- Explains trade reasoning in a structured format, including:
  - Recommended assets
  - Trade size and direction
  - Leverage levels

---

### Trade Executor
- Validates recommendations to ensure compliance with size limits.
- Normalizes order sizes based on market liquidity.
- Handles order placement with retries and error logging.

---

## Installation

### Prerequisites
- Python 3.8+
- [Poetry](https://python-poetry.org/) for dependency management

### Steps
```bash
# Clone the repository
git clone https://github.com/yourusername/theseus_alpha.git
cd theseus_alpha

# Install dependencies
poetry install

# Configure environment variables
cp .env.example .env
```

---

## Configuration

### Environment Variables
Set up the `.env` file with the following:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### HyperLiquid Configuration (`config.json`)
Provide your HyperLiquid credentials:
```json
{
    "secret_key": "your_hyperliquid_secret_key",
    "account_address": "your_account_address"
}
```

---

## Usage

### Running the System
```bash
poetry run python main.py
```

#### Workflow
1. **Connect to HyperLiquid**: The system establishes a connection to the blockchain.
2. **Generate Profiles**: Spot and perpetual trading profiles are analyzed and displayed.
3. **Adjust Preferences**: Users can configure their trading parameters.
4. **AI Recommendations**: GPT-4 provides actionable trading advice.
5. **Trade Execution**: Orders are placed in the market based on the advice.

---

## Trading Parameters

### Size Limits
- Minimum Order Size: **$10 USD**
- Maximum Order Size: **$150 USD**
- Orders are normalized based on available liquidity.

### Supported Markets
- **Spot**: Focused on PURR/USDC in testnet mode.
- **Perpetuals**: Wide range of markets determined by user preferences and market conditions.

### Safety Features
- Position size limits
- Slippage protection
- Trade execution timing controls
- Comprehensive error handling and retries

---

## Development

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific tests
poetry run pytest tests/test_profilers.py  # Test profilers
poetry run pytest tests/test_executor.py   # Test execution
```

### Code Quality
```bash
# Format code
poetry run black .

# Type checking
poetry run mypy .
```

---

## Project Structure
```
theseus_alpha/
├── src/
│   ├── profilers/        # Trading profile analysis
│   ├── adjusters/        # Profile adjustment logic
│   ├── trading/          # Trading execution
│   └── utils/           # Shared utilities
├── tests/               # Test suite
└── docs/               # Documentation
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Testing

Run the full test suite to ensure system stability:
```bash
poetry run pytest
```

---

## Advanced Features

### Modular Trading Preferences
- Select **Spot Only**, **Perp Only**, or **Both Markets** during the configuration step.
- Profiles and preferences are dynamically adjusted based on user input.

### Real-Time Market Adaptation
- Continuously evaluates market conditions.
- Provides updated advice in volatile environments.

### Explainable AI Recommendations
- Every trade comes with a detailed rationale, enabling better understanding of the strategy.

---

## Upcoming Features

### Gamification for Beginner Users
#### Modes:
1. **Legacy Mode**: Current CLI setup, tailored for users familiar with blockchain/trading concepts like perpetual contracts and drawdowns.
2. **Story Mode**: A gamified experience to make the trading process beginner-friendly while teaching blockchain basics.

**Example Comparison**
- **Legacy Mode:**
```
=== Welcome to Theseus Alpha Trading System ===
Analyzing your complete trading profile...
=== Trading Preferences ===
Based on your profile, would you like the agent to:
1. Focus on Spot Trading Only
2. Focus on Perpetual Trading Only
3. Trade Both Markets (Recommended for your profile)
```
- **Story Mode:**
```
"Welcome, brave adventurer, to Theseus Alpha, a mythological realm where you’ll journey through the world of on-chain trading. Guided by Zeus, Poseidon, and Ares, you’ll make critical decisions to grow your wealth and skills."

**Prologue:**
Zeus asks: "Will you start in the Magic Garden of Spot Trading or brave the Treacherous Plains of Perpetuals?"

- **Magic Garden of Spot Trading:**
Poseidon: "Here, wealth grows slowly but steadily, like a gentle tide."
*ELI5*: Spot trading is simple. You buy and hold an asset, like planting a seed and waiting for it to grow.

- **Treacherous Plains of Perpetuals:**
Ares: "Massive rewards await those bold enough to tread here, but beware the risk of ruin!"
*ELI5*: Perpetuals are advanced contracts where you can profit even if the market drops. It’s like riding a chariot at full speed—thrilling but risky.
```

### Webhooks for Real-Time Notifications
- **Event Triggers**: Notifications for stop-loss hits, margin calls, or significant portfolio updates.
- **Notification Channels**: Users can choose alerts via Telegram, Slack, or Discord bots.

---

## Troubleshooting

### Common Issues
- **Error: `OPENAI_API_KEY` not set**: Ensure the `.env` file contains your OpenAI API key.
- **Connection Error**: Verify HyperLiquid credentials and network connectivity.
- **Order Execution Failures**: Check for sufficient account balance and market liquidity.

### Logs
Detailed logs are available to debug issues. Run the system with `logging` set to `DEBUG` for more insights:
```bash
poetry run python main.py --log-level DEBUG
```

---

## Credits

Theseus Alpha integrates:
- [HyperLiquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- [OpenAI GPT-4](https://openai.com/)

---

## License

Theseus Alpha is distributed under the MIT License. See [LICENSE](LICENSE) for full details.
