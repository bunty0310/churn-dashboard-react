// frontend/src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// This component is the entire application UI
function App() {
  // 'useState' is a React Hook to manage state. We create a state object
  // to hold the values of all our form inputs.
  const [formData, setFormData] = useState({
    tenure: 24,
    MonthlyCharges: 70.0,
    TotalCharges: 1400.0,
    Contract: 'Month-to-month',
    PaymentMethod: 'Electronic check',
    gender: 'Male', Partner: 'No', Dependents: 'No', PhoneService: 'Yes',
    MultipleLines: 'No', InternetService: 'DSL', OnlineSecurity: 'No',
    OnlineBackup: 'Yes', DeviceProtection: 'No', TechSupport: 'No',
    StreamingTV: 'No', StreamingMovies: 'No', PaperlessBilling: 'Yes', SeniorCitizen: 0,
  });

  // More state variables: one for the prediction result, and one to track loading status.
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  // This function is called whenever a user changes an input in the form.
  const handleChange = (e) => {
    const { name, value } = e.target;
    // It updates the formData state with the new value.
    setFormData(prevState => ({ ...prevState, [name]: value }));
  };

  // This function is called when the form is submitted.
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevents the browser from reloading the page
    setLoading(true); // Show a loading indicator
    setPrediction(null); // Clear previous prediction

    // The API endpoint is relative because our Flask server will serve this app.
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api/predict';

    try {
      // We use axios to send a POST request with the form data to our backend.
      const res = await axios.post(API_URL, formData);
      // We update the prediction state with the result from the API.
      setPrediction(res.data.churn_prediction);
    } catch (error) {
      console.error("Error making prediction:", error);
      alert("An error occurred. Please check the console for details.");
    } finally {
      setLoading(false); // Hide the loading indicator
    }
  };

  // The JSX below describes the HTML structure of our component.
  return (
    <div className="App">
      <h1>Customer Churn Prediction</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* We only show a few inputs here for simplicity, but a full app would have all of them. */}
          <div className="form-group">
            <label>Tenure (months)</label>
            <input type="number" name="tenure" value={formData.tenure} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Monthly Charges</label>
            <input type="number" step="0.01" name="MonthlyCharges" value={formData.MonthlyCharges} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label>Contract</label>
            <select name="Contract" value={formData.Contract} onChange={handleChange}>
              <option value="Month-to-month">Month-to-month</option>
              <option value="One year">One year</option>
              <option value="Two year">Two year</option>
            </select>
          </div>
          <div className="form-group">
            <label>Payment Method</label>
            <select name="PaymentMethod" value={formData.PaymentMethod} onChange={handleChange}>
                <option value="Electronic check">Electronic check</option>
                <option value="Mailed check">Mailed check</option>
                <option value="Bank transfer (automatic)">Bank transfer (automatic)</option>
                <option value="Credit card (automatic)">Credit card (automatic)</option>
            </select>
          </div>
          <button type="submit" className="predict-button" disabled={loading}>
            {loading ? 'Predicting...' : 'Predict Churn'}
          </button>
        </div>
      </form>

      {/* This section only renders if a prediction has been made. */}
      {prediction !== null && (
        <div className={`result ${prediction === 1 ? 'danger' : 'success'}`}>
          {prediction === 1 ? 'Result: This customer is LIKELY TO CHURN.' : 'Result: This customer is LIKELY TO STAY.'}
        </div>
      )}
    </div>
  );
}
export default App;