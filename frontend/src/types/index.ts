export interface ParameterConfig {
    name: string;
    description: string;
    type: 'number' | 'string' | 'boolean';
    default?: any;
    min?: number;
    max?: number;
    options?: string[];
}

export interface Strategy {
    name: string;
    description: string;
    parameters: Record<string, ParameterConfig>;
    status: 'active' | 'inactive';
}

export interface Trade {
    timestamp: string;
    strategy: string;
    symbol: string;
    type: 'LONG' | 'SHORT';
    pnl: number;
    status: 'OPEN' | 'CLOSED';
}

export interface StrategyPerformance {
    strategy_name: string;
    symbol: string;
    interval: string;
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    profit_factor: number;
}

export interface PerformanceSummary {
    total_pnl: number;
    total_trades: number;
    win_rate: number;
    current_drawdown: number;
}

export interface PerformanceData {
    summary: PerformanceSummary;
    strategy_performance: StrategyPerformance[];
    recent_trades: Trade[];
}
