import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import api from '../api';
import Header from '../components/Header';
import CommentItem from '../components/CommentItem';

export default function PostDetailPage() {
  const { postId } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [commentContent, setCommentContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    fetchPost();
  }, [postId]);

  const fetchPost = async () => {
    try {
      const response = await api.get(`/posts/${postId}`);
      setPost(response.data);
      setComments(response.data.comments || []);
    } catch (error) {
      console.error('게시글 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!commentContent.trim()) return;

    setSubmitting(true);
    try {
      await api.post(`/posts/${postId}/comments`, { content: commentContent });
      setCommentContent('');
      fetchPost();
    } catch (error) {
      console.error('댓글 작성 실패:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="text-center py-8">로딩 중...</div>;
  if (!post) return <div className="text-center py-8">글을 찾을 수 없습니다.</div>;

  return (
    <div>
      <Header title={post.title} />
      <div className="max-w-4xl mx-auto p-6">
        <article className="bg-white rounded shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold mb-3">{post.title}</h1>
          <div className="text-gray-600 text-sm mb-4">
            <span>작성자: {post.author?.display_name}</span>
            <span className="mx-2">•</span>
            <span>{new Date(post.created_at).toLocaleDateString()}</span>
            <span className="mx-2">•</span>
            <span>조회: {post.view_count}</span>
          </div>
          {post.source && (
            <div className="mb-4 text-sm text-gray-500">
              <span>출처: </span>
              {(() => {
                const md = post.source.match(/^\[(.+?)\]\((.+?)\)$/);
                if (md) {
                  return (
                    <a href={md[2]} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                      {md[1]}
                    </a>
                  );
                }
                if (post.source.startsWith('http')) {
                  return (
                    <a href={post.source} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                      원문 보기
                    </a>
                  );
                }
                return <span>{post.source}</span>;
              })()}
            </div>
          )}
          <div className="prose prose-sm max-w-none mb-6 py-6 border-t border-b">
            <ReactMarkdown>{post.content}</ReactMarkdown>
          </div>
          {post.attachments && post.attachments.length > 0 && (
            <div className="mb-4 bg-gray-50 p-4 rounded">
              <h3 className="font-bold mb-2">첨부파일</h3>
              <ul>
                {post.attachments.map((att) => (
                  <li key={att.id}>
                    <a
                      href={`http://localhost:8000/api/attachments/${att.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-500 underline"
                    >
                      {att.filename}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </article>

        <div className="bg-white rounded shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">댓글 ({comments.length})</h2>

          {user?.id && (
            <form onSubmit={handleCommentSubmit} className="mb-6 pb-6 border-b">
              <textarea
                value={commentContent}
                onChange={(e) => setCommentContent(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded mb-2"
                placeholder="댓글을 입력하세요..."
                rows="3"
              />
              <button
                type="submit"
                disabled={submitting || !commentContent.trim()}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
              >
                {submitting ? '작성 중...' : '댓글 작성'}
              </button>
            </form>
          )}

          <div className="space-y-4">
            {comments.map((comment) => (
              <CommentItem key={comment.id} comment={comment} />
            ))}
            {comments.length === 0 && <p className="text-gray-500">댓글이 없습니다.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
