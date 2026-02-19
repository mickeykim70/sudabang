import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Header from '../components/Header';

export default function BoardListPage() {
  const [boards, setBoards] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBoards();
  }, []);

  const fetchBoards = async () => {
    try {
      const response = await api.get('/boards');
      setBoards(response.data);
    } catch (error) {
      console.error('게시판 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">로딩 중...</div>;

  return (
    <div>
      <Header title="수다방 - 게시판 목록" />
      <div className="max-w-6xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">게시판</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {boards.map((board) => (
            <div
              key={board.id}
              onClick={() => navigate(`/boards/${board.id}`)}
              className="p-4 border border-gray-300 rounded cursor-pointer hover:shadow-lg transition"
            >
              <h2 className="text-xl font-bold mb-2">{board.name}</h2>
              <p className="text-gray-600 text-sm">{board.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
