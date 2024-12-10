import React, { useState, useRef, useEffect } from "react";
import { TextField, Button, Box, Typography, Paper, MenuItem, Select, FormControl, InputLabel } from "@mui/material";
import MonacoEditor from "react-monaco-editor";
import axios from "axios";

const App = () => {
  const [inputType, setInputType] = useState("text");
  const [textInput, setTextInput] = useState("");
  const [codeInput, setCodeInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [language, setLanguage] = useState("python"); // Default language

  const [company, setCompany] = useState("");
  const [position, setPosition] = useState("");
  const [interviewType, setInterviewType] = useState("");
  const [recruiterMaterial, setRecruiterMaterial] = useState("");
  const [sessionData, setSessionData] = useState({
    company: "",
    position: "",
    interviewType: "",
    recruiterMaterial: "",
  });

  const chatEndRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom whenever messages change
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSessionSubmit = () => {
    setSessionData({ company, position, interviewType, recruiterMaterial });
  };

  const handleSubmit = async () => {
    const input = inputType === "text" ? textInput : codeInput;
    if (!input.trim()) return;

    const newMessages = [
      ...messages,
      { sender: "user", type: inputType, content: input },
    ];

    setMessages(newMessages);
    inputType === "text" ? setTextInput("") : setCodeInput("");

    try {
      const res = await axios.post("http://localhost:8000/process", {
        input,
        type: inputType,
        language: language,
      });
    
      const responseType = res.data.type || "text"; // Default to text if type isn't provided
      setMessages([
        ...newMessages,
        { sender: "system", type: responseType, content: res.data.response },
      ]);
    } catch (error) {
      console.error("Error processing input:", error);
      let errorMessage = "An error occurred: ";
      if (error.response) {
        errorMessage += `Status: ${error.response.status}, Message: ${error.response.data}`;
      } else if (error.request) {
        errorMessage += "No response received from the server.";
      } else {
        errorMessage += error.message;
      }
      setMessages([
        ...newMessages,
        { sender: "system", type: "text", content: errorMessage },
      ]);
    }
  };

  const handleReset = () => {
    setCompany("");
    setPosition("");
    setInterviewType("");
    setRecruiterMaterial("");
    setTextInput("");
    setCodeInput("");
    setMessages([]);
    setSessionData({
      company: "",
      position: "",
      interviewType: "",
      recruiterMaterial: "",
    });
  };

  return (
    <Box sx={{ display: "flex", flexDirection: "column", padding: 3, maxWidth: 1200, margin: "auto" }}>
      {/* Logo / Banner */}
      <Box sx={{ display: "flex", flex: 1 }}>
        {/* Left-Side User Data Input */}
        <Box sx={{ flex: 1, paddingRight: 2, borderRight: "1px solid #ccc" }}>
          <Typography variant="h6" gutterBottom>
            Interview Format Information
          </Typography>

          <TextField
            fullWidth
            label="Company Name"
            variant="outlined"
            sx={{ marginBottom: 2 }}
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          />
          <TextField
            fullWidth
            label="Position"
            variant="outlined"
            sx={{ marginBottom: 2 }}
            value={position}
            onChange={(e) => setPosition(e.target.value)}
          />
          <TextField
            fullWidth
            label="Interview Type (e.g., Coding, Past experience)"
            variant="outlined"
            sx={{ marginBottom: 2 }}
            value={interviewType}
            onChange={(e) => setInterviewType(e.target.value)}
          />
          <TextField
            fullWidth
            label="Preparation Material/Input"
            variant="outlined"
            multiline
            rows={4}
            sx={{ marginBottom: 2 }}
            value={recruiterMaterial}
            onChange={(e) => setRecruiterMaterial(e.target.value)}
          />
          <Button
            variant="contained"
            fullWidth
            sx={{ marginBottom: 2 }}
            onClick={handleSessionSubmit}
          >
            Submit Session Data
          </Button>
          <Button
            variant="outlined"
            color="error"
            fullWidth
            sx={{ marginBottom: 2 }}
            onClick={handleReset}
          >
            Reset All
          </Button>

          {sessionData.company && (
            <Box sx={{ marginTop: 2 }}>
              <Typography variant="body1">
                <strong>Company:</strong> {sessionData.company}
              </Typography>
              <Typography variant="body1">
                <strong>Position:</strong> {sessionData.position}
              </Typography>
              <Typography variant="body1">
                <strong>Interview Type:</strong> {sessionData.interviewType}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Right-Side Chat Interface */}
        <Box sx={{ flex: 2, paddingLeft: 2 }}>
          <Typography variant="h4" align="center" gutterBottom>
            Interview Chat
          </Typography>

          <Box
            sx={{
              height: 400,
              overflowY: "auto",
              border: "1px solid #ccc",
              borderRadius: 2,
              padding: 2,
              marginBottom: 2,
              backgroundColor: "#f9f9f9",
            }}
          >
            {messages.map((message, index) => (
              <Box
                key={index}
                sx={{
                  display: "flex",
                  justifyContent: message.sender === "user" ? "flex-start" : "flex-end",
                  marginBottom: 1,
                }}
              >
                <Paper
                  sx={{
                    padding: 1,
                    backgroundColor: message.sender === "user" ? "#e3f2fd" : "#ede7f6",
                    maxWidth: "70%",
                    wordWrap: "break-word",
                  }}
                >
                  {message.type === "code" ? (
                    <Box
                      component="pre"
                      sx={{
                        fontFamily: "monospace",
                        backgroundColor: "#000",
                        color: "#fff",
                        padding: 1,
                        borderRadius: 1,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {message.content}
                    </Box>
                  ) : (
                    <Typography variant="body1">{message.content}</Typography>
                  )}
                </Paper>
              </Box>
            ))}
            {/* Invisible div to ensure scrolling */}
            <div ref={chatEndRef} />
          </Box>

          <Button
            variant="outlined"
            onClick={() => setInputType(inputType === "text" ? "code" : "text")}
            sx={{ marginBottom: 2 }}
          >
            Switch to {inputType === "text" ? "Code" : "Text"} Input
          </Button>

          {/* Language Selector - Only show when input type is code */}
          {inputType === "code" && (
            <FormControl fullWidth sx={{ marginBottom: 2 }}>
              <InputLabel id="language-select-label">Programming Language</InputLabel>
              <Select
                labelId="language-select-label"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                label="Programming Language"
              >
                <MenuItem value="javascript">JavaScript</MenuItem>
                <MenuItem value="python">Python</MenuItem>
                <MenuItem value="java">Java</MenuItem>
                <MenuItem value="csharp">C#</MenuItem>
                <MenuItem value="cpp">C++</MenuItem>
                <MenuItem value="typescript">TypeScript</MenuItem>
              </Select>
            </FormControl>
          )}

          {inputType === "text" ? (
            <TextField
              fullWidth
              label="Enter your text"
              variant="outlined"
              multiline
              rows={4}
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
            />
          ) : (
            <MonacoEditor
              height="200"
              language={language}
              theme="vs-dark"
              value={codeInput}
              onChange={(value) => setCodeInput(value)}
            />
          )}

          <Button
            variant="contained"
            fullWidth
            sx={{ marginTop: 2 }}
            onClick={handleSubmit}
          >
            Submit
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default App;