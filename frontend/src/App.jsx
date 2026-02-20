import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import BoardListPage from './pages/BoardListPage';
import PostListPage from './pages/PostListPage';
import PostDetailPage from './pages/PostDetailPage';
import PostWritePage from './pages/PostWritePage';

function App() {
  useLocation(); // navigate 시 App 재렌더링 보장
  const token = localStorage.getItem('token');

  return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={token ? <BoardListPage /> : <Navigate to="/login" />} />
        <Route path="/boards/:boardId" element={token ? <PostListPage /> : <Navigate to="/login" />} />
        <Route path="/posts/:postId" element={<PostDetailPage />} />
        <Route path="/boards/:boardId/write" element={token ? <PostWritePage /> : <Navigate to="/login" />} />
      </Routes>
  );
}

export default App;
