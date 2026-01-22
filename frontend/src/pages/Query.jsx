import { useState } from 'react';
import { Search, Loader2, FileText, Table2, BarChart3 } from 'lucide-react';
import { querySystem } from '../services/api';
import ReactMarkdown from 'react-markdown';

const Query = () => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    ticker: '',
    fiscal_year: '',
    section: ''
  });
  const [topK, setTopK] = useState(10);
  const [strategy, setStrategy] = useState('adaptive');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const exampleQueries = [
    "What are Apple's main revenue sources?",
    "How has revenue grown over the past 3 years?",
    "What are the key risk factors for this company?",
    "Compare R&D spending with competitors",
    "Show me the revenue breakdown table"
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build filters object
      const queryFilters = {};
      if (filters.ticker) queryFilters.company_ticker = filters.ticker;
      if (filters.fiscal_year) queryFilters.fiscal_year = parseInt(filters.fiscal_year);
      if (filters.section) queryFilters.section = filters.section;

      const response = await querySystem({
        query,
        top_k: topK,
        filters: Object.keys(queryFilters).length > 0 ? queryFilters : null,
        strategy
      });

      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const setExampleQuery = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Query System</h1>
        <p className="text-gray-600">
          Ask questions about your 10-K filings using adaptive multi-vector search
        </p>
      </div>

      {/* Query Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Main Query Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What was Apple's revenue in fiscal year 2024?"
              className="input-field min-h-[100px]"
              required
            />
          </div>

          {/* Example Queries */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Example Queries
            </label>
            <div className="flex flex-wrap gap-2">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setExampleQuery(example)}
                  className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Ticker (optional)
              </label>
              <input
                type="text"
                value={filters.ticker}
                onChange={(e) => setFilters({ ...filters, ticker: e.target.value.toUpperCase() })}
                placeholder="e.g., AAPL"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fiscal Year (optional)
              </label>
              <input
                type="number"
                value={filters.fiscal_year}
                onChange={(e) => setFilters({ ...filters, fiscal_year: e.target.value })}
                placeholder="e.g., 2024"
                className="input-field"
                min="2000"
                max="2030"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Section (optional)
              </label>
              <select
                value={filters.section}
                onChange={(e) => setFilters({ ...filters, section: e.target.value })}
                className="input-field"
              >
                <option value="">All Sections</option>
                <option value="Item_1">Item 1 - Business</option>
                <option value="Item_1A">Item 1A - Risk Factors</option>
                <option value="Item_7">Item 7 - MD&A</option>
                <option value="Item_8">Item 8 - Financial Statements</option>
              </select>
            </div>
          </div>

          {/* Advanced Options */}
          <details className="border border-gray-200 rounded-lg p-4">
            <summary className="cursor-pointer font-medium text-gray-700">
              Advanced Options
            </summary>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Results: {topK}
                </label>
                <input
                  type="range"
                  value={topK}
                  onChange={(e) => setTopK(parseInt(e.target.value))}
                  min="5"
                  max="30"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search Strategy
                </label>
                <select
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                  className="input-field"
                >
                  <option value="adaptive">Adaptive (Recommended)</option>
                  <option value="rrf">RRF Fusion</option>
                  <option value="weighted">Weighted Fusion</option>
                </select>
              </div>
            </div>
          </details>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !query}
            className="btn-primary w-full md:w-auto flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Search</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="card bg-red-50 border border-red-200">
          <div className="flex items-start space-x-3">
            <div className="text-red-600 font-semibold">Error:</div>
            <div className="text-red-700">{error}</div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-6">
          {/* Answer */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Answer</h2>
            <div className="prose max-w-none">
              <ReactMarkdown>{result.answer}</ReactMarkdown>
            </div>
          </div>

          {/* Sources */}
          {result.sources && result.sources.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Sources ({result.sources.length})
              </h3>
              <div className="space-y-2">
                {result.sources.map((source, index) => (
                  <div
                    key={index}
                    className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <FileText className="w-4 h-4 text-gray-500 mt-1 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{source}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Context Preview */}
          {result.context && (
            <details className="card">
              <summary className="cursor-pointer font-medium text-gray-900">
                Retrieved Context Details
              </summary>
              <div className="mt-4 space-y-4">
                {/* Text Chunks */}
                {result.context.text_chunks?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-2">
                      <FileText className="w-4 h-4" />
                      <span>Text Chunks ({result.context.text_chunks.length})</span>
                    </h4>
                    <div className="space-y-2">
                      {result.context.text_chunks.slice(0, 3).map((chunk, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded text-sm">
                          <div className="font-medium text-gray-700 mb-1">
                            {chunk.section} • Score: {chunk.score?.toFixed(3)}
                          </div>
                          <p className="text-gray-600 line-clamp-2">{chunk.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Tables */}
                {result.context.tables?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-2">
                      <Table2 className="w-4 h-4" />
                      <span>Tables ({result.context.tables.length})</span>
                    </h4>
                    <p className="text-sm text-gray-600">
                      {result.context.tables.length} table(s) retrieved
                    </p>
                  </div>
                )}

                {/* Charts */}
                {result.context.charts?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center space-x-2">
                      <BarChart3 className="w-4 h-4" />
                      <span>Charts ({result.context.charts.length})</span>
                    </h4>
                    <p className="text-sm text-gray-600">
                      {result.context.charts.length} chart(s) retrieved
                    </p>
                  </div>
                )}
              </div>
            </details>
          )}

          {/* Usage Stats */}
          {result.usage && (
            <div className="card bg-gray-50">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Model: {result.model}</span>
                <span className="text-gray-600">
                  Tokens: {result.usage.input_tokens} in / {result.usage.output_tokens} out
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Query;
