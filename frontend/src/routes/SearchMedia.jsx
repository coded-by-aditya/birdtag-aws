import { useState } from "react";
import { Auth } from "aws-amplify";

export default function SearchMedia() {
  const [tags, setTags] = useState([{ name: "", count: 1 }]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleTagChange = (index, field, value) => {
    const newTags = [...tags];
    if (field === "count") {
      const parsed = parseInt(value);
      newTags[index][field] = isNaN(parsed) || parsed < 1 ? 1 : parsed;
    } else {
      newTags[index][field] = value;
    }
    setTags(newTags);
  };

  const addTagField = () => setTags([...tags, { name: "", count: 1 }]);
  const removeTagField = (index) => setTags(tags.filter((_, i) => i !== index));

  const handleSearch = async () => {
    const tagObject = {};
    for (const { name, count } of tags) {
      if (name.trim() && count > 0) {
        tagObject[name.trim()] = count;
      }
    }

    if (Object.keys(tagObject).length === 0) {
      alert("Please enter at least one valid tag.");
      return;
    }

    setLoading(true);
    setResults([]);

    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      const response = await fetch(
        "https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/search-by-tags",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ tags: tagObject }),
        }
      );

      const data = await response.json();
      setResults(data.links || []);
    } catch (err) {
      console.error("Search failed:", err);
      alert("Error fetching search results.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-4 py-10 max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8 text-blue-800">🔍 Search by Bird Species & Tag</h2>

      <div className="space-y-4 mb-6">
        {tags.map((tag, index) => (
          <div key={index} className="flex gap-2 items-center">
            <input
              type="text"
              value={tag.name}
              onChange={(e) => handleTagChange(index, "name", e.target.value)}
              placeholder="e.g., myna"
              className="border px-3 py-1 rounded w-1/2"
            />
            <input
              type="number"
              value={tag.count}
              onChange={(e) => handleTagChange(index, "count", e.target.value)}
              min="1"
              className="border px-3 py-1 rounded w-1/4"
            />
            {tags.length > 1 && (
              <button onClick={() => removeTagField(index)} className="text-red-600 font-bold">
                ❌
              </button>
            )}
          </div>
        ))}

        <button onClick={addTagField} className="text-blue-600 font-semibold text-sm">
          ➕ Add Another Tag
        </button>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {results.length > 0 ? (
        <div className="mt-10">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">📁 Search Results</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {results.map(({ signed_url, display_url }, idx) => (
              <div key={idx} className="p-4 border rounded shadow bg-white flex flex-col items-center text-center">
                {display_url.match(/\.(jpeg|jpg|png|gif|webp)$/i) ? (
                  <img
                    src={signed_url}
                    alt={`thumb-${idx}`}
                    className="rounded w-full object-cover max-h-64 mb-2"
                  />
                ) : (
                  <div className="mb-2">
                    <p className="text-gray-700 mb-1">🎞️ Video / Other File</p>
                    <a
                      href={signed_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-blue-600 underline text-sm break-all"
                    >
                      View / Download
                    </a>
                  </div>
                )}
                <code className="text-xs text-gray-600 break-all bg-gray-100 px-2 py-1 rounded w-full mt-2">
                  <a href={signed_url} target="_blank" rel="noreferrer" className="hover:underline">
                    {display_url}
                  </a>
                </code>
              </div>
            ))}
          </div>
        </div>
      ) : (
        results && (
          <div className="text-center mt-10 text-gray-500">
            ❌ No matching media found for the given tags.
          </div>
        )
      )}
    </div>
  );
}