import { useState } from "react";
import { Auth } from "aws-amplify";

export default function SearchBySpecies() {
  const [speciesList, setSpeciesList] = useState([""]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSpeciesChange = (index, value) => {
    const updated = [...speciesList];
    updated[index] = value;
    setSpeciesList(updated);
  };

  const addSpeciesField = () => setSpeciesList([...speciesList, ""]);

  const removeSpeciesField = (index) => {
    const updated = [...speciesList];
    updated.splice(index, 1);
    setSpeciesList(updated);
  };

  const handleSearch = async () => {
    const species = speciesList.map((s) => s.trim()).filter((s) => s);
    if (species.length === 0) {
      alert("Please enter at least one species.");
      return;
    }

    setLoading(true);
    setResults([]);

    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      const response = await fetch("https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/search-by-species", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ species }),
      });

      const data = await response.json();
      setResults(data.links || []);
    } catch (err) {
      console.error("Error searching:", err);
      alert("Failed to fetch results.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-10 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8 text-green-800">🕊️ Search by Any Species</h2>

      <div className="space-y-4 mb-6">
        {speciesList.map((s, index) => (
          <div key={index} className="flex gap-2 items-center">
            <input
              type="text"
              value={s}
              onChange={(e) => handleSpeciesChange(index, e.target.value)}
              placeholder="e.g., crow"
              className="border px-3 py-1 rounded w-2/3"
            />
            {speciesList.length > 1 && (
              <button onClick={() => removeSpeciesField(index)} className="text-red-600 font-bold text-xl">✖️</button>
            )}
          </div>
        ))}
        <button onClick={addSpeciesField} className="text-green-600 font-semibold text-sm">
          ➕ Add Another Species
        </button>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {results.length > 0 ? (
        <div className="mt-10">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">📁 Matched Media</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {results.map((url, idx) => {
              const extension = new URL(url).pathname.split(".").pop().toLowerCase();
              const isImage = ["jpg", "jpeg", "png", "gif", "webp"].includes(extension);
              const pathMatch = url.match(/\/(images|videos|audios|thumbnails|exports)\/[^/?]+/);
              const displayText = pathMatch ? `https://birdtag-storage-aus-dev.s3.amazonaws.com${pathMatch[0]}` : url;

              return (
                <div key={idx} className="p-4 border rounded shadow bg-white flex flex-col items-center text-center">
                  {isImage ? (
                    <img src={url} alt={`media-${idx}`} className="rounded w-full object-cover max-h-64 mb-2" />
                  ) : (
                    <div className="mb-2">
                      <p className="text-gray-700 mb-1">🎞️ Video / Other File</p>
                      <a href={url} target="_blank" rel="noreferrer" className="text-blue-600 underline text-sm break-all">
                        View / Download
                      </a>
                    </div>
                  )}
                  <code className="text-xs text-gray-600 break-all bg-gray-100 px-2 py-1 rounded w-full mt-2">
                    <a href={url} target="_blank" rel="noreferrer" className="hover:underline">
                      {displayText}
                    </a>
                  </code>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        !loading && (
          <p className="text-center mt-10 text-gray-500">❌ No matching media found.</p>
        )
      )}
    </div>
  );
}