import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import Header from '../components/Header';
import PostCard from '../components/PostCard';

export default function PostListPage() {
  const { boardId } = useParams();
  const navigate = useNavigate();
  const [posts, setPosts] = useState([]);
  const [boardName, setBoardName] = useState('');
  const [loading, setLoading] = useState(true);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchPosts();
  }, [boardId]);

  const fetchPosts = async () => {
    try {
      const boardRes = await api.get(`/boards/${boardId}`);
      setBoardName(boardRes.data?.name || '');
    } catch (error) {
      console.error('게시판 조회 실패:', error);
    }

    try {
      const response = await api.get(`/boards/${boardId}/posts`);
      setPosts(response.data);
    } catch (error) {
      console.error('게시글 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center py-8">로딩 중...</div>;

  return (
    <div>
      <Header title={`${boardName} - 게시글 목록`} />
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">{boardName}</h1>
          {user?.id && (
            <button
              onClick={() => navigate(`/boards/${boardId}/write`)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              글 쓰기
            </button>
          )}
        </div>
        <div className="space-y-4">
          {posts.map((post) => (
            <PostCard
              key={post.id}
              post={post}
              onClick={() => navigate(`/posts/${post.id}`)}
            />
          ))}
          {posts.length === 0 && <p className="text-gray-500">글이 없습니다.</p>}
        </div>
      </div>
    </div>
  );
}
