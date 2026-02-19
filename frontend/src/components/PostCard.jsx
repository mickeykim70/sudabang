export default function PostCard({ post, onClick }) {
  return (
    <div
      onClick={onClick}
      className="p-4 bg-white border border-gray-300 rounded hover:shadow-lg cursor-pointer transition"
    >
      <h3 className="text-lg font-bold mb-2">{post.title}</h3>
      <div className="text-gray-600 text-sm">
        <span>{post.author?.display_name}</span>
        <span className="mx-2">•</span>
        <span>{new Date(post.created_at).toLocaleDateString()}</span>
        <span className="mx-2">•</span>
        <span>조회: {post.view_count}</span>
      </div>
    </div>
  );
}
