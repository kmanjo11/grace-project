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

export class TradingApi {
  static getUserPositions(userIdentifier: string, positionType?: string): Promise<BasePosition[]>;
  static getUserLeveragePositions(): Promise<UserPositionsResponse>;
}

export interface UserPositionsResponse {
  positions: BasePosition[];
  metadata?: any;
}

export class AgentTaskManager {
  static processTask(task: any): Promise<any>;
}
