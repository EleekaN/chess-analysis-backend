"use client";
import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState(null);
  const [pgnText, setPgnText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setPgnText(""); // Clear text input when a file is selected
  };

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!file && !pgnText) {
      alert("Please upload a PGN file or paste PGN text!");
      return;
    }

    // const formData = new FormData();
    // if (file) {
    //   formData.append("file", file);
    // } else {
    //   formData.append("pgn", pgnText);
    // }

    const formData = new FormData();
    formData.append("pgn", pgnText);  // Ensure pgnText is a valid PGN string

    // setLoading(true);

    try {
      const response = await fetch("https://chess-analysis-backend-3z15.onrender.com/analyze", {
        method: "POST",
        body: formData,
        headers: {
          "Accept": "application/json"
        }
      });

      const result = await response.json();
      setAnalysis(result);
    } catch (error) {
      console.error("Error analyzing PGN:", error);
      alert("Failed to analyze PGN.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Chess PGN Analyzer</h1>

      {/* PGN File Upload */}
      <input
        type="file"
        accept=".pgn"
        onChange={handleFileChange}
        className="mb-4"
      />

      <span className="text-gray-600 mb-2">or</span>

      {/* PGN Text Input */}
      <textarea
        value={pgnText}
        onChange={(e) => {
          setPgnText(e.target.value);
          setFile(null); // Clear file selection when text is entered
        }}
        placeholder="Paste PGN text here..."
        className="w-full max-w-lg h-32 p-2 border rounded-md"
      />

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze PGN"}
      </button>

      {/* Display Analysis */}
      {analysis && (
        <div className="mt-6 p-4 bg-white shadow-md rounded-lg w-full max-w-2xl">
          <h2 className="text-xl font-semibold">Analysis Result</h2>
          <pre className="mt-2 p-2 bg-gray-200 rounded">{JSON.stringify(analysis, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
