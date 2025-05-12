// Position Types
export interface BasePosition {
  id: string;
  token: string;
  type: 'leverage' | 'spot';
  amount: number;
  entryPrice: number;
  currentPrice: number;
  openTimestamp: number;
  unrealizedPnl?: number;
}

export interface LeveragePosition extends BasePosition {
  leverage: number;
  liquidationPrice?: number;
  marginRatio?: number;
}

export interface SpotPosition extends BasePosition {}

export interface UserPositionsResponse {
  positions: BasePosition[];
  metadata?: any;
}

import { API_ENDPOINTS } from './apiClient';
import { getAuthToken } from '../utils/authUtils';

export const TradingApi = {
  getUserLeveragePositions: async (): Promise<UserPositionsResponse> => {
    try {
      const response = await fetch(API_ENDPOINTS.USER.LEVERAGE_POSITIONS, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Unknown error');
      }
      
      return {
        positions: data.positions || [],
        metadata: data.metadata || {}
      };
    } catch (error) {
      console.error('Error fetching leverage positions:', error);
      throw error;
    }
  },

  getUserSpotPositions: async (): Promise<UserPositionsResponse> => {
    try {
      const response = await fetch(API_ENDPOINTS.USER.SPOT_POSITIONS, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!data.success) {
        throw new Error(data.message || 'Unknown error');
      }
      
      return {
        positions: data.positions || [],
        metadata: data.metadata || {}
      };
    } catch (error) {
      console.error('Error fetching spot positions:', error);
      throw error;
    }
  }
};
