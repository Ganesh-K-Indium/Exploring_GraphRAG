import { useState } from 'react';
import { Upload, Loader2, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { uploadAndIngest } from '../services/api';

const Ingest = () => {
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState({
    ticker: '',
    filing_date: '',
    fiscal_year: new Date().getFullYear()
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid PDF file');
      setFile(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    if (!metadata.ticker) {
      setError('Please enter a company ticker');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadAndIngest(file, metadata);
      setResult(response);
      
      // Reset form
      setFile(null);
      setMetadata({
        ticker: '',
        filing_date: '',
        fiscal_year: new Date().getFullYear()
      });
      
      // Reset file input
      const fileInput = document.getElementById('file-upload');
      if (fileInput) fileInput.value = '';
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Ingest 10-K Document</h1>
        <p className="text-gray-600">
          Upload a 10-K PDF to extract text, tables, images, entities, and relationships
        </p>
      </div>

      {/* Upload Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              10-K PDF File *
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-500 transition-colors">
              <input
                id="file-upload"
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <Upload className="w-12 h-12 text-gray-400" />
                <span className="text-sm text-gray-600">
                  {file ? (
                    <span className="text-primary-600 font-medium">
                      {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                  ) : (
                    <>Click to upload or drag and drop</>
                  )}
                </span>
                <span className="text-xs text-gray-500">PDF up to 50MB</span>
              </label>
            </div>
          </div>

          {/* Metadata */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Ticker *
              </label>
              <input
                type="text"
                value={metadata.ticker}
                onChange={(e) => setMetadata({ ...metadata, ticker: e.target.value.toUpperCase() })}
                placeholder="e.g., AAPL"
                className="input-field"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fiscal Year *
              </label>
              <input
                type="number"
                value={metadata.fiscal_year}
                onChange={(e) => setMetadata({ ...metadata, fiscal_year: e.target.value })}
                placeholder="e.g., 2024"
                className="input-field"
                required
                min="2000"
                max="2030"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filing Date (optional)
              </label>
              <input
                type="date"
                value={metadata.filing_date}
                onChange={(e) => setMetadata({ ...metadata, filing_date: e.target.value })}
                className="input-field"
              />
            </div>
          </div>

          {/* Processing Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-900 mb-2">
              What will be extracted:
            </h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>✓ Text content with section detection</li>
              <li>✓ Tables with structured data and descriptions</li>
              <li>✓ Images and financial charts (analyzed with GPT-4o Vision)</li>
              <li>✓ Entities (companies, people, metrics, products, risks)</li>
              <li>✓ Relationships and graph connections</li>
              <li>✓ Multi-vector embeddings (dense, sparse, ColBERT)</li>
            </ul>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !file}
            className="btn-primary w-full md:w-auto flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing... This may take several minutes</span>
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                <span>Upload and Ingest</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="card bg-red-50 border border-red-200">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-red-900">Error</div>
              <div className="text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}

      {/* Success Display */}
      {result && (
        <div className="card bg-green-50 border border-green-200">
          <div className="flex items-start space-x-3 mb-4">
            <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold text-green-900">
                Ingestion Complete!
              </h3>
              <p className="text-green-700 mt-1">{result.message}</p>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {result.stats?.num_chunks || 0}
              </div>
              <div className="text-sm text-gray-600">Chunks Created</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {result.stats?.num_entities || 0}
              </div>
              <div className="text-sm text-gray-600">Entities Extracted</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {result.stats?.num_relationships || 0}
              </div>
              <div className="text-sm text-gray-600">Relationships Found</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-gray-900">
                {result.stats?.num_embeddings || 0}
              </div>
              <div className="text-sm text-gray-600">Embeddings Generated</div>
            </div>
          </div>

          {/* Document Info */}
          <div className="mt-4 p-4 bg-white rounded-lg">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <FileText className="w-4 h-4" />
              <span>Document ID: {result.document_id}</span>
              <span>•</span>
              <span>{result.file_name}</span>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="card bg-gray-50">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Tips for Best Results</h3>
        <ul className="space-y-2 text-sm text-gray-700">
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span>Use official 10-K PDFs from SEC EDGAR for best extraction quality</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span>Ensure ticker symbol matches the company in the document</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span>Provide accurate fiscal year for proper temporal analysis</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span>Ingestion typically takes 2-10 minutes depending on document length</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-primary-600 mt-1">•</span>
            <span>You can ingest multiple years of the same company for historical analysis</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Ingest;
