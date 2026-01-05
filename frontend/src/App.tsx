import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { ReviewSession } from './pages/ReviewSession';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/review/:id" element={<ReviewSession />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
