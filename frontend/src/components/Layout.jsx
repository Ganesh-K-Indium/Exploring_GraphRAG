import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Search, 
  Upload, 
  Database, 
  Info,
  Activity 
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { checkHealth } from '../services/api';

const Layout = ({ children }) => {
  const location = useLocation();
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const status = await checkHealth();
        setHealthStatus(status);
      } catch (error) {
        setHealthStatus({ status: 'unhealthy', error: error.message });
      }
    };
    
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const navigation = [
    { name: 'Home', path: '/', icon: Home },
    { name: 'Query', path: '/query', icon: Search },
    { name: 'Ingest', path: '/ingest', icon: Upload },
    { name: 'Entities', path: '/entities', icon: Database },
    { name: 'About', path: '/about', icon: Info },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Graph RAG for 10-K
                </h1>
                <p className="text-xs text-gray-500">Multimodal Financial Analysis</p>
              </div>
            </div>

            {/* Status indicator */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                healthStatus?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm text-gray-600">
                {healthStatus?.status === 'healthy' ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    isActive(item.path)
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="text-center text-sm text-gray-500">
            <p>
              Multimodal Graph RAG System • OpenAI GPT-4o • Neo4j • Qdrant
            </p>
            <p className="mt-1">
              Built with React + FastAPI • Multi-Vector Hybrid Search
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
