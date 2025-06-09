import { useState } from "react";
import { Auth } from "aws-amplify";

const API_BASE = "https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com";
const BUCKET_NAME = "birdtag-storage-aus-dev";

export default function QueryByUpload() {
  const [file, setFile] = useState(null);
  const [tags, setTags] = useState({});
  const [links, setLinks] = useState([]);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setTags({});
    setLinks([]);
    setStatus("");
  };

  const handleUploadAndQuery = async () => {
    if (!file) {
      alert("Please select a file.");
      return;
    }

    setLoading(true);
    setStatus("Uploading...");
    const uniqueFilename = file.name;
    const fileKey = `temp/${uniqueFilename}`;

    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      const res = await fetch(`${API_BASE}/generate-temp-upload-url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ filename: uniqueFilename, folder: "temp" }),
      });

      if (!res.ok) throw new Error("Failed to get pre-signed URL");
      const { url } = await res.json();

      await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": file.type },
        body: file,
      });

      setStatus("Processing...");

      const result = await pollForResult(fileKey, token);
      setTags(result.tags);
      setLinks(result.links);

      if (Object.keys(result.tags).length === 0) {
        setStatus("No bird species detected in the uploaded file.");
      } else if (result.links.length === 0) {
        setStatus("No matches found.");
      } else {
        setStatus("✅ Done!");
      }
    } catch (err) {
      console.error("Upload or query failed:", err);
      setStatus("❌ Failed to upload or retrieve result.");
    } finally {
      setLoading(false);
    }
  };

  const pollForResult = async (key, token) => {
    const maxRetries = 20;
    const delay = 5000;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        const res = await fetch(`${API_BASE}/query-media-by-file?key=${encodeURIComponent(key)}`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (res.status === 200) {
          const data = await res.json();
          return data;
        }
      } catch (_) {
        // continue polling
      }

      await new Promise((r) => setTimeout(r, delay));
    }

    throw new Error("Timed out waiting for query result.");
  };

  return (
    <div className="flex justify-center items-center min-h-[80vh] px-4">
      <div className="bg-white shadow-md rounded-2xl p-8 max-w-md w-full text-center">
        <h2 className="text-3xl font-bold text-blue-800 mb-6">🔍 Query Media by Upload</h2>

        <input
          type="file"
          accept="image/*,video/*,audio/*"
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100"
        />

        {file && (
          <p className="mt-4 text-sm text-gray-600 truncate">📎 {file.name}</p>
        )}

        <button
          onClick={handleUploadAndQuery}
          disabled={loading}
          className="mt-6 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {loading ? "Processing..." : "Upload & Search"}
        </button>

        {status && <p className="mt-4 text-sm text-gray-700">{status}</p>}

        {Object.keys(tags).length > 0 && (
          <div className="mt-6 text-left">
            <h3 className="font-semibold text-blue-700">Detected Tags:</h3>
            <ul className="list-disc list-inside text-sm">
              {Object.entries(tags).map(([tag, count]) => (
                <li key={tag}>{tag} ({count})</li>
              ))}
            </ul>
          </div>
        )}

        {links.length > 0 && (
          <div className="mt-6 text-left">
            <h3 className="font-semibold text-blue-700 mb-2">Matching Media Links:</h3>
            <ul className="list-disc list-inside text-sm text-blue-600">
              {links.map((link, i) => {
                try {
                  const urlObj = new URL(link);
                  const s3Key = urlObj.pathname; // e.g., /images/myna_2.jpg
                  const displayUrl = `https://${BUCKET_NAME}.s3.amazonaws.com${s3Key}`;

                  return (
                    <li key={i} className="mb-4">
                      <a href={link} target="_blank" rel="noopener noreferrer" className="hover:underline break-all">
                        {displayUrl}
                      </a>
                      <div className="mt-2">
                        {link.match(/\.(jpg|jpeg|png)$/i) ? (
                          <img src={link} alt={`media-${i}`} className="w-full max-h-64 object-contain border rounded" />
                        ) : link.match(/\.(mp4|mov|avi)$/i) ? (
                          <video controls className="w-full max-h-64 rounded">
                            <source src={link} />
                          </video>
                        ) : null}
                      </div>
                    </li>
                  );
                } catch {
                  return null;
                }
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}