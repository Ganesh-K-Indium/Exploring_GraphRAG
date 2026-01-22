import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Loader2, Building2, User, MapPin, DollarSign, Package, AlertTriangle } from 'lucide-react';
import { getEntities } from '../services/api';

const Entities = () => {
  const navigate = useNavigate();
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [entityType, setEntityType] = useState('');
  const [limit, setLimit] = useState(100);

  const entityTypes = [
    { value: '', label: 'All Types', icon: Database },
    { value: 'Company', label: 'Companies', icon: Building2 },
    { value: 'Person', label: 'People', icon: User },
    { value: 'Location', label: 'Locations', icon: MapPin },
    { value: 'FinancialMetric', label: 'Financial Metrics', icon: DollarSign },
    { value: 'Product', label: 'Products', icon: Package },
    { value: 'RiskFactor', label: 'Risk Factors', icon: AlertTriangle },
  ];

  useEffect(() => {
    fetchEntities();
  }, [entityType, limit]);

  const fetchEntities = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getEntities({
        entity_type: entityType || undefined,
        limit
      });
      setEntities(response.entities || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getEntityIcon = (type) => {
    const entityTypeConfig = entityTypes.find(et => et.value === type);
    return entityTypeConfig?.icon || Database;
  };

  const handleEntityClick = (entity) => {
    if (entity.type === 'Company' && entity.ticker) {
      navigate(`/company/${entity.ticker}`);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Entity Browser</h1>
        <p className="text-gray-600">
          Explore entities extracted from 10-K documents in the knowledge graph
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Entity Type
            </label>
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value)}
              className="input-field"
            >
              {entityTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Limit: {limit}
            </label>
            <input
              type="range"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              min="10"
              max="500"
              step="10"
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="card bg-red-50 border border-red-200">
          <div className="text-red-700">{error}</div>
        </div>
      )}

      {/* Entity List */}
      {!loading && !error && (
        <div>
          <div className="card mb-4">
            <div className="text-sm text-gray-600">
              Showing <span className="font-semibold text-gray-900">{entities.length}</span> entities
              {entityType && ` of type ${entityTypes.find(t => t.value === entityType)?.label}`}
            </div>
          </div>

          {entities.length === 0 ? (
            <div className="card text-center py-12">
              <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Entities Found</h3>
              <p className="text-gray-600">
                Ingest some 10-K documents to populate the knowledge graph
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {entities.map((entity, index) => {
                const EntityIcon = getEntityIcon(entity.type);
                const isClickable = entity.type === 'Company' && entity.ticker;

                return (
                  <div
                    key={index}
                    onClick={() => isClickable && handleEntityClick(entity)}
                    className={`card ${isClickable ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''}`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <EntityIcon className="w-5 h-5 text-primary-600" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold text-gray-900 truncate">
                          {entity.name}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1">
                          {entity.type}
                        </p>
                        
                        {/* Additional properties */}
                        <div className="mt-2 space-y-1">
                          {entity.ticker && (
                            <div className="text-xs">
                              <span className="text-gray-500">Ticker:</span>{' '}
                              <span className="font-medium text-gray-700">{entity.ticker}</span>
                            </div>
                          )}
                          {entity.sector && (
                            <div className="text-xs">
                              <span className="text-gray-500">Sector:</span>{' '}
                              <span className="text-gray-700">{entity.sector}</span>
                            </div>
                          )}
                          {entity.role && (
                            <div className="text-xs">
                              <span className="text-gray-500">Role:</span>{' '}
                              <span className="text-gray-700">{entity.role}</span>
                            </div>
                          )}
                          {entity.value && (
                            <div className="text-xs">
                              <span className="text-gray-500">Value:</span>{' '}
                              <span className="text-gray-700">
                                {entity.value} {entity.unit}
                              </span>
                            </div>
                          )}
                          {entity.fiscal_year && (
                            <div className="text-xs">
                              <span className="text-gray-500">FY:</span>{' '}
                              <span className="text-gray-700">{entity.fiscal_year}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Entities;
