import { useState } from "react";
import { Auth } from "aws-amplify";

export default function GetOriginalUrl() {
  const [thumbnailUrl, setThumbnailUrl] = useState("");
  const [originalUrl, setOriginalUrl] = useState(null);
  const [displayUrl, setDisplayUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleLookup = async () => {
    if (!thumbnailUrl.trim()) {
      alert("Please enter a valid thumbnail URL.");
      return;
    }

    setLoading(true);
    setOriginalUrl(null);
    setDisplayUrl(null);

    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      const response = await fetch("https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/get-original-url", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ thumbnail_url: thumbnailUrl.trim() })
      });

      const data = await response.json();

      if (response.ok && data.original_url) {
        setOriginalUrl(data.original_url);

        const match = data.original_url.match(/\/(images|videos|audios|thumbnails|exports)\/[^/?]+/);
        const publicUrl = match ? `https://birdtag-storage-aus-dev.s3.amazonaws.com${match[0]}` : data.original_url;

        setDisplayUrl(publicUrl);
      } else {
        setOriginalUrl("Not found.");
        setDisplayUrl(null);
      }
    } catch (err) {
      console.error("Error fetching original URL:", err);
      alert("Failed to fetch original URL.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <h2 className="text-3xl font-bold text-center text-blue-800 mb-8">
        🔎 Get Full-Size Media by Thumbnail URL
      </h2>

      <input
        type="text"
        value={thumbnailUrl}
        onChange={(e) => setThumbnailUrl(e.target.value)}
        placeholder="Paste thumbnail S3 URL here"
        className="w-full border rounded px-4 py-2 mb-4"
      />

      <button
        onClick={handleLookup}
        disabled={loading}
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50 w-full"
      >
        {loading ? "Looking up..." : "Get Original URL"}
      </button>

      {originalUrl && (
        <div className="mt-6 bg-gray-100 p-4 rounded break-words text-sm">
          {originalUrl === "Not found." ? (
            <p className="text-red-600 font-semibold">❌ Original media not found.</p>
          ) : (
            <>
              <p className="text-gray-700 font-semibold mb-1">📍 Original URL:</p>
              <a href={originalUrl} target="_blank" rel="noreferrer" className="text-blue-600 underline">
                {displayUrl}
              </a>
            </>
          )}
        </div>
      )}
    </div>
  );
}