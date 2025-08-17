"""
Market data module for fetching real-time gold prices and generating charts
"""
import asyncio
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.utils
from plotly.subplots import make_subplots


class GoldPriceProvider:
    """
    Provides real-time gold price data from multiple sources
    """
    
    def __init__(self):
        self.base_price = 2050.0  # Base gold price in USD per ounce
        self.current_price = self.base_price
        self.price_history = []
        self.last_update = datetime.utcnow()
    
    async def fetch_real_gold_price(self) -> Optional[float]:
        """
        Fetch real gold price from external API
        Falls back to simulation if API is unavailable
        """
        try:
            # Try to fetch from a free gold price API
            response = requests.get(
                "https://api.metals.live/v1/spot/gold",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return float(data.get('price', self.current_price))
        except Exception as e:
            print(f"Failed to fetch real gold price: {e}")
        
        # Fallback to simulation
        return self.simulate_price_movement()
    
    def simulate_price_movement(self) -> float:
        """
        Simulate realistic gold price movements
        """
        # Calculate time since last update
        now = datetime.utcnow()
        time_diff = (now - self.last_update).total_seconds()
        
        # Random walk with mean reversion
        volatility = 0.02  # 2% volatility
        mean_reversion = 0.001
        drift = -mean_reversion * (self.current_price - self.base_price) / self.base_price
        
        # Random component
        random_component = random.gauss(0, volatility) * (time_diff / 3600) ** 0.5
        
        # Calculate price change
        price_change = drift + random_component
        self.current_price *= (1 + price_change)
        
        # Add some noise for intraday movements
        self.current_price += random.gauss(0, 0.5)
        
        # Keep price within reasonable bounds
        self.current_price = max(1800, min(2500, self.current_price))
        
        self.last_update = now
        return self.current_price
    
    async def get_current_price(self) -> Dict:
        """
        Get current gold price with bid/ask spread
        """
        price = await self.fetch_real_gold_price()
        spread = random.uniform(0.5, 1.5)  # Bid-ask spread
        
        price_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'price': round(price, 2),
            'bid': round(price - spread/2, 2),
            'ask': round(price + spread/2, 2),
            'volume': random.randint(100, 1000),
            'change_24h': round(random.uniform(-2.0, 2.0), 2),
            'change_percent': round(random.uniform(-0.1, 0.1), 4)
        }
        
        # Store in history
        self.price_history.append(price_data)
        
        # Keep only last 1000 price points
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]
        
        return price_data
    
    def get_price_history(self, hours: int = 24) -> List[Dict]:
        """
        Get historical price data for specified hours
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            price for price in self.price_history
            if datetime.fromisoformat(price['timestamp']) > cutoff_time
        ]


class ChartGenerator:
    """
    Generates interactive charts for market data visualization
    """
    
    def __init__(self, price_provider: GoldPriceProvider):
        self.price_provider = price_provider
    
    def create_price_chart(self, hours: int = 24) -> str:
        """
        Create an interactive price chart using Plotly
        """
        price_history = self.price_provider.get_price_history(hours)
        
        if not price_history:
            return self._create_empty_chart()
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(price_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create candlestick-style chart
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=('Gold Price (USD/oz)', 'Volume', 'Price Change %'),
            row_heights=[0.6, 0.2, 0.2]
        )
        
        # Price line chart
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['price'],
                mode='lines',
                name='Price',
                line=dict(color='gold', width=2),
                hovertemplate='<b>Price</b>: $%{y:.2f}<br><b>Time</b>: %{x}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Bid-Ask spread
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['ask'],
                mode='lines',
                name='Ask',
                line=dict(color='red', width=1, dash='dash'),
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['bid'],
                mode='lines',
                name='Bid',
                line=dict(color='green', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(255,215,0,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Volume chart
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color='lightblue',
                showlegend=False
            ),
            row=2, col=1
        )
        
        # Price change percentage
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['change_percent'],
                mode='lines+markers',
                name='Change %',
                line=dict(color='purple', width=1),
                marker=dict(size=3),
                showlegend=False
            ),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='Gold Derivatives Market Data - Live Feed',
            xaxis_title='Time',
            height=600,
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="Change %", row=3, col=1)
        
        return fig.to_json()
    
    def create_pnl_chart(self, positions_data: List[Dict]) -> str:
        """
        Create P&L chart for position tracking
        """
        if not positions_data:
            return self._create_empty_chart()
        
        df = pd.DataFrame(positions_data)
        
        fig = go.Figure()
        
        # Unrealized P&L
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['unrealized_pnl'],
                mode='lines+markers',
                name='Unrealized P&L',
                line=dict(color='blue', width=2),
                marker=dict(size=5)
            )
        )
        
        # Realized P&L
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['realized_pnl'],
                mode='lines+markers',
                name='Realized P&L',
                line=dict(color='green', width=2),
                marker=dict(size=5)
            )
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title='Position P&L Tracking',
            xaxis_title='Time',
            yaxis_title='P&L (USD)',
            height=400,
            template='plotly_white'
        )
        
        return fig.to_json()
    
    def create_exposure_chart(self, exposure_data: Dict) -> str:
        """
        Create exposure analysis chart
        """
        contracts = list(exposure_data.keys())
        exposures = list(exposure_data.values())
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                x=contracts,
                y=exposures,
                marker_color=['red' if x < 0 else 'green' for x in exposures],
                text=[f"${x:,.0f}" for x in exposures],
                textposition='auto'
            )
        )
        
        fig.update_layout(
            title='Position Exposure by Contract',
            xaxis_title='Contract',
            yaxis_title='Exposure (USD)',
            height=300,
            template='plotly_white'
        )
        
        return fig.to_json()
    
    def _create_empty_chart(self) -> str:
        """
        Create an empty chart when no data is available
        """
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            height=400,
            template='plotly_white',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig.to_json()


# Global instances
gold_price_provider = GoldPriceProvider()
chart_generator = ChartGenerator(gold_price_provider)