import { TradingApi, LeveragePosition } from '../api/apiClient';

import { api } from '../ui/api/apiClient';

export class AgentTaskManager {
  // Centralized log method for consistent logging
  private static logTaskActivity(taskId: string, message: string, level: 'info' | 'warn' | 'error' = 'info') {
    const timestamp = new Date().toISOString();
    const logMsg = `[${timestamp}] Task ${taskId}: ${message}`;
    
    switch(level) {
      case 'warn':
        console.warn(logMsg);
        break;
      case 'error':
        console.error(logMsg);
        break;
      default:
        console.log(logMsg);
    }
  }
  
  static async processTask(task: any): Promise<any> {
    try {
      switch (task.task_type) {
        case 'get_user_positions':
          return await this.handleGetUserPositions(task);
        case 'execute_trade':
          return await this.handleExecuteTrade(task);
        case 'price_check':
          return await this.handlePriceCheck(task);
        case 'check_wallet_balance':
          return await this.handleCheckWalletBalance(task);
        case 'trade_initiate':
          return await this.handleTradeInitiate(task);
        case 'get_user_trades':
          return await this.handleGetUserTrades(task);
        case 'get_social_insights':
          return await this.handleGetSocialInsights(task);
        // Graceful fallback for unimplemented task types
        default:
          console.warn(`Task type '${task.task_type}' not implemented in frontend yet. Proxying to backend.`);
          return await this.proxyTaskToBackend(task);
      }
    } catch (error) {
      console.error('AgentTaskManager Error:', error);
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        task_id: task.task_id,
        task_type: task.task_type
      };
    }
  }

  private static async handleGetUserPositions(task: any): Promise<any> {
    try {
      const userIdentifier = task.content?.user_id || 'default';
      const positionType = task.content?.position_type;

      this.logTaskActivity(task.task_id, `Fetching ${positionType || 'all'} positions for user ${userIdentifier}`);

      // Construct the URL with query parameters to avoid RequestInit type issues
      const queryParams = positionType ? `?type=${encodeURIComponent(positionType)}` : '';
      const positions = await api.get(`/api/trading/positions/${userIdentifier}${queryParams}`);

      this.logTaskActivity(task.task_id, `Found ${positions.data.length} positions`);

      return {
        status: 'success',
        task_id: task.task_id,
        positions: positions.data,
        analysis: this.analyzePositions(positions.data)
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Error fetching positions: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to fetch positions'
      };
    }
  }

  static async handleExecuteTrade(task: any): Promise<any> {
    try {
      const tradeParams = task.content || {};
      this.logTaskActivity(task.task_id, `Executing ${tradeParams.side} trade for ${tradeParams.size} ${tradeParams.market}`);
      
      // Forward to backend API
      const response = await api.post('/api/trading/execute', tradeParams);
      
      this.logTaskActivity(task.task_id, `Trade execution completed: ${response.data.success ? 'Success' : 'Failed'}`);
      
      return {
        status: response.data.success ? 'success' : 'error',
        task_id: task.task_id,
        ...response.data
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Trade execution error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to execute trade'
      };
    }
  }

  static async handlePriceCheck(task: any): Promise<any> {
    try {
      const { market, token } = task.content || {};
      const symbol = market || token || '';
      
      if (!symbol) {
        throw new Error('Market or token symbol is required');
      }
      
      this.logTaskActivity(task.task_id, `Checking price for ${symbol}`);
      
      const response = await api.get(`/api/trading/price/${encodeURIComponent(symbol)}`);
      
      return {
        status: 'success',
        task_id: task.task_id,
        symbol,
        price: response.data.price,
        timestamp: response.data.timestamp || new Date().toISOString()
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Price check error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to check price'
      };
    }
  }

  static async handleCheckWalletBalance(task: any): Promise<any> {
    try {
      const { user_id, token } = task.content || {};
      
      if (!user_id) {
        throw new Error('User ID is required');
      }
      
      this.logTaskActivity(task.task_id, `Checking wallet balance for user ${user_id}${token ? ` (${token})` : ''}`);
      
      // Construct URL with query parameters to avoid RequestInit type issues
      const queryParams = token ? `?token=${encodeURIComponent(token)}` : '';
      const response = await api.get(`/api/wallet/balance/${user_id}${queryParams}`);
      
      return {
        status: 'success',
        task_id: task.task_id,
        user_id,
        balances: response.data.balances
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Balance check error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to check wallet balance'
      };
    }
  }

  static async handleTradeInitiate(task: any): Promise<any> {
    try {
      const tradeParams = task.content || {};
      this.logTaskActivity(task.task_id, `Initiating trade setup for ${tradeParams.market || 'unknown market'}`);
      
      // Just validate parameters and return success - actual execution happens with execute_trade
      const requiredParams = ['market', 'side'];
      const missingParams = requiredParams.filter(param => !tradeParams[param]);
      
      if (missingParams.length > 0) {
        throw new Error(`Missing required parameters: ${missingParams.join(', ')}`);
      }
      
      return {
        status: 'success',
        task_id: task.task_id,
        message: 'Trade initiation validated successfully',
        validated_params: tradeParams
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Trade initiation error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to initiate trade'
      };
    }
  }

  static async handleGetUserTrades(task: any): Promise<any> {
    try {
      const { user_id, limit, offset } = task.content || {};
      
      if (!user_id) {
        throw new Error('User ID is required');
      }
      
      this.logTaskActivity(task.task_id, `Fetching trade history for user ${user_id}`);
      
      // Construct URL with query parameters to avoid RequestInit type issues
      let queryParams = '';
      if (limit || offset) {
        const queryParts = [];
        if (limit) queryParts.push(`limit=${encodeURIComponent(limit)}`);
        if (offset) queryParts.push(`offset=${encodeURIComponent(offset)}`);
        queryParams = `?${queryParts.join('&')}`;
      }
      
      const response = await api.get(`/api/trading/history/${user_id}${queryParams}`);
      
      return {
        status: 'success',
        task_id: task.task_id,
        user_id,
        trades: response.data.trades || [],
        total: response.data.total || response.data.trades?.length || 0
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Get trades error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to get trade history'
      };
    }
  }

  static async handleGetSocialInsights(task: any): Promise<any> {
    try {
      const { query, topic, limit } = task.content || {};
      
      this.logTaskActivity(task.task_id, `Fetching social insights${query ? ` for query "${query}"` : topic ? ` on topic "${topic}"` : ''}`);
      
      // Build endpoint and query parameters
      let endpoint = '/api/social-media';
      const queryParts = [];
      
      if (query) {
        endpoint += '/sentiment';
        queryParts.push(`query=${encodeURIComponent(query)}`);
      } else if (topic) {
        endpoint += '/influential';
        queryParts.push(`topic=${encodeURIComponent(topic)}`);
      } else {
        endpoint += '/trending';
      }
      
      if (limit) queryParts.push(`limit=${encodeURIComponent(limit)}`);
      
      // Append query parameters to URL
      const queryString = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
      const response = await api.get(`${endpoint}${queryString}`);
      
      return {
        status: 'success',
        task_id: task.task_id,
        ...response.data.data
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Social insights error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to get social insights'
      };
    }
  }

  static async proxyTaskToBackend(task: any): Promise<any> {
    try {
      this.logTaskActivity(task.task_id, `Proxying unimplemented task type '${task.task_type}' to backend`);
      
      // Generic proxy to backend for unimplemented task types
      const response = await api.post('/api/agent/task', task);
      
      return {
        ...response.data,
        task_id: task.task_id,
        proxied: true
      };
    } catch (error) {
      this.logTaskActivity(task.task_id, `Proxy task error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error');
      return {
        status: 'error',
        task_id: task.task_id,
        error: error instanceof Error ? error.message : 'Failed to proxy task to backend'
      };
    }
  }
  

  private static analyzePositions(positions: any[]): any {
    if (!positions || positions.length === 0) {
      return {
        total_positions: 0,
        total_value: 0,
        risk_level: 'No Positions'
      };
    }

    const totalPositions = positions.length;
    const totalValue = positions.reduce((sum, pos) => sum + (pos.amount * pos.currentPrice), 0);
    const leveragePositions = positions.filter(pos => pos.type === 'leverage');
    const avgLeverage = leveragePositions.length > 0 
      ? leveragePositions.reduce((sum, pos) => sum + pos.leverage, 0) / leveragePositions.length 
      : 0;

    // Simple risk calculation
    const riskScore = avgLeverage * totalPositions;
    const riskLevel = riskScore < 5 ? 'Low Risk' 
      : riskScore < 15 ? 'Moderate Risk' 
      : 'High Risk';

    return {
      total_positions: totalPositions,
      total_value: totalValue,
      avg_leverage: avgLeverage,
      risk_level: riskLevel
    };
  }
}
