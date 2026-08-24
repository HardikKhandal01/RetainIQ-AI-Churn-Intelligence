import { useState, useRef } from 'react';
import axios from 'axios';
import { Activity, AlertCircle, BarChart3, Users, Zap, ShieldAlert, UploadCloud, FileSpreadsheet, DollarSign, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';

function App() {
  const [formData, setFormData] = useState({
    customer_id: 'CUS-' + Math.floor(1000 + Math.random() * 9000),
    tenure: 12, monthly_charges: 50.0, total_charges: 600.0, contract: 'Month-to-month',
    usage_frequency: 'Medium', support_tickets: 2, engagement_score: 50, last_activity_days: 10
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  
  // Bulk Upload State
  const [bulkResults, setBulkResults] = useState<any[]>([]);
  const [bulkLoading, setBulkLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Pagination State (Gmail style)
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 50;

  const handlePredict = async (e: React.FormEvent) => {
    if(e) e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('https://retainiq-ai-churn-intelligence.onrender.com/api/predict', formData);
      setResult(response.data.prediction);
    } catch (error) {
      alert("Error processing prediction.");
    }
    setLoading(false);
  };

  const handleChange = (e: any) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setBulkLoading(true);
    setCurrentPage(1); // Reset to page 1 on new upload
    const formDataUpload = new FormData();
    formDataUpload.append("file", file);

    try {
      const response = await axios.post('https://retainiq-ai-churn-intelligence.onrender.com/api/predict/bulk', formDataUpload, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setBulkResults(response.data.results);
    } catch (error) {
      alert("Error uploading CSV file.");
    }
    setBulkLoading(false);
  };

  // --- NAYA FEATURE: Row Click Handler ---
  const handleRowClick = (row: any) => {
    // 1. Form ko auto-fill karna
    setFormData(prev => ({
      ...prev,
      customer_id: row.customer_id,
      monthly_charges: row.monthly_charges,
    }));
    
    // 2. Result ko auto-show karna bina API call ke
    setResult({
      churn_probability: row.churn_probability,
      risk_level: row.risk_level,
      segment: row.segment
    });

    // 3. Page ko smoothly upar scroll karna jahan Single Form hai
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // --- NAYA FEATURE: Full Detailed Recommendation Logic ---
  const getDetailedRecommendation = (risk: string, segment: string) => {
    if (risk === 'Critical') {
      return "URGENT ACTION REQUIRED: This customer is at a highly critical risk of churning. \n\n1. Immediately assign a dedicated Customer Success Manager. \n2. Reach out via phone within the next 2 hours to address any unresolved issues. \n3. Offer a flat 20-30% retention discount on their next billing cycle to buy time. \n4. Do not rely on automated emails for this segment—personal touch is mandatory to prevent revenue loss.";
    }
    if (risk === 'High') {
      return "HIGH RISK DETECTED: This customer is showing strong signs of leaving. \n\n1. Schedule a proactive check-in call this week. \n2. Review their usage patterns and suggest newly added features that align with their initial goals. \n3. Ensure all their open support tickets are resolved with priority. \n4. Send a targeted re-engagement campaign offering a free consultation.";
    }
    if (risk === 'Medium') {
      return "MODERATE RISK: The customer might be experiencing mild friction or exploring competitors. \n\n1. Send an NPS (Net Promoter Score) survey to gauge current satisfaction. \n2. Trigger automated check-in emails highlighting underutilized features. \n3. Offer a small incentive (like an extended trial of a premium feature) for completing a feedback form.";
    }
    return "ACCOUNT HEALTHY: This customer is stable and actively engaged. \n\n1. Continue standard engagement protocols. \n2. Identify opportunities for upselling or cross-selling premium features based on their 'Loyal' segment status. \n3. Request a positive review or referral. \n4. Maintain regular newsletter updates to keep them informed.";
  };

  // Calculate Summary Stats for Bulk
  const totalRiskCustomers = bulkResults.filter(r => r.risk_level === 'Critical' || r.risk_level === 'High').length;
  const revenueAtRisk = bulkResults.filter(r => r.risk_level === 'Critical' || r.risk_level === 'High')
                                   .reduce((sum, r) => sum + r.monthly_charges, 0);

  // Pagination Logic
  const totalPages = Math.ceil(bulkResults.length / rowsPerPage);
  const indexOfLastRow = currentPage * rowsPerPage;
  const indexOfFirstRow = indexOfLastRow - rowsPerPage;
  const currentRows = bulkResults.slice(indexOfFirstRow, indexOfLastRow);

  const nextPage = () => { if (currentPage < totalPages) setCurrentPage(currentPage + 1); };
  const prevPage = () => { if (currentPage > 1) setCurrentPage(currentPage - 1); };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-4 md:p-8">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between pb-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-500/20">
            <Zap className="text-white w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wide">
            RetainIQ <span className="text-slate-400 text-sm font-normal ml-2">| AI Churn Intelligence</span>
          </h1>
        </div>
      </header>

      {/* ---------------- SINGLE PREDICTION SECTION ---------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto mb-12">
        <div className="lg:col-span-2 bg-[#1e293b] p-6 rounded-2xl border border-slate-700 shadow-xl relative overflow-hidden">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-400" /> Single Customer Input
          </h2>
          <form onSubmit={handlePredict} className="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
            <div className="space-y-1"><label className="text-xs text-slate-400">Customer ID</label><input type="text" name="customer_id" value={formData.customer_id} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Tenure (Months)</label><input type="number" name="tenure" value={formData.tenure} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Monthly Charges</label><input type="number" name="monthly_charges" value={formData.monthly_charges} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Total Charges</label><input type="number" name="total_charges" value={formData.total_charges} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Contract</label><select name="contract" value={formData.contract} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white"><option>Month-to-month</option><option>One year</option><option>Two year</option></select></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Usage Frequency</label><select name="usage_frequency" value={formData.usage_frequency} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white"><option>Low</option><option>Medium</option><option>High</option></select></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Support Tickets</label><input type="number" name="support_tickets" value={formData.support_tickets} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Engagement Score</label><input type="number" name="engagement_score" value={formData.engagement_score} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            <div className="space-y-1"><label className="text-xs text-slate-400">Last Activity</label><input type="number" name="last_activity_days" value={formData.last_activity_days} onChange={handleChange} className="w-full bg-[#0f172a] border border-slate-600 rounded-lg p-2 text-white outline-none focus:border-blue-500" /></div>
            
            <button type="submit" disabled={loading} className="md:col-span-3 mt-2 bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg flex justify-center items-center gap-2">
              {loading ? 'Analyzing...' : <><Activity className="w-5 h-5" /> Run AI Prediction</>}
            </button>
          </form>
        </div>

        <div className="bg-[#1e293b] p-6 rounded-2xl border border-slate-700 shadow-xl flex flex-col relative h-full">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-emerald-400"><BarChart3 className="w-5 h-5" /> Single Result</h2>
          {!result ? (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-500"><AlertCircle className="w-8 h-8 mb-2 opacity-50" /><p>Awaiting Data...</p></div>
          ) : (
            <div className="flex flex-col h-full gap-4">
              {/* Primary Stats */}
              <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-600 text-center">
                <p className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Churn Probability</p>
                <h3 className="text-4xl font-black text-white">{(result.churn_probability * 100).toFixed(1)}%</h3>
              </div>
              <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-600 text-center">
                <p className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-1">Risk Level & Segment</p>
                <p className={`text-xl font-bold ${result.risk_level === 'Critical' ? 'text-red-500' : result.risk_level === 'High' ? 'text-orange-400' : result.risk_level === 'Medium' ? 'text-yellow-400' : 'text-emerald-400'}`}>
                  {result.risk_level} Risk
                </p>
                <p className="text-sm text-indigo-400 mt-1 font-medium">{result.segment}</p>
              </div>

              {/* NAYA FEATURE: Full Detailed Recommendation Scrollable Box */}
              <div className="bg-[#0f172a] p-4 rounded-xl border border-slate-600 flex-1 flex flex-col">
                <p className="text-xs text-slate-400 uppercase font-bold tracking-wider mb-2 flex items-center gap-2">
                  <Activity className="w-3 h-3 text-blue-400" /> Action Plan
                </p>
                <div className="max-h-32 overflow-y-auto pr-2 text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                  {getDetailedRecommendation(result.risk_level, result.segment)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ---------------- BULK UPLOAD & TABLE SECTION ---------------- */}
      <div className="max-w-7xl mx-auto border-t border-slate-700 pt-10">
        <div className="flex flex-col md:flex-row justify-between items-center mb-8">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2"><FileSpreadsheet className="text-blue-500" /> Bulk Customer Analysis</h2>
            <p className="text-slate-400 text-sm mt-1">Upload your CSV database to identify at-risk customers instantly.</p>
          </div>
          
          <input type="file" accept=".csv" className="hidden" ref={fileInputRef} onChange={handleFileUpload} />
          <button onClick={() => fileInputRef.current?.click()} disabled={bulkLoading} className="mt-4 md:mt-0 bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 shadow-lg shadow-emerald-500/20">
            {bulkLoading ? 'Processing Data...' : <><UploadCloud className="w-5 h-5" /> Upload CSV Dataset</>}
          </button>
        </div>

        {bulkResults.length > 0 && (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-[#1e293b] p-5 rounded-xl border border-slate-700 flex items-center gap-4">
                <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400"><Users className="w-6 h-6" /></div>
                <div><p className="text-sm text-slate-400">Total Analyzed</p><h4 className="text-2xl font-bold text-white">{bulkResults.length}</h4></div>
              </div>
              <div className="bg-[#1e293b] p-5 rounded-xl border border-red-500/30 flex items-center gap-4">
                <div className="p-3 bg-red-500/10 rounded-lg text-red-400"><ShieldAlert className="w-6 h-6" /></div>
                <div><p className="text-sm text-slate-400">High/Critical Risk Customers</p><h4 className="text-2xl font-bold text-red-400">{totalRiskCustomers}</h4></div>
              </div>
              <div className="bg-[#1e293b] p-5 rounded-xl border border-yellow-500/30 flex items-center gap-4">
                <div className="p-3 bg-yellow-500/10 rounded-lg text-yellow-400"><DollarSign className="w-6 h-6" /></div>
                <div><p className="text-sm text-slate-400">Monthly Revenue at Risk</p><h4 className="text-2xl font-bold text-yellow-400">${revenueAtRisk.toFixed(2)}</h4></div>
              </div>
            </div>

            {/* Data Table */}
            <div className="bg-[#1e293b] rounded-xl border border-slate-700 overflow-hidden shadow-2xl">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-[#0f172a] text-slate-300">
                    <tr>
                      <th className="p-4 font-semibold border-b border-slate-700">Customer ID</th>
                      <th className="p-4 font-semibold border-b border-slate-700">Monthly Revenue</th>
                      <th className="p-4 font-semibold border-b border-slate-700">Churn Probability</th>
                      <th className="p-4 font-semibold border-b border-slate-700">Risk Level</th>
                      <th className="p-4 font-semibold border-b border-slate-700">Segment</th>
                      <th className="p-4 font-semibold border-b border-slate-700">Recommended Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {currentRows.map((row, idx) => (
                      <tr 
                        key={idx} 
                        onClick={() => handleRowClick(row)}
                        title="Click to view detailed analysis"
                        className="hover:bg-slate-700/50 transition-colors cursor-pointer group"
                      >
                        <td className="p-4 font-medium text-white flex items-center gap-2">
                          {row.customer_id}
                        </td>
                        <td className="p-4">${row.monthly_charges.toFixed(2)}</td>
                        <td className="p-4 font-bold">{(row.churn_probability * 100).toFixed(1)}%</td>
                        <td className="p-4">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${
                            row.risk_level === 'Critical' ? 'bg-red-500/20 text-red-400' :
                            row.risk_level === 'High' ? 'bg-orange-500/20 text-orange-400' :
                            row.risk_level === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-emerald-500/20 text-emerald-400'
                          }`}>
                            {row.risk_level}
                          </span>
                        </td>
                        <td className="p-4 text-indigo-300">{row.segment}</td>
                        <td className="p-4 text-slate-300 text-xs flex justify-between items-center pr-6">
                          {row.action}
                          <ExternalLink className="w-4 h-4 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Gmail Style Pagination Bar */}
              <div className="bg-[#0f172a] p-4 border-t border-slate-700 flex items-center justify-between text-sm text-slate-400">
                <div>
                  Showing <span className="text-white font-medium">{bulkResults.length > 0 ? indexOfFirstRow + 1 : 0}</span> to <span className="text-white font-medium">{Math.min(indexOfLastRow, bulkResults.length)}</span> of <span className="text-white font-medium">{bulkResults.length}</span> entries
                </div>
                <div className="flex items-center gap-2">
                  <span>Page {currentPage} of {totalPages || 1}</span>
                  <button 
                    onClick={prevPage} 
                    disabled={currentPage === 1}
                    className="p-2 bg-[#1e293b] hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed rounded-lg border border-slate-600 text-white transition-colors">
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={nextPage} 
                    disabled={currentPage === totalPages || totalPages === 0}
                    className="p-2 bg-[#1e293b] hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed rounded-lg border border-slate-600 text-white transition-colors">
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>

            </div>
          </>
        )}
      </div>

    </div>
  );
}

export default App;