import { useState } from "react";
import { Auth } from "aws-amplify";

export default function Upload() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [messages, setMessages] = useState([]);

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files)); // ✅ Store all selected files
    setMessages([]);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      alert("Please select files first.");
      return;
    }

    setUploading(true);
    setMessages([]);

    try {
      const session = await Auth.currentSession();
      const token = session.getIdToken().getJwtToken();

      for (const file of selectedFiles) {
        try {
          const filename = file.name;

          const getUrlResponse = await fetch(
            `https://l0ulh45lbj.execute-api.us-east-1.amazonaws.com/generate-media-upload-url?filename=${encodeURIComponent(filename)}&content_type=${encodeURIComponent(file.type)}`,
            {
              method: "GET",
              headers: { Authorization: `Bearer ${token}` },
            }
          );

          if (!getUrlResponse.ok) throw new Error("Failed to get upload URL");

          const { upload_url } = await getUrlResponse.json();

          const uploadResponse = await fetch(upload_url, {
            method: "PUT",
            headers: { "Content-Type": file.type },
            body: file,
          });

          if (!uploadResponse.ok) throw new Error("Failed to upload file");

          setMessages(prev => [...prev, `✅ ${filename} uploaded successfully.`]);
        } catch (err) {
          console.error(`Upload failed for ${file.name}:`, err);
          setMessages(prev => [...prev, `❌ ${file.name} failed to upload.`]);
        }
      }

      setSelectedFiles([]);
    } catch (err) {
      console.error("Upload failed:", err);
      setMessages(["❌ Upload failed. Please try again."]);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-[80vh] px-4">
      <div className="bg-white shadow-md rounded-2xl p-8 max-w-md w-full text-center">
        <h2 className="text-3xl font-bold text-blue-800 mb-6">📤 Upload Bird Media</h2>

        <input
          type="file"
          accept="image/*,video/*,audio/*"
          multiple // ✅ Allow multiple selection
          onChange={handleFileChange}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100"
        />

        {selectedFiles.length > 0 && (
          <ul className="mt-4 text-left text-sm text-gray-600">
            {selectedFiles.map((file) => (
              <li key={file.name} className="truncate">📎 {file.name}</li>
            ))}
          </ul>
        )}

        <button
          onClick={handleUpload}
          disabled={uploading}
          className="mt-6 bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
        >
          {uploading ? "Uploading..." : "Upload All"}
        </button>

        {messages.length > 0 && (
          <ul className="mt-4 text-sm text-left">
            {messages.map((msg, idx) => (
              <li key={idx}>{msg}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}