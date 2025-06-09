import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";
import Home from "./routes/Home";
import Upload from "./routes/Upload";
import Query from "./routes/Query";
import Results from "./routes/Results";
import SignUp from "./routes/SignUp";
import SignIn from "./routes/SignIn";
import RequireAuth from "./components/RequireAuth";
import AllMedia from "./routes/AllMedia";
import SearchMedia from "./routes/SearchMedia";
import SearchBySpecies from "./routes/SearchBySpecies";
import GetOriginalUrl from "./routes/GetOriginalUrl";
import QueryByUpload from "./routes/QueryByUpload";

function App() {
  return (
    <Router>
      <div className="bg-gray-100 text-gray-900 min-h-screen">
        <NavBar />
        <div className="pt-20 max-w-6xl mx-auto px-4">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/signup" element={<SignUp />} />
            <Route path="/signin" element={<SignIn />} />

            {/* Protected Routes */}
            <Route
              path="/upload"
              element={
                <RequireAuth>
                  <Upload />
                </RequireAuth>
              }
            />
            <Route
              path="/query"
              element={
                <RequireAuth>
                  <Query />
                </RequireAuth>
              }
            />
            <Route
              path="/results"
              element={
                <RequireAuth>
                  <Results />
                </RequireAuth>
              }
            />
            <Route
              path="/all-media"
              element={
                <RequireAuth>
                  <AllMedia />
                </RequireAuth>
              }
            />
            <Route
              path="/search"
              element={
                <RequireAuth>
                  <SearchMedia />
                </RequireAuth>
              }
            />
            <Route
              path="/search-by-species"
              element={
                <RequireAuth>
                  <SearchBySpecies />
                </RequireAuth>
              }
            />
            <Route
              path="/get-original-url"
              element={
                <RequireAuth>
                  <GetOriginalUrl />
                </RequireAuth>
              }
            />
            <Route
              path="/query-upload"
              element={
                <RequireAuth>
                  <QueryByUpload />
                </RequireAuth>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;