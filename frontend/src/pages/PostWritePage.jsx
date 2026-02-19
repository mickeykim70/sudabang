import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import Header from '../components/Header';

export default function PostWritePage() {
  const { boardId } = useParams();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [source, setSource] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post(`/boards/${boardId}/posts`, {
        title,
        content,
        source: source || '자체판단',
      });

      const postId = response.data.id;

      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        try {
          await api.post(`/posts/${postId}/attachments`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
        } catch (fileError) {
          console.error('파일 업로드 실패:', fileError);
        }
      }

      navigate(`/posts/${postId}`);
    } catch (err) {
      setError(err.response?.data?.detail || '글 작성 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Header title="글 작성" />
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">글 작성</h1>
        {error && <div className="bg-red-100 text-red-700 p-3 rounded mb-4">{error}</div>}
        <form onSubmit={handleSubmit} className="bg-white rounded shadow-md p-6">
          <div className="mb-4">
            <label className="block font-bold mb-2">제목</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded"
              placeholder="제목을 입력하세요"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block font-bold mb-2">본문 (Markdown)</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded font-mono"
              placeholder="# 제목&#10;&#10;본문을 입력하세요. Markdown 형식을 사용할 수 있습니다."
              rows="10"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block font-bold mb-2">출처</label>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded"
              placeholder="URL 또는 자체판단"
            />
          </div>
          <div className="mb-6">
            <label className="block font-bold mb-2">파일 첨부 (선택)</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full px-4 py-2 border border-gray-300 rounded"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? '작성 중...' : '등록'}
          </button>
        </form>
      </div>
    </div>
  );
}
