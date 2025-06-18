"""
Main Application Class
"""

import asyncio
import logging
from typing import Optional

from ..capture.screen_capture import ScreenCapture
from ..vision.pattern_detector import PatternDetector
from ..ai.sentiment_analyzer import SentimentAnalyzer
from ..ai.price_predictor import PricePredictor
from ..data.market_data import MarketDataManager
from ..api.websocket_server import WebSocketServer
from ..config.settings import Settings

class TradingOverlayApp:
    """Main application orchestrator"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.screen_capture: Optional[ScreenCapture] = None
        self.pattern_detector: Optional[PatternDetector] = None
        self.sentiment_analyzer: Optional[SentimentAnalyzer] = None
        self.price_predictor: Optional[PricePredictor] = None
        self.market_data: Optional[MarketDataManager] = None
        self.websocket_server: Optional[WebSocketServer] = None
        
        # State
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing AI Trading Overlay System...")
        
        # Initialize components
        self.screen_capture = ScreenCapture(self.settings)
        self.pattern_detector = PatternDetector(self.settings)
        self.sentiment_analyzer = SentimentAnalyzer(self.settings)
        self.price_predictor = PricePredictor(self.settings)
        self.market_data = MarketDataManager(self.settings)
        self.websocket_server = WebSocketServer(self.settings)
        
        # Start WebSocket server
        await self.websocket_server.start()
        
        self.logger.info("All components initialized successfully")
    
    async def run(self):
        """Run the main application loop"""
        await self.initialize()
        
        self.running = True
        self.logger.info("Starting main application loop...")
        
        try:
            # Start background tasks
            tasks = [
                asyncio.create_task(self._screen_capture_loop()),
                asyncio.create_task(self._analysis_loop()),
                asyncio.create_task(self._data_update_loop()),
            ]
            
            # Wait for all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def _screen_capture_loop(self):
        """Main screen capture loop"""
        while self.running:
            try:
                # Capture screen
                image = await self.screen_capture.capture()
                
                if image is not None:
                    # Detect patterns
                    patterns = await self.pattern_detector.analyze(image)
                    
                    # Broadcast to frontend
                    await self.websocket_server.broadcast({
                        'type': 'patterns',
                        'data': patterns
                    })
                
                await asyncio.sleep(self.settings.CAPTURE_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Screen capture error: {e}")
                await asyncio.sleep(1)
    
    async def _analysis_loop(self):
        """Main AI analysis loop"""
        while self.running:
            try:
                # Get current market data
                market_data = await self.market_data.get_current_data()
                
                # Analyze sentiment
                sentiment = await self.sentiment_analyzer.analyze()
                
                # Generate predictions
                predictions = await self.price_predictor.predict(market_data, sentiment)
                
                # Broadcast results
                await self.websocket_server.broadcast({
                    'type': 'analysis',
                    'data': {
                        'sentiment': sentiment,
                        'predictions': predictions,
                        'timestamp': asyncio.get_event_loop().time()
                    }
                })
                
                await asyncio.sleep(self.settings.PREDICTION_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Analysis error: {e}")
                await asyncio.sleep(5)
    
    async def _data_update_loop(self):
        """Market data update loop"""
        while self.running:
            try:
                await self.market_data.update()
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Data update error: {e}")
                await asyncio.sleep(10)
    
    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up resources...")
        self.running = False
        
        if self.websocket_server:
            await self.websocket_server.stop()
        
        self.logger.info("Cleanup completed")
