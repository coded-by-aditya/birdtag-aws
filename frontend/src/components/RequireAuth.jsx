import { useEffect, useState } from 'react';
import { Auth } from 'aws-amplify';
import { Navigate } from 'react-router-dom';

export default function RequireAuth({ children }) {
  const [checking, setChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    Auth.currentAuthenticatedUser()
      .then(() => setIsAuthenticated(true))
      .catch(() => setIsAuthenticated(false))
      .finally(() => setChecking(false));
  }, []);

  if (checking) return <div className="text-center mt-10">Checking auth...</div>;

  return isAuthenticated ? children : <Navigate to="/signin" />;
}