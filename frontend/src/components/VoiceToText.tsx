
import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const VoiceToText = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I can help you with voice or text messages. Try speaking or typing your message.',
      timestamp: new Date()
    }
  ]);
  const [textInput, setTextInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [inputMode, setInputMode] = useState<'voice' | 'text'>('text');
  const [recognition, setRecognition] = useState<SpeechRecognition | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognitionInstance = new SpeechRecognition();
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = false;
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onstart = () => {
        setIsListening(true);
        console.log('Voice recognition started');
      };

      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Voice input received:', transcript);
        handleSendMessage(transcript);
      };

      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionInstance.onend = () => {
        setIsListening(false);
        console.log('Voice recognition ended');
      };

      setRecognition(recognitionInstance);
    }
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages are added
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;
  
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    };
  
    setMessages(prev => [...prev, userMessage]);
    setTextInput('');
  
    console.log("📤 Sending to backend:", content);
  
    try {
      const res = await fetch("http://localhost:8001/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.content })

      });
  
      const data = await res.json();
  
      console.log("✅ Response from backend:", data);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.message || '✅ Request sent to assistant successfully.',
        timestamp: new Date()
      };
  
      setMessages(prev => [...prev, assistantMessage]);
  
    } catch (error) {
      console.error("❌ Error contacting backend:", error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 2).toString(),
        type: 'assistant',
        content: "❌ Failed to get response from assistant.",
        timestamp: new Date()
      }]);
    }
  };
  
    

  const startVoiceRecording = () => {
    if (recognition && !isListening) {
      recognition.start();
    }
  };

  const stopVoiceRecording = () => {
    if (recognition && isListening) {
      recognition.stop();
    }
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(textInput);
  };

  const toggleInputMode = () => {
    if (isListening) {
      stopVoiceRecording();
    }
    setInputMode(prev => prev === 'voice' ? 'text' : 'voice');
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-full">
              <MessageCircle className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Voice & Text Assistant</h1>
              <p className="text-sm text-gray-500">Speak or type your messages</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              Mode: {inputMode === 'voice' ? 'Voice' : 'Text'}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleInputMode}
              className="flex items-center space-x-2"
            >
              {inputMode === 'voice' ? <Mic className="w-4 h-4" /> : <MessageCircle className="w-4 h-4" />}
              <span>Switch to {inputMode === 'voice' ? 'Text' : 'Voice'}</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 px-6 py-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <Card className={`max-w-xs md:max-w-md lg:max-w-lg ${
                message.type === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white border shadow-sm'
              }`}>
                <CardContent className="p-4">
                  <div className="flex items-start space-x-2">
                    <div className="flex-1">
                      <div className={`text-xs font-medium mb-1 ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.type === 'user' ? 'You' : 'Assistant'}
                      </div>
                      <p className={`text-sm leading-relaxed ${
                        message.type === 'user' ? 'text-white' : 'text-gray-800'
                      }`}>
                        {message.content}
                      </p>
                      <div className={`text-xs mt-2 ${
                        message.type === 'user' ? 'text-blue-200' : 'text-gray-400'
                      }`}>
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="bg-white border-t px-6 py-4">
        {inputMode === 'text' ? (
          <form onSubmit={handleTextSubmit} className="flex items-center space-x-2">
            <Input
              type="text"
              placeholder="Type your message..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              className="flex-1"
              disabled={isListening}
            />
            <Button 
              type="submit" 
              disabled={!textInput.trim() || isListening}
              className="px-4 py-2"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        ) : (
          <div className="flex items-center justify-center space-x-4">
            <div className="text-center">
              {isListening && (
                <div className="text-sm text-blue-600 mb-2 font-medium">
                  Listening... Speak now
                </div>
              )}
              <Button
                onClick={isListening ? stopVoiceRecording : startVoiceRecording}
                size="lg"
                className={`w-16 h-16 rounded-full transition-all duration-200 ${
                  isListening 
                    ? 'bg-red-600 hover:bg-red-700 animate-pulse' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isListening ? (
                  <MicOff className="w-6 h-6" />
                ) : (
                  <Mic className="w-6 h-6" />
                )}
              </Button>
              <div className="text-xs text-gray-500 mt-2">
                {isListening ? 'Tap to stop' : 'Tap to speak'}
              </div>
            </div>
          </div>
        )}
        
        {!recognition && (
          <div className="text-center text-sm text-amber-600 bg-amber-50 rounded-lg p-3 mt-2">
            Voice recognition is not supported in your browser. Please use text input.
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceToText;
