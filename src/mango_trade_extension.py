"""
Mango V4 Trade Extension for Grace Trading System

This module provides an optional, non-invasive extension to existing trading capabilities
using Mango V4 as an additional data source and trading option.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from mango_explorer_v4 import Client, Cluster
from solana.rpc.async_api import AsyncClient

class MangoTradeExtension:
    """
    A lightweight extension to provide additional trading insights 
    without modifying existing trade infrastructure.
    """
    
    def __init__(
        self, 
        cluster: str = 'devnet', 
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize Mango V4 trade extension.
        
        :param cluster: Solana cluster to connect to
        :param logger: Optional logger for tracking events
        """
        self._logger = logger or logging.getLogger(__name__)
        
        # Determine cluster URL
        if cluster == 'mainnet':
            cluster_url = 'https://api.mainnet-beta.solana.com'
        elif cluster == 'devnet':
            cluster_url = 'https://api.devnet.solana.com'
        else:
            raise ValueError(f"Unsupported cluster: {cluster}")
        
        # Initialize clients
        self._solana_client = AsyncClient(cluster_url)
        self._mango_client = Client(
            cluster=Cluster.mainnet if cluster == 'mainnet' else Cluster.devnet
        )
    
    async def get_market_insights(
        self, 
        symbols: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Retrieve market insights without interfering with existing trade logic.
        
        :param symbols: Optional list of symbols to get insights for
        :return: Dictionary of market insights
        """
        try:
            # Fetch group details
            group = await self._mango_client.get_group()
            
            # Collect market insights
            market_insights = {}
            
            for market in group.perp_markets:
                # Only process specified symbols if provided
                if symbols and market.name not in symbols:
                    continue
                
                market_insights[market.name] = {
                    'symbol': market.name,
                    'max_leverage': market.max_leverage,
                    'base_asset': market.base_token,
                    'quote_asset': market.quote_token,
                    'additional_data': {
                        'open_interest': market.open_interest,
                        'funding_rate': market.funding_rate
                    }
                }
            
            return market_insights
        
        except Exception as e:
            self._logger.error(f"Error fetching Mango market insights: {e}")
            return {}
    
    def generate_trade_recommendation(
        self, 
        market_insights: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate trade recommendations based on Mango market insights.
        
        :param market_insights: Market insights from get_market_insights
        :return: Trade recommendations dictionary
        """
        recommendations = {}
        
        for symbol, insight in market_insights.items():
            # Basic recommendation logic
            recommendation = {
                'symbol': symbol,
                'recommendation': 'neutral',
                'confidence': 0.5,
                'reason': 'Mango V4 market data analysis'
            }
            
            # Example simple recommendation logic
            if insight.get('additional_data', {}).get('funding_rate', 0) > 0:
                recommendation.update({
                    'recommendation': 'sell',
                    'confidence': 0.7,
                    'reason': 'Positive funding rate suggests potential market correction'
                })
            elif insight.get('additional_data', {}).get('open_interest', 0) > 1000000:
                recommendation.update({
                    'recommendation': 'buy',
                    'confidence': 0.6,
                    'reason': 'High open interest indicates strong market interest'
                })
            
            recommendations[symbol] = recommendation
        
        return recommendations

# Async example usage
async def main():
    trade_extension = MangoTradeExtension(cluster='devnet')
    
    # Get market insights
    insights = await trade_extension.get_market_insights()
    
    # Generate recommendations
    recommendations = trade_extension.generate_trade_recommendation(insights)
    
    print("Mango V4 Market Insights:", insights)
    print("Trade Recommendations:", recommendations)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
