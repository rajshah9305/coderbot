const express = require('express');
const axios = require('axios');
const { authenticateToken } = require('../middleware/auth');
const winston = require('winston');

const router = express.Router();

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'chat-routes' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ filename: 'error.log', level: 'error' })
  ]
});

// Chat service URL
const CHAT_SERVICE_URL = process.env.CHAT_SERVICE_URL || 'http://chat-service:8000';

// Send a message to the chat service
router.post('/completions', authenticateToken, async (req, res) => {
  try {
    const { messages, conversation_id, model, temperature, max_tokens, code_context } = req.body;
    
    // Validate required fields
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ 
        status: 'error', 
        message: 'Messages array is required' 
      });
    }
    
    // Call the chat service
    const response = await axios.post(`${CHAT_SERVICE_URL}/api/chat/completions`, {
      messages,
      conversation_id,
      model,
      temperature,
      max_tokens,
      code_context
    }, {
      headers: {
        'Authorization': `Bearer ${req.headers.authorization.split(' ')[1]}`
      },
      timeout: 60000 // 60 second timeout
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error(`Error calling chat service: ${error.message}`);
    
    // Handle different types of errors
    if (error.response) {
      const status = error.response.status;
      const errorData = error.response.data || {};
      
      res.status(status).json({
        status: 'error',
        message: 'Error processing chat request',
        error: errorData.detail || errorData.message || 'Unknown error'
      });
    } else if (error.request) {
      res.status(503).json({
        status: 'error',
        message: 'Chat service unavailable',
        error: 'Unable to reach the chat service. Please try again later.'
      });
    } else {
      res.status(500).json({
        status: 'error',
        message: 'Error processing chat request',
        error: error.message
      });
    }
  }
});

// Get user conversations
router.get('/conversations', authenticateToken, async (req, res) => {
  try {
    const response = await axios.get(`${CHAT_SERVICE_URL}/api/chat/conversations`, {
      headers: {
        'Authorization': `Bearer ${req.headers.authorization.split(' ')[1]}`
      },
      timeout: 10000 // 10 second timeout
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error(`Error fetching conversations: ${error.message}`);
    
    // Handle different types of errors
    if (error.response) {
      const status = error.response.status;
      const errorData = error.response.data || {};
      
      res.status(status).json({
        status: 'error',
        message: 'Error fetching conversations',
        error: errorData.detail || errorData.message || 'Unknown error'
      });
    } else if (error.request) {
      res.status(503).json({
        status: 'error',
        message: 'Chat service unavailable',
        error: 'Unable to reach the chat service. Please try again later.'
      });
    } else {
      res.status(500).json({
        status: 'error',
        message: 'Error fetching conversations',
        error: error.message
      });
    }
  }
});

// Get a specific conversation
router.get('/conversations/:id', authenticateToken, async (req, res) => {
  try {
    const conversationId = req.params.id;
    
    // Validate conversation ID
    if (!conversationId || conversationId.trim() === '') {
      return res.status(400).json({
        status: 'error',
        message: 'Conversation ID is required'
      });
    }
    
    const response = await axios.get(`${CHAT_SERVICE_URL}/api/chat/conversations/${conversationId}`, {
      headers: {
        'Authorization': `Bearer ${req.headers.authorization.split(' ')[1]}`
      },
      timeout: 10000 // 10 second timeout
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error(`Error fetching conversation: ${error.message}`);
    
    // Handle different types of errors
    if (error.response) {
      const status = error.response.status;
      const errorData = error.response.data || {};
      
      res.status(status).json({
        status: 'error',
        message: 'Error fetching conversation',
        error: errorData.detail || errorData.message || 'Unknown error'
      });
    } else if (error.request) {
      res.status(503).json({
        status: 'error',
        message: 'Chat service unavailable',
        error: 'Unable to reach the chat service. Please try again later.'
      });
    } else {
      res.status(500).json({
        status: 'error',
        message: 'Error fetching conversation',
        error: error.message
      });
    }
  }
});

// Delete a conversation
router.delete('/conversations/:id', authenticateToken, async (req, res) => {
  try {
    const conversationId = req.params.id;
    
    // Validate conversation ID
    if (!conversationId || conversationId.trim() === '') {
      return res.status(400).json({
        status: 'error',
        message: 'Conversation ID is required'
      });
    }
    
    const response = await axios.delete(`${CHAT_SERVICE_URL}/api/chat/conversations/${conversationId}`, {
      headers: {
        'Authorization': `Bearer ${req.headers.authorization.split(' ')[1]}`
      },
      timeout: 10000 // 10 second timeout
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error(`Error deleting conversation: ${error.message}`);
    
    // Handle different types of errors
    if (error.response) {
      const status = error.response.status;
      const errorData = error.response.data || {};
      
      res.status(status).json({
        status: 'error',
        message: 'Error deleting conversation',
        error: errorData.detail || errorData.message || 'Unknown error'
      });
    } else if (error.request) {
      res.status(503).json({
        status: 'error',
        message: 'Chat service unavailable',
        error: 'Unable to reach the chat service. Please try again later.'
      });
    } else {
      res.status(500).json({
        status: 'error',
        message: 'Error deleting conversation',
        error: error.message
      });
    }
  }
});

// Update conversation title
router.put('/conversations/:id/title', authenticateToken, async (req, res) => {
  try {
    const conversationId = req.params.id;
    const { title } = req.body;
    
    // Validate inputs
    if (!conversationId || conversationId.trim() === '') {
      return res.status(400).json({
        status: 'error',
        message: 'Conversation ID is required'
      });
    }
    
    if (!title || title.trim() === '') {
      return res.status(400).json({
        status: 'error',
        message: 'Title is required'
      });
    }
    
    const response = await axios.put(`${CHAT_SERVICE_URL}/api/chat/conversations/${conversationId}/title`, {
      title
    }, {
      headers: {
        'Authorization': `Bearer ${req.headers.authorization.split(' ')[1]}`
      },
      timeout: 10000 // 10 second timeout
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error(`Error updating conversation title: ${error.message}`);
    
    // Handle different types of errors
    if (error.response) {
      const status = error.response.status;
      const errorData = error.response.data || {};
      
      res.status(status).json({
        status: 'error',
        message: 'Error updating conversation title',
        error: errorData.detail || errorData.message || 'Unknown error'
      });
    } else if (error.request) {
      res.status(503).json({
        status: 'error',
        message: 'Chat service unavailable',
        error: 'Unable to reach the chat service. Please try again later.'
      });
    } else {
      res.status(500).json({
        status: 'error',
        message: 'Error updating conversation title',
        error: error.message
      });
    }
  }
});

module.exports = router;