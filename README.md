# Theseus Alpha 🔮

Theseus Alpha is an intelligent trading system built for the HyperLiquid blockchain that uses LLM-driven analysis to make trading decisions. Named after the mythological hero who navigated the labyrinth, our system navigates the complexities of crypto trading using artificial intelligence.

## System Architecture

[ARCHITECTURE_DIAGRAM.png]

The system follows a modular architecture focused on profile analysis, intelligent decision-making, and safe execution.

## Key Features

- 🧠 **AI-Driven Trading**: Uses GPT-4 for market analysis and trade decisions
- 📊 **Deep Profile Analysis**: Learns from both spot and perpetual trading history
- 🛡️ **Risk Management**: Built-in position sizing and exposure controls
- 🎯 **Smart Execution**: Optimized order execution with slippage protection
- 🔄 **Real-Time Adaptation**: Adjusts to changing market conditions

## Components

### Profilers

#### Spot Profiler
- Analyzes token holdings and trades
- Calculates risk metrics and portfolio concentration
- Determines trading style and patterns

#### Perpetual Profiler
- Analyzes leverage usage and position sizing
- Calculates win rates and profit ratios
- Determines risk appetite and experience level

### Profile Adjusters
- Customizes trading parameters
- Adapts to user preferences
- Manages risk tolerance settings

### LLM Trading Advisor
- Analyzes market conditions
- Generates trading recommendations
- Provides reasoning for each trade

### Trade Executor
- Validates and normalizes orders
- Manages execution timing
- Handles errors and retries

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/theseus_alpha.git
cd theseus_alpha

# Install dependencies using Poetry
poetry install

# Configure your environment
cp .env.example .env
```

## Configuration

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### HyperLiquid Configuration (config.json)
```json
{
    "secret_key": "your_hyperliquid_secret_key",
    "account_address": "your_account_address"
}
```

## Usage

```bash
# Run the trading system
poetry run python main.py
```

The system will:
1. Connect to HyperLiquid
2. Generate trading profiles
3. Adjust based on preferences
4. Get AI-driven trading advice
5. Execute trades with safety checks

## Trading Parameters

### Size Limits
- Minimum order: $10 USD
- Maximum order: $150 USD
- Size normalized based on available liquidity

### Supported Markets
- Spot: PURR/USDC (testnet)
- Perpetuals: Based on available market depth

### Safety Features
- Position size limits
- Slippage protection
- Execution timing controls
- Error handling and retries

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black .

# Check typing
poetry run mypy .
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Testing

Run the full test suite:
```bash
poetry run pytest
```

Run specific test categories:
```bash
poetry run pytest tests/test_profilers.py  # Test profilers
poetry run pytest tests/test_executor.py   # Test execution
```

## Credits

This project uses the official [HyperLiquid Python SDK](https://github.com/hyperliquid-dex/hyperliquid-python-sdk) and OpenAI's GPT-4.

## License

MIT License - see [LICENSE](LICENSE) for details.