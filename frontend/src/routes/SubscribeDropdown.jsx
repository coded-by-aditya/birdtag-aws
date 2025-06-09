import { useState, useEffect } from "react";
import { Auth } from "aws-amplify";

const birdTags = ["owl", "pigeon", "myna", "kingfisher", "peacock"];

export default function SubscribeDropdown() {
  const [selectedTags, setSelectedTags] = useState([]);
  const [message, setMessage] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSubscribedTags = async () => {
      try {
        const session = await Auth.currentSession();
        const token = session.getIdToken().getJwtToken();

        const response = await fetch("https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/get-user-subscriptions", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await response.json();
        if (data.tags) {
          setSelectedTags(data.tags);
        }
      } catch (err) {
        console.error("Failed to fetch subscriptions:", err);
      }
    };

    fetchSubscribedTags();
  }, []);

  const handleTagToggle = (tag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleSubmit = async () => {
    setMessage("");
    if (selectedTags.length === 0) {
      setMessage("Please select at least one bird tag.");
      return;
    }

    setLoading(true);
    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      const response = await fetch("https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/subscribe-to-tags", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ tags: selectedTags }),
      });

      const data = await response.json();
      setMessage(data.message || data);
    } catch (err) {
      setMessage("Failed to subscribe: " + err.message);
    }
    setLoading(false);
  };

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setIsOpen((o) => !o)}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
      >
        Subscribe
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-slate-100 border border-gray-300 rounded shadow-lg z-50 p-4 text-gray-800">
          <p className="font-semibold mb-2">Choose Tags:</p>
          <div className="grid grid-cols-2 gap-2 mb-4">
            {birdTags.map((tag) => (
              <label key={tag} className="flex items-center text-sm">
                <input
                  type="checkbox"
                  checked={selectedTags.includes(tag)}
                  onChange={() => handleTagToggle(tag)}
                  className="mr-2 accent-green-600"
                />
                <span className="capitalize">{tag}</span>
              </label>
            ))}
          </div>
          <button
            onClick={handleSubmit}
            className="w-full bg-blue-600 text-white py-1 px-2 rounded hover:bg-blue-700 disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Subscribing..." : "Subscribe"}
          </button>
          {message && <p className="text-xs mt-2 text-gray-700">{message}</p>}
        </div>
      )}
    </div>
  );
}