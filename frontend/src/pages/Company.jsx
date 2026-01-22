import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Building2, Loader2, User, TrendingUp, MapPin, AlertCircle } from 'lucide-react';
import { getCompany } from '../services/api';

const Company = () => {
  const { ticker } = useParams();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCompany();
  }, [ticker]);

  const fetchCompany = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getCompany(ticker);
      setCompany(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="font-semibold text-red-900">Error Loading Company</div>
            <div className="text-red-700">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="card text-center py-12">
        <Building2 className="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Company Not Found</h3>
        <p className="text-gray-600">
          No data found for ticker {ticker}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-start space-x-4">
          <div className="w-16 h-16 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
            <Building2 className="w-8 h-8 text-primary-600" />
          </div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{company.name}</h1>
            <div className="flex items-center space-x-4 mt-2">
              <span className="badge badge-primary">
                {company.ticker}
              </span>
              {company.sector && (
                <span className="text-sm text-gray-600">
                  {company.sector}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Financial Metrics */}
      {company.metrics && company.metrics.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5" />
            <span>Financial Metrics</span>
            <span className="text-sm font-normal text-gray-500">
              ({company.metrics.length})
            </span>
          </h2>
          
          <div className="space-y-3">
            {company.metrics.map((metric, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{metric.name}</h3>
                    <div className="mt-1 space-y-1">
                      {metric.value && (
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Value:</span> {metric.value} {metric.unit}
                        </div>
                      )}
                      {metric.fiscal_year && (
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">Fiscal Year:</span> {metric.fiscal_year}
                        </div>
                      )}
                      {metric.yoy_change && (
                        <div className="text-sm text-gray-600">
                          <span className="font-medium">YoY Change:</span> {metric.yoy_change}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Executives */}
      {company.executives && company.executives.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <User className="w-5 h-5" />
            <span>Executive Team</span>
            <span className="text-sm font-normal text-gray-500">
              ({company.executives.length})
            </span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {company.executives.map((exec, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-medium text-gray-900">{exec.name}</h3>
                {exec.role && (
                  <p className="text-sm text-gray-600 mt-1">{exec.role}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Subsidiaries */}
      {company.subsidiaries && company.subsidiaries.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <MapPin className="w-5 h-5" />
            <span>Subsidiaries</span>
            <span className="text-sm font-normal text-gray-500">
              ({company.subsidiaries.length})
            </span>
          </h2>
          
          <div className="flex flex-wrap gap-2">
            {company.subsidiaries.map((subsidiary, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
              >
                {subsidiary}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!company.metrics || company.metrics.length === 0) &&
       (!company.executives || company.executives.length === 0) &&
       (!company.subsidiaries || company.subsidiaries.length === 0) && (
        <div className="card text-center py-12">
          <p className="text-gray-600">
            No detailed information available for this company yet.
            <br />
            Ingest more 10-K documents to populate this data.
          </p>
        </div>
      )}
    </div>
  );
};

export default Company;
