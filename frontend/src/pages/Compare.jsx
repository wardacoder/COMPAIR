import { useState, useEffect, useRef } from "react";
import CategoryTabs from "../components/CategoryTabs";
import CompareForm from "../components/CompareForm";
import ResultDisplay from "../components/ResultDisplay";
import FeedbackSection from "../components/FeedbackSection";
import Navbar from "../Navbar";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { motion } from "framer-motion";
import API_BASE from "../config/api";

export default function Compare() {
  const [category, setCategory] = useState("other");
  const [items, setItems] = useState(["", ""]);
  const [criteria, setCriteria] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const resultRef = useRef(null);

  const [userPreferences, setUserPreferences] = useState({
    priorities: [],
    budget: "",
    use_case: ""
  });
  const [showPreferences, setShowPreferences] = useState(false);

  useEffect(() => {
    setItems(["", ""]);
    setCriteria("");
    setUserPreferences({ priorities: [], budget: "", use_case: "" });
    setShowPreferences(false);
  }, [category]);

  const handleCompare = async () => {
    setLoading(true);
    setResult(null);
    try {
      // Filter out empty items
      const validItems = items.filter(item => item.trim().length > 0);
      
      if (validItems.length < 2) {
        alert("Please enter at least 2 items to compare.");
        setLoading(false);
        return;
      }

      const requestBody = {
        category,
        items: validItems,
        criteria,
        ...(showPreferences && (
          userPreferences.priorities.length > 0 ||
          userPreferences.budget ||
          userPreferences.use_case
        ) && {
          user_preferences: userPreferences
        })
      };

      console.log("📤 FRONTEND SENDING TO BACKEND:", requestBody);

      const res = await fetch(`${API_BASE}/compare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      
      const data = await res.json();
      console.log("✅ FRONTEND RECEIVED FROM BACKEND:", data);
      console.log("✅ Response has table:", Array.isArray(data.table) && data.table.length > 0);
      
      // Check if response has an error
      if (!res.ok) {
        const errorMsg = data.detail || data.message || "Failed to compare items. Please try again.";
        alert(errorMsg);
        setResult({ message: errorMsg });
        return;
      }
      
      // Check if response has a message (error message from backend)
      if (data.message && !data.table) {
        alert(data.message);
        setResult(data);
        return;
      }
      
      // Validate that we have a table
      if (!data.table || !Array.isArray(data.table) || data.table.length === 0) {
        console.error("❌ Invalid response: no table data", data);
        alert("The comparison did not return valid results. Please try again.");
        setResult({ message: "The comparison did not return valid results. Please try again." });
        return;
      }
      
      setResult(data);

      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 300);
    } catch (err) {
      console.error("❌ Compare error:", err);
      alert(`Error while comparing items: ${err.message}`);
      setResult({ message: `Error: ${err.message}` });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    try {
      const res = await fetch(`${API_BASE}/save-comparison`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: "guest123",
          category,
          items,
          result,
        }),
      });
      const data = await res.json();
      console.log("✅ Save response:", data);
      alert("Comparison saved successfully!");
    } catch (err) {
      console.error("❌ Save error:", err);
      alert("Failed to save comparison");
    }
  };

  const handleExportPDF = async () => {
    if (!result) return;
    const element = document.getElementById("result-section");
    const canvas = await html2canvas(element);
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF("p", "mm", "a4");
    const imgWidth = 190;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    pdf.addImage(imgData, "PNG", 10, 10, imgWidth, imgHeight);
    pdf.save("COMPAIR_Result.pdf");
  };

  return (
    <div
      className="min-h-screen flex flex-col
      bg-gradient-to-br from-blue-50 via-white to-sky-50
      dark:from-slate-950 dark:via-slate-900 dark:to-black 
      transition-colors duration-500"
    >
      {/* Navigation Bar */}
      <Navbar />
      
      <div className="flex flex-col items-center p-6 pb-20 text-center">

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <p className="text-gray-600 dark:text-gray-400 text-lg max-w-2xl mx-auto">
          Choose a category below to start comparing
        </p>
      </motion.div>

      {/* Category Tabs & Form */}
      <CategoryTabs selected={category} onChange={setCategory} />
      
      {/* ✅ UPDATED: Pass onCompare and isComparing props */}
      <CompareForm
        category={category}
        items={items}
        setItems={setItems}
        criteria={criteria}
        setCriteria={setCriteria}
        userPreferences={userPreferences}
        setUserPreferences={setUserPreferences}
        showPreferences={showPreferences}
        setShowPreferences={setShowPreferences}
        onCompare={handleCompare}  // ✅ NEW
        isComparing={loading}       // ✅ NEW
      />

      {/* Results Section */}
      {result && (
        <motion.div
          ref={resultRef}
          id="result-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mt-10 w-full max-w-4xl"
        >
          <ResultDisplay
            result={result}
            onSave={handleSave}
            onExport={handleExportPDF}
            onReset={() => setResult(null)}
          />
          
          {/* Feedback Section - Always show after comparison */}
          <FeedbackSection 
            comparisonId={result.comparison_id || "temp-" + Date.now()} 
            userId="guest123"
            hasPersonalization={!!result.personalized_winner}
          />
        </motion.div>
      )}
      </div>
    </div>
  );
}