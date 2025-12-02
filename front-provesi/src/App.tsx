import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Warehouses from './pages/Warehouses';
import Items from './pages/Items';
import AuditLogs from './pages/AuditLogs';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/productos" element={<Products />} />
          <Route path="/bodegas" element={<Warehouses />} />
          <Route path="/items" element={<Items />} />
          <Route path="/auditoria" element={<AuditLogs />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
