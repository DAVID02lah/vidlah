"""
AI Price Prediction Module using LSTM and Multi-modal Analysis
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

from ..config.settings import Settings

@dataclass
class PricePrediction:
    """Price prediction result"""
    timeframe: str  # '15m', '1h', '4h', '1d', '2d'
    min_price: float
    max_price: float
    avg_price: float
    probability: float
    confidence: float
    explanation: str

class PricePredictor:
    """AI-powered price prediction using LSTM and multi-modal analysis"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Prediction timeframes
        self.timeframes = ['15m', '1h', '4h', '1d', '2d']
        
        # Mock model weights (in real implementation, these would be trained models)
        self.model_weights = {
            'technical': self.settings.TECHNICAL_WEIGHT,
            'sentiment': self.settings.SENTIMENT_WEIGHT
        }
    
    async def predict(self, market_data: Dict, sentiment_data: Dict, symbol: str = "SPY") -> List[Dict]:
        """Generate price predictions for multiple timeframes"""
        try:
            predictions = []
            
            for timeframe in self.timeframes:
                prediction = await self._predict_timeframe(
                    timeframe, market_data, sentiment_data, symbol
                )
                predictions.append(self._prediction_to_dict(prediction))
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Price prediction failed: {e}")
            return self._default_predictions()
    
    async def _predict_timeframe(self, timeframe: str, market_data: Dict, 
                                sentiment_data: Dict, symbol: str) -> PricePrediction:
        """Predict price for specific timeframe"""
        try:
            # Get current price (mock)
            current_price = market_data.get('current_price', 400.0)
            
            # Calculate technical indicators influence
            technical_score = self._calculate_technical_score(market_data)
            
            # Get sentiment influence
            sentiment_score = sentiment_data.get('overall_score', 0.0)
            
            # Combine scores with weights
            combined_score = (
                technical_score * self.model_weights['technical'] +
                sentiment_score * self.model_weights['sentiment']
            )
            
            # Calculate price range based on timeframe and volatility
            volatility = self._get_volatility_for_timeframe(timeframe)
            price_range = current_price * volatility * (1 + abs(combined_score))
            
            # Calculate predictions
            if combined_score > 0:  # Bullish
                min_price = current_price
                max_price = current_price + price_range
                avg_price = current_price + (price_range * 0.6)
            else:  # Bearish
                min_price = current_price - price_range
                max_price = current_price
                avg_price = current_price - (price_range * 0.6)
            
            # Calculate probability and confidence
            probability = min(0.9, 0.5 + abs(combined_score) * 0.4)
            confidence = min(0.95, 0.6 + abs(combined_score) * 0.3)
            
            # Generate explanation
            explanation = self._generate_explanation(
                combined_score, technical_score, sentiment_score, timeframe
            )
            
            return PricePrediction(
                timeframe=timeframe,
                min_price=round(min_price, 2),
                max_price=round(max_price, 2),
                avg_price=round(avg_price, 2),
                probability=round(probability, 3),
                confidence=round(confidence, 3),
                explanation=explanation
            )
            
        except Exception as e:
            self.logger.error(f"Timeframe prediction failed for {timeframe}: {e}")
            return self._default_prediction(timeframe)
    
    def _calculate_technical_score(self, market_data: Dict) -> float:
        """Calculate technical analysis score"""
        # This would use real technical indicators
        # For now, using mock calculation
        
        rsi = market_data.get('rsi', 50)
        macd = market_data.get('macd', 0)
        volume_ratio = market_data.get('volume_ratio', 1.0)
        
        # Simple scoring based on indicators
        rsi_score = (rsi - 50) / 50  # Normalize RSI
        macd_score = np.tanh(macd)  # Normalize MACD
        volume_score = min(1.0, (volume_ratio - 1.0) * 2)  # Volume boost
        
        # Combine scores
        technical_score = (rsi_score * 0.4 + macd_score * 0.4 + volume_score * 0.2)
        
        return np.clip(technical_score, -1.0, 1.0)
    
    def _get_volatility_for_timeframe(self, timeframe: str) -> float:
        """Get expected volatility for timeframe"""
        volatility_map = {
            '15m': 0.005,  # 0.5%
            '1h': 0.01,    # 1%
            '4h': 0.02,    # 2%
            '1d': 0.03,    # 3%
            '2d': 0.05     # 5%
        }
        return volatility_map.get(timeframe, 0.02)
    
    def _generate_explanation(self, combined_score: float, technical_score: float, 
                            sentiment_score: float, timeframe: str) -> str:
        """Generate natural language explanation"""
        direction = "upward" if combined_score > 0 else "downward"
        strength = "strong" if abs(combined_score) > 0.5 else "moderate" if abs(combined_score) > 0.2 else "weak"
        
        # Technical explanation
        tech_explanation = ""
        if abs(technical_score) > 0.3:
            tech_trend = "bullish" if technical_score > 0 else "bearish"
            tech_explanation = f"Technical indicators show {tech_trend} momentum with "
            if technical_score > 0:
                tech_explanation += "RSI suggesting buying pressure and positive MACD crossover."
            else:
                tech_explanation += "RSI indicating oversold conditions and negative MACD divergence."
        else:
            tech_explanation = "Technical indicators are neutral with mixed signals."
        
        # Sentiment explanation
        sentiment_explanation = ""
        if abs(sentiment_score) > 0.2:
            sentiment_trend = "positive" if sentiment_score > 0 else "negative"
            sentiment_explanation = f"Market sentiment is {sentiment_trend} with "
            if sentiment_score > 0:
                sentiment_explanation += "bullish news flow and social media buzz supporting upward movement."
            else:
                sentiment_explanation += "bearish news sentiment and negative social media activity."
        else:
            sentiment_explanation = "Market sentiment remains neutral."
        
        # Combine explanations
        probability_pct = int(abs(combined_score) * 100)
        
        explanation = f"Based on {strength} {direction} signals, there's a {probability_pct}% probability of {direction} movement in the {timeframe} timeframe. {tech_explanation} {sentiment_explanation}"
        
        return explanation
    
    def _prediction_to_dict(self, prediction: PricePrediction) -> Dict:
        """Convert prediction to dictionary"""
        return {
            'timeframe': prediction.timeframe,
            'min_price': prediction.min_price,
            'max_price': prediction.max_price,
            'avg_price': prediction.avg_price,
            'probability': prediction.probability,
            'confidence': prediction.confidence,
            'explanation': prediction.explanation,
            'timestamp': datetime.now().isoformat()
        }
    
    def _default_prediction(self, timeframe: str) -> PricePrediction:
        """Return default prediction when calculation fails"""
        return PricePrediction(
            timeframe=timeframe,
            min_price=395.0,
            max_price=405.0,
            avg_price=400.0,
            probability=0.5,
            confidence=0.3,
            explanation=f"Unable to generate reliable prediction for {timeframe} - using neutral forecast"
        )
    
    def _default_predictions(self) -> List[Dict]:
        """Return default predictions when analysis fails"""
        predictions = []
        for timeframe in self.timeframes:
            predictions.append(self._prediction_to_dict(self._default_prediction(timeframe)))
        return predictions
