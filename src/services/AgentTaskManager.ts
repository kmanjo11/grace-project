import { TradingApi, LeveragePosition } from '../api/apiClient';

export class AgentTaskManager {
  static async processTask(task: any): Promise<any> {
    try {
      switch (task.task_type) {
        case 'get_user_positions':
          return await this.handleGetUserPositions(task);
        // Add more task type handlers as needed
        default:
          throw new Error(`Unsupported task type: ${task.task_type}`);
      }
    } catch (error) {
      console.error('AgentTaskManager Error:', error);
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  private static async handleGetUserPositions(task: any): Promise<any> {
    const { user_identifier, position_type } = task.content;
    
    try {
      const positions = await TradingApi.getUserPositions(user_identifier, position_type);
      
      // Basic position analysis
      const analysis = this.analyzePositions(positions);
      
      return {
        status: 'success',
        positions: positions,
        analysis: analysis
      };
    } catch (error) {
      console.error('Get User Positions Error:', error);
      return {
        status: 'error',
        error: error instanceof Error ? error.message : 'Failed to retrieve positions'
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
