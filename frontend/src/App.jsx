import { useEffect, useState } from "react";
import api from "./services/api";
import "./App.css";

function App() {
  // Resume
  const [resume, setResume] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  // Jobs
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);

  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [description, setDescription] = useState("");

  const [jobsLoading, setJobsLoading] = useState(false);
  const [jobLoading, setJobLoading] = useState(false);

  // Matching
  const [matchResult, setMatchResult] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);

  // Error
  const [error, setError] = useState("");

  // -----------------------------
  // Fetch Jobs
  // -----------------------------

  const fetchJobs = async () => {
    setJobsLoading(true);
    setError("");

    try {
      const response = await api.get("/jobs");

      setJobs(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to load jobs."
      );
    } finally {
      setJobsLoading(false);
    }
  };

  // -----------------------------
  // Load jobs when page opens
  // -----------------------------

  useEffect(() => {
    fetchJobs();
  }, []);

  // -----------------------------
  // Select Resume
  // -----------------------------

  const handleResumeSelect = (event) => {
    const file = event.target.files[0];

    setResume(file);
    setUploadMessage("");
    setError("");
    setMatchResult(null);
  };

  // -----------------------------
  // Upload Resume
  // -----------------------------

  const handleResumeUpload = async () => {
    if (!resume) {
      setError("Please select a resume PDF.");
      return;
    }

    if (resume.type !== "application/pdf") {
      setError("Please select a PDF file.");
      return;
    }

    setUploadLoading(true);
    setError("");
    setUploadMessage("");

    try {
      const formData = new FormData();

      formData.append("file", resume);

      const response = await api.post(
        "/Upload_file",
        formData
      );

      setUploadMessage(
        `Resume uploaded successfully. ${response.data.total_pages} pages processed.`
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to upload resume."
      );
    } finally {
      setUploadLoading(false);
    }
  };

  // -----------------------------
  // Create Job
  // -----------------------------

  const createJob = async () => {
    if (
      !jobTitle.trim() ||
      !company.trim() ||
      !description.trim()
    ) {
      setError("Please fill all job fields.");
      return;
    }

    setJobLoading(true);
    setError("");

    try {
      await api.post("/jobs", {
        title: jobTitle,
        company: company,
        description: description,
      });

      setJobTitle("");
      setCompany("");
      setDescription("");

      await fetchJobs();
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to create job."
      );
    } finally {
      setJobLoading(false);
    }
  };

  // -----------------------------
  // Select Job
  // -----------------------------

  const selectJob = (job) => {
    setSelectedJob(job);
    setMatchResult(null);
    setError("");
  };

  // -----------------------------
  // Match Resume With Job
  // -----------------------------

  const matchResume = async () => {
    if (!resume) {
      setError("Please select a resume.");
      return;
    }

    if (!selectedJob) {
      setError("Please select a job.");
      return;
    }

    setMatchLoading(true);
    setError("");
    setMatchResult(null);

    try {
      const formData = new FormData();

      formData.append("file", resume);

      const response = await api.post(
        `/jobs/${selectedJob.id}/match`,
        formData
      );

      setMatchResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Failed to match resume with job."
      );
    } finally {
      setMatchLoading(false);
    }
  };

  // -----------------------------
  // Render
  // -----------------------------

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <h1>AI Resume Matcher</h1>

        <p>
          Match your resume with job requirements using AI
        </p>
      </header>

      <main className="container">

        {/* Global Error */}
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {/* -------------------------------- */}
        {/* 1. Resume Upload */}
        {/* -------------------------------- */}

        <section className="card">

          <h2>1. Upload Resume</h2>

          <input
            type="file"
            accept=".pdf"
            onChange={handleResumeSelect}
          />

          {resume && (
            <p className="file-name">
              Selected Resume:
              <strong> {resume.name}</strong>
            </p>
          )}

          <button
            onClick={handleResumeUpload}
            disabled={uploadLoading}
          >
            {uploadLoading
              ? "Uploading..."
              : "Upload Resume"}
          </button>

          {uploadMessage && (
            <p className="success">
              {uploadMessage}
            </p>
          )}

        </section>

        {/* -------------------------------- */}
        {/* 2. Create Job */}
        {/* -------------------------------- */}

        <section className="card">

          <h2>2. Create Job</h2>

          <input
            type="text"
            placeholder="Job title"
            value={jobTitle}
            onChange={(event) =>
              setJobTitle(event.target.value)
            }
          />

          <input
            type="text"
            placeholder="Company"
            value={company}
            onChange={(event) =>
              setCompany(event.target.value)
            }
          />

          <textarea
            placeholder="Job description"
            value={description}
            onChange={(event) =>
              setDescription(event.target.value)
            }
          />

          <button
            onClick={createJob}
            disabled={jobLoading}
          >
            {jobLoading
              ? "Creating..."
              : "Create Job"}
          </button>

        </section>

        {/* -------------------------------- */}
        {/* 3. Job List */}
        {/* -------------------------------- */}

        <section className="card">

          <h2>3. Select Job</h2>

          {jobsLoading && (
            <p>Loading jobs...</p>
          )}

          {!jobsLoading && jobs.length === 0 && (
            <p>No jobs available.</p>
          )}

          <div className="job-list">

            {jobs.map((job) => (
              <div
                key={job.id}
                className={`job-item ${
                  selectedJob?.id === job.id
                    ? "selected"
                    : ""
                }`}
                onClick={() => selectJob(job)}
              >

                <h3>{job.title}</h3>

                <p>{job.company}</p>

                <small>
                  Job ID: {job.id}
                </small>

              </div>
            ))}

          </div>

          {selectedJob && (
            <div className="selected-job">

              <strong>Selected Job:</strong>{" "}

              {selectedJob.title}

            </div>
          )}

        </section>

        {/* -------------------------------- */}
        {/* 4. Resume Matching */}
        {/* -------------------------------- */}

        <section className="card">

          <h2>4. Match Resume</h2>

          {!resume && (
            <p className="info">
              Please select a resume first.
            </p>
          )}

          {!selectedJob && (
            <p className="info">
              Please select a job first.
            </p>
          )}

          {resume && selectedJob && (
            <p>
              Matching{" "}
              <strong>{resume.name}</strong>
              {" "}with{" "}
              <strong>{selectedJob.title}</strong>
            </p>
          )}

          <button
            onClick={matchResume}
            disabled={
              matchLoading ||
              !resume ||
              !selectedJob
            }
          >
            {matchLoading
              ? "Analyzing Resume..."
              : "Match Resume"}
          </button>

        </section>

        {/* -------------------------------- */}
        {/* 5. Match Result */}
        {/* -------------------------------- */}

        {matchResult && (
          <section className="results">

            <div className="card">

              <h2>5. Resume Analysis</h2>

              {/* Match Score */}

              <div className="score">

                <span>
                  {matchResult.match_score}%
                </span>

                <p>Match Score</p>

              </div>

              {/* Job Information */}

              <div className="job-summary">

                <h3>
                  {matchResult.job_title}
                </h3>

                <p>
                  {matchResult.company}
                </p>

              </div>

              {/* Matched Skills */}

              <div className="result-section">

                <h3>Matched Skills</h3>

                {matchResult.analysis.matched_skills.length > 0 ? (
                  <ul>
                    {matchResult.analysis.matched_skills.map(
                      (skill, index) => (
                        <li key={index}>
                          {skill}
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p>No matched skills found.</p>
                )}

              </div>

              {/* Skill Gaps */}

              <div className="result-section">

                <h3>Skill Gaps</h3>

                {matchResult.analysis.skill_gaps.length > 0 ? (
                  <ul>
                    {matchResult.analysis.skill_gaps.map(
                      (skill, index) => (
                        <li key={index}>
                          {skill}
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p>No skill gaps found.</p>
                )}

              </div>

              {/* Strengths */}

              <div className="result-section">

                <h3>Strengths</h3>

                {matchResult.analysis.strengths.length > 0 ? (
                  <ul>
                    {matchResult.analysis.strengths.map(
                      (strength, index) => (
                        <li key={index}>
                          {strength}
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p>No strengths found.</p>
                )}

              </div>

              {/* Improvement Suggestions */}

              <div className="result-section">

                <h3>Improvement Suggestions</h3>

                {matchResult.analysis.improvement_suggestions.length > 0 ? (
                  <ul>
                    {matchResult.analysis.improvement_suggestions.map(
                      (suggestion, index) => (
                        <li key={index}>
                          {suggestion}
                        </li>
                      )
                    )}
                  </ul>
                ) : (
                  <p>No improvement suggestions.</p>
                )}

              </div>

            </div>

          </section>
        )}

      </main>

    </div>
  );
}

export default App;