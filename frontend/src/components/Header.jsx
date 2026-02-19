import { useNavigate } from 'react-router-dom';

export default function Header({ title }) {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleHome = () => {
    navigate('/');
  };

  return (
    <header className="bg-blue-600 text-white shadow-md">
      <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <div onClick={handleHome} className="cursor-pointer">
          <h1 className="text-2xl font-bold">수다방</h1>
          <p className="text-sm">{title}</p>
        </div>
        <div>
          {user?.id ? (
            <div className="flex items-center gap-4">
              <span className="text-sm">{user.display_name}</span>
              <button
                onClick={handleLogout}
                className="bg-red-500 px-3 py-1 rounded text-sm hover:bg-red-600"
              >
                로그아웃
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="bg-white text-blue-600 px-3 py-1 rounded text-sm hover:bg-gray-100"
            >
              로그인
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
