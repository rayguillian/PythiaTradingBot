import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface PerformanceData {
    summary: {
        total_pnl: number;
        total_trades: number;
        win_rate: number;
        profit_factor: number;
        sharpe_ratio: number;
        sortino_ratio: number;
        max_drawdown: number;
        current_drawdown: number;
    };
    strategy_performance: {
        strategy_name: string;
        symbol: string;
        interval: string;
        total_return: number;
        sharpe_ratio: number;
        max_drawdown: number;
        win_rate: number;
        profit_factor: number;
    }[];
    recent_trades: {
        timestamp: string;
        strategy: string;
        symbol: string;
        type: string;
        pnl: number;
        status: string;
    }[];
    timestamp: string;
}

const PythiaDashboard: React.FC = () => {
    const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPerformanceData = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await axios.get<PerformanceData>('http://localhost:8000/api/performance');
                setPerformanceData(response.data);
            } catch (err) {
                setError('Failed to fetch performance data');
                console.error('Error fetching performance data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchPerformanceData();
        const interval = setInterval(fetchPerformanceData, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading && !performanceData) return <div>Loading...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!performanceData?.summary) return <div>No data available</div>;

    const { summary, strategy_performance, recent_trades } = performanceData;

    return (
        <div className="pythia-dashboard">
            <h1>Pythia Dashboard</h1>
            
            {/* Summary Section */}
            <div className="summary-section">
                <h2>Portfolio Summary</h2>
                <div className="summary-stats">
                    <div className="stat-item">
                        <label>Total P&L</label>
                        <span className={`value ${summary.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                            {summary.total_pnl?.toFixed(2)}%
                        </span>
                    </div>
                    <div className="stat-item">
                        <label>Total Trades</label>
                        <span className="value">{summary.total_trades || 0}</span>
                    </div>
                    <div className="stat-item">
                        <label>Win Rate</label>
                        <span className="value">{summary.win_rate?.toFixed(2)}%</span>
                    </div>
                    <div className="stat-item">
                        <label>Profit Factor</label>
                        <span className="value">{summary.profit_factor?.toFixed(2)}</span>
                    </div>
                    <div className="stat-item">
                        <label>Sharpe Ratio</label>
                        <span className="value">{summary.sharpe_ratio?.toFixed(2)}</span>
                    </div>
                    <div className="stat-item">
                        <label>Sortino Ratio</label>
                        <span className="value">{summary.sortino_ratio?.toFixed(2)}</span>
                    </div>
                    <div className="stat-item">
                        <label>Max Drawdown</label>
                        <span className="value negative">{summary.max_drawdown?.toFixed(2)}%</span>
                    </div>
                    <div className="stat-item">
                        <label>Current Drawdown</label>
                        <span className="value negative">{summary.current_drawdown?.toFixed(2)}%</span>
                    </div>
                </div>
            </div>

            {/* Strategy Performance Table */}
            <div className="strategy-performance-section">
                <h2>Strategy Performance</h2>
                <div className="table-container">
                    <table className="performance-table">
                        <thead>
                            <tr>
                                <th>Strategy</th>
                                <th>Symbol</th>
                                <th>Interval</th>
                                <th>Total Return (%)</th>
                                <th>Sharpe Ratio</th>
                                <th>Max Drawdown (%)</th>
                                <th>Win Rate (%)</th>
                                <th>Profit Factor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {strategy_performance?.map((data, index) => (
                                <tr key={index}>
                                    <td>{data.strategy_name}</td>
                                    <td>{data.symbol}</td>
                                    <td>{data.interval}</td>
                                    <td>{(data.total_return * 100).toFixed(2)}%</td>
                                    <td>{data.sharpe_ratio.toFixed(2)}</td>
                                    <td>{(data.max_drawdown * 100).toFixed(2)}%</td>
                                    <td>{(data.win_rate * 100).toFixed(1)}%</td>
                                    <td>{data.profit_factor.toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Recent Trades Section */}
            <div className="recent-trades-section">
                <h2>Recent Trades</h2>
                <div className="table-container">
                    <table className="trades-table">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Strategy</th>
                                <th>Symbol</th>
                                <th>Type</th>
                                <th>P&L</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recent_trades?.map((trade, index) => (
                                <tr key={index}>
                                    <td>{new Date(trade.timestamp).toLocaleString()}</td>
                                    <td>{trade.strategy}</td>
                                    <td>{trade.symbol}</td>
                                    <td className={trade.type.toLowerCase()}>{trade.type}</td>
                                    <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                                        {trade.pnl.toFixed(2)}%
                                    </td>
                                    <td>{trade.status}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="last-update">
                Last updated: {new Date(performanceData.timestamp).toLocaleString()}
            </div>
        </div>
    );
};

export default PythiaDashboard;
