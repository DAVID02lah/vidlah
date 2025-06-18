"""
AI Trading Overlay System - Main Application Entry Point
"""

import asyncio
import logging
from pathlib import Path

from src.core.application import TradingOverlayApp
from src.utils.logger import setup_logging
from src.config.settings import Settings

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Load settings
    settings = Settings()
    
    logger.info("Starting AI Trading Overlay System")
    logger.info(f"Version: {settings.APP_VERSION}")
    
    # Initialize and run the application
    app = TradingOverlayApp(settings)
    
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()
