export default function Home() {
    return (
      <div className="min-h-screen bg-gray-900 text-white p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Grace - Terminal</h1>
          <p className="text-xl text-gray-300 mb-8">AI-powered finance and investment assistant</p>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <a href="/chat" className="bg-blue-600 hover:bg-blue-700 p-4 rounded-lg text-center">
              Chat
            </a>
            <a href="/wallet" className="bg-green-600 hover:bg-green-700 p-4 rounded-lg text-center">
              Wallet
            </a>
            <a href="/trading" className="bg-purple-600 hover:bg-purple-700 p-4 rounded-lg text-center">
              Trading
            </a>
            <a href="/social" className="bg-pink-600 hover:bg-pink-700 p-4 rounded-lg text-center">
              Social
            </a>
            <a href="/settings" className="bg-gray-600 hover:bg-gray-700 p-4 rounded-lg text-center">
              Settings
            </a>
            <a href="/login" className="bg-red-600 hover:bg-red-700 p-4 rounded-lg text-center">
              Login
            </a>
          </div>
        </div>
      </div>
    );
  }