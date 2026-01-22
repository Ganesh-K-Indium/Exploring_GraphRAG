import { Link } from 'react-router-dom';
import { Search, Upload, Database, TrendingUp, Network, Sparkles } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: Sparkles,
      title: 'Multimodal Extraction',
      description: 'Extracts text, tables, images, and charts from 10-K PDFs using GPT-4o Vision',
      color: 'text-purple-600 bg-purple-100'
    },
    {
      icon: Network,
      title: 'Graph + Vector Hybrid',
      description: 'Combines Neo4j knowledge graph with Qdrant vector database for powerful queries',
      color: 'text-blue-600 bg-blue-100'
    },
    {
      icon: TrendingUp,
      title: 'Multi-Year Analysis',
      description: 'Ingest multiple years and analyze historical trends, YoY changes, and patterns',
      color: 'text-green-600 bg-green-100'
    },
    {
      icon: Search,
      title: 'Adaptive Search',
      description: 'Dense + Sparse + ColBERT embeddings with query-adaptive fusion strategies',
      color: 'text-yellow-600 bg-yellow-100'
    }
  ];

  const quickActions = [
    {
      title: 'Query Documents',
      description: 'Ask questions about your 10-K filings',
      path: '/query',
      icon: Search,
      color: 'bg-primary-600 hover:bg-primary-700'
    },
    {
      title: 'Ingest New 10-K',
      description: 'Upload and process a new filing',
      path: '/ingest',
      icon: Upload,
      color: 'bg-green-600 hover:bg-green-700'
    },
    {
      title: 'Browse Entities',
      description: 'Explore the knowledge graph',
      path: '/entities',
      icon: Database,
      color: 'bg-purple-600 hover:bg-purple-700'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Multimodal Graph RAG for 10-K Analysis
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Extract insights from SEC 10-K filings using advanced multimodal AI, 
          graph databases, and multi-vector search
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.path}
              to={action.path}
              className={`${action.color} text-white rounded-lg p-6 transition-all transform hover:scale-105 shadow-md`}
            >
              <Icon className="w-8 h-8 mb-3" />
              <h3 className="text-lg font-semibold mb-2">{action.title}</h3>
              <p className="text-sm opacity-90">{action.description}</p>
            </Link>
          );
        })}
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="card">
                <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats Section */}
      <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border border-primary-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-3xl font-bold text-primary-900">3</div>
            <div className="text-sm text-primary-700 mt-1">Vector Types</div>
            <div className="text-xs text-primary-600 mt-1">Dense + Sparse + ColBERT</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-900">2</div>
            <div className="text-sm text-primary-700 mt-1">Databases</div>
            <div className="text-xs text-primary-600 mt-1">Neo4j + Qdrant</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-900">∞</div>
            <div className="text-sm text-primary-700 mt-1">Years Supported</div>
            <div className="text-xs text-primary-600 mt-1">Historical Analysis</div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="card">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Getting Started</h3>
        <ol className="space-y-3 text-gray-700">
          <li className="flex items-start">
            <span className="font-semibold text-primary-600 mr-2">1.</span>
            <span>
              <strong>Ingest Documents:</strong> Upload your 10-K PDF files with metadata (ticker, fiscal year)
            </span>
          </li>
          <li className="flex items-start">
            <span className="font-semibold text-primary-600 mr-2">2.</span>
            <span>
              <strong>Query the System:</strong> Ask questions about revenue, risks, strategy, or any aspect
            </span>
          </li>
          <li className="flex items-start">
            <span className="font-semibold text-primary-600 mr-2">3.</span>
            <span>
              <strong>Explore Entities:</strong> Browse the knowledge graph to see extracted entities and relationships
            </span>
          </li>
          <li className="flex items-start">
            <span className="font-semibold text-primary-600 mr-2">4.</span>
            <span>
              <strong>Analyze Trends:</strong> Compare metrics across years for historical insights
            </span>
          </li>
        </ol>
      </div>
    </div>
  );
};

export default Home;
