import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  Paper,
  Alert,
  Snackbar,
  CircularProgress,
} from '@mui/material';

function CodeExecutor() {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [prompt, setPrompt] = useState('');
  const [userInput, setUserInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const ws = useRef(null);
  const token = localStorage.getItem('accessToken');

  // Establish WebSocket connection when a session is set
  useEffect(() => {
    if (sessionId) {
      // Determine protocol based on current connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws.current = new WebSocket(`${protocol}//${window.location.host}/ws/compiler/`);
      ws.current.onopen = () => {
        setWsConnected(true);
        setSnackbarOpen(true);
        setError({ severity: 'success', message: 'WebSocket connected successfully' });
        // Send the session id so backend knows which session to interact with
        ws.current.send(JSON.stringify({ action: 'set_session', session_id: sessionId }));
      };
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.prompt !== undefined) {
            setPrompt(data.prompt);
          }
          if (data.error) {
            setError({ severity: 'error', message: data.error });
            setSnackbarOpen(true);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
          setError({ severity: 'error', message: 'Error processing server response' });
          setSnackbarOpen(true);
        }
      };
      ws.current.onclose = () => {
        setWsConnected(false);
        setError({ severity: 'warning', message: 'WebSocket connection closed' });
        setSnackbarOpen(true);
      };
      ws.current.onerror = () => {
        setError({ severity: 'error', message: 'WebSocket connection error' });
        setSnackbarOpen(true);
      };
      return () => {
        ws.current.close();
      };
    }
  }, [sessionId]);

  // Poll for interactive prompt every 2 seconds if WebSocket is connected
  useEffect(() => {
    let interval;
    if (wsConnected && sessionId) {
      interval = setInterval(() => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          ws.current.send(JSON.stringify({ action: 'get_prompt' }));
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [wsConnected, sessionId]);

  const handleExecute = async () => {
    if (!code.trim()) {
      setError({ severity: 'warning', message: 'Please enter some code to execute' });
      setSnackbarOpen(true);
      return;
    }

    if (!token) {
      setError({ severity: 'error', message: 'Authentication token missing. Please log in again.' });
      setSnackbarOpen(true);
      return;
    }

    setLoading(true);
    setOutput('Preparing execution environment...');

    try {
      const response = await axios.post(
        '/api/compiler/execute/',
        { code },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setSessionId(response.data.session_id);
      setOutput('Code execution started...\n');
      setError({ severity: 'success', message: 'Code submitted successfully' });
      setSnackbarOpen(true);
    } catch (err) {
      console.error('Execution error:', err);
      let errorMessage = 'Error executing code.';
      
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        errorMessage = err.response.data.message || 
                      `Server error: ${err.response.status} ${err.response.statusText}`;
      } else if (err.request) {
        // The request was made but no response was received
        errorMessage = 'No response from server. Please check your connection.';
      }
      
      setOutput(`Error: ${errorMessage}`);
      setError({ severity: 'error', message: errorMessage });
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleUserInputSubmit = () => {
    if (!userInput.trim()) {
      setError({ severity: 'warning', message: 'Please enter input before submitting' });
      setSnackbarOpen(true);
      return;
    }
    
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'user_input', input: userInput }));
      setOutput(prev => `${prev}\nInput: ${userInput}`);
      setPrompt('');
      setUserInput('');
    } else {
      setError({ severity: 'error', message: 'WebSocket connection lost. Please refresh the page.' });
      setSnackbarOpen(true);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Snackbar 
        open={snackbarOpen} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={error?.severity || 'info'} sx={{ width: '100%' }}>
          {error?.message}
        </Alert>
      </Snackbar>
      
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom>
          Python Compiler
        </Typography>
        <Box sx={{ mb: 2 }}>
          <TextField
            label="Enter Python Code"
            multiline
            fullWidth
            rows={10}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            variant="outlined"
            disabled={loading}
          />
        </Box>
        <Button 
          variant="contained" 
          onClick={handleExecute} 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          {loading ? 'Executing...' : 'Execute Code'}
        </Button>
        <Box sx={{ mt: 4 }}>
          <Typography variant="h6">Output:</Typography>
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              backgroundColor: '#f5f5f5',
              minHeight: '150px',
              maxHeight: '300px',
              overflowY: 'auto',
            }}
          >
            <Typography component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
              {output}
            </Typography>
          </Paper>
        </Box>
        {prompt && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6">Interactive Prompt:</Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {prompt}
            </Typography>
            <TextField
              label="Your Input"
              fullWidth
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              variant="outlined"
              disabled={loading}
            />
            <Button 
              variant="contained" 
              sx={{ mt: 2 }} 
              onClick={handleUserInputSubmit}
              disabled={loading || !prompt}
            >
              Submit Input
            </Button>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default CodeExecutor;
