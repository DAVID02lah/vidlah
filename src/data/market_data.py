"""
Market Data Manager - Real-time market data integration
"""

import logging
import asyncio
from typing import Dict, Optional
from datetime import datetime
import aiohttp

from ..config.settings import Settings

class MarketDataManager:
    """Manages real-time market data from multiple sources"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Data cache
        self.current_data = {}
        self.last_update = None
        
        # API endpoints
        self.data_sources = {
            'alpha_vantage': 'https://www.alphavantage.co/query',
            'finnhub': 'https://finnhub.io/api/v1',
            'yahoo': 'https://query1.finance.yahoo.com/v8/finance/chart'
        }
    
    async def get_current_data(self, symbol: str = "SPY") -> Dict:
        """Get current market data for symbol"""
        try:
            if self._is_data_stale():
                await self.update(symbol)
            
            return self.current_data.get(symbol, self._default_market_data())
            
        except Exception as e:
            self.logger.error(f"Failed to get current data: {e}")
            return self._default_market_data()
    
    async def update(self, symbol: str = "SPY"):
        """Update market data from APIs"""
        try:
            # Get data from multiple sources
            price_data = await self._fetch_price_data(symbol)
            technical_data = await self._fetch_technical_indicators(symbol)
            volume_data = await self._fetch_volume_data(symbol)
            
            # Combine all data
            combined_data = {
                **price_data,
                **technical_data,
                **volume_data,
                'last_updated': datetime.now().isoformat()
            }
            
            self.current_data[symbol] = combined_data
            self.last_update = datetime.now()
            
            self.logger.info(f"Updated market data for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Failed to update market data: {e}")
    
    async def _fetch_price_data(self, symbol: str) -> Dict:
        """Fetch current price data"""
        try:
            # This would integrate with real APIs
            # For now, returning mock data
            return {
                'current_price': 425.67,
                'open': 423.45,
                'high': 427.89,
                'low': 422.10,
                'previous_close': 424.32,
                'change': 1.35,
                'change_percent': 0.32
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch price data: {e}")
            return {'current_price': 400.0}
    
    async def _fetch_technical_indicators(self, symbol: str) -> Dict:
        """Fetch technical indicators"""
        try:
            # This would calculate or fetch real technical indicators
            return {
                'rsi': 62.5,
                'macd': 1.23,
                'macd_signal': 0.98,
                'macd_histogram': 0.25,
                'sma_20': 422.15,
                'sma_50': 418.67,
                'sma_200': 410.23,
                'bb_upper': 428.45,
                'bb_middle': 424.32,
                'bb_lower': 420.18,
                'volume_sma': 125000000
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch technical indicators: {e}")
            return {}
    
    async def _fetch_volume_data(self, symbol: str) -> Dict:
        """Fetch volume and liquidity data"""
        try:
            return {
                'volume': 145000000,
                'avg_volume': 125000000,
                'volume_ratio': 1.16,
                'dollar_volume': 61675000000
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch volume data: {e}")
            return {'volume': 100000000, 'volume_ratio': 1.0}
    
    def _is_data_stale(self, max_age_seconds: int = 30) -> bool:
        """Check if data needs updating"""
        if self.last_update is None:
            return True
        
        age = (datetime.now() - self.last_update).total_seconds()
        return age > max_age_seconds
    
    def _default_market_data(self) -> Dict:
        """Return default market data"""
        return {
            'current_price': 400.0,
            'open': 400.0,
            'high': 402.0,
            'low': 398.0,
            'previous_close': 399.5,
            'change': 0.5,
            'change_percent': 0.125,
            'rsi': 50.0,
            'macd': 0.0,
            'volume': 100000000,
            'volume_ratio': 1.0,
            'last_updated': datetime.now().isoformat(),
            'error': 'Using default data'
        }
