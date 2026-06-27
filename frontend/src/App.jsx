import { useState } from 'react'

// This is the address of your FastAPI backend.
// Make sure your backend server (uvicorn app:app --reload) is running
// on this address before testing the frontend.
const API_BASE_URL = 'http://127.0.0.1:8000'

function App() {
  // --- React State ---
  // 'state' is data that React tracks and re-renders the UI for,
  // whenever it changes.

  // What the user has typed into the search box
  const [searchTerm, setSearchTerm] = useState('')

  // The list of recommended movies returned by the API
  const [recommendations, setRecommendations] = useState([])

  // True while we're waiting for the API to respond (lets us show
  // a loading message instead of a confusing blank screen)
  const [isLoading, setIsLoading] = useState(false)

  // Holds an error message if something goes wrong (movie not found,
  // network failure, etc.) so we can show it to the user
  const [errorMessage, setErrorMessage] = useState('')

  // --- This function runs when the user clicks "Search" ---
  async function handleSearch() {
    // Don't search if the box is empty
    if (!searchTerm.trim()) {
      return
    }

    setIsLoading(true)
    setErrorMessage('')
    setRecommendations([])

    try {
      // encodeURIComponent makes the search term safe to put in a URL
      // (handles spaces, special characters, etc.)
      const url = `${API_BASE_URL}/recommend?title=${encodeURIComponent(searchTerm)}&top_n=5`

      const response = await fetch(url)

      if (!response.ok) {
        // FastAPI returns a 404 with a JSON 'detail' field when the
        // movie isn't found — we read and show that exact message.
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Something went wrong.')
      }

      const data = await response.json()
      setRecommendations(data.recommendations)
    } catch (error) {
      setErrorMessage(error.message)
    } finally {
      // 'finally' runs whether the request succeeded or failed —
      // we always want to stop showing the loading state.
      setIsLoading(false)
    }
  }

  // Allow pressing Enter in the search box to trigger search too
  function handleKeyDown(event) {
    if (event.key === 'Enter') {
      handleSearch()
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white px-4 py-12">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2">
          🎬 CineMind AI
        </h1>
        <p className="text-gray-400 text-center mb-8">
          Type a movie you like, and discover similar ones.
        </p>

        {/* --- Search bar --- */}
        <div className="flex gap-2 mb-8">
          <input
            type="text"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. Avatar, Inception, The Dark Knight"
            className="flex-1 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700
                       text-white placeholder-gray-500 focus:outline-none
                       focus:border-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-700
                       disabled:bg-gray-700 disabled:cursor-not-allowed
                       font-semibold transition-colors"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* --- Error message --- */}
        {errorMessage && (
          <p className="text-red-400 text-center mb-4">{errorMessage}</p>
        )}

        {/* --- Results --- */}
        {recommendations.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold mb-4">
              Movies similar to "{searchTerm}":
            </h2>
            <div className="grid gap-3">
              {recommendations.map((movie) => (
                <div
                  key={movie.title}
                  className="bg-gray-800 rounded-lg p-4 flex justify-between items-center"
                >
                  <span className="font-medium">{movie.title}</span>
                  <span className="text-sm text-gray-400">
                    match: {(movie.similarity_score * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App