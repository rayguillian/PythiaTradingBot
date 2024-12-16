import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Strategy } from '../types';

const StrategyConfiguration: React.FC = () => {
    const [strategies, setStrategies] = useState<Record<string, Strategy>>({});
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedStrategy, setSelectedStrategy] = useState<string>('');
    const [parameters, setParameters] = useState<Record<string, string>>({});

    useEffect(() => {
        const fetchStrategies = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await axios.get('http://localhost:8000/api/strategies');
                console.log('API Response:', response.data);
                setStrategies(response.data.strategies || {});
            } catch (err) {
                setError('Failed to fetch strategies');
                console.error('Error fetching strategies:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchStrategies();
    }, []);

    const handleStrategyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const strategyId = event.target.value;
        console.log('Selected Strategy ID:', strategyId);
        console.log('Available Strategies:', strategies);
        
        setSelectedStrategy(strategyId);
        if (strategyId && strategies[strategyId]) {
            console.log('Strategy Config:', strategies[strategyId]);
            const defaultParams: Record<string, string> = {};
            const strategyParams = strategies[strategyId].parameters;
            Object.entries(strategyParams).forEach(([key, config]) => {
                defaultParams[key] = config.default?.toString() || '';
            });
            setParameters(defaultParams);
        } else {
            setParameters({});
        }
    };

    const handleParameterChange = (paramName: string, value: string) => {
        setParameters(prev => ({
            ...prev,
            [paramName]: value
        }));
    };

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        if (!selectedStrategy) return;

        try {
            setLoading(true);
            setError(null);
            await axios.post('http://localhost:8000/api/strategies/configure', {
                strategy_id: selectedStrategy,
                parameters
            });
            // Show success message or redirect
        } catch (err) {
            setError('Failed to configure strategy');
            console.error('Error configuring strategy:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading && Object.keys(strategies).length === 0) return <div>Loading...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="strategy-configuration">
            <h2>Strategy Configuration</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="strategy-select">Select Strategy:</label>
                    <select
                        id="strategy-select"
                        value={selectedStrategy}
                        onChange={handleStrategyChange}
                        className="form-control"
                    >
                        <option value="">Select a strategy...</option>
                        {Object.entries(strategies).map(([id, strategy]) => (
                            <option key={id} value={id}>
                                {strategy.name}
                            </option>
                        ))}
                    </select>
                </div>

                {selectedStrategy && strategies[selectedStrategy] && (
                    <div className="parameters-section">
                        <h3>Parameters</h3>
                        {Object.entries(strategies[selectedStrategy].parameters).map(([paramName, config]) => (
                            <div key={paramName} className="form-group">
                                <label htmlFor={paramName}>{config.name || paramName}:</label>
                                <input
                                    type={config.type === 'number' ? 'number' : 'text'}
                                    id={paramName}
                                    value={parameters[paramName] || ''}
                                    onChange={(e) => handleParameterChange(paramName, e.target.value)}
                                    className="form-control"
                                    placeholder={config.description}
                                    min={config.type === 'number' ? config.min : undefined}
                                    max={config.type === 'number' ? config.max : undefined}
                                />
                                {config.description && (
                                    <small className="form-text text-muted">{config.description}</small>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={!selectedStrategy || loading}
                >
                    {loading ? 'Configuring...' : 'Configure Strategy'}
                </button>
            </form>
        </div>
    );
};

export default StrategyConfiguration;
