import { Network, Database, Search, Sparkles, TrendingUp, Zap } from 'lucide-react';

const About = () => {
  const architecture = [
    {
      title: 'Multimodal Extraction',
      icon: Sparkles,
      description: 'Extracts text, tables, images, and charts from PDF documents',
      tech: ['pypdf', 'pdfplumber', 'PyMuPDF', 'GPT-4o Vision']
    },
    {
      title: 'Entity & Relationship Extraction',
      icon: Network,
      description: 'NER + LLM extraction of entities and their relationships',
      tech: ['spaCy NER', 'GPT-4o', 'Entity Resolution']
    },
    {
      title: 'Multi-Vector Embeddings',
      icon: Zap,
      description: 'Three-tier embedding for optimal retrieval',
      tech: ['Dense (OpenAI)', 'Sparse (SPLADE)', 'ColBERT']
    },
    {
      title: 'Hybrid Storage',
      icon: Database,
      description: 'Graph database + Vector database with bidirectional linking',
      tech: ['Neo4j', 'Qdrant', 'Cross-database linking']
    },
    {
      title: 'Adaptive Retrieval',
      icon: Search,
      description: 'Query classification with multi-vector fusion',
      tech: ['RRF Fusion', 'Weighted Fusion', 'Reranking']
    },
    {
      title: 'RAG Generation',
      icon: TrendingUp,
      description: 'Context-aware answer generation with citations',
      tech: ['GPT-4o', 'Multimodal Context', 'Source Attribution']
    }
  ];

  const features = [
    'Multimodal PDF extraction (text, tables, charts)',
    'Multi-vector hybrid search (dense + sparse + ColBERT)',
    'Graph + Vector database integration',
    'Adaptive query classification',
    'Multi-year historical analysis',
    'Entity and relationship extraction',
    'Automatic source citations',
    'Production-ready REST API'
  ];

  const techStack = [
    { category: 'Frontend', items: ['React 18', 'Vite', 'Tailwind CSS', 'React Router'] },
    { category: 'Backend', items: ['FastAPI', 'Python 3.10+', 'Asyncio', 'Pydantic'] },
    { category: 'AI/ML', items: ['OpenAI GPT-4o', 'SPLADE', 'ColBERT', 'spaCy'] },
    { category: 'Databases', items: ['Neo4j', 'Qdrant', 'Vector Indices', 'Graph Queries'] },
    { category: 'Infrastructure', items: ['Docker', 'Uvicorn', 'Axios', 'CORS'] }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">About This System</h1>
        <p className="text-gray-600">
          A production-ready Multimodal Graph RAG system for analyzing SEC 10-K financial reports
        </p>
      </div>

      {/* Architecture */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Architecture</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {architecture.map((component, index) => {
            const Icon = component.icon;
            return (
              <div key={index} className="card">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {component.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  {component.description}
                </p>
                <div className="flex flex-wrap gap-1">
                  {component.tech.map((tech, i) => (
                    <span key={i} className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Features */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {features.map((feature, index) => (
            <div key={index} className="flex items-start space-x-2">
              <div className="w-1.5 h-1.5 rounded-full bg-primary-600 mt-2 flex-shrink-0" />
              <span className="text-gray-700">{feature}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Technology Stack</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {techStack.map((stack, index) => (
            <div key={index} className="card">
              <h3 className="font-semibold text-gray-900 mb-3">{stack.category}</h3>
              <ul className="space-y-2">
                {stack.items.map((item, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-center space-x-2">
                    <span className="w-1 h-1 rounded-full bg-primary-600" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Flow */}
      <div className="card bg-gradient-to-br from-primary-50 to-primary-100 border border-primary-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Pipeline Flow</h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              1
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">PDF Upload</div>
              <div className="text-sm text-gray-600">User uploads 10-K document with metadata</div>
            </div>
          </div>
          
          <div className="ml-4 border-l-2 border-primary-300 h-6" />
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              2
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Multimodal Extraction</div>
              <div className="text-sm text-gray-600">Extract text, tables, images, charts</div>
            </div>
          </div>
          
          <div className="ml-4 border-l-2 border-primary-300 h-6" />
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              3
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Ontology Creation</div>
              <div className="text-sm text-gray-600">NER + LLM extract entities & relationships</div>
            </div>
          </div>
          
          <div className="ml-4 border-l-2 border-primary-300 h-6" />
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              4
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Multi-Vector Embedding</div>
              <div className="text-sm text-gray-600">Generate dense, sparse, and ColBERT vectors</div>
            </div>
          </div>
          
          <div className="ml-4 border-l-2 border-primary-300 h-6" />
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              5
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Hybrid Storage</div>
              <div className="text-sm text-gray-600">Store in Neo4j + Qdrant with linking</div>
            </div>
          </div>
          
          <div className="ml-4 border-l-2 border-primary-300 h-6" />
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              6
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">Query & Retrieve</div>
              <div className="text-sm text-gray-600">Adaptive multi-vector hybrid search</div>
            </div>
          </div>
          
          <div className="ml-4 border-l-2 border-primary-300 h-6" />
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold">
              7
            </div>
            <div className="flex-1">
              <div className="font-medium text-gray-900">RAG Generation</div>
              <div className="text-sm text-gray-600">GPT-4o generates answer with citations</div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance Stats */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Performance Characteristics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Extraction Speed</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Text: ~2-5s per 100 pages</li>
              <li>• Tables: ~0.5s per table</li>
              <li>• Images: ~1s per image</li>
              <li>• Charts (Vision): ~3-5s each</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Embedding Speed</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Dense: ~100 texts/sec</li>
              <li>• Sparse: ~50 texts/sec</li>
              <li>• ColBERT: ~20 texts/sec</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium text-gray-900 mb-2">Query Speed</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li>• Hybrid search: ~200-500ms</li>
              <li>• Graph enrichment: ~50-100ms</li>
              <li>• RAG generation: ~2-5s</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Links */}
      <div className="card bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Documentation</h2>
        <div className="space-y-2 text-sm text-gray-700">
          <div>📖 <span className="font-medium">README.md</span> - Complete system documentation</div>
          <div>🚀 <span className="font-medium">QUICKSTART.md</span> - 5-minute setup guide</div>
          <div>📊 <span className="font-medium">HISTORICAL_ANALYSIS_GUIDE.md</span> - Multi-year analysis</div>
          <div>🔧 <span className="font-medium">API Docs</span> - http://localhost:8000/docs</div>
        </div>
      </div>
    </div>
  );
};

export default About;
