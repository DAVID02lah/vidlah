"""
AI Sentiment Analysis Module
"""

import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import re

from ..config.settings import Settings

class SentimentAnalyzer:
    """Multi-modal sentiment analysis from news, social media, and insider trades"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentiment sources
        self.news_sources = []
        self.social_sources = ['reddit', 'twitter']
        
    async def analyze(self, symbol: str = "SPY") -> Dict:
        """Perform comprehensive sentiment analysis"""
        try:
            # Get sentiment from different sources
            news_sentiment = await self._analyze_news_sentiment(symbol)
            social_sentiment = await self._analyze_social_sentiment(symbol)
            insider_sentiment = await self._analyze_insider_activity(symbol)
            
            # Combine sentiments with weights
            overall_sentiment = self._combine_sentiments(
                news_sentiment, 
                social_sentiment, 
                insider_sentiment
            )
            
            return {
                'overall_score': overall_sentiment['score'],
                'overall_label': overall_sentiment['label'],
                'confidence': overall_sentiment['confidence'],
                'breakdown': {
                    'news': news_sentiment,
                    'social': social_sentiment,
                    'insider': insider_sentiment
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Sentiment analysis failed: {e}")
            return self._default_sentiment()
    
    async def _analyze_news_sentiment(self, symbol: str) -> Dict:
        """Analyze news sentiment using FinBERT or similar"""
        try:
            # This would integrate with news APIs and FinBERT
            # For now, returning mock data
            return {
                'score': 0.65,  # -1 to 1 scale
                'label': 'positive',
                'confidence': 0.78,
                'article_count': 15,
                'key_themes': ['earnings beat', 'market expansion', 'analyst upgrade']
            }
            
        except Exception as e:
            self.logger.error(f"News sentiment analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.5}
    
    async def _analyze_social_sentiment(self, symbol: str) -> Dict:
        """Analyze social media sentiment from Reddit/Twitter"""
        try:
            reddit_sentiment = await self._get_reddit_sentiment(symbol)
            twitter_sentiment = await self._get_twitter_sentiment(symbol)
            
            # Combine social sentiments
            combined_score = (reddit_sentiment['score'] + twitter_sentiment['score']) / 2
            
            return {
                'score': combined_score,
                'label': self._score_to_label(combined_score),
                'confidence': 0.65,
                'mention_count': reddit_sentiment['mentions'] + twitter_sentiment['mentions'],
                'trending': combined_score > 0.3,
                'reddit': reddit_sentiment,
                'twitter': twitter_sentiment
            }
            
        except Exception as e:
            self.logger.error(f"Social sentiment analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.5}
    
    async def _get_reddit_sentiment(self, symbol: str) -> Dict:
        """Get sentiment from Reddit discussions"""
        # This would use PRAW to get Reddit data
        return {
            'score': 0.45,
            'mentions': 127,
            'top_posts': ['Bullish on tech sector', 'Great earnings report']
        }
    
    async def _get_twitter_sentiment(self, symbol: str) -> Dict:
        """Get sentiment from Twitter"""
        # This would use Twitter API
        return {
            'score': 0.32,
            'mentions': 89,
            'trending_hashtags': ['#bullish', '#earnings']
        }
    
    async def _analyze_insider_activity(self, symbol: str) -> Dict:
        """Analyze insider trading activity"""
        try:
            # This would check SEC EDGAR and congressional trading data
            return {
                'score': 0.2,  # Positive = buying, Negative = selling
                'label': 'slightly_positive',
                'confidence': 0.85,
                'recent_activity': [
                    {'type': 'buy', 'amount': 100000, 'date': '2025-06-15'},
                    {'type': 'buy', 'amount': 50000, 'date': '2025-06-14'}
                ],
                'congress_activity': True,
                'insider_count': 3
            }
            
        except Exception as e:
            self.logger.error(f"Insider analysis failed: {e}")
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.5}
    
    def _combine_sentiments(self, news: Dict, social: Dict, insider: Dict) -> Dict:
        """Combine different sentiment sources with weights"""
        # Weight different sources
        news_weight = 0.5
        social_weight = 0.3
        insider_weight = 0.2
        
        # Calculate weighted score
        combined_score = (
            news['score'] * news_weight +
            social['score'] * social_weight +
            insider['score'] * insider_weight
        )
        
        # Calculate confidence based on agreement
        scores = [news['score'], social['score'], insider['score']]
        confidence = 1.0 - (max(scores) - min(scores)) / 2.0  # Lower confidence if scores disagree
        
        return {
            'score': combined_score,
            'label': self._score_to_label(combined_score),
            'confidence': max(0.3, confidence)  # Minimum confidence of 0.3
        }
    
    def _score_to_label(self, score: float) -> str:
        """Convert numerical score to label"""
        if score > 0.5:
            return 'very_positive'
        elif score > 0.1:
            return 'positive'
        elif score > -0.1:
            return 'neutral'
        elif score > -0.5:
            return 'negative'
        else:
            return 'very_negative'
    
    def _default_sentiment(self) -> Dict:
        """Return default sentiment when analysis fails"""
        return {
            'overall_score': 0.0,
            'overall_label': 'neutral',
            'confidence': 0.3,
            'breakdown': {
                'news': {'score': 0.0, 'label': 'neutral'},
                'social': {'score': 0.0, 'label': 'neutral'},
                'insider': {'score': 0.0, 'label': 'neutral'}
            },
            'timestamp': datetime.now().isoformat(),
            'error': 'Analysis failed, using default values'
        }
