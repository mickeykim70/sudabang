export default function CommentItem({ comment }) {
  return (
    <div className="bg-gray-50 p-4 rounded border border-gray-200">
      <div className="flex justify-between items-start mb-2">
        <span className="font-bold">{comment.author?.display_name}</span>
        <span className="text-gray-500 text-sm">{new Date(comment.created_at).toLocaleString('ko-KR', { year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' })}</span>
      </div>
      <p className="text-gray-700">{comment.content}</p>
    </div>
  );
}
