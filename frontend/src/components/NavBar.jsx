import { Link, useNavigate, useLocation } from "react-router-dom";
import { Auth } from "aws-amplify";
import { useEffect, useState } from "react";
import SubscribeDropdown from "../routes/SubscribeDropdown";

export default function NavBar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [signedIn, setSignedIn] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    Auth.currentAuthenticatedUser()
      .then(user => {
        setSignedIn(true);
        const { given_name, family_name } = user.attributes || {};
        setUserName(`${given_name || ''} ${family_name || ''}`.trim());
      })
      .catch(() => {
        setSignedIn(false);
        setUserName('');
      })
      .finally(() => setAuthChecked(true));
  }, [location.pathname]);

  const handleSignOut = async () => {
    try {
      await Auth.signOut();
      setSignedIn(false);
      setUserName('');
      navigate("/signin");
    } catch (err) {
      console.error("Error signing out: ", err);
    }
  };

  if (!authChecked) return null;

  return (
    <nav className="fixed top-0 left-0 w-full bg-blue-900 text-white shadow-md z-50">
      <div className="max-w-6xl mx-auto px-6 py-3 flex justify-between items-center">
        {/* Logo */}
        <div className="text-xl font-bold flex items-center gap-2">
          <span>🐦</span>
          <span className="text-yellow-300">BirdTag</span>
        </div>

        {/* Right Side */}
        <div className="flex flex-col items-end gap-1 text-sm font-medium">
          {/* First Row: Nav Links */}
          <div className="flex flex-wrap gap-4 justify-end">
            {signedIn ? (
              <>
                <Link to="/upload" className="hover:text-yellow-300">Upload</Link>
                <Link to="/all-media" className="hover:text-yellow-300">All Media</Link>
                <Link to="/search" className="hover:text-yellow-300">Search by Tag</Link>
                <Link to="/search-by-species" className="hover:text-yellow-300">Search by Species</Link>
                <Link to="/get-original-url" className="hover:text-yellow-300">Get Original URL</Link>
                <Link to="/query-upload" className="hover:text-yellow-300">Query by Upload</Link>
              </>
            ) : (
              <>
                <Link to="/" className="hover:text-yellow-300">Home</Link>
                <Link to="/signup" className="hover:text-yellow-300">Sign Up</Link>
                <Link to="/signin" className="hover:text-yellow-300">Sign In</Link>
              </>
            )}
          </div>

          {/* Second Row: Subscribe + User Info + Sign Out */}
          {signedIn && (
            <div className="flex gap-4 items-center mt-2 flex-wrap">
              <SubscribeDropdown />
              {userName && (
                <span className="text-yellow-200 italic whitespace-nowrap">👤 {userName}</span>
              )}
              <button onClick={handleSignOut} className="hover:text-red-300">Sign Out</button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}