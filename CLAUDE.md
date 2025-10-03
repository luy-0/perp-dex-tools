# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modular cryptocurrency trading bot that supports multiple exchanges (EdgeX, Backpack, Paradex, Aster, Lighter, GRVT). The bot implements an automated trading strategy that places orders and automatically closes them at a profit, primarily designed for high-volume trading.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For GRVT exchange support (requires Python 3.10+)
pip install grvt-pysdk

# For Paradex exchange support (requires separate environment)
python3 -m venv para_env
source para_env/bin/activate  # Windows: para_env\Scripts\activate
pip install -r para_requirements.txt
```

### Running the Bot
```bash
# Basic command structure
python runbot.py --exchange <exchange> --ticker <ticker> --quantity <amount> --take-profit <percentage> --max-orders <limit> --wait-time <seconds>

# Example: EdgeX ETH trading
python runbot.py --exchange edgex --ticker ETH --quantity 0.1 --take-profit 0.02 --max-orders 40 --wait-time 450

# Example: With grid step control
python runbot.py --exchange edgex --ticker ETH --quantity 0.1 --take-profit 0.02 --max-orders 40 --wait-time 450 --grid-step 0.5
```

### Testing
```bash
# Run tests (single test file available)
python tests/test_query_retry.py
```

## Code Architecture

### Core Components

1. **Entry Point**: `runbot.py`
   - Command-line argument parsing
   - Environment configuration loading
   - Trading bot initialization

2. **Trading Engine**: `trading_bot.py`
   - `TradingBot` class: Main trading logic
   - `TradingConfig` dataclass: Configuration management
   - `OrderMonitor` dataclass: Order state tracking

3. **Exchange Abstraction**: `exchanges/`
   - `base.py`: Abstract `BaseExchangeClient` class defining the interface
   - `factory.py`: `ExchangeFactory` for dynamic exchange client creation
   - Individual exchange implementations: `edgex.py`, `backpack.py`, `paradex.py`, `aster.py`, `lighter.py`, `grvt.py`

4. **Utilities**: `helpers/`
   - `logger.py`: Trading and debug logging
   - `telegram_bot.py`: Telegram notifications
   - `lark_bot.py`: Lark/Feishu notifications

### Key Design Patterns

- **Factory Pattern**: Exchange clients are created dynamically through `ExchangeFactory`
- **Abstract Base Class**: All exchange clients inherit from `BaseExchangeClient` for consistent interface
- **Dataclass Configuration**: Trading parameters managed through `TradingConfig` dataclass
- **Retry Decorator**: `@query_retry` for handling API failures with exponential backoff

### Exchange Integration Requirements

Each exchange client must implement:
- `get_price()`: Get current market price
- `get_contract_id()`: Resolve ticker to contract ID
- `place_order()`: Place orders with standardized parameters
- `get_order_status()`: Check order status
- `cancel_order()`: Cancel specific orders
- `get_open_orders()`: List active orders
- `get_positions()`: Get current positions

### Configuration Management

- Environment variables loaded from `.env` file (customizable via `--env-file`)
- Exchange-specific credentials required for each supported exchange
- Optional notification integrations (Telegram, Lark)
- Logging configuration (console, file, CSV trading logs)

## Important Notes

- **Python Version**: Requires Python 3.8+ (3.10-3.12 recommended, required for GRVT)
- **No Built-in Testing Framework**: No pytest/unittest setup - only basic test file
- **No Linting Configuration**: No flake8/pylint/black configuration present
- **Risk Management**: Strategy does not include stop-loss - relies on grid step and position limits
- **Multi-account Support**: Supports multiple accounts via separate `.env` files
- **Exchange-specific Features**: Some exchanges have special modes (e.g., Aster boost mode)