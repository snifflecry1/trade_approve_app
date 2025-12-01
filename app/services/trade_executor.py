from app.entities.trade_detail import TradeDetail
from typing import Optional
import logging
import random

logger = logging.getLogger(__name__)

class TradeExecutor:
    def execute_trade(
        self, 
        trade: TradeDetail, 
        strike: Optional[float] = None
    ) -> TradeDetail:
        """
        Execute a trade with a counterparty and set the strike price.
        
        This simulates sending a trade to an external counterparty for execution
        and receiving back the actual strike rate at which the trade executed.
        
        Args:
            trade: The approved trade to execute.
            strike: The actual strike price from execution. If None, generates
                   a simulated strike based on the notional amount.
        
        Returns:
            TradeDetail: Updated trade with strike price set.
        """
        if trade.strike is not None:
            raise ValueError(f"Trade already has strike set: {trade.strike}")
        
        # Simulate getting strike from counterparty if not provided
        if strike is None:
            # Generate realistic strike (e.g., exchange rate around 1.0 +/- 10%)
            strike = round(random.uniform(0.9, 1.1), 4)
            logger.info(f"Simulated execution strike: {strike}")
        
        # Update the trade with the execution strike
        trade.strike = strike
        
        logger.info(f"Trade executed with strike: {strike}")
        return trade