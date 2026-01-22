import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Query from './pages/Query';
import Ingest from './pages/Ingest';
import Entities from './pages/Entities';
import Company from './pages/Company';
import About from './pages/About';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/query" element={<Query />} />
          <Route path="/ingest" element={<Ingest />} />
          <Route path="/entities" element={<Entities />} />
          <Route path="/company/:ticker" element={<Company />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
