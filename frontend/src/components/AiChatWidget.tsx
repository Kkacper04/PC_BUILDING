import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Fab,
  Paper,
  Typography,
  IconButton,
  TextField,
  Button,
  CircularProgress,
  Divider,
} from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import ReactMarkdown from 'react-markdown';
import { useChatStore } from '../store/chatStore';
import { useBuildStore } from '../store/buildStore';
import { useChatMutation, fetchCPU, fetchGPU, fetchMotherboard, fetchRAMItem, fetchPSU, fetchCase, fetchCooler, fetchStorageItem } from '../api/queries';


export const AiChatWidget: React.FC = () => {
  const { isOpen, toggleChat, messages, addMessage, clearChat } = useChatStore();
  const setComponent = useBuildStore((state) => state.setComponent);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const chatMutation = useChatMutation({
    onSuccess: (data) => {
      addMessage({ role: 'assistant', content: data.message });
      if (data.suggested_build) {
        // Dodaj ukrytą wiadomość systemową, żeby wyrenderować przycisk akceptacji dla tego buildu
        addMessage({ role: 'system', content: JSON.stringify(data.suggested_build) });
      }
    },
    onError: () => {
      addMessage({ role: 'assistant', content: 'Wystąpił błąd podczas łączenia z AI. Upewnij się, że lokalny model jest uruchomiony.' });
    }
  });

  // Auto-scroll w dół
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSend = () => {
    if (!inputValue.trim() || chatMutation.isPending) return;

    const userMsg = { role: 'user' as const, content: inputValue };
    addMessage(userMsg);
    setInputValue('');

    // Tworzymy payload wysyłając tylko role user i assistant (bez naszych systemowych buttonów)
    const payload = messages.filter(m => m.role !== 'system').concat(userMsg);
    chatMutation.mutate(payload);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const applyBuild = async (buildStr: string) => {
    try {
      const build = JSON.parse(buildStr) as Record<string, number | null>;
      
      const promises = [];
      if (build.cpu) promises.push(fetchCPU(build.cpu).then(c => setComponent('cpu', c)));
      if (build.gpu) promises.push(fetchGPU(build.gpu).then(c => setComponent('gpu', c)));
      if (build.motherboard) promises.push(fetchMotherboard(build.motherboard).then(c => setComponent('motherboard', c)));
      if (build.ram) promises.push(fetchRAMItem(build.ram).then(c => setComponent('ram', c)));
      if (build.psu) promises.push(fetchPSU(build.psu).then(c => setComponent('psu', c)));
      if (build.case) promises.push(fetchCase(build.case).then(c => setComponent('case', c)));
      if (build.cooler) promises.push(fetchCooler(build.cooler).then(c => setComponent('cooler', c)));
      if (build.storage) promises.push(fetchStorageItem(build.storage).then(c => setComponent('storage', c)));

      await Promise.all(promises);
    } catch (err) {
      console.error("Błąd podczas ładowania proponowanego zestawu:", err);
    }
  };

  return (
    <>
      <Fab
        color="primary"
        onClick={toggleChat}
        sx={{ position: 'fixed', bottom: 24, right: 24, zIndex: 1000 }}
      >
        {isOpen ? <CloseIcon /> : <ChatIcon />}
      </Fab>

      {isOpen && (
        <Paper
          elevation={6}
          sx={{
            position: 'fixed',
            bottom: 90,
            right: 24,
            width: 350,
            height: 500,
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
            borderRadius: 3,
            overflow: 'hidden',
            backgroundColor: '#121212',
            border: '1px solid rgba(255,255,255,0.1)'
          }}
        >
          <Box sx={{ p: 2, backgroundColor: 'primary.main', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AutoFixHighIcon sx={{ color: 'white' }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', color: 'white' }}>
                AI Builder
              </Typography>
            </Box>
            <Button size="small" onClick={clearChat} sx={{ color: 'white', minWidth: 'auto', p: 0.5, fontSize: '0.7rem' }}>
              Clear
            </Button>
          </Box>

          <Box sx={{ flex: 1, overflowY: 'auto', p: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {messages.map((msg, idx) => {
              if (msg.role === 'system') {
                return (
                  <Box key={idx} sx={{ display: 'flex', justifyContent: 'center' }}>
                    <Button 
                      variant="contained" 
                      color="success" 
                      size="small"
                      onClick={() => applyBuild(msg.content)}
                      startIcon={<AutoFixHighIcon />}
                    >
                      Apply this build to cart!
                    </Button>
                  </Box>
                );
              }

              const isUser = msg.role === 'user';
              return (
                <Box key={idx} sx={{ alignSelf: isUser ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
                  <Paper
                    sx={{
                      p: 1.5,
                      backgroundColor: isUser ? 'primary.main' : '#1e1e1e',
                      color: isUser ? 'white' : 'text.primary',
                      borderRadius: 2,
                      borderTopRightRadius: isUser ? 0 : undefined,
                      borderTopLeftRadius: !isUser ? 0 : undefined,
                    }}
                  >
                    <Typography variant="body2" sx={{ '& p': { m: 0 } }} component="div">
                      {isUser ? msg.content : <ReactMarkdown>{msg.content}</ReactMarkdown>}
                    </Typography>
                  </Paper>
                </Box>
              );
            })}
            
            {chatMutation.isPending && (
              <Box sx={{ alignSelf: 'flex-start' }}>
                <CircularProgress size={20} />
              </Box>
            )}
            <div ref={messagesEndRef} />
          </Box>
          <Divider sx={{ borderColor: 'rgba(255,255,255,0.05)' }} />

          {/* Input */}
          <Box sx={{ p: 2, backgroundColor: '#0f0f0f', display: 'flex', gap: 1 }}>
            <TextField
              size="small"
              fullWidth
              placeholder="Ask the AI..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={chatMutation.isPending}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 5 } }}
            />
            <IconButton 
              color="primary" 
              onClick={handleSend} 
              disabled={!inputValue.trim() || chatMutation.isPending}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      )}
    </>
  );
};
