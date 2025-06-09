import { useEffect, useState } from 'react';
import { Auth } from 'aws-amplify';

export default function AllMedia() {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editedTags, setEditedTags] = useState({});

  const fetchMedia = async () => {
    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      const response = await fetch('https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/get-all-media', {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` }
      });

      const data = await response.json();
      setMedia(data);
    } catch (err) {
      console.error('Error fetching media:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMedia(); }, []);

  const handleDelete = async (fileId) => {
    if (!window.confirm("Are you sure you want to delete this file?")) return;

    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      await fetch("https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/delete-files", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ file_ids: [fileId] }),
      });

      setMedia(prev => prev.filter(item => item.file_id !== fileId));
    } catch (err) {
      console.error("Error deleting file:", err);
      alert("Delete failed.");
    }
  };

  const handleModifyTags = async (fileId, operation, tag, count) => {
    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      await fetch("https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/modify-tags", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          file_ids: [fileId],
          operation,
          tags: [`${tag},${count}`]
        }),
      });

      setEditedTags(prev => {
        const copy = { ...prev };
        delete copy[`${fileId}-${tag}`];
        return copy;
      });

      await fetchMedia();
    } catch (err) {
      console.error("Error modifying tags:", err);
      alert("Failed to update tags.");
    }
  };

  if (loading) return <p className="text-center mt-10 text-lg">Loading media...</p>;

  return (
    <div className="mt-12 px-6 pb-10">
      <h2 className="text-4xl font-bold text-center text-blue-900 mb-10">📦 All Media Files</h2>
      <ul className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {media.map((item) => (
          <li
            key={item.file_id}
            className="flex flex-col justify-between h-full p-5 bg-gray-50 shadow-md rounded-2xl border border-gray-200"
          >
            <div className="flex flex-col gap-4">
              <div className="flex justify-between gap-4">
                <div className="flex-1">
                  <p className="font-semibold text-lg text-gray-700">📁 File ID:</p>
                  <p className="text-sm text-gray-800 break-all">{item.file_id}</p>
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-lg text-gray-700">📂 Type:</p>
                  <p className="text-sm text-gray-800">{item.file_type}</p>
                </div>
              </div>

              <div>
                <p className="font-semibold text-lg text-gray-700">🔗 Original URL:</p>
                <a
                  href={item.original_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-blue-600 hover:underline text-sm"
                >
                  Original Link
                </a>
              </div>

              {item.thumbnail_url && (
                <div>
                  <p className="font-semibold text-lg text-gray-700">🖼️ Thumbnail:</p>
                  <img
                    src={item.thumbnail_url.replace("s3://birdtag-storage-aus-dev/", "https://birdtag-storage-aus-dev.s3.amazonaws.com/")}
                    alt="thumbnail"
                    className="w-full h-auto max-h-[400px] object-contain rounded-lg border border-gray-300 bg-white"
                  />
                </div>
              )}

              <div>
                <p className="font-semibold text-lg text-gray-700 mb-1">🏷️ Tags:</p>
                <div className="flex flex-col gap-2">
                  {item.tags && Object.entries(item.tags).map(([tag, count]) => {
                    const tagKey = `${item.file_id}-${tag}`;
                    return (
                      <div key={tagKey} className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-gray-900 bg-gray-200 rounded px-2 py-1">{tag}</span>
                        <input
                          type="number"
                          min="1"
                          defaultValue={count}
                          className="border px-2 py-1 rounded text-sm w-20"
                          onChange={(e) => {
                            const newVal = parseInt(e.target.value);
                            if (!isNaN(newVal)) {
                              setEditedTags(prev => ({
                                ...prev,
                                [tagKey]: { newVal, oldVal: count }
                              }));
                            }
                          }}
                        />
                        <button
                          onClick={() => handleModifyTags(item.file_id, 0, tag, count)}
                          className="bg-red-100 text-red-700 px-2 py-1 rounded text-xs hover:bg-red-200"
                        >
                          Remove Tag
                        </button>
                        {editedTags[tagKey] && editedTags[tagKey].newVal !== editedTags[tagKey].oldVal && (
                          <button
                            onClick={() => handleModifyTags(item.file_id, 1, tag, editedTags[tagKey].newVal - editedTags[tagKey].oldVal)}
                            className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs hover:bg-blue-200"
                          >
                            Update Tag
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Add new tag */}
              <form
                className="flex flex-wrap gap-2 mt-4"
                onSubmit={async (e) => {
                  e.preventDefault();
                  const tag = e.target.elements.newTag.value.trim();
                  const count = parseInt(e.target.elements.newCount.value);

                  if (!tag || isNaN(count) || count < 1) {
                    alert("Enter valid tag and count.");
                    return;
                  }

                  await handleModifyTags(item.file_id, 1, tag, count);
                  e.target.reset();
                }}
              >
                <input
                  name="newTag"
                  type="text"
                  placeholder="New tag"
                  className="border px-2 py-1 rounded text-sm flex-1 min-w-[100px]"
                  required
                />
                <input
                  name="newCount"
                  type="number"
                  min="1"
                  placeholder="Count"
                  className="border px-2 py-1 rounded text-sm w-20"
                  required
                />
                <button
                  type="submit"
                  className="bg-green-600 text-white text-sm font-medium px-3 py-1 rounded hover:bg-green-700"
                >
                  Add
                </button>
              </form>
            </div>

            <button
              onClick={() => handleDelete(item.file_id)}
              className="mt-6 w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded"
            >
              ❌ Delete File
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}